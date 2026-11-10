"""A story's timeline: each scene's shots and the layers that run over them, the story's pins, and
the strips that draw them sized to the window.

A scene's number is its place in the story. A shot id is its scene's number and letters fixed when
the shot is made: 3a, 3b … 3z, 3aa; when the scene's number changes, every id in it follows. A
bare number is the scene. A layer end is a shot id (its start;
its end when it is the layer's `to`), a shot id plus seconds into it (`3b+8`), or `open` for a
layer that carries across the scene's edge. A take is a made file for a shot, `3a.1`, `3a.2`;
`3a.1+` is the one approved; its `in` is where in the file the cut starts it. A note on a shot,
layer, take or pin is never part of the content. A pin runs from a shot id or scene number to another,
or over the whole story when both are empty.

Shots, layers, takes and pins are added, changed, moved and removed here, by scene number and
id; the files they keep sit in the story's assets/ or stay links, and clean lists the ones none
keeps.

Every table is read by its header. A column storypad doesn't know is meta: kept, with its values,
through every rewrite, shown by detail and left out of the script and the cut.
"""

import filecmp
import hashlib
import re
import urllib.request
from pathlib import Path

from storyfile import TimelineError, cell, meta_pairs, name, same, save, slug, table, table_text, unique

ENDS = ('cut', 'match', 'dissolve', 'fade')
SHOT = re.compile(r'^(\d+)([a-z]+)$')
REF = re.compile(r'^(\d+[a-z]+)(?:\+(\d+(?:\.\d+)?))?$')
TAKE = re.compile(r'^(\d+[a-z]+)\.(\d+)(\+)?$')
ID = re.compile(r'^(\d+)([a-z]+(?:\.\d+)?)?$')
SHOTS = ('id', 'shot', 'length', 'ends', 'shows', 'note')
LAYERS = ('layer', 'from', 'to', 'in', 'out', 'file', 'note')
TAKES = ('take', 'file', 'prompt', 'model', 'refs', 'in', 'note')
PINS = ('pin', 'from', 'to', 'keep', 'ref', 'note')
BASIS = 'basis'
FADE_IN, FADE_OUT = '░▒▓', '▓▒░'
UNKNOWN = 10


# ── Reading and writing ────────────────────────────────────────────

def seconds(text):
    """`12`, `12s`, `1:40` → seconds; empty or `?` → None (not known yet)."""
    text = (text or '').strip().rstrip('s')
    if text in ('', '?'):
        return None
    m = re.match(r'^(?:(\d+):)?(\d+(?:\.\d+)?)$', text)
    if not m or not int(m.group(1) or 0) * 60 + float(m.group(2)):
        raise TimelineError(f'not a length: {text!r}; use seconds or m:ss, more than 0')
    return int(m.group(1) or 0) * 60 + float(m.group(2))


def clock(secs):
    secs = round(secs)
    return f'{secs // 60}:{secs % 60:02d}'


def num(value):
    return int(value) if value == int(value) else value


def ending(text, kinds=ENDS):
    """`cut`, `match`, `dissolve 4`, `fade 6` → (kind, seconds)."""
    parts = (text or '').split()
    timed = ('dissolve', 'fade')
    if not parts or parts[0] not in kinds or len(parts) > (2 if parts[0] in timed else 1):
        raise TimelineError(f"not an ending: {text!r}; use {', '.join(k + (' <s>' if k in timed else '') for k in kinds)}")
    secs = seconds(parts[1]) if len(parts) > 1 else 0
    if parts[0] in timed and secs is None:
        raise TimelineError(f'{parts[0]} needs its seconds, as in "{parts[0]} 4"')
    return parts[0], secs


def ending_text(end):
    kind, secs = end
    return f'{kind} {num(secs)}' if secs else kind


def letters(n):
    """1 → a, 26 → z, 27 → aa."""
    out = ''
    while n:
        n, r = divmod(n - 1, 26)
        out = chr(97 + r) + out
    return out


def letter_index(text):
    n = 0
    for c in text:
        n = n * 26 + ord(c) - 96
    return n


def next_id(scene_num, shots, retired=()):
    """The next letter after every shot the scene has or has had."""
    used = [letter_index(m.group(2)) for m in (SHOT.match(x) for x in [s['id'] for s in shots] + list(retired))
            if m and int(m.group(1)) == scene_num]
    return f'{scene_num}{letters(max(used, default=0) + 1)}'


def find_shot(shots, shot_id):
    for i, s in enumerate(shots):
        if s['id'] == shot_id:
            return i
    return None


def shot_in(scene, text):
    """The index of shot `text` in `scene`; refused when it names another scene or no shot."""
    text = text.strip()
    m = SHOT.match(text)
    if not m:
        raise TimelineError(f'not a shot id: {text!r}; a shot id is a scene number and letters, as in {scene["num"]}a')
    if int(m.group(1)) != scene['num']:
        raise TimelineError(f"{text} is in scene {m.group(1)}, not {scene['num']} {scene['name']}")
    i = find_shot(scene['shots'], text)
    if i is None:
        raise TimelineError(f"{scene['num']} {scene['name']} has no shot {text}")
    return i


def ref(text, scene):
    """A layer end → {'shot': id, 'at': seconds into it or None}, or None for `open`."""
    text = (text or '').strip()
    if text == 'open':
        return None
    m = REF.match(text)
    if not m:
        raise TimelineError(f'not a layer end: {text!r}; use a shot id, as in {scene["num"]}b, '
                            f'{scene["num"]}b+8, or open')
    shot = scene['shots'][shot_in(scene, m.group(1))]
    at = float(m.group(2)) if m.group(2) else None
    if at is not None and shot['length'] is None:
        raise TimelineError(f"{shot['id']} {shot['name']} has no length yet; give it one first")
    return {'shot': shot['id'], 'at': at}


def ref_text(r):
    if r is None:
        return 'open'
    return r['shot'] + (f"+{num(r['at'])}" if r['at'] is not None else '')


