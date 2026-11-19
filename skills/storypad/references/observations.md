# Video observations

Shot, transition and timing choices for product and UI videos, measured from studied references, with rules drawn from them and a vocabulary of named effects; storypad reads it when laying out shots and transitions.

Timings come from the Euzy frame timestamps (12 fps capture, so ±0.08 s). Sampled at 3 fps across each recording, plus 12 fps runs over the key transitions. "~" marks an estimate. Easing is read from position and scale steps between frames, so it is estimated too.

LIVE and HERO were added 2026-11-17. They were probed with ffprobe (both 30 fps, video only, no audio stream). Frames were extracted with ffmpeg at 3 fps across each whole video (timings ±0.17 s, marked "sheet") and at the full 30 fps over each transition (±0.03 s, the default for these two).

Tags: **L1**, **L2**, **L3** = the product-tile loop recordings, **APP** = the full-app showcase recording. **P1–P12** = the page screenshots. **LIVE** = a live-support product film. **HERO** = a product hero loop.

Every observation starts with a bold name: the standard motion-design, UI-animation or film-editing term where one exists, otherwise a plain descriptive name marked "(our name)". The **Vocabulary** section at the end lists every name with its source.

## The references

| Ref | What it is |
|---|---|
| L1 | Dialpad product-tile loop, 11.2 s, portrait tile, captioned "Assist / Realtime AI or manager help". A "Live Status" pill types itself in, scales up and dissolves into an "Assist" table card. The table's rows arrive one at a time, it holds, fades out, and the loop repeats (cycle ~5.3 s). |
| L2 | Dialpad tile loop, 10.6 s, "AI Workers / Execute complex workflows". A carousel of template cards scrolls sideways. The background washes purple and one card ("Conversation Research") is singled out, scales up and dissolves into its own chat. In the chat a question is asked, a "Thinking…" pill appears, two step chips arrive, an answer list replaces the chips with "View full report", and it all fades back to the carousel. |
| L3 | Dialpad tile loop, 15.4 s, "AI Virtual Agents / From triage to resolution". A chat agent "Kate" resolves an exchange and gets an "Exchange confirmed" chip. Then a voice card "Lisa" plays a live waveform, a transcript is revealed word by word, an orange "Account lookup" action pill types in, two step chips arrive, and a black "Case logged ✓" chip ends it. Then back to Kate (cycle ~11.3 s). |
| APP | Dialpad full-app showcase, 14.9 s, landscape. The whole desktop app sits on a halftone-dot backdrop and cycles three screens (Contact Centers inbox → AI Live Coach on a live call with a dark call bar → AI Agents table) with plain cross-dissolves, ~4 s each. No camera moves. |
| P1 | Close crop of an agent graph: an AI Agent node joined by thin connectors to three Skill nodes and a Workflow node. Large type, white cards, grey hairline borders. |
| P2 | Close crop of a "Test Results" card: three result rows, each with a check or cross icon, a bold title, 2–3 lines of body and tag chips. |
| P3 | Close crop: a question in large type, a pill "✓ Collecting interaction data" with a lime check disc, and a "Skill usage" card with four gradient bars and big numbers. Deep soft shadows. |
| P4 | Dialpad /ai-agent page, step 1 of 4 ("Find the work worth automating"). The left side is a stepper with a thin progress bar under the active heading (~10 % filled). On the right, the P3 animation is mid-build: the bar card is still an empty skeleton panel and the "…" loader is showing. |
| P5 | Same page, step 2 ("Build the agents that do the work"), progress ~18 %. The agent graph is shown without its Workflow node. |
| P6 | Same as P5 with progress ~55 %. The Workflow node has now arrived: the graph builds as the step's bar fills. |
| P7 | Step 3 ("Test it before a customer does"), progress ~35 %: the Test Results card. |
| P8 | Step 4 ("Govern the work as it happens"), progress ~88 %: a Conversation Transcript card with tool-call tags ("Exit skill · Book new appointments", "Workflow triggered · Payments"). |
| P9 | "Generative AI, governed." section: the AI Agents table card floats on a halftone-dot panel with ~13 % margin. |
| P10 | "Begin where the last interaction ended." A full app window (agent canvas: three nodes in a row) centred on the page with a soft shadow, mostly empty canvas. |
| P11 | Three tiles (Insight / Assistance / Automation). Each has one card on a coloured dot field and an **outcome pill overlapping the card's bottom edge** ("Refund processed", "Duplicate charge reversed", "Lab test scheduled"). |
| P12 | /ai-contact-center tiles: one card per tile (CSAT 97 %, Dialer table, AI Live Coach with a highlighted "Tracking Number: ALX47293" span, an Agent coverage chart). |
| LIVE | Live-support product film, 62.0 s, 1920×1080, 30 fps, no audio. It is not a loop. A caller's problem, in one spoken line, is revealed under a live waveform on a dark warm stage. Then the product's live call card, tilted in 3D, builds row by row while the camera cuts between wide and close framings: a symptom logged, a cause ruled out, an AI-suggested check, the caller's reading, a file sent to the caller, the root cause, a fix walked through. A summary card fills in and is closed. It ends on the caller's thanks, in one spoken line, and the product logo. |
| HERO | Product hero loop, 37.9 s, 2560×1440, 30 fps, no audio. An insurance-renewal board ("Good morning, Marcus") wipes in from a solid blue field, and the camera pushes in on one client card (Greg & Carol Whitmore). A scripted cursor walks the card through outreach, a customer questionnaire on a phone mock-up, a quote comparison in a side sheet, the customer's typed reply and close-out. The card moves column by column to Completed, a small particle burst plays, and the camera pulls back and loops. |

