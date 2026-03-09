---
name: mem
description: Memory management system with high-fidelity summarization, extensible protocols, and lifecycle hooks for context preservation across sessions.
---

# Mem Skill

Memory management system using LLM context for sophisticated operations.


## INSTRUCTION FILES STRUCTURE




## SUB COMMANDS

- INSTALL
  - Example: /mem install
    - load and execute .../skills/mem/references/install.md

- SUMMARY
  - Example: /mem summary
    - execute the instructions in this file following all instructions as specified

- CONTINUE
  - Example: /mem continue {path}
    - load and execute .../skills/mem/references/continue.md

- CAPTURE
  - Example: /mem capture {idea} to {path}
  - load and execute .../skills/mem/refrences/capture.md

- REQUIREMENTS (TBD)
- DECIDE (TBD)
- TODO (TBD)
- SPLIT (TBD)


## GENERAL RULES AND INSTRUCTIONS

- Execute all instructions completely
- CRITICAL: Strict chronological order throughout
  - Sequence from start → current (including previous summaries)
  - Later information supersedes earlier
  - Track evolution of decisions/changes over time


## DISCUSSIONS

- Main Features: List all features/components discussed or implemented (in order discussed)
- Technical Decisions: Architecture choices, design patterns, libraries selected (maintain temporal order)
- Business Logic: Core business rules and requirements that shaped the implementation
- Edge Cases: Special scenarios or constraints we've identified


## SYSTEM

Summary uses XML-like <tags> as SLOTs. Each SLOT has default content that external instructions can augment:

- before: augment executes before default
- replace: augment replaces default (prunes default)
- after: augment executes after default


### SLOT DEFINITION

Let SLOT {name} be:
- inputs 
  - {where}:
    - one of "before", "replace", or "after"
  - {instructions}
    - the instructions to execute

```text
<summary>
  <section>
    [BEFORE augments]
    [DEFAULT (unless replaced)]
    [AFTER augments]
  </section>
</summary>
```

### SLOT Examples

Thus,

Augment from path/to/augment/example
- SLOT path/to/augment/example before <analysis>

Becomes
```xml
<summary>
    <analysis>
        <example>
            ... example augment instructions go here
        </example>
        ... default instructions go here
    </analysis>
    ...
</summary>
```

Augment from path/to/augment/example
- SLOT path/to/augment/example replaces <analysis>

Becomes
```xml
<summary>
    <analysis>
        <example>
            ... example augment instructions go here
        </example>
    </analysis>
    ...
</summary>
```

Augment from path/to/augment/example
- SLOT path/to/augment/example after <analysis>

Becomes
```xml
<summary>
    <analysis>
        ... default instructions go here
        <example>
            ... examples augment instructions go here
        </example>
    </analysis>
    ...
</summary>
```


## SECTIONS DEFINITION

Augments can add new SECTIONs to the summary structure:

ADD SECTION `<name>` before|after|replace `<existing-section>`

Example:
ADD SECTION `<decisions>` after `<requirements>`

Becomes:
```text
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

Augmented SECTIONS behave like SLOTS just like the default ones do.


## <analysis> DEFINITION

A high-level paraphrase of the conversation.  Summarize what was discussed, accomplished,
key terms, and overview to preserve continuity when resumed.  Be concise, because 
most details will be captured in the following sections.


## <evolution> DEFINITION

CRITICAL: Sequential narrative of how conversation evolved. Each entry is 1-3 sentences telling the story.

Format:
```text
  [SESSION 1]
1. Started by loading emma reference files (ag-ui-specs, new-app-tool, bindings map, styles) to restore context from prior
   sessions and understand the existing AG-UI tool architecture.
2. User asked to list existing disk drive AG-UI tools — after reviewing, clarified they only wanted disk-tools.js frontend
   tools plus the MCP load/save tools, not the entire disk management system.
3. User requested SmartPort tools mirroring the floppy disk pattern. Created plan covering frontend AG-UI tools and MCP
   integration, user approved approach.

   [SESSION 2]
4. Implemented smartport-tools.js with 4 core operations and created load-smartport-image.js MCP tool for .hdv/.po/.2mg
formats, keeping it separate from floppy disk infrastructure per user confirmation.
```

Rules:
- Narrative style, 1-3 sentences per entry
- Include context and reasoning
- Sequential but can capture more events than timeline
- APPEND only



## <timelines> DEFINITION

CRITICAL: Factual ledger of IMPORTANT events only. Brief entries, key milestones.

Format:
```text
      [SESSION 1]
- T1: Created SmartPort AG-UI tools (4 tools)
- T2: Created load-smartport-image.js MCP tool
- T3: Added slot management (list/install)
  
      [SESSION 2]
- T4: Created general slot-tools.js
- T5: Fixed slot config window refresh bug
```

Rules:
- APPEND only, never replace
- Show updates: "T2: PostgreSQL" → "T8: Switched to SQLite"
- Brief factual entries (what happened)
- Only important milestones
- Doesn't require 1:1 with evolution (filtered view)
- Preserve causality (T4 led to T5, T5 led to T6)
- Mark session boundaries
- Strict chronological order
- Cross-reference details (e.g., "T6: See  for rationale")








## SUMMARY STRUCTURE

```xml
<summary>
  <analysis>
  </analysis>

  <evolution>
  </evolution>

  <timeline>
  </timeline>

  <cache>
  </cache>

  <mcp-tools>
  </mcp-tools>

  <requirements>
  </requirements>

  <references>
    <files>
    </files>
    <web>
    </web>
  </references>

  <troubleshooting>
  </troubleshooting>

  <todos>
  </todos>

  <current-step>
  </current-step>

  <current-conversation>
  </current-conversation>

  <relevance>
    <examples>
    </examples>
    <planning>
    </planning>
  </relevance>

  <meta>
  </meta>
</summary>
```
