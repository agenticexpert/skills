# install — enable the /until slash command

Copy the skill's bundled command file into a Claude Code commands directory so `/until` registers as a slash command. One-time, idempotent, no playbook logic — this file is the whole procedure.

## Scope

- `/fabble install` → this project: `.claude/commands/`
- `/fabble install global` → every project: `~/.claude/commands/`
- Any other argument → stop and ask which scope; never guess a directory.

## Procedure — in order

1. **Locate the source.** `commands/until.md` inside this skill's own directory (sibling of `SKILL.md` — resolve from the skill's location, never from the working directory). Source missing → STOP; tell the user the skill install is incomplete and to re-run `npx skills add agenticexpert/skills/fabble`. Never reconstruct the command file from memory.
2. **Resolve the target.** `<scope dir>/until.md`. Create the directory if absent.
3. **Collision check.** Target exists → compare with source. Identical → report "already installed", stop (no copy). Different → replace it and say so in the confirmation.
4. **Copy** source → target, byte-for-byte. No edits, no reformatting.
5. **Verify.** Read the target back; must exist and match the source. Mismatch → report the failure plainly; do not claim success.

## Output

Exactly one confirmation line: where the file landed · invoke as `/until [opus|sonnet] <ask>` · delete that file to uninstall. Prepend "replaced existing" when step 3 replaced. Nothing else — no tour of the skill, no usage examples beyond the invoke form.

## Boundaries

- Touch nothing but the single target file (and its parent directory when creating it).
- Never edit `commands/until.md` in the skill itself during install.
- Never install to both scopes in one run; one scope per invocation.
