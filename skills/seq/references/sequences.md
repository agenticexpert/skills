# Sequences

- A sequence = an ordered list of step keys.
- Steps are defined once in the Step Library; sequences reference them by key.
- `standard` is the default (used when `/seq <task>` has no `as <name>`).
- Both `/seq` (inline) and `/minion` (delegated) run these same step semantics —
  seq reads them here; minion bakes `standard` into its dispatch template
  (`minion/references/dispatch.md` — when step semantics change, edit BOTH).
- Every step has EXIT ARTIFACTS: concrete outputs, not thinking. A step is
  complete when its artifacts exist. Artifacts are what the next step verifies
  against, and what the audit ledger carries between tasks.

## Inline output discipline (token saver)

seq runs in MAIN — every command's output lands in this window. Capture compact:
keep the pass/fail summary line, surface only the failing case(s). NEVER dump full
test/lint/build logs, or bulk file contents, inline. (minion's sub-agent absorbs
this in its own context; seq does not — so it matters more here.)

## Registry

| Name     | Steps                                                    | Use for |
|----------|----------------------------------------------------------|---------|
| standard | audit-before → work → audit-after → report               | Default. The full loop. |
| quick    | work → report                                            | Trivial/mechanical task, low risk, skip audits. |
| review   | audit-before → work → audit-after → verify → report      | High-risk task; fresh-eyes verification before report. |
| tdd      | audit-before → test-first → work → audit-after → report  | Code task with checkable behavior; prove the gap first. |
| deep     | audit-before → frame → work → attack → audit-after → report | Hard, ambiguous, or design-heavy task; buys reasoning depth (forced alternatives + self-critique) on any model. |

Add a row to define a new named sequence. One-off: `as <key>,<key>,...` runs an
unregistered sequence directly. Keep step keys from the Step Library.

## Project override — `.agents/seq/sequences.md`

The Registry and Step Library above are the built-in defaults. A project can
override them WITHOUT editing this skill by creating `.agents/seq/sequences.md`
(repo-relative). When that file exists, both seq and minion read it too:

- **Layered — override wins.** Its `## Registry` rows and `### <key>` step
  definitions layer over the built-ins; a Name or key it redefines replaces the
  built-in of that name. Anything it doesn't mention falls through to the
  built-ins.
- **Sets the default.** A `Default: <name>` line at the top makes `<name>` the
  sequence every bare `/seq <task>` / `/minion <task>` runs — in place of
  `standard`. Omit the line to keep the file's sequences available while leaving
  the default as `standard`.
- **Restore.** Delete the file → back to the built-in registry and `standard`.
  Or drop only the `Default:` line → keep your sequences, restore `standard` as
  the default.

Same format as this file: a `## Registry` table and `## Step Library` `### <key>`
sections, plus the optional `Default:` line. `as <name>` / `as <keys>` still
override per run and resolve against the override first, then the built-ins.

Minion note: a headless dispatch can only bake step definitions it can see —
resolution order at dispatch time (in main): the override file's Step Library →
this file's built-in Step Library → the four core steps the dispatch carries
(audit-before, work, audit-after, report). A step minion can't source from any
of those → minion says so and runs `standard` or asks. Capability caveat: the
sub-agent cannot spawn sub-agents — a step whose primary path needs one (e.g.
`verify`) runs via its stated inline fallback; no fallback defined → don't bake
it headless.

## Abort rule (all sequences) — WHEN / DO

WHEN any of these hit — a needed decision isn't in the spec or repo; a referenced
file is missing or contradicts; a criterion needs guessing; the premise is wrong;
the fix exceeds scope; an approach cannot be stated in ≤3 sentences →
DO: STOP inline and surface the blocker to the user, then wait. seq runs inline,
so it does NOT return — it pauses here. Never push through a broken premise.
Surface it in the four-line clarifier block (Problem / Choices / Rec / Answer) —
`SKILL.md → Surfacing a decision`. The blocker is the Problem line; the fork is
the Choices line. Never bury the ask under a wall of reasoning.

