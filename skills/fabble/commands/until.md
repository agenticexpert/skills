---
description: Elevate an ask into a goal — a self-contained prompt whose one-run execution achieves it. Targets Fable 5 by default; open the arguments with `opus` or `sonnet` to retarget.
argument-hint: "[opus|sonnet] <the ask to elevate>"
---

Invoke the fabble skill and work from its promptify playbook (`.claude/skills/fabble/references/promptify.md`). $ARGUMENTS is the intent to elevate; produce the prompt whose execution achieves it. Target = Fable 5 unless the arguments open with `opus` or `sonnet` — then target that model and apply the Opus/Sonnet deltas (`.claude/skills/fabble/references/opus-behavior.md`).
