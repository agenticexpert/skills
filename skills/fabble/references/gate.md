# Gate Checklist — Check Definitions & Probes

Seven checks. Each has probes — concrete tests executed against the actual prompt text, not impressions of it. Run every probe of every check before any verdict. Score each check PASS / RISK / BLOCK per the rubric at the bottom.

## Check 1 — Goal clarity

One unambiguous end state, verifiable by a stranger.

**Probes:**
- Extract the end-state sentence verbatim. Can't find one sentence that states it → BLOCK.
- Stranger test: could someone with no context on this conversation read the end state and decide yes/no whether it was reached? "Improve", "better", "explore", "help with", "look into" without a measure fail this.
- Count the goals. More than one distinct end state → either one is the real goal and the rest are path (rewrite), or it's a genuine multi-goal (feed to check #2 for sequence assessment).
- Success criteria vs. activity: "analyze the data" is activity; "a ranked list of the top 5 churn drivers with supporting numbers" is an end state. Activity-framed goals → RISK, rewrite as end state.

## Check 2 — Attainability

Reachable in one run with stated resources. Executable, not aspirational.

**Probes:**
- Resource inventory: list every access, tool, credential, dataset, and file the goal requires. Each must be stated as available, provisioned via attach-instruction, or plainly unnecessary. Unlisted-but-required → guess-point for check #3.
- Aspirational scan: does the end state require the world to cooperate — users to sign up, a third party to respond, time to pass, approvals mid-run? Aspirational goal → BLOCK unless rewritable to its executable core ("get 1,000 signups" → "build and deploy the landing page + waitlist"; rewrite is a patch, note as assumption if it narrows intent).
- One-run volume: estimate the output honestly. Multiple distinct deliverable *types*, a user decision required between stages, or volume beyond one sitting → sequence candidate (SHIP AS SEQUENCE). A single large deliverable that fits one long run is NOT a sequence trigger — Fable 5 sustains hours; splitting a one-run goal is a defect. Opus/Sonnet target: the bar drops — those models don't hold a multi-sitting goal, so a goal exceeding one sitting is a sequence candidate even with a single deliverable type.
- Capability check: is any required step something no model can do from a chat session (physical action, accounts it can't touch, live human interviews)? → BLOCK or rewrite to the executable boundary.

## Check 3 — Problem-space support

Every fact Fable 5 needs is present or derivable. The session starts empty.

**Probes:**
- Noun sweep: every named system, product, person, team, metric, and domain term — is it defined in the prompt or genuinely common knowledge? Undefined internal names ("the Phoenix pipeline", "Marcus's spreadsheet") → guess-points.
- Reference sweep: every "the attached", "our", "the earlier", "as discussed" — is the material written into the prompt or covered by a bracketed attach-instruction (`[Attach: X before sending]`)? Unprovisioned reference → BLOCK (nothing exists in the session to resolve it).
- Guess-point list: walk the task; at every decision Fable 5 would make, ask "does the prompt give the fact that decides this?" Log each miss. Defaultable miss → patch as labeled assumption. Fork-grade miss (wrong guess wastes the run) → DECIDE.
- Freshness: does the task depend on facts newer than the prompt states (current prices, versions, org structure)? Either supply them or explicitly authorize/direct lookup.

## Check 4 — Path sufficiency

Constraints on the path, not steps of the path. Fable 5 derives good paths from goal + constraints; it can't derive constraints that live only in the user's head.

**Probes:**
- Missing-constraint scan: is there a plausible path that satisfies the goal as written but the user would reject? (Wrong stack, wrong tone, forbidden approach, breaking an unstated compatibility, touching a system that's off-limits.) Each such path reveals a missing Boundary or Context line → patch.
- Order dependencies: are there real sequencing constraints (X must exist before Y, don't deploy before tests)? Stated, or safely obvious?
- Step-by-step smell (inverse defect): numbered how-to instructions for things Fable 5 derives — micromanaged steps, prescribed sub-plans. The test: could the executor recover the order from the goal and constraints alone? Recoverable → delete. Not recoverable (deploy order, protocol steps, a required call sequence) → genuine constraint, keep. Cutting is a patch.
- Dead ends: does the prompt say what to do when the primary approach fails (fallback authorized? stop and report?), where failure is plausible?

## Check 5 — Deliverable definition

Form, structure, medium, length pinned; stop conditions countable.

**Probes:**
- Medium named? (chat answer / file / table / doc / code + where it lives.) Missing → patch with the obvious default, labeled if non-obvious.
- Structure: sections or fields per item enumerated? A plan-type output must carry a success measure per action — owner + output alone fails.
- Length ceiling present where length matters? "Comprehensive" is not a length.
- Stop-condition count test: rewrite each stop condition as a number or a binary. "Cover the important cases" fails; "12 weeks, 3–4 actions each, every action has owner+risk+measure" passes. Uncountable → patch.
- Pause conditions: destructive actions, real scope changes, and user-only inputs listed as stop-and-ask points where the task can hit them?

## Check 6 — Round-trip economy (the run simulation)

**Mandatory procedure — execute in full, log results internally:**

1. Read the prompt as the target model in a fresh session: only the prompt text and named attachments exist. Opus/Sonnet target: simulate its deltas — optimistic completion claims, early stop on multi-part work, no generalization beyond stated scope.
2. Execute mentally start to finish, section by section, decision by decision.
3. At each decision, classify: **(a)** answered by prompt — continue; **(b)** defaultable guess — log; **(c)** fork-grade guess (wrong answer wastes the run) — log; **(d)** would stop and ask — log.
4. At the end, check the deliverable produced by simulation against the stated goal: same thing? A simulation that "completes" but produces the wrong deliverable is a failed prompt, not a passed check.
5. Disposition: every (b) → patch with labeled assumption; every (c) and (d) → DECIDE fork with YOLO default; zero logged points → PASS.

Redo-cost lens for classification: a round trip costs a full run. A guess whose worst case is a small revision is defaultable (b). A guess whose worst case is "throw the output away" is a fork (c).

## Check 7 — Target-model fit

Default target: Fable 5 — run the scans below as written. Target is Opus/Sonnet
(user said so, or the prompt names it): apply the deltas in
`opus-behavior.md` (same directory) — classifier scan off (keep defensive framing on
security asks), grounded-progress / no-early-stop REQUIRED
on autonomous runs and the completion checklist on any multi-part deliverable (not over-prescription), verification rules must name the
command or source that proves them, length band 150–600.

**Over-prescription scan (cut on sight — cutting is a patch):**
- Instructions for defaults: "think carefully", "be thorough", "double-check your work", "handle edge cases", "be smart about ambiguity". Fable 5 does all of these unprompted.
- Emphasis inflation: `CRITICAL:`, `YOU MUST`, `ALWAYS`, repeated rules. State once, plainly — repetition causes overtriggering, not compliance.
- Step-by-step scaffolding for derivable work (overlaps check #4 — cut there counts here).
- Forced-progress scaffolding ("summarize after every N tool calls") — Fable 5 updates well by default.
- Example stacks — more than one worked example for the same output shape; keep the single best, cut the rest.

**Classifier scan (any hit → patch the framing or DECIDE; a tripped classifier refuses and wastes the whole run):**

| Trigger | What trips it | Safe reframe |
|---|---|---|
| Reasoning echo | "show your chain of thought", "explain your internal reasoning", "output your thinking" | Ask for rationale in the deliverable ("one-sentence justification per recommendation") |
| Offensive cyber | Exploit/attack framing, "break into", "bypass" — even benign security work false-positives on offensive phrasing | Defensive framing + explicit authorization/purpose in Purpose section ("audit X for vulnerabilities so we can fix them") |
| Wet-lab bio | Research-biology protocols, pathogen/synthesis framing | Not reframable — Fable 5 isn't intended for the domain; flag as DECIDE (different model) |

**Presence checks:**
- Boundaries section exists when the session could act outward or the goal invites scope creep (code, comms, state changes). Missing where needed → patch.
- Verification rules checkable against something concrete (a source, a tool result, a stated criterion) — "verify your work is correct" is not a rule.
- Autonomous-run blocks (grounded progress, no-early-stop, final-summary readability) present for long agentic runs, absent for short interactive tasks. Wrong direction either way → patch.
- Work-ledger block present when the run is multi-step (n discrete items) and long enough to hit compaction — mandatory on Opus/Sonnet targets for any autonomous multi-step run (`opus-behavior.md` §9); absent on short single-deliverable tasks. Wrong direction either way → patch.
- One worked example present when the output shape is nontrivial and described only in prose — mandatory on Opus/Sonnet targets (`opus-behavior.md` §10), permitted on Fable. Marked as illustration so content isn't copied.
- Purpose states who it's for and what the output enables (Fable 5 performs better knowing intent).
- Length 150–450 words per prompt. Over → cut context that doesn't change output. A vague one-sentence section → concretize or delete.

**Prompt anatomy** (fallback drafting template when handed a raw goal and `promptify.md` is unavailable; also the shape patches should preserve):

Purpose (2–4 sentences: I'm working on X for Y; they need Z) → Task (single concrete ask, imperative) → Context (labeled fact lines) → Effort (only if steering warranted) → Boundaries (explicit do-nots) → Verification Rules (concrete checks + labeled `Assumptions:` list with flag-if-wrong instruction) → Stop Conditions (countable done-definition + pause points) → Output Format (literal template/field list). Drop any section that adds nothing; never pad.

## Scoring rubric

| Score | Meaning | Disposition |
|---|---|---|
| **PASS** | All probes clean | Nothing to do |
| **RISK** | Defect with a defensible default, or a cut-only fix | Patch it yourself; label assumptions; counts toward SHIP WITH ASSUMPTIONS if an assumption was baked |
| **BLOCK** | Wrong guess wastes the run: wrong deliverable type, wrong system/target, destructive or outward action, wrong audience, unprovisioned material that can't be defaulted | DECIDE fork with YOLO default — unless resolvable from the material given, then resolve and downgrade |

Bias check before finalizing: recount your DECIDE forks. Each one you could have defaulted is a review failure equal to a missed gap. Max 5 forks; if you have more, you're escalating defaultables.