def parse(scene, shot_lines, layer_lines, take_lines):
    """Fill scene['shots'], scene['layers'] and scene['takes'] from their tables, each item keeping
    its row, and scene['heads'] with each table's header."""
    heads = scene['heads'] = {}
    heads['shots'], rows = table(shot_lines, SHOTS)
    scene['shots'], seen = [], set()
    for r in rows:
        if not r['shot']:
            continue
        m = SHOT.match(r['id'])
        if m and int(m.group(1)) != scene['num']:
            raise TimelineError(f"shot {r['id']} carries scene {m.group(1)}'s number, but its scene is scene "
                                f"{scene['num']}; put the scene table's rows back in their order, then use scene move")
        if not m or r['id'] in seen:
            raise TimelineError(f"shot id {r['id']!r} is not a new id for scene {scene['num']}, as in {scene['num']}a")
        seen.add(r['id'])
        scene['shots'].append({'id': r['id'], 'name': name(r['shot']), 'length': seconds(r['length']),
                               'ends': ending(r['ends'] or 'cut'), 'shows': r['shows'], 'note': r['note'], 'row': r})
    fades = ('cut', 'fade')
    heads['layers'], rows = table(layer_lines, LAYERS)
    scene['layers'] = [{'name': name(r['layer']), 'from': ref(r['from'], scene), 'to': ref(r['to'], scene),
                        'in': ending(r['in'] or 'cut', fades), 'out': ending(r['out'] or 'cut', fades),
                        'file': r['file'], 'note': r['note'], 'row': r} for r in rows if r['layer']]
    heads['takes'], rows = table(take_lines, TAKES)
    scene['takes'] = []
    for r in rows:
        if not r['take']:
            continue
        m = TAKE.match(r['take'])
        tid = m and f'{m.group(1)}.{int(m.group(2))}'
        if not m or find_shot(scene['shots'], m.group(1)) is None or find_take([scene], tid):
            raise TimelineError(f"take {r['take']!r} is not a new take of a shot in scene {scene['num']}, "
                                f"as in {scene['num']}a.1")
        if m.group(3) and approved(scene, m.group(1)):
            raise TimelineError(f'{m.group(1)} has two approved takes; mark one with +')
        scene['takes'].append({'id': tid, 'shot': m.group(1), 'approved': bool(m.group(3)), 'file': r['file'],
                               'prompt': r['prompt'], 'model': r['model'], 'refs': r['refs'],
                               'in': seconds(r['in']), 'note': r['note'], 'row': r})


def tables(scene):
    """The `## Shots`, `## Layers` and `## Takes` bodies, takes in their shots' order; None for a section
    with nothing in it."""
    place = {x['id']: i for i, x in enumerate(scene['shots'])}
    shots = [{**x['row'], 'id': x['id'], 'shot': x['name'], 'length': '' if x['length'] is None else str(num(x['length'])),
              'ends': ending_text(x['ends']), 'shows': x['shows'], 'note': x['note']} for x in scene['shots']]
    layers = [{**x['row'], 'layer': x['name'], 'from': ref_text(x['from']), 'to': ref_text(x['to']),
               'in': ending_text(x['in']), 'out': ending_text(x['out']), 'file': x['file'], 'note': x['note']}
              for x in scene['layers']]
    takes = [{**t['row'], 'take': take_tag(t), 'file': t['file'], 'prompt': t['prompt'], 'model': t['model'],
              'refs': t['refs'], 'in': '' if t['in'] is None else str(num(t['in'])), 'note': t['note']}
             for t in sorted(scene['takes'], key=lambda t: (place[t['shot']], int(t['id'].split('.')[1])))]
    heads = scene['heads']
    return tuple(table_text(heads[kind], rows, known) if rows else None
                 for kind, rows, known in (('shots', shots, SHOTS), ('layers', layers, LAYERS), ('takes', takes, TAKES)))


# ── Takes ──────────────────────────────────────────────────────────

def take_tag(take):
    return take['id'] + ('+' if take['approved'] else '')


def approved(scene, shot_id):
    return next((t for t in scene['takes'] if t['shot'] == shot_id and t['approved']), None)


def next_take(scene, shot_id, retired=()):
    """The next number after every take the shot has or has had."""
    used = [int(t['id'].split('.')[1]) for t in scene['takes'] if t['shot'] == shot_id]
    used += [int(m.group(2)) for m in map(TAKE.match, retired) if m and m.group(1) == shot_id]
    return f'{shot_id}.{max(used, default=0) + 1}'


def basis(scene, shot, pins, scenes):
    """What a shot's prompt and approved take draw on, as a short key: its shows line (else its name),
    its scene's script and each pin over it but one keeping a take of the shot itself."""
    over = sorted(f"{p['name']}|{p['keep']}|{ref_file(scenes, p['ref']) or p['ref']}"
                  for p in pins_over(pins, scenes, shot['id']) if p['ref'].split('.')[0] != shot['id'])
    return hashlib.sha1('\n'.join([shot['shows'] or shot['name'], scene['script'], *over]).encode()).hexdigest()[:8]


def fill_basis(scene, pins, scenes):
    """Give each prompt and approved take kept with no basis the one it draws on now, so it starts
    unmarked; whether any was given."""
    filled = False
    for shot in scene['shots']:
        take = approved(scene, shot['id'])
        for row in ([shot['row']] if shot['row'].get('prompt') else []) + ([take['row']] if take else []):
            if not row.get(BASIS):
                row[BASIS], filled = basis(scene, shot, pins, scenes), True
    return filled


def to_review(scene, shot, pins, scenes):
    """The shot's prompt and approved take when what they draw on changed since they were written
    or approved."""
    now, take = basis(scene, shot, pins, scenes), approved(scene, shot['id'])
    return (['its prompt'] if shot['row'].get('prompt') and shot['row'].get(BASIS) not in (None, '', now) else []) \
        + ([f"approved take {take['id']}"] if take and take['row'].get(BASIS) not in (None, '', now) else [])


def review_text(what):
    return f"{' and '.join(what)}, since its shows line, the script or a pin over it changed"


def shot_tasks(scene, pins, scenes):
    """Each shot's open tasks: no take or no length yet, a take to pick among the ones it has, a prompt
    or approved take to review."""
    out = []
    for x in scene['shots']:
        takes = [t['id'] for t in scene['takes'] if t['shot'] == x['id']]
        gaps = ([] if takes else ['no take yet']) + (['no length yet'] if x['length'] is None else [])
        out += [f"shot {x['id']} {x['name']}: {', '.join(gaps)}"] if gaps else []
        if takes and not approved(scene, x['id']):
            out.append(f"shot {x['id']} {x['name']}: pick one of its takes ({', '.join(takes)})")
        what = to_review(scene, x, pins, scenes)
        out += [f"shot {x['id']} {x['name']}: review {review_text(what)}"] if what else []
    return out


def layer_text(layer):
    """The words a layer puts on screen (--meta text=): a title's, drawn in the cut when it has no file."""
    return layer['row'].get('text', '')


def layer_tasks(scene):
    """Each layer's open task: no file yet, unless it has words to draw."""
    return [f"layer {l['name']}: no file yet" for l in scene['layers'] if not l['file'] and not layer_text(l)]


def find_take(scenes, take_id):
    return next((t for s in scenes for t in s['takes'] if t['id'] == take_id), None)


def approve(scene, take):
    for t in scene['takes']:
        if t['shot'] == take['shot']:
            t['approved'] = t is take


# ── Editing ────────────────────────────────────────────────────────

def anchors(layers, shot_id):
    return [l['name'] for l in layers
            if any(l[s] is not None and l[s]['shot'] == shot_id for s in ('from', 'to'))]


def keeping(pins, shot_ids):
    """The pins that keep a take of any of `shot_ids`."""
    return [p['name'] for p in pins if (TAKE.match(p['ref']) or [None, None])[1] in shot_ids]