The 16 Dialpad references are marketing material from dialpad.com. The Dialpad recordings have no input events (empty action index), so they are autoplaying animations, not someone driving the app. LIVE and HERO are rendered video files. The cursors in them are drawn into the animation, not recorded input.

## Observations

### Motion & camera

1. **Locked-off shot** — The camera does not move inside an animation. In L1, L2, L3 and APP the frame never pans or zooms across a UI. The tile is fixed, and motion comes from components entering, leaving or growing in place. [L1 L2 L3 APP] *LIVE and HERO disagree: LIVE's virtual camera drifts and cuts between framings (41, 46), and HERO pushes in, pans and pulls back (44, 45).*
2. **Rise-and-fade entrance (our name), ease-out** — Elements enter by rising and fading. In L3 the Lisa card goes from ~0 % to full opacity while rising ~40 px (of a 1052 px-tall tile) over ~0.42 s (4.63 → 5.06 s). It decelerates into place, which reads as ease-out (est.). [L3 HERO] *HERO's phone mock-up enters the same way (51).*
3. **Drift-up exit (our name)** — Elements leave by drifting up and fading. The Kate card fades to ~0 while drifting up ~25 px over ~0.33 s (4.05 → 4.38 s), and its dark header greys out first. The same exit closes the Lisa sequence (11.06 → 11.73 s). [L3]
4. **Fade through (scale variant)** — The "Live Status" pill grows 1.0 → ~1.4× over ~0.25 s (3.47 → 3.72 s), speeding up (ease-in, est.), and dissolves as it grows. The incoming table card starts ~5 % larger and blurred under a warm gradient wash, then settles to 1.0 over ~0.35 s (3.80 → 4.14 s). [L1]
5. **Container transform** — Focus pull on a chosen item. The carousel scrolls left steadily (~1 card per 0.5 s). The background washes from warm grey to a purple gradient in ~0.17 s (8.21 → 8.38 s). The chosen card centres while its neighbours fade, scales up ~1.08× (8.38 → 9.07 s), then dissolves (~0.33 s) into its own detail view. [L2]
6. **Live signal (our name)** — Live data motion stands in for "it's listening". In L3 the waveform bars draw in from the left over ~0.7 s and keep pulsing during the hold. A three-dot typing indicator runs for ~1 s before the agent's reply. [L3 LIVE] *LIVE's waveform pulses with the caller's speech and flattens in the pauses (69).*
7. **Self-driving UI (our name)** — No cursor appears in any animation. Nothing is clicked or typed by a visible hand. [L1 L2 L3 APP] *LIVE and HERO disagree: both show a staged cursor (60).*

*From LIVE and HERO:*

41. **Ken Burns drift (virtual camera drift)** — Every LIVE shot is a tilted 3D view of one card that keeps creeping: the card slides and grows a few percent across each 2–6 s shot. For example, the wide shot from 10.0 to 13.7 s (sheet) rises and grows ~3–8 % of the frame (est.). The camera is never still, but it never moves fast enough to read as a move. Disagrees with item 1. [LIVE vs L1 L2 L3 APP]
42. **Perspective tilt (2.5D card) (our name)** — LIVE shows the UI as a flat card rotated in 3D. It rises ~3–4° to the right (est.) with perspective, and the near edge is larger: from the call bar's entry at 6.43 s onward. Close-ups tilt harder than wide frames. [LIVE]
43. **Shallow depth of field** — In LIVE close-ups (from 14.00, 19.80, 27.60, 33.43 and 47.40 s) the card's far edge (the older rows at the top) is blurred while the newest row is sharp, so the eye lands on the new line. [LIVE]
44. **Push-in / pull-back** — HERO opens wide on the full app. It pushes in ~1.6× (est.) over ~0.40 s (2.73 → 3.13 s), easing in and out (est.), onto the first board column. It stays at that zoom for the whole story, then pulls back to the wide view over ~0.6 s (35.80 → 36.40 s), decelerating (ease-out, est.). Disagrees with items 1 and 8. [HERO vs L1 L2 L3 APP]
45. **Follow pan** — When a card moves to the next board column, HERO's camera pans after it in ~0.3 s (12.9 → 13.1 s and 28.5 → 28.8 s, sheet), so the card keeps its place in the frame. [HERO]

### Zoom

8. **Push-in (absent)** — None of the Dialpad references uses a camera zoom (punch-in). The only scale changes are on one element: the pill's 1.4× scale-through (L1) and the selected card's ~1.08× lift (L2). [L1 L2] *LIVE (cut-ins, 46) and HERO (push-in, 44) both change the framing.*
9. **Isolation framing (our name)** — Emphasis by isolation instead of zoom. Each tile shows one component at a legible size, so nothing needs a zoom to be read. The page screenshots crop to one component (P1, P2, P3) or float it on a backdrop. [L1 L2 L3 P1–P3 P9 P11 P12 LIVE] *LIVE isolates one card too, but its close-ups crop into it (47).*
10. **Establishing shot** — Where a full app screen is shown, it stays wide and still (APP holds ~4 s per screen with no zoom; P10 shows the whole window). This is the one place the references disagree with item 9: whole-screen context (APP, P10) versus isolated components (the rest). [APP P10 vs L1 L2 L3 P11 P12] *HERO takes the APP side but only for its opening and closing ~1.5–1.8 s, and pushes in for everything between (44, 72).*

*From LIVE and HERO:*

