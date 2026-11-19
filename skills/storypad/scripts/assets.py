"""Assets and locations in prep: the `@name` records a world keeps in world.md, which its stories' prep,
scenes, takes, pins and layers wait on or use, each with its expectation and state; a location's variations,
each started by a moment of the world; which variation each shot uses; and the views, tasks and checks they
raise. An older story kept its own in index.md, an older series in its Recurring Elements table.
"""

import os
import re
import textwrap

import timeline
from continuity import falls, find_moment, moments_of, place, reached, slots
from storyfile import TimelineError, cell, meta_pairs, same, table, table_text

ASSETS = ('Asset', 'State', 'Expect', 'File', 'Note')
LOCATIONS = ('Location', 'Of', 'From', 'State', 'Expect', 'Look', 'File', 'Note')
RECURRING = ('Element', 'Type', 'Description', 'Of', 'From', 'State', 'Expect', 'Look', 'File')
STATES = ('needed', 'made', 'approved')
MENTION = re.compile(r'@([a-z0-9][a-z0-9-]*(?:/[a-z0-9][a-z0-9-]*)?)')
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+){0,2}$')
EXPECT_ROOM, WIDTH = 48, 98


def parse_records(body):
    """The Assets and Locations tables of world.md, or of an older story's index.md, each record as {'name',
    'kind', 'of', …}."""
    ahead, arows = table(body.get('assets'), ASSETS)
    lhead, lrows = table(body.get('locations'), LOCATIONS)
    recs = [{**r, 'name': r['asset'], 'kind': 'asset', 'of': '', 'from': '', 'look': ''} for r in arows if r['asset']]
    recs += [{**r, 'name': r['location'], 'kind': 'variation' if r['of'] else 'location'} for r in lrows if r['location']]
    return {'assets_head': ahead, 'locations_head': lhead, 'records': recs}


def parse_recurring(lines):
    """An older series' Recurring Elements: header and records; a row whose Type is not location or variation is
    an asset."""
    head, rows = table(lines, RECURRING)
    recs = [{**r, 'name': r['element'], 'kind': r['type'] if r['type'] in ('location', 'variation') else 'asset',
             'note': r.get('note', '')} for r in rows if r['element']]
    return head, recs


def key(r):
    return f"{r['of']}/{r['name']}" if r['kind'] == 'variation' else r['name']


def records(doc):
    """The records a world keeps; on a story or series, its world's."""
    return doc['records'] if 'records' in doc else (doc.get('world') or {}).get('records', [])


def records_text(world):
    """world.md's Assets and Locations bodies; None for a table with nothing in it."""
    assets = [{k: v for k, v in r.items() if k not in ('name', 'kind', 'of', 'from', 'look')} | {'asset': r['name']}
              for r in world['records'] if r['kind'] == 'asset']
    places = [{k: v for k, v in r.items() if k not in ('name', 'kind')} | {'location': r['name']}
              for r in world['records'] if r['kind'] != 'asset']
    return (table_text(world['assets_head'], assets, ASSETS) if assets else None,
            table_text(world['locations_head'], places, LOCATIONS) if places else None)


def find(story, ref):
    """A record of the world by `@name` or `location/variation`."""
    text = ref.strip().lstrip('@')
    hits = [r for r in records(story) if same(key(r), text) or (r['kind'] != 'variation' and same(r['name'], text))]
    if not hits:
        raise TimelineError(f'no asset or location {text}')
    return hits[0]


def mentions(text):
    return MENTION.findall(text or '')


def scene_places(scene):
    return mentions(scene['meta'].get('location', ''))


def shot_places(scene, shot):
    return mentions(shot['row'].get('location', '')) or scene_places(scene)


def variations(story, loc):
    return [r for r in records(story) if r['kind'] == 'variation' and same(r['of'], loc['name'])]


def starts(story, var):
    """Where a variation starts, as a slot index, or None when its From names no moment: on a world or series, -1;
    in the story its moment falls in, at that scene or shot (the start when it names none); in a story whose
    when is that moment or later, at the start; else past the end."""
    try:
        m = find_moment(moments_of(story), var['from'])
    except TimelineError:
        return None
    if 'scenes' not in story:
        return -1
    if same(m['story'], story.get('key')):
        p = place(story.get('scenes', []), m['at'])
        return p[0] if p else -1
    return -1 if reached(story, m) else len(slots(story.get('scenes', [])))


