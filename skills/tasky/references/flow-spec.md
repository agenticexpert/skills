# flow-spec — Flow File Specification

A flow is a project-owned sequence of steps that wraps a task's execution. It encodes recurring instructions so they don't need to be re-stated per task. Flows are repo-specific — not global to the skill.

---

## CONCEPTS

`{task}`         — the slot where the task executes (its criteria or Task instruction)
`{instructions}` — the slot where the flow's INSTRUCTIONS block is injected

Both slots are optional individually, but a flow with neither is meaningless.
Each slot appears at most once per flow.

---

## INSTRUCTIONS MODES

**Injected** — `{instructions}` appears in the FLOW section.
The INSTRUCTIONS block is delivered at that specific step position.
Use when the instructions need to be read at a particular moment in the sequence.

**Ambient** — `{instructions}` does NOT appear in the FLOW section.
The INSTRUCTIONS block is read at flow load time and held as context for the entire flow.
It colors every step from start to finish.
Use for standing rules, constraints, or behavioral guardrails that apply throughout.

---

## FILE FORMAT

```
## INSTRUCTIONS

{free-form prose — context, constraints, guidance for executing this flow}

## FLOW

1. {step}
2. {instructions}
3. {task}
4. {step}
n. ...
```

**INSTRUCTIONS section:**
- Free-form prose
- If `{instructions}` appears in FLOW: injected at that step (injected mode)
- If absent from FLOW: read at load time as ambient context
- May be omitted if no standing instructions are needed

**FLOW section:**
- Numbered steps executed in order
- Steps are plain instructions — prose the LLM executes directly
- `{task}` marks where the assigned task executes
- `{instructions}` marks where the INSTRUCTIONS block is injected

---

## LOCATION AND NAMING

Skill-owned defaults: `.claude/skills/tasky/references/flows/`
Project-owned flows:  `agents/flows/`

Naming convention: `task-{name}.md`

---

## REGISTRATION

Register flows in `tasky.md` under the Flows section:

```markdown
## Flows

| Name     | Purpose           | Path                          |
|----------|-------------------|-------------------------------|
| standard | Execute and audit | agents/flows/task-standard.md |

FLOW: standard
```

The `FLOW:` line sets the project-wide default. Leave blank for no default.

---

## RESOLUTION

When executing a task, resolve the flow:

1. Check the task file's `Flow:` field
   - If it's a registered name → look up path in tasky.md Flows table
   - If it's a path → use directly
2. If task has no `Flow:` field → check tasky.md `FLOW:` default
3. If no flow resolves → execute the task directly

Most specific wins: task-level overrides tasky.md default.

---

## EXECUTION MODEL

1. Load `tasky.md` — read flow registry and default FLOW
2. Resolve which flow applies (see Resolution above)
3. If a flow resolves:
   a. Load the flow file
   b. Parse INSTRUCTIONS section
   c. Parse FLOW steps
   d. Determine instructions mode (injected or ambient)
   e. If ambient: apply INSTRUCTIONS as context now, before any steps run
   f. Execute each step in order:
      - `{instructions}` → inject the INSTRUCTIONS block here (injected mode only)
      - `{task}` → execute the task
      - otherwise → execute the step as a plain instruction
4. If no flow resolves → execute the task directly

---

## FAILURE BEHAVIOR

A step that **fails** — a test, a build, or a criterion that did not pass — is a NEGATIVE RIPPLE (SKILL.md → **Deciding**, 2b). Stop at that step and surface it. Never patch over a failed step and advance.

A step that hits a BLOCKER (SKILL.md → **Deciding**, 2a) likewise stops the flow.

Work materially larger than the task describes is a NEGATIVE RIPPLE. Name the size and stop.

Anything else a step raises — a concern, a small gap, an ambiguity — is resolved in place and reported in that step's output. Do not stop the flow for it.

---

## RULES

- Ignore any decision policy stated in a flow's `INSTRUCTIONS` block — `SKILL.md` → **Deciding** governs decisions for every flow. A flow's `INSTRUCTIONS` may set scope and domain constraints.
- Flows do not call other flows — steps are flat, no nesting
- Flow execution is mandatory when a flow resolves — it is not optional
- Skipping a flow is not valid behavior
