# Log Views Playbook

Folded views over the trigger logs at `.agents/mem/logs/`. Logs are append-oriented history; a view folds that history into current state.

| Command | Log (trigger) | Fold rule |
|---|---|---|
| `/mem decisions` | decisions.md (decision) | Latest status per title; superseded entries collapse into their replacement |
| `/mem requirements` | requirements.md (requirement) | Current set: Stated and Implied, with Clarified/Changed applied; omit Dropped unless asked |
| `/mem todos` | todos.md (todo) | Open first (Added, then Blocked with blocker named), then Completed; omit Dropped unless asked |
| `/mem keys` | keys.md (kv) | Latest value per key; omit Cleared unless asked; show Prior only on request |
| `/mem refs` | references.md (reference) | Active resources grouped by type; omit Superseded/Removed unless asked |

Steps:

1. Read the log. Missing → say no log yet and name the trigger that feeds it (`/mem trigger {name}`).
2. Fold per the rule. Present compact — a table or short list, not the raw log.
3. Point at the raw file for full history.
