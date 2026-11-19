"""A world: world.md, holding what its stories share (its assets and locations, its threads and events, the pins on
them, kept by command from any of its stories) and its timeline (the moments in order, and the moment each story is set at), and
the story and series folders inside it, found, started, read with it, listed, shown, drawn and checked. A story or
series in no world is the older layout.
"""

import datetime

import assets
import continuity
import timeline
from continuity import (edit_event, edit_thread, falls, find_moment, label, parse_world, place, settle, threads_text)
from episodes import episode_changed, is_series, read_series, save_series, series_doc, series_status
from scenes import old, open_counts, read_story, save_story, ticks, world_key, writable
from storyfile import (TimelineError, cell, dated, frontmatter, meta_pairs, name, put_sections, same, save, sections,
    slug, table, table_text, top)

DOC = 'world.md'
TIMELINE = ('Moment', 'Story', 'At', 'Note')
SECTIONS = ('Timeline', 'Threads', 'Events', 'Assets', 'Locations', 'Pins', 'Notes')


def is_world(path):
    return (path / DOC).is_file()


def world_of(path):
    """The world a story or series sits in: its folder's parent, for an episode its series' parent; None
    outside one."""
    parent = path.resolve().parent
    if is_series(parent):
        parent = parent.parent
    return parent if is_world(parent) else None


def in_world(path):
    """`path`, refused while it is in the older layout: a story or series in no world; an episode names its
    series."""
    if world_of(path) is None:
        at = path.parent if is_series(path.resolve().parent) else path
        raise TimelineError(old(at, 'it is in no world'))
    return path


def world_doc(path):
    """world.md, read: its title, its timeline's moments in order, its threads and events, its assets and
    locations, its pins (each from one of its series, threads or records, or over every story), and its series'
    names."""
    text = (path / DOC).read_text(encoding='utf-8')
    body, h = sections(text), top(text)
    head, rows = table(body.get('timeline'), TIMELINE)
    world = {'path': path, 'text': text, 'title': h.group(1) if h else path.name, 'key': '', 'moments_head': head,
             'moments': rows, 'series': [p.name for p in stories(path) if is_series(p)], **parse_world(body),
             **assets.parse_records(body)}
    world['pins_head'], world['pins'] = timeline.parse_pins(body.get('pins'), timeline.world_pin_end(world))
    return world


def world_at(path):
    """The world `path` is, or the one the story or series at `path` sits in, read."""
    return world_doc(path if is_world(path) else world_of(path))


def save_world(world):
    """world.md written back when its timeline, threads, events, records or pins changed."""
    bodies = {'Timeline': table_text(world['moments_head'], world['moments'], TIMELINE) if world['moments'] else None}
    bodies['Threads'], bodies['Events'] = threads_text(world)
    bodies['Assets'], bodies['Locations'] = assets.records_text(world)
    bodies['Pins'] = timeline.pins_table(world['pins_head'], world['pins'])
    text = dated(world['text'], put_sections(world['text'], SECTIONS, bodies))
    if text != world['text']:
        save(world['path'] / DOC, text)
        world['text'] = text


def story_at(path):
    """A story read with its world, and with its series' series.md when it is an episode."""
    parent, world = path.resolve().parent, world_of(path)
    world = world and world_doc(world)
    return read_story(path, series_doc(parent) if (path / 'index.md').is_file() and is_series(parent) else None,
                      world)


def series_at(path):
    """A series and its episodes read with their world."""
    world = world_of(path)
    return read_series(path, world and world_doc(world))


def story_changed(story):
    """After a change to `story`: series.md rewritten when it is an episode, world.md when a moment, an event or a
    thread's place in it followed a move."""
    episode_changed(story)
    if story['world']:
        settle(story)
        save_world(story['world'])


def worlds(root):
    return sorted(p for p in root.iterdir() if p.is_dir() and is_world(p)) if root.is_dir() else []


