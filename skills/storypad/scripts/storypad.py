#!/usr/bin/env python3
"""Storypad state, read from the files.

  storypad.py show <story> [<scene>] [--view strip|breakdown|table|gantt]
  storypad.py show <story|series> [<scene> | <from>-<to>] --view threads|small|events [--thread T[,T]]
  storypad.py show <story> --view assets|locations
  storypad.py detail <story> <scene or shot id> [<layer>]
  storypad.py detail <story|series|world> @<name>
  storypad.py detail <story|series|world> --thread <name>
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
  storypad.py pin add <story|series|world> <name> --keep K [--ref FILE|URL|TAKE] [--from T] [--to T] [--link]
                      [--note T]
  storypad.py pin set <story|series|world> <name> [--rename N] [--keep K] [--ref FILE|URL|TAKE] [--from T]
                      [--to T] [--link] [--note T]
  storypad.py pin remove <story|series|world> <name>
  storypad.py episode add <series> [<title>] [--before N]
  storypad.py episode move <series> <N> <to N>
  storypad.py episode set <series> <N> [--name <title>]
  storypad.py thread add <story|series|world> <name> [--status S] [--on <shots>] [--heard <shots>] [--episodes N,N]
  storypad.py thread set <story|series|world> <name> [--rename N] [--status S] [--on <shots>] [--heard <shots>]
                         [--episodes N,N]
  storypad.py thread remove <story|series|world> <name> [--force]
  storypad.py event add <story|world> <thread> <event> --at REF [--kind K] [--seen on|off|heard] [--note T]
  storypad.py event set <story|series|world> "<thread>: <event>" [--rename N] [--at REF] [--kind K] [--seen S]
                        [--note T]
  storypad.py event remove <story|series|world> "<thread>: <event>"
  storypad.py event link <story|series|world> "<thread>: <event>" "<thread>: <event>" --effect <word>
  storypad.py event unlink <story|series|world> "<thread>: <event>" "<thread>: <event>"
  storypad.py asset add <story|series|world> <name> --expect E [--state S] [--file F [--link]] [--note T]
  storypad.py asset set <story|series|world> <name> [--rename N] [--expect E] [--state S] [--file F [--link]]
                        [--note T]
  storypad.py asset remove <story|series|world> <name> [--force]
  storypad.py location add <story|series|world> <name> --expect E [--look L] [--of <location> --from <moment>]
                           [--state S] [--file F [--link]] [--note T]
  storypad.py location set <story|series|world> <name> [--rename N] [--expect E] [--look L] [--from <moment>]
                           [--state S] [--file F [--link]] [--note T]
  storypad.py location remove <story|series|world> <name> [--force]
  storypad.py cut <story> [<scene>] [--output PATH] [--size WxH]
  storypad.py clean <story|series|world> [--delete]
  storypad.py check <story|series|world>
  storypad.py todo <story> [<scene> | <from>-<to>] [--only beats|prep|script|shots|layers|assets|locations|threads]
  storypad.py todo <series|world> [--only …]
  storypad.py sync <story>
  storypad.py compile <story> [--output PATH | --stdout]
  storypad.py migrate <story|series> [--into <world>]
  storypad.py list [<root>]
  storypad.py show <world> [--view assets|locations|threads|small|events] [--thread T[,T]]
  storypad.py moment add <world> <name> [--before <moment>] [--story <story> --at REF] [--note T]
  storypad.py moment set <world> <name> [--rename N] [--story <story>] [--at REF] [--note T]
  storypad.py moment move <world> <name> <to moment>
  storypad.py moment remove <world> <name>
  storypad.py when <story> <moment>                          ("" clears it)
  storypad.py new [<world>/]<title> [--series] [--when <moment>] [--venue V] [--premise P] [--audience A]
                  [--length L]
  storypad.py version save <story|series|world> <name> [--note T] [--film F] [--from DIR]
  storypad.py version list <story|series|world>
  storypad.py version show <story|series|world> <ref> [<file>]
  storypad.py version diff <story|series|world> <ref> [<ref>]
  storypad.py version restore <story|series|world> <ref>

Every add and set also takes --meta key=value, repeatable; key= removes it. On a shot, layer,
take, pin or thread it is a column of its own; on a scene or an episode, a frontmatter key.

A world is a folder holding world.md and its stories and series: <world>/<story>/ and
<world>/<series>/ep-<key>/. new <title> makes a world of that name holding the story; new
<world>/<title> adds one to a world already there. A story is a folder holding index.md and scenes/;
a series is a folder holding series.md and ep-<key>/ story folders. show, todo, check, sync and clean
take either. A story or series in no world, or keeping its own assets or locations, is the older layout:
every command but migrate refuses it. migrate wraps one in no world in a world of its own name,
<path>/<name>/; --into moves it into a world already there instead. Its assets and locations move to
world.md; a name the world already has is never merged: migrate lists each and refuses until one side is
renamed.

A world has a timeline: its moments, in order, in world.md. A moment falls between stories, or with
--story and --at at a scene or shot of one story or episode (named by its folder from the world: film,
saga/ep-first), and follows that scene or shot's moves. A story's when (when, new --when) is the moment
it is set at; stories with the same when happen at the same time. A moment's rename reaches every when
and variation naming it; its remove is refused while one does. show <world> draws the timeline.

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

A pin keeps one aspect (--keep; "all" keeps the file exactly) of its --ref. A story's own pin, kept in
its index.md, holds over a shot, a scene, or a run from one to another (T is a shot id or scene number;
neither = the whole story, as a colour grade). A pin on a shared thing is the world's, kept in world.md:
--from a series holds it over every episode of that series (one added on a series with no --from or
--to is from it), --from a thread over the thread's On screen in each story (the whole story where the
thread runs with no On screen there), --from @<asset or location> over the scenes and shots using it,
and one added on the world with no --from over every story. pin set and remove on a story reach its
own pin by that name, else the world's; a pin's name is one in the world. With no --ref, a pin on one
shot keeps its approved take; a world's pin keeps a file, a link or @name. A file is copied into the
story's or the world's assets/ unless already there; --link keeps a link instead.

A note on a scene, shot, take, layer or pin is never part of the content: compile and cut leave
it out, and detail shows it. Names and values stay on one line, without |.

A thread is anything the audience carries from one moment to a later one. Threads and events are the
world's, kept in world.md, and thread and event commands on a story, series or world change them. On a
story, --on lists the shots or scenes where it is seen and --heard where it is only heard (3a, 2,
3c-4c), kept in world.md under the story's key (film: 3a; saga/ep-first: 2). On a series, --episodes
lists the episodes it runs through. An event is one moment on a thread, its <thread>: <event> one name
in the world: added on a story or episode, --at is before, after, a scene or a shot id; added on the
world, before, after or a moment; never on a series. --kind is set up, beat, change or pays off (empty:
the first is set up, the rest beat); --seen is on, off or heard (empty: on). A link is one event acting
on another, in any story, named by its --effect word. A thread its events in the world pay off is
resolved. Every thread and event command prints the thread's path. A thread with events, or a scene or
shot holding events or moments, is refused removal without --force. show --view threads|small|events
draws the thread graph, the small view and the events grid of the threads with a mark in the story;
under 40 columns, the list form. On a series the columns are episodes: an episode number draws that
episode's own view, <from>-<to> a run of episodes. On a world they are its moments, every thread drawn.
A thread's rename reaches every event, link and pin naming it.

An asset (a person cast, a prop, a recording) or a location (a set, a place) is a record of the world, kept
in world.md with its file in the world's assets/, that a prep line, a scene's location: field or a shot's
--meta location= of any of its stories names as @name; --expect is what it must be. asset and location
commands on a story, series or world all change the world's record.
A location with --of and --from is a variation, @<location>/<name>, started by a moment: used by its
location's shots from the moment's shot on in the story it falls in, from the start in every story whose
when is that moment or later, and nowhere else. A state is needed, made or approved; a file makes it made, and it
stays open in todo until approved. No command ticks a prep box. --file @name on a take or layer,
--ref @name and --from @<location> on a pin point at the record's file. --rename rewrites every @name in
every story of the world; remove is refused while anything names the record, and --force strips the @name
and removes with it each pin starting from it, naming them, never leaving one wider.
detail @name reads it through every story. A story's assets and locations views list the records it uses,
show <world> --view assets|locations every one; check and todo on a world name the records' problems and
open records, on a story those it uses.

Removing a scene that has a script, ticked beats or takes, or a shot that has takes, is refused
without --force, and the refusal lists what would be lost. While a scene's timeline can't be read,
every command that writes to its story, clean and cut refuse and name it; show, detail, todo,
check and compile still run.

A story's status is how far its story work has got: brainstorming with no scenes, then outlining,
then refining once set in index.md; open tasks never change it. todo lists the open tasks: each
open beat and prep item and each scene with no script; each shot with no take or no length, each
shot with takes but none approved, and each prompt (--meta prompt=) or approved take marked for
review: its shows line, its scene's script, a pin over it or a record it uses changed since it was
written or approved; shot set --reviewed clears that. One kept before storypad marked them takes its mark,
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

Every command but migrate that changes a story's, series' or world's text files keeps the state it leaves
them in as a version, versions/<number>/ in that folder, and first the state it found when they were
changed outside storypad since. Text is each .md outside assets/, takes/ and build/; every other file is listed by path and
size, never copied. A story's threads, events, assets, locations, world pins and moments are in world.md:
their versions are the world's. version save names the files now, or with --from those of a folder laid out
the same, with a note and the film they made. A ref is a version's name or number. diff compares a ref with
a second one, else with the files now; restore puts a ref's text files back and removes those it doesn't
keep, the state before kept first. show, todo, check, compile, clean and cut never read versions/.
"""

