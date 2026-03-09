# parked — Parking Lot for Future Ideas

Fast capture for ideas that will likely become roadmaps. No commitment, no structure required at capture time. Triage separately.

---

## File Location

```
agents/docs/thinky/parked.md    # The parking lot
```

---

## Format

```markdown
# Parked Ideas

| ID  | Idea                                      | Captured    | Status   |
|-----|-------------------------------------------|-------------|----------|
| P01 | Refactor NES out of studio for SNES       | 2026-03-07  | parked   |
| P02 | Add multiplayer support                   | 2026-03-07  | promoted |
```

Status: `parked` | `promoted` | `discarded`

When promoted, add a note in the row: `→ roadmap-name`

```markdown
| P02 | Add multiplayer support | 2026-03-07 | promoted → multiplayer-v1 |
```

---

## Commands

### `thinky park "<idea>"`

Fast capture — minimum friction:

1. Read `agents/docs/thinky/parked.md` (create if missing)
2. Assign next ID (P01, P02, ...)
3. Append row with today's date and status `parked`
4. Confirm with one line: `Parked as P01.`

No follow-up questions. No elaboration. Just capture and move on.

### `thinky triage`

Review parked items one at a time:

1. Read `parked.md`
2. Show only items with status `parked`, oldest first
3. For each, display the idea and ask:
   - `[r]` promote to roadmap — ask for roadmap name, update status to `promoted → {name}`, create roadmap via tasky
   - `[g]` add to goals — add to `goals.md` as uncovered goal, update status to `promoted → goals`
   - `[d]` discard — update status to `discarded`
   - `[s]` skip — leave as parked, come back later
4. Continue until all parked items are handled or user skips
5. Show summary: N promoted, N discarded, N remaining