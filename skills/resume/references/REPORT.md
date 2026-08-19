# Resume report contract

The JSON island is the product. The HTML template renders it and exposes item-scoped workbench actions.

## Inline order

The first substantive line is always:

`MOVE FORWARD: yes|not yet|no — <first deciding gate or quoted urgency reason>`

Then:

1. Must-Talk 0–4 and ATS/screener/manager values.
2. Target decode: why the role exists and how the resume supports it.
3. Five-reader evidence: ATS → recruiter → HR → hiring manager → technical reviewer.
4. Gets Attention, maximum 3 exact quotes.
5. Ranked who/what/why/do findings.
6. Do Next: fix now · confirm · defend.

No heading, masthead, JD summary, or rubric verdict may precede the move-forward line.

## Decision object

```json
{
  "moveForward": "not yet",
  "reason": "ATS is weak-pass: the required platform evidence is buried.",
  "mustTalk": 2,
  "gates": {"ats":"weak-pass","screener":"call","manager":"interview"},
  "urgencyQuote": null
}
```

Enums:

- `moveForward`: `yes|not yet|no`
- ATS: `fail|risky|weak-pass|pass`
- screener: `no-call|maybe|call|urgent-call`
- manager: `no|insufficient|interview|priority-interview`

Derive Must-Talk by the ordered table in `READERS.md`; never type an independent score.

Before derivation, normalize a private decision vector from retrievability signals — whether the deciding content is findable and attached to proof — plus explicit claims, quoted proof, confirmed requirements, and material missing evidence. Parse status is tracked separately and never enters the vector. Effect-free prose is excluded. Equal vectors must render equal gates and move-forward calls. Without a JD, missing unspecified keywords cannot lower ATS.

## Contract `2.4.0`

Top-level keys required: `meta,resumeDoc,getsAttention,rubric,sections,resumeSections,items,outcomes`.

### `meta`

Required:

- `contractVersion: "2.4.0"`
- `reportId`, `name`, `role`: strings
- `mode`: `quick-scan|standard|rewrite|skillmatch`
- `decision`: the exact decision object above
- `readers`: exactly five `{name,verdict,evidence}` records named and ordered `ATS, Recruiter, HR, Hiring manager, Technical reviewer`
- existing presentation fields used by the template: `brief,scaleNote,plus1,signoff`; optional `pii,eyebrow,docTitle`
- `targetDecode`: the exact object below
- `parseStatus`: the exact object below — descriptive parse metadata, excluded from the decision vector and Must-Talk (not a gate)

```json
{
  "buyingNeed": {
    "statement": "Role exists to …",
    "beneficiary": "string|null",
    "constraint": "string|null",
    "status": "confirmed|inferred|unknown",
    "evidence": [{"source":"jd|user","quote":"exact source wording"}],
    "confirmingQuestion": "string|null"
  },
  "jdSupport": {
    "nonNegotiables": [{"need":"string","status":"proven|confirm|absent","itemIds":[1]}],
    "centralProblem": {"status":"strong|buried|weak|missing|unknown","itemIds":[1]},
    "differentiator": {"statement":"string","itemIds":[1]},
    "smallestTruthfulRepair": {"itemId":1,"action":"keep|tighten|rewrite|collapse|split|move|expand|cut|confirm","instruction":"string","truth":"confirmed|needs-confirmation"}
  }
}
```

`differentiator` and `smallestTruthfulRepair` may be `null`. Evidence caps at three records. `unknown` has an empty statement/evidence, null beneficiary/constraint, and a confirming question. `inferred` has JD evidence and a confirming question. `confirmed` has complete exact JD/user support and no question.

Confirmed repair actions are `keep|tighten|rewrite|collapse|split|move|expand|cut`. `needs-confirmation` permits only `confirm` and cannot supply replacement wording.

### `parseStatus`

Descriptive parse metadata. It never enters the normalized decision vector or Must-Talk derivation, and it is not editable through any durable verb, so it can never move the ATS gate on its own.

```json
{
  "state": "untested|tested",
  "affectsAts": false,
  "evidence": null
}
```

Invariants (enforced identically by both validator ports):

- `state: "untested"` ⇒ `evidence` is `null` **and** `affectsAts` is `false`. This is the default for every report with no observed extraction and for every migrated legacy report.
- `state: "tested"` ⇒ `evidence` is an object `{source,ref,observed}` with `source ∈ {extraction-artifact, parser-command}` and non-empty `ref` and `observed`. Only this branch may set `affectsAts: true`, and only then may tested parsing move ATS — through the cited observed evidence.

