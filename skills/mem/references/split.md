# Split Playbook

Siphon one idea, topic, or discussion thread out of this conversation into a standalone file. The output must let someone resume the thread in a fresh conversation without the original context.

`/mem split {idea} [to {path}] [and prune]` — default `.agents/mem/ideas/{slug}.md`, slug derived from the idea title.

Split is a fork — the main line keeps the thread. `and prune` cuts it: the topic goes to `.agents/mem/summary/.prune_log` and the next summarize drops it from the main line.

## Rules

- An existing file at the output path is a prior split — read it first; keep its Genesis, extend Evolution and Current State.
- Auto-detect where the idea first emerged; trace it chronologically to current state.
- Preserve decisions and rejections with reasoning — what was chosen, what wasn't, why.
- Artifacts exact: code, commands, errors, outputs verbatim. Never summarize artifacts.
- Rabbit holes that yielded nothing: one line.
- Unrelated threads: excluded.
- Tangents worth keeping: list at the end as atomic one-liners — don't inflate the main narrative.
- In doubt, keep more, not less.

## Output Format

```markdown
# {Idea Title}

> Captured: {ISO date}
> Source: {one line — the conversation context}

## Genesis
What triggered the idea, initial framing.

## Evolution
Chronological development — phases, Q&A that shaped it, decisions and rejections with reasoning.

## Current State
Where the idea stands: decided approach, open questions, next steps.

## Artifacts
Code, commands, examples — verbatim.

## Related Atomic Ideas
- {idea}: {one line} — connection to the main thread.
```

## Delivery

1. Write the file to the output path.
2. Report: "`{path}` ready — `/mem continue from {path}` or a plain read resumes it." Note when a prior split was extended.
3. `and prune` → confirm the topic is logged for pruning at the next summarize.