def remove_shot(scene, index, pins, scenes):
    shot = scene['shots'][index]
    users = list(dict.fromkeys(anchors(scene['layers'], shot['id']) + holding(pins, scenes, {shot['id']}) +
                               keeping(pins, {shot['id']})))
    if users:
        raise TimelineError(f"{shot['id']} {shot['name']} anchors {', '.join(users)}; "
                            'move or remove those first')
    scene['shots'].pop(index)
    scene['takes'] = [t for t in scene['takes'] if t['shot'] != shot['id']]


def move_shot(scene, index, dest, at, pins, scenes, retired):
    """Move a shot to place `at` in another scene, under the next id there, its takes with it under
    new ids; a pin naming it or keeping one of its takes follows. Refused when that changes what a
    pin or layer runs over. Returns the old id and the removed list renamed."""
    old = scene['shots'][index]['id']
    moved = next_id(dest['num'], dest['shots'], retired)

    def new(text):
        t = TAKE.match(text or '')
        return moved if text == old else f'{moved}.{t.group(2)}' if t and t.group(1) == old else text

    was = spans(pins, scenes)
    dest['shots'].insert(at, scene['shots'].pop(index))
    dest['takes'] += [t for t in scene['takes'] if t['shot'] == old]
    scene['takes'] = [t for t in scene['takes'] if t['shot'] != old]
    retired = rename(scenes, pins, retired, new)
    unmoved(was, new, pins, scenes)
    return old, retired


def rename(scenes, pins, removed, new):
    """Apply `new` to every id the story holds: shot and take ids, layer ends, pin ends and the
    takes pins keep. Returns the removed list renamed."""
    for s in scenes:
        for x in s['shots']:
            x['id'] = new(x['id'])
        for layer in s['layers']:
            layer['from'], layer['to'] = ({**r, 'shot': new(r['shot'])} if r else r for r in (layer['from'], layer['to']))
        for t in s['takes']:
            t['id'], t['shot'] = new(t['id']), new(t['shot'])
    for p in pins:
        p['from'], p['to'] = new(p['from']), new(p['to'])
        p['ref'] = new(p['ref']) if TAKE.match(p['ref']) else p['ref']
    return [new(x) for x in removed]


def renumber(scenes, pins, removed):
    """Number the scenes by their place in `scenes`, every id naming one following. Returns the
    removed list renamed and the renaming."""
    to = {s['num']: n for n, s in enumerate(scenes, 1)}

    def new(text):
        m = ID.match(text or '')
        return f"{to[int(m.group(1))]}{m.group(2) or ''}" if m and int(m.group(1)) in to else text

    removed = rename(scenes, pins, removed, new)
    for s in scenes:
        s['num'] = to[s['num']]
    return removed, new


def find_scene(story, ref):
    """A scene by its number, or by its name: the scene named so, else the one whose name holds the
    words. Two or more are refused with their list."""
    text, scenes = str(ref).strip(), story['scenes']
    if text.isdigit():
        for s in scenes:
            if s['num'] == int(text):
                return s
        raise TimelineError(f"no scene {text}; the scenes are {', '.join(str(s['num']) for s in scenes)}")
    hits = [s for s in scenes if same(s['name'], text)] or \
        [s for s in scenes if text.casefold() in s['name'].casefold()]
    listed = lambda found: ', '.join(f"{s['num']} {s['name']}" for s in found) or 'none yet'
    if len(hits) > 1:
        raise TimelineError(f'{text!r} fits {len(hits)} scenes: {listed(hits)}; give its number')
    if not hits:
        raise TimelineError(f'no scene {text!r}; the scenes are {listed(scenes)}')
    return hits[0]


def scene_ref(story, text):
    """A pin end as given, a scene's name turned into its number."""
    text = (text or '').strip()
    return text if not text or text.isdigit() or SHOT.match(text) else str(find_scene(story, text)['num'])


def scene_of(story, shot_id):
    """The scene a shot id belongs to, and the shot's index in it."""
    m = SHOT.match(shot_id.strip())
    if not m:
        raise TimelineError(f'{shot_id} is not a shot id; a shot id is a scene number and letters, as in 3b')
    s = readable(find_scene(story, m.group(1)))
    return s, shot_in(s, shot_id)


def unread(scene):
    return f"{scene['num']} {scene['name']}: its timeline can't be read: {scene['broken']}"


def readable(scene):
    if scene['broken']:
        raise TimelineError(unread(scene))
    return scene


def retire(story, tag):
    """Record a removed scene file, shot id or take id, so a new one never takes it."""
    best = {}
    for x in story['removed'] + [tag]:
        t, m = TAKE.match(x), SHOT.match(x)
        key, rank = ((t.group(1) + '.', int(t.group(2))) if t else
                     (m.group(1), letter_index(m.group(2))) if m else (x, 0))
        if key not in best or rank > best[key][0]:
            best[key] = (rank, x)
    story['removed'] = [x for _, x in best.values()]


def keep_work(what, work, force):
    """Refuse to remove `what` while it holds work, unless `force`."""
    if work and not force:
        raise TimelineError(f"removing {what} would lose {', '.join(work)}; add --force to remove it anyway")


def find_layer(scene, name):
    for layer in scene['layers']:
        if same(layer['name'], name):
            return layer
    raise TimelineError(f"no layer {name!r} in {scene['num']} {scene['name']}")


def carry(scenes, scene, layer):
    """The run `layer` belongs to, in story order: (scene, layer) for it and for the layer of its
    name in each scene it carries into or out of, as the cut joins them."""
    at = next(n for n, x in enumerate(scenes) if x is scene)
    run = [(scene, layer)]
    for step, leave, enter in ((-1, 'from', 'to'), (1, 'to', 'from')):
        i, here = at + step, layer
        while here[leave] is None and 0 <= i < len(scenes):
            here = next((l for l in scenes[i]['layers'] if l['name'] == layer['name'] and l[enter] is None), None)
            if not here:
                break
            run.insert(0 if step < 0 else len(run), (scenes[i], here))
            i += step
    return run