```json
"parseStatus": {
  "state": "tested",
  "affectsAts": true,
  "evidence": {"source":"extraction-artifact|parser-command","ref":"fixtures/extracted/base.txt","observed":"…first extracted lines…"}
}
```

### `rubric[]`

The demonstrated-skill rubric — a top-level array, sibling of `items`/`outcomes`. Each entry has
exactly `competency,grade,evidenceIds,gaps` and may additionally carry `bar` and `standing`; any
other key is rejected with `rubric[i] must have exactly competency,grade,evidenceIds,gaps`:

- `competency`: non-empty string.
- `grade`: integer 0–5, no decimals.
- `evidenceIds`: non-empty array of `resumeDoc` dot-paths (e.g. `resumeDoc.experience.0.bullets.0`),
  each resolving against `resumeDoc`. A competency produces **zero** `items[]` rows.
- `gaps`: array of strings — the confirmation prompts and ungraded observations, folded into the
  competency.

Non-empty only in `skillmatch` mode; every other mode carries `rubric: []`. The report renders it in
its own **Rubric** tab. The five-reader grid renders inline in the report body, below Why-this-role
and above Gets Attention. Grades never enter the decision vector or Must-Talk.

### `jdSet[]`

The supplied postings. Optional top-level array, sibling of `rubric`. Absent or `[]` is valid; legal
in every mode. When present every entry has exactly
`postingId,label,archetype,archetypeStatus,experience`:

- `postingId`: non-empty string ≤80, unique across `jdSet` — the address every `sources` value resolves to.
- `label`: non-empty string ≤120.
- `archetype`: `leadership|ic|architect|forward-deployed|generalist`.
- `archetypeStatus`: `inferred|confirmed`.
- `experience`: string ≤80 or `null` — the posting's stated experience requirement, verbatim.

A `postingId` no `bar` or `openBars` entry names is rejected. The rule fires only once at least one
bar exists.

### `rubric[].bar` and `rubric[].standing`

Optional. `bar` is an object with exact keys `requirement,level,range,sources`:

- `requirement`: the posting's wording verbatim, non-empty ≤400.
- `level`: string ≤120 or `null` — the strictest level named across `sources`.
- `range`: string ≤160 or `null` — the span when the sources named different levels. A non-null
  `range` requires at least two `sources`.
- `sources`: non-empty array of unique `jdSet[].postingId` values, each resolving.

**No count and no total is stored.** A row's `N of M` is `sources.length` of `jdSet.length`, derived
at render. `standing` is `meets|below|above|unprovable` and requires a `bar`. A row with no `bar` is a
demonstrated competency no posting named; it carries no standing.

### `openBars[]`

One entry per JD requirement with no applicant evidence. Optional top-level array; non-empty only in
`skillmatch` mode. Exact keys `requirement,level,range,sources,question` — the first four as in `bar`,
and `question` non-empty ≤240. A requirement string appears on at most one row across `rubric[].bar`
and `openBars[]`: a requirement is either graded or open, never both.

### `craft[]`

The craft-axis coverage — one entry per graded element, the answer to *is this winning*. Optional
top-level array, sibling of `items`. Absent or `[]` is valid; when present every entry has exactly
`path,element,grade,bars,itemIds`:

- `path`: string starting `resumeDoc.`, ≤256 chars — the graded element.
- `element`: `headline|summary|bullet|role-header|section|document|contact`.
- `grade`: `winning|competent|median|below-bar`, per `CRAFT.md`.
- `bars`: non-empty array of `{bar,grade,note}` — the atom-level scrutiny that produced the roll-up.
  `bar` is a bar name from `CRAFT.md`, ≤80 chars; `grade` uses the same four values; `note` is ≤240
  chars and quotes the wording it judged. At most 20 entries.
- `itemIds`: array of `items[]` `n` values this element produced; each must resolve. Empty is valid
  and is the expected value for a `winning` or `competent` element.

Paths are unique across `craft`. An element graded `below-bar` or `median` carries at least one
`itemIds` value — every such grade owes the reader an action; `winning` carries none; `competent` may
carry none. No atom appears as an `items[]` row — atoms surface only here and in the owning unit's
`fields[]`.

### `severity`

