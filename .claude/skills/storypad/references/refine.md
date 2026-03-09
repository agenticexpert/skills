# Refine

Iterate on an outline through multiple refinement lenses.


## Prerequisites

- A storypad must be open with existing sections and beats
- If no sections exist, redirect: "No outline to refine. Run `/storypad outline` first."


## Overview

Refinement applies focused lenses to the outline, each examining a different dimension. Run one lens at a time, or cycle through all five for a thorough review.

Update frontmatter: `status: refining`, `updated: {today}` on first refinement pass.


## Refinement Lenses

### 1. Audience Lens
**Question**: "Will this resonate with the target audience?"

- Review the `audience` field in frontmatter
- For each section, evaluate:
  - Does this address something the audience cares about?
  - Is the complexity level appropriate?
  - Will they understand the context, or does it need setup?
- Flag sections that assume too much knowledge
- Suggest reordering if the audience journey isn't smooth
- Check: Is there a clear value proposition in the Intro?

### 2. Pacing Lens
**Question**: "Does this flow well and hold attention?"

- Analyze section sizes (number of beats) and variety
- Flag problems:
  - Any section with 8+ beats (too dense — consider splitting)
  - Three or more similar sections in a row (monotony)
  - No variety in the first half (front-loaded boredom)
- Suggest section splits or merges to improve rhythm
- Evaluate the energy curve: does it build, plateau, or dip?

### 3. Story Lens
**Question**: "Is there a clear narrative arc?"

- Check for story structure:
  - **Setup**: Is the problem/question established early?
  - **Development**: Does each section build on the previous?
  - **Payoff**: Is there a satisfying resolution or takeaway?
- Identify missing beats:
  - No tension/conflict? Suggest adding stakes or challenges
  - No resolution? Suggest a clear conclusion section
  - No transformation? Show what changes from start to end
- Check transitions: does each section flow logically to the next?

### 4. Venue Lens
**Question**: "Does this work for the specific venue?"

- Load the venue file and check against its conventions
- For YouTube specifically:
  - Hook: Does the Intro create immediate curiosity?
  - Retention: Are there "pattern interrupts" to maintain watch time?
  - CTA: Is the call to action natural, not forced?
  - Thumbnailability: Is there a clear visual moment for a thumbnail?
  - SEO: Does the premise match searchable topics?
- Flag venue-specific anti-patterns

### 5. Series Lens (only for series episodes)
**Question**: "Does this fit within the larger series?"

- Only applies if `type: series-episode` in frontmatter
- Load `series.md` from the parent directory
- Check:
  - Does the episode honor its arc position (opener, develop, pivot, etc.)?
  - Are active continuity threads referenced or advanced?
  - Is there a callback to at least one previous episode?
  - Does the episode end with a hook for the next?
  - Are recurring elements included?
- Flag orphaned threads (active but not referenced in recent episodes)


## Refinement Output

For each lens, produce a brief report:

```
── Audience Lens ──────────────────────
 [pass] Clear value proposition in Intro
 [flag] "MCP" section assumes prior knowledge of tool calling
 [suggest] Add brief explainer beat before MCP details

── Pacing Lens ────────────────────────
 [flag] Tools section has 6 beats — consider splitting
 [suggest] Split into "Tool Basics" and "Wiring It Up"
 [pass] Good variety across sections
```

Use `[pass]`, `[flag]`, and `[suggest]` markers for scanability.


## Applying Changes

After presenting the refinement report:

1. Ask the user which suggestions to apply
2. For approved changes:
   - Update sections (reorder, split, merge, add/remove beats)
   - Add prep items if new dependencies are identified
3. Update frontmatter `updated` date
4. Run pipeline visualization to show the updated outline


## Iterating

Refinement is repeatable. Each pass may reveal new issues or confirm previous fixes. The user can:
- Run `/storypad refine` again for a fresh pass
- Run specific lenses by mentioning them: "refine with pacing lens"
- Mark the storypad as final when satisfied
