"""A story and its scenes: index.md and scenes/<key>.md read and written back, scenes added,
moved, renamed and removed by place, and the story shown, checked, listed as to-do and compiled.
"""

import math
import re
import shutil
import textwrap
from pathlib import Path

import assets
import storyfile
import timeline
from continuity import (detail_thread, follow, moment_problems, shot_lines, show_view, story_threads, strand, stranded,
    thread_problems, thread_tasks)
from storyfile import (FIXED, TimelineError, cell, checks, dated, frontmatter, listed, listing, listing_problems,
    meta_pairs, named, put_frontmatter, put_sections, replace_section, same, save, sections, slug, top, unique)
from venues import closing_scene, first_scenes

OLD_SCENE = re.compile(r'^(\d+) - (.+)\.md$')
SCENES = ('#', 'Name', 'File', 'Status', 'Beats', 'Prep')
BAR = 20
STAGES = ('brainstorming', 'outlining', 'refining')


def old(path, reason):
    return f'{path} is in the old layout: {reason}; run storypad migrate {path}'


def old_story(path):
    """Why a story is in the old layout, or None."""
    folder = path / 'scenes'
    names = sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []
    staged = [n for n in names if n.startswith('.place-')]
    numbered = [n for n in names if OLD_SCENE.match(n)]
    if staged:
        return f'scenes/{staged[0]} is left from an unfinished reorder'
    return numbered and f'scenes/{numbered[0]} is a numbered scene file' or None


def parse_scene(path, text, num):
    """A scene numbered `num`, from its file's text. A timeline that can't be read leaves the scene
    with no shots and its reason in 'broken'."""
    h, body = top(text), sections(text)
    scene = {'num': num, 'file': path.name, 'path': path, 'text': text, 'disk': text, 'dirty': False,
             'title': h.group(1) if h else '', 'meta': frontmatter(text), 'broken': None, 'row': {},
             'beats': checks(body.get('beats')), 'prep': checks(body.get('prep')),
             'script': '\n'.join(body.get('script', [])).strip(),
             'note': '\n'.join(body.get('notes', [])).strip()}
    scene['name'] = scene['title'] or f'Scene {num}'
    try:
        timeline.parse(scene, body.get('shots'), body.get('layers'), body.get('takes'))
    except TimelineError as e:
        scene.update(shots=[], layers=[], takes=[], broken=str(e))
    return scene


def done_total(items):
    return sum(i['done'] for i in items), len(items)


def scene_status(scene):
    done, total = done_total(scene['beats'] + scene['prep'])
    if total and done == total:
        return 'done'
    return 'started' if done else 'pending'


def scene_tasks(scene):
    """The scene's own open tasks, as (their --only kind, the task): each open beat and prep item, its script,
    an unreadable timeline."""
    out = [('beats', b['text']) for b in scene['beats'] if not b['done']]
    out += [('prep', f"prep: {p['text']}") for p in scene['prep'] if not p['done']]
    out += [] if scene['script'] else [('script', 'script')]
    return out + ([('shots', f"fix its timeline, which can't be read: {scene['broken']}")] if scene['broken'] else [])


def closing(story):
    """The scene named for the one the story's venue flow ends on, or None."""
    end = closing_scene(story['fm'].get('venue'))
    return next((s for s in story['scenes'] if end and same(s['title'], end)), None)


def cut_tasks(story):
    """Each problem the cut would carry: what check names, but an unreadable scene."""
    last, scenes = closing(story), story['scenes']
    after = len(scenes) - last['num'] if last else 0
    order = [f"{last['num']} {last['name']} is the closing scene, but {after} scene{'s' if after > 1 else ''} "
             f"come{'' if after > 1 else 's'} after it; move it last"] if after else []
    return order + listing_problems('Scenes', story, 'file', {s['file'] for s in scenes}, 'scenes/') \
        + timeline.problems(scenes) + timeline.assets_missing(story)


