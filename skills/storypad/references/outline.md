# Outline

## From the notes

1. Read `index.md` (scene table, Notes, its active `Decided:` lines: each one no later line's
   `(replaces: …)` names, Scratchpad), each scene file the scene table lists, and the scene flow
   in `venues/<venue>.md`. For an episode, first run `references/series.md` → **Continuity**'s
   check of the active threads.
2. Follow any order an active `Decided:` line sets. Otherwise group the ideas into scenes in the order the
   audience meets them, each named for what it does in the story, as many as the target length
   carries. Notes empty → the ideas are what the premise needs the audience to see.
3. A scene the scene table already holds keeps its row and file. Add each scene it lacks with
   `storypad.py scene add <story> <name>`, with `--before` the existing scene it comes before. Then
   write into each scene's file, `scenes/<File>` from its row in the scene table, only what it
   lacks: beats for what the audience sees or hears, prep for what must exist before it can be
   made, and `## Script` holding the Scratchpad's words for that scene, else empty.
   - Each prep item names its record as `@name`. A record fits → reuse it. None fits → ask the
     owner what it must be, then `asset add` or `location add <story> <name> --expect <it>`.
   - Place a beat that pays off each `active` thread where the story lands it.
4. Run `storypad.py sync`, then `show <story> --view breakdown`.
5. Reply with the chart, the ideas left out (they stay in Notes), each prep item that blocks
   making a scene, and each active thread still without a pays off.

## Changing scenes

- **Add a scene:** `scene add <story> <name> --before <scene>`. With no place given it goes before
  the scene the venue's flow ends on (Wrapup), else at the end.
- **Remove a scene:** `scene remove <story> <scene>`.
- **Rename a scene:** `scene set <story> <scene> --name <name>`.
- **Change beats, prep or script:** edit the scene file, then `sync`.
- **Mark progress:** check each box the user says is made, then `sync`.

## Shots

- **Lay out the shots:** for each scene, `shot add` one shot per beat the audience sees that no
  shot of the scene shows yet, in beat order, with `--shows` saying what the beat shows. Give `--length` and `--ends` only where the
  ask, the script or the notes state them. Add no layers. Then `show <story>`.
- **Threads on screen:** for each thread a shot's shows line names, `thread set <story> <thread> --on
  <its shots>`; `--heard` where it is only heard. List those in the reply.
- **Where a shot is set:** a scene's frontmatter `location: "@ditch"`; one shot set elsewhere takes
  `shot set <id> --meta location=@<location>`. Name the location, never a variation: the world's moments pick it.
- **What a shot shows:** `shot set <id> --shows "<subject, framing, camera move, action>"`, in the
  user's words when they give them.
- **A transition:** `shot set <id> --ends` on the shot before it.
- **Move a shot:** `shot move <story> <id> <to id>` takes that shot's place; a scene number puts it
  at the scene's end. Moved into another scene, it takes the next id there, and its takes go with
  it.
- **A sound, music, a title, an effect:** `layer add <story> <scene> <name> --from --to`, with
  `--in`/`--out fade <s>` where it fades, and `--file` once its sound or image exists. A title's
  words: `--meta text="<words>"`; with no file the cut draws them. A layer that
  runs on into the next or previous scene ends `open`, and the neighbouring scene gets a layer of
  the same name from or to `open`.
- **Swap or replace a layer** ("swap the music", "a new title"): a layer the scene already has
  (`detail <story> <scene>` lists them) changes with `layer set <story> <scene> <name> --file <file>`,
  and its timing or fades with `--from`, `--to`, `--in`, `--out`. A layer carried across scenes
  keeps one file: one `layer set --file` on any scene of the carry changes it in every scene the
  carry runs through; its timing and fades change in each scene that holds it. Only a layer the
  scene lacks takes `layer add`.
- Each shot and layer command prints the scene's strip and anything that no longer lines up. Show
  the strip; fix what it names.