Optional integer on each `items[]` entry, `1|2|3`, per the tier table in `CRAFT.md`. Tier 4 is
discarded and never emitted. Absent defaults to `2` at render. The report groups findings by tier and
filters on it.

### `sections`

Each entry is `{id,title}`. IDs are unique. Exact order:

- quick-scan/standard/rewrite: `resume`, optional `linkedin`, `donext`, `readers`
- skillmatch: `resume`, optional `linkedin`, `donext`, `readers` — same as every other mode; grades and their confirmation prompts live in `rubric`, not in sections

`linkedin`, when present, is immediately after `resume`. Readers are last.

### `resumeSections`

The per-section whole-read. A top-level array, sibling of `items`. Each entry is a first-class stored
assessment of one résumé section, and `items[]` findings group beneath it. Each has exactly
`sectionId,path,title,verdict,status,staleness,assessment`:

- `sectionId`: non-empty string, unique across `resumeSections`. Item→section link: each `items[]`
  entry carries a `sectionId` that must resolve to one of these (membership only — the derivation
  rule lives in the bridge migration, never in the validator).
- `path`: string starting `resumeDoc.`, ≤256 chars — the section's représentative résumé node.
- `title`: non-empty string, ≤80 chars.
- `verdict`: `strong|adequate|weak|unread`. `status`: `open|done|ignore`. `staleness`: `fresh|stale`.
- `assessment`: string, ≤800 chars; non-empty **unless** `verdict` is `unread`. No sentence count and
  no minimum: a whole-read says as much as the section needs, and how long the résumé itself runs
  never changes how much it says (evidence-equivalence). Sentences obey the rule every other prose
  field obeys — none runs past fifteen words. The ≤800 is a machine backstop that fails closed, never
  a target and never counted while writing.
- Cross-field invariants: `staleness: "stale"` requires `verdict != "unread"`; an empty `assessment`
  requires `verdict == "unread"`.

**Stale lifecycle.** A section is assessed (`verdict != "unread"`) when the agent has read it. When a
child point-item change is *accepted* — `acceptRewrite` or a content `updateItem` — that child's
assessed parent flips to `staleness: "stale"` in the same atomic write, and the report shows a
`stale — re-read pending` badge. `setStatus` is workflow, not content, and never marks stale. The
served page cannot re-read prose: the agent clears staleness on a following turn via the
`rereadSection` verb, which rewrites `verdict/status/assessment` and sets `staleness: "fresh"`.

### `items[]`

**Granularity — one row per decision unit, never per atom.** An `items[]` entry is something a human
reacts to, not every accuracy-checkable field. Required units: identity/contact = 1 row; headline +
summary = 1 (2 only when headline and summary carry independent decision effects); each employment
header (org **+** title **+** dates **+** location, plus any internal progression such as a
LinkedIn-only promotion) = 1; each accomplishment bullet = 1; each education / cert / prof-dev entry =
1; LinkedIn carries only genuine deltas versus the resume. FORBIDDEN: separate rows for the `org`,
`title`, `dates`, or `location` of one role; a row per skill keyword; a row per contact field. A
normal two-page resume lands **15–35** entries (a soft render advisory, not a validator reject).

Atoms are not lost: an employment-header unit carries them in its `fields[]` array
(`{k:"org",v:…},{k:"title",v:…},{k:"dates",v:…},{k:"location",v:…}`), which a validator may still
check against `resumeDoc` or a LinkedIn delta — it simply never surfaces an atom as its own row.
`ctx.atom` holds a human-readable composite of the unit; a bullet references its employment header
through `ctx.neighbor` (display) and `ctx.relatedIds:[headerN]` (navigation), never by copying the
header text into the bullet.

Required item fields:

`n,section,sectionId,status,title,verdict,reason,urgency,suggestion,fields,decisionEffect,meta,ctx`

- `n`: unique integer, never boolean.
- `section`: existing section ID.
- `sectionId`: résumé-section id resolving to a `resumeSections` entry (the whole-read this finding
  groups beneath). Distinct from `section`, the structural tab id.
- `status`: `open|done|ignore`.
- `urgency`: `crit|high|med|low|none`.
- `decisionEffect`: `decision|proof|risk|action|none`, equal to `ctx.decisionEffect`.
- `fields`: array of `{k,v}`; empty is valid.
- `meta`: exactly `{scope:"atom|context",visibility:"hotspot|supporting|clean"}`.
- optional: `quoted,rewrite,confirm,tag,prompt,target`.
- `target`, when non-empty, is unique across items.

