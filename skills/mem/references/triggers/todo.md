# TRIGGER: todo

## Condition
Any durable work item that is created, completed, blocked, or dropped — explicit ("add a TODO", "we still need to...") or implied (a gap acknowledged but deferred).

## Audit
Before finalizing each response, evaluate the current exchange for:

- **Added**: A new work item surfaced ("we should also...", "later we need...")
- **Completed**: A tracked item was finished
- **Blocked**: An item can't proceed; note what blocks it
- **Dropped**: An item was abandoned or became irrelevant

## Action
If any of the above are detected, APPEND or UPDATE the trigger's log (default `.agents/mem/logs/todos.md`):

```markdown
## {short title}
- Status: Added | Completed | Blocked | Dropped
- Summary: {one sentence}
- Blocker: {only when Blocked}
- Date: {ISO date}
```

Do not ask permission. Do not skip. Log before finishing the response.

## Notes
- Deferred fixes ("good enough for now") count as Added
- Completing an item updates its entry — don't duplicate
- Conversation-scoped micro-steps ("run this command next") don't qualify; durable work items do
