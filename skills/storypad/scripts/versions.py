"""Versions: each state a story's, series' or world's text files were in, kept in its versions/ folder. The state a
command leaves is kept as it ends; a change made outside storypad, before the next command writes. A version is
named on request, listed, shown, compared with another or the files now, and restored.

versions/<number>/ or versions/<name>/ holds the text files at their paths and version.json: when, by what, what
changed, and every other file of the folder by path and size, never copied.
"""

import datetime
import difflib
import json
import os
import re
import shlex
import shutil
from pathlib import Path

import storyfile
from storyfile import TimelineError

FOLDER = 'versions'
INFO = 'version.json'
MARKERS = ('index.md', 'series.md', 'world.md')
MEDIA = ('assets', 'takes', 'build')
NAME = re.compile(r'^[A-Za-z][A-Za-z0-9._-]*$')

run = None


def marker(folder):
    return next((m for m in MARKERS if (folder / m).is_file()), None)


def contents(root):
    """root's files as (text, other), each {posix path: Path}: text is every .md outside assets/, takes/ and build/;
    versions/, hidden files and the stories and series inside a world or series are left out."""
    text, other = {}, {}
    for top, dirs, names in os.walk(root):
        here = Path(top)
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and not (
            here == root and (d == FOLDER or d not in MEDIA and marker(here / d))))
        media = bool(set(here.relative_to(root).parts) & set(MEDIA))
        for n in sorted(names):
            if not n.startswith('.'):
                (text if n.endswith('.md') and not media else other)[(here / n).relative_to(root).as_posix()] = here / n
    return text, other


def read(files):
    return {rel: p.read_bytes() for rel, p in files.items()}


def changes(old, new):
    """What changed from `old` to `new`, both {path: bytes}, on one line."""
    parts = []
    for word, rels in (('changed', [r for r in new if r in old and new[r] != old[r]]),
                       ('added', [r for r in new if r not in old]), ('removed', [r for r in old if r not in new])):
        if rels:
            parts.append(f"{word} {', '.join(rels[:4])}" + (f' and {len(rels) - 4} more' if len(rels) > 4 else ''))
    return '; '.join(parts) or 'no change'


def entry(root, ref):
    folder = root / FOLDER / ref
    if not ref or ref != Path(ref).name or not (folder / INFO).is_file():
        known = ', '.join(e['id'] for e in entries(root)[:8]) or 'none yet'
        raise TimelineError(f'no version {ref!r} in {root}; newest: {known}')
    return dict(json.loads((folder / INFO).read_text(encoding='utf-8')), id=ref, folder=folder)


def entries(root):
    """Every version of root, newest first."""
    found = [entry(root, p.name) for p in (root / FOLDER).iterdir() if (p / INFO).is_file()] \
        if (root / FOLDER).is_dir() else []
    return sorted(found, key=lambda e: datetime.datetime.fromisoformat(e['saved']), reverse=True)


def kept(e):
    """A version's text files, {path: bytes}."""
    return read({p.relative_to(e['folder']).as_posix(): p for p in sorted(e['folder'].rglob('*'))
                 if p.is_file() and p.name != INFO})


def last(root):
    """The newest numbered version: the state storypad last left or found."""
    numbered = [int(p.name) for p in (root / FOLDER).glob('*') if p.name.isdigit() and (p / INFO).is_file()] \
        if (root / FOLDER).is_dir() else []
    return entry(root, str(max(numbered))) if numbered else None


def keep(root, source, name=None, **info):
    """source's text files, and its other files by path and size, kept as a version of root: `name`, else the next
    number."""
    text, other = contents(source)
    if name:
        folder = root / FOLDER / name
        folder.mkdir(parents=True)
    else:
        n = max([int(p.name) for p in (root / FOLDER).glob('*') if p.name.isdigit()] + [0])
        while True:
            n += 1
            folder = root / FOLDER / str(n)
            try:
                folder.mkdir(parents=True)
                break
            except FileExistsError:
                pass
    for rel, p in text.items():
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, folder / rel)
    info.update(saved=datetime.datetime.now().astimezone().isoformat(timespec='microseconds'),
                media=[{'path': rel, 'bytes': p.stat().st_size} for rel, p in other.items()])
    (folder / INFO).write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    return folder.name


def start(argv):
    """Keep versions for this command: each folder it writes text into is watched from its first write."""
    global run
    run = {'argv': list(argv), 'roots': []}
    storyfile.before_save = watched


def watched(path):
    if path.suffix == '.md':
        root = next((p for p in (path.parent, path.parent.parent if path.parent.name == 'scenes' else None)
                     if p and marker(p)), None)
        if root:
            watch(root)


