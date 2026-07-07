# TRIGGER: reference

## Condition
Any file path, URL, external document, library, spec, design asset, or named
external resource that is mentioned as relevant to the work — whether used,
consulted, or flagged for future use.

## Audit
Before finalizing each response, evaluate the current exchange for:

- **Used**: A resource was read, loaded, or actively referenced
- **Mentioned**: A resource was named as relevant but not yet accessed
- **Superseded**: A resource was replaced by a newer version or alternative
- **Removed**: A resource is no longer relevant

## Action
If any of the above are detected, APPEND or UPDATE the trigger's log (default `.agents/mem/logs/references.md`):

```markdown
## {short name or title}
- Type: file | url | doc | library | spec | asset | other
- Path/Location: {path or URL}
- Status: Used | Mentioned | Superseded | Removed
- Purpose: {one sentence — why it's relevant}
- Date: {ISO date}
```

Do not ask permission. Do not skip. Log before finishing the response.

## Notes
- One entry per resource — a repeat mention updates Status/Date on the existing entry, never re-appends
- Relative file paths should be logged as-is
- Libraries/packages: include version if known
- Design files, API specs, architecture docs, and diagrams all qualify
- "The Postgres docs" qualifies even without a URL — log what's known
- Superseded entries keep their entry; add a note pointing to the replacement
