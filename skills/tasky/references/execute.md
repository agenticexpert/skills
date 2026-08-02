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

**User names a milestone, or asks to work several tasks** — that is **Milestone Mode** below; take its tasks in sequence.

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

**If `## Task` is populated:** work from Task. Criteria is the acceptance gate.

**If `## Task` is empty:** Criteria is both the instruction and the acceptance gate.

Who checks the boxes off depends on the path: inline, whoever does the work, on verifying each item; under dispatch, the orchestrator from the receipt's verdicts (**State Ownership**).

If both Task and Criteria are empty (placeholder task), fill it in and proceed — don't ask permission to. Where milestone context yields enough to meet the bar in define.md → **Detail Levels**, write it, flip the status to `pending` per define.md → **Exit**, and execute. A name-only stub in a milestone with no description does not clear that bar and is genuinely un-inferable — that is a blocker (SKILL.md → **Deciding**, BLOCKER).

---

## Starting Work

**Which role you are.** You received a dispatch brief → you are the sub-agent; **State Ownership** binds you and you write no tasky state. No brief → you are the orchestrator: you own tasky state, and the work phase runs in a dispatched sub-agent unless **Running Inline** applies.

The rest of this playbook addresses the orchestrator.

Confirm the dispatchability precondition (**Dispatch Brief**) before writing any status — both its tests are decidable from the task file and disk. Not dispatchable → resolve it, or stop as a BLOCKER with the task left as it was.

Then set status to DOING:
```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> doing
```

**Resolve the flow** — you resolve it, not the sub-agent:

1. Check the task file's `Flow:` field
   - If it's a registered name → look up the path in `tasky.md` Flows table
   - If it's a path → use it directly
2. If the task has no `Flow:` → check `tasky.md` for a project-wide `FLOW:` default
3. If no flow resolves → the task executes directly

Resolve every path listed in `## References` to an absolute path. Whoever runs the work phase loads each into context before starting — don't work from memory when a reference exists.

If a flow resolves, whoever runs the work phase reads the flow file and executes its steps in order. `{task}` is where the task's criteria or Task instruction executes. See `.claude/skills/tasky/references/flow-spec.md` for full flow execution rules.

Then build the dispatch brief below.

---

## Dispatch Brief

Write a self-contained brief — never a pointer to the task file alone. Carry all eight as literal text:

1. Absolute repo root.
2. Absolute task-file path. The sub-agent reads it before starting, for the `## Task` instruction and the Criteria list it must return verdicts against.
3. The project / roadmap / track / milestone / task slugs.
4. The resolved flow file path (from **Starting Work**), or "no flow — execute the task directly". The sub-agent reads it and runs its steps in order, with `{task}` as the substitution point.
5. Every `## References` path, absolute. The sub-agent loads each before starting; it never works from memory when a reference exists.
6. The ownership rule, addressed to the sub-agent, in these words: "You write no tasky state — no `set-status`, no criterion checkboxes, no task-file or `project.json` edit — and you do not invoke tasky. Return a per-criterion verdict with its evidence; the orchestrator writes the boxes."
7. The blocker rule, addressed to the sub-agent, in these words: "You cannot ask. On an un-inferable decision, or a step that fails, stop, edit nothing further, and return BLOCKED plus the one question."
8. The receipt template — quote it verbatim from **The Receipt** below.

**Dispatchability precondition.** Dispatch only when both hold:

- The task is at least **Workable on disk** — Description plus Criteria-or-Task populated in the file, not discussed in chat (define.md → **Detail Levels**, **Exit**).
- Every `## References` path exists.

Under-specified → do not dispatch. Define it inline first per **Loading a Task**; when un-inferable, stop as a BLOCKER. A BLOCKER reached after the task is already at DOING → write `paused` before surfacing it.

A `## References` path that does not exist → repair it to the real path, or remove the entry when the material is gone. Either way, name the path and what you did with it in one line (validate.md → **Step 1 — Mechanical Checks**). Neither repairable nor removable → stop as a BLOCKER.

Check both tests on every dispatch, including each task of a parallel batch.

---

## State Ownership

You perform every write to tasky state — set-status, criterion checkboxes, task files, `project.json`. The sub-agent performs none.

The sub-agent returns a per-criterion verdict with its evidence. You write `[ ]` → `[x]` only for a verdict carrying evidence — the command that ran, the file that exists, the output that proves it.

**Stated cost:** criteria land only at receipt time. A run that dies loses partial progress. Re-dispatch from the first unchecked criterion.

Unchanged under dispatch: READY not DONE, the disk re-read before READY, and the report-form hand-back (**Completing**); DONE only on user confirmation; never create, rename, or resequence a task.

---

## Background Dispatch

