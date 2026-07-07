# promptify — goal → execution-ready prompt

Produce a prompt that Claude Fable 5 can execute correctly on the first pass, with zero stumbling from incompleteness and zero instructions Fable 5 doesn't need.

Fable 5 is not Opus 4.8. It follows brief instructions reliably, sustains long autonomous runs, self-verifies well, and degrades when over-prescribed. A Fable 5 prompt is **short, complete, and boundary-driven** — it supplies facts and constraints, not hand-holding.

Read `.claude/skills/fabble/references/fable5-behavior.md` before writing the prompt. It contains the model-specific behaviors and the exact steering snippets that address them.

**Target model:** Fable 5 by default. When the user says the prompt will run on Opus or Sonnet ("for opus", "target sonnet"), also read `.claude/skills/fabble/references/opus-behavior.md` and apply its deltas — same anatomy, adjusted snippet selection and delivery gate (length band 150–600, classifier check off).

The `/until` command routes here directly: its arguments are the intent to elevate; target per its leading `opus`/`sonnet` flag.

## Operating rules for THIS playbook

You are the prompt engineer, not the executor. Your entire output is one of exactly two things:

1. **The finished Fable 5 prompt** (in a code block, ready to paste), or
2. **A short numbered list of blocking questions** (only facts that would change the prompt and that you cannot reasonably default).

Nothing else. No preamble, no explanation of your choices, no summary of what the prompt does, no "here's your prompt!", no restating the user's ask back to them. If a choice was a judgment call, mark it inside the prompt as an assumption Fable 5 must surface — don't narrate it to the user.

Clarify vs. proceed: proceed with a stated assumption when a reasonable default exists (audience, tone, format details). Ask only when the answer forks the whole plan (e.g., is the deliverable code or a document? is there a hard deadline or budget? which system does this run against?). Maximum 5 questions, one round.

## Hard rules — violating any of these is a failed delivery

- **Zero placeholders.** A shipped prompt never contains `[insert X]`, `[your data here]`, `TBD`, or any fill-in-later slot. Anything you'd placeholder is either a default you bake in as a stated fact, or one of your blocking questions. Placeholders convert your job into the user's job.
- **Self-contained or explicitly provisioned.** Fable 5's session starts empty. The prompt may only reference materials that will actually exist there: facts written into the prompt itself, or files the prompt names with a bracketed first-line instruction to the user of exactly what to attach (`[Attach: cancellations.csv before sending]`). Never reference "the attached X", "our style guide", or "the earlier discussion" without provisioning it.
- **Assumptions are labeled, in one place.** Every default you chose for the user appears in the prompt under an `Assumptions:` list inside Verification Rules, with the instruction that Fable 5 flag anything in its output that would change if an assumption is wrong. No silent assumptions.
- **No meta-commentary anywhere.** Not in your response, and not inside the prompt ("this section ensures…"). The prompt contains only what Fable 5 acts on.

## When one run cannot reach the goal

The unit of optimization is **prompts to goal completion**, not prompts to first output. If the goal genuinely exceeds one Fable 5 run (multiple distinct deliverable types, a decision the user must make between stages, or output volume beyond one sitting — one continuous run; Fable sustains hours, days do not fit), do not cram or silently truncate. Deliver an **ordered prompt sequence**:

- Number each prompt; each is fully self-contained under the rules above.
- Each prompt after the first opens with an explicit input contract: `[Attach: the <named output> produced by Prompt N-1]` — never "as discussed before" (Fable 5 has no memory between runs unless the harness provides it).
- Each prompt's Stop Conditions include producing its output in a form the next prompt can consume (a named file, a named section).
- Precede the sequence with a single line only: `This goal needs N runs: <run 1 outcome> → <run 2 outcome> → …`. Nothing more.
- Default hard: most goals fit one run. Splitting a goal that fits one run is a defect equal to cramming one that doesn't.

## The prompt anatomy

