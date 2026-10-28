# Report — what the user reads when tasky hands back

The reader is the user: one person at a terminal who saw none of the work.

```
STATUS: <where this task stands — one short sentence>

- <a fact>
  - <a detail of that fact>

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
  - my pick: <option> — <what only you know that could change it>
```

**The one test, for every line:** would the user, knowing only this task's goal, see at once why the line is there? No → cut it. Nothing else earns a line — not a reason, a comparison, a warning about later work, or how it works inside. A warning stays only when it is severe enough that the user must change course now.

`STATUS:` always comes first. Each line holds one sentence; a second fact is its own bullet. Every other section appears only when a line in it passes the test. Every step line starts with who acts, the user's steps first: `You:` the user; `Me:` this chat; `Agent:` an agent this chat started; `Pi:` a pi run; `GPT:` a Codex run; `BG:` a command running in the background; anyone or anything else, by a short name for it (`CI:`, `Gemini:`, a person's name). `DOING NOW:` holds each of those running at this moment, and any step the user can take meanwhile. With `DOING NOW:` shown, `THEN:` names what comes after it: the next step and who takes it, or the next task. It never holds a step of the user's; theirs shows once the running work ends. With nothing running, the steps go under `NEXT:`. Either holds only steps no one has started. Every report shows what moves the work on: `DOING NOW:` with who runs it, or a `You:` step or `DECIDE:` for what the user does next. With nothing running, the next step is the user's, even when it is only saying go on the next task. `WAITING ON:` lists only what is outside the session and holds a later step: an outside run, another person. The user's answer is a `DECIDE:`. When the next step is the user trying the work, `NEXT:` holds a `TEST IT:` block: numbered actions, then what the user should see, as bullets.

`DECIDE:` appears only when the task cannot finish without the user's answer. It names the choice by what the user would notice, what each option changes for them, the builder's pick, and what only the user knows that could change it. A choice that does not block the task, or that can only be named in code terms, is not a DECIDE.

```
STATUS: CSV export is on the reports page and matches the table.

- large reports take twice the target time
  - target: 2 seconds

DOING NOW:
- Agent: streaming exports

THEN:
- Me: time a large export against the target
```
