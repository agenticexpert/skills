#!/usr/bin/env python3
"""
position.py — Where the work stands, derived from the snapshot on every read.

The snapshot is project.json's order arrays, milestone and track dependencies and
branch records, plus each task file's status, dependencies, criteria and Session
line. No pointer is stored: the task "next" lands on, the current milestone of a
track, the project's next task and the branch position are computed here, and every
view and "next" reads them from here.

Branch records are the one stored state that names a place. reconcile() brings
them back in line with their marker rows; settle() runs it after every write that
changes sequence, placement or status, and prints each contradiction the snapshot
holds with the task it resolves to. Neither ever writes a task file.
"""

import json
import os
import re

from tasky_config import TASKY_ROOT
from claims import other_holder

MID_RE = re.compile(r"^branch--[0-9a-f]{8}$")
STATUS_RE = re.compile(r"^Status:[ \t]*(.+)$", re.MULTILINE)
DEPS_RE = re.compile(r"^Dependencies:[ \t]*\[(.*)\][ \t]*$", re.MULTILINE)
CRITERION_RE = re.compile(r"^(\s*-\s*\[)([ xX])(\]\s*)(.*)$")

OPEN = ("todo", "pending", "paused")
WORKABLE = OPEN + ("doing",)
HOP_CAP = 64


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


def label(t_key):
    """Display form of a t_key — track/milestone."""
    parts = t_key.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else t_key


def load_project(project):
    path = os.path.join(TASKY_ROOT, project, "project.json")
    data = {}
    if os.path.isfile(path):
        with open(path) as f:
            data = json.load(f)
    for key in ("tracks", "milestones", "tasks", "oob_roadmaps", "oob_tracks",
                "oob_milestones", "oob_tasks", "milestone_deps", "branches"):
        data.setdefault(key, {})
    data.setdefault("roadmaps", [])
    return data


def save_project(project, data):
    with open(os.path.join(TASKY_ROOT, project, "project.json"), "w") as f:
        json.dump(data, f, indent=2)


def criteria_lines(content):
    """(line index, checked, text) for each checkbox under ## Criteria."""
    out, inside = [], False
    for i, line in enumerate(content.split("\n")):
        if line.startswith("## "):
            inside = line.strip() == "## Criteria"
            continue
        m = CRITERION_RE.match(line) if inside else None
        if m:
            out.append((i, m.group(2) != " ", m.group(4).strip()))
    return out


def milestone_dir(project, t_key):
    return os.path.join(TASKY_ROOT, project, *t_key.split("/"))


def read_task(path):
    """Status, dependencies, criteria count and hold of one task file; None when the file is gone."""
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        content = f.read()
    status, deps = STATUS_RE.search(content), DEPS_RE.search(content)
    items = criteria_lines(content)
    return {
        "status": status.group(1).strip().lower() if status else "x",
        "deps": [d.strip() for d in deps.group(1).split(",") if d.strip()] if deps else [],
        "criteria": (len(items), sum(1 for _, checked, _ in items if checked)),
        "held": bool(other_holder(path)),
    }


def tasks_in(project, data, t_key, oob=False, stop=None):
    """The milestone's tasks in sequence order, read from disk; marker rows and missing files
    skipped, the list ending above the marker row `stop` when given."""
    order = list(data["oob_tasks" if oob else "tasks"].get(t_key, []))
    mdir = milestone_dir(project, t_key)
    if stop in order:
        order = order[:order.index(stop)]
    if not order and not oob and os.path.isdir(mdir):
        out_of_band = data["oob_tasks"].get(t_key, [])
        order = sorted(f[:-3] for f in os.listdir(mdir)
                       if f.endswith(".md") and not f.startswith(".") and f[:-3] not in out_of_band)
    out = []
    for slug in order:
        task = None if is_marker(slug) else read_task(os.path.join(mdir, f"{slug}.md"))
        if task:
            task["slug"] = slug
            out.append(task)
    return out


def progress(tasks):
    """(status, done, total) of a milestone's tasks, a task with no status not counted:
    done when every counted task is DONE, todo while each is TODO, PENDING or PAUSED,
    else doing."""
    counted = [t for t in tasks if t["status"] != "x"]
    done = sum(1 for t in counted if t["status"] == "done")
    if counted and done == len(counted):
        return "done", done, len(counted)
    return ("todo" if all(t["status"] in OPEN for t in counted) else "doing"), done, len(counted)


def is_done(tasks):
    return progress(tasks)[0] == "done"


def destination_progress(project, data, t_key):
    """progress() of a whole milestone, its out-of-band tasks counted."""
    return progress(tasks_in(project, data, t_key) + tasks_in(project, data, t_key, oob=True))