def shots_using(story):
    """{record key: [slot]} for each location and variation, from the scenes' location fields and the
    events: a location holds until the slot of a variation's From event, then that variation."""
    order, out = slots(story.get('scenes', [])), {}
    for s in story.get('scenes', []):
        for x in s['shots'] or [None]:
            tag = x['id'] if x else str(s['num'])
            for loc_name in (shot_places(s, x) if x else scene_places(s)):
                loc = next((r for r in records(story) if r['kind'] == 'location' and same(r['name'], loc_name)), None)
                if loc is None:
                    continue
                i, held = order.index(tag), loc
                for v in variations(story, loc):
                    at = starts(story, v)
                    if at is not None and at <= i and (held is loc or at >= starts(story, held)):
                        held = v
                out.setdefault(key(held), []).append(tag)
    return out


def prep_lines(story, rec):
    """Each prep line naming the record, as (scene, item)."""
    return [(s, p) for s in story.get('scenes', []) for p in s['prep'] if any(same(m, key(rec)) for m in mentions(p['text']))]


def users(story, rec):
    """Every take, pin and layer pointing at the record, by its tag."""
    at = f'@{key(rec)}'
    out = [f"take {t['id']}" for s in story.get('scenes', []) for t in s['takes'] if same(t['file'], at)]
    out += [f"pin {p['name']}" for p in story.get('pins', []) if same(p['ref'], at) or same(p['from'] or '', at)]
    return out + [f"layer {l['name']} in {s['num']}" for s in story.get('scenes', []) for l in s['layers'] if same(l['file'], at)]


def file_of(story, ref):
    """The file a `@name` ref keeps, as a path from the story (the world keeps it from its own folder); '' when it
    has none, None when it names nothing."""
    try:
        r = find(story, ref)
    except TimelineError:
        return None
    return from_world(story, r['file'])


def from_world(story, file):
    """A file the world keeps, as a path from the story; a link, an absolute path or `@name` as it is."""
    home = story.get('world')
    if not home or not file or timeline.as_given(file):
        return file
    return os.path.relpath(home['path'].resolve() / file, story['path'].resolve())


def slots_of(story, ref):
    """The scene numbers and shot ids of the story using the record `ref`: the shots set at it or with a take
    pointing at it, and each scene whose prep names it, with its shots."""
    rec = find(story, ref)
    at = key(rec)
    out = set(shots_using(story).get(at, []))
    out |= {t['shot'] for s in story['scenes'] for t in s['takes'] if same(t['file'], f'@{at}')}
    return out | {tag for s, _ in prep_lines(story, rec) for tag in [str(s['num'])] + [x['id'] for x in s['shots']]}


def mark_uses(story):
    """Give each shot what its prompt draws on from the records (the files of the records its takes point
    at, and the variation it is set in), and each pin keeping a record the record's file."""
    using = shots_using(story)
    by_slot = {tag: k for k, tags in using.items() if '/' in k for tag in tags}
    for s in story.get('scenes', []):
        for x in s['shots']:
            files = sorted(f"{t['file']}={file_of(story, t['file'])}" for t in s['takes']
                           if t['shot'] == x['id'] and t['file'].startswith('@'))
            x['uses'] = ' '.join(files + ([by_slot[x['id']]] if x['id'] in by_slot else []))
    for p in story['pins'] + story.get('world_pins', []):
        if p['ref'].startswith('@'):
            p['kept'] = file_of(story, p['ref']) or p['ref']


