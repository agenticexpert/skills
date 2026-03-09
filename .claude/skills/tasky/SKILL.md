# tasky — Development Task Manager

A generic task and roadmap management skill. Tracks features, tasks, milestones, roadmaps, decisions, and issues. Works in any project.

## Usage

**Setup**
```
/tasky init
```

**Tasks**
```
/tasky list
/tasky list <feature>
/tasky next <feature>
/tasky show <feature> <id>
/tasky done <feature> <id>
/tasky update <feature> <id>
/tasky create <feature>
/tasky add <feature> "<description>"
/tasky resequence <feature>
/tasky check-deps <feature>
```

**Roadmaps & Milestones**
```
/tasky roadmap list
/tasky roadmap create <name>
/tasky roadmap show <roadmap>
/tasky roadmap status <roadmap>
/tasky milestone list <roadmap>
/tasky milestone create <roadmap> <name>
/tasky milestone show <roadmap> <milestone>
/tasky milestone assign <roadmap> <milestone> <feature> <task-id>
/tasky milestone unassign <roadmap> <milestone> <feature> <task-id>
/tasky timeline <roadmap>
```

- Keep answers short and scannable
- Show code/file changes only when the user is ready to act on them

## Project Configuration: TASKY.md

Tasky supports a project-level configuration file at the **git root**: `TASKY.md`.

### What it does

`TASKY.md` lets project owners define standing instructions that tasky follows on every invocation — conventions, defaults, workflow rules — without repeating them in every prompt. Think of it as a project-specific extension of the skill.

### What it can contain

- **Default roadmap**: avoid repeating it on every roadmap command
- **Data directory**: if not using the default `agents/docs/tasky/`
- **Conventions**: e.g. "always run `bun run check` after marking a task done"
- **Workflow rules**: e.g. "ask before marking a task done if it has open sub-items"
- **Custom status values or tag conventions**
- Any project-specific instructions you want tasky to always follow

### `tasky init`

Creates `TASKY.md` at the git root interactively:

1. Check whether `TASKY.md` already exists — if so, warn and ask before overwriting
2. Ask the user:
   - Project / product name
   - Default roadmap name (or "none")
   - Data directory (default: `agents/docs/tasky/`)
   - Any standing conventions or workflow rules they want enforced
   - Anything else they want tasky to always remember
3. Write `TASKY.md` from a structured template using their answers
4. Confirm the file was created and show the path

Template written by `init`:

```markdown
# TASKY — Project Configuration

> This file is read by tasky at the start of every session. Edit it to add
> project-specific instructions, conventions, or defaults.

## Project

- **Name**: {project name}
- **Default roadmap**: {roadmap name, or "none"}
- **Data directory**: {data directory}

## Conventions

{user-supplied conventions, or placeholder text}

## Always Do

{user-supplied standing rules, or placeholder text}

## Notes

{free-form notes}
```

## Startup

**Before executing any tasky command**, run this startup sequence:

1. Determine the project root (directory containing `.git/`, or the working directory if no git repo)
2. Check whether `{project_root}/TASKY.md` exists
3. If it exists and has **not** been read yet in this session:
   - Read it
   - Treat its contents as authoritative project-level instructions
   - These instructions **extend and override** skill defaults where they conflict
4. Proceed with the requested command

If `TASKY.md` is not found, continue with skill defaults — no warning needed.

## How It Works

Detects intent and routes to the appropriate reference:
- Task commands → `references/task-management.md`
- Roadmap/milestone/timeline commands → `references/roadmap.md`
- Decision intent → `references/decisions.md`
- Issue/bug intent → `references/issues.md`

## Commands

### Setup

| Command | Description |
|---------|-------------|
| `init` | Create `TASKY.md` at the project root (interactive) |

### Tasks

| Command | Description |
|---------|-------------|
| `list` | List all features |
| `list <feature>` | List tasks in a feature with status and blockers |
| `next <feature>` | Show next unblocked task |
| `show <feature> <id>` | Show full task detail |
| `done <feature> <id>` | Mark a task completed — runs `status.py` |
| `undone <feature> <id>` | Revert a completed task — runs `status.py` |
| `update <feature> <id>` | Edit a task's fields |
| `create <feature>` | Create a new feature task set |
| `add <feature> "<desc>"` | Add a task to a feature |
| `resequence <feature>` | Reorder tasks in a feature |
| `check-deps <feature>` | Validate dependency graph |

### Roadmaps & Milestones

| Command | Description |
|---------|-------------|
| `roadmap list` | List all roadmaps — format spec in `references/roadmap.md` |
| `roadmap create <name>` | Create a new roadmap |
| `roadmap show <roadmap>` | Gantt chart of milestones + task progress — format spec in `references/roadmap.md` |
| `roadmap status <roadmap>` | One-line status summary |
| `milestone list <roadmap>` | List milestones for a roadmap |
| `milestone create <roadmap> <name>` | Add a milestone to a roadmap |
| `milestone show <roadmap> <milestone>` | Show milestone + assigned tasks |
| `milestone assign ...` | Assign a task to a milestone |
| `milestone unassign ...` | Remove task from a milestone |
| `timeline <roadmap>` | Visual timeline of milestones + tasks — format spec in `references/roadmap.md` |

## Files

```
.claude/skills/tasky/
├── SKILL.md                    # This file
└── references/
    ├── task-management.md      # Task commands and formats
    ├── roadmap.md              # Roadmap and milestone commands and formats
    ├── decisions.md            # Decision logging and query
    ├── issues.md               # Issue and bug tracking
    ├── gantt.py                # Gantt chart generator — always use this, never render manually
    └── status.py               # Status cascade — always use this for done/undone, never update manually

agents/docs/tasky/
├── index.md               # Top-level index: all roadmaps + task sets
├── tasks/
│   ├── index.md           # Index of all standalone task sets
│   └── {feature}/
│       ├── index.md       # Feature overview + milestone links
│       └── tasks/
│           ├── index.md   # Task manifest (table + dep tree)
│           └── NN-kebab-title.md
├── roadmaps/
│   ├── index.md           # Index of all roadmaps
│   └── {name}/
│       └── milestones/
│           ├── index.md   # Milestone index + status
│           └── NN - {name}.md  # Individual milestone files
├── decisions/
│   ├── index.md           # All decisions across topics
│   └── {topic}.md         # Decisions grouped by area
└── issues/
    ├── index.md           # All issues, scannable
    └── NNN-slug.md        # Individual issue files
```

## Intent Detection

1. Parse command prefix or natural language intent:
   - `roadmap`, `milestone`, `timeline` → load `references/roadmap.md`
   - `list`, `next`, `show`, `done`, `update`, `create`, `add`, `resequence`, `check-deps` → load `references/task-management.md`
   - `decision`, `remember`, `we decided`, `note that`, `why did we`, `what did we decide` → load `references/decisions.md`
   - `issue`, `bug`, `defect`, `there's a bug`, `that's fixed`, `something's broken` → load `references/issues.md`
2. Disambiguate milestone overview vs. detail:
   - "show milestones", "show project milestones", "milestone overview", or any request to see all milestones for a roadmap → treat as `roadmap show` (Gantt via `gantt.py`)
   - "show milestone X" or "milestone show <roadmap> <milestone>" (a specific milestone) → treat as `milestone show`
   - When in doubt, default to `roadmap show` (Gantt) — never render milestone summaries as plain tables
3. Execute with the reference as context