def milestone_state(tasks, where):
    """(pointer task or None, contradiction lines) for one milestone.

    The pointer is the first DOING task whose dependencies are DONE and whose criteria
    are not all checked; with none, the first TODO, PENDING or PAUSED task from the top
    whose dependencies are DONE. A milestone holding another session's task has none."""
    index = {t["slug"]: i for i, t in enumerate(tasks)}
    done = {t["slug"] for t in tasks if t["status"] == "done"}
    found = []
    for i, t in enumerate(tasks):
        for dep in t["deps"]:
            if dep not in index:
                found.append(f"`{t['slug']}` depends on `{dep}`, which is not in this milestone")
            elif dep not in done and t["status"] in ("doing", "ready", "done"):
                found.append(f"`{t['slug']}` is {t['status'].upper()} but its dependency `{dep}` is not DONE")
            elif index[dep] > i:
                found.append(f"`{t['slug']}` sits above its dependency `{dep}`")
    finished = [t for t in tasks if t["status"] == "doing" and t["criteria"][0]
                and t["criteria"][0] == t["criteria"][1]]
    found += [f"`{t['slug']}` is DOING with every criterion checked" for t in finished]
    doing = [t for t in tasks if t["status"] == "doing" and not t["held"]]
    if len(doing) > 1:
        found.append(f"{len(doing)} tasks are DOING at once: " + ", ".join(f"`{t['slug']}`" for t in doing))

    pointer = None
    if not any(t["held"] for t in tasks):
        unblocked = [t for t in tasks if all(d in done for d in t["deps"])]
        pointer = (next((t for t in unblocked if t in doing and t not in finished), None)
                   or next((t for t in unblocked if t["status"] in OPEN), None))
    then = f"next there is `{pointer['slug']}`" if pointer else "nothing there is ready to start"
    return pointer, [f"In {where}, {line}; {then}." for line in found]


def sequence_state(project, data, t_key, oob=False, stop=None, seen=()):
    """(place or None, contradiction lines) for one milestone, its marker rows in sequence.

    A marker row leading out of the milestone stands in sequence for its destination
    while that destination is unfinished and has a place of its own. The place is the
    first DOING item from the top, else the first open one: {"t_key", "task", "oob",
    "mid", "doing"}, t_key the milestone holding the task and mid the marker row it sits
    behind, None for the milestone's own task. None while another session holds a task
    here. The lines are this milestone's only."""
    tasks = tasks_in(project, data, t_key, oob, stop)
    pointer, problems = milestone_state(tasks, label(t_key))
    if any(t["held"] for t in tasks):
        return None, problems
    order = list(data["oob_tasks" if oob else "tasks"].get(t_key, []))
    if stop in order:
        order = order[:order.index(stop)]
    items = []
    if pointer:
        at = order.index(pointer["slug"]) if pointer["slug"] in order else 0
        items.append((at, {"t_key": t_key, "task": pointer, "oob": oob, "mid": None,
                           "doing": pointer["status"] == "doing"}))
    for at, mid in enumerate(order):
        rec = data["branches"].get(mid) if is_marker(mid) else None
        dest = rec.get("destination") if rec else None
        if not dest or dest == t_key or dest in seen or len(seen) >= HOP_CAP:
            continue
        if destination_progress(project, data, dest)[0] == "done":
            continue
        inner, _ = sequence_state(project, data, dest, rec.get("oob", False), mid, seen + (t_key,))
        if inner:
            items.append((at, dict(inner, mid=mid)))
    doing = [item for item in items if item[1]["doing"]]
    pick = min(doing or items, key=lambda item: item[0], default=None)
    return (pick[1] if pick else None), problems


def track_state(project, data, roadmap, track):
    """The current milestone of one track: {t_key, task, doing, problems, done}.

    `doing` lists every milestone (sequenced or out of band) whose pointer is a DOING
    task; the current milestone is the first of them, else the sequence_state place of the
    first sequenced milestone from the top with one and every milestone dependency done,
    which is a branch destination when a marker row there leads the sequence. `problems` holds
    (t_key, line) pairs."""
    m_key = f"{roadmap}/{track}"
    oob = data["oob_milestones"].get(m_key, [])
    sequenced = [m for m in data["milestones"].get(m_key, []) if m not in oob]
    problems, doing, states, finished = [], [], [], set()
    for slug in sequenced + list(oob):
        t_key = f"{m_key}/{slug}"
        if not os.path.isdir(milestone_dir(project, t_key)):
            continue
        tasks = tasks_in(project, data, t_key)
        pointer, lines = milestone_state(tasks, label(t_key))
        problems += [(t_key, line) for line in lines]
        if is_done(tasks):
            finished.add(slug)
        if pointer and pointer["status"] == "doing":
            doing.append((t_key, pointer))
        if slug in sequenced:
            place = sequence_state(project, data, t_key)[0]
            states.append((slug, t_key, (place["t_key"], place["task"]) if place else None))

    position = {slug: i for i, slug in enumerate(sequenced)}
    current = doing[0] if doing else None
    for slug, t_key, at in states:
        deps = data["milestone_deps"].get(t_key, [])
        for dep in deps:
            if dep not in position:
                line = f"milestone `{slug}` depends on `{dep}`, which is not in this track"
            elif position[dep] > position[slug]:
                line = f"milestone `{slug}` sits above its dependency `{dep}`"
            else:
                continue
            problems.append((m_key, line))
        if current is None and at and all(d in finished for d in deps):
            current = at

    where = f"the current milestone is `{label(current[0])}`" if current else "no milestone is ready to start"
    problems = [(key, line if key != m_key else f"In {track}, {line}; {where}.") for key, line in problems]
    return {"t_key": current[0] if current else None, "task": current[1] if current else None,
            "doing": doing, "problems": problems,
            "done": bool(sequenced) and finished.issuperset(sequenced)}


