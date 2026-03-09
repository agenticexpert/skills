# issues — Log and Track Bugs and Defects

Lightweight issue tracking. Log it, link it to whatever resolves it, let the cascade close it.

---

## File Location

```
agents/docs/tasky/issues/
├── index.md          # all issues, scannable
└── NNN-slug.md       # individual issue files
```

---

## Intent Triggers

| User says… | Action |
|------------|--------|
| "bug:", "there's a bug", "log a bug", "found an issue", "something's broken" | → log issue |
| "that's fixed", "close the bug", "resolved", "fixed that" | → close issue |
| "discard", "won't fix", "not a bug" | → discard issue |
| "put that on the backburner" | → backburner issue |
| "list bugs", "what's open", "show issues" | → list open issues |
| "link issue NNN to task / milestone" | → link issue |

---

## Issue File Format (`issues/NNN-slug.md`)

```markdown
# Issue 001 — Drag flickers on fast move

**Type**: bug | debt | question
**Status**: backburner | active | complete | discarded
**Date**: 2026-02-21
**Detail**: Happens when pointer moves faster than ~500px/s. Only in Chrome.
**Resolved by**: —    ← task ref (tasks/core/04) or milestone ref (milestones/blocky/02)
```

---

## Index Format (`issues/index.md`)

```markdown
# Issues — Index

| ID  | Description                      | Type  | Status      | Resolved by     |
|-----|----------------------------------|-------|-------------|-----------------|
| 001 | Drag flickers on fast move       | bug   | active      | tasks/core/04   |
| 002 | Resize handle misaligned on zoom | bug   | complete    | milestones/blocky/03 |
```

---

## Linking to Tasks and Milestones

Add `**Issue**: NNN` to any task or milestone file to link it.

**Task file:**
```markdown
**Issue**: 001
```

**Milestone file:**
```markdown
**Issue**: 001
```

When the task or milestone status changes, `status.py` cascades to the issue:

| Task/Milestone status | Issue status |
|-----------------------|--------------|
| `active`              | `active`     |
| `completed`           | `complete`   |
| `pending` / `planned` | `backburner` |

The `**Resolved by**` field is set on first link and does not change on subsequent cascades.

---

## Commands

### Log an issue

1. Read `issues/index.md` for next ID (zero-pad to 3 digits)
2. Infer type from language
3. Create `issues/NNN-slug.md`
4. Append row to `issues/index.md`
5. Confirm: *"Logged bug 003 — drag flickers on fast move"*

### Close / discard an issue

1. Match by ID or keyword
2. Update **Status** in issue file + index row
3. Confirm: *"Closed issue 003"*

### Link to task or milestone

1. Find issue by ID or keyword
2. Set **Resolved by** in issue file (if not already set)
3. Update index row
4. Remind user to add `**Issue**: NNN` to the task or milestone file

### List issues

Show open issues (`backburner` + `active`) by default. User can ask for all or by type.

---

## Tone

Fast. User says *"bug — the drag is flickering"* — log it, confirm it, move on.
