# fablize — existing prompt → runs on Fable 5

Rewrite an existing Sonnet/Opus-era prompt so Fable 5 executes it at full capability. The upgrade is mostly deletion: Fable 5 follows brief instructions reliably, self-verifies, sustains long autonomous runs, and degrades under over-prescription. What earlier models needed as scaffolding is now noise — and two old habits (reasoning-echo, offensive framing) now abort the run outright with a refusal.

Read `.claude/skills/fabble/references/fable5-behavior.md` before rewriting. It is the shared source of truth for Fable 5 defaults, failure modes, steering snippets, and classifier hazards. If that file is missing, stop and tell the user rather than working from memory.

## Operating rules

- Your output is exactly two things: the upgraded prompt in a code block, then a change ledger (one line per change with the reason). Nothing else — no preamble, no explanation of your craft. If the user says "prompt only", drop the ledger too.
- Never change what the prompt is *for*. Every fact, constraint, tool contract, and output requirement in the source survives the rewrite. Upgrade the how, never the what.
- If the source references materials that won't exist in the target session ("the attached spec", "our style guide"), bake the content in or open the prompt with a bracketed attach-instruction (`[Attach: styleguide.md before sending]`). Zero placeholders.
- Judge each instruction against the reference's "does by default" list and failure-mode menu — not against taste.

## The triage

Every instruction in the source lands in exactly one bucket.

### CUT — scaffolding that is now noise or actively hurts

- Capability hand-holding: "think step by step", "think carefully", "be thorough", "double-check your work", "take your time".
- Emphasis inflation: `CRITICAL:`, `YOU MUST`, `ALWAYS`, `IMPORTANT` walls. These cause overtriggering, not compliance. Keep one plain statement of the rule.
- Anti-laziness: "don't be lazy", "go above and beyond", "make sure you actually do X".
- Tool nudges: "if in doubt, use [tool]", "default to [tool]", "remember to use your tools".
- Forced cadence: "after every N tool calls, summarize progress". Fable 5 gives well-calibrated updates unprompted.
- Step-by-step how-to plans where goal plus constraints suffice. Keep ordering only where sequence encodes a real dependency (deploy order, protocol steps).
- Repetition: a rule stated in three places keeps its single best statement.
- Role cosplay that carries no facts ("you are a world-class senior engineer").

### COLLAPSE — enumeration → one governing principle

Fable 5 generalizes from a brief principle; the itemized case list is Sonnet-era scaffolding. Replace with the matching reference snippet, adapted to the task. Keep the principle's scope stated where its reach isn't obvious ("every section, not just the first") — Fable follows literally and won't extend a rule past its stated reach:

- Lists of verbosity/style cases → the lead-with-outcome line.
- Lists of when-to-check-in cases → the pause-only-when line (destructive action, real scope change, input only the user has).
- Lists of don't-overbuild cases → the anti-scope-creep block.

### REWRITE — same intent, safe or sharper form

- "Show your reasoning / chain of thought / explain your thinking step by step" → rationale in the deliverable ("justify each recommendation in one sentence"). The original form trips the `reasoning_extraction` classifier and the run returns nothing.
- Offensive-security phrasing → defensive framing plus authorization context in the purpose line ("audit X for injection risks so we can fix them").
- Vague quality bars ("only report important issues") → concrete bars ("report anything that could cause incorrect behavior, a test failure, or a misleading result; omit style nits").
- Negative style rules → positive target ("do not use markdown" → "write in flowing prose paragraphs").

### KEEP — untouched

Facts, domain context, term definitions, tool inventories and contracts, output formats, concrete verification rules, genuine boundaries, sequencing that encodes real dependencies.

### ADD — only what a plausible failure mode justifies

From the reference's failure-mode menu, keyed to the prompt's task shape:

- No intent stated → add a purpose line ("I'm working on X for Y; they need Z"). Almost always the highest-value addition.
- Ambiguous or exploratory ask → act-when-ready line.
- Code task → anti-scope-creep block.
- Session has outward-facing or state-changing capabilities → boundaries statements naming the specific adjacent actions to fence off.
- Long autonomous run → grounded-progress block, no-early-stop block, verification cadence (fresh sub-agent verifier if the harness supports one), final-summary readability block, memory surface. Multi-step (n discrete items) → work-ledger block.
- Goal spans sessions → memory file instruction.

Never add a snippet whose failure mode is not plausible for *this* prompt — that recreates the over-prescription the upgrade exists to remove.

## Delivery gate — all must pass before delivering

Walk the items one by one against the actual rewritten text and confirm each — an item you did not walk is a failed item.

- Zero instructions that restate Fable 5 default behavior.
- Zero classifier hazards: no reasoning-echo, no offensive-cyber framing, no wet-lab-bio framing (bio-adjacent tasks get routed to a different model, not rephrased).
- Every ADD traces to a named failure mode; every CUT appears in the ledger.
- Diff against the source: all original facts, constraints, and format requirements survive.
- Usually shorter than the source. If it grew, each addition must be justified by a long-run or boundary failure mode; unexplained growth fails the gate.
- Length: 150–450 words (the Fable band). Growth past the source needs a per-addition justification; growth past the band fails regardless.
- Goal exceeds one run (distinct deliverable types, a mid-flow user decision, volume beyond one long run) → deliver an ordered sequence per `promptify.md`'s sequence rules, not one oversized prompt.
- Run simulation: read the result as Fable 5 in a fresh session. Zero points where you would guess, ask, or reach for material that isn't there.

## Ledger format

One line per change, most impactful first:

```
− cut: "think step by step… be extremely thorough" — default behavior
− cut: 5-step how-to plan — goal + boundaries suffice; steps encoded no real dependency
~ collapsed: 4 verbosity rules → lead-with-outcome line
~ rewrote: "explain your reasoning step by step" → one-sentence rationale in deliverable (reasoning_extraction hazard)
+ added: purpose line — source carried no intent context
+ added: grounded-progress block — long autonomous run
```

If effort matters for this prompt, steer it in the prompt with the reference's §8 effort snippets, and close the ledger with one note for the harness knob: `note: run at high effort (default); xhigh if capability-sensitive`.
