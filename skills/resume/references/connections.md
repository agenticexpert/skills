# Report bridge

The report is one HTML template plus one JSON island. The file is durable; the localhost bridge is session-scoped.

## Start

```bash
python3 references/agui_bridge.py render --island report.json --out report.html --serve
python3 references/agui_bridge.py serve --report report.html
```

On Windows the interpreter is `py -3`, and the quoting differs: PowerShell takes `--args '{"path":"x"}'`, while `cmd` takes `--args "{\"path\":\"x\"}"` and does not strip single quotes. Forward slashes work in every path on every platform.

The bridge hosts one report. `/heartbeat` returns:

```json
{"alive":true,"report":"/real/path/report.html"}
```

`report` is `null` when the bridge has no report; `reportId` is the hosted island ID or null. Reuse succeeds only when requested and hosted realpaths are identical. Pages connect as `resume:<reportId>:<instanceId>:<encoded-realpath>` and send that realpath as `artifact` on durable commands. The bridge requires both ID and realpath, so copied reports sharing an ID cannot cross-write. Different-report and report-vs-null conflicts exit nonzero and name both identities; the bridge never claims to host the requested file.

## Durability

Durable verbs are `updateItem`, `setStatus`, `acceptRewrite`, `patchResume`, `patchLinkedin`, and `rereadSection`.

The durable store is the `#report-data` island inside `report.html` — that island is the JSON, and every durable verb rewrites it in place. The `--island` file passed to `render` is build input only and is never written back; neither is any source document the island was built from. `exportData` returns the current island for saving as a standalone file.

Every durable command performs:

1. lock;
2. read the hosted file;
3. parse its `#report-data`;
4. mutate in memory;
5. validate against that file’s `#report-contract`;
6. write a sibling temporary file and `os.replace` it;
7. broadcast to connected pages.

Failure before step 6 changes nothing. The page must not repaint, write localStorage, or close a draft until the bridge reports success.

## Item verbs

- `updateItem(n,patch)` allows `reason,suggestion,verdict,rewrite,prompt,decisions,questions`. The last two map only to `item.ctx`.
- `setStatus(n,"open"|"done"|"ignore")` changes status alone.
- `acceptRewrite(n,index)` writes the unique target, appends `accepted-rewrite:<index>` to `ctx.decisions`, and sets status `done` in one transaction.
- `getContext(n)` is page-local and returns exactly the 13-key capsule. It never returns status, the full item, or `resumeDoc`.
- Row Export JSON returns the same capsule. Converse wraps it as `{instruction,context}`.
- `patchResume(path,text)` and `patchLinkedin(path,text)` set one existing node in `resumeDoc` / `linkedinDoc`. Each is confined to its own prefix; `acceptRewrite` follows whichever prefix the item's `target` names.
- `exportData({scope:"cross-item"})` copies the island out as a standalone file; the UI labels it Cross-item export.

Positional and named argument forms remain valid for bridge commands.

## Reads

Untargeted `getState`, `exportData`, `getItem`, `getContext`, `listRubric`, and `getRubricContext` are answered from the hosted report file — the copy of record — so no tab need be open. An explicit `--to` routes to that page instead, which is how you ask a specific tab what it holds. `listChanges` is always page-local: it is per-session state and is not on disk.

Store-answered `listRubric` and `getRubricContext` return `stale: null`. Staleness is derived from a page's session change log, so disk cannot know it.

Never parse the island by hand. Every field a caller needs is reachable through a verb.

## Offline

Report reading, preview, expand, prompt staging, copying, and context export work without the bridge. Durable actions are disabled or fail visibly with “A bridge owning this report is required.” They never make an optimistic local change.

## CLI

```bash
python3 references/agui_bridge.py tools
python3 references/agui_bridge.py list
python3 references/agui_bridge.py cmd --to <report-or-instance> --verb getContext --args '[1]'
python3 references/agui_bridge.py export --report report.html --doc resume|linkedin|island [--format md|json] [--out PATH]
python3 references/agui_bridge.py stop
```

`export` is the round trip out of the island: it reads the report's current `resumeDoc` or `linkedinDoc` and writes it back as a document. Read-only on the report, no bridge required, and it runs whether or not a server is hosting the file. Markdown by default; `--doc island` emits the whole island as JSON. Exported résumés carry contact fields — local only.

Candidate data remains local. The bridge makes no external requests.
