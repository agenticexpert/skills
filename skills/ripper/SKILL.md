---
name: ripper
description: Retention Interference Premortem. Ripper cuts into a launch before loyalists do: it finds what makes workflow-fit users — allies, champions, loyalists — hesitate, drift, misframe, or stop advocating, then turns every cut into an owned retention action. 6 personas × 3 logics over 2 horizons; every finding graded 1–10 and delivered as what/why/who/do. Default `fair`; user may set `critical`, `brutal`, `decimating`.
license: MIT
metadata: { version: 4.1.0, category: decision-discipline }
---

## Purpose

Ripper protects the people already inclined to care. A generic premortem asks
*what could go wrong*; Ripper asks *where do our allies, champions, and loyalists
quietly stop coming back* — and ends every cut in an owned action that keeps them.

**R.I.P. = Retention Interference Premortem** — **Retain** (who already wants
this to work?) · **Interfere** (what interrupts their trust, use, return,
advocacy?) · **Preserve** (what owned action keeps them in the workflow?).

Not for: adversarial / competitive analysis.

**Use:** pre-release · pre-commitment · positioning · before authoring effort scales.
**Skip:** routine work · already-committed decisions (run a postmortem instead).

## Protocol

### 0. Subject — before anything else

Scan first — conversation, project notes, attached files, prior decisions. No
questions until scanned. Build the brief:

- **What it is** — one sentence. · **Enables** — the workflow it serves. ·
  **Audience** — who that workflow fits. · **Success** — retention at +3 months.

Confirm with the user in one short block. Corrections → apply. "Just deliver" →
proceed unconfirmed. A field unfillable after one question → halt.

Short-circuits: subject explicitly named with a clear noun ("rip the X page") →
one-line subject inference, one-sentence confirm. Non-SaaS subject (personal
decision, research scoping, third-party review) → recast: audience =
stakeholders, workflow = decision process, success = your future self's
conviction at +3 months.

### 1. Depth — default `standard`

Lightest depth that still gives honest signal. Output density follows depth;
more is one ask away (Step 8).

| Depth | Use when | Research | Output |
|---|---|---|---|
| `quick cut` | fast pressure before writing/building | supplied context only; unchecked claims stay `assm` | Top Cuts + 1–3 findings |
| `standard` | normal pre-launch / positioning review | supplied artifacts + obvious neighbors | Top Cuts + all findings + Pattern + Do Next |
| `verdict` | high-stakes; must be defensible | full research; sourced neighbor rows; verified COGs | full report, rendered to disk |

### 2. Personas — default 6

Capture per persona: name · logic · standing · win. Tag `real` / `composite` /
`hypothetical`.

| Persona | Logic | Measure | Failure mode | Finding ends in |
|---|---|---|---|---|
| advocate, pragmatist, craftsperson, almost-convert | **friendly** | where they hesitate | turns detractor / drifts away | fix |
| influencer | **influencer** | what makes them lean in | shrug or mis-amplification (frames the wrong audience) | show / pre-empt |
| divergent innovator | **divergent** | what their take reveals about the idea | (clarifier — no failure mode) | clarity-to-keep |

- Logics do not collapse.
- **divergent** — never pre-script the keep/discard.
- **influencer** — excitement ≠ validation. An influencer-pleasing move that
  costs craftsperson trust → flag it. Wrong-audience amplification is retention
  loss.

### 3. Intensity — default `fair`

`fair` neutral · `critical` exacting · `brutal` plain, no cushioning ·
`decimating` adversarial skeptic, evidenced. Intensity scales voice only — the
floor is constant:

