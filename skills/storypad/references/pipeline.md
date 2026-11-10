# Pipeline

One run from an idea to a cut. Run the steps in order without stopping, except where a step
stops.

1. Before the first command, tell the user which of these the run takes:
   - **Script:** the owner writes each scene's words, or the agent drafts them. The owner's words
     later → the run goes on and those scenes stay open.
   - **Files:** the user gives the shots' files now, or later from the tool that makes them. Later →
     the run stops after the per-shot prompts.
   - **Approval:** the ask approves takes up front ("use whatever comes out") → each take is
     approved as it is added (`take add --approve`). Otherwise the run lists the takes for review
     and waits.
2. A new subject → a new story (`references/new.md`); a story the ask names → that story.
3. Scenes: `references/outline.md` → **From the notes**, steps 1–4.
4. Script: `references/script.md`, steps 1–4, for each scene with no script, as step 1 chose.
5. Shots: `references/outline.md` → **Shots** → **Lay out the shots**.
6. A prompt for every shot: `references/pins.md` → **Prompts**. Files later → reply with each
   shot's id, name and prompt, ask for a file per shot, and stop.
7. Takes, shot by shot in story order: `references/pins.md` → **Takes** for each file the user
   gives. A shot with no file stays open. A file whose shot is unclear → ask which shot.
8. For review: reply with each shot's takes by id and file, and stop until the user picks; then
   `take approve` each pick.
9. `storypad.py cut <story>`. Reply with where the cut is, each shot it left black and each layer
   it left out.

## Keep going

"Keep going", "continue", "next" on a story already started:

1. `storypad.py todo <story>`.
2. A step is an open task a playbook does: a scene with no script → `references/script.md` when
   the owner asked for drafted words; a prompt marked for review → `references/pins.md` →
   **Prompts**; a problem on the cut → `references/outline.md` → **Shots**. Exactly one step → do
   it, then `todo` again. More than one → name them and ask which.
3. Stop and ask for what only the owner gives: their words for a scene, a file for a shot or layer,
   a pick among takes, or a box checked as made.
4. Never add a scene, shot, prompt or take that `todo` or `show` already lists.
