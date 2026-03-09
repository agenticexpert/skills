# tracky — Search & Surface

## Progressive Disclosure Model

TRACKY.md contains the full registry — file, title, type, status, purpose — for every tracked entry. This means:

- List and filter: read TRACKY.md only (no individual files opened)
- Show: read TRACKY.md + one file
- Search: read TRACKY.md first; open files only for registry matches

Never read individual entry files speculatively. Fetch only when the registry indicates relevance.

---

## List All Entries

`/tracky list`

1. Read `TRACKY.md` — extract the `## Registry` table
2. Display all rows, grouped by type, ordered within each group by status:
   - `current` first, `draft` second, `superseded` last
3. Format:

```
decision  (3)
  ✓ no-build-step-dev          No build step for dev — use source-first resolution
  ✓ monorepo-structure         Why packages/morphy, morphy-svelte, apps/demo
  ~ split-tasky-skills         Should roadmap and tasks be separate skills?  [draft]

spec  (2)
  ✓ drag-group-behavior        How linked nodes move together during drag
  ~ appshell-regions           AppShell layout regions and slot names  [draft]

note  (1)
  ✓ desktop-app-aesthetic      VS Code / Figma productivity app as the visual target
```

Symbols: `✓` current · `~` draft · `✗` superseded · `?` question type

---

## List by Type

`/tracky list <type>`

Same as above but filtered to one type. Valid types: `decision`, `spec`, `note`.

---

## Show a Full Entry

`/tracky show <slug>`

1. Look up `{slug}` in the TRACKY.md registry — confirm it exists
2. Read `{data_dir}/{slug}.md`
3. Display the full entry (all fields + content + why)
4. If status is `superseded`: show what supersedes it
5. If `Related` entries exist: list them by title (from registry — no file reads); offer to show any of them

---

## Search

`/tracky search <query>`

### Phase 1 — Registry scan (no file reads)

1. Read TRACKY.md registry
2. Match query keywords against: file slug, title, purpose
3. Collect candidate entries

### Phase 2 — Content scan (targeted file reads)

4. For each candidate, read the full entry file
5. Match query against Content and Why sections
6. Rank by: title match > purpose match > content match

### Output

Group results by type. Show: slug, title, type, status, one-sentence excerpt.
Flag `superseded` entries — they may indicate the current answer is elsewhere.

### Restricting by type

`/tracky search decision <query>` — restrict search to one type (`decision`, `spec`, or `note`).

---

## Passive Surfacing

When working on something where tracky knowledge is relevant (e.g. discussing a component, reviewing a task):

1. Scan TRACKY.md registry titles + purposes for keyword matches (no file reads)
2. If 1–3 relevant `current` or `question` entries found: mention them briefly
   - "2 tracky entries on this — want to see them?"
3. If 4+ matches: summarize by type, offer to show
4. Never surface `superseded` entries passively
5. Never interrupt the main task — offer, don't block