46. **Cut-in / cut-out (axial cut)** — LIVE changes the framing of the same card with hard cuts, not a zoom move. Close → wide at 9.20 s, wide → close at 14.00, closer at 19.80, wide at 22.80, close at 27.60, close at 33.43, wide at 37.20, close at 47.40, and closer at 50.80 s. Wide frames give context and close frames make one line legible. The two alternate. Disagrees with items 8 and 11. [LIVE vs L1 L2 L3 APP]
47. **Full-bleed crop (our name)** — In LIVE close-ups the card runs off the frame on two or three sides (14.00–19.80 s, 27.60–30.0 s, 47.40–50.80 s). The camera crops mid-card and does not try to show the whole component. Body text is ~2× its size in the wide frames (est.). [LIVE]

### Transitions

11. **Hard cut (absent)** — No hard cuts. Every state change is a dissolve, a fade-and-drift or a scale-through. [L1 L2 L3 APP] *LIVE disagrees: it hard-cuts between framings of the same card (46). It keeps soft transitions between different subjects (48). HERO's loop seam is a hard cut (54).*
12. **Cross-dissolve** — A cross-dissolve between whole screens takes ~0.17–0.25 s (APP: 2.63–2.80 s, 6.58–6.75 s, 10.62–10.80 s, 14.67–14.76 s). [APP]
13. **Dip to background (empty beat)** — Exit, empty beat, enter. A brief near-empty frame of ~0.2–0.33 s separates sequences (L3 4.46–4.63 s; L1 2.04 s is fully empty before the pill). [L3 L1 LIVE] *LIVE agrees: empty beats of ~0.1–0.35 s (48).*
14. **Shared-element transition** — Transitions carry meaning. The thing named becomes the thing shown: the pill labelled "Live Status" grows into the Live Status table (L1), and the "Conversation Research" card grows into the Conversation Research chat (L2). [L1 L2 HERO] *HERO's card carries the deal from column to column (52).*
15. **Colour wash (our name)** — A colour wash marks a mode change. A full-tile gradient (purple in L2, warm cream in L1) appears only during the hand-off and clears once the new state has settled (~0.3–0.7 s). [L2 L1]

*From LIVE and HERO:*

48. **Dip to background between subjects** — LIVE still separates different cards with a fade-out, an empty beat and a fade-in. Examples: the file card (old card gone at 30.20 s, empty to 30.30, new card at ~30 % opacity at 30.33, full by ~30.6); the waveform after the closed state (card fading 52.9 → 53.20, waveform from 53.23); the logo (quote fading 57.27 → 57.6, empty to 57.83). Empty beats last ~0.1–0.35 s. This agrees with item 13. Hard cuts are kept for a new framing of the same card (46). [LIVE L3 L1]
49. **Wipe** — HERO opens on a solid brand-blue frame (0–0.17 s). The white app body wipes in left → right below it in ~0.17 s (0.20 → 0.37 s). [HERO]
50. **Modal side sheet with scrim** — HERO opens a record as a sheet that slides in from the right in ~0.1 s (3.87 → 3.97 s) and covers the right ~half of the frame, while the board behind greys under a scrim (~30 %, est.). The sheet slides back out in ~0.17 s (6.20 → 6.37 s). [HERO]
51. **Device mock-up pop-over (our name)** — HERO shows the customer's side as a phone mock-up. It rises from below in ~0.2 s (7.53 → 7.73 s), decelerating (ease-out, est.), while a darker scrim (~45 %, est.) covers the board. It drops back out the same way (~12.3 s and ~27.7–28.0 s, sheet). [HERO]
52. **Shared-element transition across lists** — When the deal's stage changes, the same card travels from one column to the next as a ghost at ~50 % opacity in ~0.25 s (33.73 → 33.97 s), then lands with its new text. [HERO]
53. **Collapse-to-point exit (our name)** — LIVE's opening quote fades (5.53 → 5.80 s), then the waveform shrinks sideways to a dot and fades (5.67 → ~6.40 s). The next element (the call bar) enters elsewhere, at 6.43 s. [LIVE]
54. **Hard-cut loop seam** — HERO's last wide frame (37.9 s) cuts straight to its first solid-blue frame, and the loop restarts with the wipe (49). This agrees with item 39 (it loops), but the seam is a cut. [HERO]

### Morphs

55. **Skeleton-to-content morph** — LIVE's call bar arrives as a blank grey bar (6.43 s) and turns white (6.53 s). Then its label, timer, name and number fade in (6.60 → ~7.33 s). The summary card enters as a titled grey panel (42.33 s, sheet) and fills row by row. HERO's board columns show as empty shells (0.43 s) before their cards appear. Agrees with item 25. [LIVE HERO L1 L3 P4]
56. **Container expand (our name)** — The LIVE live card grows downward to make room for each new row: 9.53 → ~9.80 s for the first row (~0.27 s, ease-out, est.). The new row fades in while the card grows. The card never jumps in size. [LIVE]
57. **Button state morph (our name)** — Clicking turns the button itself into its result. A white outlined send button becomes its green "sent" state on the click frame at 28.87 s, and the colour settles over ~0.1 s. The close button cross-fades to a dark "closed" state with a check in ~0.07 s (52.07 → 52.13 s). There is no toast and no separate confirmation. [LIVE]
58. **Field-to-header morph (our name)** — During HERO's opening wipe (49) the solid blue field that filled the frame stays on as the app's header band ("Good morning, Marcus"). [HERO]
59. **Strike-through rule-out (our name)** — A ruled-out cause is struck through and greyed in place (11.33 s, sheet), ~0.7 s after its row arrived (10.67 s). A ruled-out cause changes the existing row instead of adding a new one. [LIVE]

### User interaction

