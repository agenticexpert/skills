# Compile

Stitch all section script blocks into a clean `script.md` for read-through, voice recording, or export.


## Prerequisites

- A storypad must be open (storypad.md loaded in context)
- At least some sections should have `script:` blocks — a compile with no scripts is valid but mostly empty


## Command

```bash
python3 .claude/skills/storypad/scripts/compile.py {path-to-storypad.md}
```

Optional flags:
- `--output {path}` — write to a specific file instead of `{storypad-dir}/script.md`
- `--stdout` — print to terminal instead of writing a file


## What It Produces

A `script.md` file in the storypad directory with:

```markdown
# Build a customer support chatbot from scratch

venue: youtube  |  compiled from: storypad.md

---

## Intro

So here's what we're going to build today. A full customer
support chatbot — that can look up orders, process refunds,
and hand off to a human when needed.

---

## Loop

[ no script yet ]

---

## Tools

So the bare loop can talk, but it can't DO anything.
Let's fix that.

Tool calling lets the model reach out and take action —
think of it like giving the chatbot hands.

---
```

Sections with no `script:` block appear as `[ no script yet ]`. This makes gaps visible without breaking the flow.


## After Compiling

1. Run the compile script
2. Display the output path and coverage summary:
   ```
   Script compiled → agents/docs/storypads/chatbot-tutorial/script.md
     Sections with script: 5/7
     Missing script: Loop, Context
   ```
3. Offer to open the compiled script for review
4. The user can copy/paste into a teleprompter, voice AI, or document


## Workflow

The compile step sits at the end of the scratchpad → sections → compile flow:

1. **Scratchpad** — Hash out ideas, try different ways of saying things
2. **Sections** — Pull the best ideas into `script:` blocks within each section
3. **Compile** — `/storypad compile` stitches them into a clean linear script

Re-compiling is safe — it always overwrites `script.md` with the current state of the sections. The source of truth stays in `storypad.md`.
