#!/usr/bin/env python3
"""
manage_branches.py — Open, close, drop, and inspect branch-and-return records.

A branch record lives in project.json["branches"], keyed by a reserved marker id
(MID) of the form branch--<8 lowercase hex>. The same MID is written as a row into
two task order arrays: the origin milestone's (the open end) and the destination
milestone's (the closing end). No <MID>.md file is ever written, so every reader
that joins an order entry to its file skips the row and no count or sequence
number moves.

Usage:
  python manage_branches.py open  <project> <origin-t_key> <dest-t_key> [--oob]
  python manage_branches.py close <project> <MID>
  python manage_branches.py drop  <project> <MID>
  python manage_branches.py show  <project> [<MID>] [--return]
"""

import argparse
import datetime
import json
import os
import re
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasky_config import TASKY_ROOT, validate_slug, validate_slash_path

MID_RE = re.compile(r"^branch--[0-9a-f]{8}$")

WORKABLE = ("todo", "pending", "doing", "paused")

HOP_CAP = 64

RECORD_FIELDS = (
    "id", "origin", "origin_anchor", "anchor_prior_status",
    "destination", "oob", "parent", "state", "opened",
)


# ---------------------------------------------------------------------------
# Marker rows
# ---------------------------------------------------------------------------

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
# Paths and persistence
# ---------------------------------------------------------------------------

def project_json_path(project):
    return os.path.join(TASKY_ROOT, project, "project.json")


def milestone_path(project, t_key):
    return os.path.join(TASKY_ROOT, project, *t_key.split("/"))


def load_project_json(project):
    path = project_json_path(project)
    if not os.path.isfile(path):
        return {"roadmaps": [], "tracks": {}, "milestones": {}, "tasks": {},
                "oob_tasks": {}, "branches": {}}
    with open(path) as f:
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


def save_project_json(project, data):
    with open(project_json_path(project), "w") as f:
        json.dump(data, f, indent=2)


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Task files
# ---------------------------------------------------------------------------

def task_file(project, t_key, slug):
    return os.path.join(milestone_path(project, t_key), f"{slug}.md")


def read_task_status(path):
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        for line in f:
            m = re.match(r"^Status:\s*(.+)$", line.strip())
            if m:
                return m.group(1).strip()
    return "X"


def read_task_deps(path):
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        for line in f:
            m = re.match(r"^Dependencies:\s*\[(.*)\]", line.strip())
            if m:
                raw = m.group(1).strip()
                return [d.strip() for d in raw.split(",") if d.strip()] if raw else []
    return []


def write_task_status(path, new_status):
    with open(path) as f:
        content = f.read()
    content = re.sub(r"^Status:.*$", f"Status: {new_status}", content, flags=re.MULTILINE)
    with open(path, "w") as f:
        f.write(content)


def order_of(data, t_key, oob=False):
    key = "oob_tasks" if oob else "tasks"
    return data[key].setdefault(t_key, [])


def label(t_key):
    """Display form of a t_key — track/milestone."""
    parts = t_key.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else t_key


# ---------------------------------------------------------------------------
# Record helpers
# ---------------------------------------------------------------------------

def new_mid(branches):
    while True:
        mid = "branch--" + secrets.token_hex(4)
        if mid not in branches:
            return mid


def record_or_fail(data, mid):
    rec = data["branches"].get(mid)
    if rec is None:
        fail(f"no branch record '{mid}' in this project.")
    return rec


def parent_chain(data, mid):
    """Records from mid outward through parent, capped at HOP_CAP."""
    chain, seen, hops = [], set(), 0
    while mid and hops < HOP_CAP:
        if mid in seen:
            break
        rec = data["branches"].get(mid)
        if rec is None:
            break
        chain.append(rec)
        seen.add(mid)
        mid = rec.get("parent")
        hops += 1
    return chain


def record_for_destination(data, t_key, open_only=False):
    for rec in data["branches"].values():
        if rec.get("destination") != t_key:
            continue
        if open_only and rec.get("state") != "open":
            continue
        return rec
    return None


def closing_index(data, rec):
    order = order_of(data, rec["destination"], rec.get("oob", False))
    return order.index(rec["id"]) if rec["id"] in order else len(order)


