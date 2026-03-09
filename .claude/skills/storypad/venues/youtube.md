# YouTube Venue Plugin

Venue configuration for YouTube video and series sketches.


## Terminology Mapping

| Storypad.Term   | YouTube Term      | Notes                                      |
|---------------|-------------------|--------------------------------------------|
| sketch        | video             | Single content piece                       |
| section       | section           | Major narrative phase of a video           |
| beat          | beat/moment       | Specific item within a section             |
| prep          | prep/dependency   | Something to build/prepare before filming  |
| series        | series/playlist   | Collection of related videos               |
| episode       | episode/video     | Single entry in a series                   |
| arc           | story arc         | Multi-episode narrative thread             |
| hook          | hook              | Opening seconds that capture attention     |
| premise       | concept/topic     | Core idea the video explores               |
| callback      | callback          | Reference to earlier content               |
| cliffhanger   | cliffhanger       | Unresolved thread to drive next episode    |
| CTA           | call to action    | Subscribe, comment, link click, etc.       |


## Standard Video Structure

Every YouTube video follows this general flow. Sections can be reordered, but this is the default:

```
intro → content sections → wrapup
```

1. **Intro** — Hook, show the payoff, set up what we'll cover.
2. **Content Sections** — The core value. Each section is a narrative phase that builds on the previous.
3. **Wrapup** — Recap, CTA, where to get the code/resources, sign-off.


## Section Types

Sections are freeform — name them after what they cover. Common patterns:

- **Intro** — Hook + overview + show the finished thing
- **Setup** — Project scaffolding, dependencies, environment
- **Concept sections** — Named after the concept (e.g., "Loop", "Tools", "Context")
- **Demo** — Full working walkthrough of the finished product
- **Wrapup** — Recap, resources, CTA


## Beat Types

Beats within sections describe what happens on screen:

| Type            | Code   | Description                                         |
|-----------------|--------|-----------------------------------------------------|
| talking-head    | TH     | Direct-to-camera presenter talking                  |
| b-roll          | BR     | Supplementary footage over narration                |
| screen-share    | SS     | Screen recording, slides, browser, code editor      |
| demo            | DM     | Live demonstration of a product/process             |
| interview       | IV     | Conversation with a guest                           |
| transition      | TR     | Brief visual/audio bridge between sections          |
| montage         | MN     | Rapid sequence of clips                             |
| text-overlay    | TO     | Text/graphics on screen (stats, quotes, lists)      |
| animation       | AN     | Animated explainer or motion graphics               |

Beat types are optional — use them when it helps clarify what the viewer sees.


## Single Video — storypad.md Template

```yaml
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
```

```markdown
# {Title}

## Premise
{One-sentence core idea}

## Sections

### Intro
- [ ] Hook
- [ ] Show the finished result
- [ ] Overview of what we'll cover

### Wrapup
- [ ] Recap what we built
- [ ] Where to get the code
- [ ] CTA

## Notes
{Research links, reference material, sources}

## Scratchpad
{Freeform script drafting — rough dialogue, voice ideas, half-formed lines}

## References
{Links, sources, inspiration}
```

### Section Format Rules
- Each section is an `### H3` heading under `## Sections`
- Beats are markdown checklist items: `- [ ]` (pending) or `- [x]` (done)
- Prep items follow a `prep:` marker within the same section
- Script content follows a `script:` marker within the same section
- Sections are ordered by narrative flow (the order the viewer experiences them)
- Add content sections between Intro and Wrapup as the storypad develops

### Prep Items
Prep items are things you need to build, create, or have ready before filming a section:

```markdown
### Demo
- [ ] Full end-to-end walkthrough
- [ ] Throw a curveball it handles
prep:
- [ ] Git repo public with README
- [ ] Deployed demo instance running
- [ ] Test data seeded
```

Prep items use the same `- [ ]` / `- [x]` checkbox format as beats.

### Script Blocks
Each section can have a `script:` block containing the actual narration/dialogue for that section. Write rough first, refine later — use the Scratchpad to hash out ideas before committing them here:

```markdown
### Tools
- [x] What tool calling is and why it matters
- [x] Define a lookup-order tool
- [ ] Wire it into the loop
prep:
- [x] Build the lookup-order tool
script:
  So the bare loop can talk, but it can't DO anything.
  Let's fix that.

  Tool calling lets the model reach out and take action —
  think of it like giving the chatbot hands.

  [show code] Here's our lookup-order tool. It takes an
  order ID, hits our database, and returns the status.
```

Script content is freeform text indented under `script:`. It continues until the next section heading or end of the `## Sections` block.


## Series — series.md Template

```yaml
---
venue: youtube
type: series
status: planning
created: {date}
updated: {date}
series-name: ""
premise: ""
cadence: ""
target-episodes: null
tags: []
---
```

```markdown
# {Series Name}

## Premise
{What this series is about and why it exists}

## Episode Arc

| Ep  | Title         | Status      | Arc Position | Premise                    |
|-----|---------------|-------------|--------------|----------------------------|
| 01  |               | planning    | opener       |                            |
| 02  |               | planning    | develop      |                            |
| 03  |               | planning    | develop      |                            |

## Continuity Threads

| Thread           | Status   | Introduced | Last Referenced | Episodes     |
|------------------|----------|------------|-----------------|--------------|
|                  | active   | ep-01      |                 |              |

## Recurring Elements

| Element          | Type       | Description                              |
|------------------|------------|------------------------------------------|
|                  | catchphrase| Repeated phrase or sign-off              |
|                  | segment    | Recurring segment format                 |
|                  | character  | Recurring persona or guest               |
|                  | visual     | Recurring visual motif                   |
```

### Arc Positions
- `opener` — Series premiere, establishes premise and hooks
- `develop` — Builds on established threads, deepens content
- `pivot` — Shifts direction, introduces new thread or challenge
- `climax` — Peak tension or payoff of a major thread
- `closer` — Series finale or season wrap-up
- `standalone` — Self-contained, minimal continuity dependency

### Continuity Thread Statuses
- `active` — Currently developing across episodes
- `resolved` — Thread reached its conclusion
- `dormant` — Paused, may return later
- `recurring` — Ongoing element that doesn't resolve (e.g., running joke)

### Series-Specific Features

**Episode Arcs**: Plan the narrative trajectory across episodes. Each episode has an arc position that shows where it sits in the larger story.

**Callbacks**: Reference earlier episodes to reward loyal viewers. Track in continuity threads with episode cross-references.

**Continuity Tracking**: The continuity threads table ensures you don't drop plot threads or forget established facts.

**Cliffhangers**: End episodes with unresolved questions or teases. Mark these as `active` threads and reference them in the next episode's hook.

**Cross-Episode References**: When one episode references another, update the continuity threads table with both episode numbers. This creates a web of connections viewers can follow.
