# Summarize Playbook

Create a durable, structured summary of this conversation — full fidelity, chronological, resumable by any agent without the original context.

Default output: `.agents/mem/summary/SUMMARY.md`. Create directories as needed.

## Arguments

| Pattern | Effect |
|---|---|
| `/mem summarize` | Default format → `.agents/mem/summary/SUMMARY.md` |
| `to {path}` | Custom output path |
| `using {augment}` | Apply an augment file — see Augment Files |
| `keeping {web\|files\|context7}` | Keep that cache — flips the matching discard flag for this run |
| `from {source}` | Summarize a file instead of the live conversation — an archived transcript (`.agents/mem/transcripts/`), an export, any conversation record. Too large for one read → process in sequential chunks, carrying section content forward; write once at the end |

Arguments combine freely. Project-specific reference material rides in via an augment's free-form instructions.

`using` resolution: a bare name loads this skill's `references/augments/{name}.md`; a path with a slash resolves from the working directory.

## Inputs

- The existing summary — the file at the output path when present (read it first), else a checkpoint already in context (the /clear hook prints it and archives the file). Either is the previous summary: the base every APPEND section grows from, the source of session and T numbering
- `discard_web_cache` (default true) — drop web fetch/search content
- `discard_context7_cache` (default true) — drop context7 content
- `discard_referenced_file_cache` (default true) — drop old file contents, except CLAUDE.md and files loaded in the recent thread; dropped files reload from disk when needed
- Pending prunes — read `.agents/mem/summary/.prune_log`; each line is a prune topic

Flags flip per-run via `keeping {...}`; an augment's free-form instructions can also set them.

## General Rules

- Review everything chronologically, previous summaries first
- Later supersedes earlier — show both states, never silently drop the original
- APPEND sections grow across summaries; never rewrite their history
- Mark session boundaries [SESSION n] in every section that spans them; n = previous summary's highest session + 1, else 1
- Omit sections with nothing to say — Delivery confirms omissions; a format that tracks them (the default's `<meta>`) records them too
- Preserve code, commands, errors, and exact user questions verbatim — never paraphrase artifacts

## Pruning

`/mem prune {topic}` appends the topic to `.agents/mem/summary/.prune_log` and stops — no summary written.

At the next summarize:
1. Remove every discussion of each pruned topic from all sections.
2. If something kept depends on a pruned topic, keep one line: "earlier {topic} discussion (pruned) led to…".
3. Delivery confirms pruned topics; a format that tracks them (the default's `<meta>`) records them too.
4. Clear `.prune_log` after writing to the default `.agents/mem/summary/SUMMARY.md`. A `to {path}` summary applies pending prunes but leaves the log intact.

## Slot System

Every section is a SLOT: default instructions that augments can extend or replace at three positions.

```text
<summary>
  <section>
    [BEFORE augments]
    [DEFAULT (unless replaced)]
    [AFTER augments]
  </section>
</summary>
```

Directive: `SLOT before|replace|after <section>` followed by the instructions to run at that position. Multiple augments at the same position run in declaration order.

Augment output lands inside the section wrapped in a tag named for the augment source — provenance stays visible in the summary. An augment that also adds a section under its own name produces both — the section, and its wrapped slot output elsewhere; nesting keeps them distinct.

A SLOT naming a section not in the composed format is skipped — Delivery reports it.

Augment from `augments/example.md` — `SLOT before <analysis>` becomes:

```xml
<summary>
    <analysis>
        <example>
            ... example augment output goes here
        </example>
        ... default output goes here
    </analysis>
    ...
</summary>
```

`replace` keeps only the `<example>` block (prunes the default); `after` places it below the default.

## Adding and Removing Sections

`ADD SECTION <name> before|after|replace <existing-section>` — anchored placement.
`ADD SECTION <name> first|last` — positional placement when there is nothing to anchor to.
`REMOVE SECTION <name>` — drop a composed section and its slots.
`RESET FORMAT` — discard everything composed so far; the file continues from an empty `<summary>`.

ADD SECTION output is not wrapped — the section tag itself is the provenance.

Resolution:

- An anchor naming a section not in the composed format falls back to `last` — the content still lands; Delivery reports the fallback.
- ADD SECTION naming a section already composed does not duplicate it — the instructions join that section as `SLOT after`.

`ADD SECTION <decisions> after <requirements>` becomes:

```xml
<summary>
    ...
    <requirements>
    </requirements>
    <decisions>
      ... decision content
    </decisions>
    <troubleshooting>
    </troubleshooting>
    ...
</summary>
```

Added sections behave as SLOTs just like the defaults.

## Instructions Source

Every directive is followed by its instructions — inline, or loaded via `from {path}`:

```text
ADD SECTION <name> last from default-sections.md#{name}
SLOT after <section> from {path}
```

A `#{name}` suffix selects one definition from a multi-section file: the block under the `## <name>` heading, ending at the next `##` heading. The file loads once, however many anchors point into it.

`from` paths resolve relative to the file containing the directive; not found there → relative to this skill's `references/`. The project augment `.agents/mem/mem.md` can mix its own definition files with the built-in set (`default-sections.md#{name}`).

## Augment Files

An augment file (passed via `using {path}`) contains any mix of:

- `SLOT ...` directives
- `ADD SECTION ...` directives
- Free-form instructions — execute before building the summary (e.g. load project docs)

Worked example: `references/augments/decisions.md`.

## Composition

The default format is not hardcoded — it is an augment file: `default-summary.md`, a sequence of `ADD SECTION ... last from default-sections.md#{name}` directives over the section definitions in `default-sections.md`. Defaults and user extensions are the same language; they differ only by load order.

Build:

1. Start with an empty `<summary>`.
2. Apply the built-in default format: `default-summary.md`.
3. Apply the project augment: `.agents/mem/mem.md`, if present.
4. Apply `using {augment}` files in argument order.
5. Execute the composed instructions.

Resolve every `from` path first, then load the distinct files in one batch — a single command or parallel reads; anchored paths into the same file share one read. Never compose a section whose definition file you haven't read.

`mem.md` extends or overrides the default without redefining it — SLOT into sections, add sections, remove them. Full redefinition: start the file with `RESET FORMAT` and build from empty. One-off variations stay on `using`.

## Structure

A summary is the composed sections, in composed order, wrapped in `<summary>`:

```xml
<summary>
  <section>
    ... content per that section's instructions
  </section>
  <another-section>
    ...
  </another-section>
</summary>
```

The concrete tags and their order come from whichever format applied — never from this spec.

## Delivery

1. An existing file at the output path → copy it into `.agents/mem/summary/archive/` with a timestamp suffix first; no version is ever overwritten. Then write the summary.
2. Confirm: output path, sections omitted, topics pruned, directives skipped or fallen back, unresolved decision count.
3. Unresolved decisions exist → offer `/mem decide`.