def edit_shot(story, a):
    """Add, change, move or remove a shot; returns the scenes it changed. A prompt set, or --reviewed,
    keeps what the prompt (and with --reviewed the approved take) now draws on."""
    pairs = meta_pairs(getattr(a, 'meta', None), SHOTS + (BASIS,))
    pins = story['pins'] + story['series_pins']
    if a.op == 'add':
        s = find_scene(story, a.target)
        shots = s['shots']
        at = shot_in(s, a.before) if a.before else len(shots)
        shot = {'id': next_id(s['num'], shots, story['removed']), 'name': name(a.name), 'length': seconds(a.length),
                'ends': ending(a.ends), 'shows': cell(a.shows), 'note': '', 'row': dict(pairs)}
        shots.insert(at, shot)
        if shot['row'].get('prompt'):
            shot['row'][BASIS] = basis(s, shot, pins, story['scenes'])
        return [s]
    s, i = scene_of(story, a.target)
    shots = s['shots']
    if a.op == 'set':
        shot, take = shots[i], approved(s, shots[i]['id'])
        shot.update({'name': name(a.name) if a.name else shot['name'],
                     'length': seconds(a.length) if a.length else shot['length'],
                     'ends': ending(a.ends) if a.ends else shot['ends'],
                     'shows': cell(a.shows) if a.shows is not None else shot['shows'],
                     'note': cell(a.note) if a.note is not None else shot['note']})
        shot['row'].update(pairs)
        now = basis(s, shot, pins, story['scenes'])
        if 'prompt' in dict(pairs) or a.reviewed:
            shot['row'][BASIS] = now if shot['row'].get('prompt') else ''
        if a.reviewed and take:
            take['row'][BASIS] = now
    elif a.op == 'move':
        dest, j = scene_of(story, a.to) if SHOT.match(a.to.strip()) else (find_scene(story, a.to), None)
        if dest is not s:
            gone, story['removed'] = move_shot(s, i, dest, len(dest['shots']) if j is None else j,
                                                        story['pins'], story['scenes'], story['removed'])
            retire(story, gone)
            return [s, dest]
        was = spans(story['pins'], story['scenes'])
        shots.insert(len(shots) if j is None else j, shots.pop(i))
        unmoved(was, lambda x: x, story['pins'], story['scenes'])
    else:
        shot, takes = shots[i], [t['id'] for t in s['takes'] if t['shot'] == shots[i]['id']]
        remove_shot(s, i, story['pins'], story['scenes'])
        keep_work(f"{shot['id']} {shot['name']}", [f"takes {', '.join(takes)}"] if takes else [], a.force)
        retire(story, shot['id'])
    return [s]


def edit_layer(story, a):
    """Add, change or remove a layer; returns the scenes it changed, the one named last. A carried
    layer keeps one file: a file given goes to every scene of its run, under the run's first scene,
    unless it is the file the layer already keeps; a layer added into a run with a file takes it."""
    s = find_scene(story, a.target)
    layers = s['layers']
    pairs = meta_pairs(getattr(a, 'meta', None), LAYERS)
    end = lambda text: ending(text, ('cut', 'fade'))
    if a.op == 'add':
        if any(same(l['name'], a.name) for l in layers):
            raise TimelineError(f"{s['num']} {s['name']} already has a layer {a.name!r}")
        layer = {'name': name(a.name), 'from': ref(a.start, s), 'to': ref(a.end, s),
                 'in': end(a.fade_in), 'out': end(a.fade_out), 'file': '', 'note': '', 'row': dict(pairs)}
        layers.append(layer)
    elif a.op == 'set':
        layer = find_layer(s, a.name)
        if a.rename and any(l is not layer and same(l['name'], a.rename) for l in layers):
            raise TimelineError(f"{s['num']} {s['name']} already has a layer {a.rename!r}")
        values = {'name': name(a.rename) if a.rename else layer['name'],
                  'note': cell(a.note) if a.note is not None else layer['note']}
        for key, value, read in (('from', a.start, lambda v: ref(v, s)),
                                 ('to', a.end, lambda v: ref(v, s)),
                                 ('in', a.fade_in, end), ('out', a.fade_out, end)):
            values[key] = read(value) if value else layer[key]
        layer.update(values)
        layer['row'].update(pairs)
    else:
        layers.remove(find_layer(s, a.name))
        return [s]
    run = carry(story['scenes'], s, layer)
    held, given = layer['file'] and local(story['path'], layer['file']), Path(a.file or '').expanduser()
    if a.file and not a.link and held and held.is_file() and given.is_file() and filecmp.cmp(held, given, shallow=False):
        file = layer['file']
    elif a.file:
        file = keep_asset(story, f"{run[0][0]['num']} {layer['name']}", a.file, a.link)
    elif a.op == 'add':
        file = next((l['file'] for _, l in run if l['file']), '')
    else:
        return [s]
    for _, l in run:
        l['file'] = file
    return [x for x, _ in run if x is not s] + [s]


def edit_take(story, a):
    pairs = meta_pairs(getattr(a, 'meta', None), TAKES + (BASIS,))
    if a.op == 'add':
        s, i = scene_of(story, a.target)
        shot = s['shots'][i]
        tid = next_take(s, shot['id'], story['removed'])
        over = pins_over(story['pins'] + story['series_pins'], story['scenes'], shot['id'])
        refs = a.refs if a.refs is not None else \
            ', '.join(dict.fromkeys(ref_file(story['scenes'], p['ref']) or p['ref'] for p in over))
        prompt = a.prompt if a.prompt is not None else shot['row'].get('prompt')
        take = {'id': tid, 'shot': shot['id'], 'approved': False, 'prompt': cell(prompt),
                'model': cell(a.model), 'refs': cell(refs), 'in': seconds(a.inpoint),
                'note': cell(a.note), 'row': dict(pairs)}
        take['file'] = keep_asset(story, tid, a.file, a.link)
        s['takes'].append(take)
    else:
        m = TAKE.match(a.target.strip().rstrip('+'))
        if not m:
            raise TimelineError(f'{a.target} is not a take id; a take id is a shot id and a number, as in 3a.2')
        s, _ = scene_of(story, m.group(1))
        take = find_take([s], f'{m.group(1)}.{int(m.group(2))}')
        if not take:
            raise TimelineError(f"{m.group(1)} has no take {a.target}")
    if a.op == 'set':
        values = {key: cell(getattr(a, key)) for key in ('prompt', 'model', 'refs', 'note')
                  if getattr(a, key) is not None}
        if a.inpoint is not None:
            values['in'] = seconds(a.inpoint)
        take.update(values)
        take['row'].update(pairs)
    elif a.op == 'remove':
        users = [p['name'] for p in story['pins'] if p['ref'] == take['id']]
        if users:
            raise TimelineError(f"{take['id']} is kept by {', '.join(users)}; change or remove those pins first")
        s['takes'].remove(take)
        retire(story, take['id'])
    elif a.op == 'unapprove':
        take['approved'] = False
    elif a.op == 'approve' or a.approve:
        approve(s, take)
        shot = s['shots'][find_shot(s['shots'], take['shot'])]
        take['row'][BASIS] = basis(s, shot, story['pins'] + story['series_pins'], story['scenes'])
    return [s]


def pin_ref(story, a, start, end):
    """What a pin keeps: a take id, a link, or a file copied into assets/."""
    if a.ref and TAKE.match(a.ref):
        if not find_take(story.get('scenes', []), a.ref):
            raise TimelineError(f'no take {a.ref} in the story')
        return a.ref
    if a.ref:
        return keep_asset(story, getattr(a, 'rename', None) or a.name, a.ref, a.link)
    if 'scenes' not in story or not start or start != end or not SHOT.match(start):
        raise TimelineError('give --ref: the file, link or take to keep')
    s, i = scene_of(story, start)
    best = approved(s, start)
    if not best:
        raise TimelineError(f"{start} {s['shots'][i]['name']} has no approved take; approve one or give --ref")
    return best['id']