def tally(story):
    """The story's status, its open tasks on scenes, shots, layers and the cut, and its beats and prep
    done. The status is how far the story work has got: brainstorming with no scenes, else outlining,
    or refining once refine has set it; open tasks never change it."""
    scenes, fm = story['scenes'], story['fm']
    done, total = done_total([i for s in scenes for i in s['beats'] + s['prep']])
    pins = story['pins'] + story['world_pins']
    opened = {'scene': sum(len(scene_tasks(s)) for s in scenes),
              'shot': sum(len(timeline.shot_tasks(s, pins, scenes)) for s in scenes),
              'layer': sum(len(timeline.layer_tasks(s)) for s in scenes),
              'thread': len(thread_tasks(story)) if 'events' in story else 0,
              'record': len(assets.record_tasks(story) + assets.record_problems(story)),
              'cut': len(cut_tasks(story))}
    notes = ''.join(sections(story['text']).get('notes', [])).strip()
    if not scenes:
        status = 'brainstorming' if notes or fm.get('status') not in STAGES else fm['status']
    else:
        status = 'outlining' if fm.get('status') in (None, '', *STAGES[:2]) else 'refining'
    story.update(status=status, done=done, total=total, open=opened)


def open_counts(opened):
    """`2 on scenes, 1 on shots`: each place with tasks open; `nothing open` when none is."""
    where = {'scene': 'scenes', 'shot': 'shots', 'layer': 'layers', 'thread': 'threads',
             'record': 'assets and locations', 'cut': 'the cut'}
    return ', '.join(f'{n} on {where[k]}' for k, n in opened.items() if n) or 'nothing open'


def standing(story):
    """The story's status with its open tasks."""
    if not story['scenes']:
        return f"{story['status']} · no scenes yet"
    n = sum(story['open'].values())
    return f"{story['status']} · " + (f"{n} open: {open_counts(story['open'])}" if n else 'nothing open')


def world_key(path, world):
    """A story's or series' key in the world folder `world`: its folder path from there, as film or
    saga/ep-first."""
    return path.resolve().relative_to(world.resolve()).as_posix()


def keeps_own(path, body):
    """Refused while the story's index.md (`body`, its sections) or the series' series.md keeps its own assets,
    locations, threads or events, or pins on shared things (a story's from a thread or record, any of a series'):
    they belong in world.md."""
    own = assets.parse_records(body)['records'] + assets.parse_recurring(body.get('recurring elements'))[1]
    if own:
        raise TimelineError(old(path, f"it keeps its own assets or locations, as {own[0]['name']}; they belong in "
                                      "its world's world.md"))
    held = [r for s in ('threads', 'continuity threads', 'events') for r in storyfile.table(body.get(s), ('Thread',))[1]
            if r['thread']]
    if held:
        raise TimelineError(old(path, f"it keeps its own threads or events, as {held[0]['thread']}; they belong in "
                                      "its world's world.md"))
    series = (path / 'series.md').is_file()
    shared = [r for r in storyfile.table(body.get('pins'), timeline.PINS)[1]
              if r['pin'] and (series or timeline.shared_pin(r))]
    if shared:
        raise TimelineError(old(path, f"it keeps pins on shared things, as {shared[0]['pin']}; they belong in its "
                                      "world's world.md"))


def listed_scenes(path, body):
    """The scenes of the story at `path` in the order of its Scenes table (`body`, its index.md's sections), with
    the table's header, its rows naming nothing there or one listed above, and the files it doesn't list."""
    folder = path / 'scenes'
    files = {p.name for p in folder.glob('*.md') if not p.name.startswith('.')} if folder.is_dir() else set()
    head, order, rows, odd, unlisted = listing(body.get('scenes'), SCENES, 'file', files)
    scenes = [parse_scene(folder / f, (folder / f).read_text(encoding='utf-8'), n) for n, f in enumerate(order, 1)]
    for s in scenes:
        s['row'] = rows.get(s['file'], {})
    return scenes, head, odd, unlisted


