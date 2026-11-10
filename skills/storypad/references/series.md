# Series

## Add an episode

1. `storypad.py episode add <series> [<title>] [--before <episode>]`. The episode starts with the
   venue's first scenes (Intro, Wrapup) and their beats.
2. Fill its arc row's Arc Position from the ask or the episode's place in the run: `opener`,
   `develop`, `pivot`, `climax`, `closer` or `standalone`.

Reorder with `episode move <series> <episode> <to episode>`; rename with
`episode set <series> <episode> --name <title>`.

Work the episode as any story: brainstorm, outline, refine.

## Continuity

- **A thread opens** when the episode leaves the audience something to carry into a later one:
  `storypad.py thread add <series> <name> --episodes <this episode>`.
- **A thread is picked up:** `thread set <series> <name> --episodes <every episode it runs
  through>`, and mark the beat that picks it up `(see <that episode's title>)`.
- **A thread ends or pauses:** `thread set <series> <name> --status resolved` or `dormant`;
  `recurring` for one that never ends. Rename with `--rename`; its pins follow.
- **A thread's look, face, voice or sound to hold:** `storypad.py pin add <series> <name> --keep
  <aspect> --ref <file or link> --from <thread>`; no `--from` holds it in every episode. Each episode
  the thread lists holds it in its shots' prompts.
- Before outlining an episode, list the active threads absent from the last two episodes. The
  outline picks each one up, or the reply names it as still open.