Every `decisionEffect: none` item is `tighten|cut`. A clean `keep` carries a proof/risk/decision/action effect and may omit its prompt; every non-`keep` item carries a non-empty prompt containing literal labels and values:

`ctx.path` names the element the item's suggestion would edit, and `quoted`, `reason`, and `suggestion` all address that element. A suggestion that sends its edited text to a different role, employer, section, or period than `quoted` is misanchored: repath it to the element that would carry the repair, or rescope it to `context` on the section that would hold the proof. Naming another role as the source of a fact is not misanchoring. An `atom` item never anchors to an element that merely resembles the concern.

`clean` visibility requires `verdict: keep`. A `context` item needs two unique related item IDs, or a summary/role/section path with at least two evidence lines. When a context hotspot names the missing facts, do not emit atom or supporting rows that repeat them. A hotspot must affect a gate, materially strengthen important proof, remove credibility risk, or resolve a repeated pattern; zero hotspots is valid.

Candidate-facing hotspot copy addresses `you`, names the location and likely reviewer conclusion, and gives exactly one smallest action. A confirmation question names the item that should receive the verified answer and asks directly about the missing condition or outcome—never generic “facts,” “evidence,” “proof,” or “if any.” Write to sentence counts, not character counts: `title` is one clause and never a sentence, `reason` prefers two sentences and never runs past four, `suggestion` is one sentence and never more than two. No sentence runs past fifteen words; split the thought or cut it. The renderer backstops hotspot copy at 80, 600, and 400 characters respectively and fails closed past them; those ceilings catch a runaway, they are not the target and are never counted while writing. Do not expose `atom`, `gate`, `decisionEffect`, `provenance`, `semantic`, `vector`, `PCOPO`, or “the candidate.”

```text
Item: <n>
Atom: <quoted atom>
Evidence: <support or missing>
Truth: <truth constraint>
Decision effect: <effect>
Task: <requested action>
```

### `ctx`

Every item carries exactly these 13 keys:

```text
itemId,path,lane,reader,atom,neighbor,evidence,truth,decisionEffect,
suggestion,relatedIds,decisions,questions
```

`itemId` equals item `n`; `decisionEffect` equals the item value. `neighbor` contains at most one adjacent atom. `relatedIds`, `decisions`, and `questions` are arrays. No status, full item, `resumeDoc`, contact field, or unrelated atom belongs here.

Capsules carry machine-enforced payload bounds, checked by the validator and never counted while writing: `path` 256, `lane` 160, `reader` 80, `atom`/`neighbor` 600 each, `evidence` 800, `truth` 240, `decisionEffect` 20, and `suggestion` 600 characters. Each array has at most 20 values; decision/question values cap at 400 characters. These bound the payload so a serialized résumé cannot masquerade as one atom or list entry; they say nothing about how long prose should read.

A LinkedIn row has at least one `ctx.relatedIds` value resolving to a `resume` item.

### `outcomes[]`

Every entry has exactly:

```json
{
  "resumeVersion": "v3",
  "itemIds": [4],
  "window": {"start":"2026-07-01","end":"2026-07-31"},
  "applications": 12,
  "callbacks": 4,
  "interviews": 3,
  "note": "Changed the opening summary."
}
```

Rules: non-empty version; non-empty unique existing integer IDs; exact `window` object with real ISO calendar dates and start ≤ end; counts are nonnegative integers, not booleans; `interviews ≤ callbacks ≤ applications`; note is a string; no extra/missing keys. Reject language that attributes an application, callback, call, or interview outcome to an edit. Preserve temporal/comparison observations and explicit non-attribution.

Render every observation as: before → smallest change → decision effect → counts/note, prefixed **observed after, not attributed to**. Never infer causation from sequence.

### `resumeDoc`

Preserve the existing structured resume:

`name,headline,contact{location,phone,email,links[]},summary,coreTech[{label,items}],experience[{org,role,dates,bullets,stack?}],extras[{title,items}]`

Preview nodes retain `data-path` targets. Accepted rewrites update one unique target.

Store prose exactly as the source wrote it, markdown included; never strip emphasis on the way in. Both previews render `**bold**` as typography in headline, summary, about, bullets, and extras items — a preview printing the asterisks shows the reader something no reviewer would ever see. Emphasis is the only markup honored, it converts after escaping, and identity fields — `name`, `org`, `role`, `dates` — render escaped and unstyled.

