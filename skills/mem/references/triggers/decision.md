# TRIGGER: decision

## Condition
Any technical choice, architectural path, stance, or suggestion that was made,
considered, or bypassed — including implicit ones where no explicit decision
language was used.

## Audit
Before finalizing each response, evaluate the current exchange for:

- **Made**: A path was agreed upon or committed to ("Let's use X", "We'll go with Y")
- **Identified**: A new option surfaced but not yet decided ("We could use X...")
- **Ignored**: A suggestion was raised but bypassed without being addressed
- **Changed**: A previous decision was reversed or superseded
- **Rejected**: An option was explicitly ruled out with reasoning

## Action
If any of the above are detected, APPEND or UPDATE the trigger's log (default `.agents/mem/logs/decisions.md`):

```markdown
## {short title}
- Status: Made | Identified | Ignored | Changed | Rejected
- Summary: {one sentence}
- Reasoning: {why — include subtext if implicit}
- Date: {ISO date}
```

A **Changed** or **Made** entry that supersedes or resolves a prior entry notes it:
```
- Supersedes: {prior decision title}
```

Do not ask permission. Do not skip. Log before finishing the response.

## Notes
- Before appending, scan the log for the same decision — a re-detection updates the existing entry, never duplicates it
- Catch subtext: "Maybe later" = Ignored. "Actually..." = Changed.
- If a decision contradicts a prior log entry, flag it in the log entry
- Minor stylistic choices (indentation, naming tweaks) do not qualify
- Architectural, library, pattern, and workflow choices do qualify