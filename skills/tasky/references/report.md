# Report — what the user reads when tasky hands back

The reader is the user: one person at a terminal who saw none of the work.

```
STATUS: <where this task stands — one short sentence>

- <a fact>
  - <a detail of that fact>

NEXT:
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

`STATUS:` always comes first. Every other section appears only when a line in it passes the test. When the next step is the user trying the work, `NEXT:` holds a `TEST IT:` block: numbered actions, then what the user should see, as bullets. Every other `NEXT:` line starts with who acts, `You:` or `Me:`. The user's steps come first; a step of the builder's that runs meanwhile says so.

`DECIDE:` appears only when the task cannot finish without the user's answer. It names the choice by what the user would notice, what each option changes for them, the builder's pick, and what only the user knows that could change it. A choice that does not block the task, or that can only be named in code terms, is not a DECIDE.

```
STATUS: CSV export is on the reports page and matches the table.

- large reports take twice the target time
  - target: 2 seconds

NEXT:
- Me: streaming exports
```
