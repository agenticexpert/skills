# TRIGGER: kv

## Condition
Any named fact, configuration value, setting, constant, or "remember that
X = Y" pattern — whether stated explicitly or established implicitly as a
known fact during the conversation.

## Audit
Before finalizing each response, evaluate the current exchange for:

- **Set**: A value is explicitly established ("The API URL is...", "Use port 3000")
- **Implied**: A fact is treated as established without being formally stated
- **Updated**: A previously set key's value has changed
- **Cleared**: A key is no longer valid or was removed

## Action
If any of the above are detected, APPEND or UPDATE the trigger's log (default `.agents/mem/logs/keys.md`):

```markdown
## {KEY_NAME}
- Value: {value}
- Status: Set | Implied | Updated | Cleared
- Context: {one sentence — where/why this was established}
- Date: {ISO date}
```

If **Updated**, preserve the prior value:
```
- Prior: {old value}
```

Do not ask permission. Do not skip. Log before finishing the response.

## Notes
- Keys should be SCREAMING_SNAKE_CASE by convention
- Env vars, ports, hostnames, credentials (redacted), feature flags, user
  preferences, and project constants all qualify
- Transient values (loop counters, one-off command output) and facts derivable
  from the repo don't qualify
- If unsure of the key name, derive it from context
- At the next summarize, `<cache>` stores only the pointer
  `{KEY_NAME} → keys.md @ {ISO date}` — never the full value; the log is the
  source of truth
- Recall: when a key is referenced later, read .agents/mem/logs/keys.md for the full value