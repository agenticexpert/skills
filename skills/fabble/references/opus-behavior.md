# Opus / Sonnet — Behavior Deltas & Steering Snippets

Target-model deltas for prompts executed by Claude Opus (4.6+) or Claude Sonnet
instead of Fable 5. Same prompt anatomy, different snippet selection. Read
`fable5-behavior.md` first — this file states only what CHANGES; everything not
mentioned here carries over unchanged (Purpose framing, boundaries statements,
anti-scope-creep block, act-when-ready line, memory surface).

## What still holds

- Brief, explicit instructions beat emphatic repetition — Opus 4.8 follows a rule
  stated once. Don't re-inflate prompts with `CRITICAL:` / `YOU MUST`.
- Full spec up front; goal + constraints over step enumeration for derivable work.
- Purpose framing improves output on all current models.
- Zero placeholders / self-contained rules — model-independent.

## What changes

### 1. Verification must demand evidence, not honesty

Fable self-verifies well by default; Opus/Sonnet claim completion optimistically.
Include on every prompt with checkable work (not just long runs):

> A claim of "done", "passing", or "verified" must trace to a command you ran in
> this session with observed output. If you did not run it, report it as
> unverified — never as done.

### 2. Grounded-progress + no-early-stop are DEFAULT for autonomous runs

On Fable these blocks are selected only for long runs; for Opus/Sonnet include
both whenever no human is watching mid-run. Use the snippet wording from
`fable5-behavior.md` §4 and §5 unchanged.

### 3. Completion checklist — close the Stop Conditions with it

Opus/Sonnet stop early on multi-part deliverables. Add:

> Before answering, walk the stop conditions above one by one and confirm each is
> met. Any unmet → keep working. Never deliver a partial result without labeling
> exactly what is missing.

### 4. Point-of-use constraint placement

Long-context instruction adherence decays on Opus/Sonnet. Don't repeat rules —
place each constraint in the section where it bites: an output-format rule inside
Output Format, a don't-touch-X rule in Boundaries next to the work that could
touch X. One statement, positioned; not three statements.

### 5. Step scaffolding allowed for genuinely multi-part work

Fable's de-prescription rule relaxes. A numbered step list for a task with real
ordering (migrate → verify → cut over) helps Opus/Sonnet and does not degrade
output. Still delete steps the model derives trivially; keep only ordering that
is a genuine constraint.

### 6. Effort steering

No `effort` parameter semantics to lean on. Steer with framing: deep work →
"take the time to do this thoroughly; verify against the stop conditions before
answering" — pair with the act-when-ready line to prevent deliberation loops.
Adaptive thinking handles depth on 4.6+; no "think step by step" filler.

### 7. Classifier hazards — table does not apply

The Fable-specific refusal classifiers (`reasoning_extraction`, etc.) don't run
on Opus/Sonnet. The reasoning-echo ban stays as a quality rule (chain-of-thought
dumps are low-value output), and security tasks still carry defensive framing +
authorization in Purpose — but as ordinary-refusal hygiene, not classifier
avoidance. Never spend a DECIDE fork on it.

### 8. Length band

150–600 words per prompt (vs. 150–450 for Fable). The extra budget goes to
evidence-demand lines, the completion checklist, and justified step scaffolding —
never to restated context or emphasis.

### 9. Work ledger is DEFAULT for multi-step autonomous work

On Fable the work-ledger block (`fable5-behavior.md` §13) is selected only when
compaction or m-of-n drop is plausible; Opus/Sonnet stop early on multi-part
work and lose plan items to compaction more readily — include the block on ANY
autonomous run with n discrete items. It is what the completion checklist (§3)
walks against: the checklist proves each item done; the ledger guarantees the
list itself survived to be walked.

## Delivery-gate adjustments (also for audit check #7)

When the target is Opus/Sonnet:

- **Defaults check:** "be thorough / think carefully / double-check" still
  deleted — noise on every current model. But grounded-progress and no-early-stop
  are REQUIRED on autonomous runs, and the completion checklist on any multi-part
  deliverable — not over-prescription.
- **Classifier check:** skip (§7); keep defensive framing on security asks.
- **Checkability:** unchanged — and each Verification Rule should name the
  command or source that proves it (§1).
- **Length:** gate at 150–600 words.
