# Default Section Definitions

Every built-in section definition in one file, so composing the default format costs one read. `default-summary.md` selects from here via `from default-sections.md#{name}` anchors — each `## <name>` heading opens one definition, which runs to the next `##` heading. Anchor syntax and slot language: `summarize.md`.

## `<analysis>`

A high-level paraphrase of the conversation. Summarize what was discussed, accomplished,
key terms, and overview to preserve continuity when resumed. Be concise, because
most details will be captured in the other sections.

## `<evolution>`

CRITICAL: Sequential narrative of how conversation evolved. Each entry is 1-3 sentences telling the story.

Format:
```text
[SESSION 1]
1. Started by loading emma reference files (ag-ui-specs, new-app-tool, bindings map, styles) to restore context
   from prior sessions and understand the existing AG-UI tool architecture.
2. User asked to list existing disk drive AG-UI tools — after reviewing, clarified they only wanted disk-tools.js
   frontend tools plus the MCP load/save tools, not the entire disk management system.
3. User requested SmartPort tools mirroring the floppy disk pattern. Created plan covering frontend AG-UI tools
   and MCP integration, user approved approach.

[SESSION 2]
4. Implemented smartport-tools.js with 4 core operations and created load-smartport-image.js MCP tool for
   .hdv/.po/.2mg formats, keeping it separate from floppy disk infrastructure per user confirmation.
```

Rules:
- Narrative style, 1-3 sentences per entry
- Include context and reasoning
- Sequential but can capture more events than timeline
- APPEND only
- Where ambiguity exists (e.g. two databases discussed and a reference could mean either), note the candidates — don't assume

## `<timeline>`

CRITICAL: Factual ledger of IMPORTANT events only. Brief entries, key milestones.

Format:
```text
[SESSION 1]
- T1: Created SmartPort AG-UI tools (4 tools)
- T2: Created load-smartport-image.js MCP tool
- T3: Added slot management (list/install)

[SESSION 2]
- T4: Created general slot-tools.js
- T5: Fixed slot config window refresh bug
```

Rules:
- APPEND only, never replace
- T{n} continues from the previous summary's highest T
- Show updates: "T2: PostgreSQL" → "T8: Switched to SQLite"
- Brief factual entries (what happened)
- Only important milestones
- Doesn't require 1:1 with evolution (filtered view)
- Preserve causality (T4 led to T5, T5 led to T6)
- Mark session boundaries
- Strict chronological order
- Cross-reference details (e.g., "T6: See `<troubleshooting>` for rationale")

## `<cache>`

Content preserved against the discard inputs.

Rules:
- When {discard_web_cache} = false, preserve web fetch/search content here
- When {discard_context7_cache} = false, preserve context7 content here
- When {discard_referenced_file_cache} = false, preserve file contents here. When true, preserve only the exceptions (CLAUDE.md and its references, files loaded in the recent conversation) — list them by path
- Key/value facts stay in the kv log — store pointers only: {KEY_NAME} → keys.md @ {ISO date}

## `<mcp-tools>`

MCP servers and custom tools used or configured. Preserve working parameters — a resumed session should not rediscover them.

Format:
```text
MCP SERVER: github-mcp
TOOLS: create_issue, search_issues, create_pr
CONFIG: Uses GITHUB_TOKEN env var
USAGE: create_issue(repo="user/repo", title="...", body="...")
```

Rules:
- Persists across summaries — carry forward, prune only tools that left the project
- Include tool limitations discovered
- Include successful tool combinations and parameters that work well

## `<requirements>`

The current requirement set — functional and non-functional, original and evolved.

Rules:
- Show evolution chronologically: Stated → Clarified → Changed → Dropped
- Implied requirements count — if the user described an outcome, capture the underlying requirement
- Include constraints (technical, business, design) and performance targets
- Edge cases identified count as constraints — capture them here
- If the requirement trigger is active, fold from .agents/mem/logs/requirements.md instead of re-deriving

## `<references>`

Every external resource the conversation leaned on.

Format:
```text
<files>
- path/to/file.md — why it matters
</files>
<web>
- https://... — what it answered
</web>
```

Rules:
- Full paths; track chronological changes ("auth.js: [SESSION 1] created → [SESSION 2] refactored")
- Web entries only when worth re-fetching; context7 lookups live under `<web>`
- If the reference trigger is active, fold from .agents/mem/logs/references.md instead of re-deriving

## `<troubleshooting>`

Problems encountered and their outcomes, in order encountered.

Rules:
- Each entry: symptom, cause, fix
- Error messages exact
- Keep workarounds and the debt they leave behind
- Keep failed attempts and debugging insights — they save the next session from repeating them
- Preserve causality (fix A unblocked problem B)

## `<todos>`

Pending and in-progress work.

Rules:
- Order added, session-marked; open items from previous summaries stay until closed
- Show closure, don't erase: "fix auth bug → done [SESSION 3]"
- Include in-flight work — started, not finished
- Include deferred decisions and when they were deferred
- End with the immediate next actions
- If the todo trigger is active, fold from .agents/mem/logs/todos.md instead of re-deriving

## `<current-step>`

The resume point. When work was interrupted, preserve enough detail to resume exactly where it left off.

Format:
```text
INTERRUPTED: Implementing user authentication
STEP: 3 of 5 - Was adding JWT token validation to /api/auth/verify
NEXT: Run 'npm test auth.test.js' then fix the refresh token logic in auth.service.js line 47
CONTEXT: User wanted 15-minute access tokens, 7-day refresh tokens, using RS256
```

Rules:
- Rewritten every summary — describes now, not history
- Nothing interrupted → omit the section; the current state lives in `<current-conversation>`
- What was happening: exact task/operation in progress
- Exact next action: the precise next step to take
- Partial changes: files modified but not completed
- Error context: if debugging, the exact error message and what was tried
- User's last request: exact wording

## `<current-conversation>`

The live thread — what the conversation was doing right before this summary.

Rules:
- Rewritten every summary — the live thread now, not an archive of past threads
- Current focus: what was being worked on most recently
- Last commands/operations performed, in order
- Active debugging or investigation
- User preferences expressed (style, workflow)
- Conversation momentum: what direction things were heading

## `<relevance>`

Examples and planning details that remain relevant to the work ahead.

Rules:
- `<examples>`: worked examples and snippets — carried over and current, verbatim, code never paraphrased
- `<planning>`: active plans and planning details — carried over, current, and any updates to the carried ones

## `<triggers>`

Active triggers, preserved so they survive summary and compaction. Reactivated whenever the block re-enters context.

Copy `.agents/mem/triggers.md` verbatim as the whole section — the state file already is this block, tags and protocol lines included; don't wrap it again. The format has one owner: the mem skill's references/trigger.md → Survival.

No state file but triggers active in context → rebuild it in that format, write it back to `.agents/mem/triggers.md`, then copy it in. No active triggers → omit the section.

## `<meta>`

Machine-readable footer about the summary itself.

Format:
```text
Summary: #3
Sessions: 1-4
Omitted: mcp-tools, relevance
Pruned: none
Unresolved decisions: 2
1. Database choice for caching layer
2. Embedding update strategy
```

Rules:
- Count unresolved decisions and list brief titles — feeds /mem decide
- Track the summary iteration count and how the focus evolved across iterations
- Note recurring issues that appear across multiple summaries
