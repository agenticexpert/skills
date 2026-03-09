# Series

Create and manage multi-episode series with continuity tracking.


## Input Parsing

Parse: `/storypad series {name} [--venue youtube]`

1. **Name**: Required. The series name.
   - Slugify to kebab-case: lowercase, replace spaces/underscores with hyphens, strip non-alphanumeric (except hyphens)

2. **Venue**: Optional. Defaults to `youtube`.
   - Must match a file in `.claude/skills/storypad/venues/{venue}.md`

3. **Check for conflicts**: If `agents/docs/sketches/{slug}/` already exists:
   - If it contains `series.md`, offer to open it
   - If it's a single storypad, report conflict


## Series Creation

### 1. Create Directory Structure

```
agents/docs/sketches/{slug}/
├── series.md
```

Episode directories are created later when individual episodes are added.

### 2. Populate series.md

1. Read the venue file: `.claude/skills/storypad/venues/{venue}.md`
2. Extract the **Series — series.md Template** section
3. Populate:
   - Replace `{date}` with today's date
   - Replace `{Series Name}` with the original name
   - Set `status: planning`
4. Write to `agents/docs/sketches/{slug}/series.md`

### 3. Confirm Creation

```
Created series: {name}
Location: agents/docs/sketches/{slug}/series.md
Venue: {venue}
```

Ask for a series premise: "What's this series about?"
Update the `premise` field and Premise section.


## Adding Episodes

When the user wants to add an episode (from within a series context):

### 1. Determine Episode Number
- Scan existing `ep-NN-*` directories
- Next episode = max(NN) + 1, zero-padded to two digits

### 2. Get Episode Details
- Ask for episode title (or accept from command)
- Slugify the title for the directory name

### 3. Create Episode Structure

```
agents/docs/sketches/{series-slug}/ep-{NN}-{episode-slug}/
├── storypad.md
└── viz/
```

### 4. Populate Episode storypad.md
- Use the single storypad template from the venue
- Add series-specific frontmatter:
  ```yaml
  type: series-episode
  series: "{series-name}"
  episode: {NN}
  ```

### 5. Update series.md
- Add a new row to the Episode Arc table
- Set arc position based on context (ask if unclear)

### 6. Confirm
```
Created episode {NN}: {title}
Location: agents/docs/sketches/{series-slug}/ep-{NN}-{slug}/storypad.md
```


## Episode Numbering

- Format: `ep-NN-{kebab-slug}/`
- NN is zero-padded to two digits: `01`, `02`, ... `99`
- Episodes are numbered sequentially with no gaps
- If an episode is removed, do NOT renumber remaining episodes (preserve references)


## Continuity Thread Management

### Adding Threads
When a new continuity thread is identified during brainstorming or outlining:
1. Add a row to the Continuity Threads table in series.md
2. Set status to `active`
3. Set `Introduced` to current episode
4. Set `Episodes` to the current episode

### Updating Threads
When a thread is referenced in a new episode:
1. Update `Last Referenced` to the current episode
2. Append the episode to `Episodes` list
3. Update status if changed (active → resolved, etc.)

### Thread Statuses
- `active` — Currently developing
- `resolved` — Reached conclusion
- `dormant` — Paused, may return
- `recurring` — Ongoing element that doesn't resolve


## Cross-Episode References

When one episode references content from another:
1. Note the reference in the episode's storypad.md Notes section
2. Update the continuity thread in series.md
3. Format: `(see ep-{NN})` in segment notes

This creates a traceable web of connections across the series.


## Series Status Overview

When viewing a series (via `/storypad open {series-name}` or `/storypad status` within a series):

```
Series: {name} [{venue}] — {status}
Episodes: {count} | Threads: {active}/{total}

 Ep  Title              Status       Arc
 ─────────────────────────────────────────
 01  Getting Started    refining     opener
 02  Deep Dive          outlining    develop
 03  Advanced Tips      brainstorming develop
 ─────────────────────────────────────────

Active Threads: {list of active thread names}
```


## Error Handling

- **Missing name**: "Usage: `/storypad series {name} [--venue youtube]`"
- **Directory conflict**: "'{slug}' already exists as a single storypad. Choose a different name."
- **Unknown venue**: "Venue '{venue}' not found. Available venues: youtube"
