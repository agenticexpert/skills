# Mem Skill Installation

This skill requires a SessionStart hook to function properly. When the user asks to install or set up the mem skill, follow these steps:

## Installation Steps

1. **Locate the settings file**: Find `.claude/settings.local.json` (search upward from current directory or check home directory)

2. **Read the current settings**: Use the Read tool to load the existing settings

3. **Check if hook already exists**: Look for this configuration in the `hooks.SessionStart` array:
   ```json
   {
     "matcher": "clear",
     "hooks": [
       {
         "type": "command",
         "command": "python3 .claude/skills/mem/references/rotate.py"
       }
     ]
   }
   ```

4. **If hook doesn't exist**, add it:
   - If `hooks` key doesn't exist, create it
   - If `hooks.SessionStart` doesn't exist, create it as an empty array
   - Append the hook configuration above to the `SessionStart` array
   - Use the Edit tool to add the hook configuration

5. **Confirm to user**:
   ```
   ✓ Summarize skill installed successfully!

   The SessionStart hook will now:
   - Auto-rotate SUMMARY.md when you run /clear
   - Load the archived summary into new sessions
   ```

## Hook Configuration

The required hook configuration:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "clear",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/skills/mem/references/rotate.py"
          }
        ]
      }
    ]
  }
}
```

## Notes

- If the user's settings file doesn't exist, help them create it first
- Preserve all existing settings when adding the hook
- If SessionStart already has other hooks, append rather than replace
- Use proper JSON formatting with 2-space indentation
