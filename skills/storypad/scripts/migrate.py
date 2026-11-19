"""Migration: a story's numbered scene files, or a series' numbered episode folders and their scenes,
converted to the layout keyed by name, a story or series in no world wrapped in one or moved into one already
there, its assets, locations, threads, events and pins on shared things moved to world.md (a name the world has
refused, never merged; what an earlier run already moved, kept once) and its variations started from moments of the
world's timeline in place of events; every new file written before any old one is deleted.
"""

import filecmp
import os
import re
import shutil
from pathlib import Path

import assets
import timeline
from continuity import (EVENTS, STORY_THREADS, episode_of, episodes_of, falls, label, parse_threads, place, places,
    places_text, renumber_threads, slots, thread_end, threads_table)
from episodes import ARC, OLD_EPISODE, is_series, series_doc, series_text
from scenes import OLD_SCENE, SCENES, index_text, listed_scenes, parse_scene, reorder, scene_text, tally, world_key
from storyfile import (TimelineError, frontmatter, named, put_frontmatter, replace_section, same, save, sections, slug,
    table, top, unique)
from world import DOC, index_of, is_world, save_world, set_at, world_doc, world_of, world_text, world_title

OLD_NAME = re.compile(r'^(\d+)[ \t]*-[ \t]*(.+)$')


def plan_story(src, dst):
    """A story in the old layout read from `src` and set to live in `dst`: its scenes in their old
    file order, each named by a key and numbered by its place, every id following. Each scene keeps
    its old file in 'old'. Refused on anything it can't carry over."""
    folder = src / 'scenes'
    names = sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []
    staged = [n for n in names if n.startswith('.place-')]
    if staged:
        raise TimelineError(f'{folder / staged[0]} is left from an unfinished reorder; give it back its '
                            '"NN - Title.md" name, then migrate')
    olds = sorted((n for n in names if OLD_SCENE.match(n)), key=lambda n: int(OLD_SCENE.match(n).group(1)))
    news = [n for n in names if n.endswith('.md') and not OLD_SCENE.match(n)]
    if olds and news:
        raise TimelineError(f'{folder} holds both layouts, as in {olds[0]} and {news[0]}; '
                            'move one of them out, then migrate')
    text = (src / 'index.md').read_text(encoding='utf-8')
    fm, body = frontmatter(text), sections(text)
    scenes, keys = [], set()
    for n in olds:
        m = OLD_SCENE.match(n)
        scene_doc = (folder / n).read_text(encoding='utf-8')
        h = top(scene_doc)
        numbered = h and OLD_NAME.match(h.group(1))
        title = numbered.group(2) if numbered else h.group(1) if h else m.group(2)
        key = unique(slug(title) or 'scene', keys.__contains__)
        keys.add(key)
        s = parse_scene(dst / 'scenes' / f'{key}.md', named(scene_doc, title),
                        int(numbered.group(1)) if numbered else int(m.group(1)))
        if s['broken']:
            raise TimelineError(f"{folder / n}: its timeline can't be read: {s['broken']}; fix it, then migrate")
        scenes.append({**s, 'old': folder / n, 'disk': None})
    nums = [s['num'] for s in scenes]
    twice = sorted({n for n in nums if nums.count(n) > 1})
    if twice:
        raise TimelineError(f"two scenes are numbered {twice[0]}: "
                            f"{', '.join(s['old'].name for s in scenes if s['num'] == twice[0])}; renumber one, then migrate")
    head, rows = table(body.get('scenes'), SCENES)
    found, odd = {}, []
    for i, r in enumerate(rows):
        if r['file'] in olds and r['file'] not in found:
            found[r['file']] = r
        else:
            odd.append((i, r))
    for s in scenes:
        s['row'] = found.get(s['old'].name, {})
    pins_head, pins = timeline.parse_pins(body.get('pins'), lambda t: timeline.pin_end(t, scenes))
    h = top(text)
    story = {'path': dst, 'doc': dst / 'index.md', 'text': put_frontmatter(text, 'episode', None), 'fm': fm,
             'scenes': [], 'head': head, 'odd': odd, 'unlisted': [], 'pins_head': pins_head, 'pins': pins, 'world_pins': [],
             'title': h.group(1) if h else dst.name,
             'removed': [x for x in fm.get('removed', '').split() if not x.isdigit()]}
    reorder(story, scenes)
    return story


