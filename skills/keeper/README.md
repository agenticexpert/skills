# Keeper

**Keeper is a keep-or-correct discipline for architecture and implementation decisions: it judges each element of a system and answers, with evidence, whether it's the right thing to keep under the current constraints.**

The discipline is **conditional permanence**. Every verdict carries the conditions it holds under, the evidence it rests on, the owner who acts on it, and the trigger that would force a revisit. A `keep` isn't permanent; it's *kept under X, re-evaluated when Y — and someone is named to watch for Y*.

The question, per element:

> **Is this the right design or implementation to keep under the current constraints?**

> **Not an ADR replacement.** ADRs document decisions for posterity. Keeper *judges* what already exists and names what would invalidate the judgment. Run Keeper before writing an ADR — or to revisit one.

---

## The Four Verdicts

| Verdict | Meaning |
|---|---|
| `keep` | Leave unchanged under the stated conditions. Sound and optimal-enough. |
| `fix` | Keep the choice; correct the execution. |
| `pivot` | Replace the choice — another approach fits the constraints better and the gain exceeds the switching cost. |
| `drop` | Remove the element — the need isn't worth carrying. |

`pivot` replaces the choice. `drop` removes the need.

---

## When to Use

- Architecture review · implementation review above line-level code critique.
- Product or system design review · mid-build course correction.
- Pre-scale review, before more work commits to the current approach.
- Design choices that work but need judgment on whether they're right enough to keep.

Not for line-level critique or recording forward decisions (write an ADR).

---

## How to Load It

Keeper is a semantic skill. Describe the design or implementation you want judged and Claude loads it. On activation it scans the conversation and workspace (`CLAUDE.md`, README, `/docs/`, `/memory/`, attached files, the repo if available), builds the subject — what's under review, scope, why now, constraints — then confirms with you before running.

Examples:

- "Is this auth design worth keeping, or should we pivot?"
- "Review the build pipeline's Docker-first stance — keep, fix, pivot, or drop?"
- "Judge these three storage approaches against our constraints."

You can also force it by name: `/keeper`.

---

## How It Runs

> **No intensity scale.** Verdict harshness is set by evidence, not voice. For adversarial tone, use ripper.

**Run depth** — pick the lightest one that still gives honest signal. Default is `standard`.

| Depth | Use when | Output |
|---|---|---|
| `quick call` | one named element, fast judgment | Top Calls + that verdict |
| `standard` | subsystem or design review | Top Calls + all verdicts + cascades + Do Next |
| `verdict` | high-stakes / pre-scale; must be defensible | full sourced report |

**Elements** — you name them, or Keeper picks the 3–7 highest-stakes (blast radius, reversibility cost, dependent count, constraint sensitivity) and confirms the list with you.

**Quality lenses** — applied selectively, only the load-bearing ones: constraint fit, cohesion, coupling, reversibility, complexity budget, failure behavior, boundary clarity, operational fit, marginal value.

**Evidence** — every verdict carries a tag: `exec` (observed in real use) · `insp` (artifact opened and read this run — not "it exists") · `prov` (your stated constraint) · `rsch` (external source, dated within 12 months or tagged stale/foundational) · `assm` (plausible, unverified). An `assm`-only element comes back as **`evidence-needed`** with a list of what to gather — it is never graded. When a `pivot` leans on a real, named alternative, a sourced neighbor comparison is required — two same-as points, two different-from points, and a net verdict the reasoning cites.

---

## What You Get Back

Every verdict is four lines under a verdict heading — owner first, concise prose, sorted `drop` → `pivot` → `fix` → `keep`:

```
### [FIX] session-token refresh — soundness @ medium
who:  auth service owner
what: the element — what it commits to and the structural property found,
      traced to the inspected artifact
why:  why this verdict and not the adjacent one (why not keep, why not pivot)
      + the conditions it holds under [exec|insp|prov|rsch|assm]
do:   the specific correction + the trigger that forces a revisit
```

A `keep`'s do reads *"hold under X; re-evaluate when Y"* — and its who is the person watching for Y. An optimality `pivot` that hasn't weighed switching cost against marginal gain is downgraded to *keep, suboptimal-but-not-worth-switching*. A `drop` with unhandled dependents is downgraded or flagged cascade-blocked.

The synthesis on top: **Top Calls** (the first three verdicts to act on), **Cascades** (any verdict that invalidates another, with the resolution), the anti-confirmation check (the verdict you'll most dislike, with the discomfort typed `structural` or `motivated`), and **Do Next** — change now / gather / watch, every line carrying its owner.

Want depth on any call? Say `expand element N` — full anatomy (dated sources, condition boundaries, switching-cost math, neighbor rows, lens notes) is one ask away.

An action without an owner is a wish; a trigger without a watcher never fires.

---

## Output

The report arrives inline, and every run renders the signature architect's-blueprint `.html` to `agents/reports/keeper/<UTC-timestamp>.html` by default. Ask and you also get the diff-friendly `.md`. Both formats follow [`references/REPORT.md`](references/REPORT.md).

---

## Installation

```bash
npx skills add agenticexpert/skills/keeper
```

Part of [Agentic Expert](../../README.md). Built by **Shawn Bullock** — [agenticexpert.ai](https://agenticexpert.ai).

## License

MIT.