def tracks_in_order(data):
    """(roadmap, track, sequenced) for every track: roadmaps then tracks in order, out-of-band last."""
    oob_roadmaps = [r for rs in data["oob_roadmaps"].values() for r in rs]
    for roadmap in list(data["roadmaps"]) + [r for r in oob_roadmaps if r not in data["roadmaps"]]:
        oob_tracks = data["oob_tracks"].get(roadmap, [])
        order = [t for t in data["tracks"].get(roadmap, {}).get("order", []) if t not in oob_tracks]
        for track in order + list(oob_tracks):
            yield roadmap, track, roadmap not in oob_roadmaps and track not in oob_tracks


def project_state(project, data):
    """{t_key, task, problems}: where "next" lands in the project.

    A DOING task wins, the first in sequence. With none, the innermost open branch: its
    destination while it holds workable tasks, else the return it walks to. With
    neither, the first track from the top whose track dependencies are done, at its
    current milestone."""
    states = [(roadmap, track, sequenced, track_state(project, data, roadmap, track))
              for roadmap, track, sequenced in tracks_in_order(data)]
    done = {(roadmap, track): state["done"] for roadmap, track, _, state in states}
    problems, doing, first = [], [], None
    for roadmap, track, sequenced, state in states:
        problems += state["problems"]
        doing += state["doing"]
        deps = data["tracks"].get(roadmap, {}).get("deps", {}).get(track, [])
        if (first is None and sequenced and state["t_key"]
                and all(done.get((roadmap, d), True) for d in deps)):
            first = (state["t_key"], state["task"])

    if len(doing) > 1:
        names = ", ".join(f"`{label(t_key)}`" for t_key, _ in doing)
        problems.append(("", f"DOING tasks sit in {len(doing)} milestones at once: {names}; "
                             f"next is `{doing[0][1]['slug']}` in `{label(doing[0][0])}`."))
    at = doing[0] if doing else (branch_next(project, data) or first)
    return {"t_key": at[0] if at else None, "task": at[1] if at else None, "problems": problems}


def scoped(problems, scopes):
    """The lines whose place is one of the scopes, inside one, or holds one."""
    keep = []
    for key, line in problems:
        for scope in scopes:
            if key == scope or key.startswith(scope + "/") or scope.startswith(key + "/") or not key or not scope:
                keep.append(line)
                break
    return keep


def current_position(project, data):
    """The milestone holding this session's DOING task, first in sequence; else the newest
    open branch's destination; else None."""
    for roadmap, track, _ in tracks_in_order(data):
        m_key = f"{roadmap}/{track}"
        oob = data["oob_milestones"].get(m_key, [])
        for slug in [m for m in data["milestones"].get(m_key, []) if m not in oob] + list(oob):
            t_key = f"{m_key}/{slug}"
            if any(t["status"] == "doing" and not t["held"] for t in tasks_in(project, data, t_key)):
                return t_key
    newest = None
    for order, rec in enumerate(data["branches"].values()):
        if rec.get("state") != "open":
            continue
        key = (rec.get("opened", ""), order)
        if newest is None or key >= newest[0]:
            newest = (key, rec)
    return newest[1]["destination"] if newest else None


def open_record_into(data, t_key):
    return next((rec for rec in data["branches"].values()
                 if rec.get("destination") == t_key and rec.get("state") == "open"), None)


def exhausted(project, data, rec):
    """No workable task above the branch's closing marker."""
    above = tasks_in(project, data, rec["destination"], rec.get("oob", False), stop=rec["id"])
    done = {t["slug"] for t in above if t["status"] == "done"}
    return not any(t["status"] in WORKABLE and all(d in done for d in t["deps"]) for t in above)