### `linkedinDoc`

Optional. Present only when LinkedIn content was supplied; an island without the key is valid and unchanged.

`headline?,about?,experience?[{org,role,dates,bullets}],skills?[],extras?[{title,items}]`

Every key is optional and the object must be non-empty; unknown keys are rejected. `org`, `role`, `dates`, `headline`, `about`, and `title` are strings; `bullets`, `skills`, and `items` are arrays of strings. It carries no contact fields — identity lives in `resumeDoc.contact` only.

When present it renders in its own view behind its own tab, never inside the résumé preview, and is writable through `patchLinkedin`; a LinkedIn item's `target` may name a `linkedinDoc.*` path. The résumé preview renders `resumeDoc` and nothing else: a reader must never have to work out which medium a line came from. When absent, the tab stays hidden, LinkedIn findings remain editable as items through `updateItem`, and nothing else changes.

## Workbench behavior

- Edit creates a draft only.
- Save calls `updateItem`; the bridge validates and atomically writes before broadcast/repaint.
- Cancel discards the draft and does not call the bridge.
- Accept rewrite calls `acceptRewrite`; resume node, `ctx.decisions`, and status change together or not at all.
- Status calls `setStatus`; no page/localStorage repaint before success. On reload, disk-backed status is authoritative; localStorage is only a post-write cache.
- Accepting a point change (`acceptRewrite`, content `updateItem`) marks its assessed parent section `stale` in the same write; `setStatus` does not. `rereadSection` clears it back to `fresh`.
- `getContext`, Converse, and row Export JSON return only the exact 13-key `ctx` capsule.
- Converse envelope is exactly `{instruction,context}`.
- Cross-item export is separately labeled and is the only full-island UI action.
- Offline reading, preview, expand, stage, and copy remain available. Durable actions explain that the bridge owning this report is required.
- The table opens with `hotspot` rows only. `Show all observations (N)` reveals `supporting|clean` rows in place and toggles back to `Show hotspots`; it changes no report data or status.
- With zero hotspots, render `No changes are important enough to recommend right now.` and retain the reveal control.

## Atomic bridge verbs

- `updateItem(n,patch)`: allow `reason,suggestion,verdict,rewrite,prompt,decisions,questions`; map the last two only into `ctx`. Marks the item's assessed parent section stale.
- `setStatus(n,status)`
- `acceptRewrite(n,index)`: marks the item's assessed parent section stale.
- `rereadSection(sectionId,patch)`: `patch` sets only `verdict,status,assessment`; the verb also sets `staleness: "fresh"`. `staleness` is system-managed and cannot be set through the patch.
- `patchLinkedin(path,text)`: sets one existing `linkedinDoc.*` node. Rejected when the island carries no `linkedinDoc`. `acceptRewrite` follows whichever prefix the item's own `target` names.

Each performs locked read → mutate → validate → atomic write → broadcast. Failure changes nothing. The written island is the copy of record; the `--island` build input and any source document are never written back.

## Export

```bash
python3 references/agui_bridge.py export --report report.html --doc resume|linkedin|island [--format md|json] [--out PATH]
```

Reads the report's island and emits one document. `resume` and `linkedin` render `resumeDoc` / `linkedinDoc` as markdown, or as JSON with `--format json`; `island` emits the whole island as JSON. Read-only on the report, requires no bridge, and validates the island before emitting. A missing `linkedinDoc` exits nonzero rather than emitting an empty document. Exported résumés carry contact fields and stay local.

## Render

```bash
python3 references/agui_bridge.py render --island report.json --out report.html --serve
```

The renderer accepts `2.4.0` directly and migrates older versions forward on a deep copy before validating. From `2.3.0` it synthesizes `resumeSections` — one `unread`/`fresh` whole-read per section derived from each item's `ctx.path` prefix — and stamps every item's `sectionId`. From `2.2.0` it also inserts the default `rubric: []`. From `2.1.0` it additionally inserts the default `untested` `parseStatus`. From `2.0.0` it additionally inserts an unknown target decode and assigns each legacy item `{scope:"atom",visibility:"hotspot"}`. It stamps the copy `2.4.0` and validates it. The caller’s object and old standalone HTML remain unchanged. Unsupported versions fail closed. Candidate data stays local.