- No action → cut the finding. No generic dismissals ("derivative", "won't
  care", "too complex").
- Every finding traces to a real source (subject, brief, conversation, sourced
  neighbor row); unsourced → cut. Uncertain → tag `assm` + a verification step;
  tone never substitutes for evidence, and `assm` stays visible everywhere the
  finding appears — findings, Top Cuts, Do Next.
- Critique the work, never persons/teams/orgs. A finding that only stands by
  attacking a person → rewrite as critique of the work or cut.
- Reject: `fair` without persona + moment + cause · `critical` tracing only to
  surface detail · `brutal` harsh verbs without a named mechanism each ·
  `decimating` confident tone on `assm` with no verification step.

### 4. Research — depth-gated

Do not reason from priors when a claim is checkable and material. Special
checks: **divergent** — does the idea exist under another name? Real fork,
study it. **craftsperson** — verify quality claims against current standards.
**influencer** — inspect what is landing or saturated in the space now.

**Neighbors.** A neighbor = a real, named thing the workflow-fit audience
already knows, overlapping the subject on a visible axis (vocabulary, category,
feature, distribution, audience). Resemblance triggers inspection — never a
verdict by itself. A comparison is REQUIRED when a finding depends on
resemblance, the audience likely knows the neighbor, confusion risk drives a
1–4 grade, or depth is `verdict`. Then emit:

```
Neighbor: <name> — they sell X; subject is Y.
  same: <point> [src] · <point> [src]
  diff: <point> [src] · <point> [src]
  net:  complement | adjacent | confusable | clone → <retention implication>
```

≥2 sourced points per side (URL or `inspected: <artifact>`) or drop the claim.
No verified COG → grade capped at 5–6.

### 5. Project — two horizons, sequential, B inherits A

- **A — release / first contact.** · **B — +3 months.**
- 1–3 findings per persona per applicable horizon. Specific = persona + moment
  + cause. "They probably won't get it" fails; "the pragmatist drifted at week
  six because recalling which blueprint to load was slower than asking the
  model" passes.

### 6. The finding contract — what / why / who / do

Every finding is EXACTLY these four lines under a graded heading. Print them; a
finding missing a line does not exist.

```
### [<grade>] <persona> @ <A|B> — <short summary>
what: the cut — persona, moment, cause, traced to a named part of the subject.
      1–2 sentences; persona voice welcome.
why:  the stakes — what stops (first-contact stay, week-six return, depth of
      use, advocacy) + evidence tag [exec|insp|assm] + the grade bracket: why
      not one milder, why not one harsher. 1–2 sentences.
who:  owner of the do. Named person/role from context; unknown → the role that
      owns the traced artifact (copy, docs, code, design, pricing).
do:   the retention action — fix | show | clarity-to-keep — with cost
      [cheap|medium|expensive]. Evidence assm + high impact → the do IS the
      verification step with a real person.
```

Evidence tags: `exec` — observed from a real such person · `insp` — looked, not
stress-tested · `assm` — imagined, unverified (checkable-but-unchecked stays
`assm`). Read a text artifact → `insp`; ran the behavior → `exec`; didn't look
→ `assm`.

### 7. Grade 1–10 (1 = most critical), then synthesize

| Grade | Meaning |
|---|---|
| 1–2 | Loses a core persona at first contact or turns them detractor. |
| 3–4 | Causes drift; persona stops reaching for it. |
| 5–6 | Bounded retention friction. Planned fix. |
| 7–8 | Minor; secondary persona or rare case. |
| 9–10 | Cosmetic / speculative. |

Caps (non-overridable): high-impact `assm` → grade by impact, do = verify ·
shared finding → take the lowest (most critical) instance, not the average ·
overlap without a verified COG → capped 5–6 · `brutal`/`decimating` resting on
unchecked-but-checkable → disqualified, not softened.

Synthesis — printed after the findings:

- **Top Cuts** — Most Critical · Biggest Drift Risk (highest at horizon B) ·
  Biggest Frame Risk (highest influencer / neighbor-confusion). Three views;
  coincide → say so; diverge → the divergence is signal.
- **Pattern** — top 1–2 roots recurring across personas (cross-logic recurrence
  = strongest signal) + the dominant fix.
- **Anti-confirmation** — the finding most tempting to dismiss. Motivated
  dismissal (slows you / hurts) → promote 1–2 grades; structural (real reason
  it won't matter) → leave.
- **Do Next** — fix before release (grade 1–4, cheap/medium) · test before
  building (high-impact `assm` + verification) · watch (5+ with escalation
  signal).

### 8. Output

- Inline report is the default deliverable: masthead line (subject · depth ·
  intensity · personas · findings · date) → dev-stage caveat if unreleased →
  Top Cuts → findings sorted 1→10 in the four-line contract → Pattern → Do
  Next. Template: `references/REPORT.md`.
- Disk render at `verdict` depth or when the user asks — **HTML by default**
  (`agents/reports/ripper/<UTC-timestamp>.html`); `.md` (same basename) only
  when the user asks for it — both contracts in REPORT.md. Cannot write files
  when a render is required → emit inline and say why. Never silently skip a
  required render.
- **More on ask:** `expand finding N` → full anatomy per REPORT.md's expansion
  schema (voice quote, trace detail, retention surface, win/risk, neighbor
  rows). The report stays lean because depth is one ask away.

### 9. Conformance — refuse to emit if any fails

- [ ] Masthead: brief confirmed, depth + intensity declared.
- [ ] Every finding = what/why/who/do, none empty, printed under a graded heading.
- [ ] Every `why` carries an evidence tag AND a grade bracket.
- [ ] High-impact `assm` → its `do` is a verification step.
- [ ] Findings sorted 1 → 10; Top Cuts show three views.
- [ ] Neighbor-dependent findings carry the sourced neighbor block.
- [ ] No person/team/org attacked; dev-stage caveat present iff unreleased.

## Operating principles

Retention is the deliverable. Loyalists are the signal; strangers are noise. A
cut without an action is theater; an action without an owner is a wish. Evidence
outranks tone. Resemblance is confusion risk, not guilt. Grade the wound, not
the mood. Harsh on the work, neutral on the people.

## Override

First-principles analysis of *this specific situation* overrides any rule —
note the deviation. Load-bearing, never skip: subject brief · personas × logics
· the four-line contract · grade caps · conformance.
