# tracky — Entry Management

## Data Location

Read from `TRACKY.md` `Data directory` field. Default: `agents/tracky/`.

---

## Fast Capture

`/tracky note "<text>"`

Zero friction — drop a thought and keep moving:

1. Generate a slug from the text
2. Write `{data_dir}/{slug}.md` with TYPE: `note`, STATUS: `deferred`, content = the text, today's date
3. Add a row to the `## Registry` table in `TRACKY.md`:
   ```
   | {slug}.md | {text} | note | deferred | {text} |
   ```
4. Confirm with one line: `Noted as {slug}.`

No follow-up questions. No elaboration. Just capture and move on.

---

## Adding an Entry

`/tracky add "<title>"`

1. Ask the user (if not already clear from context):
   - Type: `decision`, `spec`, `note`, or `issue`?
   - Content: what is known, decided, or specified? (free-form markdown)
   - Why: rationale, constraints, or context? (optional — prompt once, skip if declined)
   - Purpose: one-line summary for the registry (visible without opening the file)
   - Related: any existing slugs or task IDs this connects to? (optional)
2. Generate a slug from the title: lowercase, hyphens, no special chars, max 40 chars
   - If slug already exists, append `-2`, `-3`, etc.
3. Write `{data_dir}/{slug}.md` using the entry file format
4. Add a row to the `## Registry` table in `TRACKY.md`:
   ```
   | {slug}.md | {title} | {type} | current | {purpose} |
   ```
5. Confirm: show the slug, type, and one-liner purpose

### Entry file format

```markdown
# {title}

TYPE: decision | spec | note
STATUS: current
ADDED: {YYYY-MM-DD}
UPDATED: {YYYY-MM-DD}

## Content

{content}

## Why

{rationale — omit this section entirely if not provided}
```

---

## Triage

`/tracky triage`

Review all `deferred` entries one at a time:

1. Read TRACKY.md registry — collect entries with STATUS: `deferred`, oldest first
2. For each, display the title and content, then prompt:
   - `[a]` act on it — change status to `current`, ask for any detail to add
   - `[p]` promote to tasky — create a task (asks for feature name), mark as `current`
   - `[d]` discard — mark as `superseded`, no replacement
   - `[s]` skip — leave as `deferred`, come back later
3. Continue until all deferred entries handled or user skips
4. Show summary: N acted on, N promoted, N discarded, N remaining

---

## Updating an Entry

`/tracky update <slug>`

1. Read `{data_dir}/{slug}.md`; display current content
2. Ask what to change: content, why, type, status, purpose, or title
3. Apply changes; set UPDATED to today's date
4. If purpose changed: update the Purpose column in the TRACKY.md registry row
5. If title changed: update the Title column in the registry row
6. If status changed: update the Status column in the registry row
7. Write the file back; confirm

---

## Superseding an Entry

`/tracky supersede <slug>`

Used when a decision changes, a spec evolves, a question is answered, or knowledge becomes stale.

1. Read `{data_dir}/{slug}.md`; display it
2. Set its `Status` → `superseded`; set `Updated` to today
3. Update the `Status` column in the `TRACKY.md` registry row to `superseded`
4. Ask: "What replaces it?"
   - New entry: provide a title → run Add flow; set `Supersedes: {old-slug}` on new entry; set `Superseded by: {new-slug}` on old entry
   - Existing entry: provide a slug → link them (set fields on both)
   - Nothing — just marking stale
5. Confirm: show old entry (superseded) and new slug/title if created

---

## Slug Rules

- Lowercase
- Spaces → hyphens
- Remove special characters (keep alphanumeric and hyphens)
- Max 40 characters
- Be descriptive: `drag-group-behavior`, `no-build-step-dev`, `appshell-region-names`
