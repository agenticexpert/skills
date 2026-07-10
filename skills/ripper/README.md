# Ripper

**Ripper is a retention premortem: it finds where the people already inclined to love your launch quietly drop trust, drift, or describe you to the wrong crowd — and turns every cut into an owned retention action.**

A generic premortem asks *what could go wrong*. Ripper asks *where do your allies, champions, and loyalists quietly stop coming back* — and ends every finding in an action that keeps them.

Before you ship, it works through the people who already fit your workflow and finds where they'd hesitate, drift, or quietly stop recommending you. Every finding has to name the loyalist, the moment, the cause, the owner, and the action that keeps them.

**R.I.P. = Retention Interference Premortem**

- **Retain** — who already wants this to work?
- **Interfere** — what interrupts their trust, use, return, or advocacy?
- **Preserve** — what owned action keeps them in the workflow?

Ripper speaks for your loyalists. It does not do competitive or adversarial market analysis.

---

## When to Use

- **Use it early** — while positioning, copy, scope, or feature shape can still change. The point is to surface the retention cut while there's still time to act on it.
- **Don't use it as a launch-eve ritual.** A retention premortem the night before ship is theater; the findings have nowhere to land.
- **Skip it** for routine work or decisions you've already committed to — run a postmortem instead.

---

## How to Load It

Ripper is a semantic skill. There's no command to memorize — describe what you're about to ship and Claude loads it. On activation it scans the current conversation and workspace (`CLAUDE.md`, README, docs, attached files) to build the subject, then confirms it with you before running.

Examples:

- "We're a month out from launch. What would make our power users walk away — while we can still fix it?"
- "Run a retention premortem on this positioning before we lock the copy."
- "Where do our champions lose trust with this feature shape?"

You can also force it by name: `/ripper`.

---

## How It Runs

**Intensity** — controls how blunt the language gets. Rigor stays the same at every level. Default is `fair`.

| Level | Voice |
|---|---|
| `fair` | neutral |
| `critical` | exacting |
| `brutal` | plain, no cushioning |
| `decimating` | adversarial skeptic, still evidenced |

The blade language is deliberate. The retention cut has to be precise; the cut is *for* the loyalist, never against them.

**Run depth** — pick the lightest one that still gives honest signal. Default is `standard`.

| Depth | Use when | Output |
|---|---|---|
| `quick cut` | fast pressure before you build or write | Top Cuts + 1–3 findings |
| `standard` | normal pre-launch / positioning review | Top Cuts + all findings + synthesis |
| `verdict` | high-stakes launch; needs to be defensible | full sourced report, rendered to disk |

**Personas** — six by default, each reading the work through its own logic:

| Persona | Logic | Looks for |
|---|---|---|
| advocate, pragmatist, craftsperson, almost-convert | friendly | where they hesitate or drift |
| influencer | influencer | what makes them lean in — or amplify the wrong audience |
| divergent innovator | divergent | what their reaction reveals about the idea |

---

## What You Get Back

Every finding is four lines under a graded heading — concise prose, most-critical first:

```
### [2] craftsperson @ B — drifts at week six
what: the cut — the moment and cause, traced to a named part of the subject
why:  what stops (first contact, week-six return, depth, advocacy) + why this
      grade and not one milder or harsher [exec|insp|assm]
who:  the owner of the action — person or role
do:   the retention action, with cost [cheap|medium|expensive]
```

The evidence tag is honest by construction: `exec` = observed from a real such person, `insp` = looked but not stress-tested, `assm` = imagined and unverified — and a high-impact `assm` finding's action is always *verify with a real person*, never *build*.

The synthesis on top: **Top Cuts** (most critical, biggest drift risk, biggest frame risk), the shared roots underneath them, the finding you're most tempted to dismiss, and what to fix before release / test before building / watch.

Want depth on any cut? Say `expand finding N` — full anatomy (persona voice, trace detail, retention surface, neighbor comparison) is one ask away.

A finding with no action gets cut — a cut without an action is theater, and an action without an owner is a wish.

---

## Output

The report arrives inline by default. At `verdict` depth — or whenever you ask — it also renders the signature dark-forensic `.html` to `agents/reports/ripper/<UTC-timestamp>.html`; ask and you also get the diff-friendly `.md`. Both formats follow [`references/REPORT.md`](references/REPORT.md).

---

## Installation

```bash
npx skills add agenticexpert/skills/ripper
```

Part of [Agentic Expert](../../../README.md). Built by **Shawn Bullock** — [agenticexpert.ai](https://agenticexpert.ai).

## License

MIT.
