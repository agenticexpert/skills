<div align="center">

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-5-brightgreen.svg)

</div>

Agents need a boost sometimes — on a plan that has to hold for a week, a decision that deserves a second opinion, a prompt worth tuning before an expensive run, knowledge that has to survive the context window.

Here's how.

---

## What it does

| When this is your problem | Reach for |
|---|---|
| A deliverable is a fuzzy blob — you don't know the pieces, the order, or what's blocked | **[Tasky](.claude/skills/tasky/README.md)** — turns it into a plan you can execute and track, all through conversation |
| You built something and don't know whether it should survive | **[Keeper](.claude/skills/keeper/README.md)** — one verdict per piece: keep, fix, pivot, or drop |
| You ship in a month and want to know how it fails — while you can still change course | **[Lookback](.claude/skills/lookback/README.md)** — assumes the launch already failed, then works back to why |
| Your best users quietly stop recommending you and you never find out why | **[Ripper](.claude/skills/ripper/README.md)** — finds where they hesitate or drift, and turns each one into a fix |
| The session ends and everything it knew dies with it | **[Mem](.claude/skills/mem/README.md)** — durable summaries that survive `/clear`, compaction, and handoffs |

## What it looks like

Keeper, asked whether an auth design is worth keeping:

```
session store              KEEP    3 call sites, no coupling to the token path.
refresh-token rotation     FIX     silently no-ops on clock skew — auth.ts:214.
device fingerprinting      DROP    40 lines, one caller, breaks Safari private mode.

Pivot only if SSO lands next quarter. Otherwise this holds.
```

Every call conditional, every call tied to something in your code. That's the house style across all five.

## How to use it

**Nothing to memorize.** Say what you're doing; Claude matches it against each skill and loads the right one.

- "Let's plan out the roadmap for `<thing>`." · "What's next?" · "What's blocked?"
- "Is this auth design worth keeping, or should we pivot?"
- "We ship in a month. Run a premortem while we can still change course."
- "What would make our power users quietly stop recommending us?"
- "Checkpoint this session." · "Continue from the last checkpoint."

Need to force one? Every skill loads by name: `/tasky` `/keeper` `/lookback` `/ripper` `/mem`.

## Install

```bash
# All five
npx skills add agenticexpert/skills

# Or just one
npx skills add agenticexpert/skills/tasky
npx skills add agenticexpert/skills/keeper
npx skills add agenticexpert/skills/lookback
npx skills add agenticexpert/skills/ripper
npx skills add agenticexpert/skills/mem
```

Updating:

```bash
npx skills update agenticexpert/skills   # everything from this source
npx skills update tasky                  # one skill by name
```

**Start here:** install all five, then say *"Let's plan out the roadmap for `<what you're building>`."* Tasky picks it up. The rest find you when you need them.

---

## Going deeper

The five group into three jobs. Each skill's own README has the full method.

- **Plan & execute** — [Tasky](.claude/skills/tasky/README.md) breaks the work down into a plan you can run and track.
- **Stress-test a decision** — [Keeper](.claude/skills/keeper/README.md) judges what exists · [Lookback](.claude/skills/lookback/README.md) hunts the failure before it happens · [Ripper](.claude/skills/ripper/README.md) hunts the quiet churn.
- **Context** — [Mem](.claude/skills/mem/README.md) keeps what the model would otherwise forget.

They compose: Tasky plans it, Lookback tries to break it, Keeper decides what survives, Mem remembers what happened.

Built by **Shawn Bullock** — [agenticexpert.ai](https://agenticexpert.ai).

## License

MIT. See [LICENSE](LICENSE).
