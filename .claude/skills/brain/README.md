# brain

Central knowledge index for the project. `BRAIN.md` lives at the git root and is always in context — it's the brain itself, not a config file.

Keeps answers fast and tokens low. No speculative doc searching — follow links from BRAIN.md only.


## Setup

```
/brain init                          # create BRAIN.md skeleton
/brain init auth/sessions            # scaffold a category doc set
```

`init <domain>/<category>` is conversational — brain asks one question at a time to fill in vision, pillars, decisions, and implementation.


## Ask & Look Up

```
/brain ask "how do we handle sessions?"    # lookup in Q&A — no file scanning
/brain map                                 # show all categories
/brain show auth/sessions                  # open that category's docs
```

`ask` is pure lookup. If the answer isn't in BRAIN.md, brain says so — it doesn't go hunting.


## Add Knowledge

```
/brain add fact "we use SQLite, not Redis, for sessions"
/brain add ref "session design" agents/docs/auth/sessions/decisions.md
```


## Freshness

Entries go stale after 90 days.

```
/brain freshen             # list stale entries
/brain confirm Q01         # update confirmed date to today
```


## BRAIN.md format

```markdown
# Brain

> Last freshened: 2026-03-09

## Map

- [auth/sessions](agents/docs/auth/sessions/) — how user sessions are created and stored
- [infra/deploy](agents/docs/infra/deploy/) — deployment pipeline and environments

## Q&A

**Q01 — How do we handle sessions?**
SQLite, 24h TTL. Redis was rejected (infra overhead). *Confirmed: 2026-03-09* → [decisions](agents/docs/auth/sessions/decisions.md)

## Facts

- Sessions use SQLite, not Redis *(2026-03-09)*
- Deploy target is single-server; multi-region not planned *(2026-03-09)*
```


## Category docs — agents/docs/auth/sessions/

```
vision.md          why this category exists
pillars.md         non-negotiables and constraints
decisions.md       what was decided and why
implementation.md  how it actually works
```


## Files

```
BRAIN.md                      # git root — always loaded
agents/docs/{domain}/{cat}/
  vision.md
  pillars.md
  decisions.md
  implementation.md
```