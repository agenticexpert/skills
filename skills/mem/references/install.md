# Install Playbook

Mem's lifecycle hooks: load the checkpoint at every session boundary, archive everything, lose nothing. One script handles every event: `references/lifecycle.py {clear|compact|startup|sessionend}`.

| Event | Hook | What happens |
|---|---|---|
| `/clear` | SessionStart, matcher `clear` | SUMMARY.md printed into the fresh context, then moved to `archive/` (consumed); a leftover `EXPORT.txt` is archived alongside |
| compaction | SessionStart, matcher `compact` | The live-trigger block `.agents/mem/triggers.md` re-injected — active triggers survive the compact |
| fresh launch | SessionStart, matcher `startup` | SUMMARY.md printed into context, read-only — the file stays put |
| any session end | SessionEnd | Raw transcript copied to `.agents/mem/transcripts/{timestamp}.jsonl` — same `%Y%m%d_%H%M%S` stamp as the summary rotation, so the two pair by nearest timestamp; replaces manual `/export` |

Steps:

1. Read `.claude/settings.local.json` — search upward from the current directory; create the file if missing.
2. Merge the hooks below in — preserve all existing settings and hooks. Adjust command paths to where this skill actually lives (e.g. `~/.claude/skills/mem/references/lifecycle.py` for a user-level install). `$CLAUDE_PROJECT_DIR` resolves to the repo root no matter which subdirectory the session launched from — keep it in project-level installs; the script reads the same variable to locate `.agents/mem`. An old `rotate.py` entry is superseded — replace it.
3. Re-read the merged file: every pre-existing hook and setting still present, the four mem entries added. A merge that dropped anything is a failed install — fix before confirming.
4. Confirm: "mem lifecycle installed — checkpoint loads on /clear and startup, triggers survive compaction, transcripts auto-archive."

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "clear",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/skills/mem/references/lifecycle.py\" clear" }
        ]
      },
      {
        "matcher": "compact",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/skills/mem/references/lifecycle.py\" compact" }
        ]
      },
      {
        "matcher": "startup",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/skills/mem/references/lifecycle.py\" startup" }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/skills/mem/references/lifecycle.py\" sessionend" }
        ]
      }
    ]
  }
}
```

Notes:

- Every hook fails open — an error never blocks a session.
- The transcript is the complete raw record; `/export` is a rendering of the same data. Summarize a dead session anytime: `/mem summarize from .agents/mem/transcripts/{timestamp}.jsonl` (match the timestamp to the summary you're pairing it with).
- SessionStart stdout enters the new session's context — that is the whole loading mechanism.
