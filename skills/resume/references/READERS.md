# Resume Readers — the gauntlet

Five readers in funnel order, each with a time budget, one question, and its
own verdict vocabulary. Honor each budget literally: a reader sees only what
their seconds reach — the 10-second skim never reaches page 2, so nothing
there can rescue its verdict. The funnel fails at the first reader who passes
on the candidate; that failure is the highest-damage finding.

## Target decode — JD context, before the readers

Find the reason the role exists through constraint inversion:

1. Turn prominent responsibilities into the costly conditions they prevent or outcomes they create.
2. Cluster repeated consequences. Select one dominant state change, not a list of duties.
3. Bind it to the beneficiary and operative constraint.
4. Write `Role exists to …` and mark it `confirmed|inferred|unknown`.

`confirmed` requires recorded user confirmation or source language that explicitly labels the causal purpose, such as “this role exists to” or “the primary purpose is”; action-verb duties remain `inferred`. `inferred` requires at least one exact JD quote and one confirming question. `unknown` carries no statement or evidence and asks what business result the role is expected to change. Keep at most three exact `jd|user` evidence records.

Then map candidate evidence without producing a match score. Choose the dominant central outcome first; select at most two decision-critical prerequisite responsibilities or conditions, not restatements of that outcome or every JD clause:

- non-negotiables: `proven|confirm|absent`; judge the core responsibility by semantic equivalence, not preferred verb strength or incidental scope modifiers; producing or updating its core artifacts proves maintaining the control; work on the same state variable can support `confirm`, while upstream reporting does not confirm a downstream decision
- central problem: `strong` for an explicit central result; `buried` when at least one substantive experience item directly names ownership, responsibility, or quantified scale for the central outcome/process but the full connection is implicit or split—a summary category alone does not qualify; `weak` for role scope or feeder activity only; `missing` for no relevant evidence; `unknown` for no defensible target
- differentiator: one evidenced statement or none
- smallest truthful repair: one confirmed action, one confirmation request, or none

Unconfirmed evidence permits `confirm`, never replacement wording. Reorder before rewriting; surface relevant proof early; compress the irrelevant; mirror JD language only when truthful.

## ATS — retrievability + evidence-visibility gate (automated)

Question: is the deciding content retrievable and attached to proof?
Checks: is the target identity findable · are the canonical role/domain/tool
terms present and *attached to* the evidence that earns them (not stranded in a
graphic, callout box, or skills blob) · are confirmed must-haves surfaced · is
the strongest qualifying evidence within the reader's reach. A supported
canonical term outranks an unsupported keyword list on the same facts; keyword
dumps, verbosity, and polish add no value.
**Verdict: pass / weak-pass / risky / fail — plus the named missing must-have
terms. Never a percentage.**
Classify each missing term: must include (truthful) · useful if truthful ·
not relevant · stuffing risk · needs evidence first. Never add a keyword the
candidate cannot defend in an interview.

No JD or confirmed target bar: grade retrievability and evidence visibility only. Missing unspecified keywords, tools, education, or contact fields are unconfirmed risks, not ATS deductions. Normalize to explicit facts before scoring; evidence-equivalent long and terse versions must receive the same ATS value.

Parsing is `untested` unless a directly observed extraction artifact or parser command is on record. Untested parsing can neither raise nor lower ATS, and never licenses a "parses cleanly" / "will parse" / "ATS-readable" claim; buried or detached proof lowers ATS on *retrievability* grounds without asserting any parser behavior. Tested parsing may move ATS only through the cited observed evidence.

## Recruiter — 10-second skim

Question: do I instantly know what this person is and why they might fit?
Checks: headline · summary first line · current title · lane clarity ·
above-the-fold proof · obvious mismatch risk.
Kills — reach and legibility only: no lane readable in 10 seconds · strongest
proof below the fold or out of skim reach · too many lanes at once · title
that contradicts the target.
A single generic line never kills this read, and padding never rescues it: the
same proof reachable in a padded and a terse version reads the same. But this
reader's verdict is comparative — `stop-and-read` means it beat the rest of the
stack in ten seconds, not that nothing was wrong with it. Apply the aggregate
craft rule in `CRAFT.md`: when a third or more of the elements inside the
ten-second reach grade `median` or worse, this verdict falls one step, because a
page of interchangeable lines is what the skim is built to discard.
Verdict: stop-and-read / maybe / confused / pass.

## HR — 30-second fit check