def moved_scenes(story):
    return [f"    scenes/{s['old'].name} → scenes/{s['file']}  ({s['num']} {s['name']})" for s in story['scenes']]


def migrate_story(path):
    story = plan_story(path, path)
    if not story['scenes']:
        return f'{path} is already in the new layout'
    writes = [(s['path'], scene_text(s)) for s in story['scenes']]
    there = [p for p, _ in writes if p.exists()]
    if there:
        raise TimelineError(f'{there[0]} is already there; move it out, then migrate')
    for p, text in writes:
        save(p, text)
    save(story['doc'], index_text(story))
    for s in story['scenes']:
        s['old'].unlink()
    return '\n'.join([f'migrated {path}'] + moved_scenes(story))


def migrate_series(path):
    names = sorted(p.name for p in path.iterdir() if p.is_dir())
    staged = [n for n in names if n == '.new-episode' or n.startswith('.place-')]
    if staged:
        raise TimelineError(f'{path / staged[0]} is left from an unfinished episode add or move; '
                            'finish it or move it out by hand, then migrate')
    text = (path / 'series.md').read_text(encoding='utf-8')
    body = sections(text)
    head, rows = table(body.get('episode arc'), ARC)
    olds = sorted((n for n in names if OLD_EPISODE.match(n) and n not in {r['folder'] for r in rows}
                   and (path / n / 'index.md').is_file()), key=lambda n: int(OLD_EPISODE.match(n).group(1)))
    news = [n for n in names if n.startswith('ep-') and n not in olds]
    if not olds:
        return f'{path} is already in the new layout'
    if news:
        raise TimelineError(f'{path} holds both layouts, as in {olds[0]} and {news[0]}; '
                            'move one of them out, then migrate')
    episodes, keys = [], set()
    for n in olds:
        m = OLD_EPISODE.match(n)
        index = (path / n / 'index.md').read_text(encoding='utf-8')
        h = top(index)
        key = unique(slug(m.group(2) or (h.group(1) if h else '')) or 'episode',
                     lambda k: k in keys or (path / f'ep-{k}').exists())
        keys.add(key)
        e = plan_story(path / n, path / f'ep-{key}')
        e.update(old=path / n, was=int(frontmatter(index).get('episode') or m.group(1)))
        episodes.append(e)
    was = [e['was'] for e in episodes]
    twice = sorted({n for n in was if was.count(n) > 1})
    if twice:
        raise TimelineError(f"two episodes are numbered {twice[0]}: "
                            f"{', '.join(e['old'].name for e in episodes if e['was'] == twice[0])}; renumber one, then migrate")
    found, odd = {}, []
    for i, r in enumerate(rows):
        n = int(r['ep']) if r['ep'].isdigit() else None
        if n in was and n not in found:
            found[n] = r
        else:
            odd.append((i, r))
    for num, e in enumerate(episodes, 1):
        h = top(e['text'])
        tally(e)
        e.update(num=num, row=found.get(e['was'], {}), title=h.group(1) if h else f'Episode {num}')
    threads_head, threads = parse_threads(body.get('continuity threads'))
    renumber_threads(threads, {e['was']: e['num'] for e in episodes})
    pins_head, pins = timeline.parse_pins(body.get('pins'), thread_end([t['thread'] for t in threads]))
    for p in pins:
        for e in episodes:
            if p['ref'].startswith(f"{e['old'].name}/"):
                p['ref'] = e['path'].name + p['ref'][len(e['old'].name):]
    series = replace_section(series_text({'text': text, 'fm': frontmatter(text), 'head': head, 'odd': odd,
                                          'episodes': episodes}),
                             'Pins', timeline.pins_table(pins_head, pins), before='Notes')
    series = replace_section(series, 'Continuity Threads', threads_table(threads_head, threads), before='Pins')
    for e in episodes:
        def skip(folder, files, e=e):
            here = Path(folder)
            return ['index.md'] if here == e['old'] else \
                [f for f in files if OLD_SCENE.match(f)] if here == e['old'] / 'scenes' else []
        shutil.copytree(e['old'], e['path'], ignore=skip)
        for s in e['scenes']:
            save(s['path'], scene_text(s))
        save(e['doc'], index_text(e))
    save(path / 'series.md', series)
    for e in episodes:
        shutil.rmtree(e['old'])
    return '\n'.join([f'migrated {path}'] + [line for e in episodes for line in
                                             [f"  {e['old'].name} → {e['path'].name}  ({e['num']} {e['title']})"]
                                             + moved_scenes(e)])


