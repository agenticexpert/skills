# freshen — Brain Freshness Management

Entries in BRAIN.md carry a `Confirmed:` date. Freshen surfaces what hasn't been confirmed recently so knowledge doesn't silently go stale.

---

## Staleness Threshold

Default: **90 days**. An entry is stale if its `Confirmed:` date is more than 90 days before today.

Today's date is always available from context. Compare against it directly.

---

## Entry IDs

Q&A entries and Facts carry IDs as part of the Markdown for `brain confirm` to target them. Format:

- Q&A: `Q01`, `Q02`, ...
- Facts: `F01`, `F02`, ...

```markdown
**Q01 — How is CPU timing handled?**
Fixed cycles per scanline. *Confirmed: 2026-03-07* → [detail](...)

- F01 — PPU renders 262 scanlines per frame *(2026-03-07)*
```

---

## Commands

### `brain freshen`

1. Read BRAIN.md
2. Find all entries with a `Confirmed:` or `*(date)*` older than 90 days
3. Display stale entries grouped by type (Q&A / Facts), with their IDs:

```
Stale entries (older than 90 days)

Q&A
  Q03  How does the PPU handle sprites?   Last confirmed: 2025-11-01
  Q07  Why does studio use tile-first?    Last confirmed: 2025-10-14

Facts
  F02  PPU renders 262 scanlines          Last confirmed: 2025-12-01
```

4. Prompt: "Confirm an entry with `/brain confirm <id>`, or review its category with `/brain show <domain>/<category>`."

If nothing is stale: `All entries confirmed within 90 days.`

### `brain confirm <entry-id>`

1. Find the entry by ID in BRAIN.md
2. Ask: "Still accurate? Any updates needed?"
   - If yes, accurate as-is: update `Confirmed:` date to today
   - If needs update: edit the answer/fact inline, then update date
3. Confirm: `Q03 confirmed 2026-03-07.`

### When Other Skills Complete Work

When `tasky done` or similar marks work complete in a relevant domain:
- Note which `agents/docs/{domain}/{category}/` was affected
- Suggest: `brain freshen` or specifically `brain confirm` for related entries
- Do not auto-update — always confirm with the user first