def return_walk(project, data, start):
    """([(record, live anchor or None)] for each exhausted branch level from start outward,
    innermost first; True when the walk stopped at HOP_CAP)."""
    hops, at = [], start
    for _ in range(HOP_CAP):
        rec = open_record_into(data, at)
        if rec is None or not exhausted(project, data, rec):
            return hops, False
        anchor = rec.get("origin_anchor")
        live = bool(anchor) and anchor in data["tasks"].get(rec["origin"], []) and os.path.isfile(
            os.path.join(milestone_dir(project, rec["origin"]), f"{anchor}.md"))
        hops.append((rec, anchor if live else None))
        at = rec["origin"]
    return hops, True


def branch_next(project, data):
    """(t_key, task) the innermost open branch leads to, or None with no open branch."""
    start = current_position(project, data)
    rec = open_record_into(data, start) if start else None
    if rec is None:
        return None
    hops, _ = return_walk(project, data, start)
    if not hops:
        place = sequence_state(project, data, start, rec.get("oob", False), rec["id"])[0]
        return (place["t_key"], place["task"]) if place else None
    last, anchor = hops[-1]
    held = next((t for t in tasks_in(project, data, last["origin"])
                 if t["slug"] == anchor and t["status"] in WORKABLE), None)
    if held:
        return last["origin"], held
    place = sequence_state(project, data, last["origin"])[0]
    return (place["t_key"], place["task"]) if place else None


def trailing_match(a, b):
    n = 0
    for x, y in zip(reversed(a.split("/")), reversed(b.split("/"))):
        if x != y:
            break
        n += 1
    return n


def remove_rows(data, mid):
    for kind in ("tasks", "oob_tasks"):
        for order in data[kind].values():
            while mid in order:
                order.remove(mid)


def reconcile(project, data):
    """Bring every branch record in line with its marker rows, which travel with their
    milestone through any move, rename or delete. Returns a plain line per repair; the
    caller saves. Task files are never touched."""
    lines, branches = [], data["branches"]
    rows = {}
    for kind in ("tasks", "oob_tasks"):
        for t_key, order in data[kind].items():
            for slug in order:
                if is_marker(slug):
                    rows.setdefault(slug, []).append((kind, t_key))

    for mid, found in rows.items():
        if mid not in branches:
            remove_rows(data, mid)
            lines.append(f"Removed a branch marker in {label(found[0][1])} that had no branch behind it.")

    for mid, rec in list(branches.items()):
        left = list(rows.get(mid, []))
        dest_kind = "oob_tasks" if rec.get("oob") else "tasks"
        ends = {"destination": (dest_kind, rec.get("destination")), "origin": ("tasks", rec.get("origin"))}
        placed = {}
        for end, row in ends.items():
            if row in left:
                left.remove(row)
                placed[end] = row[1]
        pairs = sorted(((trailing_match(key, ends[end][1] or ""), end, (kind, key))
                        for end in ends if end not in placed for kind, key in left if kind == ends[end][0]),
                       reverse=True)
        for _, end, row in pairs:
            if end not in placed and row in left:
                left.remove(row)
                placed[end] = row[1]

        if len(placed) < 2:
            remove_rows(data, mid)
            del branches[mid]
            gone = "destination" if "destination" not in placed else "origin"
            lines.append(f"Removed the branch {label(rec.get('origin', ''))} → {label(rec.get('destination', ''))}: "
                         f"its {gone} milestone is gone.")
            continue
        if (placed["origin"], placed["destination"]) != (rec.get("origin"), rec.get("destination")):
            rec["origin"], rec["destination"] = placed["origin"], placed["destination"]
            lines.append(f"The branch {label(rec['origin'])} → {label(rec['destination'])} moved with its milestones.")
        anchor = rec.get("origin_anchor")
        if anchor and anchor not in data["tasks"].get(rec["origin"], []):
            rec["origin_anchor"], rec["anchor_prior_status"] = None, None
            lines.append(f"`{anchor}` left {label(rec['origin'])}; the branch to {label(rec['destination'])} "
                         f"now returns to the {label(rec['origin'])} milestone.")
        closing = data[dest_kind][rec["destination"]]
        if closing[-1] != mid:
            closing.remove(mid)
            closing.append(mid)

    for mid, rec in branches.items():
        if rec.get("state") == "open":
            rec["parent"] = next((other for other, o in branches.items() if other != mid
                                  and o.get("state") == "open" and o.get("destination") == rec.get("origin")), None)
    return lines


def settle(project, scopes):
    """Run after every write that changes sequence, placement or status: reconcile the
    branch records, save when that changed them, then print one line per repair and one
    per contradiction within the scopes (t_key prefixes) with the task it resolves to."""
    if not os.path.isfile(os.path.join(TASKY_ROOT, project, "project.json")):
        return
    data = load_project(project)
    before = json.dumps(data, sort_keys=True)
    repairs = reconcile(project, data)
    if json.dumps(data, sort_keys=True) != before:
        save_project(project, data)
    for line in repairs + scoped(project_state(project, data)["problems"], scopes):
        print(line)
