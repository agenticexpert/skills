---
name: storypad
description: Brainstorm, outline, and visualize creative storylines with pluggable venue support. Plan YouTube videos, series, or any creative content from idea to structured outline.
triggers:
  - brainstorm
  - storyline
  - outline
  - storyboard
  - sketch
---

# Storypad Skill

Creative storyline development — from raw ideas to structured outlines with ASCII visualization.


## Philosophy

**Expand before you structure.** The best creative work comes from exploring widely before committing to a shape. Storypad.enforces this by separating brainstorming (divergent thinking) from outlining (convergent thinking). Never skip brainstorming to jump straight into sections.

**Venues shape vocabulary, not creativity.** A YouTube video and a book chapter have different structures, but the creative process is the same. Venues provide terminology, templates, and structure — they never limit what you can imagine.

**Progressive disclosure.** Start with a premise. Brainstorm freely. Then shape it into sections with beats. Refine. Visualize. Each step builds on the last, and you can revisit any step.

**Everything lives in one file.** Each storypad is a single `storypad.md` with YAML frontmatter and markdown sections. No databases, no config files — just text you can read, edit, and version.


## Sub Commands

- NEW
  - Example: `/storypad new {name} [--venue youtube]`
  - Load and execute `.../skills/storypad/references/new.md`
  - Creates a new storypad with directory structure and populated template

- BRAINSTORM
  - Example: `/storypad brainstorm [topic]`
  - Load and execute `.../skills/storypad/references/brainstorm.md`
  - Free-form ideation, appends to Notes section

- OUTLINE
  - Example: `/storypad outline`
  - Load and execute `.../skills/storypad/references/outline.md`
  - Creates/modifies sections and beats from brainstorm notes

- ADD
  - Example: `/storypad add {section-name}`
  - Load and execute `.../skills/storypad/references/outline.md`
  - Adds a new section to the outline

- VISUALIZE
  - Example: `/storypad visualize [--table|--gantt]`
  - Load and execute `.../skills/storypad/references/visualize.md`
  - Default: pipeline view. Options: `--table`, `--gantt`

- REFINE
  - Example: `/storypad refine`
  - Load and execute `.../skills/storypad/references/refine.md`
  - Iterates on outline through multiple lenses

- COMPILE
  - Example: `/storypad compile [--output {path}]`
  - Load and execute `.../skills/storypad/references/compile.md`
  - Stitches all section `script:` blocks into a clean `script.md`

- SERIES
  - Example: `/storypad series {name} [--venue youtube]`
  - Load and execute `.../skills/storypad/references/series.md`
  - Creates and manages multi-episode series

- STATUS
  - Example: `/storypad status`
  - Inline: Read the current storypad.md and display a summary
  - Shows: title, venue, status, beat counts, completion percentage
  - Format:
    ```
    {Title} [{venue}] — {status}
    Sections: {count} | Beats: {done}/{total} | Premise: {premise}
    ```

- LIST
  - Example: `/storypad list`
  - Inline: Scan `agents/docs/sketches/` directory
  - Display table of all storypads:
    ```
    | Name              | Venue   | Type   | Status       | Beats  |
    |-------------------|---------|--------|--------------|--------|
    | my-video          | youtube | single | outlining    | 3/24   |
    | tutorial-series   | youtube | series | brainstorming| —      |
    ```

- OPEN
  - Example: `/storypad open {name}`
  - Inline: Load `agents/docs/sketches/{name}/storypad.md` into context
  - If series, also load `series.md` for continuity reference
  - Confirm what was loaded and show current status


## Storage

All sketches live under `agents/docs/sketches/`:

```
agents/docs/sketches/
├── {storypad-name}/
│   ├── storypad.md               # Main storypad document
│   └── viz/
│       └── outline.txt         # ASCII visualization output
├── {series-name}/
│   ├── series.md               # Series-level arc and continuity
│   ├── ep-01-{slug}/
│   │   ├── storypad.md
│   │   └── viz/
│   └── ep-02-{slug}/
│       ├── storypad.md
│       └── viz/
```

### Naming Rules
- Directory names: kebab-case, lowercase, alphanumeric + hyphens
- Episode directories: `ep-NN-{kebab-slug}/` (zero-padded two digits)
- Visualization output: always `viz/outline.txt`


## Storypad.md Format

Every storypad.md has YAML frontmatter followed by markdown content:

```yaml
---
venue: youtube          # Which venue plugin to use
type: single            # single | series-episode
status: brainstorming   # brainstorming | outlining | refining | final
created: YYYY-MM-DD
updated: YYYY-MM-DD
premise: ""             # One-line concept
target-length: ""       # Venue-specific (e.g., "10:00" for YouTube)
audience: ""            # Target audience description
tags: []                # Freeform tags
series: ""              # Series name (only for series-episode type)
episode: null           # Episode number (only for series-episode type)
---
```

