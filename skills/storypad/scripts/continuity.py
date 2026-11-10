"""A series' continuity threads: the episodes each runs through, renumbered with them, edited
by command, and the series pins they carry into each episode.
"""

import re

from storyfile import TimelineError, meta_pairs, name, same, table, table_text

THREADS = ('Thread', 'Status', 'Introduced', 'Last Referenced', 'Episodes')
THREAD_ICON = {'active': '●', 'resolved': '✓', 'dormant': '○', 'recurring': '↻'}


def parse_threads(lines):
    """The Continuity Threads table's header and threads."""
    head, threads = table(lines, THREADS)
    return head, [t for t in threads if t['thread']]


def threads_table(head, threads):
    return table_text(head, threads, THREADS)


def thread_end(threads):
    """A series pin end: a continuity thread's name, or None for the whole series."""
    def end(text):
        text = (text or '').strip()
        if not text:
            return None
        hit = next((t for t in threads if same(t, text)), None)
        if hit is None:
            raise TimelineError(f"no thread {text}; the threads are {', '.join(threads) or 'none yet'}")
        return hit
    return end


def episodes_of(thread):
    return [int(n) for n in re.findall(r'\d+', thread['episodes'])]


def series_pins(series, num):
    """The series pins that hold in episode `num`, as whole-story pins with story-relative refs."""
    threads = {t['thread']: episodes_of(t) for t in series['threads']}
    out = []
    for p in series['pins']:
        if p['broken'] or (p['from'] and num not in threads.get(p['from'], [])):
            continue
        ref = p['ref'] if re.match(r'^(https?://|/|~)', p['ref']) else f"../{p['ref']}"
        out.append({**p, 'name': p['name'] + (f" ({p['from']})" if p['from'] else ''),
                    'from': None, 'to': None, 'ref': ref})
    return out


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


def edit_thread(series, a):
    threads = series['threads']
    pairs = meta_pairs(getattr(a, 'meta', None), [c.lower() for c in THREADS])
    found = [t for t in threads if same(t['thread'], a.name)]
    if a.op == 'add':
        if found:
            raise TimelineError(f"there is already a thread {found[0]['thread']!r}")
        found = [{'thread': name(a.name), 'status': 'active', 'introduced': '', 'last referenced': '',
                  'episodes': ''}]
    elif not found:
        raise TimelineError(f"no thread {a.name!r}; the threads are {', '.join(t['thread'] for t in threads) or 'none yet'}")
    t = found[0]
    users = [p for p in series['pins'] if p['from'] == t['thread']]
    if a.op == 'remove':
        if users:
            raise TimelineError(f"{t['thread']} carries the pins {', '.join(p['name'] for p in users)}; "
                                'change or remove those first')
        threads.remove(t)
        return
    rename = getattr(a, 'rename', None)
    if rename and any(x is not t and same(x['thread'], rename) for x in threads):
        raise TimelineError(f'there is already a thread {rename!r}')
    values = {'thread': name(rename) if rename else t['thread'], 'status': a.status or t['status']}
    if a.episodes is not None:
        nums = {int(n) for n in re.findall(r'\d+', a.episodes)}
        have = range(1, len(series['episodes']) + 1)
        unknown = sorted(nums - set(have))
        if unknown:
            raise TimelineError(f"no episode {', '.join(map(str, unknown))}; the episodes are "
                                f"{', '.join(map(str, have)) or 'none yet'}")
        listed_nums = sorted(nums)
        values.update({'episodes': ', '.join(map(str, listed_nums)),
                       'introduced': str(listed_nums[0]) if listed_nums else '',
                       'last referenced': str(listed_nums[-1]) if listed_nums else ''})
    t.update(values)
    t.update(pairs)
    if a.op == 'add':
        threads.append(t)
    for p in users:
        p['from'] = p['to'] = t['thread']