def edit_record(world, docs, a, kind, keep):
    """asset or location add|set|remove on the world's records; `docs` is every story, series and episode of the
    world, each as (doc, how a line about it starts). Returns the record's key, its state before, the docs
    changed with it, to be written, and the names of the world's pins removed with it; the world's own pins follow
    too. A forced remove takes each pin starting from the record with it, never leaving one wider. `keep(label)`
    keeps --file in the world's assets/ and gives its path."""
    recs = world['records']
    of = getattr(a, 'of', None)
    hit = [r for r in recs if (r['kind'] == 'asset') == (kind == 'asset') and same(r['name'], a.name)
           and (a.op != 'add' or kind == 'asset' or same(r['of'], of or ''))]
    if a.op == 'add':
        if not NAME.match(a.name):
            raise TimelineError(f'{a.name!r}: a name is lowercase, one to three words joined by -')
        if hit or (not of and any(r['kind'] != 'variation' and same(r['name'], a.name) for r in recs)):
            raise TimelineError(f'there is already a record {a.name}')
        if not (a.expect or '').strip():
            raise TimelineError(f'{a.name} needs its expectation: what it must be, in your words; give --expect')
        if kind == 'location' and bool(of) != bool(a.start):
            raise TimelineError('a variation names its location with --of and the moment that starts it with --from')
        rec = {'name': a.name, 'kind': 'variation' if of else kind, 'of': '', 'from': '', 'state': 'needed',
               'expect': '', 'look': '', 'file': '', 'note': ''}
        if of:
            base = find(world, of)
            if base['kind'] != 'location':
                raise TimelineError(f'{of} is not a location')
            rec['of'] = base['name']
        recs.append(rec)
    elif len(hit) > 1:
        raise TimelineError(f"{a.name} fits {', '.join(key(r) for r in hit)}; name it as location/variation")
    elif not hit:
        try:
            rec = find(world, a.name)
        except TimelineError:
            raise TimelineError(f'no {kind} {a.name}')
    else:
        rec = hit[0]
    was = rec['state']
    if a.op == 'remove':
        kids = [v['name'] for v in variations(world, rec)] if rec['kind'] == 'location' else []
        if kids:
            raise TimelineError(f"{rec['name']} has the variations {', '.join(kids)}; remove those first")
        named = [at + u for d, at in [(world, 'the world: ')] + docs for u in uses_of(d, rec)]
        gone = [p for p in world['pins'] if same(p['from'] or '', f'@{key(rec)}')]
        if named and not a.force:
            also = f" and remove the pins {', '.join(p['name'] for p in gone)} starting from it" if gone else ''
            raise TimelineError(f"{key(rec)} is named by {'; '.join(named)}; add --force to strip the @{key(rec)}"
                                + also)
        world['pins'] = [p for p in world['pins'] if p not in gone]
        rewrite(world, f'@{key(rec)}', '')
        touched = [d for d, _ in docs if rewrite(d, f'@{key(rec)}', '')]
        recs.remove(rec)
        return key(rec), was, touched, [p['name'] for p in gone]
    if getattr(a, 'start', None):
        rec['from'] = find_moment(world['moments'], a.start)['moment']
    if a.expect is not None:
        if not a.expect.strip():
            raise TimelineError('an expectation is never empty')
        if rec['expect'] and rec['expect'] != cell(a.expect) and rec['state'] == 'approved':
            rec['state'] = 'made'
        rec['expect'] = cell(a.expect)
    for k in ('look', 'note'):
        if getattr(a, k, None) is not None:
            rec[k] = cell(getattr(a, k))
    if a.file:
        rec['file'] = keep(key(rec).replace('/', '-'))
        if rec['state'] == 'needed' and not a.state:
            rec['state'] = 'made'
    if a.state:
        rec['state'] = a.state
    touched = []
    if a.op == 'set' and a.rename:
        new = a.rename if not rec['of'] else f"{rec['of']}/{a.rename}"
        if not NAME.match(a.rename):
            raise TimelineError(f'{a.rename!r}: a name is lowercase, one to three words joined by -')
        if any(r is not rec and same(key(r), new) for r in recs):
            raise TimelineError(f'there is already a record {new}')
        kids = variations(world, rec) if rec['kind'] == 'location' else []
        moves = [(f'@{key(rec)}', f'@{new}')] + [(f'@{key(v)}', f"@{a.rename}/{v['name']}") for v in kids]
        touched = [d for d, _ in docs if any([rewrite(d, old, to) for old, to in moves])]
        for old, to in moves:
            rewrite(world, old, to)
        for v in kids:
            v['of'] = a.rename
        rec['name'] = a.rename
    rec.update(meta_pairs(getattr(a, 'meta', None), [c.lower() for c in LOCATIONS]))
    return key(rec), was, touched, []


def uses_of(story, rec):
    """Everything in a story or series naming the record: prep lines, scene locations, takes, pins and layers."""
    at = key(rec)
    out = [f"prep in {s['num']} {s['name']}" for s, _ in prep_lines(story, rec)]
    out += [f"{s['num']} {s['name']}'s location" for s in story.get('scenes', []) if any(same(m, at) for m in scene_places(s))]
    out += [f"shot {x['id']}'s location" for s in story.get('scenes', []) for x in s['shots']
            if any(same(m, at) for m in mentions(x['row'].get('location', '')))]
    return out + users(story, rec)