def is_exhausted(project, data, rec):
    """FR-7 — no workable entry above the closing marker."""
    order = order_of(data, rec["destination"], rec.get("oob", False))
    above = order[:closing_index(data, rec)]
    slugs, _ = split_markers(above)
    statuses = {}
    for slug in slugs:
        statuses[slug] = (read_task_status(task_file(project, rec["destination"], slug)) or "x").lower()
    for slug in slugs:
        if statuses[slug] not in WORKABLE:
            continue
        deps = read_task_deps(task_file(project, rec["destination"], slug))
        if all(statuses.get(d) == "done" for d in deps):
            return False
    return True


def drift_lines(project, data):
    """Every inconsistency the record set carries. Never repaired."""
    out = []
    branches = data["branches"]
    for mid, rec in branches.items():
        origin_order = data["tasks"].get(rec.get("origin", ""), [])
        dest_order = order_of(data, rec.get("destination", ""), rec.get("oob", False))
        open_present = mid in origin_order
        close_present = mid in dest_order
        if not open_present and not close_present:
            out.append(f"{mid}: the record appears in neither order array.")
        elif not open_present:
            anchor = rec.get("origin_anchor")
            idx = origin_order.index(anchor) if anchor in origin_order else len(origin_order)
            out.append(
                f"{mid}: open end missing from tasks[\"{rec.get('origin')}\"]; it belongs at index {idx}."
            )
        elif not close_present:
            key = "oob_tasks" if rec.get("oob") else "tasks"
            out.append(
                f"{mid}: closing end missing from {key}[\"{rec.get('destination')}\"]; "
                f"it belongs at index {len(dest_order)}."
            )
        expected = None
        for other_mid, other in branches.items():
            if other_mid != mid and other.get("destination") == rec.get("origin"):
                expected = other_mid
                break
        if rec.get("parent") != expected:
            out.append(
                f"{mid}: parent is {rec.get('parent')!r} but the record whose destination "
                f"is '{rec.get('origin')}' is {expected!r}."
            )
        for field in ("origin", "destination"):
            t_key = rec.get(field)
            if t_key and not os.path.isdir(milestone_path(project, t_key)):
                out.append(f"{mid}: {field} '{t_key}' has no directory.")
        if len(parent_chain(data, mid)) >= HOP_CAP:
            out.append(f"{mid}: parent chain exceeds {HOP_CAP} hops.")
    for t_key, order in list(data["tasks"].items()) + list(data["oob_tasks"].items()):
        for slug in order:
            if is_marker(slug) and slug not in branches:
                out.append(f"{slug}: marker row in '{t_key}' has no record.")
    return out


def current_position(project, data):
    """§7 — the milestone holding a doing task, else the newest open record's destination."""
    for t_key, order in data["tasks"].items():
        slugs, _ = split_markers(order)
        for slug in slugs:
            status = read_task_status(task_file(project, t_key, slug))
            if status and status.lower() == "doing":
                return t_key
    newest = None
    for order, rec in enumerate(data["branches"].values()):
        if rec.get("state") != "open":
            continue
        key = (rec.get("opened", ""), order)
        if newest is None or key >= newest[0]:
            newest = (key, rec)
    return newest[1]["destination"] if newest else None


# ---------------------------------------------------------------------------
# open
# ---------------------------------------------------------------------------

def remove_marker_rows(data, rec):
    mid = rec["id"]
    for key in ("tasks", "oob_tasks"):
        for order in data[key].values():
            while mid in order:
                order.remove(mid)


