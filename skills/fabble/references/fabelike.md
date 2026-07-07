# fabelike — existing prompt, stays on Sonnet/Opus, raised to its ceiling

Rewrite an existing Sonnet/Opus prompt so it extracts the most fable-like output those models can produce. The insight this playbook runs on: Fable 5's quality edge splits into two parts. The **contract** — intent stated, full spec up front, boundaries fenced, claims traced to evidence, done defined countably — is model-agnostic and ports completely. The **capability** — one-principle generalization, internal self-verification, hours-long coherence — does not port, but each gap has a known compensation that Fable wouldn't need and Sonnet/Opus do.

Doctrine in one line: **port the contract, compensate the personality.**

Read both behavior files before rewriting:
- `.claude/skills/fabble/references/fable5-behavior.md` — Fable defaults and steering snippets (the contract items are the GRAFT list below).
- `.claude/skills/fabble/references/opus-behavior.md` — what changes when the runtime is Sonnet/Opus.

If either file is missing, stop and tell the user rather than working from memory.

## Operating rules

- Output exactly two things: the enhanced prompt in a code block, then a change ledger (one line per change with the reason). "prompt only" suppresses the ledger. When Ceiling honesty triggers, its flag and path (b) offer follow the ledger — nothing else ever does.
- The runtime target does not change. Never introduce Fable-only assumptions (multi-hour unsupervised autonomy, self-managed memory across days, one-principle steering without scope).
- Never change what the prompt is *for*. All source facts, tool contracts, and output requirements survive.
- Zero placeholders; bake in or add `[Attach: …]` per `promptify.md`'s portability rule.

## The three moves

### 1. GRAFT — the fable contract, model-agnostic

Add whichever of these the source lacks. These improve output on every current model:

- **Purpose line.** "I'm working on X for Y; they need Z. With that in mind: [ask]." Highest-value single addition.
- **Full spec up front.** Fold progressively-revealed requirements from surrounding turns into the one prompt.
- **Boundaries.** Explicit fences: scope limits, forbidden side effects, flag-don't-do list.
- **Evidence-grounded claims.** On any prompt with checkable work: "A claim of done, passing, or verified must trace to a command run in this session with observed output; otherwise report it as unverified — never as done."
- **Countable done.** Measurable completion criteria, not "when finished."
- **Output format + lead-with-outcome.** Literal template or field list; summary opens with what happened.

### 2. COMPENSATE — where Fable relies on capability, substitute scaffolding

Most of these are things fablize would delete; here they earn their place:

- **Principle + explicit scope.** Every current model follows literally; Fable needs a rule's reach stated only where it isn't obvious, Sonnet/Opus need it on every broad rule. State the governing principle *and* its reach: "…this applies to every section, not just the first."
- **Externalized self-verification.** Fable self-checks internally; Sonnet/Opus need it in the prompt: "Before answering, walk the stop conditions one by one and confirm each is met; any unmet → keep working." For high-stakes deliverables, build the loop into the prompt itself: draft → review against the named criteria → revise, as explicit phases.
- **Plan-then-execute for ambiguity.** Fable scopes and proceeds; give Sonnet/Opus the hinge: "State your plan in one short paragraph, then execute it. Don't ask clarifying questions you can resolve with a stated assumption."
- **Quality modifiers.** "Go beyond the basics; include as many relevant features and interactions as possible" — noise on Fable, real fuel on Sonnet/Opus for open-ended builds. Keep or add for generative/design/feature work.
- **Tool nudges with why.** Keep explicit when-and-how tool guidance if the source's workflow depends on a tool the model undertriggers; state the reason, not just the command.
- **Step scaffolding for real ordering.** A numbered sequence for genuinely ordered work (migrate → verify → cut over) helps Sonnet/Opus and stays. Steps the model derives trivially still get cut.
- **Grounded-progress + no-early-stop as defaults.** On Fable these are long-run-only; on Sonnet/Opus include both whenever no human watches mid-run.
- **Work ledger on any multi-step run.** Fable holds a plan through compaction better; Sonnet/Opus drop step m of n. Externalize the task list (file or harness task list, one countable line per item, done only on evidence, re-read after any compaction) — the completion checklist then has a list guaranteed to still exist when it walks it.
- **Split goals that exceed one run.** Fable holds a multi-day goal in one prompt; Sonnet/Opus don't. If the goal outsizes a single sitting, deliver an ordered prompt sequence with explicit input contracts between runs (`promptify.md`'s sequence rules apply verbatim). This split-in-place covers goals that are merely oversized; a prompt built on fable-only capability assumptions throughout goes to Ceiling honesty instead.