Dispatch in the background. While the run is live the user sees one line from it — task slug and status DOING — and nothing else from the run.

**The sub-agent cannot ask.** On an un-inferable decision it stops, edits nothing further, and returns BLOCKED plus the one question. You set `paused` and surface it in SKILL.md → **Deciding** voice. A failed step returns BLOCKED the same way (flow-spec.md → **FAILURE BEHAVIOR**).

**Orphan rule.** On load, a task at DOING with no live dispatch in this session is resumable: re-read its criteria from disk and re-dispatch from the first unchecked one.

**Short receipt.** A receipt reporting COMPLETE while some criteria are NOT MET, with no BLOCKED question: write the boxes whose verdicts carry evidence, then set `paused` and surface the criteria that came back unmet. Do not re-dispatch them in place — a second attempt is the user's call.

### The Receipt

The sub-agent returns exactly this:

```
TASK: <slug>
STATUS: COMPLETE | BLOCKED
CRITERIA:
  <criterion text> — MET: <the evidence> | NOT MET: <what is missing>
FILES: <path, one line each>
BLOCKED: <the single question, or "none">
```

---

## Attaching to Work in Flight

When you are routed to a task already under way rather than starting it fresh, attach — do not restart.

Set DOING, then dispatch from the first criterion unchecked on disk. Never re-dispatch a criterion already `[x]`. A criterion already satisfied by evidence produced before the attach is checked off by you under **State Ownership**, not re-run.

---

## Milestone Mode

Serial by default — one dispatch live at a time.

Parallel dispatch is permitted only when all four hold:

1. The user asked for it explicitly.
2. For each task, you can name the file set it will touch from that task's `## References` and `## Task` text.
3. Those file sets are disjoint.
4. No task in the batch depends on another (**Before Starting**).

Any one unmet → serial. Maximum three concurrent.

---

## Running Inline

The user saying `inline`, "watch this", or "step through" executes this playbook in the main window with no dispatch.

Fall back to inline automatically when you are already running under a dispatch brief, or when you cannot dispatch — no dispatch tool available to you, or a dispatch attempt is refused.

An orchestrator running inline performs the state writes itself. A sub-agent under a brief never becomes the state owner on any path — it does the work and returns the receipt (**State Ownership**).

---

## Working

Work runs from the task's `## Task` instruction, or its Criteria when `## Task` is empty, or the flow sequence when one resolved — reached through the brief under dispatch, read directly when inline.

Under dispatch, return a per-criterion verdict naming its evidence; the orchestrator writes the boxes (**State Ownership**). Inline, check a box only when you can name its evidence.

If something unexpected surfaces — wrong assumption, missing piece, design conflict — surface it before continuing. Don't paper over it. Under dispatch that is a BLOCKED receipt; inline, tell the user.

---

## Pausing

If work must stop before completion:
```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> paused
```

Terminate any live dispatch before writing `paused`. No means of termination → dispatch nothing further and discard the receipt when it lands. Either way, criteria that receipt would have carried are not written.

Criteria already `[x]` on disk preserve what was done — inline, that is everything checked so far; under dispatch, only what a prior receipt already landed (**State Ownership**). When work resumes, pick up from the first unchecked criterion on disk (or the flow step containing it).

---

## Completing

All criteria checked → set status to READY, not DONE. READY means the work is done but has not been validated yet. The user must confirm before DONE is set.

Before setting READY, re-read the task file from disk — every criterion `[x]` in the file, not in your memory of the session. A criterion still `[ ]` means the work isn't done, whatever the conversation says.

```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> ready
```

Then hand back to the user. This hand-back is the step's ONLY user-facing output, and it ALWAYS takes the form in `references/report.md` — never a raw status line, never a machine dump. Cannot render the form → surface that as a blocker; never fall back to internals.

Fill the form from the criteria: `DONE:` states whether the work the user asked for is finished; the optional `NOTES:` tail names what the user should run or check to validate, and what each check should show. All criteria met → the minimal report, often just the `DONE:` line plus a short `NOTES:` tail carrying the validation step. Any criterion unmet → a `BLOCKED:` line names only the unmet ones, in plain language.

Never surface internals in the hand-back — criterion numbers, checkboxes, gate mechanics, `set-status`, directory slugs, the Receipt. What the user should test belongs in the `NOTES:` tail in plain language, not a separate machine `TO TEST` dump. Report CONTENT is governed by SKILL.md → **Deciding**, same as every other hand-back.

Wait. Do not mark DONE until the user confirms.

Once the user confirms:

```
python manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> done
```

---

## Writing a Task

When filling in a task before working it, follow define.md → **Writing the Task File** — the source of truth for field rules.

Empty tasks are valid placeholders. Fill them in when you're about to work them — that's when you have enough context to write them correctly.