def edit_pin(story, a, end):
    """Add, change or remove a pin of a story (ends: shots and scenes) or a series (ends: threads)."""
    pins = story['pins']
    pairs = meta_pairs(getattr(a, 'meta', None), PINS)
    found = [p for p in pins if same(p['name'], a.name)]
    if a.op == 'add':
        if found:
            raise TimelineError(f"there is already a pin {found[0]['name']!r}")
        start = end(a.start or a.end)
        stop = end(a.end) or start
        pin = {'name': name(a.name), 'from': start, 'to': stop, 'broken': None,
               'keep': name(a.keep), 'note': cell(a.note), 'row': dict(pairs)}
        pin['ref'] = pin_ref(story, a, start, stop)
        pins.append(pin)
        return
    if not found:
        raise TimelineError(f'no pin {a.name!r}')
    pin = found[0]
    if a.op == 'remove':
        pins.remove(pin)
        return
    if a.rename and any(p is not pin and same(p['name'], a.rename) for p in pins):
        raise TimelineError(f'there is already a pin {a.rename!r}')
    start, stop = pin['from'], pin['to']
    if a.start is not None:
        start = end(a.start)
        stop = stop if a.end else start
    if a.end is not None:
        stop = end(a.end) or start
    values = {'from': start, 'to': stop, 'keep': name(a.keep) if a.keep else pin['keep'],
              'name': name(a.rename) if a.rename else pin['name'],
              'note': cell(a.note) if a.note is not None else pin['note']}
    values['ref'] = pin_ref(story, a, start, stop) if a.ref else pin['ref']
    pin.update(values)
    pin['row'].update(pairs)
    settle(pin, end)


# ── Time ───────────────────────────────────────────────────────────

def drawn(shots):
    """Each shot's length for drawing: a shot with no length yet takes the scene's average."""
    known = [s['length'] for s in shots if s['length'] is not None]
    guess = sum(known) / len(known) if known else UNKNOWN
    return [guess if s['length'] is None else s['length'] for s in shots]


def starts(lengths):
    out, t = [], 0
    for n in lengths:
        out.append(t)
        t += n
    return out


def known(shots):
    return all(s['length'] is not None for s in shots)


def span(layer, shots):
    """(start, end) of a layer in scene seconds; an open end sits on the scene's edge."""
    lengths = drawn(shots)
    t0 = starts(lengths)

    def at(r, is_end):
        if r is None:
            return sum(lengths) if is_end else 0
        i = find_shot(shots, r['shot'])
        if r['at'] is not None:
            return t0[i] + r['at']
        return t0[i] + lengths[i] if is_end else t0[i]

    return at(layer['from'], False), at(layer['to'], True)


# ── Pins ───────────────────────────────────────────────────────────

def pin_end(text, scenes):
    """A pin end: a shot id or a scene number in the story, or None for the whole story."""
    text = (text or '').strip()
    if not text:
        return None
    for s in scenes:
        if text == str(s['num']) or find_shot(s['shots'], text) is not None:
            return text
    raise TimelineError(in_unread(scenes, text) or f'no scene or shot {text} in the story')


def in_unread(scenes, tag):
    """Why shot or take `tag` can't be found when its scene can't be read; None otherwise."""
    m = ID.match(tag)
    hit = next((s for s in scenes if m and m.group(2) and s['broken'] and s['num'] == int(m.group(1))), None)
    return hit and f"{tag} is in {hit['num']} {hit['name']}, whose timeline can't be read"


def parse_pins(lines, end):
    """The pins table's header and pins; one whose end `end` refuses is kept as written, with its
    reason."""
    head, rows = table(lines, PINS)
    out = []
    for r in rows:
        if r['pin']:
            out.append({'name': r['pin'], 'from': r['from'] or None, 'to': r['to'] or r['from'] or None,
                        'keep': r['keep'], 'ref': r['ref'], 'note': r['note'], 'row': r})
            settle(out[-1], end)
    return head, out


def settle(pin, end):
    """Mark a pin broken when `end` refuses one of its ends."""
    try:
        end(pin['from']), end(pin['to'])
        pin['broken'] = None
    except TimelineError as e:
        pin['broken'] = str(e)


def pins_table(head, pins):
    if not pins:
        return None
    return table_text(head, [{**p['row'], 'pin': p['name'], 'from': p['from'] or '',
                              'to': '' if p['to'] == p['from'] else p['to'], 'keep': p['keep'], 'ref': p['ref'],
                              'note': p['note']} for p in pins], PINS)


def covers(pin, scenes):
    """The scene numbers and shot ids a pin runs over, in story order."""
    marks = [(str(s['num']), tag) for s in scenes for tag in [str(s['num'])] + [x['id'] for x in s['shots']]]
    if pin['from'] is None:
        return {n for n, _ in marks} | {t for _, t in marks}
    tags = [t for _, t in marks]

    def first(end):
        return tags.index(end)

    def last(end):
        return max(i for i, (n, _) in enumerate(marks) if n == end) if end.isdigit() else tags.index(end)

    a, b = first(pin['from']), last(pin['to'])
    if b < a:
        a, b = first(pin['to']), last(pin['from'])
    inside = marks[a:b + 1]
    return {n for n, _ in inside} | {t for _, t in inside}


def pinned(pins, scenes):
    """Every scene number and shot id some pin with a target runs over."""
    out = set()
    for p in pins:
        if p['from'] is not None and not p['broken']:
            out |= covers(p, scenes)
    return out


def holding(pins, scenes, tags):
    """The pins that name or run over any of `tags`."""
    return [p['name'] for p in pins if p['from'] is not None and
            ({p['from'], p['to']} & tags or (not p['broken'] and covers(p, scenes) & tags))]


def layer_span(layer, shots):
    """The shot ids a layer runs over in its scene; None when an end names a shot not in it."""
    ids = [x['id'] for x in shots]
    a, b = (layer[side] and layer[side]['shot'] for side in ('from', 'to'))
    if (a and a not in ids) or (b and b not in ids):
        return None
    return set(ids[ids.index(a) if a else 0:(ids.index(b) if b else len(ids) - 1) + 1])


def spans(pins, scenes):
    """What each pin and each layer runs over, by scene number and shot id."""
    out = {('pin', '', p['name']): covers(p, scenes) for p in pins if p['from'] is not None and not p['broken']}
    out.update({('layer', str(s['num']), layer['name']): layer_span(layer, s['shots'])
                for s in scenes for layer in s['layers']})
    return out


