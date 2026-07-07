# Seq

**Seq runs one tracked task through a named step-sequence — inline, in your main conversation — so the work moves through a disciplined `audit → work → audit → report` loop while you still see it happen and can course-correct.**

It is the inline twin of [minion](../minion/README.md). Same task loop, same sequences, same audit ledger — but executed here instead of delegated. The trade is deliberate: seq costs main-window tokens, and in return it sees the chat context and lets you steer mid-run. Minion is cheaper and headless; seq is transparent and correctable.

> **Which one?** Well-defined grind you don't need to watch → `minion`. Work where you want eyes on it, or that needs this conversation's context → `seq`. Seq itself will recommend `/minion` when the task is routine enough to delegate.

---

## When to Use

- Tracked work you want to watch and adjust while it runs.
- A task that depends on something said in this conversation (a headless sub-agent couldn't see it).
- A milestone run inline, one task at a time, pausing between.
- Anytime you want the audit-before / audit-after safety net without leaving the main window.

---

## How to Load It

Seq is a semantic skill. Name the task and the venue.

Examples:

- "Seq task `<name>`." · "Do `<task>` inline." · "Run `<task>` here."
- "Seq the migration `as quick`." (bare run — no audit-before)
- "Run this `as audit,work,report`." (ad-hoc one-off sequence)

Force it by name: `/seq`.

---

## How It Runs

The flow is fixed: **resolve → gate → pick sequence → run inline → hand back.** A step is done when its exit artifacts are printed, not when its actions ran.

- **Sequences** — the default is `standard`: `audit-before → work → audit-after → report`. Sequences are named and editable in `references/sequences.md`, or run ad-hoc via `as <key>,<key>,...`. After a successful ad-hoc run, seq offers to save it as a named row.
- **Task source** — like minion, seq binds a task source (named inline, declared in `CLAUDE.md`, or a direct spec path) for `resolve` / `gate` / `expand`. It never invents a task layer and never blocks on a missing tracker.
- **Audit controls** — `--no-audit` skips audit-*before* only; audit-*after* always runs as the safety net. `--audit` forces a fresh audit-before. A truly bare run is `as quick`. An audit already run this session that covers the surface is reused, with the call stated aloud.
- **Abort rule** — when a step hits a blocker, seq stops inline, surfaces it through the clarifier block, and waits. If it aborts before any edit, nothing changed; if edits landed, it lists them.

**Hard rules:** never commits, bumps versions, or edits changelogs; never creates or resequences tasks; one task at a time, pausing between in milestone mode.

---

## Customizing Sequences

A sequence is just an ordered list of steps. The built-in default, `standard`, runs `audit-before → work → audit-after → report`. You can run something else once, keep your own sequences, or change the default — without editing the skill.

**Run a different sequence once.** Name a built-in — `/seq <task> as review` — or spell the steps out ad-hoc: `/seq <task> as audit-before,work,report`. After an ad-hoc run, seq offers to save it as a named sequence.

**Keep your own sequences and set the default.** Create `.agents/seq/sequences.md` in your repo. It uses the same format as the built-in registry — a `## Registry` table and a `## Step Library` — plus one line at the top naming the default:

```text
Default: deep

## Registry
| Name | Steps                                                            | Use for |
|------|------------------------------------------------------------------|---------|
| deep | audit-before → test-first → work → audit-after → verify → report | High-stakes changes — prove the gap first, verify before report. |
```

Now every bare `/seq <task>` runs `deep` instead of `standard`. Your sequences layer over the built-ins (`deep` here reuses built-in steps; a name matching a built-in would replace it), and anything you don't mention still falls back to the built-in. Add steps of your own under a `## Step Library` section with a `### <key>` heading and reference them by key.

**Restore the default.** Delete `.agents/seq/sequences.md` to return to the built-in registry and `standard`. Or just remove the `Default:` line to keep your sequences while letting `standard` be the default again.

> Minion reads the same file, so a default you set here applies to delegated runs too — with one limit, noted in [its README](../minion/README.md).

---

## Installation

```bash
npx skills add agenticexpert/skills/seq
```

Part of [Agentic Expert](../../../README.md).

## License

MIT.