60. **Staged cursor (our name)** — Both new videos show a cursor driving the UI, which disagrees with item 7. In LIVE the cursor appears only for the two actions the agent takes (sending a file and closing the case), and everything else changes on its own. In HERO every step is clicked, even on the phone mock-up, where the same arrow pointer taps instead of a finger. [LIVE HERO vs L1 L2 L3 APP]
61. **Cursor travel, dwell, click (our name)** — The LIVE cursor enters from below-right ~0.13 s after a cut. It travels ~0.8 s to its button on a curved path, decelerating (ease-out, est.): 27.73 → 28.53 s and 50.93 → 51.70 s. It dwells ~0.33 s on the target (28.53 → 28.87 s; 51.70 → 52.07 s), then clicks, and the state change lands on the click frame. The cursor stays on the button through the hold and fades with the card in ~0.1 s (29.93 → 30.0 s; 52.9 → 53.0 s). [LIVE]
62. **Typewriter effect (simulated typing)** — HERO's reply "Great, let's go with Travelers" types into the phone at ~26 characters/s (25.23 → 26.43 s). That is faster than item 21's ~10–15 chars/s. The cursor hovers over the keyboard without tapping keys. [HERO vs L1 L2 L3]
63. **Click cadence (our name)** — HERO lands ~11 clicks in ~30 s (sheet): card ~3.6, save ~5.7, review ~15.2, pick ~20.3, continue ~21.0, send ~22.0, reply ~24.3, send ~26.8, close-out ~31.3, outcome ~32.3, close ~33.0 s. That is roughly one click every 1–3 s. The questionnaire screens advance ~1 s apart (9.67 → 11.67 s). [HERO]

### Pacing & holds

16. **Staggered entrance** — Rows and chips arrive one at a time at ~0.33 s apart (L1 table rows: 4.72, 5.05, 5.32, 5.66 s). Chips arrive ~0.33–0.67 s apart (L2: "786 conversations found" 3.08 s, "Analyzing…" 4.08 s; L3: 8.45, 9.11, 9.78 s). [L1 L2 L3 LIVE] *LIVE's summary rows agree. Its live call rows do not: they follow the conversation (64). HERO's board stagger is tighter (65).*
17. **Fade-in** — Each new element fades in over ~0.25–0.33 s, starting at ~20–30 % opacity in the first frame. [L1 L2 L3 LIVE]
18. **Hold** — The finished state holds ~1.0–1.9 s before the exit. Measured holds: L1 table complete → fade ~1.0 s (twice); L2 answer → fade ~1.35 s; L3 "Exchange confirmed" → fade ~1.9 s; L3 "Case logged" → fade ~1.3 s. [L1 L2 L3 LIVE HERO] *LIVE and HERO agree (66).*
19. **Long hold (establishing)** — Full-screen holds are longer, ~3.9–4.0 s each (APP). They carry a whole app screen, not one component. [APP]
20. **Reveal rate (our name)** — Event rate. About 0.7–1.3 reveals per second (L1 ~7 reveals in 5.3 s; L2 ~8 in ~7 s; L3 ~9 in ~11 s). Something changes at least every ~1 s outside the end holds. [L1 L2 L3 HERO] *LIVE is slower, with 1–6 s between reveals during the call (64).*
21. **Typewriter effect / word-by-word reveal** — Short text types in. Pill and button labels type in at ~10–15 characters per second ("Live Status" over ~0.4 s; "Account lookup" over ~0.7 s, 7.44 → 8.11 s). A spoken transcript line is revealed word by word, ~5 words in ~0.7 s ("I was double charged for June.", 5.75 → 6.42 s). [L1 L2 L3 LIVE] *LIVE agrees for speech (69). HERO's typing is faster (62).*

*From LIVE and HERO:*

64. **Dialogue-paced reveal (our name)** — LIVE's live call rows arrive when the conversation supports them, not on a fixed stagger (sheet): the logged symptom 9.53 s, a ruled-out cause 10.67, the AI's suggested check 14.23, the caller's reading 20.0, the likely cause ~23.3, a next check ~24.3, the root cause ~35.7 s. They are 1–6 s apart. This disagrees with item 16 for conversational content. The summary card is a summary and keeps item 16's stagger: rows at 42.67, 43.0, 43.33, 44.0, 44.33 s (~0.33 s apart). [LIVE vs L1 L2 L3]
65. **Staggered entrance (tight)** — HERO's four board columns fill left → right in ~0.5 s (0.43 → ~0.90 s), ~0.1 s apart. Many small items get a much tighter stagger than item 16. [HERO]
66. **Hold** — LIVE's UI states hold 0.8–1.8 s before the next change: file sent 29.0 → 30.0 s; file received 31.67 → 33.43; root cause 35.67 → 37.20; fixed 45.67 → 47.40; closed 52.07 → 52.9 (sheet values ±0.17). Spoken quotes hold longer: the opening line ~3.2 s (2.33 → 5.53 s) and the closing line ~2.3 s (~55.0 → 57.27 s). HERO's opening wide holds ~1.8 s (0.9 → 2.73 s) and its closing wide ~1.5 s (36.4 → 37.9 s). Agrees with item 18. [LIVE HERO L1 L2 L3]
67. **Average shot length** — LIVE shots run 2.1–5.8 s, ~4 s on average. Shots start at 6.43, 9.20, 14.00, 19.80, 22.80, 27.60, 30.33, 33.43, 37.20, 42.0, 47.40, 50.80 and 53.23 s. This matches APP's ~4 s screens. [LIVE APP]
68. **Time-lapse counter (our name)** — LIVE's call timer runs ~13× real time (02:41 at 9.0 s → 02:56 at 10.17 s). A long call fits in a one-minute film and still reads as live. [LIVE]
69. **Word-by-word reveal (speech rhythm)** — LIVE reveals the caller's line word by word at ~7 words/s, in bursts. There is a ~0.5 s pause at the clause break (1.07 s → 1.57 s), and the waveform flattens during the pause. Each word lands grey (~40 %) and brightens to white in ~0.1 s. The closing quote does the same (from 53.73 s). The line's last word is visible from the first frame (0.03 s), ahead of the words before it, which may be a layout artifact. Agrees with item 21. [LIVE L3]

