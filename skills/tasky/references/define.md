# Define Playbook

The user wants to define one or more tasks — figuring out what they contain, writing them up, or fleshing out stubs. This is not executing. It's making tasks workable.

---

## Status Lifecycle

```
todo → pending → doing → paused (back to doing)
                       → ready → done
```

| Status | Meaning |
|---|---|
| `todo` | Stub — exists in the sequence but not yet defined (empty or near-empty) |
| `pending` | Defined and ready to execute — waiting to be picked up |
| `doing` | Actively being worked |
| `paused` | Started but on hold — criteria preserve partial progress |
| `ready` | Work complete, awaiting user validation |
| `done` | Validated and closed |
| `x` | No status — not applicable |

**Define moves a task from `todo` → `pending`.** A task should not be executed until it is at least `pending`.

---

## What You're Doing

Turning a milestone or stub into tasks that are ready to execute. The goal is not a complete plan — it's enough definition to be actionable.

Tasks don't all need the same level of detail. Define each task at the level it needs to be executable. No more.

---

## Starting Point

Three entry points:

**Milestone with no tasks** — surface what the tasks are, stub them in sequence.

**Stub tasks that need fleshing out** — identify which ones and fill them in from milestone context: the sequence, the neighbouring tasks, the milestone description. Ask only for fields genuinely un-inferable (SKILL.md → **Deciding**).

**A specific task to define** — focus on that one task, ask the minimum to make it workable.

Load the milestone's tasks with:
```
python {skills}/scripts/manage_tasks.py list <project> <roadmap> <track> <milestone>
```

---

## Surfacing Tasks for a Milestone

If no tasks exist yet, ask:

- What does this milestone deliver? What's true when it's done that wasn't true before?
- What's the first thing that has to happen?
- What are the discrete pieces — things that could be reviewed or verified independently?
- What can't start until something else finishes?

From the answers, propose a task sequence. Name them, order them, surface dependencies. Don't detail yet — create them first.

Create stubs:
```
python {skills}/scripts/manage_tasks.py create <project> <roadmap> <track> <milestone> <slug>
```

State the sequence, then move to detail. Wait for a reply only when the user is actively shaping the breakdown with you — never when a single stub is being defined inline on the way to executing it (execute.md → **Identifying the Task**).

---

## Detail Levels

**Stub** — name only. Exists so it isn't forgotten. Valid to execute from if context is obvious.

**Loose** — Description filled in. One or two sentences. Enough that someone coming cold understands what it is.

**Workable** — Description + either Criteria or Task populated. Enough to execute without asking questions mid-task.

**Detailed** — Full task: Description, Goal, Criteria, References, Task instruction. Used when the work is complex, has precise acceptance requirements, or the interface needs to be exactly right.

The task being worked next should be at least Workable. Everything else can stay Stub or Loose.

---

## Defining a Single Task

Ask only what's needed to reach the target detail level:

**To make it Workable:**
- What does this task produce or change?
- What are its steps, in order? (each becomes a Criteria box)
- Is there anything it should explicitly not do?

**To make it Detailed:**
- What's the instruction? What exactly should be built? (surfaces Task section)
- Are there references — specs, designs, prior tasks — that inform this?
- What does it depend on? Only a task that is not DONE is a dependency.

Write the answers into the task file. Don't ask for information you can infer from context.

---

## Writing the Task File

Fill in only what's needed. Leave sections blank if they add no value.

- **Description** — what this task is. 1-2 sentences.
- **Goal** — the outcome. One clear sentence: "Produces X" or "Enables Y."
- **Criteria** — verifiable items. If Task is empty, Criteria is both the instruction and the gate. A task is one piece of work with one result; it usually takes several steps. Write each step as one checkbox, in the order the work goes, ticked as the work goes. Write tight, checkable items — "Passes test X" beats "works correctly." Each item traces to something the user, the goal, a spec, the milestone or a standard the project follows asks for.
  - When a box has its own result and could be started, finished or reviewed apart from the rest: make it its own task.
  - When a box names a whole family ("each kind of X", "every rule in Y"): it is several tasks; make each its own task.
  - When a box is an outcome check standing in for the steps ("it works on the 6502"): replace it with the steps.
  - When a box or task can't be done without another task's work, or repeats part of it: it is a step of that task; fold it in as a box there.
  - A criterion the user checks by hand must be checkable the moment the task's own work lands — every screen, command and file it needs exists by then. If it waits on a later task, it belongs in that task.
- **References** — only paths that will actually be read during execution, and every file any line of the task cites or draws a fact from.
- **Task** — the instruction in impact/execution form. What to do and what it achieves — not background. If populated, Criteria becomes the acceptance gate only.

When the task adds a component, control, function or style: search the project for one that already does the job, by what it does and by the name the user sees. Name the one found in the task and tell the builder to use it, or to extract it when it sits inside another file. Name a new one only when the search finds none, and say so in the task.

---

## Exit

Gate the flip: re-read the task file first. `pending` requires the target detail level actually on disk — Workable means Description plus Criteria-or-Task populated in the file, not discussed in chat. Flipping a stub to `pending` puts an unexecutable task in the ready queue.

When the task or tasks are defined at the right detail level for what's coming next, set status to `pending`:

```
python {skills}/scripts/manage_tasks.py set-status <project> <roadmap> <track> <milestone> <slug> pending
```

The user can execute immediately or come back later. If executing now, hand off to execute.md.
