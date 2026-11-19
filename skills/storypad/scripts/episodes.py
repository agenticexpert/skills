"""A series and its episodes: series.md and its ep-<key>/ folders read and written back, episodes
added, moved and renamed by place, and the series shown and synced.
"""

import re

from continuity import THREAD_ICON, episode_tag, series_story
from scenes import (STAGES, check, keeps_own, mini, old, open_counts, read_story, run_of, story_new,
    sync_story, todo, world_key, writable)
from storyfile import (FIXED, TimelineError, cell, dated, frontmatter, listed, listing, listing_problems, meta_pairs,
    named, put_frontmatter, replace_section, save, sections, slug, top, unique)
from venues import template

OLD_EPISODE = re.compile(r'^ep-(\d+)(?:-(.*))?$')
ARC = ('Ep', 'Title', 'Folder', 'Status', 'Arc Position', 'Premise')


def series_doc(path):
    """series.md, read: the episode folders in the order of its Episode Arc table. Refused in the old layout."""
    doc = path / 'series.md'
    text = doc.read_text(encoding='utf-8')
    body = sections(text)
    dirs = sorted(p.name for p in path.iterdir() if p.is_dir())
    present = {n for n in dirs if n.startswith('ep-') and (path / n / 'index.md').is_file()}
    head, folders, rows, odd, unlisted = listing(body.get('episode arc'), ARC, 'folder', present)
    staged = [n for n in dirs if n == '.new-episode' or n.startswith('.place-')]
    if staged:
        raise TimelineError(old(path, f'{staged[0]} is left from an unfinished episode add or move'))
    numbered = [n for n in dirs if OLD_EPISODE.match(n) and n not in rows]
    if numbered:
        raise TimelineError(old(path, f'{numbered[0]} is a numbered episode folder'))
    return {'path': path, 'text': text, 'fm': frontmatter(text), 'doc': doc, 'head': head, 'folders': folders,
            'rows': rows, 'odd': odd, 'unlisted': unlisted}


def read_series(path, world=None):
    """A series and its episodes; `world` is its world's world.md, read. A series keeping its own assets,
    locations, threads, events or pins is the older layout."""
    if not is_series(path):
        raise TimelineError(f'{path} is not a series: it has no series.md')
    series = series_doc(path)
    series.update(world=world, key=world_key(path, world['path']) if world else path.name)
    keeps_own(path, sections(series['text']))
    series['episodes'] = [read_story(path / f, series, world) for f in series['folders']]
    return series


def is_series(path):
    return (path / 'series.md').exists()


def series_status(series):
    """How far the series' work has got: the stage of its episode furthest behind; brainstorming with
    no episodes."""
    return min((e['status'] for e in series['episodes']), key=STAGES.index, default='brainstorming')


def show_series(series):
    fm, eps = series['fm'], series['episodes']
    out = [f"  {fm.get('series-name') or series['path'].name}",
           f"  [{fm.get('venue', '?')}] — {series_status(series)}", '']
    if not eps:
        return '\n'.join(out + ['  (no episodes yet)'])
    w = max(10, *(len(e['title']) for e in eps))
    for e in eps:
        out.append(f"  {e['num']:<3} {e['title']:<{w}}  {e['status']:<13}  {e['row'].get('arc position', ''):<10}  "
                   f"{mini(e['done'], e['total'])} {e['done']}/{e['total']}  "
                   f"{open_counts(e['open']) if e['scenes'] else 'no scenes yet'}")
    threads = [t for t in series_story(series)['threads'] if t['runs']]
    if threads:
        out += ['', '  Threads']
        out += [f"  {THREAD_ICON.get(t['status'], '?')} {t['thread']}  [{t['status']}]  "
                f"episodes: {t['episodes']}" for t in threads]
    return '\n'.join(out)


def series_text(series):
    """series.md with the episode arc and the status as the series now holds them."""
    rows = [{**e['row'], 'ep': str(e['num']), 'title': e['title'], 'folder': e['path'].name, 'status': e['status'],
             'premise': e['row'].get('premise') or e['fm'].get('premise', '')} for e in series['episodes']]
    text = replace_section(series['text'], 'Episode Arc', listed(series['head'], rows, series['odd'], ARC))
    if 'status' in series['fm']:
        text = put_frontmatter(text, 'status', series_status(series))
    return dated(series['text'], text)


