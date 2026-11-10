#!/usr/bin/env python3
"""Storypad state, read from the files.

  storypad.py show <story> [<scene>] [--view strip|breakdown|table|gantt]
  storypad.py detail <story> <scene or shot id> [<layer>]
  storypad.py scene add <story> [<name>] [--before N]       (default: before the closing scene)
  storypad.py scene move <story> <N> <to N>
  storypad.py scene set <story> <N> [--name N] [--note T]
  storypad.py scene remove <story> <N> [--force]
  storypad.py shot add <story> <scene> <name> [--shows S] [--length L] [--ends E] [--before ID]
  storypad.py shot set <story> <id> [--name N] [--shows S] [--length L] [--ends E] [--note T] [--reviewed]
  storypad.py shot move <story> <id> <to id | to scene N>
  storypad.py shot remove <story> <id> [--force]
  storypad.py layer add <story> <scene> <name> --from REF --to REF [--in E] [--out E] [--file F [--link]]
  storypad.py layer set <story> <scene> <name> [--rename N] [--from REF] [--to REF] [--in E] [--out E]
                        [--file F [--link]] [--note T]
  storypad.py layer remove <story> <scene> <name>
  storypad.py take add <story> <shot id> --file F [--in S] [--prompt P] [--model M] [--refs R] [--note T]
                       [--link] [--approve]
  storypad.py take set <story> <take id> [--in S] [--prompt P] [--model M] [--refs R] [--note T]
  storypad.py take approve|unapprove|remove <story> <take id>
  storypad.py pin add <story|series> <name> --keep K [--ref FILE|URL|TAKE] [--from T] [--to T] [--link]
                      [--note T]
  storypad.py pin set <story|series> <name> [--rename N] [--keep K] [--ref FILE|URL|TAKE] [--from T] [--to T]
                      [--link] [--note T]
  storypad.py pin remove <story|series> <name>
  storypad.py episode add <series> [<title>] [--before N]
  storypad.py episode move <series> <N> <to N>
  storypad.py episode set <series> <N> [--name <title>]
  storypad.py thread add <series> <name> [--status S] [--episodes N,N]
  storypad.py thread set <series> <name> [--rename N] [--status S] [--episodes N,N]
  storypad.py thread remove <series> <name>
  storypad.py cut <story> [<scene>] [--output PATH] [--size WxH]
  storypad.py clean <story|series> [--delete]
  storypad.py check <story>
  storypad.py todo <story>
  storypad.py sync <story>
  storypad.py compile <story> [--output PATH | --stdout]
  storypad.py migrate <story|series>
  storypad.py list [<root>]
  storypad.py new <title> [--series] [--venue V] [--premise P] [--audience A] [--length L]

Every add and set also takes --meta key=value, repeatable; key= removes it. On a shot, layer,
take, pin or thread it is a column of its own; on a scene or an episode, a frontmatter key.

A story is a folder holding index.md and scenes/; a series is a folder holding series.md and
ep-<key>/ story folders. show, todo, check, sync and clean take either.

A scene's number is its place: its row in the Scenes table of index.md. Adding, moving or
removing a scene renumbers the scenes after it, and every shot, take and pin id follows: scene 2
becomes 3, shot 2a becomes 3a. A scene's name is free; with none it shows as "Scene 3". Where a
command takes a scene number it takes the scene's name too: the scene named so, else the one whose
name holds the words; two that fit are refused with their list. Its file,
scenes/<key>.md, is named once and never changes. An episode's number is its row in the Episode
Arc table of series.md, its folder ep-<key>/ never changes, and thread episode numbers follow it.
migrate converts the numbered scene files and episode folders of an older storypad. new and
episode add start a story or episode with its venue's first scenes (youtube: Intro, Wrapup) and
their beats; scene add gives a scene named like one of them its beats.

A shot id is the scene number and letters: 3a, 3b. The letters name the shot and never change; they
don't give its place (a shot added before 3a can be 3c), and every view lists shots in scene order.
A shot moved to another scene takes the next id there. A length is seconds or m:ss; leave it out
when not known yet. A shot ends cut, match, "dissolve <s>" or "fade <s>"; a layer starts and ends
cut or "fade <s>". A layer REF is a shot id (3b: its start, or its end as --to), seconds into one
(3b+8), or open, to carry across the scene's edge. A carried layer keeps one file: --file on any
scene of the carry goes to every scene it runs through, and a layer added into the carry takes it.

A take is a made file for a shot: 3a.1, 3a.2; the approved one is marked 3a.1+. Its file is
copied into assets/; its prompt defaults to its shot's prompt (--meta prompt=); its refs default to
the files of the pins over the shot; --in is where in the file the cut starts it. A take number is
never used twice for a shot.

A pin keeps one aspect (--keep; "all" keeps the file exactly) of its --ref over a shot, a scene,
or a run from one to another (T is a shot id or scene number; neither = the whole story). On a
series, T is a continuity thread: the pin holds in every episode the thread lists. With no
--ref, a pin on one shot keeps its approved take. A file is copied into assets/ unless already
there; --link keeps a link instead.

A note on a scene, shot, take, layer or pin is never part of the content: compile and cut leave
it out, and detail shows it. Names and values stay on one line, without |.

A thread's --episodes lists the episode numbers it runs through; its first and last set
Introduced and Last Referenced.

Removing a scene that has a script, ticked beats or takes, or a shot that has takes, is refused
without --force, and the refusal lists what would be lost. While a scene's timeline can't be read,
every command that writes to its story, clean and cut refuse and name it; show, detail, todo,
check and compile still run.

A story's status is how far its story work has got: brainstorming with no scenes, then outlining,
then refining once set in index.md; open tasks never change it. todo lists the open tasks: each
open beat and prep item and each scene with no script; each shot with no take or no length, each
shot with takes but none approved, and each prompt (--meta prompt=) or approved take marked for
review: its shows line, its scene's script or a pin over it changed since it was written or
approved; shot set --reviewed clears that. One kept before storypad marked them takes its mark,
unflagged, from the first command that reads its story. Each layer with no file. On the cut, each
problem check names. show, list and sync name the status and the open tasks, or nothing open. A
series' status is its episode furthest behind; every change to an episode rewrites the episode arc
and status in series.md. cut renders
cut.mp4 with ffmpeg from each shot's approved take, its length and ending, and every layer with a
file; a shot with no approved take is black and a layer with no file is left out, each named. A
layer with no file but a text (--meta text=, a title's words) is drawn with ffmpeg's drawtext, else
shown on a plain card.
--size is an even width and height. The last cut is replaced only once the new one is made. clean
lists the files in assets/ that no pin, take or layer keeps; --delete removes them.
"""

