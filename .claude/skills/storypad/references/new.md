# New Sketch

Create a new storypad with directory structure and venue-specific template.


## Input Parsing

Parse the command: `/storypad new {name} [--venue youtube]`

1. **Name**: Required. The storypad name.
   - Slugify to kebab-case: lowercase, replace spaces/underscores with hyphens, strip non-alphanumeric (except hyphens)
   - Example: `"My Cool Video"` → `my-cool-video`

2. **Venue**: Optional. Defaults to `youtube`.
   - Must match a file in `.claude/skills/storypad/venues/{venue}.md`
   - If venue file doesn't exist, report error and list available venues

3. **Check for conflicts**: If `agents/docs/sketches/{slug}/` already exists, report error and suggest a different name or using `/storypad open {slug}`


## Directory Creation

Create the following structure:

```
agents/docs/sketches/{slug}/
├── storypad.md
└── viz/
```

Use `mkdir -p` to create both directories.


## Template Population

1. Read the venue file: `.claude/skills/storypad/venues/{venue}.md`
2. Extract the **Single Video — storypad.md Template** section (or equivalent for other venues)
3. Populate the template:
   - Replace `{date}` with today's date (YYYY-MM-DD format)
   - Replace `{Title}` with the original (non-slugified) name
   - Set `status: brainstorming`
   - Leave `premise`, `target-length`, `audience` empty for user to fill
4. Write the populated template to `agents/docs/sketches/{slug}/storypad.md`


## After Creation

1. Confirm what was created:
   ```
   Created storypad: {name}
   Location: agents/docs/sketches/{slug}/storypad.md
   Venue: {venue}
   ```

2. Ask for a premise — the one-sentence core idea:
   - "What's the core idea for this video in one sentence?"
   - Update the `premise` field in frontmatter and the Premise section

3. Suggest next steps:
   - `/storypad brainstorm` — Start generating ideas
   - `/storypad outline` — Jump to structuring (if you already have ideas)


## Error Handling

- **Missing name**: "Usage: `/storypad new {name} [--venue youtube]`"
- **Directory exists**: "Storypad.'{slug}' already exists. Use `/storypad open {slug}` to resume, or choose a different name."
- **Unknown venue**: "Venue '{venue}' not found. Available venues: youtube"
