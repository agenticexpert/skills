"""Continuity: the threads and events of a world, kept in world.md (where each thread is seen and heard in each
story, and each event's story and place), read by each story for its own key, edited by command from a story, series
or world, drawn as the thread graph, the small view, the events grid and the list form of a story, a series or the
world, and their tasks and problems; an older series' Continuity Threads read for migrate.
"""

import re
import textwrap

from storyfile import TimelineError, cell, meta_pairs, name, same, table, table_text

THREADS = ('Thread', 'Status', 'Introduced', 'Last Referenced', 'Episodes')
THREAD_ICON = {'active': '●', 'resolved': '✓', 'dormant': '○', 'recurring': '↻'}


def parse_threads(lines):
    """The Continuity Threads table's header and threads."""
    head, threads = table(lines, THREADS)
    return head, [t for t in threads if t['thread']]


def threads_table(head, threads):
    return table_text(head, threads, THREADS)


def thread_end(threads):
    """A pin end of the world: one of its threads by name, or None for every story."""
    def end(text):
        text = (text or '').strip()
        if not text:
            return None
        hit = next((t for t in threads if same(t, text)), None)
        if hit is None:
            raise TimelineError(f"no thread {text}; the threads are {', '.join(threads) or 'none yet'}")
        return hit
    return end


def episode_tag(story):
    """How a line about an episode of a series starts: `ep N: `."""
    return f"ep {story['num']}: "


def episodes_of(thread):
    return [int(n) for n in re.findall(r'\d+', thread['episodes'])]


def places(text):
    """An On screen or Heard cell, `film: 1a-1b; saga/ep-first`, as {story key: its shots and scenes}; a key alone
    marks a story the thread runs through, its places not given yet."""
    out = {}
    for part in filter(None, (p.strip() for p in (text or '').split(';'))):
        key, _, at = part.partition(':')
        out[key.strip()] = at.strip()
    return out


def places_text(found):
    return '; '.join(f'{k}: {v}' if v else k for k, v in found.items())


def marked_in(world, thread):
    """The keys of the stories `thread` has a mark in: an event there, or a place in its On screen or Heard."""
    t = next((x for x in (world or {}).get('threads', []) if same(x['thread'], thread)), None)
    keys = {e['story'] for e in (world or {}).get('events', []) if e['story'] and same(e['thread'], thread)}
    return keys | (set(places(t['on screen'])) | set(places(t['heard'])) if t else set())


def renumber_threads(threads, to):
    """Map each thread's episode numbers through `to` (old → new). An Introduced or Last Referenced
    that named the thread's first or last episode names its new first or last; any other number in
    them is mapped."""
    moved = {k: v for k, v in to.items() if k != v}
    for t in threads if moved else []:
        nums = episodes_of(t)
        new = sorted(to.get(n, n) for n in nums)
        if any(n in moved for n in nums):
            t['episodes'] = ', '.join(map(str, new))
        for key, end in (('introduced', 0), ('last referenced', -1)):
            if nums and [int(n) for n in re.findall(r'\d+', t[key])] == [sorted(nums)[end]]:
                t[key] = re.sub(r'\d+', str(new[end]), t[key])
            else:
                t[key] = re.sub(r'\d+', lambda m: str(moved.get(int(m.group()), m.group())), t[key])


STORY_THREADS = ('Thread', 'Status', 'On screen', 'Heard')
EVENTS = ('Thread', 'Story', 'At', 'Kind', 'Event', 'Seen', 'Links')
KINDS = ('set up', 'beat', 'change', 'pays off')
SEEN = {'on': '●', 'heard': '○', 'off': '◆'}
CARRIED = '┄'
LEGEND = '  ● seen   ○ heard only   ◆ happens unseen   ┄ carried'
STOP = {'a', 'an', 'the', 'of', 'on', 'to', 'in'}
LABEL, NARROW = 14, 8
LINK = re.compile(r'^\s*(.+?)\s*→\s*(.+?):\s*(.+?)\s*$')


def slots(scenes):
    """Every place in story order: each shot id, or the number of a scene with no shots."""
    return [tag for s in scenes for tag in ([x['id'] for x in s['shots']] or [str(s['num'])])]


def place(scenes, at):
    """Where `at` sits among the slots, as (first, last) index: before is -1, after is past the end; None when
    it names nothing."""
    at, order = (at or '').strip(), slots(scenes)
    if at == 'before':
        return -1, -1
    if at == 'after':
        return len(order), len(order)
    if at in order:
        return order.index(at), order.index(at)
    hit = next((s for s in scenes if at == str(s['num']) or (at and same(s['name'], at))), None)
    if hit is None:
        return None
    mine = [x['id'] for x in hit['shots']] or [str(hit['num'])]
    return order.index(mine[0]), order.index(mine[-1])


def expand(text, scenes):
    """`1a-1b, 3c-4c, 5` → (the slots it names in story order, the parts that name nothing)."""
    order, got, bad = slots(scenes), set(), []
    for part in filter(None, (p.strip() for p in (text or '').split(','))):
        a, dash, b = part.partition('-')
        ends = [place(scenes, a), place(scenes, b)] if dash else [place(scenes, part)] * 2
        if None in ends or min(ends)[0] < 0 or max(ends)[1] >= len(order):
            bad.append(part)
            continue
        got |= set(order[min(e[0] for e in ends):max(e[1] for e in ends) + 1])
    return [x for x in order if x in got], bad


def runs(tags, scenes):
    """Slots written back as runs: `1a-1b, 4c`."""
    order, out = slots(scenes), []
    for i in sorted(order.index(t) for t in tags if t in order):
        if out and out[-1][1] == i - 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return ', '.join(order[a] if a == b else f'{order[a]}-{order[b]}' for a, b in out)


def links_of(event):
    """An event's outgoing links: (effect, thread, event)."""
    return [m.groups() for m in (LINK.match(p) for p in event['links'].split(';')) if m]


def links_text(links):
    return '; '.join(f'{w} → {t}: {e}' for w, t, e in links)


def label(e):
    return f"{e['thread']}: {e['event']}"


