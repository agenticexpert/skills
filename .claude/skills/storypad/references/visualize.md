# Visualize

Generate and display ASCII visualizations for storypads and series.


## Prerequisites

- A storypad or series must be open (storypad.md or series.md loaded in context)
- If nothing is open, prompt: "No storypad loaded. Use `/storypad open {name}` first."


## Determine View

Parse: `/storypad visualize [--table|--gantt]`

- No flag → **pipeline** (default)
- `--table` → **table** view
- `--gantt` → **gantt** view


## Scripts

All scripts live in `.claude/skills/storypad/scripts/`.

### Pipeline (default)
```bash
python3 .claude/skills/storypad/scripts/pipeline.py {path-to-storypad.md}
python3 .claude/skills/storypad/scripts/pipeline.py {path-to-series.md} --series
```
Shows: horizontal pipeline bar with prep dependencies dangling below, followed by expanded section detail with beat and prep checklists.

### Table
```bash
python3 .claude/skills/storypad/scripts/table.py {path-to-storypad.md}
python3 .claude/skills/storypad/scripts/table.py {path-to-series.md} --series
```
Shows: compact tabular summary with beat counts, prep counts, and mini progress bars.

### Gantt
```bash
python3 .claude/skills/storypad/scripts/gantt.py {path-to-storypad.md}
python3 .claude/skills/storypad/scripts/gantt.py {path-to-series.md} --series
```
Shows: roadmap-style Gantt chart with sections as rows and progress bars.


## Display and Save

1. Run the selected script and capture output
2. Display the output to the user
3. Save the output:
   - Single storypad: `{storypad-dir}/viz/outline.txt`
   - Series: `{series-dir}/viz/outline.txt` (create `viz/` if needed)
4. Confirm: "Visualization saved to {path}"


## Rules

**CRITICAL: Never render ASCII visualizations manually. Always use the scripts.**

- Default to pipeline view unless the user requests otherwise
- After creating an outline (`/storypad outline`) — auto-visualize with pipeline
- After refining (`/storypad refine`) — auto-visualize with pipeline
- On explicit request (`/storypad visualize`) — use requested view or pipeline
- Never auto-visualize during brainstorming (no sections to visualize)
