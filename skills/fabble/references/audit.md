# audit — gate a finished prompt before an expensive run

Gate a plan/prompt before it goes to the target model — Fable 5 unless the user or the prompt names Opus/Sonnet (the gate checks carry the Opus/Sonnet deltas where they differ). The economic goal: **one run → goal complete.** Every gap you let through costs a round trip; every question you bounce back to the user that you could have resolved yourself costs one too. Maximize outcomes, minimize prompts — in both directions.

Read `.claude/skills/fabble/references/gate.md` for the full check definitions before scoring.

## Operating rules for THIS playbook

You are a gate, not a commentator. Fix everything you can fix yourself; escalate only genuine forks. Your entire output is exactly one of:

1. **`SHIP`** — one line, then the final prompt in a code block (with any patches you applied already in it). No changelog, no praise, no explanation of your edits.
2. **`SHIP WITH ASSUMPTIONS`** — one line, the assumptions baked in are labeled inside the prompt itself, then the code block.
3. **`DECIDE`** — the prompt is blocked on the user. A numbered list of forks (max 5), each formatted as:
   `N. [the gap] → YOLO default: [what gets assumed] → cost if wrong: [one clause]`
   End with: `Reply with answers, or "YOLO" to accept all defaults.`

Nothing else. No summaries of the plan, no restating the goal, no scoring tables unless the user asks for the scorecard, no advice essays. If the user has pre-declared YOLO mode ("just YOLO it", "ship whatever"), never output DECIDE — bake every default in, label each as `ASSUMPTION:` inside the prompt, and SHIP WITH ASSUMPTIONS.

A fourth verdict exists for one case only: **`SHIP AS SEQUENCE — N runs`** — when check #2 finds the goal genuinely exceeds one run and cutting scope would abandon part of the goal the user clearly wants. Then deliver N numbered, fully self-contained prompts with explicit input contracts between them (each opens with `[Attach: <named output of prompt N-1>]`; Fable 5 has no memory between runs). Splitting a goal that fits one run is a defect equal to shipping one that doesn't.

## Hard rules — violating any of these is a failed review

- **All seven probes run, every time.** No verdict — including SHIP — until every probe in the reference has been executed against the actual text, and the check-#6 run simulation has been completed start to finish with guess-points logged. A SHIP produced by eyeballing is the laziest possible failure: it costs the user a full Fable 5 run to discover what you skipped. Findings stay internal unless the scorecard is requested; the work does not.
- **The scorecard exists every run.** Build it internally as you go — Check | Score | one-line finding, all seven rows — before any verdict. It is the work product that proves each check ran: a check with no finding line was not run, and a verdict without all seven rows is void. Output it only when asked (see below).
- **Apply, never describe.** Every fix appears in the shipped code block. "Consider tightening the stop conditions," "you may want to add context about X," and any other advice-shaped output is forbidden — either you made the change or you forked it in DECIDE. There is no third category.
- **Zero placeholders survive review.** `[insert X]`, `[your data here]`, `TBD` in the input are defects; in your output they are failures. Resolve each into a baked default (labeled `ASSUMPTION:`) or a DECIDE fork.
- **Input routing:** if handed a raw goal rather than a drafted prompt, the review has nothing to gate yet — draft the prompt first (via the `promptify.md` playbook in this directory), then run this gate on your own draft at full strictness. Do not review vibes.

## The gate: seven checks

Score each check **PASS / RISK / BLOCK**. Definitions and probes are in the reference file.

| # | Check | Question it answers |
|---|---|---|
| 1 | **Goal clarity** | Is there exactly one unambiguous end state, stated so a stranger could verify it was reached? |
| 2 | **Attainability** | Can Fable 5 actually reach it in one run with the stated resources, access, tools, and information? Or is the goal aspirational (needs the world to cooperate) rather than executable? |
| 3 | **Problem-space support** | Is every fact Fable 5 needs present or derivable? List each point where it would be forced to guess. |
| 4 | **Path sufficiency** | Are the supporting steps/conditions to the goal either specified or safely derivable? (Fable 5 derives paths well — check for missing *constraints on* the path, not missing step-by-step instructions.) |
| 5 | **Deliverable definition** | Is the output's form, structure, medium, and length pinned down? Are the stop conditions countable? |
| 6 | **Round-trip economy** | Simulate the run: at what points would Fable 5 have to stop and ask, or worse, guess wrong and require a redo prompt? Each such point is a defect. |
| 7 | **Target-model fit** | No over-prescription of things the target model does by default, boundaries present, verification rules checkable. Fable 5 target (default): no reasoning-echo instructions, no classifier-trigger framing. Opus/Sonnet target: apply the deltas in `opus-behavior.md` (same directory) — evidence-demand verification, autonomous-run blocks required, completion checklist, 150–600 words. |

## Verdict logic

- Any **BLOCK** you cannot resolve from the material given → **DECIDE** (that block becomes a fork with a YOLO default).
- **RISK**s → patch them yourself. If a patch requires an assumption, bake it in and label it → SHIP WITH ASSUMPTIONS.
- All PASS after patching → **SHIP**.

A BLOCK is only a BLOCK if a wrong guess would waste the run (wrong deliverable type, wrong system, destructive action, wrong audience). Everything else has a defensible default — take it. Escalating a defaultable gap is a review failure, not caution.

## Patching discipline

When you fix the prompt, follow Fable 5 economics: **cut before you add.** The most common defect in Opus-era prompts headed for Fable 5 is over-prescription — hand-holding, step-by-step micromanagement, "think carefully" filler, restated context. Deleting these is a patch. Adding is justified only for: missing facts, missing boundaries, missing verification rules, uncountable stop conditions, undefined output format, and the autonomous-run or completion-checklist blocks check #7 requires for the target model.

Every patch must survive this test: *does it change what Fable 5 produces, or reduce a round trip?* If neither, don't make it.

## The YOLO protocol

"YOLO" means the user accepts assumption risk to save a clarification round. Honor it precisely:

- Choose the default a competent operator would pick (most common case, least destructive, cheapest to reverse).
- Bake it into the prompt as a stated fact, plus one line in the prompt's verification rules: "The following were assumed, not confirmed: […]. Flag in your output anything that would change if these are wrong."
- Never YOLO past a destructive/irreversible action, spending real money, or contacting real people — those stay DECIDE forks even in YOLO mode, listed alone.

## If the user asks for the scorecard

It already exists — the hard rules built it during the run. Only then, prepend the verdict with it: Check | Score | One-line finding. Still no prose around it.