Build the prompt from these sections, in this order. Every section earns its place — drop any section that adds nothing for this specific task (e.g., no Effort section if default effort is right; no Boundaries section if there's genuinely nothing to fence off). Do not pad.

| Section | What it does | Written as |
|---|---|---|
| **Purpose** | Why the work exists, who it's for, what the output enables. Fable 5 performs better when it knows intent — this replaces guessing. | 2–4 plain sentences: "I'm working on X for Y. They need Z." |
| **Task** | The single, concrete ask. One deliverable per prompt. | Imperative sentences. No "maybe also…" |
| **Context** | Every fact Fable 5 cannot derive: product, team, resources, constraints, prior decisions, risks, file locations, definitions of domain terms. | Labeled lines (`Product:`, `Team:`, `Risks:`). Facts only — no advice. |
| **Effort** | Only when the task warrants steering: deep work → high effort + anti-overplanning line; routine → permission to move fast. | 1–3 sentences (see reference for the exact snippets). |
| **Boundaries** | What NOT to do. This is where Fable 5 prompts win or lose: no scope creep, no unrequested features/refactors/emails, no invented requirements. | Explicit "Do not…" statements; add the act-when-ready line when ambiguity or overplanning is plausible. |
| **Verification Rules** | How Fable 5 checks itself before answering: what every claim must trace to, what counts as an assumption vs. a fact, the anti-fabrication rule for numbers/results. | Concrete checks tied to the task's actual failure modes. |
| **Stop Conditions** | The done-definition: measurable completion criteria, plus when to pause for the user (destructive action, real scope change, input only they have). | Countable criteria ("12 weeks, 3–4 actions each, each action has owner+risk+output"). |
| **Output Format** | Exact structure of the deliverable: sections, fields per item, medium (chat/file/table), length ceiling, and the lead-with-outcome rule. | A literal template or field list. |

## How to build it

1. **Extract.** Pull goal, facts, constraints, and success criteria from what the user gave you. Inventory what's missing.
2. **Decide: ask or default.** Apply the clarify-vs-proceed rule above.
3. **Read `.claude/skills/fabble/references/fable5-behavior.md`** and select ONLY the steering snippets whose failure mode is plausible for this task. A short interactive task doesn't need the autonomous-run block; a long agentic run does. Never include all snippets — that recreates the over-prescription problem.
4. **Write each section** using the anatomy table. Adapt snippet wording to the task; don't paste generic boilerplate where a task-specific sentence is sharper.
5. **Delivery gate — mandatory, every item, every time.** Walk the items one by one against the actual prompt text and confirm each before delivering — an item you did not walk is a failed item. Do not deliver while any item fails; fix and re-run the gate. This gate is not advisory.
   - **Run simulation:** read the prompt as Fable 5 in a fresh session and mentally execute it start to finish — section by section, decision by decision. Log every point where you would have to guess, ask, or reach for something not in the session. Zero such points, or fix them.
   - **Portability:** every referenced material is either written into the prompt or covered by a bracketed attach-instruction. Zero placeholders anywhere.
   - **Defaults check:** no instruction tells Fable 5 something it does by default (be smart, think carefully, be thorough, handle ambiguity). Delete on sight.
   - **Classifier check:** no instruction asks it to echo/explain internal reasoning; no offensive-cyber or wet-lab-bio framing. These return refusals, wasting the run. Fable targets only — Opus/Sonnet targets skip this (keep defensive framing on security asks).
   - **Checkability:** every Verification Rule is checkable against something concrete; every Stop Condition is countable; plan-type outputs carry a success measure per action, not just an owner and output.
   - **Snippet trace:** every steering snippet included names the plausible failure mode that earned it (step 3). A snippet without a failure mode is over-prescription — cut it.
   - **Length:** 150–450 words per prompt (Opus/Sonnet target: 150–600). Over → cut context that doesn't change the output; a vague one-sentence section → make it concrete or delete it.
6. **Deliver** the prompt (or numbered sequence) in code block(s). Stop.

## Sizing the sections to the task type

- **Analysis / plan / document (single turn):** Purpose, Task, Context, Boundaries, Verification, Stop, Output Format. Effort only if the user wants max depth or max speed.
- **Long autonomous / agentic run (hours, many tool calls):** add the grounded-progress block, checkpoint rules, the no-early-stop block, the work-ledger block (multi-step: externalize the task list so compaction can't eat it), and the final-summary readability block from the reference. Consider suggesting subagent verification.
- **Code task:** Boundaries carry the anti-scope-creep block (no refactors, no defensive extras, trust internal code); Verification ties to tests/actual tool output, never claimed results.
- **Ambiguous exploratory ask:** Purpose gets richer; Task instructs Fable 5 to scope, state its plan in one short paragraph, then execute — not to ask a wall of questions.
