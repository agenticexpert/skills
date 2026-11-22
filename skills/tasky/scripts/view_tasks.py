#!/usr/bin/env python3
"""
view_tasks.py — Render a task list for a milestone.

Usage:
    python view_tasks.py <project> <roadmap> <track> <milestone>

Output:
    Milestone name + status · done/total header
    Column-aligned task table with seq (1..n) and ← next marker
    Footer: next unblocked task
"""

import os
import re
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasky_config import TASKY_ROOT
from claims import other_holder
from position import destination_progress, progress, sequence_state, split_markers

COL_SEQ    = 3
COL_STATUS = 7
MAX_TITLE  = 52

HELD_MARK  = "  ← another session"

# ---------------------------------------------------------------------------
# project.json helpers
# ---------------------------------------------------------------------------

def load_project_json(project):
    pjson = os.path.join(TASKY_ROOT, project, "project.json")
    if not os.path.isfile(pjson):
        return {"roadmaps": [], "tracks": {}, "milestones": {}, "tasks": {}}
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

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_task_file(path):
    text = Path(path).read_text(encoding="utf-8")
    title = ""
    status = "x"
    deps = []

    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        m = re.match(r"^Status:\s*(.+)$", line)
        if m:
            status = m.group(1).strip().lower()
        m = re.match(r"^Dependencies:\s*\[(.*)\]$", line)
        if m:
            raw = m.group(1).strip()
            deps = [d.strip() for d in raw.split(",") if d.strip()]

    criteria_total = len(re.findall(r"^\s*\[[ x]\]", text, re.MULTILINE))
    criteria_done  = len(re.findall(r"^\s*\[x\]",    text, re.MULTILINE))

    return title, status, deps, criteria_total, criteria_done


def load_tasks(milestone_dir, task_order):
    """Load tasks using project.json order. Falls back to filesystem if order is empty."""
    if not os.path.isdir(milestone_dir):
        return []

    if task_order:
        slugs, _ = split_markers(task_order)
    else:
        slugs = sorted([
            f.replace(".md", "")
            for f in os.listdir(milestone_dir)
            if f.endswith(".md") and not f.startswith(".")
        ])

    tasks = []
    for seq, slug in enumerate(slugs, 1):
        fpath = os.path.join(milestone_dir, f"{slug}.md")
        if not os.path.isfile(fpath):
            continue
        title, status, deps, ct, cd = parse_task_file(fpath)
        tasks.append({
            "seq":   seq,
            "slug":  slug,
            "title": title or slug,
            "status": status,
            "deps":  deps,
            "criteria_total": ct,
            "criteria_done":  cd,
            "held":  bool(other_holder(fpath)),
        })

    return tasks


# ---------------------------------------------------------------------------
# Status rollup
# ---------------------------------------------------------------------------

def compute_status(tasks):
    statuses = [t["status"] for t in tasks]
    if not statuses:
        return "x"
    if all(s == "done" for s in statuses):
        return "done"
    if all(s in ("done", "ready") for s in statuses):
        return "ready"
    done_count = sum(1 for s in statuses if s == "done")
    if any(s in ("doing", "ready") for s in statuses) or done_count > 0:
        return "doing"
    return "pending"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def dep_lines(deps):
    if not deps:
        return ["—"]
    return list(deps)


def marker_lines(markers, branches, t_key, oob):
    """Split [(mid, after_index)] into inline {after_index: [(mid, destination)]} rows and the closing line."""
    inline, closing = {}, None
    for mid, after in markers:
        rec = branches.get(mid)
        if rec is None:
            continue
        if rec.get("destination") == t_key and bool(rec.get("oob")) == bool(oob):
            closing = (
                after,
                "⤶".rjust(COL_SEQ) + "  end of branch → back to "
                + branch_label(rec.get("origin", ""))
                + (f" · {rec['origin_anchor']}" if rec.get("origin_anchor") else ""),
            )
        else:
            inline.setdefault(after, []).append((mid, rec.get("destination", "")))
    return inline, closing


def branch_label(t_key):
    parts = t_key.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else t_key