def unmoved(was, new, pins, scenes):
    """Refuse a move that changes what a pin or layer runs over; `new` gives each id after the move."""
    now = spans(pins, scenes)
    before = {(kind, new(at), n): v if v is None else {new(x) for x in v} for (kind, at, n), v in was.items()}
    moved = sorted({key[2] for key in {*before, *now} if before.get(key) != now.get(key)})
    if moved:
        raise TimelineError(f"that move changes what {', '.join(moved)} runs over; change or remove those first")


# ── Drawing ────────────────────────────────────────────────────────

def layout(blocks, cols):
    """Each block's (x, width, start, length): widths follow length; names shorten to fit cols."""
    total = sum(b['length'] for b in blocks) or 1
    cap = max((len(b['name']) for b in blocks), default=0)
    shade = {'fade': 3, 'dissolve': 2}
    edges = [shade.get(b['ends'][0], 0) + (shade.get(blocks[i - 1]['ends'][0], 0) if i else 0)
             for i, b in enumerate(blocks)]
    while cap > 1 and sum(min(len(b['name']), cap) + 6 + e for b, e in zip(blocks, edges)) > cols:
        cap -= 1
    need = [min(len(b['name']), cap) + 6 + e for b, e in zip(blocks, edges)]
    k = cols / total
    while k > 0.01 and sum(max(n, round(b['length'] * k)) for n, b in zip(need, blocks)) > cols:
        k *= 0.97
    xs, x, t = [], 0, 0
    for n, b in zip(need, blocks):
        w = max(n, round(b['length'] * k))
        xs.append((x, w, t, b['length']))
        x, t = x + w, t + b['length']
    return xs, x


def column(xs, t):
    for x0, w, t0, n in xs:
        if t <= t0 + n:
            return x0 + round((t - t0) / (n or 1) * w)
    return xs[-1][0] + xs[-1][1]


def fit(text, room):
    return text if len(text) <= room else (text[:room - 1] + '…' if room > 1 else '')


def boxes(blocks, xs, width, enter):
    """The strip: one box per block. Wall = cut, double wall = match, shade = dissolve or fade."""
    top, mid, bot = ['─'] * (width + 1), [' '] * (width + 1), ['─'] * (width + 1)
    top[0], mid[0], bot[0], top[width], mid[width], bot[width] = '┌', '│', '└', '┐', '│', '┘'
    start = {'dissolve': 4, 'fade': 5}.get(enter, 2)
    if enter == 'dissolve':
        mid[1:3] = '░░'
    elif enter == 'fade':
        mid[1:4] = FADE_IN
    elif enter == 'match':
        mid[0] = '║'
    labels = []
    for n, (b, (x0, w, t0, _)) in enumerate(zip(blocks, xs)):
        if b.get('unknown'):
            for i in range(x0 + 1, x0 + w):
                top[i] = bot[i] = '┄'
        if n:
            kind, secs = blocks[n - 1]['ends']
            if kind == 'dissolve':
                a = column(xs, t0 - secs / 2)
                c = max(column(xs, t0 + secs / 2), a + 2)
                mid[a:c] = '░' * (c - a)
                edge, nxt = a, c + 1
            else:
                top[x0], bot[x0] = '┬', '┴'
                mid[x0] = '║' if kind == 'match' else '│'
                edge, nxt = x0, x0 + 2
                if kind == 'fade':
                    mid[x0 - 3:x0], mid[x0 + 1:x0 + 4] = FADE_OUT, FADE_IN
                    edge, nxt = x0 - 3, x0 + 5
            labels[-1][1] = edge - 1
            start = nxt
        labels.append([start, width, b['name']])
    kind, _ = blocks[-1]['ends']
    tail = {'fade': 3, 'dissolve': 2}.get(kind, 0)
    labels[-1][1] = width - tail - 1
    if kind == 'fade':
        mid[width - 3:width] = FADE_OUT
    elif kind == 'dissolve':
        mid[width - 2:width] = '░░'
    elif kind == 'match':
        mid[width] = '║'
    for a, b, text in labels:
        text = fit(text, b - a)
        mid[a:a + len(text)] = text
    return [top, mid, bot]


def bar(xs, total, width, layer):
    """A layer as (column, cells): `├ ┤` where it snaps, a short shade where it fades."""
    open_l, open_r = layer['t0'] is None, layer['t1'] is None
    a = 1 if open_l else column(xs, layer['t0']) + 1
    b = max(column(xs, total if open_r else layer['t1']) - 1, a + 1)
    cells = ['─'] * (b - a + 1)
    fade_in = 0 if open_l else layer['in'][1]
    fade_out = 0 if open_r else layer['out'][1]
    n_in = min(3, max(2, column(xs, layer['t0'] + fade_in) - a)) if fade_in else 0
    n_out = min(3, max(2, b + 1 - column(xs, layer['t1'] - fade_out))) if fade_out else 0
    cells[:max(1, n_in)] = FADE_IN[:n_in] or ('─' if open_l else '├')
    cells[len(cells) - max(1, n_out):] = FADE_OUT[3 - n_out:] or ('─' if open_r else '┤')
    text = f" {layer['name']} "
    inner = len(cells) - max(1, n_in) - max(1, n_out)
    if inner >= len(text) + 2:
        s = max(1, n_in) + 1
        cells[s:s + len(text)] = text
        return a, cells
    right, left = width - b, a - 1
    if right >= len(text) - 1 or right >= left:
        return a, cells + list(fit(text.rstrip(), right))
    text = fit(text.lstrip(), left)
    return a - len(text), list(text) + cells


def stack(bars):
    """Bars into the fewest rows; a bar joins the first row it doesn't touch."""
    rows = []
    for a, cells in bars:
        for row in rows:
            if all(c == ' ' for c in row[max(0, a - 2):a + len(cells) + 2]):
                break
        else:
            row = []
            rows.append(row)
        row.extend(' ' * (a + len(cells) + 1 - len(row)))
        row[a:a + len(cells)] = cells
    return rows


def rows_of(blocks, cols):
    """Blocks split into runs that each fit cols with names of four letters or more."""
    shade = {'fade': 3, 'dissolve': 2}
    need = [min(len(b['name']), 4) + 6 + shade.get(b['ends'][0], 0) * 2 for b in blocks]
    runs, start, used = [], 0, 0
    for i, n in enumerate(need):
        if i > start and used + n > cols:
            runs.append((start, i))
            start, used = i, 0
        used += n
    return runs + [(start, len(blocks))]


def clip(layer, t0, t1):
    """A layer cut to the window t0..t1, open where it runs past; None when it's outside."""
    a = float('-inf') if layer['t0'] is None else layer['t0']
    b = float('inf') if layer['t1'] is None else layer['t1']
    if b <= t0 or a >= t1:
        return None
    return {**layer, 't0': None if a < t0 else a - t0, 't1': None if b > t1 else b - t0}


