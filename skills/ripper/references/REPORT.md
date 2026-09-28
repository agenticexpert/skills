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

The reader knows the subject but not ripper. Every line says what happens to a
real user and what to do about it, in words they would use. No codes in the
report: no horizon letters, logic names, evidence tags, grade brackets, or
persona roster. Say "on first try" or "by month three"; name a persona by who
they are ("a senior engineer who runs two premortems a quarter"); write
"unverified" where the evidence is assumed. Everything else waits for
`expand finding N`.

```markdown
# ripper / <subject>

<one sentence: who you are most likely to lose, at what moment, and the move that keeps them>

<depth> · <intensity> · <n> findings · <UTC date>
> ⚠ Not released yet — these show where to look, not proof. (only when unreleased)

## Top cuts
- **Most critical** — <what happens, to whom>
- **Biggest drift** — <who stops coming back, and when>
- **Biggest mix-up** — <who gets it wrong, and what they tell others>
(the same finding twice → say so)

## Findings
(most critical first)

### <CRITICAL|HIGH|BOUNDED|MINOR|COSMETIC> — <what happens to whom, plainly>
<the moment: who, doing what, hits what — one or two sentences; their voice welcome>
<what it costs: what they stop doing>. <Unverified — <what would confirm it>.> (only when assumed)
<Looks like <neighbor>: <the one difference that matters>.> (only when the finding rests on the resemblance)
**Do:** <the action> — <who> · <cheap|medium|expensive>

## Behind most of these
<the shared cause and the one fix>. <Looks safe to skip: <finding> — <why it still matters>.> (only when one does)

## Do next
(at most three lines, most critical first; a row with nothing in it is dropped)
- **Before release** — <who>: <action>
- **Test first** — <who>: <what to check with a real person>
- **Watch for** — <the sign it's getting worse>

*cut clean. — ripper*
```

## Expansion schema — `expand finding N`

On request only, re-emit one finding with full anatomy:

- **Persona** — name · logic · standing · win · real | composite | hypothetical.
- **Horizon** — first contact or +3 months.
- **Finding** in the persona's voice (blockquote).
- **Evidence** — exec | insp | assm.
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
- **Unverified pill** on an assumed finding only, faint.
- **Intensity tints the masthead accent only** — fair steel · critical bone ·
  brutal blood · decimating blood-bright + heavier grain. Structure and palette
  otherwise fixed per run.
- **Sections and words mirror the markdown template:** masthead (the one-line
  read + run line) → caveat banner (amber, unmissable) → Top cuts (three cards,
  Most critical largest) → findings (grade column + heading, moment, cost and
  Do; the moment renders as a blockquote with blood left-border) → Behind most
  of these → Do next → sign-off.
