# Pins

## Pinning

1. Name the aspect to keep in a few words, from the ask: "lamp look", "keeper's face", "storm
   score theme". The whole file kept as it is → `--keep all`.
2. Find the file: a shot's approved take (leave out `--ref`; `--from` is that shot), another take
   (`--ref 3a.1`), the file the user points at, or a link.
3. Set the span the ask gives: one shot (`--from 3c`), a scene (`--from 3`), a run (`--from 3c
   --to 4b`), or the whole story (neither). A beat, prep item or to-do pins to its scene.
4. `storypad.py pin add <story> <name> --keep <aspect> --ref <file or link> [--from] [--to]`. The
   file is copied into `assets/`; `--link` when the user wants the link followed instead of a copy.
5. Show the strip it prints; a pinned shot or scene carries `•` on its id, and a pin over the whole
   story or from its series marks the story's title and each scene's own strip.

Unpin with `pin remove`. A shot or scene under a pin can't be removed, and a move that changes what
a pin runs over is refused, until the pin changes or goes.

## Prompts

A prompt is the instruction for the tool that makes a shot. Storypad never makes the shot.

1. `storypad.py detail <story> <shot id>` lists the shot's prompt and the pins over it.
2. No prompt yet → write one from the shot's shows line (else its name), its scene's beats and
   script, and each pin's aspect and file, and keep it with `shot set <story> <shot id> --meta
   prompt="<prompt>"`.
3. A prompt marked for review in `detail` or `todo` → write it again from the same sources with
   `--meta prompt=`; it still holds → `shot set <story> <shot id> --reviewed`.

## Takes

1. A file the user gives for a shot → `storypad.py take add <story> <shot id> --file <file>`, with
   `--model` when the user says what made it. Its prompt defaults to the shot's prompt and its
   refs to the pins' files; give `--prompt` or `--refs` when the user names others.
2. Compare the file with each pin's file. Reply naming the take, and each pin as held, missed
   (with what differs), or not compared (with why). Never say a pin held without comparing.
3. The user picks a take → `take approve <story> <take id>`; none of them → `take unapprove`. One
   they want held from here on → pin it (**Pinning**). An approved take marked for review → name
   what changed; the user's pick → `take approve` it, or `shot set <story> <shot id> --reviewed`
   when the approved one still holds. A take whose shot starts part way into the
   file → `take set <story> <take id> --in <seconds>`.
