# New story or series

1. No premise in the ask → ask for the core idea in one sentence first.
2. `storypad.py new "<title as written>" [--series] [--venue <venue>] --premise "<premise>"
   [--audience "<audience>"] [--length "<target length>"]`, with the venue, audience and length
   the ask gives; the venue defaults to `youtube`. It makes `agents/storypad/stories/<title in
   kebab-case>/` from the venue's template, dated today, with the venue's first scenes and their
   beats.
3. Refused as already there → open that story and say so. Refused for the venue → name the venues
   it lists and stop.
4. A series: add its episodes with `references/series.md`.