def stories(world):
    """The story and series folders in a world, by name."""
    return sorted(p for p in world.iterdir() if p.is_dir() and not p.name.startswith('.')
                  and ((p / 'index.md').is_file() or is_series(p)))


def readings(world):
    """Every story, series and episode of the world, read with it."""
    out = []
    for p in stories(world['path']):
        if is_series(p):
            s = read_series(p, world)
            out += [s] + s['episodes']
        else:
            out.append(read_story(p, None, world))
    return out


def docs_of(world):
    """Every story, series and episode of the world, each as (it, how a line about it starts: `<key>: `)."""
    return [(d, f"{d['key']}: ") for d in readings(world)]


def save_docs(docs):
    """Each story, series and episode of `docs` written, every story checked before the first write."""
    for d in docs:
        if 'episodes' not in d:
            writable(d)
    for d in docs:
        save_series(d) if 'episodes' in d else save_story(d)


def world_text(title):
    today = datetime.date.today().isoformat()
    return f'---\ntype: world\ncreated: {today}\nupdated: {today}\n---\n\n# {title}\n\n## Notes\n'


def new_place(root, text, when=None):
    """Where `new` puts a story or series titled `text`, as (its world, whether that world is new, its
    folder, its title, the moment named by `when`). `<world>/<title>` adds to a world already there; a bare
    title makes a world of the same name holding it."""
    world, slash, title = text.rpartition('/')
    title = name(title)
    if slash:
        at = root / (slug(world) or name(world))
        if not is_world(at):
            known = ', '.join(p.name for p in worlds(root)) or 'none yet'
            raise TimelineError(f'no world {world} in {root}; the worlds are {known}')
    else:
        at = root / (slug(title) or 'story')
        if at.exists():
            raise TimelineError(f'{at} is already there; ' + (f'add to that world as new {at.name}/<title>'
                                                                if is_world(at) else 'open it'))
        if when:
            raise TimelineError('a new world has no moments yet; make the story, add the moment with moment add, '
                                'then set it with when')
    path = at / (slug(title) or 'story')
    if path.exists():
        raise TimelineError(f'{path} is already there; open it')
    return at, not slash, path, title, when and find_moment(world_doc(at)['moments'], when)['moment']


def world_new(path, title):
    """A new world folder holding its world.md."""
    path.mkdir(parents=True)
    save(path / DOC, world_text(title))


def moment_users(world, moment):
    """What names `moment`: each story's and episode's when, each variation's From and each of the world's own
    events at it."""
    return [f"{d['key']} when" for d in readings(world) if same(d.get('when'), moment)] + \
        [f'@{assets.key(r)}' for r in world['records'] if r['kind'] == 'variation' and same(r['from'], moment)] + \
        [f'the event {label(e)}' for e in world['events'] if not e['story'] and same(e['at'], moment)]


def renamed(doc, old_name, new_name):
    """`doc`'s when moved from one moment's name to another; whether it was."""
    if same(doc.get('when'), old_name):
        doc['when'] = new_name
        return True
    return False


def story_in(world, key):
    """The story or episode at `key` in the world, read."""
    path = world['path'] / key
    if not (path / 'index.md').is_file():
        if is_series(path):
            raise TimelineError(f'{key} is a series; name one of its episodes, as {key}/ep-<key>')
        known = ', '.join(p.name for p in stories(world['path'])) or 'none yet'
        raise TimelineError(f'no story {key} in the world; its stories are {known}')
    return story_at(path)


def index_of(items, item):
    return next(i for i, x in enumerate(items) if x is item)