def parse_world(body):
    """world.md's Threads and Events tables: header and rows."""
    head, rows = table(body.get('threads'), STORY_THREADS)
    ehead, events = table(body.get('events'), EVENTS)
    return {'threads_head': head, 'threads': [t for t in rows if t['thread']], 'events_head': ehead,
            'events': [e for e in events if e['thread'] or e['event']]}


def story_threads(story):
    """The world's threads as `story` sees them, each with what its On screen and Heard give for the story's key and
    the slots they name, and the world's events set in the story: the world's own rows, so a change to an event is a
    change to world.md."""
    world, key, scenes = story['world'] or {'threads': [], 'events': []}, story['key'], story['scenes']
    threads = []
    for t in world['threads']:
        mine = {k: places(t[k]).get(key) for k in ('on screen', 'heard')}
        threads.append({**t, 'row': t, 'runs': key in marked_in(world, t['thread']),
                        'on screen': mine['on screen'] or '', 'heard': mine['heard'] or '',
                        'on': expand(mine['on screen'], scenes)[0], 'hear': expand(mine['heard'], scenes)[0]})
    return {'threads': threads, 'events': [e for e in world['events'] if e['story'] == key]}


def settle(story):
    """Each thread's On screen and Heard in world.md, for the story's key, as its shots and scenes now hold them: a
    place moved follows and one removed is dropped; a key left with none is dropped, a key alone kept."""
    for t in story.get('threads', []):
        for k, short in (('on screen', 'on'), ('heard', 'hear')):
            if expand(t[k], story['scenes'])[0] != t[short]:
                found, text = places(t['row'][k]), runs(t[short], story['scenes'])
                found[story['key']] = text
                t['row'][k], t[k] = places_text({x: v for x, v in found.items() if v or x != story['key']}), text


def story_thread(story, text):
    """The story's own thread named `text`, or None."""
    return next((t for t in story.get('threads', []) if text and same(t['thread'], text)), None)


def moments_of(doc):
    """The moments of the world a story or series sits in, or of a world, in timeline order."""
    return [m for m in (doc.get('world') or doc).get('moments', []) if m['moment']]


def find_moment(moments, ref):
    """A moment of a world's timeline by its name."""
    named = [m for m in moments if m['moment']]
    hit = next((m for m in named if same(m['moment'], ref)), None)
    if hit is None:
        raise TimelineError(f"no moment {(ref or '').strip()!r}; the moments are "
                            f"{', '.join(m['moment'] for m in named) or 'none yet'}")
    return hit


def moments_here(story):
    """The moments of the world that fall in `story`."""
    return [m for m in moments_of(story) if m['story'] and same(m['story'], story.get('key'))]


def reached(story, moment):
    """Whether the story is set at `moment` or later: its when names that moment or one after it."""
    ms = moments_of(story)
    when = next((i for i, m in enumerate(ms) if same(m['moment'], story.get('when'))), None)
    return when is not None and when >= next(i for i, m in enumerate(ms) if m is moment)


def falls(moment):
    """Where a moment falls: `<story> <scene or shot>`, or between stories."""
    return f"{moment['story']} {moment['at']}".strip() or 'between stories'


def moment_problems(story):
    """A when naming no moment, and a moment falling in the story at no scene or shot."""
    out = []
    if story.get('when') and not any(same(m['moment'], story['when']) for m in moments_of(story)):
        out.append(f"when names {story['when']}; there is no such moment")
    return out + [f"moment {m['moment']} falls at {m['at']}; there is no such scene or shot in the story"
                  for m in moments_here(story) if m['at'] and place(story['scenes'], m['at']) is None]


def follow(story, new):
    """Every At, On screen and Heard, and the At of each moment falling in the story, follows the ids `new`
    gives."""
    for t in story.get('threads', []) if 'events' in story else []:
        t['on'], t['hear'] = [new(x) for x in t['on']], [new(x) for x in t['hear']]
    for e in story.get('events', []) + moments_here(story):
        e['at'] = new(e['at'])


def stranded(story, tags):
    """The events and moments at any of `tags` (scene numbers and shot ids), as `the event <thread>: <event>` and
    `the moment <name>`."""
    return [f'the event {label(e)}' for e in story.get('events', []) if e['at'].strip() in tags] + \
        [f"the moment {m['moment']}" for m in moments_here(story) if m['at'].strip() in tags]


def strand(story, tags):
    """Drop the At of each event and moment at any of `tags`, and the tags from On screen and Heard."""
    for e in story.get('events', []) + moments_here(story):
        if e['at'].strip() in tags:
            e['at'] = ''
    for t in story.get('threads', []) if 'events' in story else []:
        t['on'], t['hear'] = [x for x in t['on'] if x not in tags], [x for x in t['hear'] if x not in tags]


def ordered(story):
    """Each thread with its events in story order: [(thread name, [event])], a thread its events name that
    is no thread included."""
    names = [t['thread'] for t in story.get('threads', [])]
    scenes = story.get('scenes', [])
    by = {n.casefold(): [] for n in names}
    for e in story.get('events', []):
        by.setdefault(e['thread'].casefold(), []).append(e)
    key = lambda e: (place(scenes, e['at']) or (len(slots(scenes)) + 1,))[0]
    return [(n, sorted(by[n.casefold()], key=key)) for n in names] + \
        [(evs[0]['thread'], sorted(evs, key=key)) for k, evs in by.items() if k not in {n.casefold() for n in names}]


def kind(events, e):
    return e['kind'] or ('set up' if e is events[0] else 'beat')


def seen(e):
    return e['seen'] or 'on'


def paid(events):
    """Whether a thread's events pay it off: a pays off event, or a last event linking out with pays off."""
    return any(kind(events, e) == 'pays off' for e in events) or \
        bool(events and any(w == 'pays off' for w, _, _ in links_of(events[-1])))


def hanging(thread, events):
    return thread.get('status', 'active') in ('active', '') and not paid(events)


def of_thread(events, thread):
    return [e for e in events if same(e['thread'], thread)]


