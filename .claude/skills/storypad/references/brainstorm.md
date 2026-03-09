# Brainstorm

Free-form ideation workflow. Divergent thinking first, structure later.


## Prerequisites

- A storypad must be open (storypad.md loaded in context)
- If no storypad is open, prompt: "No storypad loaded. Use `/storypad open {name}` or `/storypad new {name}` first."


## Input Parsing

Parse: `/storypad brainstorm [topic]`

- **topic** (optional): A focus area or question to brainstorm around
- If no topic, brainstorm freely about the storypad's premise


## Core Principle

**Diverge before you converge.** Generate as many ideas as possible without judgment. Quality comes from quantity — bad ideas often spark good ones. Never edit or delete during brainstorming.


## Brainstorm Modes

Choose the mode based on context, or ask the user which approach they want:

### 1. Open Mode
- No constraints. Free association from the premise.
- Generate 8–12 ideas covering different angles, formats, and approaches.
- Include wild ideas — they stretch the creative space.

### 2. Focused Mode
- Narrow brainstorming around a specific topic or question.
- Go deep on one angle: "What are all the ways we could explain X?"
- Generate 6–10 variations on the focused theme.

### 3. Audience-First Mode
- Start from the audience's perspective.
- What questions would they have? What problems do they face?
- What would make them click? What would make them share?
- Generate ideas framed as audience needs/desires.

### 4. Contrarian Mode
- Challenge assumptions about the topic.
- What's the opposite of the obvious take?
- What would a critic say? What's the controversial angle?
- Generate ideas that subvert expectations.


## Output Rules

**CRITICAL: Brainstorm output is APPEND-ONLY to the Notes section.**

1. Read the current storypad.md
2. Find the `## Notes` section
3. Append a new brainstorm block:

```markdown
### Brainstorm — {mode} — {date}
{if topic}: Focus: {topic}

- Idea 1
- Idea 2
- ...
- Idea N

{any additional thoughts, connections between ideas, or questions raised}
```

4. Write the updated storypad.md
5. Update frontmatter `updated` date

### What NOT to do
- Never modify the Segments table during brainstorming
- Never delete previous brainstorm entries
- Never edit previous Notes content
- Never change the status to "outlining" (that happens in `/storypad outline`)


## After Brainstorming

Display a summary of what was generated:
```
Added {N} ideas to Notes ({mode} mode)
Total brainstorm sessions: {count}
```

Suggest next steps based on the state:
- If this is the first brainstorm: "Keep brainstorming with `/storypad brainstorm` or try a different mode."
- If there are 2+ brainstorm sessions: "Ready to structure? Try `/storypad outline` to create segments from your ideas."
- Always offer: "Or brainstorm more with `/storypad brainstorm [topic]`"


## Multiple Sessions

Brainstorming is cumulative. Each `/storypad brainstorm` call adds a new dated block to Notes. This creates a visible history of how ideas evolved. Never flatten or merge previous sessions.
