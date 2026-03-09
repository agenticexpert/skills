# knowledge — Brain Knowledge Commands

Manage the knowledge in BRAIN.md and scaffold category docs under agents/docs/.

---

## BRAIN.md Structure

Always read BRAIN.md before executing any knowledge command. It is already in context at session start.

Never search agents/docs/ speculatively. Follow links from BRAIN.md only.

---

## Category Doc Structure

Each category under `agents/docs/{domain}/{category}/` contains:

```
agents/docs/{domain}/{category}/
├── vision.md          # Why this category exists and what it delivers
├── pillars.md         # Non-negotiable constraints for this area
├── decisions.md       # Decision log — what was decided and why
└── implementation.md  # How it actually works — current state
```

### `vision.md`
```markdown
# {Domain}/{Category} — Vision

## Why
[Why this category exists]

## What It Delivers
[Concrete outcomes]
```

### `pillars.md`
```markdown
# {Domain}/{Category} — Pillars

1. [Pillar] — [Why non-negotiable]
```

### `decisions.md`
```markdown
# {Domain}/{Category} — Decisions

| ID  | Decision                    | Reason                        | Date       |
|-----|-----------------------------|-------------------------------|------------|
| 001 | [what was decided]          | [why]                         | YYYY-MM-DD |
```

### `implementation.md`
```markdown
# {Domain}/{Category} — Implementation

[Current implementation notes — kept up to date as work completes]
```

---

## Commands

### `brain init`

Creates BRAIN.md skeleton at the project root:

1. Check if BRAIN.md exists — if so, warn and confirm before overwriting
2. Write skeleton with today's date as `Last freshened`
3. Confirm path and invite first `brain init <domain>/<category>`

### `brain init <domain>/<category>`

Scaffold a new category collaboratively:

1. Create `agents/docs/{domain}/{category}/` with all four template files
2. Work with the user to fill in vision.md — ask: why does this exist, what does it deliver?
3. Ask: any pillars (non-negotiables) to capture now?
4. Ask: any decisions already made to log?
5. Leave implementation.md empty — it fills as work happens
6. Add entry to BRAIN.md Map section: `- [domain/category](path/) — {one-line description}`
7. Confirm

Do not ask all questions at once. One at a time, conversationally.

### `brain show <domain>/<category>`

1. Confirm category exists in BRAIN.md Map — if not, suggest `brain init`
2. Read and display in order: vision → pillars → decisions → implementation
3. Show all four files — do not summarize, show content

### `brain ask "<question>"`

1. Search BRAIN.md Q&A section for the closest matching question
2. If found: display the answer and link
3. If not found: say so — suggest `brain map` to find the right category, or `brain add q` to record the answer
4. Do not search agents/docs/ — lookup only

### `brain map`

Display the Map section of BRAIN.md verbatim. One-line per category.

### `brain add fact "<text>"`

1. Append to BRAIN.md Facts section:
   `- {text} *(YYYY-MM-DD)*`
2. Confirm

### `brain add q "<question>" "<answer>" [<link>]`

1. Assign next entry ID (for use with `brain confirm`)
2. Append to BRAIN.md Q&A section:
```markdown
**{Question}**
{Answer}. *Confirmed: YYYY-MM-DD* → [source]({link})
```
   Omit the link if not provided.
3. Confirm