def threads_text(world):
    """world.md's Threads and Events bodies: events in thread order; a thread its events in the world pay off is
    resolved. None for a table with nothing in it."""
    for t in world['threads']:
        if t['status'] not in ('dormant', 'recurring') and paid(of_thread(world['events'], t['thread'])):
            t['status'] = 'resolved'
    order = {t['thread'].casefold(): i for i, t in enumerate(world['threads'])}
    events = sorted(world['events'], key=lambda e: order.get(e['thread'].casefold(), len(order)))
    return (table_text(world['threads_head'], world['threads'], STORY_THREADS) if world['threads'] else None,
            table_text(world['events_head'], events, EVENTS) if events else None)


def find_thread(story, text):
    """A thread by name, else the one whose name holds the words; two that fit are refused."""
    names = [t['thread'] for t in story['threads']]
    hits = [n for n in names if same(n, text)] or [n for n in names if text.strip().casefold() in n.casefold()]
    if len(hits) > 1:
        raise TimelineError(f"{text!r} fits {' and '.join(hits)}; say which")
    if not hits:
        raise TimelineError(f"no thread {text!r}; the threads are {', '.join(names) or 'none yet'}")
    return hits[0]


def find_event(story, ref):
    """An event by `<thread>: <event>`."""
    thread, colon, event = ref.partition(':')
    if not colon:
        raise TimelineError(f'name an event as "<thread>: <event>", not {ref!r}')
    thread = find_thread(story, thread)
    hit = next((e for e in story['events'] if same(e['thread'], thread) and same(e['event'], event)), None)
    if hit is None:
        mine = [e['event'] for e in story['events'] if same(e['thread'], thread)]
        raise TimelineError(f"{thread} has no event {event.strip()!r}; its events are {', '.join(mine) or 'none yet'}")
    return hit


def at_ref(world, story, at):
    """An event's At: before, after, a scene or shot of `story`; with no story, before, after or a moment of the
    world."""
    at = name(at)
    if story is None:
        return at if at in ('before', 'after') else find_moment(moments_of(world), at)['moment']
    if place(story['scenes'], at) is None:
        raise TimelineError(f'no scene or shot {at} in the story; use before, after, a scene or a shot id')
    return at


def relabel(story, old, new):
    """Every link naming `old` (a thread, or a `thread: event`) names `new`."""
    def swap(t, e):
        if ':' in old:
            return new.split(': ', 1) if same(f'{t}: {e}', old) else (t, e)
        return (new if same(t, old) else t), e
    for e in story['events']:
        e['links'] = links_text([(w, *swap(t, x)) for w, t, x in links_of(e)])


def drop_thread(doc, thread):
    """Remove the events on `thread` from a story or series.md, and every link to it."""
    doc['events'] = [e for e in doc['events'] if not same(e['thread'], thread)]
    for x in doc['events']:
        x['links'] = links_text([l for l in links_of(x) if not same(l[1], thread)])


def edit_thread(world, here, a):
    """thread add|set|remove from a story, series or world (`here`, None for the world): the world's thread. --on and
    --heard set where it is seen and heard in the story `here`, --episodes the episodes of the series `here` it runs
    through. A rename reaches every event, link and pin of the world naming it."""
    threads = world['threads']
    found = [t for t in threads if same(t['thread'], a.name)]
    if a.op == 'add':
        if found:
            raise TimelineError(f"there is already a thread {found[0]['thread']!r}")
        mark = places_text({here['key']: ''}) if here is not None and 'episodes' not in here else ''
        found = [{'thread': name(a.name), 'status': 'active', 'on screen': mark, 'heard': ''}]
        threads.append(found[0])
    elif not found:
        raise TimelineError(f"no thread {a.name!r}; the threads are {', '.join(t['thread'] for t in threads) or 'none yet'}")
    t = found[0]
    mine = of_thread(world['events'], t['thread'])
    pinned = [p for p in world['pins'] if p['from'] and same(p['from'], t['thread'])]
    if a.op == 'remove':
        if pinned:
            raise TimelineError(f"{t['thread']} carries the pins {', '.join(p['name'] for p in pinned)}; "
                                'change or remove those first')
        if mine and not a.force:
            where = lambda e: e['event'] + (f" ({e['story']})" if e['story'] else '')
            raise TimelineError(f"{t['thread']} has the events {', '.join(map(where, mine))}; "
                                'add --force to remove it with them')
        threads.remove(t)
        drop_thread(world, t['thread'])
        return
    if a.rename and any(x is not t and same(x['thread'], a.rename) for x in threads):
        raise TimelineError(f'there is already a thread {a.rename!r}')
    for key, value in (('on screen', a.on), ('heard', a.heard)):
        if value is not None:
            if here is None or 'episodes' in here:
                raise TimelineError('--on and --heard are for a story; a series thread takes --episodes')
            bad = expand(value, here['scenes'])[1]
            if bad:
                raise TimelineError(f"no scene or shot {', '.join(bad)} in the story")
            t[key] = places_text({**places(t[key]), here['key']: name(value)})
    if a.episodes is not None:
        if here is None or 'episodes' not in here:
            raise TimelineError('--episodes is for a series; a story thread takes --on and --heard')
        nums = {int(n) for n in re.findall(r'\d+', a.episodes)}
        have = [ep['num'] for ep in here['episodes']]
        unknown = sorted(nums - set(have))
        if unknown:
            raise TimelineError(f"no episode {', '.join(map(str, unknown))}; the episodes are "
                                f"{', '.join(map(str, have)) or 'none yet'}")
        on = places(t['on screen'])
        for ep in here['episodes']:
            if ep['num'] in nums:
                on.setdefault(ep['key'], '')
            elif ep['key'] in on and not on[ep['key']]:
                del on[ep['key']]
        t['on screen'] = places_text(on)
    if a.status:
        t['status'] = a.status
    t.update(meta_pairs(getattr(a, 'meta', None), [c.lower() for c in STORY_THREADS]))
    if not a.rename:
        return
    old, t['thread'] = t['thread'], name(a.rename)
    for e in mine:
        e['thread'] = t['thread']
    relabel(world, old, t['thread'])
    for p in pinned:
        p['from'] = p['to'] = t['thread']


