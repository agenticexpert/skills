# Mem

**Mem is durable conversation memory: it turns a session into a structured, chronological summary that survives `/clear` and compaction, hands off to another agent or session, and can split into idea threads or rejoin them.**

Context windows end; work doesn't. Mem writes what happened — decisions, requirements, todos, keys, references, and the through-line — to disk in a fixed format, so the next session (or the next agent) picks up where this one stopped instead of starting cold.

**Data root: `.agents/mem/`**

```
.agents/mem/
  mem.md          project augment — extends or replaces the default format (optional)
  summary/
    SUMMARY.md    current checkpoint
    archive/      rotated summaries and exports
  ideas/          split idea threads
  logs/           trigger logs — decisions, keys, references, requirements, todos
  triggers.md     live-trigger block, re-injected by the compact hook
  transcripts/    raw conversation archives, timestamped, auto-written on session end
```

---

## What It Does

| Command | What it does |
|---|---|
| `/mem summarize [to {path}] [using {augment}] [from {source}]` | Write or update the current checkpoint. |
| `/mem continue [decide] [from {path}]` | Resume from a checkpoint — rehydrate and pick up the work. |
| `/mem split {idea} [to {path}] [and prune]` | Peel an idea thread into its own file. |
| `/mem trigger {name}` / `trigger off {name}` / `trigger list` | Turn semantic capture triggers on and off. |
| `/mem decide` | Surface the open decisions for a call. |
| `/mem decisions` · `requirements` · `todos` · `keys` · `refs` | Review a specific log. |
| `/mem prune {topic}` | Drop a topic at the next summarize. |
| `/mem install` | Install the hooks (compact re-injection, session-end transcript). |

Bare `/mem` and `/mem summary` alias `summarize`; `/mem capture` aliases `split`.

---

## A Typical Session

You've been working a while and the context is filling up. You checkpoint, then clear:

```
/mem summarize
/clear
```

What those two commands set in motion:

1. **`/mem summarize`** reads the conversation start to finish and writes a structured checkpoint to `.agents/mem/summary/SUMMARY.md` — timeline, decisions, todos, open questions, with code, commands, and your exact asks kept word-for-word. Any checkpoint already there is archived first; nothing is overwritten.
2. **`/clear`** resets the context window as usual — but mem intercepts it. Just before the window blanks, it prints that checkpoint into the *fresh* session, so the next context opens with the summary already loaded and you resume mid-thought instead of cold. The checkpoint file is then rotated into `.agents/mem/summary/archive/` with a timestamp.

Two more things happen on their own in the background:

- **When a session ends,** its raw transcript is archived to `.agents/mem/transcripts/{timestamp}.jsonl` — stamped in the same format as the rotated summary, so each summary pairs with the transcript it came from. A complete record that replaces a manual `/export`; summarize a closed session later straight from it: `/mem summarize from .agents/mem/transcripts/{timestamp}.jsonl`.
- **When the context compacts,** any active triggers (below) are re-injected so they keep running through the reset.

So the everyday loop is: **summarize → clear → the summary reappears in the next window, the old one is filed away, and the transcript is kept.**

> The auto-reappear step needs the hooks installed once with `/mem install` (see below). Without them, `/mem summarize` still writes the checkpoint — you just reload it yourself in the next session with `/mem continue`.

---

## When to Use

- Checkpointing before `/clear`, a compaction, or the end of a working session.
- Handing a task off to another agent or picking one up from a checkpoint.
- Capturing a tangent as its own thread without derailing the main summary.
- Reviewing what got decided, required, or deferred across a long build.

---

## How to Load It

Mem is a semantic skill — describe the memory action, or use the subcommands directly.

Examples:

- "Checkpoint this session." · "Summarize where we are."
- "Continue from the last checkpoint." · "Pick up where the other agent left off."
- "Capture this idea as its own thread."
- "What decisions are still open?"

Force it by name: `/mem`.

---

## How It Runs

