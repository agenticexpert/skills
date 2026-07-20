# Structure Playbook

The user wants to create, rename, resequence, or restructure the hierarchy. Execute precisely. State what you're writing, then write it — confirm first only when the change is destructive or lossy (SKILL.md → **Deciding**).

---

## Hierarchy Rules

```
{root}/
  {project}/                  ← no prefix
    project.json              ← ALL ordering and deps metadata, script-managed only
    {roadmap}/                ← no prefix
      {track}/                ← no prefix
        {milestone}/          ← no prefix, e.g. backend-api/
          {task}.md           ← no prefix, e.g. application-model.md
```

- **No `nn-` prefixes anywhere.** Filenames are plain slugs at every level.
- **All ordering lives in `project.json`** — roadmaps, tracks, milestones, and tasks each have an ordered array.
- The slug is the stable identity for dependency references.
- No files at project, roadmap, track, or milestone level. Directory existence is the record.

### project.json schema

```json
{
  "roadmaps": ["v1", "v2"],
  "tracks": {
    "v1": {
      "order": ["scaffolding", "core", "api", "polish"],
      "deps": {
        "core": ["scaffolding"],
        "api": ["core"],
        "polish": ["api"]
      }
    }
  },
  "milestones": {
    "v1/scaffolding": ["project-setup"],
    "v1/api": ["endpoints"]
  },
  "tasks": {
    "v1/scaffolding/project-setup": [
      "repo-init", "ci-setup", "base-layout", "env-config"
    ]
  },
  "focus": {
    "hide": {
      "roadmaps": ["v2"],
      "tracks": { "v1": ["polish"] },
      "milestones": { "v1/api": ["endpoints"] }
    }
  }
}
```

The `#` (seq) shown in views is derived at render time from position in these arrays — never stored.

`focus.hide` is optional. All items are in-focus by default. Items in the hide lists are suppressed from views unless `--all` is passed. Totals always reflect the full project regardless.

---

## Alias Resolution

Users will use natural names that may not match directory slugs. Resolve every natural-language name before calling any script, per navigate.md → **Resolving References**.

---

## Creating Structure

### State, Then Write

State what you're creating, then run the script. Do not wait for confirmation.

```
Creating:
  {root}/my-project/
  {root}/my-project/project.json
  {root}/my-project/v1/
  {root}/my-project/v1/core/
```

**Confirm first only when the write is destructive or lossy.** That is a NEGATIVE RIPPLE (SKILL.md → **Deciding**, 2b): name what would break, in one line, and wait. Which writes those are, by what each script does to dependency references:

| Write | Reference handling | Verdict |
|---|---|---|
| Create (any level), batch create | Cannot clobber — the script errors if the slug already exists | Proceed |
| Cross-parent move of a **track**, **milestone**, or **task** | Script checks inbound/outbound deps and blocks an invalid move | Proceed |
| Cross-parent move of a **roadmap** | No dep check at all; `focus.hide` and the Gantt slot maps are not migrated | **Confirm**, then re-apply hide and slot entries at the destination |
| Resequence (same parent) | **Not validated** — the script warns and writes anyway | Proceed, then verify no dependency now sits after its dependent |
| Rename a **track**, **milestone**, or **roadmap** | Script rewrites the dependency keys and references in `project.json`. It does *not* update `milestone_slots` or `track_slots`, and track/milestone rename does not update `focus.hide` — a renamed hidden item silently unhides and its Gantt slot reverts to default | Proceed, and re-apply the slot or hide entry if one existed |
| Rename a **project** | Renames the directory only — `project.json` is never opened, so `oob_roadmaps` (keyed by project name) is orphaned and every out-of-band roadmap silently reverts to in-band | **Confirm** — name the OOB markings that will be lost, then re-apply them |
| Rename a **task** | Script updates the `order` arrays only. Sibling tasks' `Dependencies:` lines still name the old slug | **Confirm** — name the tasks that would break |
| Delete a **task** | Inbound deps unchecked; sibling `Dependencies:` lines left dangling | **Confirm** — name what depends on it |
| Delete a **track**, **milestone**, or **roadmap** | Inbound deps unchecked, and references to the deleted item are silently stripped from `project.json` — the dependency is discarded, not dangling. Track and milestone delete also leave a stale `focus.hide` entry, so recreating the slug later comes back hidden | **Confirm** — name what depended on it |
| `remove-dep` | Discards a declared dependency | **Confirm**, including when clearing a dep to unblock a move |
| `hide` / `unhide` | Changes what every view shows; no data loss | Proceed |

After a confirmed task rename or delete, fix the dangling `Dependencies:` lines in the affected task files — the script does not.

### Project

```
python .claude/skills/tasky/scripts/manage_projects.py create-project <slug>
```

Creates `{root}/{slug}/` and an empty `project.json`.

### Roadmap

```
python .claude/skills/tasky/scripts/manage_roadmaps.py create <project> <slug>
```

Creates `{root}/{project}/{slug}/` and appends to `project.json["roadmaps"]`.

### Track

```
python .claude/skills/tasky/scripts/manage_tracks.py create <project> <roadmap> <slug>
```

Creates `{root}/{project}/{roadmap}/{slug}/` and appends to `project.json["tracks"][roadmap]["order"]`.

### Milestone

```
python .claude/skills/tasky/scripts/manage_milestones.py create <project> <roadmap> <track> <slug> [--insert <n>] [--deps <slug,...>]
```

- `--insert <n>` — places at position n in the order array (1-based), shifting others down.
- No flag — appends to end.

Creates the directory and registers in `project.json["milestones"]`.

### Task