def watch(root):
    """From here on this command's changes to root are kept; a change made outside storypad is kept first."""
    root = root.resolve()
    if root in run['roots']:
        return
    was, now = last(root), read(contents(root)[0])
    if was is None:
        keep(root, root, by='outside', summary='first kept')
    elif kept(was) != now:
        keep(root, root, by='outside', summary=changes(kept(was), now))
    run['roots'].append(root)


def finish():
    """Each watched folder whose text files the command changed: its new state kept."""
    for root in run['roots'] if run else []:
        if marker(root):
            was, now = kept(last(root)), read(contents(root)[0])
            if was != now:
                keep(root, root, by='command', command=run['argv'], summary=changes(was, now))


def root_of(path):
    if not marker(path):
        raise TimelineError(f'{path} holds no index.md, series.md or world.md; name a story, series or world')
    return path.resolve()


def save_version(path, name, note=None, film=None, source=None):
    """The files now, or those of `source`, kept as the version `name`, with a note and the film they made."""
    root = root_of(path)
    if not NAME.match(name or ''):
        raise TimelineError(f'{name!r} is not a version name; use a letter, then letters, digits, . _ or -, as v6')
    if (root / FOLDER / name).exists():
        raise TimelineError(f'{name} is a version already; versions are kept as saved, give another name')
    if source is not None and marker(source) != marker(root):
        raise TimelineError(f'{source} holds no {marker(root)}; --from takes a folder laid out like {path}')
    if film and not Path(film).exists():
        raise TimelineError(f'no film at {film}')
    if film:
        film = Path(film).resolve()
        film = film.relative_to(root).as_posix() if film.is_relative_to(root) else film.as_posix()
    keep(root, (source or root).resolve(), name, by='name', note=(note or '').strip(), film=film or '',
         **{'from': source.resolve().as_posix() if source else ''})
    return show_version(path, name)


def what(e):
    if e['by'] == 'command':
        return shlex.join(e['command'])
    if e['by'] == 'outside':
        return 'changed outside storypad'
    return ' · '.join([f"saved as {e['id']}"] + [f'{k}: {e[k]}' for k in ('film', 'from') if e.get(k)])


def line(e, width):
    return f"  {e['id']:<{width}}  {e['saved'][:16].replace('T', ' ')}  {what(e)}  · " \
           + (e.get('note') or e.get('summary') or '')


def version_list(path):
    root = root_of(path)
    found = entries(root)
    if not found:
        return f'  {path}: no versions yet'
    width = max(len(e['id']) for e in found)
    was = last(root)
    now = read(contents(root)[0])
    head = [f"  {'now':<{width}}  changed outside storypad since {was['id']}  · {changes(kept(was), now)}"] \
        if was and kept(was) != now else []
    return '\n'.join(head + [line(e, width) for e in found])


def show_version(path, ref, file=None):
    root = root_of(path)
    e = entry(root, ref)
    files = kept(e)
    if file:
        if file not in files:
            raise TimelineError(f"{ref} keeps no {file}; it keeps {', '.join(files)}")
        return files[file].decode('utf-8').rstrip('\n')
    gone = [m['path'] for m in e['media'] if not (root / m['path']).exists()]
    return '\n'.join([line(e, len(e['id'])), '', '  text: ' + ', '.join(files),
                      f"  other files: {len(e['media'])}" + (f"; missing now: {', '.join(gone)}" if gone else '')])


def diff_versions(path, ref, to=None):
    """ref against `to`, else against the files now, as a unified diff of each text file."""
    root = root_of(path)
    old = kept(entry(root, ref))
    new = kept(entry(root, to)) if to else read(contents(root)[0])
    out = []
    for rel in sorted(set(old) | set(new)):
        a, b = (f.get(rel, b'').decode('utf-8', 'replace').splitlines() for f in (old, new))
        out += difflib.unified_diff(a, b, f'{ref}/{rel}', f"{to or 'now'}/{rel}", lineterm='')
    return '\n'.join(out) or '  no difference'


def restore_version(path, ref):
    """ref's text files put back, each text file it doesn't keep removed; the state before is kept first."""
    root = root_of(path)
    e = entry(root, ref)
    files, now = kept(e), contents(root)[0]
    before = read(now)
    watch(root)
    for rel, data in files.items():
        if before.get(rel) != data:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            storyfile.save(root / rel, data)
    for rel in now:
        if rel not in files:
            now[rel].unlink()
    gone = [m['path'] for m in e['media'] if not (root / m['path']).exists()]
    return f'  restored {ref}: {changes(before, files)}' + (f"\n  missing now: {', '.join(gone)}" if gone else '')