def edit_event(world, here, a):
    """event add|set|remove|link|unlink: the world's event, named `<thread>: <event>`, one name in the world. One
    added goes in the story `here`, or with none in the world itself at before, after or a moment; a place set is
    checked against the story it is in. Returns the thread to list."""
    events = world['events']
    if a.op == 'add':
        thread = find_thread(world, a.thread)
        if any(same(e['thread'], thread) and same(e['event'], a.event) for e in events):
            raise TimelineError(f'{thread} already has an event {a.event!r}')
        e = {'thread': thread, 'story': here['key'] if here else '', 'at': at_ref(world, here, a.at), 'kind': '',
             'event': name(a.event), 'seen': '', 'links': '', 'note': cell(a.note)}
        events.append(e)
    else:
        e = find_event(world, a.target)
    if a.op in ('add', 'set'):
        for key, value, allowed in (('kind', a.kind, KINDS), ('seen', a.seen, SEEN)):
            if value is not None and value and value not in allowed:
                raise TimelineError(f"{key} {value!r}: use {', '.join(allowed)}")
            if value is not None:
                e[key] = value
        if a.op == 'set':
            if a.at and e['story'] and not (here and here.get('key') == e['story'] and 'episodes' not in here):
                raise TimelineError(f"{label(e)} is in {e['story']}; set its place there, as event set {e['story']}")
            e['at'] = at_ref(world, here if e['story'] else None, a.at) if a.at else e['at']
            e['note'] = cell(a.note) if a.note is not None else e.get('note', '')
            if a.rename:
                if any(x is not e and same(x['thread'], e['thread']) and same(x['event'], a.rename) for x in events):
                    raise TimelineError(f"{e['thread']} already has an event {a.rename!r}")
                old, e['event'] = label(e), name(a.rename)
                relabel(world, old, label(e))
    elif a.op == 'remove':
        events.remove(e)
        for x in events:
            x['links'] = links_text([l for l in links_of(x) if not same(f'{l[1]}: {l[2]}', label(e))])
    else:
        to = find_event(world, a.to)
        keep = [l for l in links_of(e) if not same(f'{l[1]}: {l[2]}', label(to))]
        e['links'] = links_text(keep + ([(name(a.effect), to['thread'], to['event'])] if a.op == 'link' else []))
    thread = e['thread']
    for t in world['threads']:
        if same(t['thread'], thread) and t['status'] == 'resolved' and not paid(of_thread(events, thread)):
            t['status'] = 'active'
    return thread


def list_form(story, thread):
    """The thread's path: its status, then each event with its mark, place and links."""
    t = next((x for x in story['threads'] if same(x['thread'], thread)), {'status': 'no such thread'})
    evs = dict((n.casefold(), v) for n, v in ordered(story)).get(thread.casefold(), [])
    out = [f"  {thread}  · {t['status']}" + (f"  · episodes: {t['episodes'] or '—'}" if 'episodes' in t else '')]
    for e in evs:
        out.append(f"    {SEEN.get(seen(e), '?')} {e['event']} · {e['at'] or 'no place yet'}")
        out += [f'      {w} → {x}: {y}' for w, x, y in links_of(e)]
    return out


def live(story, thread, evs):
    """The slot span (first, last index) a thread is live over, or None."""
    scenes, n = story['scenes'], len(slots(story['scenes']))
    at = [p for p in (place(scenes, e['at']) for e in evs) if p]
    if thread.get('status') == 'recurring':
        marks = [i for p in at for i in p] + [slots(scenes).index(x) for x in thread['on'] + thread['hear']]
        marks = [min(max(i, 0), n - 1) for i in marks]
        return (min(marks), max(marks)) if marks else None
    if not at:
        return None
    a, b = min(p[0] for p in at), max(p[1] for p in at)
    last = evs[-1] if evs else None
    for w, t, x in links_of(last) if last else []:
        hit = next((e for e in story['events'] if same(e['thread'], t) and same(e['event'], x)), None)
        if w == 'pays off' and hit and place(scenes, hit['at']):
            b = max(b, place(scenes, hit['at'])[1])
    return max(a, 0), min(b, n - 1)


def cells(story, thread, evs):
    """Each slot's mark for a thread: seen, heard only, unseen, carried, or blank."""
    order, scenes = slots(story['scenes']), story['scenes']
    span, out = live(story, thread, evs), {}
    at = {}
    for e in evs:
        p = place(scenes, e['at'])
        if p and p[0] >= 0 and p[0] < len(order):
            at.setdefault(order[p[0]], set()).add(seen(e))
    for i, tag in enumerate(order):
        here = at.get(tag, set())
        if tag in thread['on'] or 'on' in here:
            out[tag] = '●'
        elif tag in thread['hear'] or 'heard' in here:
            out[tag] = '○'
        elif 'off' in here:
            out[tag] = '◆'
        elif span and span[0] <= i <= span[1]:
            out[tag] = CARRIED
    return out


def first_mark(marks):
    return next((m for m in ('●', '○', '◆', CARRIED) if m in marks), ' ')


def threads_for(story, only):
    """The story's threads in order, as (thread row, events), narrowed to `only` names when given; a story keeps
    the threads with a mark in it: an event, or its key in their On screen or Heard."""
    rows = {t['thread'].casefold(): t for t in story['threads']}
    out = [(rows.get(n.casefold(), {'thread': n, 'status': 'no such thread', 'on': [], 'hear': []}), evs)
           for n, evs in ordered(story)]
    out = [(t, evs) for t, evs in out if t.get('runs', True)]
    if only:
        wanted = [find_thread(story, n).casefold() for n in only.split(',')]
        out = [x for x in out if x[0]['thread'].casefold() in wanted]
    return out


def crossing_layers(scenes):
    """Each layer that crosses a scene edge, with the first and last slot it covers."""
    order, spans = slots(scenes), {}
    for s in scenes:
        ids = [x['id'] for x in s['shots']]
        for l in s['layers']:
            a, b = (l[k] and l[k]['shot'] for k in ('from', 'to'))
            if (l['from'] is None or l['to'] is None) and ids and (not a or a in ids) and (not b or b in ids):
                got = ids[ids.index(a) if a else 0:(ids.index(b) if b else len(ids) - 1) + 1]
                lo, hi = spans.get(l['name'], (len(order), -1))
                spans[l['name']] = (min(lo, order.index(got[0])), max(hi, order.index(got[-1])))
    return spans


