# YouTube

## Vocabulary

| Storypad | YouTube | Means |
|---|---|---|
| story | video | one piece |
| scene | section | one phase of the video |
| beat | beat, moment | one thing the viewer sees or hears |
| prep | prep | what must be built, recorded or set up before filming |
| series | series, playlist | related videos |
| episode | episode | one video in a series |
| hook | hook | the opening seconds that hold the viewer |
| callback | callback | a reference to an earlier video |
| CTA | call to action | subscribe, comment, a link |

## Scene flow

`intro → content scenes → wrapup`. Name each scene for what it covers.

- **Intro:** the hook, the payoff shown first, what the video covers.
- **Content scenes:** one per idea the video delivers, in the order the viewer needs them.
- **Wrapup:** the recap, the viewer's next step, the CTA.

## Beat codes

Start a beat with a code when it fixes the shot: `TH` talking head, `BR` b-roll, `SS` screen
share, `DM` demo, `IV` interview, `MN` montage, `AN` animation. Transitions and text overlays go
on the timeline as shot endings and layers.

## Conventions

- The intro raises a question or shows the payoff within the first seconds.
- A pattern interrupt (a cut, a demo, a change of shot) breaks every long stretch of one shot.
- The CTA follows from the video.
- One moment in the video makes the thumbnail.
- The premise matches what the audience searches for.

## index.md template

```markdown
---
venue: youtube
type: single
status: brainstorming
created: {date}
updated: {date}
premise: ""
target-length: ""
audience: ""
tags: []
---

# {Title}

## Premise

{The core idea in one sentence}

## Scenes

## Notes

## Scratchpad

## References
```

`## Scratchpad` holds rough lines until they belong to a scene.

## First scenes

Intro and Wrapup start with these beats:

```markdown
# Intro

## Beats
- [ ] Hook
- [ ] Show the payoff
- [ ] What the video covers

## Script
```

```markdown
# Wrapup

## Beats
- [ ] Recap
- [ ] The viewer's next step
- [ ] CTA

## Script
```

## series.md template

```markdown
---
venue: youtube
type: series
status: brainstorming
created: {date}
updated: {date}
series-name: ""
premise: ""
cadence: ""
target-episodes: null
tags: []
---

# {Series Name}

## Premise

{What the series is about}

## Episode Arc

| Ep  | Title | Folder | Status | Arc Position | Premise |
|-----|-------|--------|--------|--------------|---------|
```

End each episode on an open question or tease, keep it as an `active` thread of the world
(`thread add <series> <name> --episodes N`), and pick it up in the next episode's hook.
