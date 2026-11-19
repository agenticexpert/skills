# Storypad

**A place to plan a story and take it to a rough cut: what's in it, in what order, and what's left
to do.**

A story is plain markdown you can read, edit and version: an `index.md` with the premise, the scene
table, notes and scratchpad, and one file per scene holding its beats, its prep and its script. A
small script reads those files for every count, chart and to-do list, so the progress shown is
always the files' own.

## The flow

- **new**: start a story or a series for a venue (`/storypad new my-video` makes the world `my-video`
  holding it; `new my-video/follow-up` adds one to that world). A new story or episode opens with the
  venue's first and last scenes (Intro and Wrapup on YouTube) and their beats.
- **pipeline**: "make me a video about X" runs outline, shots, a prompt per shot, takes and the cut
  in one go. Storypad never makes media: the prompts are for the tool that makes the video, and
  the run stops at them until the user gives the files. On a story that already has scenes and
  shots it adds only what is missing. It approves takes only when told to, and otherwise lists
  them for review.
- **brainstorm**: ideas appended to the notes as dated blocks; nothing is fixed yet.
- **outline**: the notes become scenes, one file each, with beats, prep and script.
- **script**: each scene's words, written by the owner or drafted by an agent into the scene file;
  storypad never records the narration.
- **refine**: review the outline for audience, pacing, story and venue. A question gets the review;
  an ask to refine applies the fixes.
- **shots**: each scene's shots, transitions and layers (sound, music, titles, effects), drawn as a
  strip at story, scene and shot zoom. A layer can carry on across scenes, such as one piece of
  music; the whole run shares one file, and swapping it on any scene swaps it for the run.
- **takes and pins**: the files the user gives for each shot, one approved; a pin keeps one aspect of a
  file over a shot, a scene or the story, so every later take holds it.
- **cut**: a rough cut, like an animatic, for checking flow and timing: `cut.mp4` from the approved
  takes and the layer files, with titles drawn from their text, made with ffmpeg.
- **reorder**: a scene's number is its place, so moving, adding or removing one renumbers the
  scenes after it and their shot ids follow; names and files stay. Removing a scene or shot that
  holds a script, ticked beats or takes needs `--force`.
- **show / todo**: the story strip, a breakdown, table or gantt chart of where it stands, and
  the tasks still open on each scene, shot, layer, thread, record and the cut, in story order; one
  scene or a run of them, or one kind with `--only`. A shot with no file
  or length and a layer with no file are open tasks like any other; with none open the board says
  nothing open. The status says only how far the story work has got: brainstorming, outlining,
  refining.
- **worlds**: every story sits in a world, a folder whose `world.md` holds what its stories share:
  actors, props and locations, every thread and event, pins on shared things, and a timeline of
  moments. Each story says when it happens by naming a moment, so a prequel added later still gets
  the right version of a place. A story keeps only its own: scenes, shots, takes, script, layers and
  the cut. `show <world>` draws the timeline and lists its stories.
- **threads and events**: what the audience carries from one moment to a later one, kept in the
  world, drawn three ways: a thread graph, a small view of the whole shape, and an events grid of
  what is seen, heard, unseen or carried at each shot. A story's views show the threads it touches;
  the world's show all. Hanging threads and broken links are open tasks.
- **assets and locations**: a prep line names what it waits on as `@name`; one record each, in the
  world, holds its expectation, its state (needed, made, approved) and its file. A location's
  variations start at a moment of the world's timeline, so each shot knows which version of the place
  it uses. Takes, pins and layers point at the record instead of copying the file. A file arriving
  never ticks a box.
- **compile**: every scene's script stitched into one `script.md`.
- **series**: episodes as story folders in the order the audience watches them; their threads,
  records and pins are the world's.
- **your own fields**: `--meta key=value` on any add or set keeps a field storypad has no flag for,
  such as a location or a camera.

## Stories from an older storypad

Scene files named `01 - Intro.md`, episode folders named `ep-01-start`, and a story or series in no
world (or keeping its own threads, records or shared pins) are the older layout. `storypad.py migrate
<story or series>` converts them, wrapping one in a world of its own name, or `--into <world>` moving
it into a world already there; a name the world already has is refused, never merged. It writes every
new file before it deletes any old one; every other command refuses an older layout until then.

## Venues

A venue is one markdown file in `venues/`: its vocabulary, default scene flow, beat types,
conventions and templates. YouTube ships; a new venue is a new file modeled on `youtube.md`.

## When to use

Planning any piece that runs in sequence and has to be made: a video or a series, a talk, a course.
Triggers: "/storypad", "make me a video about", "brainstorm", "outline", "storyboard", "plan a
series", "what's left".

## Installation

```bash
npx skills add agenticexpert/skills/storypad
```

Part of [Agentic Expert](../../README.md). Built by **Shawn Bullock**,
[agenticexpert.ai](https://agenticexpert.ai).

## License

MIT.
