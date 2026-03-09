# Mem Skill Structure

## Key Files & Cache

**Files:**
- `enhanced.md` - Default summary format template
- `SUMMARY.md` - Output checkpoint (default: `/.claude/summary/SUMMARY.md`)
- `extra-{name}.md` - Optional project-specific references to embed
- `.prune_log` - Topics to exclude from summaries

**Cache Control (inputs):**
- `discard_web_cache` - Exclude web fetch/search results
- `discard_context7_cache` - Exclude context7 queries
- `discard_referenced_file_cache` - Exclude old file contents (except recent + CLAUDE.md)

## Summary Structure & Purpose

**Section 0: Previous Summary Carryover**
- Reason: Merge old summaries, maintain chronological continuity

**Section 1: Timeline**
- Reason: Temporal sequence of events/decisions

**Section 2: File Paths**
- Reason: Track which files exist/were modified

**Section 3: Topics & Features**
- Reason: What was discussed/built

**Section 4: Requirements**
- Reason: Specifications and constraints

**Section 5: Problems Solved**
- Reason: Historical context of fixes

**Section 6: Pending Work**
- Reason: TODOs and in-progress items

**Section 7: Recent Context Flow**
- Reason: Immediate conversation thread

**Section 8: Interrupted Work** (CRITICAL)
- Reason: Resume exact point if session ends mid-task

**Section 9: Code Patterns**
- Reason: Established conventions

**Section 10: External Dependencies**
- Reason: APIs, libraries, services

**Section 11: MCP Tools**
- Reason: Custom tool configurations

**Section 12: Decisions Made**
- Reason: Resolved choices (chronological)

**Section 13: Unresolved Decisions**
- Reason: Open questions needing answers

**Section 14: Communication Context**
- Reason: User preferences, style, working relationship

**Section 15: Project State**
- Reason: Current status snapshot

**Section 16: Compaction History**
- Reason: Track summary iterations

**Metadata: Unresolved Decisions**
- Reason: Machine-readable list for `decide` command
