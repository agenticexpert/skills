# Agent Spawning for Parallel Processing in Mem Skill

> Captured: 2026-02-11
> Source: Discussion about using Task tool to spawn sub-agents with context for summary generation

## Genesis

The idea emerged from exploring how the mem skill could leverage Claude's Task tool to spawn sub-agents for processing different sections of the summary in parallel or delegating heavy analysis tasks. Initial trigger was the question: "is possible to spin up another claude agent in its context to do something, how can I do that from this skill?"

Initial framing: Could sub-agents with access to the current conversation context be used to extract specific information (decisions, patterns, etc.) and return structured results?

## Evolution

### Phase 1: Understanding Task Tool Capabilities

- **Discovery**: The Task tool can launch specialized agents (subprocesses) for complex, multi-step tasks
- **Key insight**: Certain agent types (`general-purpose`, `Explore`) have "access to current context" - they can see the full conversation history
- **Initial application**: Could be used within the mem skill to delegate analysis work

Available subagent types:
- `general-purpose`: Complex analysis, research, multi-step tasks (has context)
- `Explore`: Search codebase, find files, answer questions about code (has context)
- `Bash`: Git operations, command execution (no context)
- `Plan`: Software architect agent (no context mentioned)

### Phase 2: Context-Aware Delegation Pattern

**Q&A:**
- Q: "is possible to spin one up with a copy of the current context so it can perform operations and return a result?"
- A: Yes - agents with "access to current context" see full conversation history, can perform operations, return results

**Pattern discovered:**
```markdown
Use Task tool:
- subagent_type: "general-purpose" or "Explore"
- prompt: "Analyze the current conversation and extract [specific thing]. Return as structured list."
- description: Brief task description

Sub-agent inherits context → processes → returns results → main agent integrates
```

### Phase 3: Application to Mem Skill

**Decision**: Sub-agents could be used within SLOT augments to enhance specific summary sections

**Use cases identified:**
1. **Extract decisions**: Spawn agent to analyze conversation for all technical decisions
2. **Identify patterns**: Spawn agent to find code patterns and conventions discussed
3. **Track files**: Spawn agent to list all files mentioned with changes
4. **Parallel processing**: Spawn multiple agents simultaneously for different sections

**Example for <decisions> SLOT:**
```markdown
When processing <decisions> section:
  Spawn general-purpose agent with prompt:
  "Analyze current conversation and extract all technical decisions.
   For each: what was decided, why, alternatives considered.
   Return as structured list."

  Agent returns structured decision list
  Main agent formats and integrates into <decisions> section
```

### Phase 4: Integration with Slot System

**Realization**: Could define slot augments that spawn agents

**Pattern:**
- SLOT augment instructions include Task tool invocation
- Augment "before" or "after" can delegate work to sub-agent
- Sub-agent processes full conversation context
- Returns focused results for specific slot
- Main agent weaves results into summary

**Example augment:**
```markdown
File: extensions/decision-extractor.md

When processing <decisions> slot:

Before default instructions:
  1. Spawn sub-agent to extract decisions
  2. Use returned structured data as input for decision section
  3. Continue with default formatting
```

## Current State

**Decided approach:**
- Task tool with `general-purpose` or `Explore` subagent_type for context-aware processing
- Sub-agents inherit full conversation history
- Can be invoked from within slot augment instructions
- Results returned to main agent for integration

**Implementation possibilities:**
1. Create extension files that use Task tool for specific extractions
2. Allow parallel spawning of multiple agents for different sections
3. Use for heavy analysis (pattern detection, decision extraction, requirement gathering)

**Open questions:**
- Performance impact of spawning multiple agents?
- How to handle agent errors/failures gracefully?
- Should agents be spawned by default or opt-in via augments?
- Best practices for structuring agent prompts for consistent output?

**Next steps:**
1. Create example extension file demonstrating agent spawning
2. Test parallel agent spawning for multiple sections
3. Document agent prompt patterns for common extractions
4. Consider creating helper/wrapper for agent spawning in mem skill

## Artifacts

### Task Tool Invocation Pattern

```markdown
Task(
  subagent_type="general-purpose",
  prompt="Analyze the current conversation and extract all technical decisions made.
         For each decision, provide:
         - What was decided
         - Why it was chosen
         - What alternatives were considered
         Return as structured markdown list.",
  description="Extract decisions"
)
```

### Extension File Example: Decision Extractor

```markdown
# Extension: Decision Extraction via Sub-Agent

When processing <decisions> section:

## Before Default

Use Task tool to spawn decision extraction agent:

Task(
  subagent_type="general-purpose",
  prompt="Analyze the current conversation chronologically and extract all technical decisions.

  For each decision found:
  1. Identify when it was made (session/timestamp if available)
  2. What was decided
  3. Why this choice was made (reasoning, constraints, goals)
  4. What alternatives were considered and why they were rejected
  5. Any follow-up or impacts from this decision

  Return as structured markdown with this format:

  ## Decision: [Brief title]
  **When**: [Session/time]
  **Chosen**: [What was decided]
  **Reasoning**: [Why]
  **Alternatives Considered**:
  - [Option 1]: [Why rejected]
  - [Option 2]: [Why rejected]
  **Impact**: [Any follow-up or consequences]

  Maintain chronological order.",
  description="Extract decisions chronologically"
)

Store returned structured data in variable `extracted_decisions`

## Default Instructions

Use `extracted_decisions` as base content for <decisions> section.
Apply any additional formatting specified in default slot instructions.
```

### Parallel Processing Example

```markdown
# Multiple Agents for Different Sections

Spawn agents in parallel:

Agent 1: Extract decisions
Task(
  subagent_type="general-purpose",
  prompt="Extract all technical decisions...",
  description="Extract decisions"
)

Agent 2: Identify patterns
Task(
  subagent_type="general-purpose",
  prompt="Identify code patterns, conventions, and architectural decisions...",
  description="Identify patterns"
)

Agent 3: Track file changes
Task(
  subagent_type="general-purpose",
  prompt="List all files mentioned with what changes were made, chronologically...",
  description="Track files"
)

Agent 4: Extract requirements
Task(
  subagent_type="general-purpose",
  prompt="Extract all requirements and specifications discussed...",
  description="Extract requirements"
)

Each agent processes independently with full context.
Main agent waits for all results, then assembles final summary.
```

## Related Atomic Ideas

- **Agent error handling**: Brief mention of needing to handle agent failures gracefully. Connection: Important for robust implementation but not critical for initial exploration.

- **Agent prompt templates**: Could create library of proven agent prompts for common extractions (decisions, patterns, requirements, etc.). Connection: Standardizes agent usage and improves result consistency.

- **Cost/performance monitoring**: Using multiple agents increases token usage and latency. Connection: Need to balance thoroughness with performance and cost.