def strip(title, ids, blocks, layers, cols, enter='cut'):
    """The strip, wrapped onto more rows when its blocks can't fit the window side by side."""
    out, t = [f'  {title}'], 0
    for i, j in rows_of(blocks, cols):
        part = blocks[i:j]
        total = sum(b['length'] for b in part)
        xs, width = layout(part, cols)
        numbers = [' '] * (width + 1)
        for (x0, *_), tag in zip(xs, ids[i:j]):
            numbers[x0:x0 + len(tag)] = tag
        seen = [c for c in (clip(l, t, t + total) for l in layers) if c]
        rows = [numbers, *boxes(part, xs, width, blocks[i - 1]['ends'][0] if i else enter),
                *stack(bar(xs, total, width, l) for l in seen)]
        out += ([''] if i else []) + ['  ' + ''.join(r).rstrip() for r in rows]
        t += total
    return out


def tag(text, marked):
    return text + ('•' if text in marked else '')


def scene_layers(scene):
    out = []
    for layer in scene['layers']:
        t0, t1 = span(layer, scene['shots'])
        out.append({**layer, 't0': None if layer['from'] is None else t0,
                    't1': None if layer['to'] is None else t1})
    return out


def scene_strip(scene, enter, cols, marked=()):
    shots = scene['shots']
    title = f"{tag(str(scene['num']), marked)}  {scene['name']}"
    if not shots:
        return [f'  {title}', '  no shots yet']
    blocks = [{**s, 'length': n, 'unknown': s['length'] is None} for s, n in zip(shots, drawn(shots))]
    return strip(title, [tag(s['id'], marked) for s in shots], blocks, scene_layers(scene), cols, enter)


def enters(scenes):
    """How each scene is entered: the way the scene before it ends."""
    out, prev = [], 'cut'
    for s in scenes:
        out.append(prev)
        prev = s['shots'][-1]['ends'][0] if s['shots'] else 'cut'
    return out


def crossing(scenes, offsets):
    """Layers that cross a scene edge, joined into one bar per run, in story seconds."""
    runs, live = [], {}
    for s, off in zip(scenes, offsets):
        nxt = {}
        for layer in scene_layers(s) if s['shots'] else []:
            if layer['t0'] is None and layer['name'] in live:
                run = live.pop(layer['name'])
            elif layer['t1'] is None:
                run = {**layer, 't0': off + layer['t0'] if layer['t0'] is not None else None}
                runs.append(run)
            else:
                continue
            run['out'] = layer['out']
            run['t1'] = None if layer['t1'] is None else off + layer['t1']
            if layer['t1'] is None:
                nxt[layer['name']] = run
        live = nxt
    return runs


def scene_length(scene):
    return sum(drawn(scene['shots']))


def story_strip(title, scenes, cols, marked=()):
    planned = [scene_length(s) for s in scenes if s['shots']]
    guess = sum(planned) / len(planned) if planned else 60
    blocks = [{'name': s['name'], 'length': scene_length(s) or guess,
               'ends': s['shots'][-1]['ends'] if s['shots'] else ('cut', 0),
               'unknown': not s['shots'] or not known(s['shots'])} for s in scenes]
    sure = sum(x['length'] for s in scenes for x in s['shots'] if x['length'] is not None)
    whole = all(s['shots'] and known(s['shots']) for s in scenes)
    total = clock(sure) + ('' if whole else ' so far') if sure else 'no lengths yet'
    return strip(f'{title}  ·  {total}', [tag(str(s['num']), marked) for s in scenes], blocks,
                 crossing(scenes, starts([b['length'] for b in blocks])), cols)


# ── Detail ─────────────────────────────────────────────────────────

def pins_over(pins, scenes, target):
    return [p for p in pins if not p['broken'] and target in covers(p, scenes)]


def ref_file(scenes, ref):
    """The file a pin keeps: a take's file for a take id, else the ref; None for a missing take."""
    if not TAKE.match(ref):
        return ref
    take = find_take(scenes, ref)
    return take and take['file']


def pin_lines(pins, scenes, target):
    over = pins_over(pins, scenes, target)
    if not over:
        return []
    w = max(len(p['name']) for p in over)
    return ['  pinned'] + [f"    {p['name']:<{w}}  keep {p['keep'] or 'its look'}  ·  {p['ref']}"
                           + (f" ({ref_file(scenes, p['ref'])})" if TAKE.match(p['ref']) else '')
                           + (f"  ·  {p['note']}" if p['note'] else '')
                           + ''.join(f'  ·  {k} {v}' for k, v in meta(p, PINS).items()) for p in over]


def note_lines(text):
    lines = (text or '').splitlines()
    return [f'  note    {lines[0]}'] + [f'          {line}' for line in lines[1:]] if lines else []


def meta(item, known):
    """A row's fields beyond the columns storypad knows: its meta."""
    return {k: v for k, v in item['row'].items() if k not in known and k != BASIS and v}


def meta_lines(fields):
    return [f'  {k:<7} {v}' for k, v in fields.items()]


def when(scene, index, story_offset):
    """Where shot `index` starts, or None when a length before it isn't known yet."""
    before = scene['shots'][:index]
    if not known(before) or story_offset is None:
        return None
    t = sum(s['length'] for s in before)
    return t, story_offset + t


def detail_shot(scene, index, story_offset, pins, scenes):
    s = scene['shots'][index]
    at = when(scene, index, story_offset)
    out = [f"  {s['id']}  {s['name']}  ·  {scene['num']} {scene['name']}",
           f"  starts  {clock(at[0])} in the scene, {clock(at[1])} in the story" if at
           else '  starts  not known: a shot before it has no length yet',
           f"  length  {'not known yet' if s['length'] is None else clock(s['length'])}",
           f"  ends    {ending_text(s['ends'])}"]
    what = to_review(scene, s, pins, scenes)
    out += [f'  review  {review_text(what)}'] if what else []
    if s['shows']:
        out.insert(1, f"  shows   {s['shows']}")
    out += note_lines(s['note']) + meta_lines(meta(s, SHOTS))
    takes = [t for t in scene['takes'] if t['shot'] == s['id']]
    if takes:
        w = max(len(take_tag(t)) for t in takes)
        out.append('  takes')
        out += [f"    {take_tag(t):<{w}}  " + '  ·  '.join([t['file']] + ([f"from {num(t['in'])}s"] if t['in'] else [])
                                                         + ([t['note']] if t['note'] else [])
                                                         + [f'{k} {v}' for k, v in meta(t, TAKES).items()])
                for t in takes]
    lengths = drawn(scene['shots'])
    t0 = starts(lengths)[index]
    over = [l for l in scene_layers(scene)
            if (l['t0'] or 0) < t0 + lengths[index] and (l['t1'] if l['t1'] is not None else 1e9) > t0]
    if over:
        out.append('  over it')
        out += [f"    {l['name']:<{max(len(x['name']) for x in over)}}  {layer_times(l, scene)}" for l in over]
    return out + pin_lines(pins, scenes, s['id'])