def wrap(path):
    """A story or series in no world wrapped in a world of its own: its files copied into `<path>/<its folder's
    name>/`, world.md written in `path`, then the old files deleted."""
    inside = path / unique(path.resolve().name, lambda k: (path / k).exists())
    olds = sorted(path.iterdir())
    title = world_title(path)
    inside.mkdir()
    for p in olds:
        if p.is_dir() and not p.is_symlink():
            shutil.copytree(p, inside / p.name, symlinks=True)
        else:
            shutil.copy2(p, inside / p.name, follow_symlinks=False)
    save(path / DOC, world_text(title))
    for p in olds:
        shutil.rmtree(p) if p.is_dir() and not p.is_symlink() else p.unlink()
    return inside, f"wrapped {path} in a world: the {'series' if is_series(inside) else 'story'} is now {inside}"


def move_into(path, into):
    """A story or series in no world moved into the world `into`: its folder copied to `<into>/<its name>`, then
    the old one deleted."""
    inside = into / path.resolve().name
    shutil.copytree(path, inside, symlinks=True)
    shutil.rmtree(path)
    return inside, f"moved {path} into the world {into}: the {'series' if is_series(inside) else 'story'} is now {inside}"


def take_file(folder, ref):
    """The file of the take `ref` of the story at `folder`, read from its scene files' Takes; None when none has it."""
    for f in sorted((folder / 'scenes').glob('*.md')):
        for r in table(sections(f.read_text(encoding='utf-8')).get('takes'), timeline.TAKES)[1]:
            m = timeline.TAKE.match(r['take'])
            if m and f'{m.group(1)}.{int(m.group(2))}' == ref:
                return r['file']
    return None


def kept(doc):
    """What a story's index.md or a series' series.md keeps itself: (its assets and locations, its threads, its
    events, its pins on shared things), a series' records its Recurring Elements as world records, its threads its
    Continuity Threads and every pin of it shared, one with no From then from the series (over its episodes only). A
    pin keeping a take keeps the take's file."""
    body = sections(doc.read_text(encoding='utf-8'))
    series = doc.name == 'series.md'
    recs = [from_recurring(r) for r in assets.parse_recurring(body.get('recurring elements'))[1]] if series \
        else assets.parse_records(body)['records']
    threads = (parse_threads(body.get('continuity threads')) if series else table(body.get('threads'), STORY_THREADS))[1]
    pins = [p for p in timeline.parse_pins(body.get('pins'), lambda t: None)[1] if series or timeline.shared_pin(p)]
    for p in pins:
        if series and not p['from']:
            p['from'] = p['to'] = doc.parent.resolve().name
        if timeline.TAKE.match(p['ref']):
            p['ref'] = take_file(doc.parent, p['ref']) or p['ref']
    return recs, [t for t in threads if t['thread']], \
        [e for e in table(body.get('events'), EVENTS)[1] if e['thread'] or e['event']], pins


def held(path):
    """What the story or series at `path` keeps itself, as (where, its folder, records, threads, events, pins): its
    index.md's, or its series.md's and each episode's."""
    if not is_series(path):
        return [(path.name, path, *kept(path / 'index.md'))]
    return [(path.name, path, *kept(path / 'series.md'))] + [(f'{path.name}/{p.name}', p, *kept(p / 'index.md'))
                                                             for p in sorted(path.iterdir()) if (p / 'index.md').is_file()]


def same_file(world, kept_there, at, file):
    """Whether the file world.md keeps (`kept_there`) is `file` as kept from the folder `at`: the same link or @name,
    else the same file or a copy of it."""
    if not file or timeline.as_given(file):
        return kept_there == file
    a, b = timeline.local(world['path'], kept_there), timeline.local(at, file)
    return a.resolve() == b.resolve() or (a.is_file() and b.is_file() and filecmp.cmp(a, b, shallow=False))


