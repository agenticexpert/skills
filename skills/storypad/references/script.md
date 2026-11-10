# Script

Write each scene's words the audience hears (narration, dialogue, on-screen lines) into its
`## Script`, from the owner or as the agent's draft. Never record or generate the narration's
audio.

1. Read `index.md` (premise, audience, target length, Notes and its active `Decided:` lines,
   Scratchpad), the venue's vocabulary and conventions in `venues/<venue>.md`, and each scene
   file the ask names, else each one whose `## Script` is empty.
2. Ask who writes it, unless the ask says: the owner, or the agent.
   - **The owner:** write their words into the scene's `## Script` as given. Words they give
     later stay out until then; the scene stays open in `todo`.
   - **The agent:** draft from the scene's beats in order, the Scratchpad's lines for that scene,
     and the scenes on either side, in the venue's voice and paced to the target length.
3. Write only into `## Script` of `scenes/<File>`. A script already there is the owner's: change it
   only on their ask, and then only the lines they name.
4. Run `storypad.py sync`, then `todo <story>`.
5. Reply with each scene written, by number and name, an agent's draft quoted for the owner to
   approve or change, and each scene still without a script.
