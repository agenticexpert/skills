"""Migration: a story's numbered scene files, or a series' numbered episode folders and their scenes,
converted to the layout keyed by name, every new file written before any old one is deleted.
"""

import re
import shutil
from pathlib import Path

import timeline
from continuity import parse_threads, renumber_threads, thread_end
from episodes import ARC, OLD_EPISODE, is_series, series_text
from scenes import OLD_SCENE, SCENES, index_text, parse_scene, reorder, scene_text, tally
from storyfile import TimelineError, frontmatter, named, put_frontmatter, save, sections, slug, table, top, unique

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
             'scenes': [], 'head': head, 'odd': odd, 'unlisted': [], 'pins_head': pins_head, 'pins': pins, 'series_pins': [],
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
    series = series_text({'text': text, 'fm': frontmatter(text), 'head': head, 'odd': odd, 'episodes': episodes,
                          'threads_head': threads_head, 'threads': threads, 'pins_head': pins_head, 'pins': pins})
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


def migrate(path):
    """Convert a story's numbered scene files, or a series' numbered episode folders and their
    scenes, to the new layout: every new file is written before any old one is deleted."""
    if is_series(path):
        return migrate_series(path)
    if not (path / 'index.md').is_file():
        raise TimelineError(f'{path} is not a story or a series: it has no index.md or series.md')
    return migrate_story(path)
