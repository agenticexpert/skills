# Report — what the user reads when tasky hands back

The reader is the user: one person at a terminal who saw none of the work.

```
STATUS: <what the result means for you — one short sentence>

- <a fact>
  - <a detail of that fact>

[x] READY
  - <task>
[ ] Committed
  - <worktree> / <branch> / <task>

DOING NOW:
- You: <a step you can take meanwhile>
- <who: Me, Agent, Pi, GPT, BG or another>: <work running right now>

WAITING ON:
- <what holds the next step: an outside run, another person>

NEXT:  (THEN: when DOING NOW is shown)
  TEST IT:
    1. <what to do>
    2. <what to do>

    - <what you should see>
- Me: <my next step toward this task's goal>

DECIDE: <the choice, in terms of what you would notice>
  - <option>: <what it changes for you>
  - <option>: <what it changes for you>
```

**The one test, for every line:** does it matter to the user, knowing only this task's goal? A line with no consequence for them is cut: what was run or checked, how it works inside, a warning that changes nothing they do now, a choice made or the options weighed except as SKILL.md **Deciding** 5 keeps it. A reason stays when it says what the result means for them.

`STATUS:` always comes first and says what the result means for the user, in plain words. Never words that read as finished for work that isn't. A second point is its own bullet.

The checklist follows STATUS and its bullets: where this report's tasks stand and what of their work is committed. It covers this task and its milestone only, never other sessions' work or the rest of the repo. Each row is a box and a label, with the tasks under it by their plain names (the task file's title):
- `[x] READY`: every task in this milestone standing at READY, waiting for the user's "done", the ones set earlier included. A report on a task that is not at READY shows it under `[ ] READY`. A task hand-back always has a READY row.
- `[x] PAUSED`, `[x] DONE` or another status: a task this turn set to it. A status no task took this turn gets no row.
- `[x] Committed`: this report's tasks whose work is committed; `[ ] Committed`: those whose work is not. Each as `<worktree> / <branch> / <task>`, or `main / <task>` on the main line.
A row with no task under it is left out. Every other section appears only when a line in it passes the test. Every step line starts with who acts, the user's steps first: `You:` the user; `Me:` this chat; `Agent:` an agent this chat started; `Pi:` a pi run; `GPT:` a Codex run; `BG:` a command running in the background; anyone or anything else, by a short name for it (`CI:`, `Gemini:`, a person's name). `DOING NOW:` holds each of those running at this moment, and any step the user can take meanwhile. With `DOING NOW:` shown, `THEN:` names what comes after it: the next step and who takes it, or the next task. It never holds a step of the user's; theirs shows once the running work ends. With nothing running, the steps go under `NEXT:`. Either holds only steps no one has started. Every report shows what moves the work on: `DOING NOW:` with who runs it, `NEXT:`, or `DECIDE:`. With nothing running and no real decision, `NEXT:` names the next task and what it produces; never a prompt to close or mark a task done, the user does that when they choose. Outside the Committed row, never git state (committed or not, pushed, merged, which branch, uncommitted files) unless the user asked or it blocks a step of theirs; never a prompt to commit or push, a count of tasks left, or a pointer at others waiting. `WAITING ON:` lists only what is outside the session and holds a later step: an outside run, another person. The user's answer is a `DECIDE:`. When the next step is the user trying the work, `NEXT:` holds a `TEST IT:` block: numbered actions, then what the user should see, as bullets.

`DECIDE:` holds only a choice SKILL.md **Deciding** 2 lets surface; closing a task is never one. It names the choice by what the user would notice and what each option changes for them, its cost included. An option the builder would recommend is not a DECIDE: the builder takes it. A choice that can only be named in code terms is not a DECIDE.

```
STATUS: CSV export is on the reports page and matches the table, but large reports are slow.

- large reports take twice the target time
  - target: 2 seconds

[ ] READY
  - CSV export
[x] Committed
  - reports / reports-v2 / CSV export

DOING NOW:
- Agent: streaming exports

THEN:
- Me: time a large export against the target
```
