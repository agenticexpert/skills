# Report Form — the shape of a task summary / action hand-back

The canonical shape for any user-facing moment where a skill hands back a **task
summary** or tells the user **what to do next**. It exists to kill machine-register
hand-backs — criterion numbers, internal step/surface names, invented busywork —
and force plain, actionable language a human can act on at a glance.

This is the ONLY copy. Skills point here; they never paste the form inline (copies
drift). Used by tasky's hand-back and singleshot's `report` step, each gated by its
own trigger — see those pointers for when it fires.

## The form

```
WHERE: … (max 15 words)
WHEN: … (terse, concise)
DO:
  - (terse step 1)
  - (terse step n)
WHAT:
  - (terse) what I'm looking for 1
  - (terse) what I'm looking for n
NOTE:
  - (terse) only if something MANDATES attention
  - n
```

## Rules

- **Every section is optional.** Emit only the sections that carry information; drop
  the rest. This is never a fixed skeleton with empty fields to fill.
- **WHERE / WHEN / DO / WHAT appear only when there is something to do** — an action
  the reader must take.
- **NOTE appears only when the reader cannot act without it** — something that
  mandates attention.
- **When there are no steps** — nothing for the reader to do — **NOTE alone stands
  as the summary**, and every other section is omitted.
- Terse throughout. Plain human instructions, not a linter checklist. No criterion
  numbers, no internal step/surface names, no busywork the reader didn't ask for.