def used(story):
    """The world's records a story uses: named in it or set at by its shots; a location also when one of its
    variations is."""
    using = shots_using(story)
    return [r for r in records(story) if uses(story, r, using)
            or (r['kind'] == 'location' and any(uses(story, v, using) for v in variations(story, r)))]


def uses(story, rec, using):
    """Whether the story names the record or has a shot set at it (`using`, its shots_using)."""
    return bool(uses_of(story, rec) or using.get(key(rec)))


def stories_using(docs, rec):
    """The keys of the stories and series of `docs` that use the record."""
    return [d['key'] for d, _ in docs if uses(d, rec, shots_using(d))]


def none_yet(story, docs, kind):
    """A records view with no rows: none in the world, or none the story uses."""
    if docs is not None or not any((r['kind'] == 'asset') == (kind == 'asset') for r in records(story)):
        return f'  no {kind}s yet; {kind} add <story> <name> --expect E adds one'
    return f"  {story['title']} uses no {kind} yet; show <world> --view {kind}s lists the world's"


def rewrite(story, old, new):
    """Every `old` mention in the scene files, takes, pins and layers made `new` ('' strips it); whether any was."""
    pat = re.compile(re.escape(old) + r'(?![a-z0-9/-])')
    sub = (lambda t: re.sub(r'[ \t]*' + pat.pattern, '', t)) if not new else (lambda t: pat.sub(new, t))
    changed = False
    for s in story.get('scenes', []):
        held = lambda: (s['text'], [x['row'].get('location') for x in s['shots']], [t['file'] for t in s['takes']],
                        [l['file'] for l in s['layers']])
        was = held()
        s['text'] = sub(s['text'])
        for x in s['shots']:
            if x['row'].get('location'):
                x['row']['location'] = sub(x['row']['location']).strip(', ')
        for t in s['takes']:
            t['file'] = sub(t['file'])
        for l in s['layers']:
            l['file'] = sub(l['file'])
        if held() != was:
            s['dirty'] = changed = True
    for p in story.get('pins', []):
        was = (p['ref'], p['from'], p['to'])
        p['ref'], p['from'] = sub(p['ref']), p['from'] and sub(p['from'])
        p['to'] = p['from'] if p['from'] and p['from'].startswith('@') else p['to'] and sub(p['to'])
        changed = changed or (p['ref'], p['from'], p['to']) != was
    return changed


def strip_at(text):
    return re.sub(r'\s*' + MENTION.pattern, '', text).strip()


def preview(text, room=EXPECT_ROOM):
    if len(text) <= room:
        return text
    words = text[:room].split(' ')[:-1]
    return ' '.join(words).rstrip(',;:') + '…'


def counts(recs):
    open_ = [r for r in recs if r['state'] != 'approved']
    return (f"{len(open_)} open: {sum(r['state'] == 'needed' for r in recs)} needed, "
            f"{sum(r['state'] == 'made' for r in recs)} made")


def scene_of_slot(story, tag):
    return next(s for s in story.get('scenes', []) if tag in ([x['id'] for x in s['shots']] or [str(s['num'])]))


def listing_view(title, head, rows):
    """A records view: its title line, the column heads, a rule as wide as the widest line, the rows."""
    return '\n'.join([title, '', head, '  ' + '─' * (max(map(len, [head] + rows)) - 2)] + rows)


def show_assets(story, docs=None):
    """The assets view: on a story the assets it uses, with the scenes whose prep names each and what points at
    it; on a world (`docs`, its stories as (doc, tag)) every asset, with the stories using it."""
    recs = [r for r in (records(story) if docs is not None else used(story)) if r['kind'] == 'asset']
    if not recs:
        return none_yet(story, docs, 'asset')
    w = max(len(r['name']) for r in recs) + 3
    if docs is not None:
        cols = {key(r): ', '.join(stories_using(docs, r)) or '—' for r in recs}
        sw = max(len(c) for c in [*cols.values(), 'Stories']) + 2
        head = f"  {'Asset':<{w}}{'State':<9}{'Stories':<{sw}}Expect"
        out = [f"  {r['name']:<{w}}{r['state']:<9}{cols[key(r)]:<{sw}}{preview(r['expect'])}" for r in recs]
        return listing_view(f"  {story['title']}  ·  assets  ·  {counts(recs)}", head, out)
    head = f"  {'Asset':<{w}}{'State':<9}{'Prep in':<10}{'Used by':<10}Expect"
    out = []
    for r in recs:
        prep = ', '.join(dict.fromkeys(str(s['num']) for s, _ in prep_lines(story, r))) or '—'
        users_ = ', '.join(u.split()[1] for u in users(story, r)) or '—'
        out.append(f"  {r['name']:<{w}}{r['state']:<9}{prep:<10}{users_:<10}{preview(r['expect'])}")
    return listing_view(f"  {story['title']}  ·  assets  ·  {counts(recs)}", head, out)


