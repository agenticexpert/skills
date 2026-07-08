# Trigger Protocol


## What is a TRIGGER

A TRIGGER is a persistent, named behavioral directive. Once active, it runs a
semantic audit before every response for the remainder of the context. Triggers
survive checkpoints and compaction via the summary's `<triggers>` section and
the live-trigger state file `.agents/mem/triggers.md` — see Survival.


## Activation

```
/mem trigger {name}
/mem trigger {name} to {log-path}     # override default log path
/mem trigger {name} using {path}      # keep the condition, replace the action — see Override Slot
```

- Loads macro from `references/triggers/{name}.md`
- Registers trigger in active list
- Rewrites the live-trigger block at `.agents/mem/triggers.md` — see Survival
- Confirms activation by quoting the rewritten block — the quote is proof the state file was written; survival depends on it

Default log root: `.agents/mem/logs/` — each macro names its file there.


## Deactivation

```
/mem trigger off {name}
/mem trigger off all
```

- Removes from active list
- Rewrites `.agents/mem/triggers.md`; `off all` deletes it
- Does not delete the log


## Pre-Response Hook

When any triggers are active, before finalizing every response:

1. For each active trigger, perform its **Semantic Audit**
2. If the trigger condition is met — execute its action **before** finishing the response
3. Do not ask permission. Execution is mandatory.
4. Multiple triggers run independently (stack)


## Survival

The live-trigger block is state, not just summary content. It lives at
`.agents/mem/triggers.md`, kept current by activation and deactivation.
Summarize copies it in as the `<triggers>` section; the compact hook
(references/install.md) prints it back into context after every compaction.
Hooks not installed → the summary block still covers /clear and handoff;
`/mem install` covers compaction.

The block carries its own protocol, so it works in a session that has never
loaded this skill. Whenever a `<triggers>` block appears in context — mem
summary, hook injection, pasted checkpoint — every trigger listed is active
at its logged path. Format (state file and summary section, identical):

```
<triggers>
Live triggers — before finalizing every response, run each trigger's audit
(mem skill, references/triggers/{name}.md); on a match, execute its action
against the listed log. `(using {path})` replaces the action with that file.
  - decision → .agents/mem/logs/decisions.md
  - todo → .agents/mem/logs/todos.md (using .agents/mem/todo-action.md)
</triggers>
```

A `using` action override rides along as `(using {path})` — restore reactivates
the trigger with that action, not the default.

This is the format's only definition — the summary's section
(default-sections.md#triggers) composes `<triggers>` by copying the state file,
not by restating the format.


## Macro Structure

Each macro at `references/triggers/{name}.md` defines:

```markdown
# TRIGGER: {NAME}

## Condition
{Semantic description of what to detect — written for LLM reasoning, not regex}

## Audit
Before finalizing your response, evaluate the current exchange:
{What to look for, what signals matter, what counts as a match}

## Action
If condition is met:
{Exactly what to write, where, in what format}
{The macro owns the format — JSONL, Markdown, etc.}

## Notes
{Edge cases, conflict detection, update vs append rules}
```


## Override Slot

```
/mem trigger {name} using {path}
```

Loads the named trigger's **When** (condition/audit) but replaces the **How**
(action/format) with the file at `{path}`. The override is recorded in the
summary's `<triggers>` entry so it survives restore.


## Listing Active Triggers

```
/mem trigger list
```

Shows all currently active triggers and their log targets. Read
`.agents/mem/triggers.md` and reconcile — the in-context active set is the
truth for this session; a mismatched state file is rewritten to match.