def events_grid(story, rows, shots, window):
    """The events grid over the scenes `shots`: shot columns when every shot fits the window or only part
    of the story is asked for, else scene columns; scene columns too when those scenes have no shots."""
    scenes, order = story['scenes'], slots(story['scenes'])
    layers = crossing_layers(scenes)
    w = 2 + max([len(t['thread']) for t, _ in rows] + [len(n) for n in layers] + [4]) + 2
    marks = [(t['thread'], cells(story, t, evs)) for t, evs in rows]
    cols = [tag for s in shots for tag in ([x['id'] for x in s['shots']] or [str(s['num'])])]
    by_scene = not any(s['shots'] for s in shots) or (len(shots) == len(scenes) and w + 4 * len(cols) - 2 > window)
    out = []
    if by_scene:
        out.append((' ' * w + ''.join(f"{s['num']:<4}" for s in shots)).rstrip())
        groups = [[tag for tag in order if tag in ([x['id'] for x in s['shots']] or [str(s['num'])])] for s in shots]
        for n, m in marks:
            out.append((f'  {n:<{w - 2}}' + ''.join(f'{first_mark({m.get(t) for t in g}):<4}' for g in groups)).rstrip())
        for n, (a, b) in layers.items():
            lo = next(i for i, g in enumerate(groups) if order[a] in g)
            hi = next(i for i, g in enumerate(groups) if order[b] in g)
            out.append(f'  {n:<{w - 2}}' + ' ' * (4 * lo) + '━' * (4 * (hi - lo) + 2))
        return out
    nums = [' '] * (w + 4 * len(cols))
    for s in shots:
        tag = ([x['id'] for x in s['shots']] or [str(s['num'])])[0]
        nums[w + 4 * cols.index(tag):w + 4 * cols.index(tag) + len(str(s['num']))] = str(s['num'])
    out += [''.join(nums).rstrip(), (' ' * w + ''.join(f'{c:<4}' for c in cols)).rstrip()]
    for n, m in marks:
        out.append((f'  {n:<{w - 2}}' + ''.join(f"{m.get(c, ' '):<4}" for c in cols)).rstrip())
    for n, (a, b) in layers.items():
        inside = [i for i, c in enumerate(cols) if a <= order.index(c) <= b]
        if inside:
            out.append(f'  {n:<{w - 2}}' + ' ' * (4 * inside[0]) + '━' * (4 * (inside[-1] - inside[0]) + 2))
    return out + ['', LEGEND]


def heading(text, room):
    """A column header cut to `room` by whole words from its end, never ending on a small word; the
    number stays."""
    words = text.split()
    while len(words) > 1 and (len(' '.join(words)) > room or words[-1].casefold() in STOP):
        words.pop()
    return ' '.join(words)


def nodes_at(rows, col_of):
    """{(row, column): events there}, each event placed by `col_of`; events with no column are left out."""
    out = {}
    for ti, (_, evs) in enumerate(rows):
        for e in evs:
            c = col_of(e)
            if c is not None:
                out.setdefault((ti, c), []).append(e)
    return out


def link_ends(rows, at):
    """Each link between placed events: (source key, target key, effect)."""
    where = {label(e).casefold(): k for k, evs in at.items() for e in evs}
    return [(k, where[f'{t}: {x}'.casefold()], w) for k, evs in at.items() for e in evs
            for w, t, x in links_of(e) if f'{t}: {x}'.casefold() in where]


class Canvas:
    def __init__(self, width):
        self.width, self.rows = width, []

    def row(self, r):
        while len(self.rows) <= r:
            self.rows.append([' '] * self.width)
        return self.rows[r]

    def put(self, r, x, text, blank_only=False):
        line = self.row(r)
        if blank_only and any(c != ' ' for c in line[x:x + len(text)]):
            return
        for i, ch in enumerate(text):
            if 0 <= x + i < self.width:
                line[x + i] = ch

    def get(self, r, x):
        return self.row(r)[x] if 0 <= x < self.width else ''

    def lines(self):
        return [''.join(r).rstrip() for r in self.rows]


def words(text, width):
    """`text` wrapped to `width`, never cutting a word."""
    return textwrap.wrap(text, width, break_long_words=False) or ['']


def corner(cv, r, x, down):
    """Where a link turns off its source row: a tee where the row's line runs on, else a corner."""
    on = cv.get(r, x) in ('─', CARRIED)
    cv.put(r, x, ('┬' if on else '┐') if down else ('┴' if on else '┘'))


def vertical(cv, x, top, bottom):
    for r in range(top, bottom):
        cv.put(r, x, '┼' if cv.get(r, x) in '─┄' else '│' if cv.get(r, x) == ' ' else cv.get(r, x))


def small_view(heads, done, rows, at, edge=None):
    """Columns nine wide, a done row, a dot where a thread has events, bare lines and corners for links."""
    x0 = 2 + max(len(t['thread']) for t, _ in rows) + 2
    xs = [x0 + 9 * i for i in range(len(heads))]
    cv = Canvas(xs[-1] + 7)
    top = 3 if any(done) else 2
    for c, h in enumerate(heads):
        cv.put(0, xs[c], h[:7])
        cv.put(1, xs[c], '━' * 7)
        if done[c]:
            d, t = done[c]
            k = round(d / t * 5) if t else 0
            cv.put(2, xs[c], '▓' * k + '░' * (5 - k))
    if any(done):
        cv.put(2, 2, 'done')
    for ti, (t, evs) in enumerate(rows):
        r = top + ti
        cv.put(r, 2, t['thread'])
        cols = sorted(c for (i, c) in at if i == ti)
        for a, b in zip(cols, cols[1:]):
            cv.put(r, xs[a] + 1, '─' * (xs[b] - xs[a] - 1))
        for c in cols:
            cv.put(r, xs[c], SEEN.get(seen(at[(ti, c)][-1]), '?'))
        if cols and hanging(t, evs):
            cv.put(r, xs[cols[-1]] + 1, CARRIED * (cv.width - xs[cols[-1]] - 1))
    for (si, sc), (ti, tc), _ in link_ends(rows, at):
        if tc < sc or (si, sc) == (ti, tc):
            continue
        x = xs[tc]
        if tc > sc:
            for i in range(xs[sc] + 1, x):
                if cv.get(top + si, i) == ' ':
                    cv.put(top + si, i, '─')
            corner(cv, top + si, x, ti > si)
        vertical(cv, x, top + min(si, ti) + 1, top + max(si, ti))
    return cv.lines()