def where(story, rec):
    """A variation's start, as `<moment> (<shot>)`, on a world or series `<moment> (<where it falls>)`, or the
    start."""
    at = starts(story, rec) if rec['kind'] == 'variation' else None
    if rec['kind'] != 'variation':
        return 'the start'
    if 'scenes' not in story and at is not None:
        return f"{rec['from']} ({falls(find_moment(moments_of(story), rec['from']))})"
    order = slots(story.get('scenes', []))
    shot = 'not placed' if at is None else 'before' if at < 0 else order[at] if at < len(order) else 'after'
    return f"{rec['from']} ({shot})"


def show_locations(story, docs=None):
    """The locations view: on a story the locations and variations it uses, with the shots set at each; on a
    world (`docs`, its stories as (doc, tag)) every one, with the stories using it."""
    recs = records(story) if docs is not None else used(story)
    locs = [r for r in recs if r['kind'] == 'location']
    rows = [x for loc in locs for x in [(loc, 0)] + [(v, 2) for v in variations(story, loc) if any(v is r for r in recs)]]
    if not rows:
        return none_yet(story, docs, 'location')
    if docs is not None:
        col, tags = 'Stories', {key(r): ', '.join(stories_using(docs, r)) for r, _ in rows}
        sw = max(len(t) for t in [*tags.values(), col]) + 2
    else:
        using = shots_using(story)
        shots = any(s['shots'] for s in story.get('scenes', []))
        col, tags = 'Shots' if shots else 'Scenes', {key(r): ' '.join(using.get(key(r), [])) for r, _ in rows}
        sw = max([len(t) for t in tags.values()] + [6 if not shots else 5]) + 2 if shots else 9
    nw = max(len(r['name']) + i for r, i in rows) + 5
    fw = max(len(where(story, r)) for r, _ in rows) + 4
    head = f"  {'Location':<{nw}}{'State':<9}{'From':<{fw}}{col:<{sw}}Look, or what differs"
    out = [f"  {' ' * i + r['name']:<{nw}}{r['state']:<9}{where(story, r):<{fw}}{tags[key(r)]:<{sw}}{r['look']}"
           for r, i in rows]
    return listing_view(f"  {story['title']}  ·  locations  ·  {counts([r for r, _ in rows])}", head, out)


def wrapped(head, text, indent):
    lines = textwrap.wrap(text, WIDTH - indent) or ['']
    return [f"  {head:<{indent - 2}}{lines[0]}"] + [' ' * indent + line for line in lines[1:]]


def shots_at(docs, rec):
    """The shots set at the record in each of `docs` as (id, name), the id as `<tag><id>`."""
    out = []
    for d, at in docs:
        names = {x['id']: x['name'] for s in d.get('scenes', []) for x in s['shots']}
        out += [(at + t, names.get(t, '')) for t in shots_using(d).get(key(rec), [])]
    return out


def detail_record(world, docs, ref):
    """A record of the world: its expectation, look, shots, variations, prep, pins and users, from every story
    of `docs` using it."""
    r = find(world, ref)
    out = [f"  @{key(r)}  ·  {r['kind']}  ·  {r['state']}"] + wrapped('expect', r['expect'], 14)
    if r['kind'] != 'asset':
        out += wrapped('look', r['look'] or 'none yet', 14)
        out += wrapped('shots', ' · '.join(f'{t} {n}'.strip() for t, n in shots_at(docs, r)) or 'none', 14)
    if r['kind'] == 'location':
        vs = [f"{v['name']} from {where(world, v)} · {', '.join(t for t, _ in shots_at(docs, v)) or 'no shots'} · "
              f"{v['state']}" for v in variations(world, r)]
        out += [f"  {'variations' if i == 0 else '':<12}{line}" for i, line in enumerate(vs)]
    preps = [f"{at}{s['num']} {s['name']}: {strip_at(p['text'])}" for d, at in docs for s, p in prep_lines(d, r)]
    out += [f"  {'prep' if i == 0 else '':<12}{line}" for i, line in enumerate(preps or ['none'])]
    used = [(at, u) for d, at in [(world, '')] + docs for u in users(d, r)]
    out += [f"  {'pins':<12}{', '.join(at + u[4:] for at, u in used if u.startswith('pin ')) or 'none yet'}"]
    takes = [at + u for at, u in used if not u.startswith('pin ')]
    out += [f"  {'used by':<12}{', '.join(takes)}"] if takes else []
    return '\n'.join(out + [f"  {'file':<12}{r['file'] or 'none yet'}"])


