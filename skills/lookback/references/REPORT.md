# Lookback Report Spec

**Render policy.** The inline markdown report is the default deliverable — it
follows the template below. The disk render fires at `verdict` depth or when
the user asks — and **HTML is the default disk artifact**:
`agents/reports/lookback/<UTC-timestamp>.html` (timestamp
`YYYY-MM-DDTHH-MM-SSZ`) per the HTML contract. `.md` (same basename) is written
only when the user asks for it. State the written path(s) inline. When a
required render cannot be written, emit the markdown inline and state why.
Never silently skip a required render.

---

## Markdown template — inline report and on-ask `.md`

```markdown
# lookback / <subject>
> <one-line read on the subject>

**Brief:** launching <what> · success = <2–4 measurable outcomes> · depends on <critical deps> · constraints <what binds>
**Frame:** it is 6–18 months from now; the launch has failed on its success outcomes. Working backward.
**Run:** <quick look|standard|verdict> · <n> scenarios · <n> real · <n> disregarded · <n> T2/T3 · <UTC date>

## Top Risks
- **Most Critical** — [1] <summary>. <one-sentence why>.
- **Biggest Cluster** — <single trigger> activates <scenarios>. <why>.
- **Most Avoided** — [<rank>] <summary>. <why>.
(coincide → say so; diverge → divergence is signal)

## Scenarios
(ranked 1 → 5, most critical first)

### [<rank>] <scenario summary> — <real|disregarded> @ <T0|T1|T2|T3>
who:  <decision authority — person/role>
what: <the failure — observable trigger + causal chain, traced to a named dependency/outcome>
why:  <which success outcome dies + rank bracket> [exec|insp|assm]
do:   <pre-agreed action + the condition that fires it> [cheap|medium|expensive]

(neighbor block — only when required)
Neighbor: <name> — they failed because X; this launch risks Y.
  same: <point> [src] · <point> [src]
  diff: <point> [src] · <point> [src]
  net:  <same-pattern|analog|distant|not-applicable> → <implication>

## Cluster
<shared root or single trigger → which scenarios it activates; the cluster do that dominates its members>.
**Anti-confirmation:** <scenario>; dismissal <structural|motivated> → <outcome>.

## Do Next
**Act now** — [<rank>] <who>: <action>
**Verify** — [<rank>] <who>: <verification step>
**Watch** — [<rank>] <who>: <trigger signal that escalates it>
**Commitment** — [<rank>] <T2|T3>: mitigation <sufficient | revisit the commitment — <required action>>

---
*looked back. — lookback · <depth> · <n> scenarios · <n> real · <n> disregarded · <date>*
```

## Expansion schema — `expand scenario N`

On request only, re-emit one scenario with full anatomy:

- **Mechanism** — the full causal chain, step by step.
- **Research basis** — sources cited, or the exact assumption.
- **Neighbor rows** in full, if any.
- **Reversibility** — tier + one-line meaning + what makes it that tier.
- **Early signal** — the observable indicator at 30–90 days, in detail.
- **Rollback spec** — three labeled rows:
  - **Trigger:** <observable, pre-defined condition — no judgment calls>
  - **Authority:** <named role/person>
  - **Action:** <exact rollback step, written now>
- **Rank bracket** — why not one higher AND why not one lower, a sentence each.
- **Surfacing statement** if `disregarded` — "I have been avoiding X because Y.
  Naming it: …"
- **Verification protocol** if `assm` — what to check, where, what answer
  changes the rank.

---

## HTML contract — the default disk render

Single self-contained file. Archival dossier on dark ground — where ripper is
forensic/blade, lookback is a record being compiled from the future, looking
back. Considered, evidence-bearing, time-shifted.

- **Type:** Fraunces (display) · Spline Sans Mono (labels, rollback specs) ·
  Newsreader (body). One Google Fonts `<link>`; no other external deps. Never
  Inter/Roboto/system.
- **The frame is the masthead's anchor** — *"It is 6–18 months from now. The
  launch has failed."* — quoted, italicized serif, bone-on-dark, set apart
  beneath the title. The reader knows the lens immediately.
- **Class is the hero** of each scenario block — REAL / DISREGARDED as the
  largest tag, band color, left edge-bar — always paired with label text, never
  color-only. Tier tag beside it.
- **Rollback specs (expanded view) read like operational orders** — mono,
  bordered, three labeled rows.
- **Motion:** one staggered reveal on load. **Texture:** subtle paper grain;
  faint archival date-stamp accent at masthead. Responsive at ~640px. Light
  mode not offered.

```css
:root{
  --ink:#e8e4dc; --ink-dim:#9a958a; --ink-faint:#5c594f;
  --bg:#14130f; --bg-raise:#1c1b16; --bg-card:#1f1e18;
  --edge:#312f26; --edge-bright:#464335;
  --blood:#c2412d; --blood-bright:#e3573f;
  --amber:#d99a3a; --bone:#d8cfae; --steel:#7d9aa0;
  --class-real:#c2412d; --class-disregarded:#d99a3a;
  --tier-t0:#7d9aa0; --tier-t1:#d8cfae; --tier-t2:#d99a3a; --tier-t3:#c2412d;
  --ev-executed:#e3573f; --ev-inspected:#d99a3a; --ev-assumed:#5c594f;
}
```

- **Classes:** REAL (blood) · DISREGARDED (amber). `imagined` never renders.
- **Tiers:** T0 steel · T1 bone · T2 amber · T3 blood.
- **Evidence pills:** exec blood-bright · insp amber · assm faint.
- **Sections mirror the markdown template:** masthead (brief + frame + run
  metadata) → Top Risks (three cards, Most Critical largest) → scenarios (class
  column + who/what/why/do body; the `what` renders as a blockquote) → Cluster
  (visual chain showing which scenarios the trigger activates) → Do Next
  (commitment-check rows for T2/T3; "revisit the commitment" in blood-bright) →
  sign-off.
- Conformance = SKILL.md Step 9, unchanged. A report failing any check → fix
  before writing.
