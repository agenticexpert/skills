---
name: resume
description: Resume callback diagnosis and repair. Grades whether ATS passes it, a phone screener calls, and a hiring manager interviews—then makes the smallest evidence-backed fixes that change that decision. Supports resume, LinkedIn, job-description context, a 0–5 demonstrated-skill rubric, local HTML+JSON reports, outcome calibration, and item-scoped conversation.
license: MIT
metadata: { version: 2.4.0, category: career-craft }
---

# Resume

Prime question: **Must I move forward with this candidate?**

Do not grade “match to the JD.” A JD supplies context and required evidence; it does not supply the verdict. Grade three decisions:

1. Will ATS pass it?
2. Will the phone screener call?
3. Will the hiring manager interview?

## Run

1. Read the resume, LinkedIn, JD, callback history, and attached files before asking questions. Look only in the bounded likely locations — attached files, the working directory, and the user's recent Downloads — and stop once an unambiguous set is found; ask one question when the inputs or the target cannot be resolved there. Never print a résumé's contact details to identify or confirm a file.
2. State the lane in one line. If inferred, tag it `unconfirmed` and name the confirming question.
3. Choose the lightest mode that answers the ask:
   - `quick scan`: decision + Gets Attention + top 3 findings.
   - `standard`: decision + five-reader evidence + top 5 + Do Next.
   - `rewrite`: standard + accepted section repairs.
   - `skillmatch`: demonstrated-skill rubric plus JD expectations as context. Supplied postings merge into one lane: every row states the bar as a posting worded it, its own source count, and its standing against that bar. Standings are never counted, averaged, or expressed as a percentage.
4. Run five fresh reads in order: ATS → recruiter → HR → hiring manager → technical reviewer. Preserve each read; do not blend them.
5. Grade every atom against the winning bar in `references/CRAFT.md` — every bullet, headline, summary line, title, org, date range, location, tool name, link, and contact field — and roll each grade up to the decision unit that owns it. Scrutiny is atomic; presentation stays at the unit. This axis is never skipped and never sampled.
6. Normalize evidence before scoring: extract retrievability signals — whether the deciding content is findable and attached to proof — plus explicit claims, quoted proof, confirmed requirements, material missing evidence, and the aggregate craft grade within each reader's reach. Parse status is tracked separately and never enters the vector.
7. Roll the five reads into the three gates below.
8. Print the decision before all other substantive output.
9. Emit decision findings that change decision, proof, material risk, or action, plus a craft finding for every element graded `below-bar` or `median` at tiers 1–3.

Zero decision findings is valid. Craft coverage is never zero: every element in scope carries a grade whether or not it produces a finding. Do not manufacture criticism, and do not withhold a grade to hold the count down.

Do not manufacture a metric gap **in the decision axis**. If the resume explicitly shows an outcome-oriented responsibility, missing quantification alone is not a decision hotspot unless the target states a numeric target or threshold. Words such as “shorten,” “improve,” or “reduce” do not create one. Prefer a genuinely unproven condition over another metric on already-useful proof. This bounds decision hotspots only; the craft axis still grades the element against `difficulty visible` and reports it at its own tier.

## Decision

Use exactly:

- ATS: `fail|risky|weak-pass|pass`
- Screener (recruiter + HR): `no-call|maybe|call|urgent-call`
- Manager (hiring manager + technical): `no|insufficient|interview|priority-interview`

Without a JD or confirmed target requirements, ATS grades content retrievability and evidence visibility only — whether the target identity, canonical role/domain/tool terms, and strongest qualifying evidence are findable and attached to credible proof. A supported canonical term outranks an unsupported keyword list on the same facts; keyword dumps, verbosity, and polish add no value. Do not lower ATS for absent unspecified keywords, tools, education, or contact fields; mark them unconfirmed risks outside the ATS gate. With a JD, only a missing truthful confirmed must-have may lower ATS. Parsing is `untested` unless a directly observed extraction artifact or parser command is on record: untested parsing can neither raise nor lower ATS, and no output may claim a resume "parses cleanly" or narrate any parser behavior without that cited evidence. Buried or detached proof may lower ATS on *retrievability* grounds without asserting parser behavior; tested parsing may move ATS only through the cited observed evidence.