import argparse
import sys
from pathlib import Path

import cut
import timeline
from continuity import THREAD_ICON, edit_thread, thread_end
from episodes import (episode_add, episode_changed, episode_move, episode_set, is_series, read_series, save_series,
    series_new, series_status, show_series, story_at, sync_series)
from migrate import migrate
from scenes import (VIEWS, check, compile_script, detail, open_counts, save_story, scene_add, scene_move,
    scene_remove, scene_set, show_scene, show_story, story_new, sync_story, todo, writable)
from storyfile import TimelineError, listing_problems, name, same, save, slug
from venues import started


def list_root(root):
    if not root.is_dir():
        raise TimelineError(f'no stories folder at {root}; give the folder that holds your stories')
    rows, unread = [], []
    for path in sorted(p for p in root.iterdir() if p.is_dir()):
        kind = 'series' if is_series(path) else 'single' if (path / 'index.md').exists() else None
        try:
            if kind == 'series':
                s = read_series(path)
                opened = {k: sum(e['open'][k] for e in s['episodes']) for k in ('scene', 'shot', 'layer', 'cut')}
                rows.append((path.name, s['fm'].get('venue', '?'), f"series ({len(s['episodes'])})",
                             series_status(s), open_counts(opened) if any(e['scenes'] for e in s['episodes'])
                             else '—'))
            elif kind:
                s = story_at(path)
                rows.append((path.name, s['fm'].get('venue', '?'), 'single', s['status'],
                             open_counts(s['open']) if s['scenes'] else '—'))
        except TimelineError as e:
            rows.append((path.name, '?', kind, "can't read", ''))
            unread.append(f'{path.name}: {e}')
    if not rows:
        return f'no storypads in {root}'
    w = max(4, *(len(r[0]) for r in rows))
    lines = [f"{'Name':<{w}}  {'Venue':<8}  {'Type':<11}  {'Status':<16}  Open"]
    lines += [f'{n:<{w}}  {v:<8}  {t:<11}  {st:<16}  {d}' for n, v, t, st, d in rows]
    return '\n'.join(lines + ([''] + unread if unread else []))


