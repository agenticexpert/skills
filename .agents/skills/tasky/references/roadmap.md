# roadmap — Manage Roadmaps and Milestones

Roadmaps are named sequences of milestones. Milestones group tasks from features. Parallelism uses phase ranges.

---

## File Locations

```
agents/docs/tasky/roadmaps/
├── index.md                     # All roadmaps + status
└── {name}/milestones/
    ├── index.md                 # Milestone index — SINGLE READ for timeline/show
    └── NN - {name}.md           # Individual milestone

agents/docs/tasky/tasks/{feature}/
├── index.md                     # Feature overview + status
└── tasks/index.md               # Task manifest (status source of truth)
```

---

## Formats

### Roadmap Index (`roadmaps/index.md`)

```markdown
# Roadmaps

| Name       | Path         | Status      |
|------------|--------------|-------------|
| product-v1 | product-v1/  | active |
```

Status: `planned` | `active` | `completed`

### Milestone Index (`milestones/index.md`)

```markdown
# {Roadmap} — Milestone Index

| ID | Name       | Phase | File               | Status      | Done | Total |
|----|------------|-------|--------------------|-------------|------|-------|
| 01 | Core       | 1     | 01 - core.md       | completed   | 3    | 3     |
| 02 | Containers | 2     | 02 - containers.md | active | 2    | 8     |
| 03 | Grids      | 3     | 03 - grids.md      | planned     | 0    | 6     |
| 04 | Resizing   | 3–4   | 04 - resizing.md   | planned     | 0    | 5     |
| 11 | Companion  | 2–10  | 11 - companion.md  | planned     | 0    | 4     |

## Summary

1 completed / 1 active / 3 planned
```

Phase = slot or range (`3–4`, `2–10`) for parallel milestones.
Done/Total = task counts, kept in sync by status cascade.

### Milestone File (`milestones/NN - {name}.md`)

```markdown
# Milestone NN — {Name}

STATUS: planned | active | completed
ROADMAP: {roadmap-name}
PHASE: N (or N–M)
ISSUE: NNN                                 ← optional; links to issues/NNN-slug.md
PROCESS: {domain/category or path}         ← optional; inherited by tasks
REFERENCES: {brain entry IDs or paths}     ← optional; inherited by tasks
GUARDS: {constraints, things not to break} ← optional; inherited by tasks

## Description

[What this milestone delivers]

## Assigned Tasks

| Feature | Task ID | Title         | Status      |
|---------|---------|---------------|-------------|
| auth    | 01      | Login flow    | completed   |

## Notes

[Optional]
```

Rules:
- `{feature}/tasks/index.md` is source of truth for task status
- `tasky done` updates: task file → tasks/index.md → milestone file → milestone index Done/Total
- Tasks can appear in multiple milestones

---

## Gantt Chart

Rendering is handled entirely by `references/gantt.py`. Never render manually.

---

## Commands

### `tasky roadmap list`

Read `roadmaps/index.md`, then each roadmap's `milestones/index.md` for summary data. Display as a scannable list.

Format:

```
Roadmaps  (N active · N planned)

  [░]  product-v1    phase 2 — Containers    2/8 tasks
  [░]  mobile-app    phase 1 — Auth          0/5 tasks
  [ ]  infra         —
  [█]  bootstrap     completed
```

Status indicators:

| Indicator | Meaning   |
|-----------|-----------|
| `[ ]`     | planned   |
| `[░]`     | active    |
| `[▒]`     | at-risk   |
| `[█]`     | completed |

Summary line omits zero-count categories. If no roadmaps exist, print `No roadmaps yet. Use /tasky roadmap create <name> to add one.`

### `tasky roadmap create <name>`

1. Slugify name → create `roadmaps/{name}/milestones/` + empty `index.md`
2. Append to `roadmaps/index.md` and `agents/docs/tasky/index.md`
3. Prompt user for description

### `tasky timeline <roadmap>`

Run `gantt.py` and display the full output to the user. Never render manually.

```
python3 .claude/skills/tasky/references/gantt.py agents/docs/tasky/roadmaps/{roadmap}/milestones/index.md
```

Show the script output verbatim in a code block.

### `tasky roadmap show <roadmap>`

Same as `tasky timeline` — run `gantt.py` and display the full output to the user. Never render manually.

### `tasky roadmap status <roadmap>`

Single line: `Product v1: M01 [█] → M02 [░] (2/8) → M03 [ ]`

### `tasky milestone list <roadmap>`

Same as `roadmap show`.

### `tasky milestone create <roadmap> <name>`

1. Read `milestones/index.md` for next ID
2. Prompt for phase (default = ID)
3. Create `NN - {name}.md` skeleton
4. Append to milestone index with Done=0, Total=0

### `tasky milestone show <roadmap> <milestone>`

Read milestone file + `{feature}/tasks/index.md` per feature for live status. Show done/total.

### `tasky milestone assign <roadmap> <milestone> <feature> <task-id>`

1. Confirm task exists
2. Add `MILESTONE` to task file (or `MILESTONES` for multiple)
3. Add row to milestone file's Assigned Tasks
4. Update Done/Total in milestone index

### `tasky milestone unassign <roadmap> <milestone> <feature> <task-id>`

1. Remove row from milestone file
2. Remove/update `MILESTONE` in task file
3. Update Done/Total in milestone index

---

## Linking Tasks to Milestones

In task file: `MILESTONE: roadmap/milestone` (or `MILESTONES: r/m1, r/m2`). Omit if unassigned. Written by `tasky milestone assign`.

---

## Safeguards

- Never delete milestone files
- `tasky done` cascades: task file → tasks/index.md → feature index.md → milestone file + milestone index (Status, Done/Total) → roadmaps/index.md
- No overwrite on `roadmap create` without confirmation
- Milestone IDs: numeric, sequential, half-steps (02.5) allowed
- Grid columns: always 5 chars, no exceptions