import argparse
import sys
from pathlib import Path

import cut
import timeline
import versions
from assets import STATES, detail_record, find, made_reply
from continuity import (KINDS, SEEN, THREAD_ICON, detail_thread, list_form, series_story, series_view, world_story,
    world_view)
from episodes import (episode_add, episode_move, episode_set, is_series, picked_episodes, series_check, series_new,
    series_todo, show_series, sync_series)
from migrate import migrate
from scenes import (DRAWN, ONLY, RECORDS, VIEWS, check, compile_script, detail, picked, save_story,
    scene_add, scene_move, scene_remove, scene_set, show_scene, show_story, story_new, sync_story, todo, window,
    writable)
from storyfile import TimelineError, same, save
from venues import started
from world import (check_world, docs_of, in_world, is_world, list_root, new_place, save_continuity, save_moment,
    save_pin, save_record, save_world, series_at, set_at, set_when, show_world, story_at, story_changed, todo_world,
    world_at, world_doc, world_new)


def with_problems(out, story):
    found = timeline.problems(story.get('scenes', [])) + timeline.assets_missing(story)
    return out + ('\n\n' + '\n'.join(f'  {p}' for p in found) if found else '')


def record_reply(a, world, docs, ref, was, gone):
    """After an asset or location command: the change of state with the boxes it lets the owner tick,
    else the record; after a remove, the world's records left and each pin removed with it."""
    if a.op == 'remove':
        out = RECORDS['assets' if a.cmd == 'asset' else 'locations'](world, docs)
        return out + ''.join(f'\n  removed the pin {n}: it started from @{ref}' for n in gone)
    return made_reply(world, docs, ref, was) if find(world, ref)['state'] != was else detail_record(world, docs, ref)


