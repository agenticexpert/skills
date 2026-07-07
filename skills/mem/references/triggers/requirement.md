# TRIGGER: requirement

## Condition
Any functional or non-functional requirement that is stated, clarified,
changed, or dropped — whether explicitly framed as a requirement or implied
through user intent and constraints.

## Audit
Before finalizing each response, evaluate the current exchange for:

- **Stated**: A new requirement introduced ("It needs to...", "The system should...")
- **Clarified**: An existing requirement was refined or made more specific
- **Changed**: A requirement was altered or its scope shifted
- **Dropped**: A requirement was removed or deprioritized
- **Implied**: User described a behavior or outcome that implies an unstated requirement

## Action
If any of the above are detected, APPEND or UPDATE the trigger's log (default `.agents/mem/logs/requirements.md`):

```markdown
## {short title}
- Status: Stated | Clarified | Changed | Dropped | Implied
- Summary: {one sentence describing the requirement}
- Source: {what triggered it — user quote or behavior described}
- Date: {ISO date}
```

If **Changed** or **Dropped**, note the prior state:
```
- Prior: {what it was before}
```

Do not ask permission. Do not skip. Log before finishing the response.

## Notes
- A re-detected requirement updates its existing entry — append only what's new
- Implied requirements count — if user describes an outcome, the underlying
  requirement should be captured even if never stated as one
- Business rules, constraints, and acceptance criteria all qualify
- Vague wishes ("it should be fast") count as Implied until quantified
- When clarified, update the Status of the prior entry if identifiable
