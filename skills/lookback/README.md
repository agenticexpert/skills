# Lookback

**Lookback is a solo premortem: before you commit, it assumes the launch already failed and works backward to the five reasons why — each research-defended, each owned, each ending in a pre-agreed action.**

The frame is the engine of the whole thing:

> It is 6–18 months from now. The launch has clearly failed on its success outcomes. Work backward.

Every scenario has to name the owner, the failure, the stakes, and the action that's written down before it's needed.

Out of scope: post-event analysis, team facilitation, market analysis.

---

## The Classes

Every scenario in the top 5 is classed by the source of its claim on attention:

| Class | Source |
|---|---|
| `real` | Has evidence and a named mechanism. Requires `exec` or `insp` evidence. |
| `disregarded` | A real risk the maker has been avoiding naming. Honest discomfort, not motivated dismissal. |

A third state, `imagined` — sounds like risk because it matches a familiar pattern, but has no evidence here — exists only during triage. Research either converts it to `real` or it gets cut. It never appears in the report.

---

## When to Use

- **Use it early** — while the plan can still change. Before commitment, before scaling, before high-cost resource pours. The point is to find the failure mode while there's runway to act on it.
- **Don't use it as a launch-eve ritual.** A premortem run the night before ship is theater; the findings have nowhere to land.
- **Skip it** for routine work or for already-committed irreversible decisions.

---

## How to Load It

Lookback is a semantic skill. Describe what you're about to ship or commit to, and Claude loads it. On activation it scans the current conversation and workspace (`CLAUDE.md`, README, `/docs/`, `/memory/`, attached files), constructs the subject — what's launching, the success outcomes, critical dependencies, constraints — then confirms with you before running.

Examples:

- "We're planning to ship this in a month. Run a premortem now while we can still change course."
- "We're committing to a React 19 migration. What would make this fail at month 6?"
- "Premortem the Q2 pricing change to $99/seat before we lock the decision."

You can also force it by name: `/lookback`.

---

## How It Runs

**Generate, then force the cut.** Lookback generates 8–12 specific, mechanistic failure scenarios under the frame, then cuts to the **top 5**, ranked by impact severity × confidence in mechanism. Five is the cut — forced prioritization prevents list-bloat theater.

> *Bad: market conditions worsened.*
> *Good: the primary integration partner deprecated their v2 API with 60 days' notice, and there was no abstraction layer or fallback in place.*

**Run depth** — pick the lightest one that still gives honest signal. Default is `standard`.

| Depth | Use when | Output |
|---|---|---|
| `quick look` | fast pressure before committing | Top Risks + top 3 scenarios |
| `standard` | normal pre-launch / pre-commitment | Top Risks + all 5 + Cluster + Do Next |
| `verdict` | high-stakes; must be defensible | full sourced report, rendered to disk |

**Research each survivor.** Has this failure shape happened to comparable launches (cite real cases)? Are the depended-on technologies and partners currently stable (cite current state)? When a scenario leans on a real, named precedent, a sourced neighbor comparison is required — two same-as points, two different-from points, and a net verdict.

**Reversibility tier** — every scenario carries one: `T0` trivially reversible · `T1` reversible with cost · `T2` mostly irreversible · `T3` fully irreversible. A `T2`/`T3` scenario whose mitigation is insufficient gets "revisit the commitment" stated plainly — not softened.

---

## What You Get Back

Every scenario is four lines under a ranked heading — owner first, concise prose, most-critical first:

```
### [1] integration partner kills the v2 API — real @ T2
who:  platform lead — owns the integration layer
what: the failure — the observable trigger and the causal chain, traced to a
      named dependency or success outcome
why:  which success outcome dies + why ranked here and not one higher or
      lower [exec|insp|assm]
do:   the pre-agreed action + the condition that fires it — written now, no
      judgment calls later [cheap|medium|expensive]
```

The evidence tag is honest by construction: `exec` = observed in real comparable cases, `insp` = looked but not stress-tested, `assm` = imagined and unverified — and a high-impact `assm` scenario's action is always *verify*, never *build the mitigation*. A `disregarded` scenario's action opens with the naming: *"avoided X because Y; naming it."*

The synthesis on top: **Top Risks** (most critical, biggest cluster — the single trigger that activates 2+ scenarios at once — and most avoided), the anti-confirmation check (the scenario you're most tempted to dismiss, with the dismissal typed `structural` or `motivated`), and **Do Next** — act now / verify / watch, every line carrying its owner, plus the commitment check for anything hard to reverse.

Want depth on any scenario? Say `expand scenario N` — full anatomy (mechanism chain, research basis, neighbor rows, the full rollback spec with trigger/authority/action, early-signal detail) is one ask away.

An action without an owner is a wish; a rollback without a trigger is a hope.

---

## Output

The report arrives inline by default. At `verdict` depth — or whenever you ask — it also renders the archival-dossier `.html` to `agents/reports/lookback/<UTC-timestamp>.html`; ask and you also get the diff-friendly `.md`. Both formats follow [`references/REPORT.md`](references/REPORT.md).

---

## Installation

```bash
npx skills add agenticexpert/skills/lookback
```

Part of [Agentic Expert](../../../README.md).

## License

MIT.