**Length-neutrality invariant:** padding never raises a gate. Two versions of the same content at different lengths receive identical ATS, screener, manager, Must-Talk, and move-forward values. Word count, adjective count, and terseness cannot raise anything. Before emitting, ask: “If I delete only prose that carries no content, do the gates rise?” If yes, recompute.

Craft is not padding, and the invariant is one-directional. Aggregate craft lowers a verdict by the rule in `references/CRAFT.md`: when a third or more of the elements within a reader's reach grade `median` or worse, that reader falls one step. A single weak line never moves a gate.

Derive Must-Talk by the ordered table in `references/READERS.md`; never type an independent score. Map 0/1 → `no`; 2 → `not yet`; 3/4 → `yes`.

The first substantive line must be:

`MOVE FORWARD: yes|not yet|no — <one reason naming the first deciding gate or quoted urgency>`

Then print Must-Talk, the three gates, and the five-reader evidence. Never print a match percentage, fit band, applicant-minus-JD delta, or generic verdict before this line.

## Evidence

Review claims: `seen|jd|mkt|assm|li|web`. Resume facts: `confirmed|inferred|needs-confirmation|risky|cut-unless-proven`.

- Quote the line that earns every positive call. Gets Attention caps at 3.
- Never invent facts, numbers, tools, scale, ownership, or outcomes.
- A difference between two sources proves only the difference, never the intent behind it: do not assert *why* a résumé and LinkedIn diverge — surface the divergence and confirm it. Prior context about the person is not the supplied evidence; it cannot harden a claim.
- Every tag names its source. Attach `mkt` only with the market pattern or callback data behind it named; without a named source it is `assm`.
- An `assm` action is “confirm,” never a rewrite.
- Critique the artifact, never the candidate.

Skill grades remain 0–5 only when applicant evidence supports the grade. Expected or transferable skills without quoted applicant evidence are `ungraded · confirm`; retain the expectation/bridge, truth tag, and question. They never affect the decision until confirmed. See `references/SKILLMATCH.md`.

## Why the role exists

When a JD is present, derive one buying need before the five reads:

1. Turn prominent responsibilities into the costly condition they prevent or the outcome they create.
2. Cluster repeated consequences and select the dominant state change.
3. Name who benefits and the constraint the hire must work within.
4. Mark it `confirmed`, `inferred`, or `unknown`; attach up to three exact JD/user quotes.
5. Unless confirmed, ask one question that would settle the inference.

State it as `Role exists to …`. Then report non-negotiables (`proven|confirm|absent`), central-problem evidence (`strong|buried|weak|missing|unknown`), at most one defensible differentiator, and at most one truthful repair. This context never adds a score or changes the three-gate arithmetic.

## Findings

The two axes carry separate budgets. **Decision findings** use the fewest rows that expose the real hotspots. **Craft findings** are one per graded element and are never rationed — coverage is their purpose.

Decision findings: an atom finding covers one resume element. A context finding covers one repeated action across a summary, role, section, or bounded set of related items. Group different missing conditions from one role when they share the same reviewer consequence and one outcome narrative can resolve them. Its source IDs include only items exhibiting that problem; keep clean differentiators out. When it already names the missing facts, it is terminal: do not add atom or supporting **decision** rows that repeat any part of the same issue. A craft finding on an element inside a context finding's span is not a repeat — it names a different bar. Repair the item containing the unsupported central activity, not an already-useful proof item that could merely take another metric.