### Proportions & placement

70. **Centred voice frame (our name)** — In LIVE's quote shots the waveform is ~40 % of the frame width, centred at ~0.40 of the height. The quote's two lines are centred at ~0.62 and ~0.70 of the height, and the longer line is ~48 % of the width. Nothing else is in the frame. [LIVE]
71. **Card scale in frame** — In LIVE's wide frames the call bar and live card are ~70 % of the width (9.2–14 s), the tall live card ~50 % (22.8 s), the diagram card ~43 % and the summary card ~58 %. Close-ups bleed off the frame (47). This only partly agrees with item 23's ~55–65 %, since the range here is 43–72 %. [LIVE vs L1 L2 L3]
72. **Full-bleed app (our name)** — HERO shows the whole app edge to edge, with no backdrop or margin. In the wide frames body text is ~1 % of the frame height and cannot be read (as in item 27). After the push-in, a board card is ~20 % of the frame width. The phone mock-up is centred, ~22 % of the width and ~88 % of the height. [HERO APP P10]
73. **End card** — LIVE ends on the logo alone, centred, ~26 % of the frame width. It fades in over ~0.5 s (57.83 → 58.33 s), holds ~3.3 s and fades out (~61.67 → 61.97 s). Disagrees with item 39 (no end card). [LIVE vs L1 L2 L3 APP]

### Density & what's shown

