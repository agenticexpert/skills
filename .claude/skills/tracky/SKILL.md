# tracky — Living Knowledge Tracker

A lightweight skill for tracking what you know about your project — decisions, specs, open questions, rejected approaches, and anything else worth remembering. Entries stay current: they can be updated, superseded, or resolved as the project evolves.

Works standalone. Tasky-aware when both are present.

## Usage

**Setup**
```
/tracky init
```

**Entries**
```
/tracky note "<text>"
/tracky add "<title>"
/tracky triage
/tracky list
/tracky list <type>
/tracky show <slug>
/tracky update <slug>
/tracky supersede <slug>
/tracky search <query>
```

- Keep answers short and scannable
- Always read TRACKY.md registry first — only fetch individual files when needed (progressive disclosure)
- When showing entries, lead with type, status, and a one-line summary

## Project Configuration: TRACKY.md

TRACKY.md lives at the **git root**. It serves two purposes:

1. **Config** — project name, data directory, standing instructions
2. **Registry** — the manifest of all tracked files, their type, status, and purpose

Because the registry lives in TRACKY.md, `/tracky list` never needs to open individual files.

### Startup

**Before executing any tracky command**, run this startup sequence:

1. Determine the project root (directory containing `.git/`, or working directory)
2. Check whether `{project_root}/TRACKY.md` exists
3. If found and not yet read this session: read it — both config and registry are now loaded
4. Proceed with the requested command

If `TRACKY.md` is not found, continue with skill defaults — no warning needed.

### `tracky init`

Creates `TRACKY.md` at the git root and scaffolds the data directory interactively:

1. Check if `TRACKY.md` already exists — warn and ask before overwriting
2. Ask the user:
   - Project / product name
   - Data directory (default: `agents/tracky/`)
   - Any standing instructions for tracky to always follow
3. Write `TRACKY.md` using the template below
4. Create the data directory if it doesn't exist
5. Confirm what was created

Template written by `init`:

```markdown
# TRACKY — Project Configuration

> This file is read by tracky at the start of every session. Edit it to add
> project-specific instructions, conventions, or defaults.

## Project

- NAME: {project name}
- DATA DIRECTORY: {data directory}

## Instructions

{any standing instructions, or delete this section}

## Registry

| File | Title | Type | Status | Purpose |
|------|-------|------|--------|---------|
```

## How It Works

Routes to reference files based on intent:
- Entry management (add, update, supersede) → `references/entries.md`
- List, show, search → `references/search.md`

## Commands

### Setup

| Command | Description |
|---------|-------------|
| `init` | Create `TRACKY.md` and scaffold data directory (interactive) |

### Entries

| Command | Description |
|---------|-------------|
| `note "<text>"` | Fast-capture a thought — no questions, status: deferred |
| `add "<title>"` | Add a new tracked entry (interactive for type, content, purpose) |
| `triage` | Review all deferred entries — act, promote to tasky, discard, or skip |
| `list` | Show the registry — all entries, type, status, purpose |
| `list <type>` | Filter registry by type |
| `show <slug>` | Fetch and display the full entry file |
| `update <slug>` | Edit an entry's content, status, or type |
| `supersede <slug>` | Mark an entry superseded; optionally add a replacement |
| `search <query>` | Search registry first, then file contents for matches |

## Entry Types

| Type | Meaning |
|------|---------|
| `decision` | A choice made, an open question, or an approach considered and rejected |
| `spec` | How something works, is designed, or is constrained |
| `note` | General context, background, or nuance |
| `issue` | A bug, defect, or problem noticed but not yet acted on |

## Entry Statuses

| Status | Meaning |
|--------|---------|
| `current` | Active and accurate right now |
| `draft` | Being worked out; not yet settled |
| `deferred` | Captured but not yet acted on — shows up in triage |
| `superseded` | No longer accurate; replaced by another entry |

## Entry File Format

Each tracked entry lives at `{data_dir}/{slug}.md`:

```markdown
# {title}

TYPE: decision | spec | note
STATUS: current | draft | superseded
ADDED: {YYYY-MM-DD}
UPDATED: {YYYY-MM-DD}
SUPERSEDES: {slug} (if applicable)
SUPERSEDED BY: {slug} (if applicable)
RELATED: {comma-separated slugs or task IDs} (optional)

## Content

{free-form markdown — what is known, decided, or specified}

## Why

{rationale, constraints, context — optional but encouraged}
```

## Files

```
.claude/skills/tracky/
├── SKILL.md                  # This file
└── references/
    ├── entries.md            # Add, update, supersede procedures
    └── search.md             # List, show, search — progressive disclosure

TRACKY.md                     # Git root — config + registry (the manifest)
{data_dir}/                   # Default: agents/tracky/
└── {slug}.md                 # Individual tracked entries (flat)
```

## Tasky Integration

When both tasky and tracky are present:

- On `/tasky done`, optionally prompt: "Does this change anything in tracky?"
- When showing task detail, scan the tracky registry for entries with matching keywords — surface titles only, offer to fetch if relevant
- Integration activates automatically when `TRACKY.md` is found; can be disabled via `TASKY.md` instructions