def cmd_open(args):
    validate_slug(args.project, "project slug")
    validate_slash_path(args.origin, 3, "origin path")
    validate_slash_path(args.destination, 3, "destination path")

    origin, dest = args.origin, args.destination
    data = load_project_json(args.project)

    # --- refusals, before any write -------------------------------------
    if origin == dest and not args.oob:
        fail(f"'{dest}' is the origin milestone — a same-milestone destination never branches.")

    existing = record_for_destination(data, dest)
    if existing is not None:
        print(
            f"'{label(dest)}' already returns through {existing['id']} — "
            f"origin {existing['origin']}, anchor {existing.get('origin_anchor')}."
        )
        sys.exit(1)

    origin_rec = record_for_destination(data, origin)
    if origin_rec is not None:
        reachable = set()
        for rec in parent_chain(data, origin_rec["id"]):
            reachable.add(rec.get("origin"))
            reachable.add(rec.get("destination"))
        if dest in reachable:
            fail(f"'{dest}' is already in this branch's origin chain — that would close a loop.")

    for t_key, what in ((origin, "origin"), (dest, "destination")):
        if not os.path.isdir(milestone_path(args.project, t_key)):
            fail(f"{what} milestone '{t_key}' does not exist.")

    # --- placement, pause, anchor ---------------------------------------
    mid = new_mid(data["branches"])
    origin_order = order_of(data, origin)

    doing_index = None
    doing_slug = None
    prior_status = None
    for idx, slug in enumerate(origin_order):
        if is_marker(slug):
            continue
        status = read_task_status(task_file(args.project, origin, slug))
        if status and status.lower() == "doing":
            doing_index, doing_slug, prior_status = idx, slug, status
            break

    if doing_slug is not None:
        write_task_status(task_file(args.project, origin, doing_slug), "PAUSED")
        origin_order.insert(doing_index, mid)
    else:
        origin_order.insert(insert_limit(data, origin, origin_order, False), mid)

    anchor = None
    marker_at = origin_order.index(mid)
    following = origin_order[marker_at + 1:]
    if following:
        head = following[0]
        if not is_marker(head):
            status = read_task_status(task_file(args.project, origin, head))
            if status and status.lower() == "paused":
                anchor = head
    if anchor is None:
        for slug in following:
            if is_marker(slug):
                continue
            status = read_task_status(task_file(args.project, origin, slug))
            if status and status.lower() == "pending":
                anchor = slug
                break

    dest_order = order_of(data, dest, args.oob)
    dest_order.append(mid)

    parent = None
    for other_mid, other in data["branches"].items():
        if other.get("destination") == origin:
            parent = other_mid
            break

    data["branches"][mid] = {
        "id": mid,
        "origin": origin,
        "origin_anchor": anchor,
        "anchor_prior_status": prior_status,
        "destination": dest,
        "oob": bool(args.oob),
        "parent": parent,
        "state": "open",
        "opened": datetime.date.today().isoformat(),
    }
    save_project_json(args.project, data)

    undo = f"manage_branches.py drop {args.project} {mid}"
    if anchor:
        print(
            f"Branched to {label(dest)} — {label(origin)} · {anchor} is paused "
            f"and holds the return. Undo: {undo}"
        )
    else:
        print(
            f"Branched to {label(dest)} — no task holds the return, so it targets "
            f"the {label(origin)} milestone. Undo: {undo}"
        )


def insert_limit(data, t_key, order, oob):
    """Positions available above a trailing closing marker in this array (FR-5)."""
    if order and is_marker(order[-1]):
        rec = data.get("branches", {}).get(order[-1])
        if rec and rec.get("destination") == t_key and bool(rec.get("oob")) == bool(oob):
            return len(order) - 1
    return len(order)


# ---------------------------------------------------------------------------
# close / drop
# ---------------------------------------------------------------------------

def cmd_close(args):
    validate_slug(args.project, "project slug")
    data = load_project_json(args.project)
    rec = record_or_fail(data, args.mid)
    rec["state"] = "closed"
    save_project_json(args.project, data)
    print(f"Closed {args.mid} — {label(rec['destination'])} no longer returns to {label(rec['origin'])}.")


def restore_anchor(project, rec):
    anchor = rec.get("origin_anchor")
    prior = rec.get("anchor_prior_status")
    if not anchor or not prior:
        return
    path = task_file(project, rec["origin"], anchor)
    if os.path.isfile(path):
        write_task_status(path, prior)


def cmd_drop(args):
    validate_slug(args.project, "project slug")
    data = load_project_json(args.project)
    rec = record_or_fail(data, args.mid)
    remove_marker_rows(data, rec)
    restore_anchor(args.project, rec)
    data["branches"].pop(args.mid, None)
    save_project_json(args.project, data)
    print(f"Dropped {args.mid} — {label(rec['origin'])} resumes where it left off.")


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------

