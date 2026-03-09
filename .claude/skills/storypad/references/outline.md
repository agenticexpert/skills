# Outline

Create and manage sections with beats from brainstorm notes. Also handles `/storypad add {section}`.


## Prerequisites

- A storypad must be open (storypad.md loaded in context)
- If no storypad is open, prompt: "No storypad loaded. Use `/storypad open {name}` or `/storypad new {name}` first."


## Detect Mode

- `/storypad outline` — Full outline creation/update from brainstorm notes
- `/storypad add {section-name}` — Add a new section to existing outline


## Full Outline Workflow

### 1. Load Context

1. Read the current storypad.md
2. Read the venue file from `.claude/skills/storypad/venues/{venue}.md`
3. Extract the standard structure (e.g., intro → content → wrapup for YouTube)
4. Read the Notes section for brainstorm material

### 2. Analyze Brainstorm Notes

- Identify distinct topics, themes, or ideas from the Notes section
- Group related ideas into potential sections
- Identify the natural narrative flow/order
- Note any items that require advance preparation (prep items)

### 3. Build Sections

Apply the venue's standard structure as scaffolding:

1. Start with Intro and Wrapup as bookends
2. Fill content sections from brainstorm analysis — name each after its narrative purpose
3. Add beats within each section (what happens on screen)
4. Add prep items for sections that need advance work (tools to build, repos to publish, demos to record)

### 4. Write the Outline

Update storypad.md:
- Add or replace the `## Sections` block with the new sections
- Each section is an `### H3` with `- [ ]` beats and optional `prep:` items
- Preserve the Notes section (never modify it)
- Update frontmatter: `status: outlining`, `updated: {today}`
- Keep all other sections intact

### 5. Display the Outline

Run the pipeline visualization automatically after creating the outline:
```bash
python3 .claude/skills/storypad/scripts/pipeline.py {path-to-storypad.md}
```


## Add Section Workflow

For `/storypad add {section-name}`:

### 1. Parse Input
- `{section-name}`: The name for the new section
- If the name matches an existing section, report error

### 2. Determine Placement
- Ask the user where to insert (or auto-place before Wrapup)
- Default: insert before the last section

### 3. Create Section
- Add the `### {name}` heading with a few placeholder beats
- Ask what beats belong in this section
- Ask if any prep is needed

### 4. Update File
- Insert the new section at the correct position
- Update frontmatter `updated` date
- Write the updated storypad.md

### 5. Confirm
```
Added section: {name} ({n} beats, {m} prep)
Total sections: {count} | Total beats: {total}
```


## Section Format

Sections in storypad.md always follow this format:

```markdown
### Section Name
- [ ] Beat one
- [ ] Beat two
- [x] Beat three (done)
prep:
- [ ] Prep item one
- [ ] Prep item two
```

Rules:
- Section names are freeform — name them after what they cover
- Beats describe what the viewer sees/experiences
- Prep items are things to build/create before filming
- `- [ ]` = pending, `- [x]` = done
- Prep items are optional — only add when a section needs advance work


## Transitioning from Brainstorming

When creating an outline for the first time from brainstorm notes:
- Acknowledge which ideas from Notes are being incorporated
- Note any ideas that don't fit the current outline (they're not lost — they stay in Notes)
- Explain the structural choices ("Putting the demo after the concept sections to show the payoff")
- Identify prep items ("You'll need the git repo ready before filming the Demo section")
