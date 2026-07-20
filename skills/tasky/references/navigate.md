# Navigate Playbook

The user wants to know where things stand. Answer with data from scripts. Never guess state from memory — always run the appropriate script.

All scripts live at `.claude/skills/tasky/scripts/`.

---

## Noun → Script (Mandatory Mapping)

Match every hierarchy noun the user names — **project, roadmap, track, milestone, task** — to the script below. Resolve missing or ambiguous args first per **Resolving References**. "Drill into X" and "show X's children" are the same view — that's why pairs share a script.

| User says (singular or plural) | Script | The view |
|---|---|---|
| "the **projects**" | `view_projects.py` | every project, each with its roadmaps table |
| "the **project**" / "the **roadmaps**" | `view_projects.py <project>` | one project's roadmaps |
| "the **roadmap**" / "the **tracks**" | `view_tracks.py <project> <roadmap>` | tracks with rollup status and progress count; no milestones shown |
| "the **track**" / "the **milestones**" | `view_milestones.py <project> <roadmap> <track>` | the primary track view — a Gantt of milestones in sequence; concurrent milestones share a slot; progress bar anchored to slot columns |
| "the **milestone**" / "the **tasks**" | `view_tasks.py <project> <roadmap> <track> <milestone>` | tasks with status, criteria completion, dependency state |
| "the **task**" | `Read <root>/<project>/<roadmap>/<track>/<milestone>/<task>.md` | the `.md` file is the source of truth — title, status, deps, criteria, instructions |

**Rule:** the noun the user named selects the script — regardless of how close another view might seem.

---

## Resolving References

This procedure applies wherever a name resolves — viewing, creating, renaming, moving.

Every script call — view, create, move, or rename — needs the right args (project, roadmap, track, milestone, task). When the user names a singular noun ("the track") or a plural that implies a parent scope ("show the tracks" → which roadmap?), resolve each missing or ambiguous arg in order:

1. **Already named.** Use the slug the user already mentioned in this conversation.
2. **Single instance.** If only one option exists at that level, use it. Does not apply to the *new name itself* in a create or rename. Parent args still resolve by single instance.
3. **Discovery.** Run `view_all.py` — or `view_all.py --status doing` when looking for what's currently active — to surface candidates, and fuzzy-match the user's term against existing slugs.
4. **Surface.** Tell the user which slug you resolved to: *"I'm treating 'the milestone' as `security`"* (per the SKILL.md "Always" rule).
5. **Resolve.** Resolve by best match and state the assumption. In a create or rename, the *target* name having no existing match means it is a **new** slug — slugify it and proceed. The item being renamed still has to resolve to something real. Two or more equally-valid referents with no basis to prefer one → ask: *"Did you mean X or Y?"* That is the genuine-ambiguity case SKILL.md → **Deciding** rule 4 exempts; every other resolution proceeds.

Then run the script with the resolved slugs.

---

## Default (No Noun Named)

If — and only if — the user gives no hierarchy noun ("what's going on?", "give me a status", "where are we?"), run the full tree:

```
python .claude/skills/tasky/scripts/view_all.py
```

**Flags** (`view_all.py` unless noted):

- `--status <list>` — filter rows at all levels to matching status; also expands tasks for matching milestones. Use `all` to show everything including tasks.
- `--hide <types>` — suppress children of done parents. Values: `tasks,milestones,tracks,roadmaps`. Default: `milestones`.
- `--all` — on any view script: reveal focus-hidden items, marked `~`. Totals always include hidden items regardless — `--all` only affects which rows are shown. The full hide list is `project.json["focus"]["hide"]`.

---

## Question → Command

| Question | Command |
|---|---|
| What's active right now? | `view_all.py --status doing` — if nothing is DOING, show PENDING next |
| What's next? | `view_all.py --status pending,ready,doing` — in progress, ready to start, pending; respects the full hierarchy including track-level deps |
| What's blocked? | `view_all.py --blocked` — compact text: task slug, location, unmet deps |
| What's hidden / in focus? | any view script with `--all` |
| Dependency graph | `view_deps.py <project> <roadmap> [<track> [<milestone>]]` — ASCII tree with status char, seq, and slug; more args narrow scope: roadmap → track deps, +track → milestone deps, +milestone → task deps |

---

## "What are the next tasks?" (Report)

**Triggers:** "what are the next tasks", "show me the next tasks", "next tasks", "next tasks report"

**Not this:** "show the tasks" / "view tasks" → use `view_tasks.py` (diagram). That stays unchanged.

Steps:

1. Determine the **current thread** from conversation context — which milestone is in focus. If ambiguous, use the one with DOING tasks; with none, the most recently discussed thread.
2. Read task states for the current thread: `view_tasks.py <project> <roadmap> <track> <milestone>`
3. Get the broader picture for other open fronts: `view_all.py --status doing,paused,ready,pending`
4. Classify tasks from the `view_tasks.py` output:
   - **Ready now** = status PENDING + no unmet deps shown
   - **Stubs** = status TODO (need `tasky define` before they can run, regardless of deps)
   - **Blocked** = has unmet deps listed; include the blocking dep names
5. **Synthesize as formatted text report. Do NOT paste raw script output.**

**Output format:**

```
Ready now (PENDING, no blockers, fully specced):
  1. <slug> — <one-line description>
  2. ...

Stubs (TODO — need tasky define before run):
  3. <slug> — <one-line description>
  4. ...

Blocked (TODO, gated):
  5. <slug> — deps: <dep1> + <dep2>
  6. ...

So next runnable = #<n> <slug>[, then #<m> <slug>]. <one sentence of context>.

---

Other open fronts (not the current thread):
- <roadmap>/<track> (<done>/<total>) — <active task or brief status note>
- ...
```

Numbers run sequentially across all three sections. Omit any section with no items. Descriptions are one line — task title or slug only, no elaboration. "Other open fronts" shows tracks outside the current thread that have non-DONE work.

---

## Interpreting Results

Present results plainly. Don't over-narrate. If the user asks "what's next?" give them the next task and its milestone/track context — one thing, not a list of options.

If there's nothing DOING and nothing unblocked, surface that directly:
> "Everything is blocked. The next unblocked item is `{slug}` in `{track}` — but it's waiting on `{dep}`."

If the project is empty or has no tasks yet, say so plainly and name the single next action — decomposing the work into tracks and milestones, which routes to `plan.md`, or `brainstorm.md` when the idea is still fuzzy. State it as the next step, not as an offer among options.