def edit_moment(world, a):
    """moment add|set|move|remove on a world; returns the stories, series and episodes changed with it, to be
    written."""
    ms = world['moments']
    if a.op == 'add':
        if any(m['moment'] and same(m['moment'], a.name) for m in ms):
            raise TimelineError(f'there is already a moment {a.name.strip()!r}')
        m = {'moment': name(a.name), 'story': '', 'at': '', 'note': ''}
        ms.insert(index_of(ms, find_moment(ms, a.before)) if a.before else len(ms), m)
    else:
        m = find_moment(ms, a.name)
    if a.op == 'move':
        at = index_of(ms, find_moment(ms, a.to))
        ms.remove(m)
        ms.insert(at, m)
        return []
    if a.op == 'remove':
        users = moment_users(world, m['moment'])
        if users:
            raise TimelineError(f"{m['moment']} is named by {', '.join(users)}; change those first")
        ms.remove(m)
        return []
    if a.story_key is not None or a.at is not None:
        key = m['story'] if a.story_key is None else a.story_key.strip().strip('/')
        at = m['at'] if a.at is None else a.at.strip()
        if not key:
            if at and a.at is not None:
                raise TimelineError('--at needs --story: the story the moment falls in')
            m['story'] = m['at'] = ''
        elif not at:
            raise TimelineError('a moment in a story falls at a scene or shot; give --at')
        else:
            story = story_in(world, key)
            if at in ('before', 'after') or place(story['scenes'], at) is None:
                raise TimelineError(f"no scene or shot {at} in {story['key']}")
            m['story'], m['at'] = story['key'], name(at)
    if a.note is not None:
        m['note'] = cell(a.note)
    m.update(meta_pairs(a.meta, [c.lower() for c in TIMELINE]))
    if a.op == 'set' and a.rename:
        if any(x is not m and x['moment'] and same(x['moment'], a.rename) for x in ms):
            raise TimelineError(f'there is already a moment {a.rename.strip()!r}')
        new = name(a.rename)
        touched = [d for d in readings(world) if renamed(d, m['moment'], new)]
        for r in world['records']:
            if r['kind'] == 'variation' and same(r['from'], m['moment']):
                r['from'] = new
        for e in world['events']:
            if not e['story'] and same(e['at'], m['moment']):
                e['at'] = new
        m['moment'] = new
        return touched
    return []


def save_moment(world, a):
    """moment add|set|move|remove, written: each story, series and episode it changed, then world.md."""
    save_docs(edit_moment(world, a))
    save_world(world)
    return timeline_view(world)


def save_record(path, a):
    """asset or location add|set|remove from a story, series or world: the world's record changed, every story
    naming it following, the stories written, then world.md. Returns the world and its stories read back, the
    record's key, its state before and the names of the world's pins removed with it."""
    world = world_at(path)
    ref, was, touched, gone = assets.edit_record(world, docs_of(world), a, a.cmd,
                                                 lambda label: timeline.keep_asset(world, label, a.file, a.link))
    save_docs(touched)
    save_world(world)
    world = world_at(path)
    return world, docs_of(world), ref, was, gone


def save_continuity(path, a):
    """thread add|set|remove or event add|set|remove|link|unlink from a story, series or world: the world's thread
    or event changed, then world.md written. An event is added to a story or episode, or to the world itself, never
    to a series. Returns the thread to list, None once removed."""
    world = world_at(path)
    here = None if is_world(path) else next(d for d, _ in docs_of(world) if d['path'].resolve() == path.resolve())
    if a.cmd == 'thread':
        edit_thread(world, here, a)
        thread = None if a.op == 'remove' else a.rename or a.name
    else:
        if a.op == 'add' and here is not None and 'episodes' in here:
            raise TimelineError(f'{path} is a series; an event goes on one of its episodes, as event add '
                                f'{path}/ep-<key>, or on its world')
        thread = edit_event(world, here, a)
    save_world(world)
    return thread


