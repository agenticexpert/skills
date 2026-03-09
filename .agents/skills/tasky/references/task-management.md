# task-management — Manage Development Task Sets

Manage task sets stored under `agents/docs/tasky/tasks/{feature}/`. Supports listing, creating, adding, updating, resequencing, and dependency checking.

---

## Task Location

```
agents/docs/tasky/tasks/
├── index.md                     ← index of all features
└── {feature}/
    ├── index.md                 ← feature overview + milestone links
    └── tasks/
        ├── index.md             ← task manifest (SINGLE READ for listing)
        ├── 01-first-task.md
        ├── 02-second-task.md
        └── nn-last-task.md
```

---

## Feature Index (`agents/docs/tasky/tasks/index.md`)

Top-level index of all features. Read this first when no feature name is given.

```markdown
# Features

| Name         | Path          | Milestones           | Status      |
|--------------|---------------|----------------------|-------------|
| auth         | auth/         | product-v1/02-beta   | active |
| dashboard    | dashboard/    | product-v1/02-beta   | pending     |
| api          | api/          | product-v1/03-ga     | pending     |
| legacy-fix   | legacy-fix/   | —                    | completed   |
```

Update whenever a feature is created, completed, or assigned to a milestone.

---

## Feature Overview (`{feature}/index.md`)

```markdown
# {Feature} — Overview

STATUS: pending | active | completed
MILESTONES: product-v1/02-beta, product-v1/03-ga   ← optional

## Description

[1–2 sentences on what this feature does]

## Goals

[Key outcomes]

## Key Decisions

[Bullet-point decisions]
```

---

## Task Manifest (`{feature}/tasks/index.md`)

This is the **only file read** when listing tasks for a feature. Must stay in sync after every operation.

```markdown
# {Feature} — Task Manifest

## Tasks

| ID   | Title                          | File                              | Depends on | Status    |
|------|--------------------------------|-----------------------------------|------------|-----------|
| 01   | Create initial scaffold        | 01-initial-scaffold.md            | —          | completed |
| 02   | Add data layer                 | 02-add-data-layer.md              | —          | completed |
| 03   | Wire up UI                     | 03-wire-up-ui.md                  | 02         | pending   |

## Dependency Tree

\`\`\`
01 Create initial scaffold ──┐
02 Add data layer ───────────┴──► 03 Wire up UI ──► 04 ...
\`\`\`
```

Rules:
- Table row order: numeric ascending (01, 02, 02.5, 03, ...)
- Depends on: comma-separated task IDs, or `—` for none
- Status: `pending` | `active` | `completed`
- Dep tree: always kept in file, only shown to user when explicitly requested

### When to update the manifest

Update after **every** task operation that changes state:
- `done` → update Status column, then cascade (see Status Cascade)
- `add` → append row + rebuild dep tree; if feature was `completed`, recompute and cascade
- `resequence` → update all IDs, filenames, Depends on, rebuild dep tree
- `update` (if status or deps change) → update row + dep tree if needed; if status changed, cascade

---

## Status Cascade

Handled by `references/status.py`. Never cascade manually.

```
python3 .claude/skills/tasky/references/status.py <task-file-path> done
python3 .claude/skills/tasky/references/status.py <task-file-path> undone
```

The script updates all affected files and prints a summary of every file touched.

---

> Design note — cascade layers (applies to both `status.py` and `tasky add`):
> 1. Task file `STATUS` field
> 2. Task manifest `{feature}/tasks/index.md` — Status column for the task row
> 3. Feature overview `{feature}/index.md` — Status recomputed from all manifest rows
> 4. Global tasks index `tasks/index.md` — Status column for the feature row
> 5. Milestone file (if `MILESTONE` field present) — Assigned Tasks table row + Done/Total
> 6. Milestones index `milestones/index.md` — Done/Total + Status recomputed
> 7. Roadmap index `roadmaps/index.md` — Status recomputed from milestone statuses
>
> `status.py` runs steps 1–7. `tasky add` runs steps 2 + 5–7 (no status change — new tasks are always `pending`).

---

## Task File Format (`{feature}/tasks/NN-kebab-title.md`)

```markdown
# Task [NN] — [Title]

STATUS: pending | active | completed
DEPENDS: [task numbers, comma-separated, or "none"]
MILESTONE: {roadmap}/{milestone}          ← optional; use MILESTONES for multiple
ISSUE: NNN                                ← optional; links to issues/NNN-slug.md
IMPACTS: [affected files/systems]
PROCESS: {domain/category or path}       ← optional; inferred if not set
REFERENCES: {brain entry IDs or paths}   ← optional
GUARDS: {constraints, things not to break} ← optional

## Description

[2–3 sentence overview of what this task does]

## Spec

[Technical requirements — subsections as needed]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
```

MILESTONE field:
- Omit entirely if not assigned to a roadmap
- Single milestone: `MILESTONE: product-v1/02-beta`
- Multiple milestones: `MILESTONES: product-v1/02-beta, product-v1/03-ga`
- Written automatically by `tasky milestone assign`