22. **Single-subject frame (our name)** — One component per frame. Each tile holds one card, at most one card plus a pill, or a card plus a stack of ≤3 chips. [L1 L2 L3 P3 P11 P12 LIVE]
23. **Negative space** — The component fills ~55–65 % of the frame width with generous even margins (~15–20 % a side in the tiles, ~13 % in P9). [L1 L2 L3 P9 P11 P12] *LIVE ranges 43–72 % (71), and HERO has no margin (72).*
24. **Elliptical editing** — Only the key exchanges are shown. Conversations show 2–3 turns, never a long transcript. L3's chat shows ask → options → choice → confirmation, and its voice card shows one customer sentence. [L3 L2 LIVE] *LIVE shows four caller lines in 62 s, and the agent's side only as the card's rows.*
25. **Skeleton screen** — Placeholder states are shown on the way in. An empty card frame and empty table body appear first (L1 4.05–4.39 s; L3 Kate card 12.06 s; P4 empty "Skill usage" panel), then the content fills in. Real words never appear in a ghost: placeholders are blank bars or blank panels. [L1 L3 P4 LIVE HERO] *LIVE and HERO agree (55).*
26. **Neutral stage with elevated cards (our name)** — The backdrop is quiet. It is a flat warm light grey (~#eeece9), or a halftone dot field that densifies toward one corner (APP, P9, P11, P12). Cards are white with a 1 px hairline border, ~12–16 px radius and a soft wide shadow (P3 deepest). [all Dialpad refs] *LIVE stays quiet but goes dark (74).*
27. **Real-chrome wide shot (our name)** — Whole-UI shots use the real app at full width with all chrome present (APP, P10). Text is small, and the point is "this is a real product", not readability of any one line. [APP P10 HERO]

*From LIVE and HERO:*

74. **Vignette (dark warm stage)** — LIVE uses a near-black warm brown backdrop with a soft radial vignette (lighter centre) instead of item 26's light grey or halftone. Cards stay white. It disagrees on tone and agrees on keeping the backdrop quiet. [LIVE vs L1 L2 L3 APP P9 P11 P12]
75. **Growing record (our name)** — LIVE keeps one live card for the whole call. New facts append to it, and the camera reframes instead of replacing the card. Agrees with item 22. [LIVE]

### Emphasis & callouts

28. **Reserved accent colour** — The brand accent is reserved for the AI's action. L3 uses Dialpad orange only on the "✦ Account lookup" pill, L2 uses purple only on the "✦ Thinking…" pill, and L1's single orange dot sits on "Live Status". Everything else is greyscale. [L1 L2 L3 LIVE] *LIVE mostly agrees (77).*
29. **Outcome chip (our name)** — The outcome gets the strongest treatment. L3's last chip "Case logged ✓" is solid black with white text, while the step chips above it are white. In P11 each tile ends on a separate outcome pill with an icon in a lime disc, overlapping the card's lower edge. P3 uses the same lime check disc. [L3 P11 P3 LIVE] *LIVE marks outcomes in green and ends on a dark closed-state button (57, 77).*
30. **Step-chip stack (our name)** — Step chips sit under the action pill as a vertical stack, centred and narrower than the card (L3: "Duplicate charge identified", "Refund initiated"; L2: "786 conversations found", "Analyzing refund requests"). [L3 L2]
31. **Highlighter mark (our name)** — Inline highlight. P12's AI Live Coach card marks the key fact ("Tracking Number: ALX47293") with a pink highlight span over the words. It is the only in-text highlight seen. [P12 LIVE] *LIVE uses it twice and animates it (76).*
32. **Provenance tags (our name)** — Tool-call provenance is shown as small tagged lines ("Exit skill · Book new appointments ↗", "Workflow triggered · Payments ↗") under the agent's turn. [P8]

*From LIVE and HERO:*

76. **Highlighter wipe (our name)** — The key words get an orange-red highlight that wipes left → right: a measured reading over ~0.53 s (16.30 → 16.83 s), and a short verdict over ~0.33 s (48.67 → 49.0 s, sheet). The wipe is near-linear with a slight ease-out at the end (est.). It adds motion to item 31's static highlight. [LIVE P12]
77. **Reserved accent colour (live signal and AI suggestion)** — LIVE uses orange-red on the waveform, the listening label, the outline of the AI's suggestion card and the highlights. Outcomes go green (file sent, root cause, fixed). This agrees with items 28 and 29. HERO uses brand blue for the header, the selected card and the primary buttons. [LIVE HERO]
78. **Particle burst (our name)** — When the deal reaches Completed, small blue dots burst around the column header and the "All renewals" tab (~34.3 → 35.6 s, sheet). It is the only decorative effect in HERO. [HERO]

### Text & type

33. **Off-frame labels (no lower third)** — No in-video captions or titles. Labels live outside the animation: the caption under each tile ("AI Virtual Agents / From triage to resolution") and the stepper headings on the page (P4–P8). [L1 L2 L3 P4–P8 HERO] *LIVE partly disagrees: it puts the caller's words on screen (79).*
34. **Progress-paced stepper (our name)** — A progress bar paces the story on the page. A thin bar under the active step fills while the animation builds (P5 ~18 % shows 4 nodes, P6 ~55 % shows 5). This is page UI, not part of the video frame. [P4–P8]
35. **Hero number (our name)** — Large clean sans, two weights. Bold headings, regular body, sentence case. Big numbers are used as the hero where there is data (P3 "611", P12 "97%"). [P1–P3 P12]

*From LIVE and HERO:*

79. **On-screen quote (our name)** — LIVE shows the caller's spoken words as text, centred under a waveform, at the open and the close. These are captions of speech inside the frame, which disagrees with item 33. There are still no titles or lower thirds. [LIVE vs L1 L2 L3]

### Sound

36. **Silent autoplay (our name)** — No sound is apparent. These are silent web animations (autoplay tiles and screenshots). The references say nothing about sound. [all] *LIVE and HERO have no audio stream (ffprobe: video only).*

### Story structure

37. **Problem → work → outcome arc (our name)** — Each loop is one problem → visible work → outcome, in ~5–11 s. L3: "I was double charged for June." → "Account lookup" → "Duplicate charge identified", "Refund initiated" → "Case logged ✓". L2: question → "Thinking…" → two steps → answer. P11: issue card → outcome pill. [L3 L2 L1 P11 LIVE HERO] *LIVE stretches the same arc over 62 s, and HERO over ~38 s.*
38. **Named-step chips (our name)** — The AI's work is shown as named steps, not as prose. Every step is a short past-tense chip of 2–4 words. [L3 L2 P3 LIVE] *LIVE rows are headed the same way, with short past-tense labels.*
39. **Seamless loop (no end card) (our name)** — Loops, no ending. The tiles fade back to their first state and repeat. None has an end card or logo. [L1 L2 L3 APP HERO] *HERO loops with a hard-cut seam (54). LIVE disagrees: it is not a loop and ends on a logo end card (73).*
40. **Cold open in product** — Every Dialpad reference starts on the product UI already in context. None has a setup shot, device or person. [all Dialpad refs HERO] *LIVE disagrees: it opens on the caller's voice (80).*

*From LIVE and HERO:*

80. **Voice bookends (our name)** — LIVE opens on the caller's problem in their own words and closes on their thanks, both shown as waveform and quote, with the product in between and the logo last. Disagrees with item 40. [LIVE vs all Dialpad refs]
81. **Two-sided story (our name)** — HERO alternates between the agent's board and the customer's phone (a phone mock-up over a scrim), so both halves of each exchange are shown. [HERO]
82. **Stage-progression story (our name)** — HERO's plot is one card walking across the board's columns (Initial Outreach → Shopping Renewal → Closing → Completed). A click triggers each step, and the card's move confirms it. [HERO]

## Candidate rules

Each rule comes only from the observations it cites.

These rules were drawn before LIVE and HERO were studied. Where those two disagree with a cited item, the item says so (items 41–82).

1. **When a state settles: hold it 1.0–1.9 s before anything leaves.** (obs 18)

2. **When rows, lines or chips arrive in a group: bring them one at a time, ~0.33 s apart, each fading in over ~0.25–0.33 s.** (obs 16, 17)

3. **When the in-between of a conversation is not the point: show placeholders with no words, then only the key turns.** (obs 24, 25)

4. **When one state gives way to the next: dissolve or fade-and-drift (~0.25–0.4 s, eased), never a hard cut. Between whole screens, cross-dissolve ~0.2 s.** (obs 2, 3, 11, 12)

5. **When something must be read: isolate the one component at ~55–65 % of the frame on a quiet backdrop instead of punching into a full screen.** (obs 1, 8, 9, 22, 23, 26)
   - Middle path, when the camera zooms anyway: frame each landing so the card is whole and fills ~55–65 % of the width.
   - The references disagree among themselves here: APP and P10 show the whole app wide and still (obs 10). That supports one wide establishing shot.

6. **When the AI acts: give its action the brand accent, show its work as a stack of short past-tense chips, and give the outcome the strongest contrast.** (obs 28, 29, 30, 38)

7. **When a moment hands off to a related one: grow the named thing into what it names (scale-through, ~0.25 s out and ~0.35 s settle) with a brief colour wash.** (obs 4, 5, 14, 15)

8. **When nobody needs to be seen acting: show no cursor; let state change on its own.** (obs 7)

9. **When the shot's point is that the AI is listening: keep a live signal moving through the hold (a waveform or "Listening" dots).** (obs 6)

10. **When short text lands (a label or a spoken key line): type it in at ~10–15 chars/s, or reveal it word by word at ~7 words/s.** (obs 21)
    - The hold (rule 1) starts after the reveal ends.

11. **When putting words on screen: no captions or titles inside the frame.** (obs 33)

12. **When opening: start in the product, already in context.** (obs 40)
    - The references are 5–11 s loops, not a longer story with a caller, so this is weak evidence for a longer film.

13. **When ending: the references give no rule.** They loop with no end card (obs 39).

## Vocabulary

The growing inventory of effects and stylistic choices, one row per name used in the observations (item numbers in brackets). "our name" means no standard term was found, so the name is descriptive.

| Name | What it is | Where seen | Source of the term |
|---|---|---|---|
| Locked-off shot (1) | The camera never moves; all motion comes from the elements. | L1 L2 L3 APP (not LIVE, HERO) | https://en.wikipedia.org/wiki/Locked-off_shot |
| Rise-and-fade entrance (2) | An element fades in while rising a few percent of the frame, decelerating. | L3 HERO | our name |
| Drift-up exit (3) | An element fades out while drifting up. | L3 | our name |
| Fade through, scale variant (4) | The outgoing element grows and dissolves, and the incoming one settles from slightly larger. | L1 | https://material.io/design/motion/the-motion-system.html |
| Container transform (5) | A chosen card grows into its own detail view. | L2 L1 | https://material.io/design/motion/the-motion-system.html |
| Shared-element transition (14, 52) | The same element carries across two states or lists, so the viewer tracks it. | L1 L2 HERO | https://help.figma.com/hc/en-us/articles/360039818874 (Smart Animate matching layers) |
| Live signal (6) | A waveform or typing dots keep moving through a hold to show "listening". | L3 LIVE | our name |
| Self-driving UI (7) | State changes with no visible hand or cursor. | L1 L2 L3 APP, most of LIVE | our name |
| Staged cursor (60) | A scripted pointer drawn into the video clicks and taps the UI. | LIVE HERO | our name |
| Cursor travel, dwell, click (61) | ~0.8 s eased travel, ~0.33 s dwell on the target, and the state change on the click frame. | LIVE | our name |
| Click cadence (63) | How often the staged cursor acts (~1 click per 1–3 s). | HERO | our name |
| Ken Burns drift (41) | A slow, continuous pan and scale over a still subject. | LIVE | https://en.wikipedia.org/wiki/Ken_Burns_effect |
| Perspective tilt, 2.5D card (42) | Flat UI rotated in 3D with perspective. | LIVE | our name |
| Shallow depth of field (43) | The far part of the tilted card is blurred, so the eye lands on the sharp row. | LIVE | https://en.wikipedia.org/wiki/Depth_of_field |
| Vignette (74) | A darker frame edge with a lighter centre. | LIVE | https://en.wikipedia.org/wiki/Vignetting |
| Push-in / pull-back (8, 44) | The camera moves (or zooms) closer to the subject, then back out. | HERO (absent in the Dialpad refs) | https://filmdaft.com/?p=18959 |
| Follow pan (45) | The camera pans with a moving element so it keeps its place in the frame. | HERO | https://www.westga.edu/academics/coah/writing/glossary_of_film_terms.php (pan) |
| Cut-in / cut-out, axial cut (46) | A hard cut to a tighter or wider framing of the same subject. | LIVE | https://www.tella.com/definition/cut-in |
| Full-bleed crop (47) | A close-up where the subject runs off the frame edges. | LIVE | our name |
| Isolation framing (9) | One component shown alone at a legible size on a backdrop. | L1 L2 L3 P1–P12 LIVE | our name |
| Establishing shot (10) | A wide shot of the whole app, giving context. | APP P10 HERO | https://www.westga.edu/academics/coah/writing/glossary_of_film_terms.php |
| Real-chrome wide shot (27) | The real app at full width with all chrome, where the text isn't meant to be read. | APP P10 HERO | our name |
| Full-bleed app (72) | The app fills the frame edge to edge, with no backdrop or margin. | HERO | our name |
| Hard cut (11, 54) | An instant change from one frame to the next. | LIVE, HERO loop seam (absent in the Dialpad refs) | https://www.westga.edu/academics/coah/writing/glossary_of_film_terms.php |
| Cross-dissolve (12) | One screen fades out while the next fades in over it. | APP | https://www.westga.edu/academics/coah/writing/glossary_of_film_terms.php |
| Dip to background (13, 48) | Fade out, a 0.1–0.35 s empty beat, then fade in (a dip to black onto the backdrop). | L3 L1 LIVE | https://www.westga.edu/academics/coah/writing/glossary_of_film_terms.php (fade) |
| Wipe (49) | The next image replaces the current one by moving across the frame. | HERO | https://en.wikipedia.org/wiki/Wipe_(transition) |
| Colour wash (15) | A full-frame gradient that marks a hand-off and then clears. | L2 L1 | our name |
| Modal side sheet (50) | A panel slides in from the side over the content and blocks it. | HERO | https://material.io/components/sheets-side |
| Scrim (50, 51) | A dimming layer behind a modal surface. | HERO | https://material.io/components/sheets-bottom |
| Device mock-up pop-over (51) | A phone frame rises over the scene to show the customer's side. | HERO | our name |
| Collapse-to-point exit (53) | An element shrinks to a dot and fades out. | LIVE | our name |
| Morph (55–58) | One element becomes another (same layer, new form). | LIVE HERO | https://help.figma.com/hc/en-us/articles/360039818874 (Smart Animate) |
| Skeleton screen (25) | A blank grey layout stands in for content before it arrives. | L1 L3 P4 LIVE HERO | https://www.cyberoptik.net/glossary/skeleton-screen/ |
| Skeleton-to-content morph (55) | The placeholder itself turns into the filled element. | LIVE HERO | our name |
| Container expand (56) | A card's height animates to make room for a new row. | LIVE | our name |
| Button state morph (57) | The clicked button becomes its own result (label and colour). | LIVE | our name |
| Field-to-header morph (58) | A full-frame colour field becomes the app's header band. | HERO | our name |
| Strike-through rule-out (59) | A ruled-out item is struck through and greyed in place. | LIVE | our name |
| Staggered entrance (16, 65) | Items arrive one after another at a fixed delay (~0.1–0.33 s). | L1 L2 L3 LIVE HERO | https://m1.material.io/motion/choreography.html |
| Dialogue-paced reveal (64) | Rows arrive when the conversation supports them, 1–6 s apart. | LIVE | our name |
| Fade-in (17) | Opacity rises from ~20–30 % to full in ~0.25–0.33 s. | L1 L2 L3 LIVE | https://material.io/design/motion/the-motion-system.html (fade) |
| Ease-out (2, 44, 51, 56, 61) | Fast start that decelerates into place. | L3 LIVE HERO | https://m1.material.io/motion/duration-easing.html |
| Ease-in (4) | Slow start that accelerates out. | L1 | https://m1.material.io/motion/duration-easing.html |
| Hold (18, 19, 66) | The finished state stays still before anything leaves (~0.8–1.9 s for UI, ~2–4 s for speech, screens and the logo). | all | https://helpx.adobe.com/after-effects/using/keyframe-interpolation.html (hold keyframes) |
| Reveal rate (20) | How many reveals happen per second. | L1 L2 L3 HERO | our name |
| Average shot length (67) | The mean time between cuts (~4 s). | LIVE APP | https://en.wikipedia.org/wiki/Average_shot_length |
| Typewriter effect (21, 62) | Text appears character by character (10–15 chars/s for labels, ~26 chars/s for typed replies). | L1 L3 HERO | https://vdci.edu/learn/after-effects/character-word-line-techniques |
| Word-by-word reveal (21, 69) | Text appears a word at a time (~7 words/s), following speech rhythm. | L3 LIVE | https://vdci.edu/learn/after-effects/character-word-line-techniques |
| Time-lapse counter (68) | A live timer runs faster than real time (~13×). | LIVE | our name |
| Single-subject frame (22) | One component per frame. | L1 L2 L3 P3 P11 P12 LIVE | our name |
| Growing record (75) | One card stays on screen and gains rows instead of being replaced. | LIVE | our name |
| Negative space (23) | Empty margin around the subject (~13–20 % a side). | L1 L2 L3 P9 P11 P12 | https://en.wikipedia.org/wiki/Negative_space |
| Card scale in frame (71) | How much of the frame width the card fills (43–72 % in LIVE). | LIVE | our name |
| Centred voice frame (70) | A waveform and a centred quote alone in the frame. | LIVE | our name |
| Elliptical editing (24) | Only the key turns are shown, and the rest is skipped. | L3 L2 LIVE | https://en.wikipedia.org/wiki/Ellipsis_(narrative) |
| Neutral stage with elevated cards (26) | A light grey or halftone backdrop, white cards, hairline borders and soft shadows. | Dialpad refs | our name |
| Reserved accent colour (28, 77) | The brand accent appears only on the AI's action, the live signal or the key fact. | L1 L2 L3 LIVE HERO | https://developer.apple.com/design/human-interface-guidelines/color |
| Outcome chip (29) | The outcome gets the strongest contrast (a solid chip or green state). | L3 P11 P3 LIVE | our name |
| Step-chip stack / named-step chips (30, 38) | Short past-tense step chips, stacked under the action. | L3 L2 P3 LIVE | our name |
| Highlighter mark (31) | A colour span behind the key words. | P12 LIVE | our name |
| Highlighter wipe (76) | The highlighter span animates left → right across the words. | LIVE | our name |
| Provenance tags (32) | Small tagged lines naming the tool or workflow the agent used. | P8 | our name |
| Particle burst (78) | Small dots burst around the element that just completed. | HERO | our name |
| Off-frame labels, no lower third (33) | Titles and captions live outside the video, not as on-screen graphics. | L1 L2 L3 P4–P8 HERO | https://en.wikipedia.org/wiki/Lower_third |
| On-screen quote (79) | Spoken words shown as centred text inside the frame. | LIVE | our name |
| Progress-paced stepper (34) | A page progress bar fills as the animation builds. | P4–P8 | our name |
| Hero number (35) | One big number as the focal point of a data card. | P3 P12 | our name |
| Silent autoplay (36) | A muted web animation with no soundtrack. | all | our name |
| Problem → work → outcome arc (37) | One issue, the visible work and the result. | L3 L2 L1 P11 LIVE HERO | our name |
| Seamless loop (39) | The end returns to the first state and repeats. | L1 L2 L3 APP HERO | our name |
| End card (73) | The final frame with the logo alone, held, then faded. | LIVE | https://unity.com/en/glossary/end-card |
| Cold open in product (40) | The film starts inside the product, with no setup shot. | Dialpad refs HERO | https://en.wikipedia.org/wiki/Cold_open |
| Voice bookends (80) | The film opens and closes on the customer's own words. | LIVE | our name |
| Two-sided story (81) | Alternates between the agent's screen and the customer's device. | HERO | our name |
| Stage-progression story (82) | The plot is one card moving through the board's stages. | HERO | our name |