def own_pin(story, a):
    """Whether pin add|set|remove from `story` is on its own pin (over its shots and scenes, or the whole story with no
    --from) rather than the world's (from a thread or record). A set moving a pin between the two is refused."""
    world = story['world']
    mine = any(same(p['name'], a.name) for p in story['pins'])
    if a.op == 'add':
        return not timeline.shared_end(world, a.start or a.end)
    if a.op == 'set' and a.start:
        if mine and timeline.shared_end(world, a.start):
            raise TimelineError(f'{a.name} is a pin of {story["key"]}; a pin from a thread or record is the '
                                "world's: remove it, then add it with that --from")
        if not mine and any(same(p['name'], a.name) for p in world['pins']) \
                and not timeline.shared_end(world, a.start):
            raise TimelineError(f"{a.name} is a pin of the world; a pin over shots or scenes is a story's own: remove "
                                'it, then add it on the story')
    return mine


def save_pin(path, a):
    """pin add|set|remove from a story, series or world. On a story, a pin from a series, thread or record (or set or
    removed by the name of one) is the world's, any other the story's own; on a series or world, the world's, one
    added on a series with no --from or --to from that series. A pin's name is one in the world: a story's own never
    takes a name the world's pins have, nor the world's one a story keeps."""
    story = None if is_world(path) or is_series(path) else writable(story_at(path))
    world = story['world'] if story else world_at(path)
    if a.op == 'add' and is_series(path) and not (a.start or a.end):
        a.start = path.resolve().name
    new = a.name if a.op == 'add' else getattr(a, 'rename', None)
    if story is not None and own_pin(story, a):
        if new and any(same(p['name'], new) for p in world['pins']):
            raise TimelineError(f'there is already a pin {new!r} in the world')
        timeline.edit_pin(story, a, lambda t: timeline.pin_end(timeline.scene_ref(story, t), story['scenes']))
        assets.mark_uses(story)
        save_story(story)
        story_changed(story)
        return
    taken = new and next((d['key'] for d in readings(world) for p in d.get('pins', []) if same(p['name'], new)), None)
    if taken:
        raise TimelineError(f'there is already a pin {new!r} in {taken}')
    timeline.edit_pin(world, a, timeline.world_pin_end(world))
    save_world(world)


def check_world(path):
    """What check names in the world's records, read through every story, each record's file gone, and its
    threads and events."""
    world = world_doc(path)
    docs = docs_of(world)
    found = [p for _, p in assets.world_problems(world, docs)] + timeline.assets_missing(world) \
        + continuity.world_problems(world, {d['key'] for d, _ in docs})
    return '\n'.join(f'  {p}' for p in found) or "  the world's assets, locations, threads and events hold together"


def todo_world(path, only):
    """Each open record of the world and each problem check names in them, then its threads' open tasks."""
    world = world_doc(path)
    docs = docs_of(world)
    out = []
    for head, tasks in (('Assets and locations', assets.record_tasks(world) + assets.world_problems(world, docs)),
                        ('Threads', continuity.world_tasks(world, {d['key'] for d, _ in docs}))):
        lines = ticks(tasks, only)
        out += [head] + lines if lines else []
    return '\n'.join(out) or "  nothing open in the world's assets, locations and threads"


def set_when(path, moment):
    """A story's when: the moment it is set at; empty clears it."""
    if is_series(path):
        raise TimelineError(f'{path} is a series; each episode has its own when, as when {path}/ep-<key> <moment>')
    story = writable(story_at(path))
    story['when'] = find_moment(story['world']['moments'], moment)['moment'] if moment.strip() else ''
    save_story(story)
    return timeline_view(story['world'])


def set_at(world):
    """{key: the moment it is set at, or ''} of each story and episode of the world, from its index.md."""
    out = {}
    for p in stories(world['path']):
        for doc in [p / f / 'index.md' for f in series_doc(p)['folders']] if is_series(p) else [p / 'index.md']:
            out[world_key(doc.parent, world['path'])] = frontmatter(doc.read_text(encoding='utf-8')).get('when', '')
    return out


def whens(world):
    """{moment, case-folded: [the key of each story and episode set then]}."""
    out = {}
    for key, when in set_at(world).items():
        if when:
            out.setdefault(when.casefold(), []).append(key)
    return out


