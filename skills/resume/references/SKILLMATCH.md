# Skill evidence rubric

A JD supplies expectations, not a candidate verdict.

## Scale

| Grade | Demonstrated evidence |
|---|---|
| 0 | Required skill named; no applicant evidence found. Use only after a complete evidence sweep. |
| 1 | Exposure: vocabulary or participation, no owned output. |
| 2 | Applied: completed bounded work with the skill. |
| 3 | Ships: owned a production outcome and can defend choices. |
| 4 | Leads: set direction across a team/system and handled tradeoffs. |
| 5 | Multiplies: created an adopted practice/platform/design that raised others’ output. |

No decimals. A title, certification, keyword, or self-rating does not by itself prove 3+.

**A row is a grade, a standing, one reason, and one way up — nothing else.** `gaps` carries exactly
two strings on a sub-5 grade: the single reason the grade is what it is, then
`To reach <n+1>: <the one thing that would move it>`. A grade of 5 carries the reason alone. Each is
one sentence of at most fifteen words. A row that needs a third line has not been decided yet — choose
the deciding one and drop the rest.

**A gap reads as the judgement, never its defense.** Do not narrate what was read or how thoroughly,
do not quote or paraphrase the résumé line, and do not restate the posting's wording — the `bar`
already carries the requirement and `evidenceIds` already carries the proof. Repeating either is how a
rubric turns dense enough to stop being read. Write the reason as the specific evidence that does not
exist yet — the tradeoff never named, the outcome never measured, the direction never shown — never as
a restatement of the grade. An empty `gaps` on a sub-5 grade is not a clean bill; it is an ungrounded
grade, because nothing states what would move it.

**A grade inherits the craft state of the lines it cites.** When an `evidenceIds` path resolves to an
element graded `below-bar` or `median` in `craft[]`, a competency proved only by that broken,
unmeasured, or interchangeable line is not equivalent to one proved by a clean line. When the craft
defect is what holds the grade down, it *is* the reason; otherwise it stays in `craft[]` and the
rubric does not repeat it.

## The bar — when postings are supplied

Row generation is JD-driven; grading is résumé-driven. Every requirement in the supplied set produces
a row — graded when applicant evidence exists, open when it does not. A JD never supplies a grade.

Each row states the bar as the posting worded it, and its own source count and source postings. A
requirement several postings share takes the strictest level named, and states the range when the
postings named different levels. **There is no threshold separating a lane row from a scoped row**:
every row carries its count, and grouping is display only.

Each row also carries a standing against its bar — `meets`, `below`, `above`, or `unprovable`.
**Standing never aggregates.** No count, average, percentage, band, or rollup of standings, and
standing never enters the ATS, screener, or manager gate.

**Adding a posting never lowers a grade the evidence already earned.**

Each posting carries an archetype — `leadership`, `ic`, `architect`, `forward-deployed`,
`generalist` — read from title, reporting line, and whether the responsibilities set
direction for people, build the system, or deploy and translate at the customer. Mark it `inferred`
until the user confirms it.

A heterogeneous set is graded, never refused. State counts: postings, archetypes present,
requirements named by every posting, and the stated experience values. State the count, never the
trend: a claim about what the wider market wants is `mkt` and carries a named source or is not made.
When the résumé is irregular against an archetype, name the
rows of that archetype the evidence does reach; when it reaches none, that is one stated line about
archetype fit, not a row per requirement.

## Evidence gate

For each candidate grade:

1. Quote the applicant artifact.
2. Tag the source: `seen|li` for applicant evidence; `jd|mkt|web` may define expectations only.
3. Name the behavior the quote proves.
4. Apply the grade definition.
5. If the quote does not prove the grade, lower it or mark it ungraded.

A quote proves a grade only for the competency it *names*. Generic delivery or ownership language (“built production platforms,” “owned a rollout”) that names no datastore, architecture, system, or artifact proves exposure at most — mark that competency `ungraded · confirm`, never 2 or 3. One quote cannot ground graded rows for two competencies: if a single line is the only evidence for both, grade only the competency it names and ungrade the other.

Expected-but-unlisted and transferable skills without quoted applicant evidence are observations:

```text
<skill> — ungraded · confirm
expectation: <why the lane/JD needs it> [jd|mkt|web]
bridge: <source capability, if any> [inferred|needs-confirmation]
question: <one question that could produce applicant evidence>
```

Never assign them 0 merely because evidence is absent from the provided artifact. Grade 0 is reserved for a required skill after the full applicant evidence sweep finds none.

## Run

1. Build a category spine: domain · delivery · architecture · operations · quality/security · leadership/communication.
2. Extract applicant evidence across resume, LinkedIn, and confirmed conversation.
3. Grade only demonstrated rows.
4. Record JD expectations separately.
5. Feed evidenced strengths, missing proof, and confirmation questions into ATS/screener/manager context.
6. Apply the shared decision rule. The first substantive line remains `MOVE FORWARD...`.

## Output

```text
MOVE FORWARD: <yes|not yet|no> — <first deciding gate reason>
Must-Talk <0–4> · ATS <...> · Screener <...> · Manager <...>

Demonstrated skills
| Skill | Grade | Applicant evidence | What it proves |

Ungraded observations
| Skill | Expectation/bridge | Truth | Confirm question |

Decision effects
- <proof/risk/action that changes the call>
```

Do not emit fit bands, applicant-minus-JD arithmetic, match percentages, “ready/stretch/reach/mismatch,” or a JD-driven candidate grade. A required level may be named as the bar; it never becomes the verdict.

## HTML mapping

Use contract `2.4.0` from `REPORT.md`:

- `meta.mode: "skillmatch"`
- supplied postings are `jdSet[]`; a row's bar is `rubric[].bar` and its standing `rubric[].standing`; a requirement with no applicant evidence is an `openBars[]` entry, never a row with a null grade
- `N of M` is derived from `bar.sources` against `jdSet`; no count or total is stored
- sections: `resume`, optional `linkedin`, `donext`, `readers` — the same set as every other mode
- each competency is a `rubric[]` entry (`{competency,grade,evidenceIds,gaps}`), never an `items[]` row; a competency produces zero items and renders in its own Rubric tab
- ungraded / expected observations and their confirmation prompts fold into that competency's `gaps[]`; they cannot affect `meta.decision` until evidence exists
- `items[]` holds only decision-unit findings, each carrying exact `ctx`

## Conformance

- Every numeric grade cites at least one `evidenceIds` path that resolves in `resumeDoc`.
- Unsupported expected/transfer rows are ungraded.
- JD evidence never masquerades as applicant evidence.
- Decision is first and uses the three gates.
- No match percentage, fit band, delta, or invented proof.
- Every graded row citing a supplied posting carries that posting's wording as its bar.
- No standing is counted, averaged, summed, or rolled up, and no standing reaches a gate.
- A grade never falls because another posting was supplied.
- Counts are stated; a market claim is not.
