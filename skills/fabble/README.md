# Fabble

**Fabble is a prompt-engineering family: it authors, migrates, enhances, and gates the prompts you hand a Claude model — so the prompt, not luck, decides whether one run reaches the goal.**

One subject, five jobs. Underneath them is a single doctrine: a prompt splits into the **contract** — intent stated, full spec up front, boundaries fenced, claims traced to evidence, done defined countably — and the model's **capability**, what it does unprompted. The contract is model-agnostic and always belongs. Fable 5 needs little beyond it; Sonnet/Opus need the contract plus compensating scaffolding; over-prescribing Fable 5 degrades it.

> **The economic goal:** one run → goal complete. A round trip costs a full run, so a prompt that guesses wrong wastes the whole thing. Fabble exists to spend the words that stop that.

---

## The Five Jobs

Two questions route every ask: what do you **have**, and what should the result **run on**?

| Have | Result | Playbook |
|---|---|---|
| A goal + raw facts, no prompt yet | Execution-ready prompt | `promptify` |
| An existing prompt | Runs on Fable 5 | `fablize` |
| An existing prompt | Stays on Sonnet/Opus, raised to its ceiling | `fabelike` |
| A Fable-shaped task, staying on Sonnet/Opus | Goal re-authored + ordered run sequence | `promptify` (Opus/Sonnet deltas) |
| A finished prompt | Verdict before an expensive run | `audit` |

`promptify` builds from scratch · `fablize` ports up to Fable 5 · `fabelike` raises a prompt that stays on its current model · `audit` gates before you spend the run.

---

## When to Use

- Before an expensive or long agentic run — gate it with `audit` first.
- Porting prompts tuned for Sonnet/Opus onto Fable 5, or the reverse.
- Turning a loose ask into a spec a model can execute end-to-end unattended.
- Any prompt where a wrong guess mid-run throws away the output.

Not for one-off chat questions — the overhead only pays off when a run is long, unattended, or costly to redo.

---

## How to Load It

Fabble is a semantic skill. State the prompt job and Claude routes to the matching playbook, reads it fully, and works from it.

Examples:

- "Write a prompt for X." · "Turn this into something Fable 5 can run."
- "Upgrade this prompt for Fable 5 — it was tuned for Sonnet." · "Fablize this."
- "Make this prompt better without switching models." · "Fabelike this."
- "Is this ready for Fable 5?" · "Audit this prompt before I run it."

You can also force it by name: `/fabble`. Fabble also ships a slash command — `/until [opus|sonnet] <ask>` — that elevates a loose ask straight into a goal via `promptify`. It takes a one-time setup step to enable; see [Installation](#installation). Without it, invoke the same path in words ("elevate this into a goal").

---

## How It Runs

Each job is a playbook under `references/`, backed by three shared behavior files that stay the single source of truth:

- **`fable5-behavior.md`** — Fable 5 defaults, thirteen failure modes → steering snippets, classifier hazards.
- **`opus-behavior.md`** — what changes when the runtime is Sonnet/Opus (evidence-demand verification, completion checklist, point-of-use placement, the wider length band).
- **`gate.md`** — the seven audit checks, their probes, and the scoring rubric.

The migration playbooks work by ledger: every prompt line is triaged **cut · collapse · rewrite · keep · add**, and each change carries its reason. The gate returns one verdict — **ship · ship with assumptions · decide · ship as sequence** — after a full run-simulation of the prompt as the target model in a fresh session.

---

## Installation

```bash
npx skills add agenticexpert/skills/fabble
```

### Enable the `/until` command (one-time)

The skill install lays down the playbooks, but slash commands live in `.claude/commands/` — a tree the skill install doesn't touch. To turn on the `/until` shortcut:

```
/fabble install          # this project (.claude/commands/)
/fabble install global   # every project (~/.claude/commands/)
```

Fabble copies its bundled `commands/until.md` into the matching commands directory; Claude Code registers any file there as a slash command. `/until [opus|sonnet] <ask>` works from then on. Delete that file to remove it. This step is optional — everything else in fabble works without it; you just trigger the goal-elevation path in words instead.

Part of [Agentic Expert](../../../README.md). Built by **Shawn Bullock** — [agenticexpert.ai](https://agenticexpert.ai).

## License

MIT.