def timeline_view(world):
    """The world's moments in order: where each falls, and the stories set then."""
    ms = [m for m in world['moments'] if m['moment']]
    if not ms:
        return f"  no moments yet; moment add {world['path']} <name> adds one"
    then = whens(world)
    w, f = max(6, *(len(m['moment']) for m in ms)) + 2, max(len(falls(m)) for m in ms) + 2
    return '\n'.join([f"  {'Moment':<{w}}{'Falls':<{f}}Set then"]
                     + [f"  {m['moment']:<{w}}{falls(m):<{f}}{', '.join(then.get(m['moment'].casefold(), []))}".rstrip()
                        for m in ms])


def row(path, label):
    """A story's or series' line in a listing: (name, venue, type, status, open)."""
    if world_of(path) is None:
        raise TimelineError(old(path, 'it is in no world'))
    if is_series(path):
        s = series_at(path)
        opened = {k: sum(e['open'][k] for e in s['episodes']) for k in ('scene', 'shot', 'layer', 'thread', 'record', 'cut')}
        return (label, s['fm'].get('venue', '?'), f"series ({len(s['episodes'])})", series_status(s),
                open_counts(opened) if any(e['scenes'] for e in s['episodes']) else '—')
    s = story_at(path)
    return label, s['fm'].get('venue', '?'), 'single', s['status'], open_counts(s['open']) if s['scenes'] else '—'


def listing(items):
    """The stories `items` gives as (folder, name shown), one line each, with a line for each one that
    can't be read."""
    rows, unread = [], []
    for path, label in items:
        try:
            rows.append(row(path, label))
        except TimelineError as e:
            rows.append((label, '?', 'series' if is_series(path) else 'single', "can't read", ''))
            unread.append(f'{label}: {e}')
    w = max(4, *(len(r[0]) for r in rows))
    lines = [f"{'Name':<{w}}  {'Venue':<8}  {'Type':<11}  {'Status':<16}  Open"]
    lines += [f'{n:<{w}}  {v:<8}  {t:<11}  {st:<16}  {d}' for n, v, t, st, d in rows]
    return '\n'.join(lines + ([''] + unread if unread else []))


def list_root(root):
    """Each world in `root` with its stories, named <world>/<story>; given a world, its stories. A story or
    series in `root` outside any world is listed with the migrate that wraps it."""
    if not root.is_dir():
        raise TimelineError(f'no stories folder at {root}; give the folder that holds your stories')
    if is_world(root):
        return show_world(root)
    items = [(p, f'{w.name}/{p.name}') for w in worlds(root) for p in stories(w)]
    items += [(p, p.name) for p in stories(root) if not is_world(p)]
    empty = [w.name for w in worlds(root) if not stories(w)]
    if not items and not empty:
        return f'no storypads in {root}'
    out = listing(sorted(items, key=lambda x: x[1])) if items else ''
    return out + ('\n\n' if out and empty else '') + ''.join(f'{n}: a world with no stories yet\n' for n in empty).rstrip()


def show_world(path):
    """The world's board: its title, its timeline, each story and series in it, then its pins."""
    items = [(p, p.name) for p in stories(path)]
    world = world_doc(path)
    series = sum(1 for p, _ in items if is_series(p))
    single = len(items) - series
    counts = [f"{single} stor{'y' if single == 1 else 'ies'}"] * bool(single or not series) \
        + [f'{series} series'] * bool(series)
    head = f"  {world['title']}  ·  world  ·  {', '.join(counts)}"
    return '\n\n'.join([head, timeline_view(world), listing(items) if items else '  (no stories yet)']
                       + (['\n'.join(['  Pins'] + timeline.world_pin_lines(world))] if world['pins'] else []))


def world_title(path):
    doc = path / ('series.md' if is_series(path) else 'index.md')
    text = doc.read_text(encoding='utf-8')
    h = top(text)
    return frontmatter(text).get('series-name') or (h.group(1) if h else path.resolve().name)