def render(milestone_name, tasks, oob_tasks=None, markers=None, oob_markers=None,
           branches=None, t_key=None, place=None, problems=(), dest_progress=None):
    """place is where "next" lands and problems the contradiction lines, both from
    position.sequence_state, place carrying the task's "seq" and "title" for the footer;
    dest_progress maps a marker row to its destination's (status, done, total)."""
    if oob_tasks is None:
        oob_tasks = []
    branches = branches or {}
    dest_progress = dest_progress or {}
    place = place or {}
    pointer = place["task"]["slug"] if place and place["mid"] is None else None
    inline, closing = marker_lines(markers or [], branches, t_key, False)
    oob_inline, oob_closing = marker_lines(oob_markers or [], branches, t_key, True)

    if not tasks and not oob_tasks:
        return f"{milestone_name}\n(no tasks)"

    ms_status = compute_status(tasks)
    _, done, total = progress(tasks + oob_tasks)
    held = any(t["held"] for t in tasks + oob_tasks)
    next_seq = next((t["seq"] for t in tasks if t["slug"] == pointer), None)

    all_for_cols   = tasks + oob_tasks
    dep_lists      = [dep_lines(t["deps"]) for t in all_for_cols]
    seq_dep_lists  = dep_lists[:len(tasks)]
    oob_dep_lists  = dep_lists[len(tasks):]

    col_title = max(5, min(MAX_TITLE, max(len(t["title"]) for t in all_for_cols))) + 2
    # Width sized to longest single dep — multi-dep tasks wrap one-per-line.
    max_dep   = max((len(d) for dl in dep_lists for d in dl), default=4)
    col_deps  = max(4, max_dep) + 2

    content_w = 1 + COL_SEQ + 2 + col_title + col_deps + COL_STATUS

    right   = f"{ms_status} · {done}/{total}"
    gap     = max(1, content_w - len(milestone_name) - len(right))
    ms_line = milestone_name + " " * gap + right
    line_w  = len(ms_line)
    sep     = "─" * line_w

    col_hdr = (
        " " +
        "#".rjust(COL_SEQ) + "  " +
        "Title".ljust(col_title) +
        "Deps".ljust(col_deps) +
        "Status"
    )

    out = [ms_line, sep, col_hdr]

    def marker_row(mid, dest):
        status, mdone, mtotal = dest_progress.get(mid, ("todo", 0, 0))
        to = "to " + branch_label(dest)
        mark = ""
        if place.get("mid") == mid:
            mark = "  ← doing" if place["doing"] else "  ← next"
        return (" " + "↑".rjust(COL_SEQ) + "  " + to.ljust(max(col_title + col_deps, len(to) + 2))
                + f"{status} · {mdone}/{mtotal}" + mark)

    for mid, dest in inline.get(0, []):
        out.append(marker_row(mid, dest))

    for t, deps in zip(tasks, seq_dep_lists):
        title = t["title"]
        if len(title) > MAX_TITLE:
            title = title[:MAX_TITLE - 3] + "..."
        marker = HELD_MARK if t["held"] else ("  ← next" if t["seq"] == next_seq else "")
        if not marker and closing and t["seq"] == closing[0]:
            marker = "  ← new task inserts here"
        out.append(
            " " +
            str(t["seq"]).rjust(COL_SEQ) + "  " +
            title.ljust(col_title) +
            deps[0].ljust(col_deps) +
            t["status"] +
            marker
        )
        for d in deps[1:]:
            out.append(
                " " +
                " " * COL_SEQ + "  " +
                " " * col_title +
                d.ljust(col_deps)
            )
        for mid, dest in inline.get(t["seq"], []):
            out.append(marker_row(mid, dest))

    if closing:
        out.append(" " + closing[1])

    if oob_tasks:
        out.append(sep)
        for t, deps in zip(oob_tasks, oob_dep_lists):
            title = t["title"]
            if len(title) > MAX_TITLE:
                title = title[:MAX_TITLE - 3] + "..."
            out.append(
                " " +
                "·".rjust(COL_SEQ) + "  " +
                title.ljust(col_title) +
                deps[0].ljust(col_deps) +
                t["status"] +
                (HELD_MARK if t["held"] else "")
            )
            for d in deps[1:]:
                out.append(
                    " " +
                    " " * COL_SEQ + "  " +
                    " " * col_title +
                    d.ljust(col_deps)
                )
        for mid, dest in [row for rows in oob_inline.values() for row in rows]:
            out.append(marker_row(mid, dest))
        if oob_closing:
            out.append(" " + oob_closing[1])

    out.append(sep)

    if held:
        out.append("Next unblocked: none — another session holds this milestone")
    elif place.get("mid"):
        dest = branches[place["mid"]]["destination"]
        inside = "" if place["t_key"] == dest else f" in {branch_label(place['t_key'])}"
        out.append(f"Next unblocked: ↑ to {branch_label(dest)} — "
                   f"{place['seq']} — {place['title']}{inside}")
    elif next_seq:
        nt = next(t for t in tasks if t["seq"] == next_seq)
        out.append(f"Next unblocked: {next_seq} — {nt['title']}")
    else:
        remaining = [t for t in tasks if t["status"] not in ("done", "ready")]
        if remaining:
            out.append("Next unblocked: none (all remaining tasks are blocked)")
        else:
            out.append("All tasks complete.")
    out.extend(problems)

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 5:
        print("Usage: view_tasks.py <project> <roadmap> <track> <milestone>")
        sys.exit(1)

    project, roadmap, track, milestone = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    data = load_project_json(project)

    milestone_dir = os.path.join(TASKY_ROOT, project, roadmap, track, milestone)
    if not os.path.isdir(milestone_dir):
        print(f"Error: milestone '{milestone}' not found.", file=sys.stderr)
        sys.exit(1)
    t_key = f"{roadmap}/{track}/{milestone}"
    order = data["tasks"].get(t_key, [])
    _, markers = split_markers(order, data["branches"])
    tasks = load_tasks(milestone_dir, order)
    oob_order = data["oob_tasks"].get(t_key, [])
    oob_plain, oob_markers = split_markers(oob_order, data["branches"])
    oob_slugs = sorted(oob_plain)
    oob_tasks = load_tasks(milestone_dir, oob_slugs) if oob_slugs else []
    oob_tasks.sort(key=lambda t: (t["status"] != "done", t["status"] == "x"))
    place, problems = sequence_state(project, data, t_key)
    if place and place["mid"]:
        slug = place["task"]["slug"]
        held_in = data["oob_tasks" if place["oob"] else "tasks"].get(place["t_key"], [])
        slugs, _ = split_markers(held_in)
        place["seq"] = "·" if place["oob"] or slug not in slugs else slugs.index(slug) + 1
        title = parse_task_file(os.path.join(TASKY_ROOT, project, *place["t_key"].split("/"), f"{slug}.md"))[0]
        place["title"] = title or slug
    dest_progress = {mid: destination_progress(project, data, data["branches"][mid]["destination"])
                     for mid, _ in markers + oob_markers if mid in data["branches"]}
    print(render(milestone, tasks, oob_tasks, markers, oob_markers, data["branches"], t_key,
                 place, problems, dest_progress=dest_progress))


if __name__ == "__main__":
    main()
