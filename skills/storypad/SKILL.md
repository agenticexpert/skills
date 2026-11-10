---
name: storypad
description: Plan a story as plain files and take it to a first cut, tracking how complete it is, its scene order and what's left to do. Brainstorm into notes, outline into scenes with beats and prep, write each scene's script, lay out shots, transitions, sound, music, titles and effects on a timeline, write a prompt per shot for the tool that makes the video, record each shot's takes and the approved one, pin what must stay the same across takes and episodes, render the first cut, refine, reorder, and compile the script; a series tracks its episodes and continuity threads. Use for "/storypad", "make me a video about X", "just pipeline it", "brainstorm / outline / storyboard this video", "show the timeline", "add a dissolve / music / a title", "write the shot prompts", "use this take", "keep this look", "pin this", "cut it together", "plan a series", "write the script", "what's left on the story", "reorder the scenes", "compile the script".
license: MIT
---

# Storypad

Plan a story in plain files and track how complete it is, its scene order and what's left to do.

`scripts/` and `references/` sit in the folder holding this file. `storypad.py` is
`scripts/storypad.py` there; its `--help` lists every command.

## Files

```
agents/storypad/stories/
├── <story>/                    a single piece
│   ├── index.md                frontmatter, premise, scene table, pins, notes, scratchpad, references
│   ├── scenes/<key>.md         one file per scene, named in the scene table's File column
│   ├── assets/                 the files takes, layers and pins keep
│   ├── script.md               written by compile
│   └── cut.mp4                 written by cut
└── <series>/
    ├── series.md               episode arc, continuity threads, pins, recurring elements
    └── ep-<key>/               one story folder per episode, named in the arc's Folder column
```

```markdown
# Intro

## Beats
- [ ] What the audience sees or hears, one per line

## Prep
- [ ] What has to exist before the scene can be made; omit the section when nothing does

## Script
The words, freeform.
```

Check a box once its beat or prep item is made, never before. A scene with every box checked is
done.

A scene's number is its row in the scene table: adding, moving or removing a scene renumbers the
scenes after it, and their shot and take ids follow (scene 2 becomes 3, shot 2a becomes 3a). An
episode's number is its row in the episode arc, and thread episode numbers follow it. Take numbers
and ids from the latest `storypad.py` output. A scene's name is its file's `# ` line, whatever the
user calls it; with none it shows as "Scene 3".

A scene holds shots, each with an id: the scene number and letters, `3a`, `3b`. The letters name the
shot and never change, since its takes are named from them; they don't give its place: a shot added
before `3a` can be `3c`. Every view and table lists shots in their order in the scene. A shot has a line
for what it shows, a length when it is known, and ends `cut`, `match`, `dissolve <s>` or
`fade <s>`; the last shot's ending hands over to the next scene. A take is a made file for a shot,
`3a.1`, `3a.2`; the approved one is `3a.2+`. A layer is anything that runs over the shots: sound,
music, a title, an effect, with its file once there is one. A pin keeps one aspect of a made or
found file (a look, a face, a line, a sound) over a shot, a scene, a run of them, or the whole
story, so every later take holds it; `all` keeps the file exactly. A series pin rides a continuity
thread and holds in every episode the thread lists.

`storypad.py new` and `episode add` start `index.md` and `series.md` from the templates in
`venues/<venue>.md`; use that venue's vocabulary, scene flow and beat codes. The default venue is `youtube`.
A new story or episode starts with the venue's first scenes (Intro, Wrapup) and their beats; `scene add` seeds a
scene named like one of them with its beats.

## Rules

- Write only inside the named story's folder and its series' folder.
- Never make an image, clip or sound. A shot's file comes from the user; a shot with none stays
  open.
- Add, move, rename and remove scenes only with `storypad.py scene`, and episodes only with
  `episode`. Change shots, layers, takes, pins and threads only with `storypad.py shot`, `layer`,
  `take`, `pin` and `thread`. Name a shot in two or three words for what is seen.
- Run `storypad.py sync` after every change to beats, prep or script. Sync writes the status, the
  counts, the scene table in `index.md` and the episode arc in `series.md`.
- Status is how far the story work has got: `brainstorming` (no scenes) → `outlining` (scenes) →
  `refining` (set by refine). Open tasks never change it; with none open the board says `nothing
  open`. A task is an open beat or prep box or a scene with no script; on a shot, no take or no
  length yet, a pick among its takes, or a prompt or approved take marked for review; on a layer,
  no file yet; on the cut, each problem `check` names.
- A series' status is its episode furthest behind. Every command that changes an episode, and its
  `sync`, rewrites the episode arc and status in `series.md`.
- Storypad is a board. It never judges whether a story is ready for anything.
- Add to Notes; never delete or rewrite the user's notes.
- Answer progress, order and what's left from `storypad.py`, run this turn. Show its strips,
  charts and lists in a code block exactly as printed; never draw one by hand.
