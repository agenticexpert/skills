---
name: mem
description: Durable conversation memory — structured summaries that survive /clear and compaction, hand off between agents and sessions, split into threads, and rejoin. Activate for summarizing or checkpointing a session, continuing from a checkpoint, capturing an idea thread, activating semantic triggers, or reviewing decisions, requirements, todos, keys, or references.
license: MIT
---

# Mem Skill

Memory management using LLM context. Creates durable, structured summaries that survive `/clear` and compaction, hand off to other agents, resume, split, and rejoin.

**Data root: `.agents/mem/`**

```
.agents/mem/
  mem.md          project augment — extends or replaces the default format (optional)
  summary/
    SUMMARY.md    current checkpoint
    archive/      rotated summaries and exports
    .prune_log    topics to remove at next summarize
  ideas/          split ideas
  logs/           trigger logs (decisions.md, keys.md, references.md, requirements.md, todos.md)
  triggers.md     live-trigger block — written by trigger on/off, re-injected by the compact hook
  transcripts/    raw conversation archives, timestamped ({ts}.jsonl) — auto-written by the SessionEnd hook
```

## Subcommands

Match the command, load the playbook, execute it fully.

| Command | Playbook |
|---|---|
| `/mem summarize [to {path}] [using {augment}] [from {source}]` | references/summarize.md |
| `/mem prune {topic}` | references/summarize.md → Pruning |
| `/mem continue [decide] [from {path}]` | references/continue.md |
| `/mem split {idea} [to {path}] [and prune]` | references/split.md |
| `/mem trigger {name} [to {log-path}] [using {path}]` / `trigger off {name}` / `off all` / `trigger list` | references/trigger.md |
| `/mem decide` | references/decide.md |
| `/mem decisions` / `requirements` / `todos` / `keys` / `refs` | references/logs.md |
| `/mem install` | references/install.md |

Bare `/mem` and `/mem summary` alias `summarize`. `/mem capture` aliases `split`.

## Always

- Strict chronological order: start → current, previous summaries first. Later information supersedes earlier — keep both, mark the supersession.
- Preserve code, commands, errors, and exact user questions verbatim. Never paraphrase artifacts.
- The summary spec and slot language live in references/summarize.md — the source of truth. The default format is references/default-summary.md, composed from the section definitions in references/default-sections.md — one file, one read.