```
python .claude/skills/tasky/scripts/manage_tasks.py create <project> <roadmap> <track> <milestone> <slug> [--insert <n>] [--deps <slug,...>]
```

- `--insert <n>` — places at position n in the order array (1-based).
- No flag — appends to end.

Creates `{slug}.md` with the standard template and registers in `project.json["tasks"]`.

---

## Status Lifecycle

`todo` → (define) → `pending` → (start) → `doing` → (finish) → `ready` → (validate) → `done`. `paused` = on hold; `x` = not applicable. Full definitions live in `define.md` — the source of truth.

New tasks are created with `Status: TODO`. The define step moves them to `PENDING`.

---

## Task Template

```markdown
# {Title}

Status: TODO
Dependencies: [{dep-slug}, ...]
Flow:

## Description


## Goal


## Criteria


## References


## Task

```

Leave Dependencies empty if none. Description, Goal, Criteria, and Task start empty — they fill in during execution.

**Body rules (validate enforces these):**
- `## Criteria` must contain at least one checkbox item, and every box must be checked before status can reach READY or DONE
- `## References` entries must be file paths only — one per bullet, bare or backtick-wrapped; no prose, no wikilinks
- `Dependencies` slugs must all be DONE before this task can be marked DONE

---

## Resequencing (same parent)

```
python .claude/skills/tasky/scripts/manage_milestones.py move <project> <roadmap> <track> <slug> --insert <n>
python .claude/skills/tasky/scripts/manage_tasks.py move <project> <roadmap> <track> <milestone> <slug> --insert <n>
```

Reorders within the parent's array in project.json. No filesystem changes.

Tracks resequence the same way: `manage_tracks.py move <project> <roadmap> <slug> --insert <n>`.

**The script does not validate this — it only prints a warning and writes anyway.** After any resequence, check the moved item's dependencies yourself: if a dependency now sits after its dependent, say so and fix the order. Cross-parent moves (below) *are* validated for tracks, milestones, and tasks; same-parent resequencing never is.

---

## Moving to a Different Parent (cross-parent)

Any item can be moved to another valid container of the same type:

| Item | Moves to | `--dest` format |
|---|---|---|
| task | different milestone | `roadmap/track/milestone` |
| milestone | different track | `roadmap/track` |
| track | different roadmap | `roadmap` |
| roadmap | different project | `project` |

```
python .claude/skills/tasky/scripts/manage_tasks.py move <...path...> <slug> --dest <roadmap/track/milestone> [--insert <n>]
python .claude/skills/tasky/scripts/manage_milestones.py move <...path...> <slug> --dest <roadmap/track> [--insert <n>]
python .claude/skills/tasky/scripts/manage_tracks.py move <project> <roadmap> <slug> --dest <roadmap> [--insert <n>]
python .claude/skills/tasky/scripts/manage_roadmaps.py move <project> <roadmap> --dest <project> [--insert <n>]
```

**Dep validation blocks the move** if any sibling dependency would be broken:
- Outbound: deps the moving item holds on old siblings
- Inbound: old siblings that depend on the moving item

If conflicts exist, the script errors with the list of affected deps. Resolve them first with `remove-dep`, then retry the move.

---

## Adding Dependencies

```
python .claude/skills/tasky/scripts/manage_tasks.py add-dep <...path...> <slug> <dep-slug>
python .claude/skills/tasky/scripts/manage_milestones.py add-dep <...path...> <slug> <dep-slug>
python .claude/skills/tasky/scripts/manage_tracks.py add-dep <project> <roadmap> <track> <dep-track>
```

Dependencies are always scoped to siblings. Validate before writing.

---

## Track Ordering and Dependencies

```
python .claude/skills/tasky/scripts/manage_tracks.py add-dep <project> <roadmap> <track> <dep-track>
```

This writes to `project.json["tracks"][roadmap]["deps"]`. Never edit `project.json` directly.

The view scripts topologically sort tracks by their deps — so the track that must go first appears first.

---

## Setting Focus (Hide / Unhide)

Focus controls which roadmaps, tracks, and milestones are visible in views by default. Everything is in-focus unless explicitly hidden.

### Hide

```
python .claude/skills/tasky/scripts/manage_roadmaps.py hide <project> <roadmap>
python .claude/skills/tasky/scripts/manage_tracks.py hide <project> <roadmap> <track>
python .claude/skills/tasky/scripts/manage_milestones.py hide <project> <roadmap> <track> <milestone>
```

### Unhide

```
python .claude/skills/tasky/scripts/manage_roadmaps.py unhide <project> <roadmap>
python .claude/skills/tasky/scripts/manage_tracks.py unhide <project> <roadmap> <track>
python .claude/skills/tasky/scripts/manage_milestones.py unhide <project> <roadmap> <track> <milestone>
```

**Rules:**
- OOB items cannot be hidden (they're already separate).
- Hidden items are excluded from all view rows by default.
- Totals (progress bars, task counts) always include hidden items — true state is never obscured.
- `--all` on any view script reveals hidden items marked with `~`.

---

## Batch Creation

When creating a full structure from a plan session, build top-down:

1. State the complete structure you're creating.
2. Run scripts strictly in this order — each level must exist before the next is created:

```
1. project       manage_projects.py create-project
2. roadmap       manage_roadmaps.py create
3. track(s)      manage_tracks.py create          (all tracks for this roadmap)
4. milestone(s)  manage_milestones.py create       (all milestones per track)
5. task(s)       manage_tasks.py create            (all tasks per milestone)
```

Never create a child before its parent exists.

If any script errors mid-batch, stop — do not run children of a failed parent. Report what was created and what wasn't, from the scripts' actual output. Never report the batch complete on partial success.