- A scene named by place ("the second scene", "the last one") is the one at that place in `show`;
  one named in words is the scene whose name fits them; a command takes that name in place of the
  number. Name it back, "2: Yeast at work", before acting on it. Two scenes fit → ask which.
  "The opener" is episode 1 in a series and the first scene in a story.
- A decision the user makes goes as a `Decided:` line in the story's Notes
  (`references/brainstorm.md` step 5); one about a scene or shot they name goes as `--note` on it.
- A command refuses a target that is unclear or in another scene: give the user its reason in
  the story's words and ask which they meant.
- A remove refused for the work it would lose lists that work: show the user the list, and rerun
  with `--force` only on their yes.
- A command refused with `storypad migrate <path>`: run that command, then the refused one again,
  and tell the user the story's files were updated to the current layout.
- Name a shot by its id and name, "3c Digging", and a scene by its number and name.
- Reply in the story's words and the venue's vocabulary. Leave out commands, script names and how
  the files are kept.

## Commands

| Ask | Do |
|---|---|
| New story or series | `references/new.md` |
| "Make me a video about X", "just pipeline it", take it to a cut | `references/pipeline.md` |
| "Keep going", "continue", "what's next" on a started story | `references/pipeline.md` → **Keep going** |
| Brainstorm, explore ideas, "what if" | `references/brainstorm.md` |
| Outline, add or remove a scene, change beats | `references/outline.md` |
| Refine, review the outline, "is this working", "tighten it" | `references/refine.md` |
| Write the script, a scene's words, "draft the narration"; "tighten" naming the script, narration or a scene's words | `references/script.md` |
| Add an episode, continuity, callbacks | `references/series.md` |
| Lay out the shots, storyboard it | `references/outline.md` → **Shots** |
| Add or change a shot, a transition, a sound, music, a title, an effect | `references/outline.md` → **Shots** |
| Swap the music, replace a sound, title or effect | `storypad.py layer set <story> <scene> <name> --file <file>`; `references/outline.md` → **Shots** |
| Keep this, pin this, "same look as before" | `references/pins.md` |
| A prompt for a shot or scene, "write the shot prompts" | `references/pins.md` → **Prompts** |
| A file for a shot, "here's the clip for 3a" | `references/pins.md` → **Takes** |
| "Use this take", approve a take | `storypad.py take approve <story> <take id>`; none of them: `take unapprove` |
| Drop a take, fix its prompt or model | `storypad.py take remove\|set <story> <take id>` |
| Start a take later in its file | `storypad.py take set <story> <take id> --in <seconds>` |
| Cut it together, the first cut, assemble; "cut <scene>" | `storypad.py cut <story> [<scene>]`; name each shot it left black and each layer it left out. "Cut" renders, never deletes: taking a scene out needs "remove" or "delete" |
| Reorder scenes | `storypad.py scene move <story> <scene> <to scene>` |
| Rename a scene | `storypad.py scene set <story> <scene> --name <name>` |
| Move a shot, also into another scene | `storypad.py shot move <story> <shot id> <to shot id or scene>`; name its new id |
| A note on a scene, shot, take, layer or pin | `--note "<text>"` on its `set` command; `detail` shows it, compile and cut leave it out |
| A field of its own on a scene, shot, take, layer, pin, episode or thread (a location, a camera, an owner) | `--meta <key>=<value>` on its `add` or `set` command, the key a lowercase word; `<key>=` removes it; `detail` shows it, compile and cut leave it out |
| Clean up unused files | `storypad.py clean <story>`; show the list, then `clean <story> --delete` on the user's word |
| Show it, the timeline, how it flows | `storypad.py show <story>`; one scene: `show <story> <scene>` |
| The details of a scene, a shot or a layer | `storypad.py detail <story> <scene or shot id> [<layer>]` |
| Where it stands, what's done | `storypad.py show <story> --view breakdown\|table\|gantt` |
| Does the timeline hold together | `storypad.py check <story>` |
| What's left, the to-do list | `storypad.py todo <story>` |
| Compile the script | `storypad.py compile <story>`; name the scenes still without script |
| List stories | `storypad.py list` |
| Open a story | Read its `index.md`, and `series.md` for an episode, then `show` it |

Work on the story the ask names. None named: the story named last in the conversation; none named
yet → the only story; more than one → ask which.

## Changing storypad

- When changing `scripts/`: from this folder, `python3 tests/scenario.py record` before the first
  edit; it prints its results folder. After the change, `python3 tests/scenario.py compare --results
  <that folder>` and `python3 -m unittest tests/test_safety.py`. Each difference compare prints is
  meant or fixed.
- When a behavior no scenario runs needs checking: add its lines to a scenario in
  `tests/scenarios/`, or a new `<name>.sh` there.
