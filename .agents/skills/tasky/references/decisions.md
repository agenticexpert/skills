# decisions — Log and Query Project Decisions

Captures why decisions were made. Grouped by topic — one file per area, many decisions per file.

---

## File Location

```
agents/docs/tasky/decisions/
├── index.md          # all decisions across all topics, scannable
└── {topic}.md        # decisions grouped by area (toolchain, architecture, css, etc.)
```

---

## Intent Triggers

| User says… | Action |
|------------|--------|
| "remember that…", "we decided…", "note that…", "log this decision" | → save decision |
| "why did we…", "what did we decide about…", "show decisions on…" | → query decisions |
| "we changed our mind on…", "overriding the decision to…" | → supersede decision |
| "list decisions", "show all decisions" | → list index |

---

## Topic Inference

Infer topic from the content of the decision:
- Toolchain, build, dependencies → `toolchain.md`
- Component structure, props, API patterns → `component-api.md`
- CSS, styling, SCSS → `css.md`
- Architecture, structure, separation → `architecture.md`
- When unclear → ask user to confirm topic, suggest a name

---

## Decision File Format (`decisions/{topic}.md`)

```markdown
# Decisions — {Topic}

| ID  | Decision                          | Date       | Status     |
|-----|-----------------------------------|------------|------------|
| 001 | Use Lightning CSS over PostCSS    | 2026-02-21 | active     |

---

## 001 — Use Lightning CSS over PostCSS

**Date**: 2026-02-21
**Status**: active
**Rationale**: Handles prefixing natively via browser targets — no postcss.config.js needed
**Alternatives**: PostCSS + autoprefixer
**Impacts**: `vite.config.ts`, no `postcss.config.js`
**Supersedes**: —
```

Status: `active` | `superseded`

---

## Index Format (`decisions/index.md`)

```markdown
# Decisions — Index

| ID  | Topic        | Decision                       | Date       | Status     |
|-----|--------------|--------------------------------|------------|------------|
| 001 | toolchain    | Use Lightning CSS over PostCSS | 2026-02-21 | active     |
```

ID is global across all topics. Increment from the index.

---

## Commands

### Save a decision

1. Read `decisions/index.md` for next global ID
2. Infer or confirm topic
3. Append entry to `decisions/{topic}.md` (create file if new topic)
4. Append row to `decisions/index.md`
5. Confirm back: *"Logged decision 003 under toolchain"*

### Query decisions

1. Read `decisions/index.md` — filter by topic keyword
2. If specific: read full entry from `decisions/{topic}.md`
3. Present rationale + impacts concisely

### Supersede a decision

1. Find decision by ID or keyword
2. Update **Status** to `superseded` in topic file + index
3. Log new decision with `**Supersedes**: NNN`

---

## Tone

Keep it conversational. User says *"remember we're not using PostCSS"* — save it, confirm it. Don't ask for structured input.