def run_edit(a):
    if a.cmd in ('asset', 'location'):
        return record_reply(a, *save_record(a.story, a))
    if a.cmd in ('thread', 'event'):
        thread = save_continuity(a.story, a)
        if thread is None:
            return f'  removed {a.name}'
        return '\n'.join(list_form(world_story(world_doc(a.story)) if is_world(a.story) else
                                    series_story(series_at(a.story)) if is_series(a.story) else story_at(a.story), thread))
    if a.cmd == 'pin':
        return pin_reply(a)
    if a.cmd == 'episode':
        series = series_at(a.story)
        {'add': lambda: episode_add(series, a.name, a.before, a.meta),
         'move': lambda: episode_move(series, a.target, a.to),
         'set': lambda: episode_set(series, a.target, a.name, a.meta)}[a.op]()
        return show_series(series_at(a.story))
    story = writable(story_at(a.story))
    if a.cmd == 'scene':
        gone = {'add': lambda: scene_add(story, a.name, a.before, a.meta),
                'move': lambda: scene_move(story, a.target, a.to),
                'set': lambda: scene_set(story, a.target, a.name, a.note, a.meta),
                'remove': lambda: scene_remove(story, a.target, a.force)}[a.op]()
        save_story(story, gone or ())
        story_changed(story)
        story = story_at(a.story)
        return with_problems(show_story(story, 'strip'), story)
    changed = {'shot': timeline.edit_shot, 'layer': timeline.edit_layer, 'take': timeline.edit_take}[a.cmd](story, a)
    for s in changed:
        s['dirty'] = True
    save_story(story)
    story_changed(story)
    story = story_at(a.story)
    if a.cmd == 'take':
        return with_problems(detail(story, a.target.split('.')[0], None), story)
    return with_problems(show_scene(story, timeline.find_scene(story, changed[-1]['num'])), story)