### Three-Layer Model

```
Scratchpad → Sections → Compile
```

- **Scratchpad** (`## Scratchpad`) — freeform drafting space. Try things out, write rough dialogue, hash out voice and tone before committing anything to a section.
- **Sections** (`## Sections`) — structured outline with beats, prep, and script blocks. Pull the best ideas from the Scratchpad here.
- **Compile** (`/storypad compile`) — stitches all section `script:` blocks into a clean `script.md` for read-through or voice export.

### Sections, Beats, Prep, and Script

Each section contains:
- **Beats** — what the viewer sees/experiences (`- [ ]` / `- [x]`)
- **Prep** — things to build/prepare before filming (`prep:` marker)
- **Script** — the actual narration/dialogue for this section (`script:` marker)

```markdown
## Sections

### Intro
- [ ] Show demo of final product
- [ ] Hook — "We're building this in 15 minutes"
- [ ] Overview of what we'll cover
prep:
- [ ] Record final demo footage
- [ ] Write setup.sh
script:
  So here's what we're building today. A full customer
  support chatbot — orders, refunds, human handoff.

  I'm going to show you layer by layer, starting from
  nothing.

### Setup
- [ ] Project structure walkthrough
- [x] Install dependencies

### Wrapup
- [ ] Recap what we built
- [ ] CTA — subscribe + comment
script:
  And that's the whole stack. Loop, tools, context, MCP.

  The repo link is in the description — clone it, run it,
  show me what you build with it.
```

- Sections are `### H3` headings under `## Sections`
- Script content is freeform text indented under `script:`
- Sections are ordered by narrative flow

### Scratchpad

`## Scratchpad` sits alongside `## Notes` in storypad.md. Use it to:
- Try different ways of opening a section
- Write rough dialogue before you know if it works
- Capture voice/tone ideas without committing them to a section
- Hash out an explanation before you know where it belongs

```markdown
## Scratchpad
what if i open with something breaking?  like show the
chatbot failing FIRST, then show it working?  more tension

hook idea: "most AI chatbots are useless. here's why,
and here's how to build one that isn't"

for MCP section... "you've been writing functions.
now you're writing capabilities"
```

Nothing in the Scratchpad is structured. It's just writing.

### Status Progression
```
brainstorming → outlining → refining → final
```

Status updates automatically as you work:
- `brainstorming` — Notes section has content, no sections yet
- `outlining` — Sections exist, beats being added
- `refining` — Running refinement lenses, iterating
- `final` — All beats complete, ready for production


## Visualization

Three views available via `.../skills/storypad/scripts/`:

### Pipeline (default)
`python3 .../scripts/pipeline.py <storypad.md>`

Horizontal pipeline bar showing sections, with prep dependencies dangling below aligned to their parent section. Followed by expanded section detail with beat and prep checklists.

### Table
`python3 .../scripts/table.py <storypad.md>`

Compact tabular summary — one row per section with beat counts, prep counts, and mini progress bars.

### Gantt
`python3 .../scripts/gantt.py <storypad.md>`

Roadmap-style Gantt chart with sections as rows and progress bars indicating completion level.

All three support `--series` flag for series.md files.


## Venue Plugin System

Venues are `.md` files in `.claude/skills/storypad/venues/`. Each venue provides:

1. **Terminology mapping** — How sketch terms translate to venue-specific language
2. **Standard structure** — Default section flow for the venue
3. **Beat types** — Available type codes and descriptions
4. **Templates** — YAML frontmatter and markdown templates for storypad.md and series.md
5. **Series features** — How multi-part content works in this venue

### Adding a New Venue

To add a new venue (e.g., book, podcast, game):

1. Create `.claude/skills/storypad/venues/{venue-name}.md`
2. Follow the structure of `youtube.md`
3. No code changes needed — the venue is discovered by name from the `--venue` flag

### Available Venues
- `youtube` — YouTube video and series planning


## Anti-Patterns

**Don't skip brainstorming.** Jumping straight to an outline produces generic, formulaic content. Always brainstorm first, even briefly.

**Don't over-section.** A 10-minute YouTube video doesn't need 15 sections. 5–8 is typical. Each section should represent a meaningful narrative phase.

**Don't edit sections during brainstorming.** Brainstorm mode appends to Notes only. Structure comes later in outline mode. Mixing the two kills creative flow.

**Don't manually create ASCII visualizations.** Always use the scripts via `/storypad visualize`. Manual ASCII art drifts from the actual data.

**Don't forget to update frontmatter.** When status changes, the `updated` date and `status` field should reflect reality. The commands do this automatically.

**Don't create sketch files outside the storage directory.** All sketches belong in `agents/docs/sketches/`. This keeps them discoverable by `/storypad list`.