def thread_graph(heads, bands, rows, at, window, links, carried=(), more=None):
    """The thread graph: a column per place, a row per thread, a node per event, lines along each thread
    and links between them."""
    names = [t['thread'] for t, _ in rows]
    x0 = 2 + max(len(n) for n in names) + 2
    for wrap in (LABEL, NARROW):
        first = {k: words(lbl(evs), wrap)[0] for k, evs in at.items()}
        w = [max([len(first[k]) + 4 for k in at if k[1] == c] + [min(len(h), 16) + 2]) for c, h in enumerate(heads)]
        xs = [x0 + sum(w[:c]) + c for c in range(len(heads))]
        if xs[-1] + w[-1] - 1 <= window:
            break
    keep = len(heads)
    while keep > 1 and xs[keep - 1] + w[keep - 1] - 1 > window:
        keep -= 1
    total = xs[keep - 1] + w[keep - 1]
    cv = Canvas(total)
    for c in range(keep):
        cv.put(0, xs[c], heading(heads[c], w[c] - 2))
        cv.put(1, xs[c], '━' * min(w[c], window - xs[c]))
    r = 2
    if bands:
        tall = 0
        for c in range(keep):
            line = r
            for item in bands[c]:
                for j, part in enumerate(words(item, w[c] - 2)):
                    cv.put(line, xs[c], ('· ' if j == 0 else '  ') + part)
                    line += 1
            tall = max(tall, line - r)
        cv.put(r, 2, 'on screen')
        r += max(tall, 1)
        cv.put(r, 2, '─' * (total - 3))
        r += 1
    links = [(s, t, wd) for s, t, wd in links if s[1] < keep]
    down = {s[0] for s, t, _ in links if t[0] == s[0] + 1}
    R = []
    for ti in range(len(rows)):
        R.append(r)
        r += 1 + (2 if ti in down else 1)
    for ti, (t, evs) in enumerate(rows):
        cv.put(R[ti], 2, t['thread'])
        cols = sorted(c for (i, c) in at if i == ti)
        shown = [c for c in cols if c < keep]
        for a, b in zip(cols, cols[1:]):
            if a >= keep:
                break
            end = xs[a] + 2 + len(first[(ti, a)]) + 1
            if b < keep:
                cv.put(R[ti], end, '─' * (xs[b] - 1 - end) + '▶')
            else:
                cv.put(R[ti], end, '─' * (total - end))
        for c in shown:
            cv.put(R[ti], xs[c], f"{SEEN.get(seen(at[(ti, c)][-1]), '?')} {first[(ti, c)]}")
        if shown and shown[-1] == cols[-1] and hanging(t, evs):
            end = xs[shown[-1]] + 2 + len(first[(ti, shown[-1])]) + 1
            cv.put(R[ti], end, CARRIED * (total - end))
    for (si, sc), (ti, tc), word in links:
        if tc < sc or (si, sc) == (ti, tc):
            continue
        src = R[si]
        if tc >= keep:
            cv.put(src, total - 3, f'→ {heads[tc].split()[0]}')
            continue
        x = xs[tc]
        if tc > sc:
            for i in range(xs[sc] + 2 + len(first[(si, sc)]) + 1, x):
                if cv.get(src, i) == ' ':
                    cv.put(src, i, '─')
            corner(cv, src, x, ti > si)
        vertical(cv, x, min(src, R[ti]) + 1, max(src, R[ti]))
        if ti > si:
            cv.put(R[ti] - 1, x, '▼')
            cv.put(src + 1, x + 2, word, blank_only=True)
        else:
            cv.put(R[ti] + 1, x, '▲')
            cv.put(R[ti] + 1, x + 2, word, blank_only=True)
    for (ti, c), evs in at.items():
        rest = words(lbl(evs), wrap)[1:]
        if c < keep and rest:
            cv.put(R[ti] + 1, xs[c] + 2, ' '.join(rest), blank_only=True)
    out = cv.lines()
    while out and not out[-1]:
        out.pop()
    out += ['', f"  carried through: {', '.join(carried)}"] if carried else []
    if keep < len(heads):
        out += ['', f"  {(more or past_width)(heads[keep:])}"]
    return out


def past_width(rest):
    return f"past the window's width: {', '.join(rest)}"


def go_on(kind, command):
    """The line under a graph cut at the window's width: the numbered columns past it, and the command drawing
    them."""
    def line(rest):
        nums = [h.split()[0] for h in rest if h not in ('before', 'after')]
        if not nums:
            return past_width(rest)
        return f'{kind} {nums[0]}–{nums[-1]} go on: {command} {nums[0]}-{nums[-1]} --view threads'
    return line


def lbl(evs):
    """A node's label: its last event's, with `+N` for the others in the same column."""
    return evs[-1].get('shown', evs[-1]['event']) + (f' +{len(evs) - 1}' if len(evs) > 1 else '')


def slot_scene(scenes, i):
    """The scene number holding slot index `i`, or before / after."""
    order = slots(scenes)
    if i < 0:
        return 'before'
    if i >= len(order):
        return 'after'
    return next(str(s['num']) for s in scenes if order[i] in ([x['id'] for x in s['shots']] or [str(s['num'])]))


def story_board(story, pick):
    """Story zoom over the scenes `pick`: heads, and the column each event sits in."""
    scenes = story['scenes']
    nums = [str(s['num']) for s in pick]
    after = any((place(scenes, e['at']) or (0,))[0] >= len(slots(scenes)) for e in story['events'])

    def col(e):
        p = place(scenes, e['at'])
        if p is None:
            return None
        where = slot_scene(scenes, p[0])
        if where == 'before':
            return 0
        if where == 'after':
            return len(pick) + 1 if after else None
        return nums.index(where) + 1 if where in nums else None
    return ['before'] + [f"{s['num']} {s['name']}" for s in pick] + (['after'] if after else []), col