def save_series(series):
    text = series_text(series)
    if text != series['text']:
        save(series['doc'], text)


def episode_changed(story):
    """series.md rewritten after a change to `story`, when it is an episode."""
    if story['num']:
        save_series(read_series(story['path'].resolve().parent, story['world']))


def series_todo(series, only):
    """Each episode's open tasks."""
    return '\n'.join(line for e in series['episodes'] for line in todo(e, episode_tag(e), only=only)) or 'no episodes yet'


def series_check(series):
    """What check names in series.md (its arc), then in each episode."""
    present = {e['path'].name for e in series['episodes']}
    found = listing_problems('Episode Arc', series, 'folder', present, '')
    return '\n'.join([f'  {p}' for p in found] + [f"ep {e['num']} {e['title']}\n{check(e)}"
                                                  for e in series['episodes']]) or 'no episodes yet'


def sync_series(series, episodes):
    """Sync `episodes` of the series, every one checked before the first write, then series.md."""
    for e in episodes:
        writable(e)
    lines = [sync_story(e) for e in episodes]
    save_series(series)
    return '\n'.join(lines + [f"{series['path'].name}: {len(series['episodes'])} episodes"])


def find_episode(series, ref):
    text = str(ref).strip()
    for e in series['episodes']:
        if text.isdigit() and e['num'] == int(text):
            return e
    raise TimelineError(f"no episode {text}; the episodes are "
                        f"{', '.join(str(e['num']) for e in series['episodes']) or 'none yet'}")


def picked_episodes(series, at):
    """The episodes `at` names: one episode number, or a run `<from>-<to>`."""
    return run_of(series['episodes'], at, lambda ref: find_episode(series, ref))


def renumber_episodes(series, episodes):
    """Put the episodes in the order `episodes`, numbered by place."""
    for n, e in enumerate(episodes, 1):
        e['num'] = n
        if not top(e['text']):
            e['title'] = f'Episode {n}'
    series['episodes'] = episodes


def series_new(path, text):
    """A new series folder holding `text` as its series.md."""
    path.mkdir(parents=True)
    save(path / 'series.md', text)


def episode_index(series, title):
    """A new episode's index.md: its venue's index template, filled in for the series."""
    text = template(series['fm'].get('venue') or 'youtube', 'index.md', title)
    text = put_frontmatter(text, 'type', 'series-episode')
    return put_frontmatter(text, 'series', f'"{series["fm"].get("series-name") or series["path"].name}"')


def episode_add(series, title, before, meta):
    title, pairs = cell(title), meta_pairs(meta, FIXED)
    eps = series['episodes']
    at = find_episode(series, before)['num'] - 1 if before else len(eps)
    text = episode_index(series, title)
    for k, v in pairs:
        text = put_frontmatter(text, k, v or None)
    folder = series['path'] / f"ep-{unique(slug(title) or 'episode', lambda k: (series['path'] / f'ep-{k}').exists())}"
    story_new(folder, text, series)
    renumber_episodes(series, eps[:at] + [read_story(folder, series, series['world'])] + eps[at:])
    save_series(series)


def episode_move(series, src, dst):
    e, to = find_episode(series, src), find_episode(series, dst)
    eps = [x for x in series['episodes'] if x is not e]
    eps.insert(to['num'] - 1, e)
    renumber_episodes(series, eps)
    save_series(series)


def episode_set(series, ref, title, meta):
    e = writable(find_episode(series, ref))
    pairs = meta_pairs(meta, FIXED)
    text = named(e['text'], cell(title)) if title is not None else e['text']
    for k, v in pairs:
        text = put_frontmatter(text, k, v or None)
    if text != e['text']:
        save(e['doc'], dated(e['text'], text))
    h = top(text)
    e['title'] = h.group(1) if h else f"Episode {e['num']}"
    save_series(series)
