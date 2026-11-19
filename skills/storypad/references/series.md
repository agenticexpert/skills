# Series

A series is the order the audience watches its episodes. Its threads, events, assets, locations and
pins are its world's; the episodes' time is each one's `when` on the world's timeline, which can differ
from the watching order.

## Add an episode

1. `storypad.py episode add <series> [<title>] [--before <episode>]`. The episode starts with the
   venue's first scenes (Intro, Wrapup) and their beats.
2. Fill its arc row's Arc Position from the ask or the episode's place in the run: `opener`,
   `develop`, `pivot`, `climax`, `closer` or `standalone`.
3. The ask places it in the world's time (a flashback, "before episode 1") → `when <series>/ep-<key>
   <moment>` (`references/new.md` → **The timeline**).

Reorder with `episode move <series> <episode> <to episode>`; rename with
`episode set <series> <episode> --name <title>`.

Work the episode as any story: brainstorm, outline, refine.

## Continuity

- **A thread opens** when the episode leaves the audience something to carry into a later one:
  `storypad.py thread add <series> <name> --episodes <this episode>`.
- **A thread is picked up:** `thread set <series> <name> --episodes <every episode it runs
  through>`, and mark the beat that picks it up `(see <that episode's title>)`.
- **A thread ends or pauses:** `thread set <series> <name> --status resolved` or `dormant`;
  `recurring` for one that never ends. Rename with `--rename`; its pins and every story's events and
  links on it follow.
- **An event** goes on an episode (`event add <series>/ep-<key> …`) or the world; `event set|remove
  <series> "<thread>: <event>"` reaches it from the series.
- **A thread's look, face, voice or sound to hold:** `storypad.py pin add <series> <name> --keep
  <aspect> --ref <file or link> --from <thread>`; it holds over the thread's shots in each story. With
  no `--from` it holds over every episode of the series, and no other story.
- Before outlining an episode, list the active threads absent from the last two episodes. The
  outline picks each one up, or the reply names it as still open.

## Recurring elements

A recurring element (a catchphrase, a segment, a character, a visual) is an asset of the world:
`asset add <series> <name> --expect <it>`.

- **What uses it:** `storypad.py detail <series> @<name>`: its shots, prep, takes, pins and variations
  in every story of the world, each line `<story key>:`.
- **Its assets and locations:** `show <world> --view assets|locations`; one episode's:
  `show <series>/ep-<key> --view assets|locations`.
- **Does the series hold together:** `storypad.py check <series>`: the episode arc, then each
  episode's check; the records themselves: `check <world>`.
- **What is left on it:** `storypad.py todo <series>`: each episode's tasks; the world's open records:
  `todo <world>`.
