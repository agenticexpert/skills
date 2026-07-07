# Ripper Report Spec

**Render policy.** The inline markdown report is the default deliverable — it
follows the template below. The disk render fires at `verdict` depth or when
the user asks — and **HTML is the default disk artifact**:
`agents/reports/ripper/<UTC-timestamp>.html` (timestamp `YYYY-MM-DDTHH-MM-SSZ`)
per the HTML contract. `.md` (same basename) is written only when the user asks
for it. State the written path(s) inline. When a required render cannot be
written, emit the markdown inline and state why. Never silently skip a required
render.

---

## Markdown template — inline report and on-ask `.md`

```markdown
# ripper / <subject>
> <one-line read on the subject>

**Brief:** <what it is> · enables <workflow> · for <audience> · success = <retention at +3mo>
**Run:** <quick cut|standard|verdict> · <fair|critical|brutal|decimating> · horizons A→B · <n> personas · <n> findings · <UTC date>

> ⚠ DEV-STAGE — subject unreleased. Grades = where-to-look, not settled
> signal. Real-evidence exceptions: <list exec/insp findings, or "none">.
(banner only when subject is unreleased)

## Top Cuts
- **Most Critical** — [<grade>] <summary>. <one-sentence why>.
- **Biggest Drift Risk** — [<grade>] <summary>. <why>.
- **Biggest Frame Risk** — [<grade>] <summary>. <why>.
(coincide → say so; diverge → divergence is signal)

## Personas
- **<name>** · <logic> · <real|composite|hypothetical> — <standing>; win = <retention shape>.

## Findings
(sorted grade 1 → 10)

### [<grade>] <persona> @ <A|B> — <short summary>
what: <the cut — moment, cause, traced to a named part of the subject>
why:  <what stops + why this grade, bracketed> [exec|insp|assm]
who:  <owner of the do — person/role>
do:   <fix|show|clarity-to-keep action> [cheap|medium|expensive]

(neighbor block — only when required)
Neighbor: <name> — they sell X; subject is Y.
  same: <point> [src] · <point> [src]
  diff: <point> [src] · <point> [src]
  net:  <complement|adjacent|confusable|clone> → <retention implication>

## Pattern
<top 1–2 shared roots + the dominant fix>.
**Anti-confirmation:** <finding>; dismissal <structural|motivated>.

## Do Next
**Fix before release** — [<grade>] <who>: <action>
**Test before building** — [<grade>] <who>: <verification>
**Watch** — [<grade>] <escalation signal>

---
*cut clean. — ripper · <depth> · <intensity> · <dry-run|verdict> · <date>*
```

## Expansion schema — `expand finding N`

On request only, re-emit one finding with full anatomy:

- **Finding** in the persona's voice (blockquote).
- **Evidence detail** — what was inspected/executed, or the exact assumption.
- **Trace** — file / section / line.
- **Retention surface** — trust | fit | return | depth | advocacy.
- **Win/Risk** — which drove the grade.
- **Retention impact** — first-contact stay | week-six return | depth of use |
  advocacy.
- **Full bracket** — why not one milder AND why not one harsher, a sentence each.
- **Neighbor rows** in full, if any.
- **Verification protocol** if `assm` — who to ask, what to show, what answer
  changes the grade.

---

## HTML contract — the default disk render

Single self-contained file. Forensic report on dark ground — editorial,
precise, severe. Not a deck, not a dashboard.

- **Type:** Fraunces (display) · Spline Sans Mono (labels) · Newsreader (body).
  One Google Fonts `<link>`; no other external deps. Never Inter/Roboto/system.
- **Grade is the hero** of each finding block — largest element, band color,
  left edge-bar — always paired with band label text, never color-only.
- **Motion:** one staggered reveal on load. **Texture:** subtle film grain;
  faint blood-red radial at masthead. Responsive at ~640px. Light mode not
  offered.

```css
:root{
  --ink:#e8e4dc; --ink-dim:#9a958a; --ink-faint:#5c594f;
  --bg:#14130f; --bg-raise:#1c1b16; --bg-card:#1f1e18;
  --edge:#312f26; --edge-bright:#464335;
  --blood:#c2412d; --blood-bright:#e3573f;
  --amber:#d99a3a; --bone:#d8cfae; --steel:#7d9aa0;
  --grade-crit:#e3573f; --grade-high:#d99a3a; --grade-mid:#c5b66a;
  --grade-low:#7d9aa0; --grade-min:#5c594f;
  --ev-executed:#e3573f; --ev-inspected:#d99a3a; --ev-assumed:#5c594f;
}
```

- **Bands:** 1–2 CRITICAL (blood) · 3–4 HIGH (amber) · 5–6 BOUNDED (bone) ·
  7–8 MINOR (steel) · 9–10 COSMETIC (faint).
- **Evidence pills:** exec blood-bright · insp amber · assm faint.
- **Intensity tints the masthead accent only** — fair steel · critical bone ·
  brutal blood · decimating blood-bright + heavier grain. Structure and palette
  otherwise fixed per run.
- **Sections mirror the markdown template:** masthead (brief + run metadata) →
  caveat banner (amber, unmissable) → Top Cuts (three cards, Most Critical
  largest) → personas → findings (grade column + what/why/who/do body; the
  `what` renders as a blockquote with blood left-border) → Pattern → Do Next →
  sign-off.
- Conformance = SKILL.md Step 9, unchanged. A report failing any check → fix
  before writing.