def describe(project, data, rec):
    out = {f: rec.get(f) for f in RECORD_FIELDS}
    out["exhausted"] = is_exhausted(project, data, rec)
    return out


def resolve_return(project, data):
    """FR-8 / FR-17 — walk home from the current position, one announced hop per level."""
    position = current_position(project, data)
    hops, answer, changed = [], None, False

    for _ in range(HOP_CAP):
        rec = record_for_destination(data, position, open_only=True)
        if rec is None or not is_exhausted(project, data, rec):
            break

        anchor = rec.get("origin_anchor")
        origin_order = data["tasks"].get(rec["origin"], [])
        anchor_live = bool(anchor) and anchor in origin_order and os.path.isfile(
            task_file(project, rec["origin"], anchor)
        )

        if anchor_live:
            hop = {"mid": rec["id"], "origin": rec["origin"], "origin_anchor": anchor, "drift": None}
            print(f"{label(rec['destination'])} is done; back to {label(rec['origin'])} · {anchor}.")
            rec["state"] = "closed"
        else:
            hop = {
                "mid": rec["id"], "origin": rec["origin"], "origin_anchor": None,
                "drift": f"anchor {anchor!r} is gone from {rec['origin']}",
            }
            print(
                f"{label(rec['destination'])} is done; the task that held the return is gone, "
                f"so back to the {label(rec['origin'])} milestone."
            )
            remove_marker_rows(data, rec)
            data["branches"].pop(rec["id"], None)

        changed = True
        hops.append(hop)
        answer = hop
        position = rec["origin"]
    else:
        hops.append({"mid": None, "origin": position, "origin_anchor": None,
                     "drift": f"return walk exceeded {HOP_CAP} hops"})
        print(f"Return walk exceeded {HOP_CAP} hops and stopped at {label(position)}.")

    if changed:
        save_project_json(project, data)

    return {"position": position, "hops": hops,
            "mid": answer["mid"] if answer else None,
            "origin": answer["origin"] if answer else position,
            "origin_anchor": answer["origin_anchor"] if answer else None,
            "drift": answer["drift"] if answer else None}


def cmd_show(args):
    validate_slug(args.project, "project slug")
    data = load_project_json(args.project)

    if args.ret:
        payload = resolve_return(args.project, data)
    elif args.mid:
        rec = record_or_fail(data, args.mid)
        payload = describe(args.project, data, rec)
    else:
        payload = {
            "position": current_position(args.project, data),
            "branches": [describe(args.project, data, rec) for rec in data["branches"].values()],
        }

    for line in drift_lines(args.project, data):
        print(f"Drift: {line}", file=sys.stderr)
    payload["drift_report"] = drift_lines(args.project, data)
    print(json.dumps(payload, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Manage tasky branch-and-return records.")
    sub = parser.add_subparsers(dest="command")

    p_open = sub.add_parser("open", help="Open a branch from an origin milestone to a destination")
    p_open.add_argument("project")
    p_open.add_argument("origin")
    p_open.add_argument("destination")
    p_open.add_argument("--oob", action="store_true",
                        help="Place the closing marker in the destination's out-of-band order")

    p_close = sub.add_parser("close", help="Mark a branch closed")
    p_close.add_argument("project")
    p_close.add_argument("mid")

    p_drop = sub.add_parser("drop", help="Remove a branch, its rows, and restore the anchor's status")
    p_drop.add_argument("project")
    p_drop.add_argument("mid")

    p_show = sub.add_parser("show", help="Print branch records as JSON")
    p_show.add_argument("project")
    p_show.add_argument("mid", nargs="?")
    p_show.add_argument("--return", dest="ret", action="store_true",
                        help="Resolve and walk the return target from the current position")

    args = parser.parse_args()

    if args.command == "open":
        cmd_open(args)
    elif args.command == "close":
        cmd_close(args)
    elif args.command == "drop":
        cmd_drop(args)
    elif args.command == "show":
        cmd_show(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