def pin_reply(a):
    """pin add|set|remove, written. From a story: its strip and the scenes the pin covers there; from a series or
    world: the world's pins."""
    save_pin(a.story, a)
    if is_world(a.story) or is_series(a.story):
        world = world_at(a.story)
        lines = ['  Pins'] + (timeline.world_pin_lines(world) or ['  none yet'])
        found = [p for p in timeline.assets_missing(world) if p.startswith('pin ')]
        return '\n'.join(lines + ([''] + [f'  {p}' for p in found] if found else []))
    story = story_at(a.story)
    lines = [show_story(story, 'strip')]
    pin = next((p for p in story['pins'] + story['world_pins'] if same(p['name'], getattr(a, 'rename', None) or a.name)),
               None)
    covered = [s for s in story['scenes'] if pin and pin['from'] and not pin['broken']
               and str(s['num']) in timeline.covers(pin, story['scenes'])]
    return with_problems('\n'.join(lines + [''] + [show_scene(story, s) for s in covered] if covered else lines), story)


STORIES = Path('agents/storypad/stories')


def new(a):
    """A new story or series from its venue's template, in the world `<world>/<title>` names, else in a new
    world of its own name."""
    if a.series and a.when:
        raise TimelineError("a series has no when; each of its episodes has its own, set with when")
    world, fresh, path, title, when = new_place(STORIES, a.title, a.when)
    text = started(a.venue, 'series.md' if a.series else 'index.md', title, a.premise,
                   {'series-name': title} if a.series else {'audience': a.audience, 'target-length': a.length,
                                                            'when': when})
    if fresh:
        world_new(world, title)
    made = f'new world → {world}\n' if fresh else ''
    if a.series:
        series_new(path, text)
        return f'{made}new series → {path}\n' + show_series(series_at(path))
    story_new(path, text)
    return f'{made}new story → {path}\n' + show_story(story_at(path), 'strip')


def story_path(arg):
    path = Path(arg)
    return path if path.is_dir() or not (STORIES / path).is_dir() else STORIES / path


