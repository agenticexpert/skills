# Fable 5 — Behavior Reference & Steering Snippets

How Claude Fable 5 (and Claude Mythos 5 — identical behavior) actually behaves, and the exact snippets that steer each failure mode. Select ONLY the snippets whose failure mode is plausible for the task at hand. Including all of them recreates the over-prescription problem this skill exists to avoid.

## What Fable 5 does by default — never instruct these

Instructions covering any of the following are noise; the delivery gate deletes them on sight:

- Thinks before acting (thinking is always on; depth self-calibrates to the task).
- Follows brief, explicit instructions reliably — one clear sentence beats three emphatic ones. `CRITICAL:`, `YOU MUST`, `ALWAYS` cause overtriggering, not compliance.
- Self-verifies well, especially at higher effort. Don't add generic "double-check your work" — only task-specific verification rules earn their place.
- Handles ambiguity by scoping and proceeding; sustains hours-long autonomous runs; gives regular, well-calibrated progress updates on long traces without being told to.
- Delegates to parallel sub-agents dependably (unlike prior models, this doesn't need suppressing).
- Interprets instructions literally and precisely. It won't generalize an instruction beyond its stated scope — if a rule should apply broadly, say so ("every section, not just the first").

**De-prescription rule:** prompts written for prior models are often too prescriptive for Fable 5 and *reduce* output quality. State the goal and constraints; don't enumerate the steps. If converting an existing prompt, strip step-by-step scaffolding first, then re-add only what the failure modes below justify.

## Failure modes → steering snippets

Adapt wording to the task; a task-specific sentence beats generic boilerplate.

### 1. Overplanning on ambiguous tasks — the act-when-ready line

**When:** ambiguous or exploratory asks, or any task where deliberation could substitute for output.

> When you have enough information to act, act. Do not re-derive facts already established, re-litigate a decision already made, or narrate options you will not pursue. If you are weighing a choice, give a recommendation, not an exhaustive survey.

### 2. Scope creep — the anti-scope-creep block

**When:** code tasks, or any deliverable where "more" is worse. This is where Fable 5 prompts win or lose.

> Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper. Don't design for hypothetical future requirements — do the simplest thing that works well. Don't add error handling, fallbacks, or validation for scenarios that cannot happen. Trust internal code and framework guarantees; validate only at system boundaries (user input, external APIs).

### 3. Unrequested adjacent actions — the boundaries statements

**When:** the session has outward-facing or state-changing capabilities (email, git, deploys, config), or the ask is diagnostic rather than a change request. Fable 5 sometimes takes adjacent-but-unrequested actions (composing the email it drafted advice about, creating backup branches).

> When the request is a question or a problem description, the deliverable is your assessment. Report findings and stop; don't apply a fix until asked.
> Before any command that changes system state — restarts, deletes, config edits — confirm the evidence supports that specific action, not just a pattern-match to a known failure.
> Do not [send / publish / delete / contact] anything. [Name the specific adjacent actions to fence off.]

### 4. Fabricated status on long runs — the grounded-progress block

**When:** long autonomous / agentic runs (many tool calls, hours). Nearly eliminates fabricated status reports.

> Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. If tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.

### 5. Early stop / permission-asking — the no-early-stop block

**When:** autonomous pipelines with no human watching. Deep into long sessions Fable 5 can end a turn with a statement of intent ("I'll now run X") instead of the tool call, or ask permission it doesn't need.

> You are operating autonomously; no one can answer questions mid-task, so asking "Want me to…?" blocks the work. For reversible actions that follow from the request, proceed without asking. Before ending your turn, check your last paragraph: if it is a plan, a question, next steps, or a promise about undone work, do that work now. End only when the task is complete or blocked on input only the user has.

### 6. Checkpoint rules — self-verification cadence

**When:** long builds where drift compounds. Fresh-context verifier sub-agents outperform self-critique — suggest them when the harness supports sub-agents.

> Establish a method for checking your own work as you build; run it every [interval / milestone], verifying against [the specification / stop conditions]. [If sub-agents available:] Use a fresh sub-agent to verify against the spec rather than reviewing your own work.

### 7. Unreadable wrap-ups — the final-summary readability block

**When:** long agentic sessions whose output a human reads cold. Deep into a run, Fable 5 can produce dense shorthand humans can't follow.

> Your final summary is for a reader who saw none of your work. Open with the outcome — one sentence on what happened or what you found — then supporting detail. Complete sentences; spell out terms; no arrow chains, invented labels, or packed identifier lists. When you mention files, commits, or flags, say in plain language what each is or what changed. If forced to choose between short and clear, choose clear.

### 8. Effort steering

**When:** only when default effort is wrong for the task. Fable 5 respects effort framing strictly — at the low end it scopes to exactly what was asked.

Deep work (pair with the act-when-ready line, or thoroughness becomes overplanning):

> This deserves your full depth. Work the problem end to end and verify the result against [the stop conditions] before answering.

Routine work — permission to move fast:

> This is routine. Move fast and answer directly; no deep exploration or verification scaffolding needed.

### 9. Sub-agent delegation

**When:** long runs with independent parallel workstreams. Don't suppress delegation (a prior-model guardrail); guide when it's desirable.

> Delegate independent subtasks to sub-agents and keep working while they run. Intervene if a sub-agent goes off track or is missing context. Do the work directly when a single read or command would answer it.

### 10. Context anxiety

**When:** very long sessions, especially if the harness shows a remaining-token countdown. Fable 5 can worry about running out of context and suggest stopping.

> You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits — continue the work.

### 11. Purpose framing — why the Purpose section exists

Fable 5 performs measurably better when it knows the intent behind a request — it connects the task to relevant information instead of inferring intent. This is the template the Purpose section implements:

> I'm working on [the larger task] for [who it's for]. They need [what the output enables]. With that in mind: [the ask].