def scene_zoom(story, rows, zoom, window):
    """The threads view of one scene: its shots as columns, between the events earlier and later."""
    scenes, order = story['scenes'], slots(story['scenes'])
    ids = [x['id'] for x in zoom['shots']] or [str(zoom['num'])]
    lo, hi = order.index(ids[0]), order.index(ids[-1])
    heads = ['earlier'] + ([f"{x['id']} {x['name']}" for x in zoom['shots']] or [f"{zoom['num']} {zoom['name']}"]) \
        + ['later']
    shown, carried, at = [], [], {}
    for t, evs in rows:
        placed = [(e, place(scenes, e['at'])) for e in evs]
        inside = [(e, p) for e, p in placed if p and lo <= p[0] <= hi]
        if not inside:
            span = live(story, t, evs)
            if span and span[0] <= hi and span[1] >= lo:
                carried.append(t['thread'])
            continue
        ti = len(shown)
        shown.append((t, evs))
        before = [(e, p) for e, p in placed if p and p[0] < lo]
        later = [(e, p) for e, p in placed if p and p[0] > hi]
        if before:
            e, p = before[-1]
            at[(ti, 0)] = [{**e, 'shown': f"{e['event']} ({slot_scene(scenes, p[0])})"}]
        for e, p in inside:
            at.setdefault((ti, 1 + order[lo:hi + 1].index(order[p[0]])), []).append(e)
        if later:
            e, p = later[0]
            at[(ti, len(heads) - 1)] = [{**e, 'shown': f"{e['event']} ({slot_scene(scenes, p[0])})"}]
    if not shown:
        return [f"  no thread has an event in {zoom['num']} {zoom['name']}"] + \
            ([f"  carried through: {', '.join(carried)}"] if carried else [])
    inner = range(1, len(heads) - 1)
    links = [l for l in link_ends(shown, at) if l[0][1] in inner and l[1][1] in inner]
    return thread_graph(heads, None, shown, at, window, links, carried)


def show_view(story, view, pick, zoom, only, window, done, command):
    """The threads, small or events view of a story, or the list form under 40 columns."""
    rows = threads_for(story, only)
    if not rows:
        return '  no threads yet; thread add <story> <name> starts one'
    if window < 40:
        return '\n'.join(line for t, _ in rows for line in list_form(story, t['thread']))
    if view == 'events':
        return '\n'.join(events_grid(story, rows, [zoom] if zoom else pick, window))
    if zoom:
        return '\n'.join(scene_zoom(story, rows, zoom, window))
    heads, col = story_board(story, pick)
    at = nodes_at(rows, col)
    if view == 'small':
        return '\n'.join(small_view([h.split()[0] for h in heads], [None] + [done(s) for s in pick]
                                    + [None] * (len(heads) - len(pick) - 1), rows, at))
    bands = [[]] + [[x['name'] for x in s['shots']] or [b['text'] for b in s['beats']] for s in pick] \
        + [[]] * (len(heads) - len(pick) - 1)
    return '\n'.join(thread_graph(heads, bands, rows, at, window, link_ends(rows, at), more=go_on('scenes', command)))


def detail_thread(story, ref):
    return '\n'.join(list_form(story, find_thread(story, ref)))


def shot_lines(story, tag):
    """For detail of a shot: the events at it and the threads on screen in it."""
    evs = [e for e in story.get('events', []) if e['at'].strip() == tag]
    on = [t['thread'] for t in story.get('threads', []) if tag in t['on']]
    return ([f"  events  {', '.join(SEEN.get(seen(e), '?') + ' ' + label(e) for e in evs)}"] if evs else []) \
        + ([f"  threads on screen  {', '.join(on)}"] if on else [])


def thread_tasks(story):
    """Each open task threads raise, as (its first scene's number, or None, the task)."""
    scenes, out = story['scenes'], []
    every = (story.get('world') or story)['events']
    for t, evs in threads_for(story, None):
        if evs and hanging(t, of_thread(every, t['thread'])):
            p = place(scenes, evs[0]['at'])
            where = slot_scene(scenes, p[0]) if p else None
            out.append((where if where not in ('before', 'after') else None,
                        f"thread {t['thread']}: set up, never paid off"))
        out += [(None, f'event {label(e)} has no place; give it a scene or shot') for e in evs if not e['at'].strip()]
    return out + [(None, p) for p in thread_problems(story)]


def what(tag):
    return 'shot' if re.match(r'^\d+[a-z]+$', tag) else 'scene'


def thread_problems(story):
    """What check names in the story's threads and events; check <world> names the world's own."""
    scenes, out = story['scenes'], []
    names = [t['thread'] for t in story['threads']]
    every = (story.get('world') or story)['events']
    for e in story['events']:
        if not any(same(e['thread'], n) for n in names):
            out.append(f"event {label(e)}: there is no thread {e['thread']}")
        at = e['at'].strip()
        if at and place(scenes, at) is None:
            out.append(f'event {label(e)} is at {at}; there is no {what(at)} {at}')
        for w, t, x in links_of(e):
            hit = next((y for y in every if same(y['thread'], t) and same(y['event'], x)), None)
            if hit is None:
                out.append(f'link {label(e)} → {t}: {x} names no event')
            elif hit.get('story', '') == e.get('story', '') and place(scenes, hit['at']) and place(scenes, at) \
                    and place(scenes, hit['at'])[0] < place(scenes, at)[0]:
                out.append(f'link {label(e)} → {label(hit)} points back in time')
    for t in story['threads']:
        for key in ('on screen', 'heard'):
            out += [f"thread {t['thread']} lists {bad} {key}; there is no {what(bad)} {bad}"
                    for bad in expand(t[key], scenes)[1]]
    return out


def world_problems(world, keys):
    """What check <world> names in its threads and events: a thread with no event in the world, a place in a story
    `keys` doesn't hold, an event in such a story, and each of the world's own events on no thread, at no moment
    or linking to no event."""
    out, names = [], [t['thread'] for t in world['threads']]
    for e in world['events']:
        if e['story']:
            out += [] if e['story'] in keys else [f"event {label(e)} is in {e['story']}; there is no such story"]
            continue
        if not any(same(e['thread'], n) for n in names):
            out.append(f"event {label(e)}: there is no thread {e['thread']}")
        at = e['at'].strip()
        if at not in ('', 'before', 'after') and not any(same(m['moment'], at) for m in moments_of(world)):
            out.append(f'event {label(e)} is at {at}; there is no such moment')
        out += [f'link {label(e)} → {t}: {x} names no event' for _, t, x in links_of(e)
                if not any(same(label(y), f'{t}: {x}') for y in world['events'])]
    for t in world['threads']:
        if not of_thread(world['events'], t['thread']):
            out.append(f"thread {t['thread']} has no events")
        out += [f"thread {t['thread']} lists {k} {col}; there is no such story" for col in ('on screen', 'heard')
                for k in places(t[col]) if k not in keys]
    return out


