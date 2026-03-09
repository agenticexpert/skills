# tracky

Lightweight tracker for what you know about your project — decisions, specs, notes, issues. Entries stay current and can be updated or superseded as things evolve.


## Setup

```
/tracky init
```

Creates `TRACKY.md` at the project root. Acts as both config and the registry of all tracked entries.


## Capture

```
/tracky note "we dropped redis, using sqlite for sessions"   # instant capture, no questions
/tracky add "auth session design"                            # interactive, prompts for type and content
```

`note` is zero-friction — fires and confirms in one line. Use it mid-thought. Triage later.


## Browse

```
/tracky list                  # all entries
/tracky list decision         # filter by type
/tracky show auth-sessions    # full entry
/tracky search redis          # registry first, then file contents
```


## Manage

```
/tracky update auth-sessions     # edit content, status, or type
/tracky supersede auth-sessions  # mark replaced, optionally link replacement
/tracky triage                   # review all deferred notes — act, promote, or discard
```


## Entry Types

```
decision   a choice made, an option rejected, or a question still open
spec       how something works, is designed, or is constrained
note       background, context, nuance
issue      bug or problem noticed but not yet acted on
```


## Entry Statuses

```
current      active and accurate
draft        being worked out, not yet settled
deferred     captured, not yet acted on — shows up in triage
superseded   replaced by another entry
```


## Triage

Deferred notes from `/tracky note` collect here.

```
/tracky triage
```

For each deferred entry, choose:
- `a` — promote to active (set type + status)
- `p` — promote to tasky task
- `d` — discard
- `s` — skip for now


## Entry file — agents/docs/tracky/auth-session-design.md

```markdown
# Auth Session Design

TYPE: decision
STATUS: current
ADDED: 2026-03-09
UPDATED: 2026-03-09
RELATED: auth/03

## Content

Using SQLite for session storage. Redis was considered but adds infra complexity
we don't need at current scale.

## Why

Single-server deployment, sessions fit in memory. Revisit if we go multi-region.
```


## Files

```
TRACKY.md                    # git root — config + registry
agents/docs/tracky/
  auth-session-design.md
  redis-rejected.md
  login-rate-limiting.md
```

Registry lives in `TRACKY.md` — `/tracky list` never opens individual files.