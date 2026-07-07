# Decide Playbook

Surface unresolved decisions and resolve them with the user.

`/mem decide` — also runs as `/mem continue decide`.

Sources — merge both:

1. The decision trigger's log (default `.agents/mem/logs/decisions.md`) — entries with Status `Identified` or `Ignored`
2. The current summary — wherever the composed format tracks unresolved decisions (the default's `<meta>` list), with full context from the summary body

Steps:

1. Collect open decisions. None → say so, stop.
2. Present each: title, context summary, the exact question asked — verbatim where captured, else reconstructed and marked so — options discussed, why still open, and whether later conversation weakened or strengthened the need to decide.
3. Ask which to address. Each resolution: append to the log as `Made` with `Supersedes: {prior title}` — the entry carries the resolution into the next summary.
4. Declined decisions stay open — no status change.
