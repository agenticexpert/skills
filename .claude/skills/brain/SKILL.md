# brain — Project Knowledge Hub

Central knowledge index for the project. Serves two purposes: helps skills navigate quickly, and lets humans ask questions or seed new work from established knowledge.

`BRAIN.md` lives at the project root and is always loaded. It is the brain — not a config file, but a living document that brain reads and maintains.

## Usage

**Setup**
```
/brain init <domain>/<category>
```

**Knowledge**
```
/brain show <domain>/<category>
/brain ask "<question>"
/brain map
/brain add fact "<text>"
/brain add q "<question>" "<answer>" [<link>]
```

**Freshness**
```
/brain freshen
/brain confirm <entry-id>
```

- Keep BRAIN.md short — it is always in context
- Never search speculatively across agents/docs/ — follow links from BRAIN.md only
- Token efficiency is a first-class concern

## Project Configuration: BRAIN.md

`BRAIN.md` at the git root is the brain. It contains:
- **Map** — category index with one-line descriptions
- **Q&A** — questions with answers and confirmation dates
- **Facts** — atomic knowledge bites with confirmation dates

Every entry carries a `Confirmed:` date. Entries are considered stale after 90 days by default.

### BRAIN.md Format

```markdown
# Brain

> Last freshened: YYYY-MM-DD

## Map

- [domain/category](agents/docs/domain/category/) — one-line description
- [domain/category](agents/docs/domain/category/) — one-line description

## Q&A

**Q01 — {Question}**
{Answer}. *Confirmed: YYYY-MM-DD* → [source](path/to/doc.md)

## Facts

- {Fact} *(YYYY-MM-DD)*
```

### `brain init`

Creates `BRAIN.md` at the git root if it does not exist:
1. Write the BRAIN.md skeleton with empty Map, Q&A, Facts sections
2. Set `Last freshened` to today
3. Confirm and proceed to first `brain init <domain>/<category>` if the user wants

## Startup

**Before executing any brain command**, check whether `BRAIN.md` exists at the project root:
- If it exists: read it — this is the active brain for this session
- If it does not exist: suggest `/brain init` — do not proceed without it

## How It Works

Detects intent and routes to the appropriate reference:
- `init`, `show`, `map`, `add`, `ask` → `references/knowledge.md`
- `freshen`, `confirm` → `references/freshen.md`

## Commands

### Setup

| Command | Description |
|---------|-------------|
| `init` | Create `BRAIN.md` skeleton at project root |
| `init <domain>/<category>` | Scaffold a category under `agents/docs/` — collaborative fill |

### Knowledge

| Command | Description |
|---------|-------------|
| `show <domain>/<category>` | Display that category's docs (vision, pillars, decisions, implementation) |
| `ask "<question>"` | Lookup in BRAIN.md Q&A — no doc searching |
| `map` | Display the Map section of BRAIN.md |
| `add fact "<text>"` | Append a fact to BRAIN.md with today's date |
| `add q "<question>" "<answer>" [<link>]` | Append a Q&A entry with today's date |

### Freshness

| Command | Description |
|---------|-------------|
| `freshen` | Show all entries with `Confirmed:` older than 90 days |
| `confirm <entry-id>` | Update the confirmed date on an entry to today |

## Files

```
BRAIN.md                            # The brain (git root) — always loaded

.claude/skills/brain/
├── SKILL.md                        # This file
└── references/
    ├── knowledge.md                # Knowledge commands and formats
    └── freshen.md                  # Freshness commands and formats

agents/docs/{domain}/{category}/
├── vision.md                       # Why this category exists
├── pillars.md                      # Non-negotiable constraints
├── decisions.md                    # What was decided and why
└── implementation.md               # How it actually works
```

## Intent Detection

1. Parse command prefix or natural language intent:
   - `init`, `show`, `map`, `add`, `ask` → load `references/knowledge.md`
   - `freshen`, `confirm` → load `references/freshen.md`
   - Natural language like "what do we know about X", "how does X work" → treat as `ask`
   - Natural language like "show me the map", "what categories exist" → treat as `map`
   - Natural language like "anything stale", "what needs updating" → treat as `freshen`
2. Execute with the reference as context
