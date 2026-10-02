# Branch Playbook

The user is jumping out of the current milestone, coming back from a detour, undoing one, or asking what is in flight.

All scripts live at `{skills}/scripts/`, where `{skills}` is the directory holding this playbook, minus `/references`. Resolve every natural-language name to slugs first, per navigate.md → **Resolving References**. A t_key is `<roadmap>/<track>/<milestone>`.

---

## Opening

### Explicit — "branch to X"

Resolve X to a destination t_key. The origin is the milestone holding the current DOING task; with none, the milestone in conversation focus. Create the destination milestone first (`structure.md`) when it does not exist. Then:

```
python {skills}/scripts/manage_branches.py open <project> <origin-t_key> <dest-t_key> [--oob]
```

Pass `--oob` when the destination work belongs out of band.

### Automatic — tasks created outside the current milestone

When you create one or more tasks in a milestone other than the one holding the current DOING task, run the same `open` immediately after the creation. Do not ask first, do not offer the command, do not pause for confirmation.

`open` prints one line naming the destination, the task that holds the return, and the undo command. Do not repeat that line (SKILL.md → **Always**).

### What `open` writes

- The origin's DOING task goes PAUSED, and the status it held is recorded.
- One marker row lands in the origin's order array, one in the destination's.
- The return anchors on that paused task; with no DOING task at the origin, on the first PENDING task after the marker; with neither, on the origin milestone itself.

A marker row has no `.md` file. Never create one, never move one by hand, never edit `project.json["branches"]` directly.

### Refusals

`open` exits non-zero, prints one line, and writes nothing when:

- the destination is the origin milestone and `--oob` was not passed;
- the destination already holds another branch's return — the line names that record, its origin and its anchor;
- the destination already sits somewhere in the origin's own chain.

State the line's substance in plain words. Do not retry and do not work around it.

---

## Returning

Whenever the current milestone is a branch destination, resolve "next" through the return check:

```
python {skills}/scripts/manage_branches.py show <project> --return
```

Announce lines print first, the JSON answer after them — parse from the first `{`. The answer carries `origin`, `origin_anchor` and `mid`, and sets `drift` when the anchor was gone and the record was dropped.

- `origin_anchor` names a task → resume it from the first unchecked criterion on disk (`execute.md` → **Pausing**).
- `origin_anchor` is null → take the origin milestone's own next task.
- `mid` is null → the current milestone still holds workable tasks; stay in it.

The script prints one line per hop and closes each record it consumes. Do not repeat those lines.

---

## Closing and undoing

```
python {skills}/scripts/manage_branches.py close <project> <MID>
python {skills}/scripts/manage_branches.py drop  <project> <MID>
```

`close` marks the detour finished when the user says so. `drop` removes both marker rows, deletes the record, and restores the anchor's status — run it when the user rejects an auto-branch.

---

## Inspecting

| Question | Command |
|---|---|
| Where am I / what's in flight? | `view_branches.py [<project>]` |
| One record, or every record with the current position | `manage_branches.py show <project> [<MID>]` |

`show` writes a `Drift:` line for every inconsistency — a missing marker row and the index it belongs at, a `parent` that disagrees with the chain, a marker row with no record, a t_key with no directory. Report drift to the user. Never repair it by hand.

---

## Where new tasks land

In a milestone whose order array ends in a closing marker, `manage_tasks.py create` and `move` place the task above that marker, whatever position is asked for, and the closing marker stays last. Ask for no special flag and adjust no position for it.