def with_problems(out, story):
    found = timeline.problems(story.get('scenes', [])) + timeline.assets_missing(story)
    return out + ('\n\n' + '\n'.join(f'  {p}' for p in found) if found else '')


def run_edit(a):
    if a.cmd in ('episode', 'thread') or (a.cmd == 'pin' and is_series(a.story)):
        series = read_series(a.story)
        if a.cmd == 'thread':
            edit_thread(series, a)
            save_series(series)
        elif a.cmd == 'pin':
            timeline.edit_pin(series, a, thread_end([t['thread'] for t in series['threads']]))
            save_series(series)
        else:
            {'add': lambda: episode_add(series, a.name, a.before, a.meta),
             'move': lambda: episode_move(series, a.target, a.to),
             'set': lambda: episode_set(series, a.target, a.name, a.meta)}[a.op]()
        series = read_series(a.story)
        out = show_series(series)
        return with_problems(out, {**series, 'scenes': []}) if a.cmd == 'pin' else out
    story = writable(story_at(a.story))
    if a.cmd == 'scene':
        gone = {'add': lambda: scene_add(story, a.name, a.before, a.meta),
                'move': lambda: scene_move(story, a.target, a.to),
                'set': lambda: scene_set(story, a.target, a.name, a.note, a.meta),
                'remove': lambda: scene_remove(story, a.target, a.force)}[a.op]()
        save_story(story, gone or ())
        episode_changed(story)
        story = story_at(a.story)
        return with_problems(show_story(story, 'strip'), story)
    if a.cmd == 'pin':
        timeline.edit_pin(story, a, lambda t: timeline.pin_end(timeline.scene_ref(story, t), story['scenes']))
        save_story(story)
        episode_changed(story)
        story = story_at(a.story)
        lines = [show_story(story, 'strip')]
        pin = next((p for p in story['pins'] if same(p['name'], getattr(a, 'rename', None) or a.name)), None)
        if pin and pin['from'] and not pin['broken']:
            lines += [''] + [show_scene(story, s) for s in story['scenes']
                             if str(s['num']) in timeline.covers(pin, story['scenes'])]
        return with_problems('\n'.join(lines), story)
    changed = {'shot': timeline.edit_shot, 'layer': timeline.edit_layer, 'take': timeline.edit_take}[a.cmd](story, a)
    for s in changed:
        s['dirty'] = True
    save_story(story)
    episode_changed(story)
    story = story_at(a.story)
    if a.cmd == 'take':
        return with_problems(detail(story, a.target.split('.')[0], None), story)
    return with_problems(show_scene(story, timeline.find_scene(story, changed[-1]['num'])), story)


STORIES = Path('agents/storypad/stories')


def new(a):
    """A new story or series in the stories folder, named for its title, from its venue's template."""
    title = name(a.title)
    path = STORIES / (slug(title) or 'story')
    if path.exists():
        raise TimelineError(f'{path} is already there; open it')
    text = started(a.venue, 'series.md' if a.series else 'index.md', title, a.premise,
                   {'series-name': title} if a.series else {'audience': a.audience, 'target-length': a.length})
    if a.series:
        series_new(path, text)
        return f'new series → {path}\n' + show_series(read_series(path))
    story_new(path, text)
    return f'new story → {path}\n' + show_story(story_at(path), 'strip')


def story_path(arg):
    path = Path(arg)
    return path if path.is_dir() or not (STORIES / path).is_dir() else STORIES / path


