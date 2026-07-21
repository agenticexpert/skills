# Setup Playbook

No `tasky.md` was found (checked `.agents/tasky/tasky.md`, then repo-root `tasky.md`). This is a first-time setup. Greet the user and walk through configuration.

---

## Greeting

Say something like:

> Welcome to Tasky. I don't see a `tasky.md` config file yet. Let me help you set one up — it only takes a moment.

---

## Step 1 — Choose a Root Directory

Ask:
> Where do you want to store your project data? This is the directory where all your projects, roadmaps, milestones, and tasks will live.
>
> Common choices:
> - `.agents/tasky` — default; tasks alongside your code
> - `tasks` — at repo root
> - `.tasks` — hidden directory

Wait for the user to decide. Suggest a default if they're unsure: `.agents/tasky`.

---

## Step 2 — Write tasky.md

Preferred location is `.agents/tasky/tasky.md`. Create the directory first if needed, then write the file:

```
mkdir -p .agents/tasky
```

`.agents/tasky/tasky.md`:

```markdown
root: {chosen-path}
```

A repo-root `tasky.md` is also recognized as a fallback. Tell the user the file was created and what it does.

---

## Step 3 — Create the Root Directory

Run:
```
mkdir -p {chosen-path}
```

---

## Step 4 — Augment CLAUDE.md

Tasky's `SKILL.md` only loads when `/tasky` is invoked, and the compactor is not guaranteed to preserve it. CLAUDE.md is always in the system prompt — the only Claude-Code-documented mechanism for surviving compaction.

1. Check whether `CLAUDE.md` exists at the repo root.
   - If yes → append the block (after a blank line if the file doesn't already end with one).
   - If no → create `CLAUDE.md` with just this block.

2. Insert the block below, with `{root}` replaced by the actual `root:` value from `tasky.md`:

```markdown
<!-- tasky:compact-instructions:start -->
## Compact Instructions

Route every action on the data root (`{root}/`) through a `references/*.md` playbook under `.claude/skills/tasky/`. "Create a task" / "track this as work" → `structure.md`, even mid-flow on another task. Before the first action that changes a file or produces a deliverable, or on an ask reporting work finished or ticking a criterion, run the Tracked-Work Check in `navigate.md`. On a match, route through `execute.md`. Never create a task; that is `structure.md`. Two or more equal matches → ask which.
<!-- tasky:compact-instructions:end -->
```

3. If `CLAUDE.md` already contains a `tasky:compact-instructions` block, replace the content between the markers (keep the markers themselves). Never duplicate or append a second block.

---

## Step 5 — Offer to Create the First Project

Ask:
> What's the first project you want to work on? I can create the structure now, or you can do that when you're ready.

If they give a name → hand off to `structure.md` to create the project.
If they want to wait → tell them they're set up and can start any time.

---

## Notes

- `tasky.md` can also hold a flows registry and project-wide default flow. See `flow.md` for details.
- The root directory can be anything — it doesn't need to be inside `agents/`.
