# Augment: Decisions Section

Worked example of an augment file — apply with `/mem summarize using .claude/skills/mem/references/augments/decisions.md`.

ADD SECTION `<decisions>` after `<requirements>`

For every decision in the conversation, in chronological order:

```text
DECISION T{n}: {title}
ASKED: {the question or choice point}
DECIDED: {what was chosen}
WHY: {reasoning — trade-offs, constraints}
STATUS: Final | Provisional | Open
```

Open decisions preserve the exact question verbatim.

If the decision trigger is active, fold from .agents/mem/logs/decisions.md instead of re-deriving.

SLOT after `<meta>`

Add a line: `decisions: {n} total, {m} open`.