WHEN the blocker appears during audit-before, before any edit →
DO: clean stop, repo untouched. WHEN you already edited → DO: stop now and list
every change. An honest stop beats a forced bad flow.

## Audit reuse (token saver) — WHEN / DO

WHEN an audit-before — or the prior task's audit-after — was JUST run this session
AND it covers this task's surface: files ⊆ the audited set (or same-milestone
continuation) AND nothing mutated that surface since (beyond the audited task's
own validated edits) AND same session →
DO: reuse it. State the call out loud ("reusing audit from <task> — same files,
nothing changed"). Skip a fresh audit-before. Never reuse silently.

WHEN scope differs, the surface changed, or you are unsure →
DO: run a fresh audit. When unsure, always fresh.

WHEN the user says `--no-audit` / "skip audit" → DO: skip audit-before ONLY —
audit-after always runs. WHEN the user says `--audit` / "re-audit" → DO: force
fresh.

The reuse decision matches against the in-context audit ledger: a printed line
`LEDGER: task=<name> | surface=<globs> | approach=<one line> | proofs=<n/m met> | validated=<yes|no>`
recorded whenever an audit completes (here, or carried from a `/minion` `AUDIT`
output).
Same ledger across both skills — `/seq` then `/minion` (or reverse) reuses
cleanly. Ledger is session-only; new session → audit fresh.

## Step Library

### audit-before

Grounding + premise check, ending in a committed approach. Not a generic review.

- FIRST check Audit reuse above. Reusable → carry the prior artifacts forward,
  state it, skip the rest of this step.
- Else: read the spec first. Its referenced files + Criteria define the surface —
  do NOT read past it. No bulk directory reads to "get oriented."
- LOCATE before READ: grep/search for the exact symbols, anchors, and call sites
  the spec names. Open those regions, not whole files.
- READ NARROW: the narrowest view that answers the question — a symbol map /
  signatures, or a specific line range — not the full file. Full read ONLY a file
  you will edit.
- EXIT ARTIFACTS — print all three as one labeled block BEFORE the first edit
  (`AUDIT-BEFORE → premise: ... | approach: ... | proofs: ...`); block absent =
  step not run:
  1. **Premise verdict:** named anchors exist / minor drift (adjust minimally, no
     scope expansion) / premise broken → Abort rule.
  2. **Approach:** ≤3 sentences. Cannot state one → that IS a blocker; abort here,
     before any edit.
  3. **Proof plan + surface:** per Criteria checkbox, one line naming how it will
     be demonstrated (which test / command / observable), plus the list of files
     you expect to touch. No Criteria in the spec → derive proofs from its stated
     ask and say so.

### test-first (optional — code tasks)

- From the proof plan, write the failing test(s) that demonstrate the gap this
  task closes. Run them; confirm each fails for the expected reason.
- EXIT ARTIFACT: failing test names + one-line failure reason each. audit-after's
  proofs then run these same tests.

### frame (deep reasoning — front-load)

Commit to reasoning BEFORE the first edit — alternatives, not just an approach.
Think hard here: this step exists to buy reasoning depth on any model.

- Take audit-before's approach as a candidate, not a decision. Name ≥1 REAL
  alternative (a different mechanism, not a strawman) and reject it with a
  concrete reason (cost, risk, drift) — or adopt it and say why the switch.
- State the assumptions the chosen approach rests on — one line each, with how
  the work will falsify it EARLY (which file / test / behavior to check first).
- Name the most likely failure mode of the chosen approach and the guard for it.
- EXIT ARTIFACT — one labeled block, printed before any edit
  (`FRAME → chosen: ... | rejected: <alt> BECAUSE ... | assumptions: ... | failure-mode: ... guard: ...`);
  block absent = step not run. Cannot name a credible alternative → say so
  explicitly (`rejected: none credible BECAUSE ...`) — that line IS the artifact,
  silence is not.

### work

- Implement until every Criteria checkbox passes. No Criteria → done = the spec's
  stated ask; the report lists what you treated as done.
- Match surrounding style, naming, idiom. Obey the repo's own coding standards
  and CLAUDE.md.
- Reuse the surface from audit-before — don't re-read it. New file needed mid-work
  → open just the region you need, narrowest view first.
- Editing a file OUTSIDE the declared surface → state why at edit time (one
  line); audit-after checks these.
- Mid-work blocker matching the Abort rule → STOP, surface it, list edits made.
- EXIT ARTIFACT: the diff.

### attack (self-critique — post-work)

Attack your own diff before proving it. A different lens than audit-after:
proofs check the Criteria; attack hunts what the Criteria don't cover.

- Re-read the diff adversarially — "how does this break?" Hunt specifically:
  edge inputs, state not reset, order dependence, silent behavior change outside
  the Criteria, and every frame assumption — confirmed during work, or busted?
- Busted assumption left unhandled → fix or Abort rule. Finding → fix now.
  Concern that dies on inspection → one dismissal line WITH the reason — a
  dismissal without a reason is a finding.
- EXIT ARTIFACT: `ATTACK → angles: <tried> | found: <list or none> | fixed: <list or n/a>`.

### audit-after

Verify against audit-before's artifacts — not adjectives.

- Run each criterion's declared proof: met / not-met + one evidence line each.
  "Met" requires a command run this turn with observed output — reading the code
  is not proof. No runnable proof exists → say so explicitly, never silently pass.
- Surface check (mechanical): touched files vs. declared surface. Outside-surface
  edits → justified (stated during work) or reverted.
- Run the project's typecheck/lint + the relevant test suite (per CLAUDE.md).
  Both green before moving on — account for any documented pre-existing failures.
- Fix what fails; re-run its proof.
- EXIT ARTIFACT: one printed ledger line, exactly this format —
  `LEDGER: task=<name> | surface=<globs> | approach=<one line> | proofs=<n/m met> | validated=<yes|no>`.
  This is what the NEXT task's audit-before reuses instead of re-auditing; the
  fixed format survives compaction and reuse matches against it mechanically.

### verify (fresh eyes — high-risk)

- Spawn a read-only sub-agent: give it the diff + spec path ONLY — no chat
  context. It checks the diff against the spec's Criteria and returns
  pass / concerns. Fresh context = no self-justification bias.
- Sub-agents unavailable → inline fallback: re-read the diff with a stated
  adversarial focus ("how does this fail the spec?") — a different lens than
  audit-after's proof run, not a repeat of it.
- Concerns → fix and re-run the affected proof; premise-level → Abort rule.
- EXIT ARTIFACT: verdict + concerns list (empty allowed).

### pre-mortem (optional — high-risk)

- Run the pre-mortem skill against the approach artifact, before work begins.
- EXIT ARTIFACT: top failure modes + the mitigation each adds to the approach.

### report

- Three lines, simple language: outcome (what changed, does it work) / files
  touched / what's next or needs review. No padding beyond that.
- Item verdicts: WHEN the task worked discrete items — audit findings, review
  points, requested changes — DO: add one line per item, verb first:
  `<ACTION>: {item} BECAUSE {reason}` — FIXED / IGNORED / MERGED / DEFERRED /
  REVERTED, or any accurate verb, caps. Every item gets a line; a verdict
  without a BECAUSE is not a verdict.
- End your turn — do not start the next task. Do NOT commit / bump version /
  edit ChangeLog.

## Adding a step

- New step key → add a `### <key>` section here with its bullet definition AND
  its EXIT ARTIFACTS, then reference it in a sequence row (or run it ad-hoc via
  `as <key>,<key>,...`).