IMPACTS field: optional on existing tasks, always added to new tasks. Lists affected source files inferred from description — state "inferred from description" so the user can correct.

PROCESS / REFERENCES / GUARDS: optional. If not set on the task, inherited from the milestone. If still unset, PROCESS is inferred from domain context. These fields evolve — can be set at creation or updated during implementation.

---

## Commands

### `tasky list` (no feature — directory view)

1. Read `agents/docs/tasky/tasks/index.md`
2. Display each feature: name, milestone assignment, status summary
3. Ask which one to drill into

If `index.md` is missing, fall back to listing directories under `agents/docs/tasky/tasks/` and reading each feature's task manifest.

### `tasky list <feature>`

Read **only** `agents/docs/tasky/tasks/{feature}/tasks/index.md`. Print Tasks table with computed "Blocked by" column and `(next)` marker on first unblocked pending task.

```
auth - task list
────────────────────────────────────────────────────────────────────────────────
 ID   Title                              Status      Dep   Milestone

 01   Login flow                         completed   —     product-v1 / 02 - beta
 02   OAuth integration                  completed   —     product-v1 / 02 - beta
 03   2FA setup                          pending     —     product-v1 / 02 - beta
 04   RBAC permissions                   pending     03    product-v1 / 02 - beta
────────────────────────────────────────────────────────────────────────────────
Next unblocked: 03 — 2FA setup
```

Columns: ID (zero-padded), Title (left-aligned), Status, Dep (depends-on IDs comma-separated or `—`), Milestone (`roadmap / NN - name`). Mark next unblocked task with `(next)` after the row or in the footer.

### `tasky next <feature>`

Show first pending task with all deps completed. Print title, ID, one-line description.

### `tasky show <feature> <id>`

Read and display the full task file. ID can be `04`, `04-wire-up-ui`, or just the number prefix.

### `tasky done <feature> <id>`

1. Resolve task file path from feature + id
2. Run `status.py <task-file-path> done`
3. Suggest next unblocked task

### `tasky undone <feature> <id>`

1. Resolve task file path from feature + id
2. Run `status.py <task-file-path> undone`

### `tasky update <feature> <id>`

Read the task file and propose edits. Update fields as directed. Show diff summary. If status changes, apply the Status Cascade. If milestone field changes, update milestone files accordingly.

### `tasky create <feature>`

Create a new feature task set:

```
agents/docs/tasky/tasks/{feature}/
    index.md           ← skeleton with placeholders
    tasks/
        index.md       ← empty manifest (Tasks table + empty Dep Tree)
```

Append a row to `agents/docs/tasky/tasks/index.md` and to the top-level `agents/docs/tasky/index.md` Task Sets table. Prompt user to fill in description and goals.

### `tasky add <feature> "<description>"`

1. Scan `tasks/` for highest NN, increment by 1
2. Generate kebab-case filename from description
3. Infer `IMPACTS` from description (state "inferred from description")
4. Suggest `DEPENDS` based on open tasks touching the same areas
5. Create task file with Description and Acceptance Criteria placeholders
6. Append row to `tasks/index.md`, rebuild dep tree
7. Milestone cascade — if the new task has a `MILESTONE` field:
   - Add a row to the milestone file's Assigned Tasks table (status: `pending`)
   - Recompute Done/Total in the milestone file
   - Update milestone index: increment Total, recompute Status
   - Update roadmap index: recompute Status from milestone statuses
8. Print new file path and summary

```
tasky add
    │
    ├──► tasks/index.md           (append row, rebuild dep tree)
    │
    └── if MILESTONE set:
         │
         ├──► milestone file      (add row to Assigned Tasks, Total +1)
         ├──► milestones/index.md (Total +1, Status recomputed)
         └──► roadmaps/index.md   (Status recomputed)
```

### `tasky resequence <feature>`

1. Show current order
2. Accept new desired order from user
3. Rename files (e.g. `03-xxx.md` ↔ `04-xxx.md`)
4. Update all `DEPENDS` references across all task files
5. Rebuild dep tree in `tasks/index.md`
6. Print diff-style summary of renames and reference updates

### `tasky check-deps <feature>`

Validate the dependency graph:
- Missing references: depends on a number with no file
- Cycles: A → B → A
- Stale: task is pending but all deps completed → flag as "ready to start"
- Out-of-order: lower-number task depends on higher-number task

Print a clean report.

---

## File Naming

Task files: `NN-kebab-case-title.md` (zero-padded: 01–99, half-steps like `02.5` allowed).
Kebab-case: lowercase, spaces → hyphens, strip special chars, 3–5 words max.

---

## Safeguards

- Never delete task files — only rename or update Status
- When resequencing, always update `DEPENDS` references across all files
- When marking done, do not remove Acceptance Criteria — leave as record
- `tasky create` does not overwrite an existing feature without confirming with user
- Always use `status.py` for any task status change — never update index files manually