def named_for(name, base):
    """Whether `name` is `base`, or a name unique made from it (`<base>-N`)."""
    return bool(re.fullmatch(re.escape(base.strip()) + r'(-\d+)?', name.strip(), re.I))


def made_for(world, key, at, event, name):
    """Whether the moment `name` is one a migrate made for the event `event` kept by the story or series at `key` in
    the folder `at`: an episode's when, or named for the event or an episode's title (as unique names it) and
    falling in that story, or in its series or between stories."""
    series = at if is_series(at) else at.parent if is_series(at.parent) else None
    eps = [series / f / 'index.md' for f in series_doc(series)['folders']] if series else []
    texts = [p.read_text(encoding='utf-8') for p in eps if p.is_file()]
    if any(same(frontmatter(t).get('when', ''), name) for t in texts):
        return True
    bases = [event] + [h.group(1) if h else f'Episode {n}' for n, h in enumerate(map(top, texts), 1)]
    scope = world_key(series, world['path']) if series else key
    m = next((m for m in world['moments'] if m['moment'] and same(m['moment'], name)), None)
    return bool(m) and any(named_for(name, b) for b in bases) \
        and (m['story'] == key or bool(series) and (not m['story'] or m['story'].startswith(f'{scope}/')))


def moved_before(world, key, kind, row, at):
    """Whether world.md already holds the record, thread, event or pin `row` kept by the story at `key` in the folder
    `at` (a series' threads: by its episodes; its events: the world's own), moved there by a migrate that stopped
    before it rewrote the story. A variation still starting from an event matches one world.md starts from a
    moment an earlier run made for it."""
    if kind == 'record':
        r = next((x for x in world['records'] if x['kind'] == row['kind'] and same(assets.key(x), assets.key(row))),
                 None)
        skip = {'file'} | ({'from'} if r and row['kind'] == 'variation' and not any(
            m['moment'] and same(m['moment'], row['from']) for m in world['moments'])
            and made_for(world, key, at, row['from'], r['from']) else set())
        return bool(r) and all(r.get(k, '') == v for k, v in row.items() if k not in skip) \
            and same_file(world, r['file'], at, row['file'])
    if kind == 'pin':
        p = next((x for x in world['pins'] if same(x['name'], row['name'])), None)
        return bool(p) and same(p['from'] or '', row['from'] or '') and p['keep'] == row['keep'] \
            and same_file(world, p['ref'], at, row['ref'])
    if kind == 'thread':
        t = next((x for x in world['threads'] if same(x['thread'], row['thread'])), None)
        return bool(t) and any(k == key or k.startswith(f'{key}/') for c in ('on screen', 'heard') for k in places(t[c]))
    story = '' if is_series(at) else key
    return any(e['story'] == story and same(label(e), label(row)) and all(e.get(k, '') == row.get(k, '') for k in ('kind', 'seen', 'links'))
               for e in world['events'])


def clashes(path, world, rerun):
    """Each record, thread, event and pin the story or series at `path` keeps whose name its world (`world`, read,
    or None) or another of its own already has, as `<kind> <name> (<here> and <there>)`; on a `rerun` in the world it
    is already in, one world.md already holds for it is no clash."""
    there = f'the world {world["path"].name}' if world else ''
    seen = [(r, there) for r in (world or {}).get('records', [])]
    names = [(t['thread'], there) for t in (world or {}).get('threads', [])]
    labels = [(label(e), there) for e in (world or {}).get('events', [])]
    pins = [(p['name'], there) for p in (world or {}).get('pins', [])]
    out = []
    for where, folder, recs, threads, events, moving in held(path):
        for r in recs:
            if rerun and moved_before(world, where, 'record', r, folder):
                continue
            other = next((at for x, at in seen if same(assets.key(x), assets.key(r)) or
                          (x['kind'] != 'variation' and r['kind'] != 'variation' and same(x['name'], r['name']))), None)
            out += [f"{r['kind']} {assets.key(r)} ({where} and {other})"] if other else []
            seen.append((r, where))
        for kind, rows, taken in (('thread', threads, names), ('event', events, labels), ('pin', moving, pins)):
            for r in rows:
                if rerun and moved_before(world, where, kind, r, folder):
                    continue
                n = r['thread'] if kind == 'thread' else r['name'] if kind == 'pin' else label(r)
                other = next((at for x, at in taken if same(x, n)), None)
                out += [f'{kind} {n} ({where} and {other})'] if other else []
                taken.append((n, where))
    return out


