# Continue Playbook

Load a checkpoint into the current context so the work resumes mid-thought instead of being rebuilt. Purely additive — never clears.

| Pattern | Effect |
|---|---|
| `/mem continue` | Load `.agents/mem/summary/SUMMARY.md`, display |
| `/mem continue decide` | Load, then run references/decide.md |
| `/mem continue from {path}` | Load custom file, display; file left untouched |

Arguments combine — `continue decide from {path}` loads the file, then runs decide.

Steps:

1. Read the file. Missing → say so; for the default path, list candidates from `.agents/mem/summary/archive/`.
2. Restore `<triggers>`: reactivate every trigger listed, at its logged path, with any `(using {path})` action override. Rewrite the state file `.agents/mem/triggers.md` to match the restored set — heals a missing or stale one.
3. Honor `<current-step>`: an interrupted task recorded there is surfaced — ask whether to resume it.
4. Display a digest, not the whole summary: current focus, interrupted step, open todos and decisions, active triggers — then point at the file for the rest. The full checkpoint is already in context. Decide mode displays only unresolved decisions.

Resume posture — once the checkpoint is in context:

- Its analysis and decisions are established. Don't re-derive or re-open them; only later conversation supersedes them.
- Volatile state (file contents, branch, running processes) is as-of the checkpoint's write — verify a volatile fact before acting on it; trust the rest.
- Once oriented, act. Restoring context is not the deliverable; the interrupted work is.

Rotation is not continue's job — the SessionStart hook archives SUMMARY.md on `/clear` (references/install.md).