def read_story(path, series=None, world=None):
    """A story, its scenes in the order of its Scenes table; `series` is its series' series.md, read,
    when it is an episode; `world` its world's world.md, read, whose records it uses. A story or series keeping
    its own assets or locations is the older layout."""
    doc = path / 'index.md'
    if not doc.is_file():
        raise TimelineError(f'{path} is not a story: it has no index.md')
    if old_story(path):
        raise TimelineError(old(path, old_story(path)))
    text = doc.read_text(encoding='utf-8')
    fm, body = frontmatter(text), sections(text)
    scenes, head, odd, unlisted = listed_scenes(path, body)
    num = series['folders'].index(path.name) + 1 if series and path.name in series['folders'] else None
    h = top(text)
    story = {'path': path, 'text': text, 'fm': fm, 'doc': doc, 'scenes': scenes, 'head': head, 'odd': odd,
             'unlisted': unlisted, 'num': num, 'row': series['rows'].get(path.name, {}) if num else {},
             'title': h.group(1) if h else f'Episode {num}' if num else path.name,
             'removed': fm.get('removed', '').split(), 'world': world, 'when': fm.get('when', ''),
             'key': world_key(path, world['path']) if world else path.name}
    keeps_own(path, body)
    if num:
        keeps_own(series['path'], sections(series['text']))
    story.update(story_threads(story))
    story['pins_head'], story['pins'] = timeline.parse_pins(body.get('pins'), lambda t: timeline.pin_end(t, scenes))
    story['world_pins'] = timeline.world_pins(story)
    assets.mark_uses(story)
    for s in scenes:
        if not s['broken'] and timeline.fill_basis(s, story['pins'] + story['world_pins'], scenes):
            s['dirty'] = True
            s['text'] = s['disk'] = scene_text(s)
            save(s['path'], s['text'])
    tally(story)
    return story


def progress(done, total, unit):
    pct = math.floor(done / total * 100) if total else 0
    filled = math.floor(done / total * BAR) if total else 0
    return f"  [{'█' * filled}{'░' * (BAR - filled)}] {pct}%  {done}/{total} {unit}"


def mini(done, total, width=5):
    filled = round(done / total * width) if total else 0
    return '█' * filled + '░' * (width - filled)


def header(story):
    fm = story['fm']
    return [f"  {story['title']}", f"  [{fm.get('venue', '?')}] — {standing(story)}"
            + (f"  ·  {fm['target-length']}" if fm.get('target-length') else ''), '']


def box(lines, width, top_joint, bottom_joint):
    """A box `width` wide around `lines`, with a connector at the top and bottom centre."""
    mid = (width - 2) // 2
    top = list('┌' + '─' * (width - 2) + '┐')
    bottom = list('└' + '─' * (width - 2) + '┘')
    if top_joint:
        top[mid + 1] = '┴'
    if bottom_joint:
        bottom[mid + 1] = '┬'
    return [''.join(top)] + [f"│{line:<{width - 2}}│" for line in lines] + [''.join(bottom)]


def item_lines(mark, text, inner):
    wrapped = textwrap.wrap(text, inner - 3) or ['']
    return [f'{mark} {wrapped[0]}'] + [f'  {line}' for line in wrapped[1:]]


def link(char, width):
    mid = (width - 2) // 2 + 1
    return ' ' * mid + char + ' ' * (width - mid - 1)


def scene_column(scene, width):
    inner = width - 2
    bd, bt = done_total(scene['beats'])
    head = [line.center(inner) for line in textwrap.wrap(f"{scene['num']} {scene['name']}", inner)]
    head.append(f"{bd}/{bt}{'  ✎' if scene['script'] else ''}".center(inner))
    items = [('│', '●' if b['done'] else '○', b['text']) for b in scene['beats']]
    items += [('┊', '◆' if p['done'] else '◇', p['text']) for p in scene['prep']]
    out = box(head, width, False, bool(items))
    for i, (line, mark, text) in enumerate(items):
        if line == '┊':
            out.append(link('┊', width))
        out += box(item_lines(mark, text, inner), width, True, i < len(items) - 1)
    return out