### 3. CUT — garbage that hurts every current model

Same knife as fablize, shorter list — modern Sonnet/Opus overtrigger on this too:

- Emphasis walls (`CRITICAL:`, `YOU MUST`, `ALWAYS`) — one plain statement stays.
- "Think step by step / think carefully / be thorough" filler — adaptive thinking handles depth; steer with effort framing instead ("take the time to do this thoroughly; verify against the stop conditions before answering").
- Forced progress cadence ("summarize every N tool calls") — current models update well unprompted.
- Repetition — each rule keeps its single best statement, placed in the section where it bites (format rules inside Output Format, fences inside Boundaries).
- Role cosplay carrying no facts.

Note what is *not* cut here: reasoning requests are legal on Sonnet/Opus (no `reasoning_extraction` classifier). Keep a rationale-in-deliverable form anyway — chain-of-thought dumps are low-value output — but this is a quality call, not a run-killer.

## Ceiling honesty — mandatory

Fabelike narrows the gap; it does not close it. If the source prompt assumes capability that doesn't compensate — unsupervised multi-hour runs, first-shot builds from very large specs, cross-session memory the harness doesn't provide — the ledger must flag it and name both escalation paths:

```
! ceiling: source assumes ~4h unsupervised run — compensated with completion
  checklist + grounded progress, but expect drift. Two ways past the ceiling:
  (a) switch model: fablize + Fable 5, one run
  (b) stay on sonnet/opus: promote to a goal — `/until opus <the intent>` —
      re-authored as a well-specified goal and split into an ordered sequence
      of self-contained runs the model can actually complete
```

Path (b) is the answer when the user insists on Sonnet/Opus: stop patching the prompt and re-author from the intent. `/until opus|sonnet <ask>` invokes the `promptify.md` playbook with the Opus/Sonnet deltas; its "when one run cannot reach the goal" rules turn the fable-shaped task into N numbered prompts, each self-contained, each with an explicit input contract (`[Attach: the <named output> of Prompt N-1]`) and stop conditions the next run can consume. What Fable 5 achieves through capability in one run, Sonnet/Opus reach through specification across several. If the user has already said they're staying on Sonnet/Opus, don't just flag the ceiling — offer to run path (b) immediately, extracting the intent from the source prompt as the `/until` input. Either way deliver the compensated prompt and ledger first; path (b) runs only on the user's yes. (Do not confuse with Claude Code's built-in `/goal`, which runs a keep-working-until-condition loop in the current session.)

Never silently promise fable results on a fable-shaped task.

## Delivery gate — all must pass

Walk the items one by one against the actual enhanced text and confirm each — an item you did not walk is a failed item.

- Purpose, boundaries, evidence demand, and countable done present (or ledger states why one is genuinely inapplicable).
- Every broadly-applicable rule states its scope explicitly — read the prompt as a literal-minded executor; any rule requiring generalization to work fails.
- Completion checklist present on any multi-part deliverable.
- No emphasis walls, no thoroughness filler, no forced cadence, no repetition.
- Grounded-progress + no-early-stop present if the prompt runs unattended.
- All source facts, constraints, and formats survive (mental diff against source).
- Length: 150–600 words per prompt. The extra budget over Fable's band goes to evidence demands, the completion checklist, and justified step scaffolding — never restated context.
- Run simulation as Sonnet/Opus in a fresh session: zero guess/ask/missing-material points, zero rules that only work if generalized.

## Ledger format

```
+ grafted: purpose line — source carried no intent context
+ grafted: evidence demand — source had checkable work, no proof rule
~ compensated: "keep output brief" → principle + explicit scope (literal follower)
~ compensated: implicit verification → 3-item completion checklist
− cut: CRITICAL/MUST wall — overtriggers on current models
! ceiling: [only if a fable-shaped assumption was found]
```