def detail_scene(scene, story_offset, pins, scenes):
    shots = scene['shots']
    out = [f"  {scene['num']}  {scene['name']}",
           f"  starts  {clock(story_offset)} in the story" if story_offset is not None
           else '  starts  not known: a scene before it has no shots or lengths yet']
    if shots:
        out.append(f"  length  {clock(sum(s['length'] for s in shots))}" if known(shots)
                   else '  length  not known: some shots have no length yet')
        out.append('  shots   ' + ', '.join(f"{s['id']} {s['name']}" for s in shots))
    else:
        out.append('  no shots yet')
    out += note_lines(scene['note']) + meta_lines(scene['meta'])
    if scene['layers']:
        out.append('  layers')
        w = max(len(l['name']) for l in scene['layers'])
        out += [f"    {l['name']:<{w}}  {layer_times(l, scene)}" for l in scene['layers']]
    return out + pin_lines(pins, scenes, str(scene['num']))


def layer_times(layer, scene):
    def end(r, t, outward):
        if r is None:
            return outward
        i = find_shot(scene['shots'], r['shot'])
        return clock(t) if known(scene['shots'][:i + 1]) else ref_text(r)

    t0, t1 = span(layer, scene['shots'])
    return (f"{end(layer['from'], t0, 'from the scene before')} → "
            f"{end(layer['to'], t1, 'into the scene after')}  ·  "
            f"in {ending_text(layer['in'])}, out {ending_text(layer['out'])}")


# ── Checks ─────────────────────────────────────────────────────────

def reach(shot):
    """How far into a shot a layer can point: its length, plus the half of a dissolve past the cut."""
    kind, secs = shot['ends']
    return shot['length'] + (secs / 2 if kind == 'dissolve' else 0)


def settled(layer, shots):
    """Whether every length a layer's ends depend on is known."""
    k = 0
    for side in ('from', 'to'):
        r = layer[side]
        if r is None:
            k = max(k, len(shots) if side == 'to' else 0)
        else:
            k = max(k, find_shot(shots, r['shot']) + (side == 'to' and r['at'] is None))
    return known(shots[:k])


def problems(scenes):
    out = []
    for n, s in enumerate(scenes):
        shots, here = s['shots'], f"{s['num']} {s['name']}"
        after = scenes[n + 1] if n + 1 < len(scenes) else None
        before = scenes[n - 1] if n else None
        for x in shots:
            kind, secs = x['ends']
            if x['length'] is not None and secs > x['length']:
                out.append(f"{x['id']} {x['name']}: its {kind} is longer than the shot")
        if shots and shots[-1]['ends'][0] in ('dissolve', 'match') and not after:
            out.append(f"{here}: ends on a {shots[-1]['ends'][0]} with no scene after it")
        for l in s['layers']:
            if settled(l, shots):
                t0, t1 = span(l, shots)
                if t1 <= t0:
                    out.append(f"{here}: {l['name']} ends before it starts")
            for side in ('from', 'to'):
                r = l[side]
                shot = r and shots[find_shot(shots, r['shot'])]
                if shot and r['at'] is not None and shot['length'] is not None and r['at'] > reach(shot):
                    out.append(f"{here}: {l['name']} points past the end of {shot['id']} {shot['name']}")
            if l['from'] is None and not any(m['name'] == l['name'] and m['to'] is None
                                             for m in (before or {'layers': []})['layers']):
                out.append(f"{here}: {l['name']} carries in, but the scene before doesn't carry it out")
            if l['to'] is None and not any(m['name'] == l['name'] and m['from'] is None
                                           for m in (after or {'layers': []})['layers']):
                out.append(f"{here}: {l['name']} carries out, but the scene after doesn't carry it in")
    return out


# ── Assets ─────────────────────────────────────────────────────────

def local(root, ref):
    path = Path(ref).expanduser()
    return path if path.is_absolute() else root / path


def keep_asset(story, label, source, weak):
    """The file a pin, take or layer stores: a link as given, or a copy inside assets/."""
    source = name(source)
    if weak:
        return source
    assets = story['path'] / 'assets'
    is_url = re.match(r'^https?://', source)
    path = None if is_url else Path(source).expanduser().resolve()
    if path and path.parent == assets.resolve():
        return name(f'assets/{path.name}')
    if path and not path.is_file():
        raise TimelineError(f'no file {source}')
    suffix = Path(source.split('?')[0]).suffix if is_url else path.suffix
    stem = unique(slug(label) or 'file', lambda k: (assets / f'{k}{suffix}').exists())
    kept = name(f'assets/{stem}{suffix}')
    assets.mkdir(exist_ok=True)
    try:
        if is_url:
            with urllib.request.urlopen(source, timeout=30) as r:
                save(story['path'] / kept, r.read())
        else:
            save(story['path'] / kept, path)
    except OSError as e:
        raise TimelineError(f"can't copy {source}: {e}; pass --link to keep a link instead")
    return kept


def kept_files(story):
    """Each pin, take and layer with the file it keeps: (who, as written, its path; None for a missing take)."""
    scenes = story.get('scenes', [])
    named = [(f"pin {p['name']}", p['ref'], ref_file(scenes, p['ref'])) for p in story['pins']]
    named += [(f"take {t['id']}", t['file'], t['file']) for s in scenes for t in s['takes']]
    named += [(f"layer {l['name']} in {s['num']}", l['file'], l['file']) for s in scenes for l in s['layers']]
    return named


def assets_missing(story):
    """Each pin whose end left the story, and each pin, take or layer whose file is gone."""
    out = [f"pin {p['name']}: {p['broken']}" for p in story['pins'] if p['broken']]
    scenes = story.get('scenes', [])
    for who, ref, path in kept_files(story):
        if path is None:
            out.append(f"{who}: {in_unread(scenes, ref) or f'no take {ref}'}")
        elif path and not re.match(r'^https?://', path) and not local(story['path'], path).exists():
            out.append(f'{who}: {path} is missing')
    return out


def unused_assets(story):
    """The files in the story's assets/ that no pin, take or layer keeps."""
    folder = story['path'] / 'assets'
    kept = {local(story['path'], path).resolve() for _, _, path in kept_files(story) if path}
    return sorted(p for p in folder.iterdir() if p.is_file() and not p.name.startswith('.')
                  and p.resolve() not in kept) if folder.is_dir() else []


def clean(target, stories, delete):
    """List each file in assets/ of `stories` that nothing keeps, or remove them; `target` is the
    folder named back."""
    found = [p for s in stories for p in unused_assets(s)]
    if not found:
        return '  every file in assets/ is kept by a pin, take or layer'
    for p in found if delete else []:
        p.unlink()
    head = 'removed, kept by no pin, take or layer' if delete else \
        'kept by no pin, take or layer; clean --delete removes them'
    return '\n'.join([f'  {head}'] + [f'    {p.relative_to(target)}' for p in found])