### 12. Memory surface

**When:** the goal spans multiple sessions and the harness gives Fable 5 somewhere to write. Even a plain `.md` file helps.

> Record lessons in [file], one per entry with a one-line summary on top — corrections and confirmed approaches alike, with why they mattered. Consult it at the start of each session. Update rather than duplicate; delete entries that prove wrong.

### 13. Plan attrition — the work-ledger block

**When:** multi-step runs (n discrete items) long enough to hit context compaction, or any run where silently dropping step m of n is plausible. The in-context plan is compaction-prey — a summarized plan can lose items without the model noticing. Externalize it.

> Before starting, write the full task list to [file / the harness task list]: one line per item, countable, each with its done-criterion. Work the items in listed order unless a stated dependency says otherwise. Mark an item done only when its evidence exists — never in advance. After any context compaction or summary, re-read the ledger before continuing: the ledger, not your memory, is the source of truth for what remains. Done means every item is checked; stopping before that means naming each unchecked item and why.

## Named one-liners the playbooks collapse to

- **Lead-with-outcome line** (lives in Output Format): "Open with the outcome — one sentence on what happened or what you found — then supporting detail."
- **Pause-only-when line** (lives in Stop Conditions): "Pause for the user only on: a destructive or irreversible action, a real scope change, or input only they have. Otherwise proceed."

## Classifier hazards — instructions that waste the run

Fable 5 runs safety classifiers on requests. A tripped classifier returns `stop_reason: "refusal"` — the run produces nothing. The delivery gate rejects prompts containing:

| Hazard | Category | What trips it | Safe framing |
|---|---|---|---|
| Reasoning extraction | `reasoning_extraction` | "Show your chain of thought", "explain your internal reasoning", "output your thinking verbatim" | Ask for a *rationale in the deliverable* ("justify each recommendation in one sentence") — never for internal reasoning itself |
| Offensive cyber | `cyber` | Exploit development, attack framing, "find a way to break into…" — even benign security work can false-positive on offensive phrasing | Defensive framing with authorization context: "audit X for vulnerabilities so we can fix them", "review this code for injection risks" |
| Wet-lab biology | `bio` | Research-biology protocols, pathogen/synthesis framing | Fable 5 is not intended for these domains; route the task to a different model rather than rephrasing |

If the task is legitimately security- or bio-adjacent, state the defensive purpose and authorization explicitly in the Purpose section — that context is what separates a clean run from a false-positive refusal.

## Calibration notes for the prompt writer

- **Turns run long.** Single hard-task requests can run many minutes. Don't split a task into micro-prompts to "keep responses fast" — one well-specified prompt with the full spec up front beats progressive revelation, which measurably reduces quality and token efficiency.
- **Full spec up front.** Fable 5's long-horizon strength activates when the complete goal, constraints, and done-definition arrive in the first message. This is why the anatomy front-loads everything.
- **One clear statement per constraint.** Repeating a rule in three places signals distrust and adds nothing; Fable 5 already follows it stated once.
