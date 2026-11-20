"""References: a file or link (an overarching spec, a design doc) attached to a roadmap, a track or a
milestone. Kept in the owner's own directory, in .references.json, as a list of {"name", "path",
"slots"?}, so renaming, moving or deleting the owner carries or removes them. A reference has no
tasks, no status and no count, and never enters a total."""

import glob
import json
import os

FILE = ".references.json"
MARK = "§"
BAR = "┄┄┄┄┄"


def read(owner_dir):
    path = os.path.join(owner_dir, FILE)
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return json.load(f)


def write(owner_dir, refs):
    path = os.path.join(owner_dir, FILE)
    if refs:
        with open(path + ".tmp", "w") as f:
            json.dump(refs, f, indent=2)
        os.replace(path + ".tmp", path)
    elif os.path.exists(path):
        os.remove(path)


def owners(roadmap_dir):
    """The roadmap's directory and each track or milestone directory under it that holds references."""
    pattern = os.path.join(glob.escape(roadmap_dir), "**", FILE)
    return [os.path.dirname(p) for p in sorted(glob.glob(pattern, recursive=True))]


def label(ref):
    scope = ref.get("scope")
    return f"{scope} › {ref['name']}" if scope else ref["name"]


def band(roadmap_dir, tracks, milestones=()):
    """A view's band: the roadmap's references, then for each track, in the order given, its own and
    those of its milestones in (track, milestone) order."""
    def owned(*parts):
        return [dict(r, scope=parts[-1] if parts else None) for r in read(os.path.join(roadmap_dir, *parts))]
    out = owned()
    for t in tracks:
        out += owned(t)
        for mt, m in milestones:
            if mt == t:
                out += owned(t, m)
    return out


def path_lines(refs):
    width = max((len(label(r)) for r in refs), default=0)
    return [f" {MARK} {label(r).ljust(width)}   {r['path']}" for r in refs]


def add(roadmap_dir, owner_dir, ref):
    if any(r["name"] == ref["name"] for d in owners(roadmap_dir) for r in read(d)):
        raise ValueError(f"reference '{ref['name']}' already exists in roadmap "
                         f"'{os.path.basename(roadmap_dir)}'; remove it first")
    write(owner_dir, read(owner_dir) + [ref])


def remove(roadmap_dir, name):
    found = False
    for d in owners(roadmap_dir):
        stored = read(d)
        kept = [r for r in stored if r["name"] != name]
        if len(kept) < len(stored):
            write(d, kept)
            found = True
    if not found:
        raise ValueError(f"no reference '{name}' in roadmap '{os.path.basename(roadmap_dir)}'")