def parser():
    p = argparse.ArgumentParser(prog='storypad', description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('show', 'todo', 'sync', 'compile', 'check', 'migrate'):
        sub.add_parser(name).add_argument('story', type=story_path)
    sub.choices['migrate'].add_argument('--into', type=story_path, help='a world already there to move a story or '
                                                                         'series in no world into')
    sub.choices['show'].add_argument('scene', nargs='?', help='a scene number or name, drawn as its strip; with '
                                     '--view threads|small|events, a scene to zoom in on or a run <from>-<to>; on '
                                     'a series, an episode or a run of them')
    sub.choices['show'].add_argument('--view', choices=['strip', *VIEWS, *DRAWN, *RECORDS], default='strip')
    sub.choices['show'].add_argument('--thread', help='the threads to draw, by name: T[,T]')
    sub.choices['todo'].add_argument('scene', nargs='?', help='a scene number or name, or a run <from>-<to>: its '
                                     'tasks and the open records it uses')
    sub.choices['todo'].add_argument('--only', choices=ONLY, help='keep one kind of task')
    sub.choices['compile'].add_argument('--output')
    sub.choices['compile'].add_argument('--stdout', action='store_true')
    d = sub.add_parser('detail')
    d.add_argument('story', type=story_path)
    d.add_argument('ref', nargs='?', help='a scene number or name, a shot id, or @<asset or location>')
    d.add_argument('layer', nargs='?', help='a layer of that scene')
    d.add_argument('--thread', help="a thread's path: its events, places and links")

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
            pi[op].add_argument('--ref', help='a file, URL, @name or take id; default: the approved take of the shot')
            pi[op].add_argument('--from', dest='start', help='a shot id or scene number or name; or a series, a '
                                                            "thread or @<asset or location>, a pin of the world")
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
            th[op].add_argument('--on', help='on a story: the shots and scenes where it is seen, as in 1a, 3c-4c')
            th[op].add_argument('--heard', help='on a story: where it is heard but not seen, in the same form')
            th[op].add_argument('--episodes', help='on a series: the episode numbers it runs through, as in 1,3')
    th['add'].set_defaults(rename=None)
    th['set'].add_argument('--rename')
    th['remove'].add_argument('--force', action='store_true', help="remove it with its events, a series' in every "
                                                                   'episode too')
    th['remove'].set_defaults(on=None, heard=None, episodes=None)
    ev = group('event', ('add', 'set', 'remove', 'link', 'unlink'),
               lambda op: None if op == 'add' else 'the event, as "<thread>: <event>"')
    ev['add'].add_argument('thread')
    ev['add'].add_argument('event', help='two or three words, unique within its thread')
    ev['add'].add_argument('--at', required=True, help='before, after, a scene or a shot id; on a series: before, '
                                                      'an episode number or after <episode>')
    for op in ('add', 'set'):
        ev[op].add_argument('--kind', choices=KINDS)
        ev[op].add_argument('--seen', choices=list(SEEN))
        ev[op].add_argument('--note', help=note)
    ev['set'].add_argument('--at')
    ev['set'].add_argument('--rename')
    for op in ('link', 'unlink'):
        ev[op].add_argument('to', help='the event it acts on, as "<thread>: <event>"')
    ev['link'].add_argument('--effect', required=True, help='one word for what it does: motive, raises, pays off, tells')
    for cmd in ('asset', 'location'):
        rc = group(cmd, ('add', 'set', 'remove'), lambda op: None)
        for op in ('add', 'set', 'remove'):
            rc[op].add_argument('name', help='lowercase, one to three words joined by -' if op == 'add' else
                                'its name; a variation as <location>/<name>')
            if op != 'remove':
                rc[op].add_argument('--expect', required=op == 'add', help='what it must be, in your words')
                rc[op].add_argument('--state', choices=STATES)
                rc[op].add_argument('--file', help='its file, kept in assets/')
                rc[op].add_argument('--link', action='store_true', help='keep a link, not a copy')
                rc[op].add_argument('--note', help=note)
                if cmd == 'location':
                    rc[op].add_argument('--look', help='what holds in every scene set there; on a variation, what '
                                                       'differs')
                    rc[op].add_argument('--from', dest='start', help="a variation: the moment of the world's "
                                                                    'timeline that starts it')
        if cmd == 'location':
            rc['add'].add_argument('--of', help='a variation: the location it changes')
        rc['set'].add_argument('--rename')
        rc['remove'].add_argument('--force', action='store_true', help='remove it and strip its @name everywhere')
    cl = sub.add_parser('clean')
    cl.add_argument('story', type=story_path)
    cl.add_argument('--delete', action='store_true', help='remove the files it lists')
    cu = sub.add_parser('cut')
    cu.add_argument('story', type=story_path)
    cu.add_argument('scene', nargs='?', help='a scene number or name: cut only that scene, with the layers carried into it played on from where they had got')
    cu.add_argument('--output')
    cu.add_argument('--size', default='1920x1080', help='an even width and height, as in 1280x720')
    nw = sub.add_parser('new')
    nw.add_argument('title', help='<world>/<title> adds it to that world; a bare title makes a world of its name '
                                  'holding it; folders are named from them')
    nw.add_argument('--series', action='store_true', help='a series, from the venue\'s series.md template')
    nw.add_argument('--when', help="the moment of the world's timeline the story is set at")
    nw.add_argument('--venue', default='youtube', help='a file in venues/')
    nw.add_argument('--premise', help='the core idea in one sentence')
    nw.add_argument('--audience')
    nw.add_argument('--length', help='the target length, as in "8-12 min"')
    mo = group('moment', ('add', 'set', 'move', 'remove'), lambda op: None)
    for op in ('add', 'set', 'move', 'remove'):
        mo[op].add_argument('name')
        if op in ('add', 'set'):
            mo[op].add_argument('--story', dest='story_key', help='the story or episode it falls in, as film or '
                                                                  'saga/ep-first; empty: between stories')
            mo[op].add_argument('--at', help='the scene or shot of that story it falls at')
            mo[op].add_argument('--note', help=note)
    mo['add'].add_argument('--before', help='the moment it goes in front of; default: the end')
    mo['set'].add_argument('--rename')
    mo['move'].add_argument('to', help='the moment whose place it takes')
    wh = sub.add_parser('when')
    wh.add_argument('story', type=story_path)
    wh.add_argument('moment', help='the moment of its world\'s timeline the story is set at; "" clears it')
    ve = group('version', ('save', 'list', 'show', 'diff', 'restore'),
               lambda op: None if op == 'list' else 'a name for it, as v6' if op == 'save' else
               "a version's name or number")
    ve['save'].add_argument('--note', help='what it is, in your words')
    ve['save'].add_argument('--film', help='the film it made')
    ve['save'].add_argument('--from', dest='source', type=Path, help='a folder laid out like the story, series or '
                                                                     'world whose text files it keeps; default: its own')
    ve['show'].add_argument('file', nargs='?', help='one of its text files, as scenes/<key>.md')
    ve['diff'].add_argument('to', nargs='?', help='a second version; default: the files now')
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
    if a.cmd == 'version':
        return {'save': lambda: versions.save_version(a.story, a.target, a.note, a.film, a.source),
                'list': lambda: versions.version_list(a.story),
                'show': lambda: versions.show_version(a.story, a.target, a.file),
                'diff': lambda: versions.diff_versions(a.story, a.target, a.to),
                'restore': lambda: versions.restore_version(a.story, a.target)}[a.op]()
    if a.cmd == 'migrate':
        return migrate(a.story, a.into)
    if a.cmd == 'detail' and is_world(a.story) and a.thread:
        return detail_thread(world_story(world_doc(a.story)), a.thread)
    if a.cmd == 'detail' and (a.ref or '').strip().startswith('@'):
        world = world_at(in_world(a.story) if not is_world(a.story) else a.story)
        return detail_record(world, docs_of(world), a.ref)
    if is_world(a.story):
        if a.cmd == 'show':
            world = world_doc(a.story)
            if a.view in RECORDS:
                return RECORDS[a.view](world, docs_of(world))
            return world_view(world, set_at(world), a.view, window(), a.thread) if a.view in DRAWN else show_world(a.story)
        if a.cmd == 'moment':
            return save_moment(world_doc(a.story), a)
        if a.cmd in ('asset', 'location', 'thread', 'event', 'pin'):
            return run_edit(a)
        if a.cmd in ('check', 'todo', 'clean'):
            return {'check': lambda: check_world(a.story), 'todo': lambda: todo_world(a.story, a.only),
                    'clean': lambda: timeline.clean(a.story, [world_doc(a.story)], a.delete)}[a.cmd]()
        raise TimelineError(f'{a.story} is a world; name a story or series in it, as {a.story}/<story>')
    if a.cmd == 'moment':
        raise TimelineError(f'{a.story} is not a world; a moment goes on the timeline of a world')
    in_world(a.story)
    if a.cmd == 'when':
        return set_when(a.story, a.moment)
    if a.cmd in ('scene', 'shot', 'layer', 'take', 'pin', 'episode', 'thread', 'event', 'asset', 'location'):
        return run_edit(a)
    if a.cmd == 'clean':
        if is_series(a.story):
            series = series_at(a.story)
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
        if not (a.ref or a.thread):
            raise TimelineError('name a scene, a shot, an @asset or location, or --thread <name>')
        if is_series(a.story):
            if a.thread:
                return detail_thread(series_story(series_at(a.story)), a.thread)
            raise TimelineError('on a series, detail takes @<asset or location> or --thread <name>; a scene or '
                                'shot is in its episode')
        return detail(story_at(a.story), a.ref, a.layer, a.thread)
    if a.cmd == 'compile':
        return compile_script(story_at(a.story), a.output, a.stdout)
    if is_series(a.story):
        s = series_at(a.story)
        if a.cmd == 'show' and a.view in RECORDS:
            raise TimelineError(f"a series is only its episodes' watching order and keeps no {a.view}; show "
                                f"{a.story.parent} --view {a.view} lists the world's, show {a.story}/ep-<key> --view "
                                f'{a.view} the ones an episode uses')
        if a.cmd == 'show' and a.view in DRAWN:
            pick = picked_episodes(s, a.scene) if a.scene else None
            if pick and '-' not in a.scene:
                return show_story(pick[0], a.view, None, a.thread)
            return series_view(s, a.view, window(), pick, a.thread)
        if a.cmd == 'sync':
            out = sync_series(s, s['episodes'])
            save_world(s['world'])
            return out
        return {'show': lambda: show_series(s),
                'check': lambda: series_check(s), 'todo': lambda: series_todo(s, a.only)}[a.cmd]()
    s = story_at(a.story)
    parent = a.story.resolve().parent
    if a.cmd == 'sync' and s['num']:
        series = series_at(parent)
        out = sync_series(series, [series['episodes'][s['num'] - 1]])
        save_world(series['world'])
        return out
    if a.cmd == 'sync':
        out = sync_story(writable(s))
        story_changed(s)
        return out
    return {'show': lambda: show_story(s, a.view, a.scene, a.thread) if a.view in (*DRAWN, *RECORDS) or not a.scene
            else show_scene(s, timeline.find_scene(s, a.scene)),
            'check': lambda: check(s),
            'todo': lambda: '\n'.join(todo(s, scenes=picked(s, a.scene) if a.scene else None, only=a.only))}[a.cmd]()


def main():
    a = parser().parse_args()
    if a.cmd != 'migrate':
        versions.start(sys.argv[1:])
    try:
        try:
            print(run(a))
        finally:
            versions.finish()
    except (TimelineError, OSError) as e:
        sys.exit(f'storypad: {e}')


if __name__ == '__main__':
    main()
