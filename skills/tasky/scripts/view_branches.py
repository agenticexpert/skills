#!/usr/bin/env python3
"""
view_branches.py — Render the branch chain from the current position outward.

Usage:
    python view_branches.py [<project>]

Output:
    A "you are here" block — the current milestone, then one hop per parent
    level, each with its done/total count and the origin it returns to — and
    below it every other open branch, truncated at 10 rows.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasky_config import TASKY_ROOT

MID_RE = re.compile(r"^branch--[0-9a-f]{8}$")

HOP_CAP = 64
ALSO_LIMIT = 10


# ---------------------------------------------------------------------------
# project.json
# ---------------------------------------------------------------------------

def load_project_json(project):
    pjson = os.path.join(TASKY_ROOT, project, "project.json")
    if not os.path.isfile(pjson):
        return {"tasks": {}, "oob_tasks": {}, "branches": {}}
    with open(pjson) as f:
        data = json.load(f)
    data.setdefault("roadmaps", [])
    data.setdefault("tracks", {})
    data.setdefault("milestones", {})
    data.setdefault("tasks", {})
    data.setdefault("oob_roadmaps", {})
    data.setdefault("oob_tracks", {})
    data.setdefault("oob_milestones", {})
    data.setdefault("oob_tasks", {})
    data.setdefault("milestone_deps", {})
    data.setdefault("branches", {})
    return data


def is_marker(slug):
    return bool(MID_RE.fullmatch(slug))


def split_markers(order, branches=None):
    """Partition an order array into task slugs and [(mid, after_index)] marker rows."""
    task_slugs, markers = [], []
    for slug in order:
        if is_marker(slug):
            markers.append((slug, len(task_slugs)))
        else:
            task_slugs.append(slug)
    return task_slugs, markers


# ---------------------------------------------------------------------------
# Milestone facts — read once, only for the milestones actually rendered
# ---------------------------------------------------------------------------

def read_task_status(path):
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        for line in f:
            m = re.match(r"^Status:\s*(.+)$", line.strip())
            if m:
                return m.group(1).strip().lower()
    return "x"


def milestone_facts(project, data, t_key, cache):
    """(done, total, {slug: status}, [task slugs in order]) for one milestone."""
    if t_key in cache:
        return cache[t_key]
    mdir = os.path.join(TASKY_ROOT, project, *t_key.split("/"))
    slugs, _ = split_markers(data["tasks"].get(t_key, []))
    oob_slugs, _ = split_markers(data["oob_tasks"].get(t_key, []))
    statuses = {}
    done = total = 0
    for slug in slugs + [s for s in oob_slugs if s not in slugs]:
        status = read_task_status(os.path.join(mdir, f"{slug}.md"))
        if status is None:
            continue
        statuses[slug] = status
        if status == "x":
            continue
        total += 1
        if status == "done":
            done += 1
    facts = (done, total, statuses, slugs)
    cache[t_key] = facts
    return facts


def label(t_key):
    parts = t_key.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else t_key


def anchor_ref(project, data, rec, cache):
    """'auth/login · wire-the-session', or 'auth/login' when no task holds the return."""
    anchor = rec.get("origin_anchor")
    origin = rec.get("origin", "")
    if not anchor:
        return label(origin)
    return f"{label(origin)} · {anchor}"


# ---------------------------------------------------------------------------
# Chain
# ---------------------------------------------------------------------------

def current_position(project, data, cache):
    for t_key in data["tasks"]:
        _, _, statuses, slugs = milestone_facts(project, data, t_key, cache)
        for slug in slugs:
            if statuses.get(slug) == "doing":
                return t_key
    newest = None
    for order, rec in enumerate(data["branches"].values()):
        if rec.get("state") != "open":
            continue
        key = (rec.get("opened", ""), order)
        if newest is None or key >= newest[0]:
            newest = (key, rec)
    return newest[1]["destination"] if newest else None


def build_chain(data, position):
    """[(t_key, record-that-returns-out-of-it or None)], innermost first."""
    chain, seen = [], set()
    t_key = position
    for _ in range(HOP_CAP):
        rec = None
        for candidate in data["branches"].values():
            if candidate.get("destination") == t_key and candidate.get("state") == "open":
                rec = candidate
                break
        chain.append((t_key, rec))
        if rec is None or rec["origin"] in seen:
            break
        seen.add(t_key)
        t_key = rec["origin"]
    return chain


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render(project, data, cache):
    branches = data["branches"]
    open_records = [r for r in branches.values() if r.get("state") == "open"]
    if not open_records:
        return "no branch in flight"

    position = current_position(project, data, cache)
    if position is None:
        return "no branch in flight"

    chain = build_chain(data, position)

    rows = []
    for depth, (t_key, rec) in enumerate(chain):
        done, total, statuses, _ = milestone_facts(project, data, t_key, cache)
        rows.append({
            "name": " " * (4 + depth * 4) + label(t_key),
            "count": f"{done} of {total} done",
            "rec": rec,
            "depth": depth,
            "paused": False,
        })
    # A milestone is annotated paused when the hop above it left a paused anchor there.
    for depth, (t_key, rec) in enumerate(chain):
        if rec is None:
            continue
        anchor = rec.get("origin_anchor")
        if not anchor or depth + 1 >= len(rows):
            continue
        _, _, statuses, _ = milestone_facts(project, data, rec["origin"], cache)
        if statuses.get(anchor) == "paused":
            rows[depth + 1]["paused"] = True

    name_w = max(len(r["name"]) for r in rows) + 2
    count_w = max(len(r["count"]) for r in rows) + 6

    out = ["▸ you are here"]
    for row in rows:
        line = row["name"].ljust(name_w) + row["count"]
        if row["paused"]:
            line = line.ljust(name_w + count_w) + "← paused"
        out.append(line.rstrip())
        if row["rec"] is not None:
            out.append(" " * (4 + row["depth"] * 4) + "↑ from  " + anchor_ref(project, data, row["rec"], cache))

    on_chain = {t_key for t_key, _ in chain}
    also = [r for r in open_records if r["destination"] not in on_chain]
    if also:
        out.append("")
        out.append("  also in flight (not on this line)")
        shown = also[:ALSO_LIMIT]
        entries = []
        for rec in shown:
            done, total, _, _ = milestone_facts(project, data, rec["destination"], cache)
            entries.append(("    " + label(rec["destination"]), f"{done} of {total} done", rec))
        w = max(len(e[0]) for e in entries) + 2
        c = max(len(e[1]) for e in entries) + 2
        for name, count, rec in entries:
            out.append(name.ljust(w) + count.ljust(c) + "↑ from  " + anchor_ref(project, data, rec, cache))
        if len(also) > ALSO_LIMIT:
            out.append(f"    … and {len(also) - ALSO_LIMIT} more")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 2:
        print("Usage: view_branches.py [<project>]")
        sys.exit(1)

    if len(sys.argv) == 2:
        projects = [sys.argv[1]]
    else:
        projects = sorted([
            d for d in os.listdir(TASKY_ROOT)
            if os.path.isdir(os.path.join(TASKY_ROOT, d)) and not d.startswith(".")
        ]) if os.path.isdir(TASKY_ROOT) else []

    blocks = []
    for project in projects:
        cache = {}
        data = load_project_json(project)
        text = render(project, data, cache)
        if text == "no branch in flight" and len(projects) > 1:
            continue
        blocks.append(text if len(projects) == 1 else f"{project}\n{text}")

    print("\n\n".join(blocks) if blocks else "no branch in flight")


if __name__ == "__main__":
    main()