An item is anchored where its repair lands. `ctx.path` names the element the `do` action would edit, and the quoted line, the reader consequence, and the action all address that one element. Test the action's destination, not the roles it cites: naming another role as the source of a fact is sound, while sending the edited text to another role, employer, section, or period than the quoted line means the anchor is wrong — move it to the element that would carry the repair. Never anchor to the element that merely resembles the concern, and never to the nearest available element when no element on the page carries the missing condition.

An absence spanning the whole resume is a context finding scoped to the section that would hold the proof, never an atom on the closest-resembling line. When no existing element could receive the repair, scope it to that section and ask there for the missing condition. When one element carries both an unverified result and a wording defect, the unverified result is the single decision hotspot and the wording is subordinate cleanup folded into that one repair; the wording still grades and reports on the craft axis at its own tier.

Every finding is exactly four lines:

```text
### [rank] <section or quote> — <gap> @ <reader>
who: <reader, moment, action>
what: <quote versus required proof>
why: <decision/proof/risk cost> [evidence tag]
do: <keep|tighten|rewrite|collapse|split|move|expand|cut|confirm> — <specific action> [truth tag]
```

Every item declares `decisionEffect: decision|proof|risk|action|none` and `meta:{scope:atom|context,visibility:hotspot|supporting|clean}`. Use `hotspot` only when the item can change a gate, materially strengthen important proof, remove a credibility risk, or resolve a repeated pattern. If deleting the text changes none of the first four values, use `supporting` or `clean`; do not promote it to a hotspot. Length, terseness, polish, and keyword count never improve or lower the call by themselves.

Write visible advice to the person reading it, not about “the candidate.” Use ordinary words. The title says where to look; `why` says what the reviewer may conclude; `do` gives exactly one smallest action. Length is measured in sentences, never characters: a title is one clause, `why` prefers two sentences and never runs past four, and `do` is one sentence and never more than two. No sentence runs past fifteen words; split the thought or cut it. Do not count characters while writing — the renderer holds a ceiling and fails closed if prose runs away. If information is missing, ask directly whether the named condition existed or what specific outcome occurred, and name the item that should receive the answer. Never ask for “facts,” “evidence,” “proof,” or “if any.” Do not make the reader choose between actions or ask where a confirmed fact belongs. Do not expose analysis terms such as atom, gate, decisionEffect, provenance, semantic, vector, or PCOPO in candidate-facing copy. Every served line — reader evidence included — is a standalone document: never reference this conversation, and without a supplied JD never assert a target the person named only in chat; treat level or fit as a résumé-internal observation and ask to confirm the target. Do not grade the reader — no approval openers (“Strong,” “Good,” “Fine,” “Nice”) and no “make sure to.”

## Output

The product is the served interactive report. For `standard`, `rewrite`, and `skillmatch`, build the JSON island and render it in the same run, then hand back its link — do not ask first, and do not stop at an inline-only review. Build the island from the analysis that produced the decision; it is not a second pass.

`python3 references/agui_bridge.py render --island <island.json> --out <report.html> --serve`

On Windows the interpreter is `py -3`; `references/connections.md` carries the shell quoting.

Build the island against the data contract in `references/REPORT.md`; read the bridge or template source only when a validation error names something the contract does not cover. Never hand-edit the template per report. A validation failure or unavailable bridge writes nothing and falls back to the inline block below; `quick scan` is inline by default. Reports contain candidate PII: keep them local, never publish.

The inline block — the report's concise companion, and the full deliverable on fallback — follows this order:

1. `MOVE FORWARD...`
2. Must-Talk + ATS/screener/manager gates.
3. Why the role exists, when JD context exists.
4. Five-reader evidence in funnel order.
5. Gets Attention (≤3).
6. Ranked hotspots; supporting and clean observations remain revealable.
7. Do Next: fix now · confirm · defend.

A request for the updated resume or LinkedIn text — in any wording, including "give me the new version," "write it out," or a request for a file — is served by exporting the report:

