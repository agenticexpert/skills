# Report Form — the shape of a task summary / action hand-back

The canonical shape for any user-facing moment where tasky hands back a **task
summary** or tells the user **what to do next**. It exists so a reader who saw none of
the work learns exactly two things and no more: whether what they asked for was done,
and anything that genuinely blocks them. Everything else — internal slugs, problems
already found and fixed, a blow-by-blow of the work — is noise the reader did not ask
for, and the form is built to keep it out.

This is the ONLY copy of the form; tasky points here and never pastes it inline (copies
drift). It governs **tasky's hand-back alone** — singleshot carries its own summary
shape and does not use this file.

## The form

A hand-back has three content slots, each opened by a literal label. **The label is the
form: an unlabeled hand-back is not this form**, however plainly it reads.

```
DONE: <one plain line — what the user asked for, and whether it is done>
BLOCKED: <only when one exists — a real blocker, or a question only the user can
         settle. Omit the label entirely when nothing blocks.>
NOTES: <optional tail — where things stand, and anything worth checking or testing>
```

- **`DONE:` is always present.** It answers the one question the reader always has —
  did the thing I asked for get done? One plain sentence, no internals.
- **`BLOCKED:` appears only when something genuinely blocks the reader** — a dependency
  that isn't done, or an ambiguity that cannot be resolved without them. Nothing
  blocking → the label does not appear at all. This is the form's teeth: a blocker the
  reader must act on is a labeled line, never buried in prose.
- **`NOTES:` is an optional tail** for specifics — the state of play, or a short list of
  what to run or verify. What-to-test items live here, in plain language.

## Forbidden — by name

None of these may appear in a hand-back:

- **Internal identifiers without their plain meaning in the same sentence** — a
  directory slug, criterion number, step or gate name, `set-status`, a checkbox. Say
  the thing in human words, or leave it out.
- **Problems found and already fixed.** If you hit something and resolved it, it is not
  the reader's concern; it does not go in the hand-back.
- **A ledger of work performed** — a blow-by-blow of what you did. The reader wants the
  outcome, not the transcript.
- **A menu whenever a preferred action can be named.** When one action is clearly right,
  state it and proceed; never pair it with options the reader would reject. tasky's
  no-false-menus rule lives in `SKILL.md → Deciding` (§4) — this form does not reopen it.

## One worked example

```
DONE: the three tasks in the login milestone are finished and their tests pass.
BLOCKED: the login form needs a session key that only you can issue.
NOTES: run `make test-auth` to confirm before you mark it done.
```