def made_reply(world, docs, ref, was):
    """After a record changes state: the change, its expectation, and the prep boxes the owner can tick in the
    stories of `docs`."""
    r = find(world, ref)
    out = [f"  @{key(r)}  {was} → {r['state']}" + (f"  ·  {r['file']}" if r['file'] else '')
           if was != r['state'] else f"  @{key(r)}  {r['state']}" + (f"  ·  {r['file']}" if r['file'] else '')]
    out += wrapped('expect', r['expect'], 11)
    if r['state'] == 'made':
        out.append('  open until approved against that')
    boxes = [(f"{at}{s['num']} {s['name']}", p) for d, at in docs for s, p in prep_lines(d, r) if not p['done']]
    if r['state'] in ('made', 'approved') and boxes:
        w = max(len(scene) for scene, _ in boxes) + 3
        out.append('  prep you can tick once it holds:' if r['state'] == 'made' else '  prep you can tick now:')
        out += [f"    {scene:<{w}}{strip_at(p['text'])}" for scene, p in boxes]
    return '\n'.join(out)


def kind_of(r):
    """The todo --only kind a record's tasks fall under."""
    return 'assets' if r['kind'] == 'asset' else 'locations'


def task(r):
    word = {'needed': 'needed', 'made': 'made, not yet approved'}[r['state']]
    return kind_of(r), f"{r['kind']} {key(r)}: {word}"


def used_in(story, scene):
    """The records a scene uses: those its prep names, then the locations and variations its shots are set in."""
    using = shots_using(story)
    mine = {x['id'] for x in scene['shots']} | {str(scene['num'])}
    keys = [m for p in scene['prep'] for m in mentions(p['text'])]
    keys += [k for k, tags in using.items() if mine & set(tags)]
    out = []
    for k in dict.fromkeys(keys):
        try:
            out.append(find(story, k))
        except TimelineError:
            pass
    return out


def record_tasks(story, scene=None):
    """Each open record, as (its --only kind, the task): those `scene` uses, else those the story uses; on a world,
    each of its own."""
    recs = used_in(story, scene) if scene else used(story) if 'scenes' in story else records(story)
    return [task(r) for r in recs if r.get('state') in ('needed', 'made')]


def record_problems(story):
    """What check names in a story's use of the records, as (its --only kind, the problem)."""
    out = []
    for s in story.get('scenes', []):
        for p in s['prep']:
            for m in mentions(p['text']):
                if file_of(story, m) is None:
                    out.append(('locations', f"prep in {s['num']} {s['name']} names @{m}; there is no asset or "
                                             f'location {m}'))
        for m in scene_places(s) + [m for x in s['shots'] for m in mentions(x['row'].get('location', ''))]:
            if not any(r['kind'] == 'location' and same(r['name'], m) for r in records(story)):
                out.append(('locations', f"scene {s['num']} {s['name']} is set at @{m}; there is no location {m}"))
        for t in s['takes']:
            if t['file'].startswith('@') and not file_of(story, t['file']):
                out.append(('assets', f"take {t['id']} points at {t['file']}, which has no file"))
    return out


def world_problems(world, docs):
    """What check names in the world's records, read through every story of `docs`, as (its --only kind, the
    problem)."""
    out = []
    for r in records(world):
        if not r['state']:
            continue
        problem = None
        if r['kind'] == 'variation':
            if starts(world, r) is None:
                problem = f"variation {key(r)} starts from {r['from']}; there is no such moment"
            elif not shots_at(docs, r):
                problem = f"variation {key(r)}: no story has a shot set at {r['of']} from {r['from']} on"
        elif r['kind'] == 'asset' and not users(world, r) and not any(prep_lines(d, r) or users(d, r) for d, _ in docs):
            problem = f"asset {r['name']}: no prep line, take, pin or layer names it"
        elif r['kind'] == 'location' and not any(prep_lines(d, r) for d, _ in docs):
            problem = f"location {r['name']}: no prep line names it"
        out += [(kind_of(r), problem)] if problem else []
    return out