def world_tasks(world, keys):
    """Each open task of the world's threads, as (threads, the task): a thread its events never pay off, one of the
    world's own events with no place, and what check <world> names in them."""
    out = [f"thread {t['thread']}: set up, never paid off" for t in world['threads']
           if of_thread(world['events'], t['thread']) and hanging(t, of_thread(world['events'], t['thread']))]
    out += [f'event {label(e)} has no place; give it a moment' for e in world['events']
            if not e['story'] and not e['at'].strip()]
    return [('threads', t) for t in out + world_problems(world, keys)]


def episode_of(at):
    """The episode number a series event's At names, or 0 for before."""
    return int(re.sub(r'\D', '', at) or 0)


def series_story(series):
    """The series as one story for its views and list form: the world's threads, each with the numbers of the
    episodes it has a mark in (`runs` when it has one), and the events in them at an episode's number: an episode's
    own, and the world's at the moment an episode is set at; the world's before stays before."""
    world, eps = series['world'] or {'threads': [], 'events': []}, series['episodes']
    num = {ep['key']: ep['num'] for ep in eps}
    then = {}
    for ep in eps:
        then.setdefault(ep['when'].casefold(), ep['num']) if ep['when'] else None
    col = lambda e: num.get(e['story']) if e['story'] else e['at'] if e['at'] == 'before' else then.get(e['at'].casefold())
    evs = [{**e, 'at': str(col(e))} for e in world['events'] if col(e)]
    threads = []
    for t in world['threads']:
        n = sorted({num[k] for c in ('on screen', 'heard') for k in places(t[c]) if k in num}
                   | {int(e['at']) for e in of_thread(evs, t['thread']) if e['at'] != 'before'})
        threads.append({**t, 'episodes': ', '.join(map(str, n)), 'runs': bool(n), 'on': [], 'hear': []})
    names = {t['thread'].casefold() for t in threads if t['runs']}
    return {'threads': threads, 'scenes': [], 'events': sorted(
        (e for e in evs if e['thread'].casefold() in names), key=lambda e: -1 if e['at'] == 'before' else int(e['at']))}


def world_story(world):
    """The world as one story for its views and list form: every thread and event, an event in a story at
    `<story key> <its place>`."""
    return {'threads': [{**t, 'on': [], 'hear': []} for t in world['threads']], 'scenes': [],
            'events': [{**e, 'at': f"{e['story']} {e['at']}".strip()} for e in world['events']]}


def columns_view(story, heads, short, col, view, window, only, done, more):
    """A series or world drawn with `heads` as columns (`short` in the small view and events grid), each event in the
    column `col` gives it, every thread or the ones `only` names; under 40 columns, the list form. `done` is each
    column's (done, total) or None, `more` names the columns past the window's width."""
    rows = threads_for(story, only)
    if not rows:
        return '  no threads yet'
    if window < 40:
        return '\n'.join(line for t, _ in rows for line in list_form(story, t['thread']))
    at = nodes_at(rows, col)
    if view == 'small':
        return '\n'.join(small_view(short, done, rows, at))
    if view == 'events':
        w = 2 + max(len(t['thread']) for t, _ in rows) + 2
        cw = [max(4, len(h) + 2) for h in short]
        out = [(' ' * w + ''.join(f'{h:<{cw[c]}}' for c, h in enumerate(short) if c)).rstrip()]
        for ti, (t, es) in enumerate(rows):
            cols = sorted(c for (i, c) in at if i == ti and c)
            line = ''.join(f"{SEEN.get(seen(at[(ti, c)][-1]), '?') if (ti, c) in at else CARRIED if cols and cols[0] < c < cols[-1] else ' ':<{cw[c]}}"
                           for c in range(1, len(heads)))
            out.append((f"  {t['thread']:<{w - 2}}" + line).rstrip())
        return '\n'.join(out)
    return '\n'.join(thread_graph(heads, None, rows, at, window, link_ends(rows, at), more=more))


def series_view(series, view, window, pick=None, only=None):
    """A series drawn with its episodes as columns, all or the ones `pick` gives: the dots are the episodes
    holding each thread's events; `only` keeps the threads it names. Under 40 columns, the list form."""
    eps = pick or series['episodes']
    nums = [ep['num'] for ep in eps]
    col = lambda e: 0 if e['at'] == 'before' else nums.index(int(e['at'])) + 1 if int(e['at']) in nums else None
    return columns_view(series_story(series), ['before'] + [f"{ep['num']} {ep['title']}" for ep in eps],
                        ['before'] + [str(ep['num']) for ep in eps], col, view, window, only,
                        [None] + [(ep['done'], ep['total']) for ep in eps], go_on('episodes', f"show {series['path']}"))


def world_view(world, when, view, window, only):
    """The world's threads drawn with its moments as columns, in timeline order: the world's own events at theirs,
    a story's at the moment it is set at (`when`, {story key: its moment}), and a story set at no moment in a column
    of its own after them."""
    ms = [m['moment'] for m in moments_of(world)]
    at = {m.casefold(): i + 1 for i, m in enumerate(ms)}
    loose = list(dict.fromkeys(e['story'] for e in world['events']
                               if e['story'] and when.get(e['story'], '').casefold() not in at))

    def col(e):
        if not e['story']:
            return 0 if e['at'] == 'before' else len(ms) + 1 if e['at'] == 'after' else at.get(e['at'].casefold())
        return at.get(when.get(e['story'], '').casefold()) or len(ms) + 2 + loose.index(e['story'])
    heads = ['before', *ms, 'after', *loose]
    return columns_view(world_story(world), heads, heads, col, view, window, only, [None] * len(heads), past_width)