- **Chronological, always** — start → current, earliest summary first. Later information supersedes earlier; both are kept, and the supersession is marked.
- **Artifacts verbatim** — code, commands, errors, and the user's exact questions are preserved word-for-word, never paraphrased.
- **One format, one source of truth** — the summary spec lives in `references/summarize.md`; the default section set lives in `references/default-sections.md`, and a project can extend or replace it via `.agents/mem/mem.md`.
- **Triggers** — semantic capture rules that log decisions, keys, references, requirements, and todos as they surface, re-injected across compaction by the hook so they survive the context reset.

---

## Customizing What Gets Saved

By default, mem writes each checkpoint into a fixed set of sections — a timeline, open decisions, todos, and so on. If your project has something worth capturing *every* time — schema changes on a database project, endpoints on an API, experiments in a research log — you can teach mem to track it. That add-on is called an **augment**: a short text file that adds to or changes what a summary contains.

**Define one.** Make a text file and describe the section you want in plain language. For a SQL project that should record every migration:

```text
ADD SECTION <schema-changes> after <timeline>

List every table or column changed this session, in order.
For each one: the exact SQL statement, why it changed, and the
migration file that applies it.
```

The first line tells mem *where* the new section goes — `after <timeline>`, though any existing section works as the anchor. Everything below it is just instructions to mem, written the way you'd explain it to a person.

**Turn it on.** Two ways:

- **Just this once:** `/mem summarize using path/to/your-file.md`
- **Every time:** save the file as `.agents/mem/mem.md`. Mem picks it up automatically on every checkpoint — no flag needed.

**Write your own format from scratch.** Don't want the built-in sections at all? Start the file with `RESET FORMAT`, then list only the sections you want:

```text
RESET FORMAT

ADD SECTION <what-we-did> first
A plain narrative of what happened this session.

ADD SECTION <next-steps> last
What's left to do, one line each.
```

That produces a two-section summary and nothing else.

The full set of directives — including how to edit or replace a built-in section rather than add one — is in `references/summarize.md`, with a worked example in `references/augments/decisions.md`.

## Capturing as You Go — Triggers

Augments shape the summary you write at checkpoint time. **Triggers** work the other way: a trigger is a standing rule that watches the conversation and logs things *the moment they come up*, so nothing has to be reconstructed later. Each writes to its own file under `.agents/mem/logs/`.

Five ship with mem:

| Trigger | Catches | Logs to |
|---|---|---|
| `decision` | choices made, considered, or reversed | `logs/decisions.md` |
| `requirement` | requirements stated, changed, or dropped | `logs/requirements.md` |
| `todo` | work items created, done, blocked, or deferred | `logs/todos.md` |
| `kv` | named facts and config values ("X = Y") | `logs/keys.md` |
| `reference` | files, URLs, docs, or libraries flagged as relevant | `logs/references.md` |

**None are on by default** — you opt in, per session.

**Turn one on:** `/mem trigger decision`. Stack as many as you like; each runs on its own. Turn one off with `/mem trigger off decision` (or `off all`), and check what's active with `/mem trigger list`. At your next `/mem summarize`, an active trigger's log feeds its section of the summary instead of being rebuilt from scratch — todos, requirements, and references have a section built in; for decisions or keys, add one with an augment (above).

**Make them stick.** Run `/mem install` once. After that, active triggers survive `/clear` and compaction: mem re-injects the live set back into the fresh context so they keep running in the next window instead of silently dropping.

**Write your own.** Create a macro at `references/triggers/{name}.md` with four parts — what to watch for, how to check each response for it, what to write and where, and any edge-case notes:

```text
# TRIGGER: risk

## Condition
Any risk, caveat, or "this could break if…" raised about the work.

## Audit
Before finishing a response, check whether a risk was named or implied.

## Action
If so, append to .agents/mem/logs/risks.md: the risk and what it affects.

## Notes
Update the existing line for a risk instead of adding a duplicate.
```

Then activate it like any built-in: `/mem trigger risk`. Full details — custom log paths, swapping a trigger's action, how survival works — are in `references/trigger.md`.

## Installation

```bash
npx skills add agenticexpert/skills/mem
```

Then run `/mem install` once to wire up the compact and session-end hooks.

Part of [Agentic Expert](../../README.md). Built by **Shawn Bullock** — [agenticexpert.ai](https://agenticexpert.ai).

## License

MIT.
