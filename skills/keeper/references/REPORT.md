# Keeper Report Spec

**Render policy.** Two deliverables per run: the inline markdown report (always,
follows the template below) and the disk render. **HTML is the default disk
artifact** — every run writes `agents/reports/keeper/<UTC-timestamp>.html`
(timestamp `YYYY-MM-DDTHH-MM-SSZ`) per the HTML contract. `.md` (same basename)
is written when the user asks. State the written path(s) inline. When files
cannot be written, emit the markdown inline and state why. Never silently skip
the render.

---

## Markdown template — inline report and on-ask `.md`

```markdown
# keeper / <subject>
> <one-line read on the subject>

**Brief:** reviewing <what> · scope <single element|subsystem|whole> · why now <trigger> · constraints <what binds>
**Run:** <quick call|standard|verdict> · <n> elements · <n> drop · <n> pivot · <n> fix · <n> keep · <n> evidence-needed · <UTC date>

## Top Calls
- **<element>** — `<verdict>` · <axis>. <one-sentence why>. [<cost>]
- **<element>** — `<verdict>` · <axis>. <one-sentence why>. [<cost>]
- **<element>** — `<verdict>` · <axis>. <one-sentence why>. [<cost>]

## Verdicts
(sorted drop → pivot → fix → keep)

### [DROP|PIVOT|FIX|KEEP] <element> — <soundness|optimality|both> @ <cheap|medium|expensive>
who:  <owner of the do — person/role; keep → who watches the trigger>
what: <the element — what it commits to + the structural property found, traced>
why:  <verdict bracket + conditions it holds under> [exec|insp|prov|rsch|assm]
do:   <action + re-evaluation trigger; keep → "hold under <conditions>; re-evaluate when <trigger>">

(neighbor block — only when required)
Neighbor: <name> — they solve X by doing Y; this element does Z.
  same: <point> [src] · <point> [src]
  diff: <point> [src] · <point> [src]
  net:  <equivalent|better-suited|worse-suited|not-comparable> → <implication>

## Cascades  (only when present)
- `<verdict>` on **<element-A>** invalidates `<verdict>` on **<element-B>`. Resolution: <required action>.
**Anti-confirmation:** <verdict most likely disliked>; discomfort <structural|motivated> → <outcome>.

## Do Next
**Change now** — [<verdict>] <who>: <action> [<cost>]
**Gather** — [evidence-needed] <who>: <what to collect before grading>
**Watch** — [keep] <who>: <re-evaluation trigger>

---
*kept clean. — keeper · <depth> · <n> elements · <date>*
```

## Expansion schema — `expand element N`

On request only, re-emit one verdict with full anatomy:

- **Basis** — every source cited with date `[YYYY-MM-DD]`; `inspected:`
  references; executed observations; provided constraints. Flag
  `rsch: stale` / `rsch: foundational` where applicable.
- **Conditions** — the full constraint boundary: under what circumstances the
  call is true, and what sits just outside it.
- **Verdict bracket** — why not each adjacent verdict, a sentence each.
- **Switching cost vs. marginal gain** — the weighing in full (optimality
  pivots).
- **Dependents** — list + how each is handled (drops).
- **Neighbor rows** in full, if any.
- **Lens notes** — which quality lenses were load-bearing and what each showed.
- **Re-evaluation trigger** — the observable condition, who watches it, what
  changes when it fires.

---

## HTML contract — the default disk render

Single self-contained file. An architect's review on dark ground — foundational
/ blueprint: precise, considered, neutral. A verdict-of-craft, not a dashboard.

- **Type:** Fraunces (display) · Spline Sans Mono (labels, tags) · Newsreader
  (body). One Google Fonts `<link>`; no other external deps. Never
  Inter/Roboto/system.
- **Verdict is the hero** of each block — DROP / PIVOT / FIX / KEEP as the
  largest tag, band color, left edge-bar — always paired with band label text,
  never color-only. Axis + cost tags beside it as mono pills.
- **Motion:** one staggered reveal on load. **Texture:** subtle paper grain;
  faint technical-drawing accent at masthead (blueprint hint, not literal).
  Responsive at ~640px. Light mode not offered.

```css
:root{
  --ink:#e8e4dc; --ink-dim:#9a958a; --ink-faint:#5c594f;
  --bg:#14130f; --bg-raise:#1c1b16; --bg-card:#1f1e18;
  --edge:#312f26; --edge-bright:#464335;
  --blood:#c2412d; --blood-bright:#e3573f;
  --amber:#d99a3a; --bone:#d8cfae; --steel:#7d9aa0;
  --verdict-drop:#e3573f; --verdict-pivot:#c2412d;
  --verdict-fix:#d99a3a; --verdict-keep:#7d9aa0;
  --ev-executed:#e3573f; --ev-inspected:#d99a3a;
  --ev-provided:#d8cfae; --ev-researched:#7d9aa0; --ev-assumed:#5c594f;
  --axis-soundness:#d8cfae; --axis-optimality:#7d9aa0;
}
```

- **Bands:** DROP blood-bright · PIVOT blood · FIX amber · KEEP steel.
- **Evidence pills:** exec blood-bright · insp amber · prov bone · rsch steel
  (`stale`/`foundational` as suffix) · assm faint.
- **Sections mirror the markdown template:** masthead (brief + run metadata) →
  Top Calls (three cards, most urgent largest) → verdicts sorted
  drop→pivot→fix→keep (verdict column with band color + edge-bar, body =
  who/what/why/do labeled rows; neighbor block as bordered sub-block) →
  Cascades (visual chain A → B with resolution at the join) + anti-confirmation
  (amber-bordered) → Do Next (each row carries its who) → sign-off.
- Evidence-needed elements render amber-bordered, visually distinct from graded
  verdicts, listing what to gather.
- Conformance = SKILL.md Step 10, unchanged. A report failing any check → fix
  before writing.
