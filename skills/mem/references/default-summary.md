# Default Summary Format

The default `/mem summarize` structure — an augment file like any other, applied first, before the project augment `.agents/mem/mem.md` and `using` files. `from` paths resolve relative to this file. Every built-in definition lives in `default-sections.md`, so the whole default format loads in one read.

ADD SECTION `<analysis>` last from default-sections.md#analysis
ADD SECTION `<evolution>` last from default-sections.md#evolution
ADD SECTION `<timeline>` last from default-sections.md#timeline
ADD SECTION `<cache>` last from default-sections.md#cache
ADD SECTION `<mcp-tools>` last from default-sections.md#mcp-tools
ADD SECTION `<requirements>` last from default-sections.md#requirements
ADD SECTION `<references>` last from default-sections.md#references
ADD SECTION `<troubleshooting>` last from default-sections.md#troubleshooting
ADD SECTION `<todos>` last from default-sections.md#todos
ADD SECTION `<current-step>` last from default-sections.md#current-step
ADD SECTION `<current-conversation>` last from default-sections.md#current-conversation
ADD SECTION `<relevance>` last from default-sections.md#relevance
ADD SECTION `<triggers>` last from default-sections.md#triggers
ADD SECTION `<meta>` last from default-sections.md#meta
