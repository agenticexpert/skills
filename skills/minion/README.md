# Minion

**Minion delegates one tracked task — or a whole milestone — to a headless sub-agent, so the heavy work (reads, edits, test output) stays out of your main conversation and only a compact summary comes back.**

You stay the orchestrator. Minion does not do the task in your window; it resolves the task, gates its dependencies, dispatches a sub-agent to run the spec end-to-end, and relays the result. The main context stays small; the work still gets done in full.

> **Twin of [seq](../seq/README.md).** Same task loop, different venue. Minion *delegates* (headless, cheap context, can't see this chat). Seq runs the same sequence *inline* (costs main tokens, but sees the conversation and lets you course-correct mid-run). Mix them per task — they share one audit ledger.

---

## When to Use

- Routine, well-specified grind you don't need to watch — the ideal delegation candidate.
- A milestone of tasks: minion runs one sub-agent per task, in dependency order, pausing after each.
- Anytime the main window is filling and the work doesn't need chat context.

**Poor candidate** — a task spanning 3+ unrelated subsystems, or exploratory work with no clear spec. Minion says so and recommends running it in main.

---

## How to Load It

Minion is a semantic skill. Name the task and Claude loads it.

Examples:

- "Minion task `<name>`." · "Delegate the auth-refactor task."
- "Run milestone `<x>` in subagents."
- "Execute this without burning main context."

Force it by name: `/minion`.

---

## How It Runs

The flow is fixed: **resolve → gate → self-contained check → (optional pre-flight) → dispatch → relay + pause.**

- **Task source** — minion needs `resolve` (name → spec path), `gate` (dependencies + status), and `expand` (milestone → task list). It binds a source in priority: named inline ("use tasky"), declared by the project's `CLAUDE.md`, or a direct spec path. It never invents a task layer, and never blocks on a missing tracker.
- **Self-contained check** — the sub-agent can't see your chat, so any decision that lives only in the conversation must be written into the spec first. Minion stops and offers to add the line rather than dispatch an under-specified task.
- **Pre-flight audit** — for architectural or uncertain work, minion audits narrow in main (locate before read, read narrow), surfaces concerns, and pauses for spec edits before dispatching.
- **Audit ledger** — every audit records one `LEDGER:` line. A later task on the same surface reuses it instead of re-auditing. The ledger is shared with seq, so `/seq` task 1 then `/minion` task 2 can reuse the same audit.

When the sub-agent returns, minion relays a terse `DONE` summary and pauses — or, on `ABORTED`, translates the sub-agent's spec-term blocker into a plain-words decision through its clarifier block.

**Hard rules:** never commits, bumps versions, or edits changelogs; never creates or resequences tasks (the source's job); one task per sub-agent.

---

## Customizing Sequences

Minion runs the `standard` loop by default — `audit-before → work → audit-after → report`, baked into the dispatch it hands the sub-agent. You can point it at a different sequence without editing the skill.

**Set the default.** minion reads the project sequence file `.agents/seq/sequences.md` — the same file [seq](../seq/README.md) uses. Give it a `Default:` line and every bare `/minion <task>` runs that sequence. Because the sub-agent is headless (below), define any non-core step right in the file:

```text
Default: reviewed

## Registry
| Name     | Steps                                                     | Use for |
|----------|-----------------------------------------------------------|---------|
| reviewed | audit-before → work → audit-after → double-check → report | Always re-read before report. |

## Step Library
### double-check
- Re-read the diff against the spec's Criteria with fresh eyes; list any gap found.
- EXIT ARTIFACT: a pass / concerns verdict (empty allowed).
```

**For a single run,** pick any sequence defined in that file by name: `/minion <task> as reviewed`. (Minion has no registry of its own — the four core steps aside, the sequences it can run are the ones in this file.)

**Restore:** delete the file, or drop the `Default:` line, to go back to `standard`.

**One limit — headless.** The sub-agent can't read your skill files, so minion can only run steps it can hand over in full: the four core steps (audit-before, work, audit-after, report) it already carries, plus any step you fully define in the file's `## Step Library` — as `double-check` is above. A default that leans on a step defined nowhere it can reach — for instance seq's built-in `verify`, which lives in the seq skill, not the shared file — runs fine under seq but makes minion fall back to `standard` and tell you. Copy that step's definition into the file to let minion run it too.

---

## Installation

```bash
npx skills add agenticexpert/skills/minion
```

Part of [Agentic Expert](../../../README.md).

## License

MIT.