def from_recurring(r):
    """An older series' Recurring Elements row as a record of world.md: its Description its expectation when it
    has none, its Type kept on an asset."""
    out = {k: v for k, v in r.items() if k not in ('element', 'description') and (k != 'type' or r['kind'] == 'asset')}
    out['expect'] = r['expect'] or r['description']
    return out | ({'description': r['description']} if r['expect'] and r['description'] else {})


def to_world(path, fresh):
    """The story or series at `path` set in its world. Just wrapped, a series' episodes each get a moment, in arc
    order, named for its title, and that moment as its when; rerun on a series that still keeps what moves, an
    episode with no when takes the moment named for its title that nothing is set at. Each variation starting from
    an event starts from a moment instead: a story's or episode's event becomes a moment named for it, falling at
    the event's scene or shot, after the moment the story is set at; a series event at an episode, that episode's when (else a moment named for it, falling at that
    episode's start); after an episode, a moment made after that one; before, a moment made first. The assets
    and locations it keeps move to world.md, each file in its assets/ copied into the world's; its threads, events
    and pins on shared things (a story's from a thread or record, every one of a series) move there too: a story's On screen and Heard under its key and its events in it, a series thread running
    through the episodes it lists, a series event before staying before and one at or after an episode going to the
    moment that starts its variations. The files are copied, then world.md written, then the stories without what
    moved. Returns a line for each change."""
    world = world_doc(world_of(path))
    moments, lines, texts, made, copies = world['moments'], [], {}, {}, []

    def edit(doc, change):
        texts[doc] = change(texts[doc] if doc in texts else doc.read_text(encoding='utf-8'))

    def moment(title, story='', at='', where=None):
        m = {'moment': unique(title, lambda k: any(x['moment'] and same(x['moment'], k) for x in moments)),
             'story': story, 'at': at, 'note': ''}
        moments.insert(len(moments) if where is None else where, m)
        lines.append(f"  moment {m['moment']} → {falls(m)}")
        return m

    def convert(where, records, events, start):
        """Each of `records`' variations starting from one of `events` started from its moment."""
        for r in records:
            e = r['kind'] == 'variation' and not any(x['moment'] and same(x['moment'], r['from']) for x in moments) \
                and next((e for e in events if same(label(e), r['from'])), None)
            if e:
                m = start(e)
                lines.append(f"  {where}@{assets.key(r)} starts from the moment {m['moment']}")
                r['from'] = m['moment']

    def rehome(at, file):
        """A record's file, kept from the folder `at`, as a path from the world: one in at's assets/ copied into
        the world's assets/."""
        if not file or timeline.as_given(file):
            return file
        src = timeline.local(at, file)
        if not (src.is_file() and src.resolve().parent == (at / 'assets').resolve()):
            return os.path.relpath(src.resolve(), world['path'].resolve())
        copied = next((d for s, d in copies if s.resolve() == src.resolve()), None)
        if copied:
            return f'assets/{copied.name}'
        stem = unique(src.stem, lambda k: (world['path'] / 'assets' / f'{k}{src.suffix}').exists()
                      or any(d.name == f'{k}{src.suffix}' for _, d in copies))
        copies.append((src, world['path'] / 'assets' / f'{stem}{src.suffix}'))
        lines.append(f"  {world_key(at, world['path'])}/{file} copied to the world's assets/{stem}{src.suffix}; "
                     'the old copy stays until clean --delete')
        return f'assets/{stem}{src.suffix}'

    def moved(at, kind, rows, as_world):
        """`rows`, records, threads, events or pins kept by the story or series in the folder `at`, moved into
        world.md as `as_world` gives; one world.md already holds for it kept once."""
        key = world_key(at, world['path'])
        for r in rows:
            if not moved_before(world, key, kind[:-1], r, at):
                world[kind].append(as_world(r))
            n = r['thread'] if kind == 'threads' else r['name'] if kind == 'pins' else label(r) if kind == 'events' \
                else f"{r['kind']} {assets.key(r)}"
            lines.append(f"  {key} {kind[:-1] + ' ' if kind != 'records' else ''}{n} → world.md")

    def own_pins(text):
        """index.md keeping only the pins over its own shots and scenes, or the whole story."""
        head, pins = timeline.parse_pins(sections(text).get('pins'), lambda t: None)
        return replace_section(text, 'Pins', timeline.pins_table(head, [p for p in pins if not timeline.shared_pin(p)]),
                               before='Notes')

    def story_moments(at, when, series_start=None, series_events=()):
        doc = at / 'index.md'
        key = world_key(at, world['path'])
        recs, threads, events, pins = kept(doc)
        scenes = listed_scenes(at, sections(doc.read_text(encoding='utf-8')))[0]

        def pos(at):
            """Where a moment falling at `at` in the story sits: none is its start, one naming nothing its end."""
            return (place(scenes, at) or (len(slots(scenes)) + 1,))[0] if at.strip() else -1

        def own(e):
            """The moment of the story's event `e`: after the moment the story is set at, among those already falling
            in it in story order; with no such moment, before the first of them falling later, else last."""
            if (key, label(e)) not in made:
                i = next((i + 1 for i, m in enumerate(moments) if when and same(m['moment'], when)), None)
                while i is not None and i < len(moments) and moments[i]['story'] == key \
                        and pos(moments[i]['at']) <= pos(e['at']):
                    i += 1
                if i is None:
                    i = next((j for j, m in enumerate(moments) if m['story'] == key and pos(m['at']) > pos(e['at'])),
                             None)
                made[(key, label(e))] = moment(label(e), key, e['at'], i)
            return made[(key, label(e))]
        convert(f'{key} ', recs, events + [e for e in world['events'] if e['story'] == key], own)
        if series_start:
            convert(f'{key} ', recs, series_events, series_start)
        moved(at, 'records', recs, lambda r: {**r, 'file': rehome(at, r['file'])})
        moved(at, 'threads', threads, lambda t: {
            **t, 'heard': places_text({key: t['heard']}) if t['heard'] else '',
            'on screen': places_text({key: t['on screen']}) if t['on screen'] or not t['heard'] else ''})
        moved(at, 'events', events, lambda e: {**e, 'story': key})
        moved(at, 'pins', pins, lambda p: {**p, 'ref': rehome(at, p['ref'])})
        edit(doc, lambda text: without(text, ('Threads', 'Events', 'Assets', 'Locations')))
        if pins:
            edit(doc, own_pins)

    if not is_series(path):
        story_moments(path, frontmatter((path / 'index.md').read_text(encoding='utf-8')).get('when', ''))
    else:
        eps, whens = [path / f for f in series_doc(path)['folders']], {}
        unfinished = not fresh and any(kept(path / 'series.md'))
        taken = {w.casefold() for w in set_at(world).values() if w}
        for n, ep in enumerate(eps, 1):
            text = (ep / 'index.md').read_text(encoding='utf-8')
            whens[n] = frontmatter(text).get('when', '')
            h = top(text)
            title = h.group(1) if h else f'Episode {n}'
            left = unfinished and next((m['moment'] for m in moments if m['moment'] and not m['story']
                                        and named_for(m['moment'], title) and m['moment'].casefold() not in taken), None)
            if not whens[n] and (fresh or left):
                whens[n] = left or moment(title)['moment']
                edit(ep / 'index.md', lambda t, when=whens[n]: put_frontmatter(t, 'when', when))
                lines.append(f"  {world_key(ep, world['path'])} when {whens[n]}")
            taken |= {whens[n].casefold()} - {''}

        def series_start(e):
            at, n = e['at'].strip(), episode_of(e['at'])
            hit = next((m for m in moments if whens.get(n) and same(m['moment'], whens[n])), None)
            if ('', label(e)) not in made:
                made[('', label(e))] = moment(label(e), where=0) if at == 'before' else \
                    moment(label(e), where=index_of(moments, hit) + 1 if hit else None) if 'after' in at else hit or \
                    moment(label(e), world_key(eps[n - 1], world['path']) if 0 < n <= len(eps) else '')
            return made[('', label(e))]

        recs, threads, events, pins = kept(path / 'series.md')
        convert('', recs, events, series_start)
        moved(path, 'records', recs, lambda r: {**r, 'file': rehome(path, r['file'])})
        moved(path, 'threads', threads, lambda t: {
            **{k: v for k, v in t.items() if k not in ('introduced', 'last referenced', 'episodes')}, 'heard': '',
            'on screen': places_text({world_key(eps[n - 1], world['path']): '' for n in episodes_of(t) if 0 < n <= len(eps)})})
        moved(path, 'events', events, lambda e: {**e, 'story': '', 'at': 'before' if e['at'].strip() == 'before'
                                                 else series_start(e)['moment']})
        moved(path, 'pins', pins, lambda p: {**p, 'ref': rehome(path, p['ref'])})
        edit(path / 'series.md', lambda text: without(text, ('Recurring Elements', 'Continuity Threads', 'Events',
                                                             'Pins')))
        for n, ep in enumerate(eps, 1):
            story_moments(ep, whens[n], series_start, events)
    for head, rows in ((world['assets_head'], [r for r in world['records'] if r['kind'] == 'asset']),
                       (world['locations_head'], [r for r in world['records'] if r['kind'] != 'asset']),
                       (world['threads_head'], world['threads']), (world['events_head'], world['events']),
                       (world['pins_head'], [p['row'] for p in world['pins']])):
        known = {h.lower() for h in head} | {'name', 'kind', 'of', 'from', 'look', 'asset', 'location'}
        head += [k.capitalize() for k in dict.fromkeys(k for r in rows for k in r) if k not in known]
    for src, dst in copies:
        dst.parent.mkdir(exist_ok=True)
        save(dst, src)
    save_world(world)
    for doc, text in texts.items():
        if text != doc.read_text(encoding='utf-8'):
            save(doc, text)
    return lines


