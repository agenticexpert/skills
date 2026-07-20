# Execute Playbook

The user wants to work a task. Identify which task, load it, do the work, update it.

---

## Identifying the Task

**User names a specific task** — resolve it (alias if needed) and load it.

**User says "continue" or "resume"** — if there is a DOING task in the known milestone context, that is the task. If the milestone isn't known, infer it from the conversation thread, or from the sole DOING task. Only when neither exists is it a blocker (SKILL.md → **Deciding**, BLOCKER).

**User says "start the next one" / "skip ahead" / "skip it"** — the explicit skip. Match this before the bare "next" case below. Pause the DOING task per **Pausing**, then take the first task in sequence *after that one* with status `pending` or `paused`. Never re-select the task just paused.

**User says "next"** (bare) — two cases:
- A DOING task exists in the milestone → resume it, and say so in one line: *"Resuming `{doing-task}`. Say 'start the next one' to switch."* No menu.
- No DOING task exists → first task in sequence with status `pending` or `paused`. If the next task is `todo` (undefined stub), define it inline from milestone context — the content bar is define.md → **Detail Levels** and **Writing the Task File**, the status flip to `pending` is define.md → **Exit** — then execute. State what you wrote.

If the milestone context isn't known in any case, resolve it per navigate.md → **Resolving References**. Only when discovery returns nothing is it a blocker.

**Anything else ambiguous** — resolve by best match, state the assumption in one line, and proceed. Surface only a blocker or a negative ripple (SKILL.md → **Deciding**).

---

## Before Starting

Verify all declared dependencies are DONE. If any are not, a dependency that can itself be started is the next action — start it. Only one that cannot is a blocker: name it and stop (SKILL.md → **Deciding**, BLOCKER).

---

## Loading a Task

Read the task file. Fields:

- **Description** — 1-2 sentence overview of what this task is
- **Goal** — what this task produces or achieves
- **Criteria** — checkboxes. Always the acceptance gate. May also be the instruction (see below).
- **References** — paths to specs, design docs, or other material. Load each into context before working.
- **Task** — the instruction. If populated, this is what to do. Written in impact/execution form.

**If `## Task` is populated:** work from Task. Criteria is the acceptance gate — check each item off when verified.

**If `## Task` is empty:** Criteria is both the instruction and the acceptance gate. Work each item, check it off when done.

If both Task and Criteria are empty (placeholder task), fill it in and proceed — don't ask permission to. Where milestone context yields enough to meet the bar in define.md → **Detail Levels**, write it, flip the status to `pending` per define.md → **Exit**, and execute. A name-only stub in a milestone with no description does not clear that bar and is genuinely un-inferable — that is a blocker (SKILL.md → **Deciding**, BLOCKER).

---

## Starting Work

Set status to DOING:
```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> doing
```

Load every path listed in `## References` into context before starting. Don't work from memory when a reference exists.

**Resolve the flow:**

1. Check the task file's `Flow:` field
   - If it's a registered name → look up the path in `tasky.md` Flows table
   - If it's a path → use it directly
2. If the task has no `Flow:` → check `tasky.md` for a project-wide `FLOW:` default
3. If no flow resolves → execute the task directly

If a flow resolves, read the flow file and execute through its steps in order. `{task}` is where the task's criteria or Task instruction executes. See `.claude/skills/tasky/references/flow-spec.md` for full execution rules.

---

## Working

Work through the task (or flow sequence if declared). When each criterion is satisfied, check it off:
- `[ ]` → `[x]`

Check a box only when you can name its evidence — the command that ran, the file that exists, the output that proves it. A box checked ahead of the work is exactly the rubber-stamping validate.md exists to catch.

If something unexpected surfaces — wrong assumption, missing piece, design conflict — tell the user before continuing. Don't paper over it.

---

## Pausing

If work must stop before completion:
```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> paused
```

Checked criteria preserve what was done. When work resumes, pick up from the first unchecked criterion (or the flow step containing it).

---

## Completing

All criteria checked → set status to READY, not DONE. READY means the work is done but has not been validated yet. The user must confirm before DONE is set.

Before setting READY, re-read the task file from disk — every criterion `[x]` in the file, not in your memory of the session. A criterion still `[ ]` means the work isn't done, whatever the conversation says.

Before setting READY, report a numbered list headed `TO TEST:` — one line per entry, each naming a single action the user takes and the result they should see, derived from the task's criteria.

```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> ready
```

Tell the user the task is ready for validation. Wait. Do not mark DONE until they confirm.

Once the user confirms:

```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> done
```

---

## Writing a Task

When filling in a task before working it, follow define.md → **Writing the Task File** — the source of truth for field rules.

Empty tasks are valid placeholders. Fill them in when you're about to work them — that's when you have enough context to write them correctly.
