# New story or series

1. No premise in the ask → ask for the core idea in one sentence first.
2. The ask names a world, or the story shares people, places or events with stories already there →
   that world: `<world>/<title>`. Unsure which world → `storypad.py list` and ask. Otherwise the title
   alone: a new world of the same name holds the story.
3. `storypad.py new "[<world>/]<title as written>" [--series] [--when <moment>] [--venue <venue>]
   --premise "<premise>" [--audience "<audience>"] [--length "<target length>"]`, with the venue,
   audience and length the ask gives; the venue defaults to `youtube`. It makes
   `agents/storypad/stories/<world>/<title in kebab-case>/` from the venue's template, dated today,
   with the venue's first scenes and their beats.
4. Refused as already there → open that story and say so. Refused for the world → name the worlds it
   lists and ask which. Refused for the venue → name the venues it lists and stop.
5. A series: add its episodes with `references/series.md`.

## The timeline

The world's timeline is its moments in order; each story's `when` names the moment it is set at.

- **A story's time** ("this happens after the storm", "a prequel"): the moment exists → `storypad.py
  when <story> <moment>`; none yet → `moment add <world> <name> [--before <moment>]` first. Same
  `when` = same time.
- **A point inside a story** (a place changes from here on): `moment add <world> <name> --story
  <story key> --at <scene or shot>`; it follows that shot's moves.
- **Reorder or rename:** `moment move <world> <name> <to moment>`; `moment set <world> <name>
  --rename <new>` (every `when` and `--from` follows). `moment remove` is refused while anything names
  it: change those first.
- `show <world>` draws the timeline with the stories set at each moment.