def without(text, headings):
    for h in headings:
        text = replace_section(text, h, None)
    return text


def migrate(path, into=None):
    """Bring a story or series to the current layout: its numbered scene files, or a series' numbered
    episode folders and their scenes, converted; one in no world wrapped in a world of its own, or moved into
    the world `into`; its assets, locations, threads, events and pins on shared things moved to world.md and its
    variations started from moments.
    Refused before any change while a name it keeps clashes with one its world has. Every new file is written
    before any old one is deleted."""
    if is_world(path):
        raise TimelineError(f'{path} is a world; migrate a story or series in it')
    if (path / 'index.md').is_file() and is_series(path.resolve().parent):
        raise TimelineError(f'{path} is an episode; migrate its series, {path.parent}')
    if not is_series(path) and not (path / 'index.md').is_file():
        raise TimelineError(f'{path} is not a story or a series: it has no index.md or series.md')
    fresh = world_of(path) is None
    if into is not None:
        if not is_world(into):
            raise TimelineError(f'{into} is not a world: it has no {DOC}')
        if not fresh:
            raise TimelineError(f'{path} is already in the world {world_of(path).name}; --into moves a story or series '
                                'in no world')
        if (into / path.resolve().name).exists():
            raise TimelineError(f'{into / path.resolve().name} is already there; rename one of the folders, then migrate')
    home = into if into is not None else world_of(path)
    taken = clashes(path, home and world_doc(home), not fresh)
    if taken:
        raise TimelineError(f"a name is never merged by guess, and these are taken: {'; '.join(taken)}; rename one "
                            "side (the world's with asset, location, thread, event or pin set --rename, the story's in its "
                            "index.md and its @names), then migrate")
    done = migrate_series(path) if is_series(path) else migrate_story(path)
    lines = [] if done.endswith('already in the new layout') else [done]
    if fresh:
        path, moved = move_into(path, into) if into is not None else wrap(path)
        lines.append(moved)
    lines += to_world(path, fresh)
    return '\n'.join(lines) or done