`python3 references/agui_bridge.py export --report <report.html> --doc resume|linkedin [--format json] [--out <path>]`

Never reproduce, retype, or reconstruct either document from conversation context, an earlier draft, or the source file. Read it out of the report that holds the accepted edits. When no report exists, say so and offer to build one rather than assembling a version by hand.

Every read of and change to a served report goes through a bridge verb — `getContext`, `getItem`, `listRubric`, `getRubricContext`, `exportData` to read; `patchResume`, `patchLinkedin`, `setStatus`, `updateItem`, `acceptRewrite`, `rereadSection` to write. Never parse, regex, or hand-edit the island, and never load the bridge as a module to reach its internals. A named row is one read and one write.

The final hand-back names the report link, the Must-Talk rubric score, the first deciding gate, and the smallest next action. When the ask names a rubric, the Must-Talk 0–4 rubric — and the 0–5 demonstrated-skill rubric under a JD — is that rubric; score it and say so.

## Workbench

Each report item is independently editable and discussable:

- Edit opens a draft; Save persists before repaint; Cancel discards the draft.
- Accept rewrite updates resume text, `ctx.decisions`, and status in one transaction.
- Status persists through its own transaction.
- Converse, `getContext(n)`, and row Export JSON use exactly the item’s 13-key `ctx` capsule—never the full resume or unrelated items.
- Full-resume work requires the separately labeled cross-item export.
- The report opens with hotspots only. `Show all observations (N)` reveals supporting and clean rows without changing JSON or status.

The capsule keys are exactly: `itemId,path,lane,reader,atom,neighbor,evidence,truth,decisionEffect,suggestion,relatedIds,decisions,questions`. `neighbor` contains at most one adjacent atom needed to understand the item.

Keep capsules atomic and never serialize `resumeDoc` into a capsule value. Per-field character caps are defined once in `references/REPORT.md`.

An actionable row prompt contains these literal labels: `Item:`, `Atom:`, `Evidence:`, `Truth:`, `Decision effect:`, `Task:`. A clean `keep` may omit the prompt, never `ctx`.

## Outcome calibration

Keep observations in top-level `outcomes[]`:

`{resumeVersion,itemIds,window:{start,end},applications,callbacks,interviews,note}`

Use: before → smallest change → decision effect → observed outcome. Always label the result **observed after, not attributed to**. Outcomes may reprioritize future fixes; they never prove causation.

Outcome notes may describe observations; reject notes that say an edit `caused`, `proved`, or `resulted in` the outcome (unless explicitly negated).

## Conformance

Refuse to emit until all pass:

- Decision is first and derived by the total rule.
- Five reader passes remain visible.
- Every finding is atom- or context-scoped, four lines, tagged, and deletion-useful.
- Every item's `do` action edits the element its `ctx.path` names; an action whose edited text lands on a different role, employer, section, or period than the quoted line is misplaced and must move before emitting. Citing another role as the source of a fact is not a move.
- Evidence-equivalent long/terse versions produce identical gates and call.
- Gets Attention ≤3 and every item quotes its proof.
- Unsupported skills are ungraded.
- No match percentage, fit band, delta, invented fact, or causal callback claim.
- HTML uses contract `2.4.0`, canonical template+JSON, exact `ctx`, and local-only data.
- ATS narrates no parser behavior ("parses cleanly", "will parse", "ATS-readable") unless `meta.parseStatus.state` is `tested` with cited observed evidence; parse status never enters the decision vector or Must-Talk.

## References

- Reader passes and roll-up: `references/READERS.md`
- Winning bar and craft grading: `references/CRAFT.md`
- Report/JSON/workbench: `references/REPORT.md`
- Skill evidence: `references/SKILLMATCH.md`
- Rewrites: `references/REWRITE.md`
- Evidence capture: `references/EVIDENCE.md`
- Bridge operation: `references/connections.md`
