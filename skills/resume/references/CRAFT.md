# Craft — the winning bar

The second axis. Decision asks whether the five readers act. Craft asks whether the writing is
best-in-class, and answers it for every element on the page.

## Scale

| Grade | Meaning |
|---|---|
| `winning` | Top-decile. Names something specific the reader could not have guessed, and could not sit on anyone else's resume. |
| `competent` | Does its job. Nothing wrong, nothing memorable. |
| `median` | Interchangeable with the same line on two hundred other resumes in this lane. |
| `below-bar` | Spends the reader's attention and returns nothing. |

Never raise a grade to avoid a finding, and never invent a flaw to fill one. A `winning` grade is a
result, reported as fully as a failure.

## Granularity — grade the atom, report the unit

Scrutiny happens at the atom: every bullet, headline, summary line, title, org, date range, location,
tool name, link, and contact field is looked at and graded. Presentation happens at the decision unit
defined in `REPORT.md` — the employment header, the bullet, the summary block.

Atom grades ride in the owning unit's `fields[]` and roll up to it: **a unit grades no higher than its
worst atom in a deciding slot, and a unit with three or more `median` atoms grades `median`.** An atom
never becomes its own row. Never trade coverage for row count in either direction — grading fewer
atoms to keep rows low is the same defect as splitting a unit to raise the count.

## The transfer test

Applies to every element. Could this exact wording sit on a different person's resume in the same
lane without becoming false?

- Yes, unchanged → `median` ceiling.
- Yes once the org name is swapped → `competent` ceiling.
- No, it names something only this person did → eligible for `winning`.

## Bullet

A winning bullet answers, in this order: **what changed · what you did to cause it · what made it
hard.** A median bullet answers only the middle one.

Bars, each independently checkable:

- **owned verb** — opens with a verb that claims the work: built, shipped, cut, led, migrated, rebuilt.
  Fails on duty language: responsible for, worked on, helped, participated in, tasked with, involved in.
- **named mechanism** — the thing is named, not categorized. A specific datastore, protocol, model, or
  system passes; a category label — modern data stores, microservices-based architectures, AI tooling —
  fails.
- **outcome, not activity** — states a change in the world, not the activity restated. `cut X to Y`
  passes; `improving system reliability` fails.
- **difficulty visible** — scale, constraint, or failure mode is present, so the reader can tell the
  work was hard. A real volume, latency, headcount, or budget passes; an unqualified `at scale` fails.
- **front-loaded** — the most interesting words fall in the first eight. Fails when the payload sits
  behind a clause of setup.
- **single idea** — one bullet, one claim. Two independent achievements joined by `and` fail; split them.
- **no adjective doing an object's job** — robust, seamless, scalable, cutting-edge, best-in-class,
  state-of-the-art fail unless the number that earns the adjective follows it.

Three or more failed bars, or any broken or ungrammatical clause, grades `below-bar`.

## Headline

- Names the lane in the words a search would use.
- Claims one level, and a level the document proves.
- Carries one proof term rather than three role nouns strung together.
- Fails on: hedging across lanes, title-stacking, an adjective list, a level the body contradicts.

## Summary

- **Line one earns the read** — names the lane and the single strongest result. Identity-only openings
  (`Experienced engineer with N years of…`) fail.
- **Claims are cashed below** — every claim here is proved by a bullet further down. An uncashed claim
  grades `below-bar` however well written.
- **No meta-language** — proven track record, passionate about, results-driven, thought leader,
  seasoned professional.
- Length is not a bar. A two-line summary that meets these grades `winning`.

## Role block

- **Lead bullet is the strongest** — bullet one carries the role's best result. Fails when bullet one
  is duty or setup.
- **Attention matches relevance** — bullet count tracks how much the target cares, not recency or
  comfort. A role that is a fifth of the story taking half the lines grades `below-bar`.
- **Kinds vary** — built · led · decided · measured. Three consecutive bullets of one kind read as one
  bullet.
- **No theme twice** — two bullets covering the same theme are one bullet plus filler.

## Document

- **The top third carries the strongest proof** — reader attention is front-weighted; the best evidence
  is placed to match.
- **No claim stated three times** — once where it is summarized, once where it was earned. A third
  instance is filler.
- **Space tracks the target** — the oldest and least-relevant roles compress.
- **Consistent grammar** — tense, person, punctuation, and the capitalization of every product name
  hold across every bullet.

## Header and factual atoms

Graded individually, reported through the employment header or contact unit that owns them.

- **date range** — one format across every role. Mixed precision (`2019–2026` beside
  `Mar 2015 - Jun 2018`), inconsistent dashes, and inconsistent spacing each fail. An unexplained gap
  over six months between adjacent ranges fails, and rounding that hides one fails harder.
- **title** — reads at the level it was. Fails on internal-only titles a stranger cannot rank,
  slash-stacking that hides which one was held, and a title contradicting the scope the bullets show.
- **org** — recognizable, or given the one clause that makes it legible: what it does, and its size or
  stage. An unknown company with no context fails.
- **location** — present and consistent across roles, or absent from all of them. Present on some and
  not others fails.
- **tool and product name** — canonical capitalization and spelling, every occurrence. `chatgpt`,
  `Postgres`/`PostgreSQL` mixed, `nodeJS`, and a version number on one mention but not the next each
  fail. This bar is strict: on the most important page, a misspelled product name is the cheapest
  possible signal of carelessness.
- **link** — resolves, is not a bare tracking URL, and is labeled by destination.
- **contact** — reachable and consistent with the links.
- **section label** — says what the section holds in the reader's vocabulary. Invented headings fail.

## Findings from craft

A craft finding cites the element's `resumeDoc` path, names the failed bar, and quotes the wording. No
named bar, no finding.

Tier by **what the failure costs the reader**, never by which slot the element occupies. Position
raises the cost of a failure; it does not by itself create one. A weak line in a prominent slot is
still only a weak line.

| Tier | Condition | Test |
|---|---|---|
| 1 | The reader stops, or stops believing. A broken or ungrammatical clause, a self-contradiction, a claim the reader will read as false, or a lane that cannot be identified at all. | Would a reasonable reader put this down, or doubt the person, because of this? |
| 2 | A real chance is lost. Reachable proof landing weaker than it should, an unquantified central claim, or an unforced consistency error. | Does the reader still act, but with less conviction than the facts deserve? |
| 3 | Cosmetic, and still moves the needle. `median` wording in material that is read but does not decide. | Would fixing it make the page better without changing any verdict? |
| 4 | A preference with no bar behind it. Discard; never emit. | Can I name the bar? If not, there is no finding. |

Tier and grade are independent axes. A `below-bar` element in the most-read slot on the page is Tier 2
unless it meets the Tier 1 test on its own terms.

## Effect on the readers

Aggregate craft moves reader verdicts; a single failed bar never does. When a third or more of the
graded elements within a reader's reach grade `median` or worse, that reader's verdict falls one step.
When the elements in reach are majority `winning`, a verdict may rise one step.

Padding cannot raise anything. A longer version of the same content grades identically at every
element and moves no verdict.

## Conformance

- Every atom in scope carries a grade; every grade rolls up to exactly one decision unit.
- Every grade names the bar it was measured against and quotes the wording it judged.
- No atom becomes its own row.
- Grades judge the writing, never the person.
- No finding exists without a named bar.
- Equal content at different lengths produces equal grades.