def breakdown(scenes):
    total = shutil.get_terminal_size((100, 24)).columns - 2
    per_row = max(1, min(len(scenes), (total + 1) // 20))
    width = min(30, (total + 1) // per_row - 1)
    out = []
    for start in range(0, len(scenes), per_row):
        columns = [scene_column(s, width) for s in scenes[start:start + per_row]]
        height = max(map(len, columns))
        for col in columns:
            col += [' ' * width] * (height - len(col))
        out += ['  ' + ' '.join(parts).rstrip() for parts in zip(*columns)] + ['']
    return out


def table(scenes):
    w = max(7, *(len(s['name']) for s in scenes))
    head = f"  {'#':<3} {'Scene':<{w}}  {'Beats':>6}  {'Prep':>5}  {'Script':>6}  Done"
    out = [head, '  ' + '─' * (len(head) - 2)]
    for s in scenes:
        bd, bt = done_total(s['beats'])
        pd, pt = done_total(s['prep'])
        out.append(f"  {s['num']:<3} {s['name']:<{w}}  {f'{bd}/{bt}':>6}  "
                   f"{f'{pd}/{pt}' if pt else '—':>5}  {'✎' if s['script'] else '—':>6}  "
                   f"{mini(bd + pd, bt + pt)}")
    return out + ['  ' + '─' * (len(head) - 2)]


def gantt(scenes):
    w = max(10, *(len(s['name']) + 4 for s in scenes))
    out = [' ' * (w + 1) + ''.join(f'{s["num"]:<6}' for s in scenes).rstrip(),
           ' ' + '─' * (w - 1) + '┬─────' * len(scenes) + '┬']
    for i, s in enumerate(scenes):
        d, t = done_total(s['beats'] + s['prep'])
        cells = ''.join('│' + (mini(d, t) if j == i else '     ') for j in range(len(scenes)))
        out.append(f" {s['name']:<{w - 1}}{cells}│ {d}/{t}")
    return out + [' ' + '─' * (w - 1) + '┴─────' * len(scenes) + '┴']


VIEWS = {'breakdown': breakdown, 'table': table, 'gantt': gantt}
DRAWN = ('threads', 'small', 'events')
RECORDS = {'assets': assets.show_assets, 'locations': assets.show_locations}
ONLY = ('beats', 'prep', 'script', 'shots', 'layers', 'assets', 'locations', 'threads')


def window():
    return shutil.get_terminal_size((100, 24)).columns


def width():
    return window() - 6


def run_of(items, at, find):
    """The numbered items `at` names through `find`: one, or a run `<from>-<to>`; a run ending before it starts
    is refused."""
    first, dash, last = at.partition('-')
    a = find(first if dash else at)
    b = find(last) if dash else a
    if b['num'] < a['num']:
        raise TimelineError(f"{at} runs backwards; give {b['num']}-{a['num']}")
    return items[a['num'] - 1:b['num']]


def picked(story, at):
    """The scenes `at` names: one scene, or a run `<from>-<to>`."""
    return run_of(story['scenes'], at, lambda ref: timeline.find_scene(story, ref))


def writable(story):
    """The story, refused while one of its scenes can't be read: a write, clean or cut would take that
    scene as empty."""
    bad = [s for s in story['scenes'] if s['broken']]
    if bad:
        raise TimelineError(f"{story['path'].name} can't be changed, cleaned or cut while scene {bad[0]['num']} "
                            f"{bad[0]['name']} can't be read: {bad[0]['broken']}")
    return story


def unreadable(story):
    return [timeline.unread(s) for s in story['scenes'] if s['broken']]


def whole_pinned(story):
    """Whether a pin of the story or of its world holds over the whole story."""
    return any(p['from'] is None and not p['broken'] for p in story['pins'] + story['world_pins'])


def show_scene(story, s):
    scenes = story['scenes']
    if s['broken']:
        return f"  {s['num']}  {s['name']}\n  its timeline can't be read: {s['broken']}"
    marked = timeline.pinned(story['pins'] + story['world_pins'], scenes) \
        | ({str(s['num'])} if whole_pinned(story) else set())
    return '\n'.join(timeline.scene_strip(s, timeline.enters(scenes)[scenes.index(s)], width(), marked))


def show_strip(story):
    marked = timeline.pinned(story['pins'] + story['world_pins'], story['scenes'])
    title = story['title'] + ('•' if whole_pinned(story) else '')
    return '\n'.join(timeline.story_strip(title, story['scenes'], width(), marked))


def show_story(story, view, at=None, only=None):
    if view in RECORDS:
        return RECORDS[view](story)
    if not story['scenes']:
        return '\n'.join(header(story) + ['  (no scenes yet)'])
    if view in DRAWN:
        pick = picked(story, at) if at else story['scenes']
        zoom = pick[0] if at and '-' not in at else None
        return show_view(story, 'threads' if zoom and view == 'small' else view, pick, zoom, only,
                         window(), lambda s: done_total(s['beats'] + s['prep']),
                         f"show {story['path']}")
    if view == 'strip':
        out = [show_strip(story), '', f'  {standing(story)}']
    else:
        out = header(story) + VIEWS[view](story['scenes'])
        out.append(progress(story['done'], story['total'], 'beats and prep done'))
    bad = unreadable(story)
    return '\n'.join(out + ([''] + [f'  {line}' for line in bad] if bad else []))


def ticks(tasks, only):
    """Each (kind, task) as an open `[ ]` line; `only` keeps one kind."""
    return [f'  [ ] {t}' for k, t in tasks if not only or k == only]


def unshot(story):
    """The shots with no take, by scene."""
    rows = [(s, [x for x in s['shots'] if not any(t['shot'] == x['id'] for t in s['takes'])]) for s in story['scenes']]
    rows = [(s, xs) for s, xs in rows if xs]
    n = sum(len(xs) for _, xs in rows)
    return [f"  {n} shot{'s' if n != 1 else ''} with no take"] + \
        [f"  {s['num']:<3}" + ' · '.join(f"{x['id']} {x['name']}" for x in xs) for s, xs in rows]


def todo(story, prefix='', scenes=None, only=None):
    """The open tasks of each scene, its shots, its layers and its threads, then the threads', the assets'
    and locations' and the cut's, each `[ ]`; last, where the story stands. Given `scenes`: their tasks and
    the records each uses. `only` keeps one kind of task."""
    out, pins, threads = [], story['pins'] + story['world_pins'], thread_tasks(story)
    if only == 'shots' and not scenes:
        tasks = [('shots', t.replace('no take yet, ', '')) for s in story['scenes']
                 for t in timeline.shot_tasks(s, pins, story['scenes']) if not t.endswith(': no take yet')]
        return [prefix + line for line in unshot(story)] + ticks(tasks, only)
    for s in scenes or story['scenes']:
        lines = ticks(scene_tasks(s) + [('shots', t) for t in timeline.shot_tasks(s, pins, story['scenes'])]
                      + [('layers', t) for t in timeline.layer_tasks(s)]
                      + [('threads', t) for n, t in threads if n == str(s['num'])]
                      + (assets.record_tasks(story, s) if scenes else []), only)
        if lines:
            out += [f"{prefix}{s['num']} {s['name']}"] + lines
    if scenes:
        return out
    for head, tasks in (('Threads', [('threads', t) for n, t in threads if n is None]),
                        ('Assets and locations', assets.record_tasks(story) + assets.record_problems(story)),
                        ('the cut', [('cut', t) for t in cut_tasks(story)])):
        lines = ticks(tasks, only)
        out += [f'{prefix}{head}'] + lines if lines else []
    return out + [f'{prefix}{standing(story)}']


def offsets(story):
    """Where each scene starts in the story; None once a scene before it has an unknown length."""
    out, t = [], 0
    for s in story['scenes']:
        out.append(t)
        if t is not None and s['shots'] and timeline.known(s['shots']):
            t += sum(x['length'] for x in s['shots'])
        else:
            t = None
    return out


def detail(story, ref, layer_name, thread=None):
    scenes = story['scenes']
    if thread:
        return detail_thread(story, thread)
    if layer_name:
        s = timeline.readable(timeline.find_scene(story, ref))
        layer = timeline.find_layer(s, layer_name)
        return '\n'.join([f"  {layer['name']}  ·  {s['num']} {s['name']}", f"  {timeline.layer_times(layer, s)}"]
                         + timeline.note_lines(layer['note'])
                         + timeline.meta_lines(timeline.meta(layer, timeline.LAYERS)))
    pins = story['pins'] + story['world_pins']
    if not timeline.SHOT.match(ref.strip()):
        s = timeline.find_scene(story, ref)
        if s['broken']:
            return show_scene(story, s)
        return '\n'.join(timeline.detail_scene(s, offsets(story)[scenes.index(s)], pins, scenes))
    s, i = timeline.scene_of(story, ref)
    return '\n'.join(timeline.detail_shot(s, i, offsets(story)[scenes.index(s)], pins, scenes)
                     + shot_lines(story, s['shots'][i]['id']))


def check(story):
    found = unreadable(story) + cut_tasks(story) + thread_problems(story) + moment_problems(story) \
        + [p for _, p in assets.record_problems(story)]
    if found:
        return '\n'.join(f'  {p}' for p in found)
    if not any(s['shots'] for s in story['scenes']):
        return '  nothing to check yet: no scene has shots'
    return '  timeline holds together'


def scene_text(scene):
    """The scene's file: its text, its shots, layers and takes tables rewritten when they changed."""
    text = scene['text']
    if scene['dirty'] and not scene['broken']:
        shots, layers, takes = timeline.tables(scene)
        text = replace_section(text, 'Shots', shots, before='Script')
        text = replace_section(text, 'Layers', layers, before='Script')
        text = replace_section(text, 'Takes', takes, before='Script')
    return text


def index_text(story):
    """index.md with the scene table, the pins, removed:, when: and the status as the story now holds them."""
    tally(story)
    rows = []
    for s in story['scenes']:
        bd, bt = done_total(s['beats'])
        pd, pt = done_total(s['prep'])
        rows.append({**s['row'], '#': str(s['num']), 'name': s['name'], 'file': s['file'], 'status': scene_status(s),
                     'beats': f'{bd}/{bt}', 'prep': f'{pd}/{pt}' if pt else '—'})
    text = replace_section(story['text'], 'Scenes', listed(story['head'], rows, story['odd'], SCENES))
    text = put_sections(text, ('Pins', 'Notes'), {'Pins': timeline.pins_table(story['pins_head'], story['pins'])})
    if story['removed'] or 'removed' in story['fm']:
        text = put_frontmatter(text, 'removed', ' '.join(story['removed']))
    if story.get('when') or 'when' in story['fm']:
        text = put_frontmatter(text, 'when', story['when'] or None)
    if 'status' in story['fm']:
        text = put_frontmatter(text, 'status', story['status'])
    return dated(story['text'], text)


def story_new(path, text, series=None):
    """A new story folder holding `text` as its index.md and its venue's first scenes (youtube: Intro,
    Wrapup) with their beats; `series` is its series' series.md, read, when it is an episode."""
    (path / 'scenes').mkdir(parents=True)
    save(path / 'index.md', text)
    story = read_story(path, series)
    for title, _ in first_scenes(story['fm'].get('venue')):
        scene_add(story, title, None, [])
    save_story(story)


def save_story(story, gone=()):
    """Write each scene file that changed, then index.md, then delete the files in `gone`."""
    writes = [(s['path'], text) for s in story['scenes'] for text in [scene_text(s)] if text != s['disk']]
    index = index_text(story)
    if index != story['text']:
        writes.append((story['doc'], index))
    if writes:
        (story['path'] / 'scenes').mkdir(exist_ok=True)
    for path, text in writes:
        save(path, text)
    for path in gone:
        path.unlink()
    return bool(writes or gone)


def sync_story(story):
    for s in story['scenes']:
        s['dirty'] = True
    changed = save_story(story)
    return f"{story['path'].name}: {standing(story)}" \
        + ('' if changed else ' (no change)')


def reorder(story, scenes):
    """Put the story's scenes in the order `scenes`, numbered by place, every id naming one
    following. Returns the renaming."""
    was = [s['num'] for s in scenes]
    story['removed'], new = timeline.renumber(scenes, story['pins'], story['removed'])
    follow(story, new)
    for s, n in zip(scenes, was):
        s['dirty'] = s['dirty'] or s['num'] != n
        s['name'] = s['title'] or f"Scene {s['num']}"
    story['scenes'] = scenes
    return new


def name_free(story, title, scene=None):
    """Refuse `title` when a scene other than `scene` already has it, trimmed and case-folded."""
    taken = next((s for s in story['scenes'] if s is not scene and title and same(s['title'], title)), None)
    if taken:
        raise TimelineError(f"{taken['num']} {taken['name']} already has that name; give "
                            f"{'the new scene' if scene is None else 'this one'} another")


def scene_add(story, title, before, meta):
    title, pairs = cell(title), meta_pairs(meta, FIXED)
    scenes = story['scenes']
    name_free(story, title)
    end = closing(story)
    at = timeline.find_scene(story, before)['num'] - 1 if before else \
        end['num'] - 1 if end and not same(title, end['title']) else len(scenes)
    folder = story['path'] / 'scenes'
    key = unique(slug(title) or 'scene', lambda k: (folder / f'{k}.md').exists() or f'{k}.md' in story['removed'])
    seed = next((text for n, text in first_scenes(story['fm'].get('venue')) if title and same(n, title)), None)
    text = named(seed or '## Beats\n\n## Script\n', title)
    for k, v in pairs:
        text = put_frontmatter(text, k, v or None)
    new = parse_scene(folder / f'{key}.md', text, len(scenes) + 1)
    new['disk'] = None
    reorder(story, scenes[:at] + [new] + scenes[at:])


def scene_move(story, src, dst):
    s, to = timeline.find_scene(story, src), timeline.find_scene(story, dst)
    was = timeline.spans(story['pins'], story['scenes'])
    scenes = [x for x in story['scenes'] if x is not s]
    scenes.insert(to['num'] - 1, s)
    new = reorder(story, scenes)
    timeline.unmoved(was, new, story['pins'], story['scenes'])


def scene_set(story, ref, title, note, meta):
    s = timeline.find_scene(story, ref)
    pairs = meta_pairs(meta, FIXED)
    if title:
        name_free(story, cell(title), s)
    if note and any(line.startswith('## ') for line in note.splitlines()):
        raise TimelineError('a note line starts with "## ", which would start a section of the scene file; '
                            'start it another way')
    text = replace_section(s['text'], 'Notes', note.strip() or None) if note is not None else s['text']
    text = named(text, cell(title)) if title is not None else text
    for k, v in pairs:
        text = put_frontmatter(text, k, v or None)
    s['text'] = text


def scene_remove(story, ref, force):
    """Remove a scene; returns its file, deleted once the rest is written."""
    s = timeline.find_scene(story, ref)
    ids = {x['id'] for x in s['shots']}
    users = timeline.holding(story['pins'], story['scenes'], {str(s['num'])} | ids) + timeline.keeping(story['pins'], ids)
    if users:
        raise TimelineError(f"{s['num']} {s['name']} is pinned by {', '.join(dict.fromkeys(users))}; "
                            'move or remove those pins first')
    tags = {str(s['num']), s['name']} | ids
    lost = stranded(story, tags)
    if lost and not force:
        raise TimelineError(f"{s['num']} {s['name']} holds {', '.join(lost)}; add --force to remove it, "
                            'and they lose their place')
    strand(story, tags)
    beats = sum(b['done'] for b in s['beats'])
    timeline.keep_work(f"{s['num']} {s['name']}", (['its script'] if s['script'] else [])
              + ([f"{beats} ticked beat{'s' if beats > 1 else ''}"] if beats else [])
              + ([f"takes {', '.join(t['id'] for t in s['takes'])}"] if s['takes'] else []), force)
    story['removed'] = [x for x in story['removed']
                        if not (timeline.ID.match(x) and int(timeline.ID.match(x).group(1)) == s['num'])]
    timeline.retire(story, s['file'])
    reorder(story, [x for x in story['scenes'] if x is not s])
    return [s['path']]


def compile_script(story, output, stdout):
    out = [f"# {story['title']}", '', '---', '']
    missing = []
    for s in story['scenes']:
        out += [f"## {s['num']:02d} - {s['name']}", '', s['script'] or '[ no script yet ]', '', '---', '']
        if not s['script']:
            missing.append(s['name'])
    text = '\n'.join(out)
    if stdout:
        return text
    target = Path(output) if output else story['path'] / 'script.md'
    save(target, text)
    have = len(story['scenes']) - len(missing)
    return f'compiled → {target}\n  scenes with script: {have}/{len(story["scenes"])}' \
        + (f"\n  missing: {', '.join(missing)}" if missing else '')