Question: does this person fit the level, band, role type, and basics?
Checks: seniority fit · title risk · dates and tenure pattern · leadership vs
IC balance · hard gatekeepers (degree, location, clearance) · communication
clarity · stability concerns.
Verdict: advance / advance-with-concern / hold / reject.

## Hiring manager — 2-minute relevance read

Question: can this person solve my actual problem?
Checks: problem–solution fit · ownership level (drove it or was near it?) ·
strongest accomplishment's relevance to this problem · delivery proof ·
ambiguity handling · business impact · a concrete reason to interview.
Verdict: interview / maybe / not-enough-signal / no.

## Technical reviewer — 10-minute credibility pass

Question: can this person do — and defend — what the resume claims?
Checks: technical specificity · architecture depth · production realism
(permissions, retrieval, streaming, data access, failure handling — not
"scalable" without scale) · quality/security/reliability thinking ·
unsupported technical claims → flagged as interview risk, not ignored.
Verdict: credible / credible-needs-proof / risky / not-credible.

## Red flags — what readers infer, and honest neutralization

What the reader infers, unprompted: gap → inactive or unexplained · layoff →
performance-related · short tenure → unstable · many roles → unfocused ·
senior/executive title → expensive, not hands-on · IC target after
leadership → step-down risk · strongest proof old → stale · missing degree →
gatekeeping fail · AI-heavy wording → hype without production proof.

Rules: no lying · no fake continuity · no over-explaining on the page · no
novelty formatting a real reader has never seen (scope facts jammed into a
title line read as AI, not as fixes).

Neutralize honestly: move current proof above the risk · target-level
headline · clarify the operating model · compress old or irrelevant roles ·
group short project/consulting work when truthful · year-only dates only when
appropriate and consistent · frame seniority as relevant scope, not
hierarchy · replace apology language with direct evidence. A concern that
cannot be neutralized on the page → **interview defense**: the short spoken
answer, the proof to lead with, the claims to avoid.

Overqualification check: does the resume imply the candidate wants a bigger
job than the target? Does it show why this role is a deliberate fit, operated
at level, not checked out?

## Buyers and lanes — positioning

Buyer types: startup needing ownership · company needing a specialist ·
enterprise needing scale proof · team needing technical leadership · product
org needing delivery · customer-facing org needing translation · AI org
needing production maturity · platform org needing architecture depth.

Per candidate lane: fit strength · resume evidence · missing proof · title
risk · interview risk · best headline. Seniority check: too senior, too
junior, too broad, too executive for IC, too hands-on for executive, too
startup for enterprise (and each reverse)?

**Positioning thesis**, three lines: *strongest when … · should avoid roles
that … · the resume must make the reader believe …*

## Three-gate roll-up

Keep all five reads above. Roll them up only after they finish:

- ATS: `fail|risky|weak-pass|pass` from the ATS read.
- Screener: `no-call|maybe|call|urgent-call` from recruiter + HR evidence.
- Manager: `no|insufficient|interview|priority-interview` from hiring-manager + technical evidence.

Each gate tracks the normalized fact vector plus the aggregate craft grade in
that reader's reach. A gate falls on proof that is absent, unreachable,
contradicted, or barred by a hard gatekeeper or genuine target mismatch — and on
craft in aggregate, by the one-step rule in `CRAFT.md`. An isolated soft concern
that rests on a fact already in the vector — limited history behind an owned
quantified outcome, a single strong role, one line that could be tighter, depth
that needs interview defense — surfaces as a ranked finding and does not lower
the gate. Padding never raises a gate: equal content at different lengths renders
equal gates.

First matching rule wins:

1. ATS `fail` → Must-Talk 0.
2. ATS `risky`, screener `no-call`, or manager `no` → 1.
3. ATS `weak-pass`, screener `maybe`, or manager `insufficient` → 2.
4. A verbatim urgency quote supporting `urgent-call` or `priority-interview` → 4.
5. ATS at least `weak-pass`, screener at least `call`, manager at least
   `interview`, **and** a named reason this resume beats the stack — a `winning`
   element the reader reached, or evidence no comparable candidate carries → 3.
6. Otherwise → 2. Absence of a reason to reject is not a reason to call.

Rule 5 requires the reason to be written down and quoted. `3` is a positive
finding about this document, never the residue left when nothing disqualifying
was found.

Must-Talk 0/1 → `MOVE FORWARD: no`; 2 → `not yet`; 3/4 → `yes`. The reason names the first deciding gate or quotes the urgency signal. A JD can set the bar; it cannot replace this decision.