def parser():
    p = argparse.ArgumentParser(prog='storypad', description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('show', 'todo', 'sync', 'compile', 'check', 'migrate'):
        sub.add_parser(name).add_argument('story', type=story_path)
    sub.choices['show'].add_argument('scene', nargs='?', help='a scene number or name, drawn as its strip')
    sub.choices['show'].add_argument('--view', choices=['strip', *VIEWS], default='strip')
    sub.choices['compile'].add_argument('--output')
    sub.choices['compile'].add_argument('--stdout', action='store_true')
    d = sub.add_parser('detail')
    d.add_argument('story', type=story_path)
    d.add_argument('ref', help='a scene number or name, or a shot id')
    d.add_argument('layer', nargs='?', help='a layer of that scene')

    def group(cmd, ops, target):
        g = sub.add_parser(cmd).add_subparsers(dest='op', required=True)
        for op in ops:
            c = g.add_parser(op)
            c.add_argument('story', type=story_path)
            if target(op):
                c.add_argument('target', help=target(op))
            if op in ('add', 'set'):
                c.add_argument('--meta', action='append', default=[], metavar='KEY=VALUE',
                               help='a field of your own, repeatable; KEY= removes it')
        return g.choices

    note = 'a note, kept out of the script and the cut; empty removes it'
    sc = group('scene', ('add', 'move', 'set', 'remove'), lambda op: None if op == 'add' else 'the scene number or name')
    sc['add'].add_argument('name', nargs='?', default='',
                           help='a name no other scene has; with none it shows as its number')
    sc['add'].add_argument('--before', help="the scene number it goes in front of; default: the venue's closing "
                                            'scene, else the end')
    sc['move'].add_argument('to', help='the scene number or name whose place it takes')
    sc['set'].add_argument('--name', help='a name no other scene has; empty removes it')
    sc['set'].add_argument('--note', help=note)
    sc['remove'].add_argument('--force', action='store_true', help='remove it with its script, ticked beats and takes')
    sh = group('shot', ('add', 'set', 'move', 'remove'),
               lambda op: 'the scene number or name' if op == 'add' else 'the shot id')
    sh['add'].add_argument('name')
    sh['add'].add_argument('--shows', help='what the shot shows, in plain words')
    sh['add'].add_argument('--length', help='leave out when not known yet')
    sh['add'].add_argument('--ends', default='cut')
    sh['add'].add_argument('--before', help='the shot id it goes in front of')
    for flag in ('--name', '--shows', '--length', '--ends'):
        sh['set'].add_argument(flag)
    sh['set'].add_argument('--note', help=note)
    sh['set'].add_argument('--reviewed', action='store_true',
                           help='its prompt and approved take still hold for what it now shows: clear their review')
    sh['move'].add_argument('to', help='the shot id whose place it takes, or a scene number or name to end that scene')
    sh['remove'].add_argument('--force', action='store_true', help='remove it with its takes')
    la = group('layer', ('add', 'set', 'remove'), lambda op: 'the scene number or name')
    for op, default in (('add', 'cut'), ('set', None), ('remove', None)):
        la[op].add_argument('name')
        if op != 'remove':
            la[op].add_argument('--from', dest='start', required=op == 'add')
            la[op].add_argument('--to', dest='end', required=op == 'add')
            la[op].add_argument('--in', dest='fade_in', default=default)
            la[op].add_argument('--out', dest='fade_out', default=default)
            la[op].add_argument('--file', help='the sound, music, title or effect file it plays')
            la[op].add_argument('--link', action='store_true', help='keep a link, not a copy')
    la['set'].add_argument('--rename')
    la['set'].add_argument('--note', help=note)
    tk = group('take', ('add', 'set', 'approve', 'unapprove', 'remove'),
               lambda op: 'the shot id' if op == 'add' else 'the take id')
    tk['add'].add_argument('--file', required=True, help='the made file')
    for op in ('add', 'set'):
        tk[op].add_argument('--in', dest='inpoint', help='seconds into the file where the cut starts it')
        tk[op].add_argument('--note', help=note)
        tk[op].add_argument('--prompt', help="default: its shot's prompt" if op == 'add' else None)
        tk[op].add_argument('--model')
        tk[op].add_argument('--refs', help='the references passed in; default: the files of the pins over the shot')
    tk['add'].add_argument('--link', action='store_true', help='keep a link, not a copy')
    tk['add'].add_argument('--approve', action='store_true')
    pi = group('pin', ('add', 'set', 'remove'), lambda op: None)
    for op in ('add', 'set', 'remove'):
        pi[op].add_argument('name')
        if op != 'remove':
            pi[op].add_argument('--keep', required=op == 'add', help='the aspect to keep; all = the file exactly')
            pi[op].add_argument('--ref', help='a file, URL or take id; default: the approved take of the shot')
            pi[op].add_argument('--from', dest='start', help='a shot id or scene number or name; on a series, a thread')
            pi[op].add_argument('--to', dest='end', help='a shot id or scene number or name')
            pi[op].add_argument('--link', action='store_true', help='keep a link, not a copy')
            pi[op].add_argument('--note', help=note)
    pi['set'].add_argument('--rename')
    ep = group('episode', ('add', 'move', 'set'), lambda op: None if op == 'add' else 'the episode number')
    ep['add'].add_argument('name', nargs='?', default='', help='any title; with none it shows as its number')
    ep['add'].add_argument('--before', help='the episode number it goes in front of')
    ep['move'].add_argument('to', help='the episode number whose place it takes')
    ep['set'].add_argument('--name', help='empty removes it')
    th = group('thread', ('add', 'set', 'remove'), lambda op: None)
    for op in ('add', 'set', 'remove'):
        th[op].add_argument('name')
        if op != 'remove':
            th[op].add_argument('--status', choices=list(THREAD_ICON))
            th[op].add_argument('--episodes', help='the episode numbers it runs through, as in 1,3')
    th['set'].add_argument('--rename')
    cl = sub.add_parser('clean')
    cl.add_argument('story', type=story_path)
    cl.add_argument('--delete', action='store_true', help='remove the files it lists')
    cu = sub.add_parser('cut')
    cu.add_argument('story', type=story_path)
    cu.add_argument('scene', nargs='?', help='a scene number or name: cut only that scene, with the layers carried into it played on from where they had got')
    cu.add_argument('--output')
    cu.add_argument('--size', default='1920x1080', help='an even width and height, as in 1280x720')
    nw = sub.add_parser('new')
    nw.add_argument('title', help='its folder in the stories folder is named from it')
    nw.add_argument('--series', action='store_true', help='a series, from the venue\'s series.md template')
    nw.add_argument('--venue', default='youtube', help='a file in venues/')
    nw.add_argument('--premise', help='the core idea in one sentence')
    nw.add_argument('--audience')
    nw.add_argument('--length', help='the target length, as in "8-12 min"')
    ls = sub.add_parser('list')
    ls.add_argument('root', type=Path, nargs='?', default=STORIES)
    return p


def run(a):
    if a.cmd == 'list':
        return list_root(a.root)
    if a.cmd == 'new':
        return new(a)
    if not a.story.is_dir():
        raise TimelineError(f'no story or series at {a.story}')
    if a.cmd == 'migrate':
        return migrate(a.story)
    if a.cmd in ('scene', 'shot', 'layer', 'take', 'pin', 'episode', 'thread'):
        return run_edit(a)
    if a.cmd == 'clean':
        if is_series(a.story):
            series = read_series(a.story)
            stories = [series] + [writable(e) for e in series['episodes']]
        else:
            stories = [writable(story_at(a.story))]
        return timeline.clean(a.story, stories, a.delete)
    if a.cmd == 'cut':
        story, name, one = writable(story_at(a.story)), 'cut.mp4', None
        if a.scene:
            one = timeline.find_scene(story, a.scene)
            name = f"cut-{one['num']:02d}.mp4"
        target = Path(a.output) if a.output else story['path'] / name
        return '\n'.join([f'cut → {target}'] + save(target, lambda tmp: cut.build(story, tmp, a.size, one)))
    if a.cmd == 'detail':
        return detail(story_at(a.story), a.ref, a.layer)
    if a.cmd == 'compile':
        return compile_script(story_at(a.story), a.output, a.stdout)
    if is_series(a.story):
        s = read_series(a.story)
        eps = s['episodes']
        present = {e['path'].name for e in eps}
        return {'show': lambda: show_series(s), 'sync': lambda: sync_series(s, eps),
                'check': lambda: '\n'.join([f'  {p}' for p in listing_problems('Episode Arc', s, 'folder', present, '')
                                            + timeline.assets_missing({**s, 'scenes': []})]
                                           + [f"ep {e['num']} {e['title']}\n{check(e)}" for e in eps])
                or 'no episodes yet',
                'todo': lambda: '\n'.join(l for e in eps for l in todo(e, f"ep {e['num']}: "))
                or 'no episodes yet'}[a.cmd]()
    s = story_at(a.story)
    parent = a.story.resolve().parent
    if a.cmd == 'sync' and s['num']:
        series = read_series(parent)
        return sync_series(series, [series['episodes'][s['num'] - 1]])
    return {'show': lambda: show_scene(s, timeline.find_scene(s, a.scene)) if a.scene else show_story(s, a.view),
            'sync': lambda: sync_story(writable(s)),
            'check': lambda: check(s),
            'todo': lambda: '\n'.join(todo(s))}[a.cmd]()


def main():
    a = parser().parse_args()
    try:
        print(run(a))
    except (TimelineError, OSError) as e:
        sys.exit(f'storypad: {e}')


if __name__ == '__main__':
    main()
