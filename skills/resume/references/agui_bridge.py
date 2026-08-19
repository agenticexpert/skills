#!/usr/bin/env python3
"""AG-UI bridge and durable host for the resume report.

A single-file, stdlib-only local bridge: report pages dial out to it over
Server-Sent Events, and agents reach the pages' `AGUIrun` verb surface
through it over plain HTTP. The connection doctrine — registry states
(connected / disconnected / broken), first-connect default, `wasDefault`
yield-and-reclaim, duplicate-name rejection only against a live stream,
the disconnect trichotomy (intentional keeps the entry, unload removes
it, a silent drop marks it broken), routing precedence (explicit target >
default > sole connection > pick-one error), broken-target wait/switch/
abort prompts, auto-promotion when the default leaves exactly one peer,
and the `_note` rider that drains onto the next successful command — is
ported from the emma/web-a2e connection architecture.

Command addressing (deterministic names, no pool): a target is an exact
`resume:<reportId>:<instanceId>:<encoded-realpath>` name, a bare instanceId (the one page
that owns it), a reportId (every connected tab of that report), or the
literal `all` (broadcast). Untargeted commands go to the default, else
the sole connection, else error with a pick-one prompt.

TWO LIFETIMES, deliberately split. The CONNECTION layer is ephemeral —
registry, pending calls, and notes live in memory, and nothing about who
was dialed in survives a stop; connections are inherently ephemeral and
stay that way. The REPORT is not: launched with `--report <path>`, the
bridge serves that one file AND owns it as the durable store. The served
page and the file on disk are one artifact. Durable verbs (updateItem,
patchResume) mutate the on-disk `#report-data` island here in Python —
validate the mutated island against the file's own shipped
`#report-contract` fail-closed (a breach writes nothing), atomic-write it
(os.replace of a temp file — never a partial file on disk), then broadcast
the same verb to every connected tab so the in-memory render matches disk.
The report path is a runtime argument: nothing about a candidate is baked
into this file.

Usage:
    python3 agui_bridge.py serve [--report <report.html>] [--dir <static-dir>]
    python3 agui_bridge.py list
    python3 agui_bridge.py cmd [--to <target>] --verb <verb> --args '<json>'
    python3 agui_bridge.py stop
    python3 agui_bridge.py tools

`serve` probes the port first. Reuse succeeds only when the requested report
realpath equals the heartbeat's hosted report realpath (or both are null);
identity conflict is nonzero, with no takeover.

HTTP surface:
    GET  /heartbeat                          liveness + hosted report identity
    GET  /events?name=<n>&wasDefault=<bool>  SSE dial-in, CONNECT_ACK first
    GET  /list                               connection listing
    GET|POST /disconnect?name=<n>&type=intentional|unload
    POST /command {"to"?,"verb","args"?,"artifact"?} route a verb, await results
    POST /result  {"tool_call_id","result"}  page posts a call result back
    POST /stop                               acknowledge, then shut down
    GET  /tools                              self-describing tool directory JSON
    GET  / or /<report basename>             the hosted --report file
    GET  <other paths>                       static file from --dir, else 404

The tool directory (`TOOL_DIRECTORY` below) is one self-describing structure
surfaced three identical ways — printed at `serve` start, returned by GET
/tools, and printed by the `tools` CLI command — enumerating every CLI
command, HTTP endpoint, and page verb with a signature and one-line semantics.
"""

import argparse
import copy
import json
import mimetypes
import os
import queue
import re
import select
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

PORT = 8917


def _set_port(port):
    """Point this process at a bridge port other than the default.

    Every localhost URL reads PORT at call time, so rebinding the module global
    is enough for the server and every client. TOOL_DIRECTORY is built once at
    import, so its published port is corrected here too — a caller reading the
    directory to find the bridge must not be sent to a port nothing is on."""
    global PORT
    PORT = port
    TOOL_DIRECTORY["port"] = port

# SSE keepalive cadence. Doubles as the drop-detection bound: every wake
# probes the socket, so a client that vanished without a disconnect signal
# is marked broken within roughly one interval.
KEEPALIVE_SECS = 5.0

# Bound on waiting for a command's results. Multi-target collection shares
# one deadline, so responsive pages' results return alongside timed-out
# markers instead of the wait compounding per target.
RESULT_TIMEOUT_SECS = 10.0

# Result-wait poll granularity: how quickly a mid-call broken transition
# turns into a prompt instead of running out the clock.
POLL_SECS = 0.25

# tool_call_name carried on every TOOL_CALL_START event.
TOOL_CALL_NAME = "agui_command"

# Sentinel pushed onto a connection's event queue to end its SSE stream.
_CLOSE = object()

# The verbs the BRIDGE executes against the durable report instead of passing
# through to the pages. Everything else is still a pure passthrough. Each one
# writes disk first and only then broadcasts, so a connected tab can never
# render a change that failed to persist.
DURABLE_VERBS = ("updateItem", "setStatus", "acceptRewrite", "applyRewrite", "patchResume", "patchLinkedin", "rereadSection")

# Read verbs the BRIDGE answers from the report file when it owns one, so the
# store is readable as well as writable without a tab open. An explicit `--to`
# still routes to that page, which is how you ask a specific tab what IT holds.
# `listChanges` is absent on purpose: it is per-session page state, not on disk.
STORE_READ_VERBS = ("getState", "exportData", "getItem", "getContext", "listRubric", "getRubricContext")

# The two writable documents. A patch verb names one; `acceptRewrite` follows
# whichever prefix the item's own target carries.
DOC_ROOTS = {"resumeDoc.": "résumé", "linkedinDoc.": "LinkedIn"}
LINKEDIN_DOC_KEYS = ("headline", "about", "experience", "skills", "extras")

CTX_KEYS = (
    "itemId", "path", "lane", "reader", "atom", "neighbor", "evidence",
    "truth", "decisionEffect", "suggestion", "relatedIds", "decisions",
    "questions",
)
CTX_STRING_KEYS = (
    "path", "lane", "reader", "atom", "neighbor", "evidence", "truth",
    "decisionEffect", "suggestion",
)
CTX_MAX_CHARS = {
    "path": 256, "lane": 160, "reader": 80, "atom": 600,
    "neighbor": 600, "evidence": 800, "truth": 240,
    "decisionEffect": 20, "suggestion": 600,
}
READER_NAMES = ("ATS", "Recruiter", "HR", "Hiring manager", "Technical reviewer")
ATS_VALUES = ("fail", "risky", "weak-pass", "pass")
SCREENER_VALUES = ("no-call", "maybe", "call", "urgent-call")
MANAGER_VALUES = ("no", "insufficient", "interview", "priority-interview")
STATUS_VALUES = ("open", "done", "ignore")
URGENCY_VALUES = ("crit", "high", "med", "low", "none")
EFFECT_VALUES = ("decision", "proof", "risk", "action", "none")
MODE_VALUES = ("quick-scan", "standard", "rewrite", "skillmatch")
STANDARD_SECTIONS = ("resume", "donext", "readers")
STANDARD_LINKEDIN_SECTIONS = ("resume", "linkedin", "donext", "readers")
# Skillmatch grades and their confirmation prompts now live in top-level
# `rubric`, so skillmatch carries the same section set as every other mode.
SKILLMATCH_SECTIONS = STANDARD_SECTIONS
SKILLMATCH_LINKEDIN_SECTIONS = STANDARD_LINKEDIN_SECTIONS
RUBRIC_KEYS = ("competency", "grade", "evidenceIds", "gaps")
RUBRIC_OPTIONAL_KEYS = ("bar", "standing")
JD_SET_KEYS = ("postingId", "label", "archetype", "archetypeStatus", "experience")
JD_ARCHETYPE_VALUES = (
    "leadership", "ic", "architect", "forward-deployed", "generalist",
)
JD_ARCHETYPE_STATUS_VALUES = ("inferred", "confirmed")
BAR_KEYS = ("requirement", "level", "range", "sources")
OPEN_BAR_KEYS = ("requirement", "level", "range", "sources", "question")
STANDING_VALUES = ("meets", "below", "above", "unprovable")
PROMPT_LABELS = ("Item:", "Atom:", "Evidence:", "Truth:", "Decision effect:", "Task:")
_PROMPT_BLOCK_RE = re.compile(
    r"(?ms)^(%s)[ \t]*(.*?)(?=^(?:%s)|\Z)"
    % ("|".join(re.escape(l) for l in PROMPT_LABELS),
       "|".join(re.escape(l) for l in PROMPT_LABELS))
)


def _prompt_blocks(prompt):
    """Each label's value, running to the next label rather than to end of line.

    A value may span lines: `ctx.evidence` carries one line per evidence group,
    and a context item on a group path needs two of them."""
    blocks = {}
    for match in _PROMPT_BLOCK_RE.finditer(prompt):
        blocks.setdefault(match.group(1), match.group(2).strip())
    return blocks
TARGET_DECODE_KEYS = ("buyingNeed", "jdSupport")
BUYING_NEED_KEYS = (
    "statement", "beneficiary", "constraint", "status", "evidence",
    "confirmingQuestion",
)
JD_SUPPORT_KEYS = (
    "nonNegotiables", "centralProblem", "differentiator",
    "smallestTruthfulRepair",
)
BUYING_STATUS_VALUES = ("confirmed", "inferred", "unknown")
EVIDENCE_SOURCE_VALUES = ("jd", "user")
NON_NEGOTIABLE_VALUES = ("proven", "confirm", "absent")
CENTRAL_PROBLEM_VALUES = ("strong", "buried", "weak", "missing", "unknown")
REPAIR_CONFIRMED_ACTIONS = (
    "keep", "tighten", "rewrite", "collapse", "split", "move", "expand", "cut",
)
ITEM_SCOPE_VALUES = ("atom", "context")
ITEM_VISIBILITY_VALUES = ("hotspot", "supporting", "clean")
RESUME_SECTION_KEYS = ("sectionId", "path", "title", "verdict", "status", "staleness", "assessment")
SECTION_VERDICT_VALUES = ("strong", "adequate", "weak", "unread")
SECTION_STALENESS_VALUES = ("fresh", "stale")
CRAFT_KEYS = ("path", "element", "grade", "bars", "itemIds")
CRAFT_BAR_KEYS = ("bar", "grade", "note")
CRAFT_ELEMENT_VALUES = ("headline", "summary", "bullet", "role-header", "section", "document", "contact")
CRAFT_GRADE_VALUES = ("winning", "competent", "median", "below-bar")
HOTSPOT_FORBIDDEN_TERMS = (
    "atom", "gate", "decisioneffect", "provenance", "semantic", "vector", "pcopo",
    "the candidate",
)
PARSE_STATUS_KEYS = ("state", "affectsAts", "evidence")
PARSE_EVIDENCE_KEYS = ("source", "ref", "observed")
PARSE_STATE_VALUES = ("untested", "tested")
PARSE_EVIDENCE_SOURCES = ("extraction-artifact", "parser-command")
PARSE_CLAIM_TERMS = ("parses cleanly", "will parse", "ats-readable")


def _unknown_target_decode():
    return {
        "buyingNeed": {
            "statement": "",
            "beneficiary": None,
            "constraint": None,
            "status": "unknown",
            "evidence": [],
            "confirmingQuestion": "What business result is this role expected to change?",
        },
        "jdSupport": {
            "nonNegotiables": [],
            "centralProblem": {"status": "unknown", "itemIds": []},
            "differentiator": None,
            "smallestTruthfulRepair": None,
        },
    }


def _default_parse_status():
    return {"state": "untested", "affectsAts": False, "evidence": None}


def _derive_section_id(path):
    """Map an item's ctx.path prefix to a résumé section id — the single
    derivation rule, shared by migration synth. Kept out of the validator, which
    only checks membership, so the rule lives in exactly one place."""
    parts = str(path).split(".")
    if len(parts) < 2 or parts[0] != "resumeDoc":
        return None
    key = parts[1]
    if key in ("name", "contact"):
        return "identity"
    if key in ("headline", "summary"):
        return "statement"
    if key == "experience":
        return "experience-%s" % parts[2] if len(parts) > 2 else "experience"
    if key == "coreTech":
        return "skills"
    if key == "extras":
        return "extras"
    return key


def _section_path(section_id):
    if section_id == "identity":
        return "resumeDoc.contact"
    if section_id == "statement":
        return "resumeDoc.summary"
    if section_id == "skills":
        return "resumeDoc.coreTech"
    if section_id == "extras":
        return "resumeDoc.extras"
    if section_id.startswith("experience-"):
        return "resumeDoc.experience.%s" % section_id.split("-", 1)[1]
    return "resumeDoc.%s" % section_id


def _section_title(section_id):
    if section_id == "identity":
        return "Identity & contact"
    if section_id == "statement":
        return "Headline & summary"
    if section_id == "skills":
        return "Skills"
    if section_id == "extras":
        return "Extras"
    if section_id.startswith("experience-"):
        idx = section_id.split("-", 1)[1]
        return "Experience %s" % (int(idx) + 1) if idx.isdigit() else "Experience"
    return section_id[:1].upper() + section_id[1:]


def _synthesize_resume_sections(migrated):
    """Stamp each item's sectionId from its ctx.path and synthesize one unread,
    fresh whole-read per derived section, in first-seen order. Honest default for
    a report no agent has assessed yet."""
    order = []
    seen = set()
    for item in migrated.get("items") if isinstance(migrated.get("items"), list) else []:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("sectionId"), str) and item["sectionId"]:
            section_id = item["sectionId"]
        else:
            ctx = item.get("ctx") if isinstance(item.get("ctx"), dict) else {}
            section_id = _derive_section_id(ctx.get("path")) or "resume"
            item["sectionId"] = section_id
        if section_id not in seen:
            seen.add(section_id)
            order.append(section_id)
    if not isinstance(migrated.get("resumeSections"), list) or not migrated.get("resumeSections"):
        migrated["resumeSections"] = [
            {
                "sectionId": sid,
                "path": _section_path(sid),
                "title": _section_title(sid),
                "verdict": "unread",
                "status": "open",
                "staleness": "fresh",
                "assessment": "",
            }
            for sid in order
        ]


def migrate_report(data, target_version):
    """Return a validated-target copy; never mutate the caller's island."""
    migrated = copy.deepcopy(data)
    meta = migrated.get("meta") if isinstance(migrated.get("meta"), dict) else None
    if meta is None:
        return migrated
    source_version = meta.get("contractVersion")
    if source_version == target_version:
        return migrated
    if target_version != "2.4.0" or source_version not in ("2.0.0", "2.1.0", "2.2.0", "2.3.0"):
        return migrated
    if source_version == "2.0.0":
        meta["targetDecode"] = _unknown_target_decode()
        for item in migrated.get("items") if isinstance(migrated.get("items"), list) else []:
            if isinstance(item, dict):
                item["meta"] = {"scope": "atom", "visibility": "hotspot"}
    if source_version in ("2.0.0", "2.1.0"):
        meta["parseStatus"] = _default_parse_status()
    migrated.setdefault("rubric", [])
    _synthesize_resume_sections(migrated)
    meta["contractVersion"] = "2.4.0"
    return migrated

# The island and its contract, addressed exactly as the page addresses them:
# the `type="application/json" id="…"` anchor. Non-greedy to the first closing
# tag, so a re-splice touches one script element and nothing around it.
_ISLAND_RE = re.compile(
    r'(<script\b[^>]*\btype="application/json"[^>]*\bid="report-data"[^>]*>)'
    r"(.*?)(</script>)",
    re.S,
)
_CONTRACT_RE = re.compile(
    r'<script\b[^>]*\btype="application/json"[^>]*\bid="report-contract"[^>]*>'
    r"(.*?)</script>",
    re.S,
)


class ReportError(Exception):
    """A durable write that must not happen: the report, the args, or the
    contract said no. Raised before anything touches disk — the caller turns
    it into `{"ok": false, "error": …}` and the file is left as it was."""


class ReportStore:
    """The hosted report file — the bridge's durable store.

    One HTML artifact on disk, addressed through its realpath (a `--report`
    symlink resolves to the file it points at, so the write lands on the real
    file and the link survives). Every mutation is the same sequence: read the
    file, lift the `#report-data` island out by its anchor, mutate the parsed
    JSON in Python, validate the result against the file's OWN shipped
    `#report-contract` (the same gate the page runs at load — fail closed),
    then re-splice ONLY the island's text node back and swap the file in with
    os.replace. Template markup, the contract block, and every byte outside the
    island are carried through untouched.

    The lock serializes writers: concurrent commands can't interleave a
    read-modify-write and lose one of the two.
    """

    def __init__(self, path):
        self.path = os.path.realpath(path)
        self._lock = threading.Lock()

    def read_bytes(self):
        """The file as served — the same bytes a durable write produces."""
        with open(self.path, "rb") as fh:
            return fh.read()

    def report_id(self):
        """Non-PII page identity used to bind a tab/command to this store."""
        html = self.read_bytes().decode("utf-8")
        match = _ISLAND_RE.search(html)
        if match is None:
            return None
        try:
            data = json.loads(match.group(2))
        except ValueError:
            return None
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        value = meta.get("reportId")
        return value if isinstance(value, str) and value else None

    def validate(self):
        """Validate the hosted artifact before serving or reusing it."""
        try:
            html = self.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise ReportError("cannot read report %s: %s" % (self.path, exc))
        match = _ISLAND_RE.search(html)
        if match is None:
            raise ReportError("no #report-data island in %s — not a report page" % self.path)
        try:
            data = json.loads(match.group(2))
        except ValueError as exc:
            raise ReportError("#report-data is not valid JSON: %s" % exc)
        errs = validate_island(data, self._contract(html))
        if errs:
            raise ReportError("contract breach: %s" % "; ".join(errs))
        return data

    def apply(self, verb, args):
        """Run a durable verb end-to-end. Returns the applied change on
        success; raises ReportError having written nothing on any failure."""
        with self._lock:
            html = self.read_bytes().decode("utf-8")
            match = _ISLAND_RE.search(html)
            if match is None:
                raise ReportError(
                    "no #report-data island in %s — not a report page"
                    % self.path
                )
            try:
                data = json.loads(match.group(2))
            except ValueError as exc:
                raise ReportError("#report-data is not valid JSON: %s" % exc)

            if verb == "applyRewrite":  # advertised alias; the page aliases it too
                verb = "acceptRewrite"
            if verb == "updateItem":
                written = _update_item(data, args)
            elif verb == "setStatus":
                written = _set_status(data, args)
            elif verb == "acceptRewrite":
                written = _accept_rewrite(data, args)
            elif verb == "patchResume":
                written = _patch_resume(data, args)
            elif verb == "patchLinkedin":
                written = _patch_linkedin(data, args)
            elif verb == "rereadSection":
                written = _reread_section(data, args)
            else:  # unreachable while DURABLE_VERBS and this chain agree
                raise ReportError("not a durable verb: %s" % verb)

            errs = validate_island(data, self._contract(html))
            if errs:
                raise ReportError(
                    "contract breach — nothing written: %s" % "; ".join(errs)
                )
            self._write(html, match, data)
            return written

    def _contract(self, html):
        """The `#report-contract` shipped IN this file — the report validates
        against the contract it was built with, never one this bridge carries."""
        match = _CONTRACT_RE.search(html)
        if match is None:
            raise ReportError(
                "no #report-contract in %s — nothing to validate against"
                % self.path
            )
        try:
            return json.loads(match.group(1))
        except ValueError as exc:
            raise ReportError("#report-contract is not valid JSON: %s" % exc)

    def _write(self, html, match, data):
        """Re-splice the island and swap the file in atomically.

        Only group 2 — the island's text node — is replaced; the opening tag,
        the closing tag, and every other byte of the document are the original
        ones. The two sequences that let text escape a <script> element are
        neutralized as JSON escapes — `</` → `<\\/` and `<!--` → `\\u003c!--`,
        both identical to the browser on parse — so no résumé text can close
        the island early or flip the tokenizer into its escaped states. The
        temp file is written in the report's own directory and os.replace'd
        onto it: a reader sees the old file or the new one, never a partial.
        """
        island = _escape_island(json.dumps(data, ensure_ascii=False, indent=1))
        merged = html[: match.start(2)] + "\n" + island + "\n" + html[match.end(2) :]
        _atomic_write(self.path, merged)


def verb_arg(args, index, key):
    """One verb argument, positional array OR named object — the page's
    AGUIarg, ported, so both sides read the same call the same way."""
    if isinstance(args, list):
        return args[index] if index < len(args) else None
    if isinstance(args, dict):
        return args.get(key)
    return None


_MISSING = object()


def _get_path(root, path):
    """Walk a `resumeDoc.experience.0.bullets.3` data-path. `_MISSING` for a
    node that isn't there — the page's getPath returning undefined."""
    node = root
    for part in str(path).split("."):
        if isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return _MISSING
        elif isinstance(node, dict):
            if part not in node:
                return _MISSING
            node = node[part]
        else:
            return _MISSING
    return node


def _update_item(data, args):
    """updateItem(n, patch): merge `patch`'s fields into the item addressed by
    n — the line-item content edit. `n` and `status` are refused: n IS the
    address, and status has its own shared path (setStatus / the tri-state
    click) that the island alone can't keep straight."""
    n = verb_arg(args, 0, "n")
    patch = verb_arg(args, 1, "patch")
    if not isinstance(n, int) or isinstance(n, bool):
        raise ReportError('updateItem needs (n, patch) — n must be an integer')
    if not isinstance(patch, dict):
        raise ReportError("updateItem patch must be an object of fields to set")
    if not patch:
        raise ReportError("updateItem patch is empty — nothing to set")
    allowed = {"reason", "suggestion", "verdict", "rewrite", "prompt", "decisions", "questions"}
    refused = sorted(set(patch) - allowed)
    if refused:
        raise ReportError("updateItem cannot set: %s" % ", ".join(refused))
    items = data.get("items")
    if not isinstance(items, list):
        raise ReportError("island has no items array")
    for item in items:
        if isinstance(item, dict) and item.get("n") == n:
            for key, value in patch.items():
                if key in ("decisions", "questions"):
                    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                        raise ReportError("updateItem %s must be an array of strings" % key)
                    item.setdefault("ctx", {})[key] = value
                else:
                    item[key] = value
            _mark_section_stale(data, n)
            return {"n": n, "fields": sorted(patch)}
    raise ReportError("no item %s" % n)


def _mark_section_stale(data, n):
    """After a durable child edit, flag its assessed parent section stale so the
    page shows a re-read is pending. An unread section is left untouched; workflow
    changes (setStatus) never mark stale."""
    section_id = None
    for item in data.get("items") or []:
        if isinstance(item, dict) and item.get("n") == n:
            section_id = item.get("sectionId")
            break
    if not isinstance(section_id, str):
        return
    for section in data.get("resumeSections") or []:
        if isinstance(section, dict) and section.get("sectionId") == section_id and section.get("verdict") != "unread":
            section["staleness"] = "stale"
            return


def _reread_section(data, args):
    """rereadSection(sectionId, patch): the agent's post-accept re-read — rewrite
    the whole-read's verdict/status/assessment and clear staleness to fresh.
    staleness is system-managed and cannot be set through the patch."""
    section_id = verb_arg(args, 0, "sectionId")
    patch = verb_arg(args, 1, "patch")
    if not isinstance(section_id, str) or not section_id:
        raise ReportError("rereadSection needs (sectionId, patch) — sectionId must be a non-empty string")
    if not isinstance(patch, dict):
        raise ReportError("rereadSection patch must be an object of fields to set")
    allowed = {"verdict", "status", "assessment"}
    refused = sorted(set(patch) - allowed)
    if refused:
        raise ReportError("rereadSection cannot set: %s" % ", ".join(refused))
    sections = data.get("resumeSections")
    if not isinstance(sections, list):
        raise ReportError("island has no resumeSections array")
    for section in sections:
        if isinstance(section, dict) and section.get("sectionId") == section_id:
            for key, value in patch.items():
                section[key] = value
            section["staleness"] = "fresh"
            return {"sectionId": section_id, "fields": sorted(patch), "staleness": "fresh"}
    raise ReportError("no resumeSection %s" % section_id)


def _find_item(data, n, verb):
    if not isinstance(n, int) or isinstance(n, bool):
        raise ReportError("%s needs an integer item n" % verb)
    for item in data.get("items") or []:
        if isinstance(item, dict) and item.get("n") == n:
            return item
    raise ReportError("no item %s" % n)


def _set_status(data, args):
    n = verb_arg(args, 0, "n")
    status = verb_arg(args, 1, "status")
    if status not in STATUS_VALUES:
        raise ReportError("setStatus status must be open|done|ignore")
    item = _find_item(data, n, "setStatus")
    item["status"] = status
    return {"n": n, "status": status}


def _same_path(a, b):
    """The page's samePath, ported: equal, or one is the other's ancestor."""
    return a == b or a.startswith(b + ".") or b.startswith(a + ".")


def _evidence_text(value):
    """The page's evText, ported: one résumé node as a readable line."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("label"), str) and isinstance(value.get("items"), list):
        return "%s: %s" % (value["label"], ", ".join(str(v) for v in value["items"]))
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return "" if value is None or value is _MISSING else str(value)


def _set_doc_path(data, path, text, roots):
    """Set one leaf under a writable document. `roots` names which prefixes are
    legal for this caller, so a patch verb stays confined to its own document
    while acceptRewrite follows the target it was given."""
    root = next((r for r in roots if isinstance(path, str) and path.startswith(r)), None)
    if root is None:
        raise ReportError("path must be %s" % " or ".join(r + "*" for r in roots))
    label = DOC_ROOTS[root]
    if not isinstance(data.get(root[:-1]), dict):
        raise ReportError("no %s document in this report" % label)
    if not isinstance(text, str):
        raise ReportError("%s text must be a string" % label)
    parts = path.split(".")
    parent = _get_path(data, ".".join(parts[:-1]))
    leaf = parts[-1]
    if isinstance(parent, list):
        try:
            index = int(leaf)
            parent[index]
        except (ValueError, IndexError):
            raise ReportError("no %s node at %s" % (label, path))
        parent[index] = text
    elif isinstance(parent, dict) and leaf in parent:
        parent[leaf] = text
    else:
        raise ReportError("no %s node at %s" % (label, path))


def _set_resume_path(data, path, text):
    _set_doc_path(data, path, text, ("resumeDoc.",))


def _accept_rewrite(data, args):
    n = verb_arg(args, 0, "n")
    index = verb_arg(args, 1, "index")
    if index is None:
        index = 0
    if not isinstance(index, int) or isinstance(index, bool):
        raise ReportError("acceptRewrite index must be an integer")
    item = _find_item(data, n, "acceptRewrite")
    rewrites = item.get("rewrite")
    if not isinstance(rewrites, list) or index < 0 or index >= len(rewrites):
        raise ReportError("acceptRewrite has no rewrite %s for item %s" % (index, n))
    chosen = rewrites[index]
    text = chosen.get("txt") if isinstance(chosen, dict) else None
    _set_doc_path(data, item.get("target"), text, ("resumeDoc.", "linkedinDoc."))
    ctx = item.get("ctx")
    if not isinstance(ctx, dict) or not isinstance(ctx.get("decisions"), list):
        raise ReportError("item %s has no ctx.decisions array" % n)
    ctx["decisions"].append("accepted-rewrite:%s" % index)
    item["status"] = "done"
    _mark_section_stale(data, n)
    return {"n": n, "index": index, "target": item.get("target"), "status": "done"}


def _patch_resume(data, args):
    """patchResume(path, text): set a `resumeDoc.*` node — the page's verb,
    same guards, but landing on disk."""
    path = verb_arg(args, 0, "path")
    text = verb_arg(args, 1, "text")
    _set_resume_path(data, path, text)
    return {"path": path, "text": text}


def _patch_linkedin(data, args):
    """patchLinkedin(path, text): set a `linkedinDoc.*` node. Same guards as
    patchResume against the report's other writable document."""
    path = verb_arg(args, 0, "path")
    text = verb_arg(args, 1, "text")
    _set_doc_path(data, path, text, ("linkedinDoc.",))
    return {"path": path, "text": text}


def derive_decision(ats, screener, manager, urgency_quote=None):
    """Total Must-Talk and move-forward rule; ordered, deterministic."""
    if ats == "fail":
        score, gate = 0, "ats"
    elif ats == "risky" or screener == "no-call" or manager == "no":
        score, gate = 1, "ats" if ats == "risky" else "screener" if screener == "no-call" else "manager"
    elif ats == "weak-pass" or screener == "maybe" or manager == "insufficient":
        score, gate = 2, "ats" if ats == "weak-pass" else "screener" if screener == "maybe" else "manager"
    elif urgency_quote and (screener == "urgent-call" or manager == "priority-interview"):
        score, gate = 4, "urgency"
    else:
        score, gate = 3, "ats"
    return {"mustTalk": score, "moveForward": "no" if score < 2 else "not yet" if score == 2 else "yes", "decidingGate": gate}


def _contains_resume_doc(value, depth=0):
    """Recognize a resumeDoc even through JSON strings/lists/wrappers."""
    if depth > 64:
        return False
    if isinstance(value, dict):
        if "name" in value and "experience" in value:
            return True
        return any(_contains_resume_doc(v, depth + 1) for v in value.values())
    if isinstance(value, list):
        return any(_contains_resume_doc(v, depth + 1) for v in value)
    if isinstance(value, str):
        candidates = [value]
        if "{" in value and "}" in value:
            candidates.append(value[value.find("{"):value.rfind("}") + 1])
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
            except ValueError:
                continue
            if parsed != value and _contains_resume_doc(parsed, depth + 1):
                return True
    return False


def _exact_keys(value, keys):
    return isinstance(value, dict) and set(value) == set(keys)


def _keys_within(value, required, optional):
    """Byte-parallel to the page's keysWithin: every required key present, every
    other key drawn from the closed optional set."""
    if not isinstance(value, dict):
        return False
    present = set(value)
    return set(required) <= present and present <= set(required) | set(optional)


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_item_ids(value, item_ids):
    return (
        isinstance(value, list)
        and all(isinstance(v, int) and not isinstance(v, bool) for v in value)
        and len(value) == len(set(value))
        and all(v in item_ids for v in value)
    )


def _validate_target_decode(meta, item_ids):
    errs = []
    decode = meta.get("targetDecode")
    if not _exact_keys(decode, TARGET_DECODE_KEYS):
        return ["meta.targetDecode must have exactly buyingNeed,jdSupport"]

    need = decode["buyingNeed"]
    if not _exact_keys(need, BUYING_NEED_KEYS):
        errs.append("meta.targetDecode.buyingNeed has invalid shape")
    else:
        status = need.get("status")
        if status not in BUYING_STATUS_VALUES:
            errs.append("meta.targetDecode.buyingNeed.status has invalid value")
        for key in ("statement", "beneficiary", "constraint", "confirmingQuestion"):
            if need.get(key) is not None and not isinstance(need.get(key), str):
                errs.append("meta.targetDecode.buyingNeed.%s has invalid type" % key)
        evidence = need.get("evidence")
        evidence_ok = isinstance(evidence, list) and len(evidence) <= 3
        if evidence_ok:
            for record in evidence:
                if not _exact_keys(record, ("source", "quote")) or record.get("source") not in EVIDENCE_SOURCE_VALUES or not _nonempty(record.get("quote")):
                    evidence_ok = False
                    break
        if not evidence_ok:
            errs.append("meta.targetDecode.buyingNeed.evidence has invalid shape")
            evidence = []
        if _contains_resume_doc(evidence):
            errs.append("meta.targetDecode must not embed resumeDoc")
        evidence_blob = " ".join(record.get("quote", "") for record in evidence if isinstance(record, dict))
        if re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", evidence_blob) or re.search(r"(?:\+?\d[\d(). -]{7,}\d)", evidence_blob):
            errs.append("meta.targetDecode must not contain contact PII")
        if status == "unknown" and not (
            need.get("statement") == ""
            and need.get("beneficiary") is None
            and need.get("constraint") is None
            and evidence == []
            and _nonempty(need.get("confirmingQuestion"))
        ):
            errs.append("meta.targetDecode.buyingNeed unknown invariant failed")
        elif status == "inferred" and not (
            _nonempty(need.get("statement"))
            and any(record.get("source") == "jd" for record in evidence if isinstance(record, dict))
            and _nonempty(need.get("confirmingQuestion"))
        ):
            errs.append("meta.targetDecode.buyingNeed inferred invariant failed")
        elif status == "confirmed":
            core = (need.get("statement"), need.get("beneficiary"), need.get("constraint"))
            source_confirms = any(
                isinstance(record, dict)
                and record.get("source") in EVIDENCE_SOURCE_VALUES
                and all(isinstance(part, str) and part.lower() in record.get("quote", "").lower() for part in core)
                for record in evidence
            )
            if not (all(_nonempty(part) for part in core) and need.get("confirmingQuestion") is None and source_confirms):
                errs.append("meta.targetDecode.buyingNeed confirmed invariant failed")

    support = decode["jdSupport"]
    if not _exact_keys(support, JD_SUPPORT_KEYS):
        return errs + ["meta.targetDecode.jdSupport has invalid shape"]
    non_negotiables = support.get("nonNegotiables")
    if not isinstance(non_negotiables, list):
        errs.append("meta.targetDecode.jdSupport.nonNegotiables must be an array")
    else:
        for idx, record in enumerate(non_negotiables):
            if not _exact_keys(record, ("need", "status", "itemIds")) or not _nonempty(record.get("need")) or record.get("status") not in NON_NEGOTIABLE_VALUES or not _valid_item_ids(record.get("itemIds"), item_ids):
                errs.append("meta.targetDecode.jdSupport.nonNegotiables[%s] is invalid" % idx)
    central = support.get("centralProblem")
    if not _exact_keys(central, ("status", "itemIds")) or central.get("status") not in CENTRAL_PROBLEM_VALUES or not _valid_item_ids(central.get("itemIds"), item_ids):
        errs.append("meta.targetDecode.jdSupport.centralProblem is invalid")
    differentiator = support.get("differentiator")
    if differentiator is not None and (
        not _exact_keys(differentiator, ("statement", "itemIds"))
        or not _nonempty(differentiator.get("statement"))
        or not _valid_item_ids(differentiator.get("itemIds"), item_ids)
        or not differentiator.get("itemIds")
    ):
        errs.append("meta.targetDecode.jdSupport.differentiator is invalid")
    repair = support.get("smallestTruthfulRepair")
    if repair is not None:
        valid_shape = _exact_keys(repair, ("itemId", "action", "instruction", "truth"))
        valid_ref = valid_shape and repair.get("itemId") in item_ids
        valid_instruction = valid_shape and _nonempty(repair.get("instruction"))
        valid_pair = valid_shape and (
            (repair.get("truth") == "confirmed" and repair.get("action") in REPAIR_CONFIRMED_ACTIONS)
            or (repair.get("truth") == "needs-confirmation" and repair.get("action") == "confirm" and "?" in repair.get("instruction", ""))
        )
        if not (valid_shape and valid_ref and valid_instruction and valid_pair):
            errs.append("meta.targetDecode.jdSupport.smallestTruthfulRepair is invalid")
    return errs


def _validate_parse_status(meta):
    """Byte-parallel to the page's validateParseStatus (report-template.html):
    same checks, same error strings, so the two ports never diverge. parseStatus
    is descriptive metadata — it is validated for shape but never enters the
    decision vector or Must-Talk."""
    status = meta.get("parseStatus")
    if not _exact_keys(status, PARSE_STATUS_KEYS):
        return ["meta.parseStatus must have exactly state,affectsAts,evidence"]
    errs = []
    state = status.get("state")
    affects = status.get("affectsAts")
    evidence = status.get("evidence")
    if state not in PARSE_STATE_VALUES:
        errs.append("meta.parseStatus.state has invalid value")
    if not isinstance(affects, bool):
        errs.append("meta.parseStatus.affectsAts must be a boolean")
    if state == "untested":
        if affects is not False or evidence is not None:
            errs.append("meta.parseStatus untested invariant failed")
    elif state == "tested":
        if (
            not _exact_keys(evidence, PARSE_EVIDENCE_KEYS)
            or evidence.get("source") not in PARSE_EVIDENCE_SOURCES
            or not _nonempty(evidence.get("ref"))
            or not _nonempty(evidence.get("observed"))
        ):
            errs.append("meta.parseStatus tested evidence invalid")
    readers = meta.get("readers")
    ats_evidence = (
        readers[0].get("evidence")
        if isinstance(readers, list) and readers and isinstance(readers[0], dict) and isinstance(readers[0].get("evidence"), str)
        else ""
    )
    lowered = ats_evidence.lower()
    if state == "untested":
        for term in PARSE_CLAIM_TERMS:
            if term in lowered:
                errs.append("meta.parseStatus untested but ATS evidence claims parser behavior: %s" % term)
    if state == "tested" and affects is True and _exact_keys(evidence, PARSE_EVIDENCE_KEYS):
        ref = evidence.get("ref") if isinstance(evidence.get("ref"), str) else ""
        if ref and ref not in ats_evidence:
            errs.append("meta.parseStatus tested affectsAts requires the ATS reader evidence to cite the observed source")
    return errs


_MISSING = object()


def _resolve_resume_path(data, path):
    """Walk a `resumeDoc.…` dot-path from the island root, parallel to the page's
    reduce over pathGet. Returns _MISSING when any segment is absent; a resolved
    JSON null is a hit (matches the JS `!==undefined` test)."""
    cur = data
    for part in str(path).split("."):
        if isinstance(cur, dict):
            if part in cur:
                cur = cur[part]
            else:
                return _MISSING
        elif isinstance(cur, list):
            if part.isdigit() and int(part) < len(cur):
                cur = cur[int(part)]
            else:
                return _MISSING
        else:
            return _MISSING
    return cur


def _validate_rubric(data, meta):
    """Byte-parallel to the page's validateRubric (report-template.html): the
    demonstrated-skill rubric is a top-level structure, not items[] rows. Each
    competency cites resumeDoc evidence by path; grades never enter the decision
    vector or Must-Talk."""
    rub = data.get("rubric")
    if not isinstance(rub, list):
        return ["rubric must be an array"]
    errs = []
    if meta.get("mode") != "skillmatch" and rub:
        errs.append("rubric must be empty unless mode is skillmatch")
    posting_ids = _jd_posting_ids(data)
    for i, entry in enumerate(rub):
        if not _keys_within(entry, RUBRIC_KEYS, RUBRIC_OPTIONAL_KEYS):
            errs.append("rubric[%s] must have exactly competency,grade,evidenceIds,gaps" % i)
            continue
        if not _nonempty(entry.get("competency")):
            errs.append("rubric[%s] competency must be non-empty" % i)
        grade = entry.get("grade")
        # Mirror the page's Number.isInteger: an integer-valued number in 0..5,
        # never a bool. 3.0 is accepted (JSON has no int/float distinction on the
        # JS side); "3" and 3.5 are rejected on both ports.
        if not (
            isinstance(grade, (int, float))
            and not isinstance(grade, bool)
            and float(grade).is_integer()
            and 0 <= grade <= 5
        ):
            errs.append("rubric[%s] grade must be an integer 0-5" % i)
        evidence_ids = entry.get("evidenceIds")
        if not (
            isinstance(evidence_ids, list)
            and evidence_ids
            and all(
                isinstance(p, str)
                and p.startswith("resumeDoc.")
                and _resolve_resume_path(data, p) is not _MISSING
                for p in evidence_ids
            )
        ):
            errs.append("rubric[%s] evidenceIds must be non-empty resumeDoc paths that resolve" % i)
        gaps = entry.get("gaps")
        if not (isinstance(gaps, list) and all(isinstance(g, str) for g in gaps)):
            errs.append("rubric[%s] gaps must be an array of strings" % i)
        if "bar" in entry:
            errs.extend(_validate_bar(entry["bar"], "rubric[%s] bar" % i, posting_ids))
        if "standing" in entry:
            if entry.get("standing") not in STANDING_VALUES:
                errs.append("rubric[%s] standing has invalid value" % i)
            if "bar" not in entry:
                errs.append("rubric[%s] standing requires a bar" % i)
    return errs


def _jd_posting_ids(data):
    jds = data.get("jdSet")
    if not isinstance(jds, list):
        return []
    return [
        e.get("postingId")
        for e in jds
        if isinstance(e, dict) and _nonempty(e.get("postingId"))
    ]


def _validate_bar(bar, label, posting_ids, keys=BAR_KEYS):
    """Byte-parallel to the page's validateBar. Shared by rubric[].bar and
    openBars[] — the first four keys are identical, so one checker serves both."""
    errs = []
    if not _exact_keys(bar, keys):
        errs.append("%s must have exactly %s" % (label, ",".join(keys)))
        return errs
    requirement = bar.get("requirement")
    if not (_nonempty(requirement) and len(requirement) <= 400):
        errs.append("%s requirement must be non-empty within 400 characters" % label)
    level = bar.get("level")
    if not (level is None or (isinstance(level, str) and len(level) <= 120)):
        errs.append("%s level must be a string within 120 characters or null" % label)
    rng = bar.get("range")
    if not (rng is None or (isinstance(rng, str) and len(rng) <= 160)):
        errs.append("%s range must be a string within 160 characters or null" % label)
    sources = bar.get("sources")
    if not (
        isinstance(sources, list)
        and sources
        and len(sources) == len(set(s for s in sources if isinstance(s, str)))
        and all(isinstance(s, str) and s in posting_ids for s in sources)
    ):
        errs.append("%s sources must be unique postingIds that resolve in jdSet" % label)
    elif rng is not None and len(sources) < 2:
        errs.append("%s range requires at least two sources" % label)
    if not posting_ids:
        errs.append("%s requires a non-empty jdSet" % label)
    if "question" in keys:
        question = bar.get("question")
        if not (_nonempty(question) and len(question) <= 240):
            errs.append("%s question must be non-empty within 240 characters" % label)
    return errs


def _validate_jd_set(data):
    """Byte-parallel to the page's validateJdSet. The supplied postings; every
    bar's sources resolve here, and N-of-M is derived from lengths, never stored."""
    if "jdSet" not in data:
        return []
    jds = data.get("jdSet")
    if not isinstance(jds, list):
        return ["jdSet must be an array"]
    errs = []
    seen = set()
    for i, entry in enumerate(jds):
        if not _exact_keys(entry, JD_SET_KEYS):
            errs.append(
                "jdSet [%s] must have exactly postingId,label,archetype,archetypeStatus,experience" % i
            )
            continue
        pid = entry.get("postingId")
        ref = pid if _nonempty(pid) else i
        if not (_nonempty(pid) and len(pid) <= 80):
            errs.append("jdSet %s postingId must be non-empty within 80 characters" % ref)
        elif pid in seen:
            errs.append("duplicate jdSet postingId %s" % pid)
        else:
            seen.add(pid)
        label = entry.get("label")
        if not (_nonempty(label) and len(label) <= 120):
            errs.append("jdSet %s label must be non-empty within 120 characters" % ref)
        if entry.get("archetype") not in JD_ARCHETYPE_VALUES:
            errs.append("jdSet %s archetype has invalid value" % ref)
        if entry.get("archetypeStatus") not in JD_ARCHETYPE_STATUS_VALUES:
            errs.append("jdSet %s archetypeStatus has invalid value" % ref)
        exp = entry.get("experience")
        if not (exp is None or (isinstance(exp, str) and len(exp) <= 80)):
            errs.append("jdSet %s experience must be a string within 80 characters or null" % ref)
    named = set()
    for entry in (data.get("rubric") or []):
        if isinstance(entry, dict) and isinstance(entry.get("bar"), dict):
            for s in (entry["bar"].get("sources") or []):
                named.add(s)
    for entry in (data.get("openBars") or []):
        if isinstance(entry, dict):
            for s in (entry.get("sources") or []):
                named.add(s)
    if named:
        for pid in seen:
            if pid not in named:
                errs.append("jdSet %s is named by no bar" % pid)
    return errs


def _validate_open_bars(data, meta):
    """Byte-parallel to the page's validateOpenBars: one entry per JD requirement
    with no applicant evidence. A requirement is either graded or open, never both."""
    if "openBars" not in data:
        return []
    obs = data.get("openBars")
    if not isinstance(obs, list):
        return ["openBars must be an array"]
    errs = []
    if meta.get("mode") != "skillmatch" and obs:
        errs.append("openBars must be empty unless mode is skillmatch")
    posting_ids = _jd_posting_ids(data)
    for i, entry in enumerate(obs):
        errs.extend(_validate_bar(entry, "openBars [%s]" % i, posting_ids, OPEN_BAR_KEYS))
    seen = set()
    dupes = []
    for entry in (data.get("rubric") or []):
        if isinstance(entry, dict) and isinstance(entry.get("bar"), dict):
            req = entry["bar"].get("requirement")
            if isinstance(req, str):
                (dupes.append(req) if req in seen else seen.add(req))
    for entry in obs:
        if isinstance(entry, dict):
            req = entry.get("requirement")
            if isinstance(req, str):
                (dupes.append(req) if req in seen else seen.add(req))
    for req in dupes:
        errs.append("duplicate bar requirement %s" % req)
    return errs


def _validate_resume_sections(data):
    """The page's validateResumeSections, ported: same checks, SAME error strings.
    Each whole-read is exactly 7 keys; every item's sectionId must resolve here."""
    errs = []
    sections = data.get("resumeSections")
    if not isinstance(sections, list):
        errs.append("resumeSections must be an array")
        return errs
    sec_ids = set()
    for i, s in enumerate(sections):
        if not _exact_keys(s, RESUME_SECTION_KEYS):
            errs.append("resumeSection [%s] must have exactly sectionId,path,title,verdict,status,staleness,assessment" % i)
            continue
        raw_id = s.get("sectionId")
        sid = raw_id if isinstance(raw_id, str) and raw_id.strip() else i
        if not (isinstance(raw_id, str) and raw_id.strip()):
            errs.append("resumeSection [%s] sectionId must be non-empty" % i)
        elif raw_id in sec_ids:
            errs.append("duplicate resumeSection sectionId %s" % raw_id)
        else:
            sec_ids.add(raw_id)
        path = s.get("path")
        if not isinstance(path, str) or not path.startswith("resumeDoc.") or len(path) > 256:
            errs.append("resumeSection %s path must be a resumeDoc path within 256 characters" % sid)
        title = s.get("title")
        if not isinstance(title, str) or not title.strip() or len(title) > 80:
            errs.append("resumeSection %s title must be non-empty within 80 characters" % sid)
        if s.get("verdict") not in SECTION_VERDICT_VALUES:
            errs.append("resumeSection %s verdict has invalid value" % sid)
        if s.get("status") not in STATUS_VALUES:
            errs.append("resumeSection %s status has invalid value" % sid)
        if s.get("staleness") not in SECTION_STALENESS_VALUES:
            errs.append("resumeSection %s staleness has invalid value" % sid)
        assessment = s.get("assessment")
        if not isinstance(assessment, str) or len(assessment) > 800:
            errs.append("resumeSection %s assessment must be a string within 800 characters" % sid)
        if s.get("staleness") == "stale" and s.get("verdict") == "unread":
            errs.append("resumeSection %s stale requires an assessed verdict" % sid)
        if assessment == "" and s.get("verdict") != "unread":
            errs.append("resumeSection %s assessment must be non-empty unless unread" % sid)
    for item in data.get("items") or []:
        if not isinstance(item, dict) or "sectionId" not in item:
            continue
        if not isinstance(item.get("sectionId"), str) or item["sectionId"] not in sec_ids:
            errs.append("item %s sectionId “%s” not in resumeSections" % (item.get("n", "?"), item.get("sectionId")))
    return errs


def _strings(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _validate_linkedin_doc(data):
    """The page's validateLinkedinDoc, ported: same checks, SAME error strings.
    The LinkedIn document is optional — an island with no `linkedinDoc` key is
    untouched here. When present it is writable through patchLinkedin, so every
    node a patch can land on is typed before the island is accepted."""
    if "linkedinDoc" not in data:
        return []
    doc = data.get("linkedinDoc")
    if not isinstance(doc, dict) or not doc:
        return ["linkedinDoc must be a non-empty object"]
    errs = []
    for key in sorted(doc):
        if key not in LINKEDIN_DOC_KEYS:
            errs.append("linkedinDoc has unknown key “%s”" % key)
    for key in ("headline", "about"):
        if key in doc and not isinstance(doc[key], str):
            errs.append("linkedinDoc.%s must be a string" % key)
    if "skills" in doc and not _strings(doc["skills"]):
        errs.append("linkedinDoc.skills must be an array of strings")
    if "experience" in doc:
        experience = doc["experience"]
        if not isinstance(experience, list):
            errs.append("linkedinDoc.experience must be an array")
        else:
            for i, role in enumerate(experience):
                if not (
                    isinstance(role, dict)
                    and set(role) <= {"org", "role", "dates", "bullets"}
                    and all(isinstance(role.get(k), str) for k in ("org", "role", "dates"))
                    and _strings(role.get("bullets"))
                ):
                    errs.append("linkedinDoc.experience %s needs string org, role, dates and a bullets array of strings" % i)
    if "extras" in doc:
        extras = doc["extras"]
        if not isinstance(extras, list):
            errs.append("linkedinDoc.extras must be an array")
        else:
            for i, extra in enumerate(extras):
                if not (
                    isinstance(extra, dict)
                    and set(extra) == {"title", "items"}
                    and isinstance(extra.get("title"), str)
                    and _strings(extra.get("items"))
                ):
                    errs.append("linkedinDoc.extras %s needs a string title and an items array of strings" % i)
    return errs


def _validate_craft(data, item_ids):
    """The page's validateCraft, ported: same checks, SAME error strings. The
    craft axis is optional — an island with no `craft` key is untouched here, and
    `craft: []` is clean. Grades never enter the decision vector or Must-Talk."""
    if "craft" not in data:
        return []
    craft = data.get("craft")
    if not isinstance(craft, list):
        return ["craft must be an array"]
    errs = []
    paths = set()
    for i, entry in enumerate(craft):
        if not _exact_keys(entry, CRAFT_KEYS):
            errs.append("craft [%s] must have exactly path,element,grade,bars,itemIds" % i)
            continue
        path = entry.get("path")
        cid = path if _nonempty(path) else i
        if not isinstance(path, str) or not path.startswith("resumeDoc.") or len(path) > 256:
            errs.append("craft %s path must be a resumeDoc path within 256 characters" % cid)
        elif path in paths:
            errs.append("duplicate craft path %s" % path)
        else:
            paths.add(path)
        if entry.get("element") not in CRAFT_ELEMENT_VALUES:
            errs.append("craft %s element has invalid value" % cid)
        grade = entry.get("grade")
        if grade not in CRAFT_GRADE_VALUES:
            errs.append("craft %s grade has invalid value" % cid)
        bars = entry.get("bars")
        if not isinstance(bars, list) or not bars or len(bars) > 20:
            errs.append("craft %s bars must be a non-empty array within 20 entries" % cid)
        else:
            for j, bar in enumerate(bars):
                if not _exact_keys(bar, CRAFT_BAR_KEYS):
                    errs.append("craft %s bar [%s] must have exactly bar,grade,note" % (cid, j))
                    continue
                name = bar.get("bar")
                if not _nonempty(name) or len(name) > 80:
                    errs.append("craft %s bar [%s] bar must be non-empty within 80 characters" % (cid, j))
                if bar.get("grade") not in CRAFT_GRADE_VALUES:
                    errs.append("craft %s bar [%s] grade has invalid value" % (cid, j))
                note = bar.get("note")
                if not isinstance(note, str) or len(note) > 240:
                    errs.append("craft %s bar [%s] note must be a string within 240 characters" % (cid, j))
        # Mirror the page's Number.isInteger test: never a bool, and an
        # integer-valued float resolves the same as its integer (JSON has no
        # int/float distinction on the JS side).
        ids_value = entry.get("itemIds")
        if not (
            isinstance(ids_value, list)
            and all(
                isinstance(v, (int, float))
                and not isinstance(v, bool)
                and float(v).is_integer()
                and int(v) in item_ids
                for v in ids_value
            )
        ):
            errs.append("craft %s itemIds must resolve to existing items" % cid)
        elif grade == "winning" and ids_value:
            errs.append("craft %s winning carries no itemIds" % cid)
        elif grade in ("below-bar", "median") and not ids_value:
            errs.append("craft %s %s needs at least one itemId" % (cid, grade))
    return errs


def validate_island(data, contract):
    """The page's load-time contract gate, ported to Python: same checks, same
    fail-closed posture, so the bridge can never write an island the page would
    then refuse to render. Returns the list of breaches — empty means clean."""
    if not isinstance(data, dict):
        return ["DATA root must be an object"]
    errs = []
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    if meta.get("contractVersion") != contract.get("version"):
        errs.append(
            "built for contract %s, this report is %s"
            % (meta.get("contractVersion") or "‹none›", contract.get("version"))
        )
    for key, kind in (contract.get("top") or {}).items():
        value = data.get(key)
        ok = (
            isinstance(value, list)
            if kind == "array"
            else isinstance(value, dict) and bool(value)
        )
        if not ok:
            errs.append(
                "DATA.%s must be %s%s"
                % (
                    key,
                    kind,
                    " (island omits it)" if key not in data else " (wrong type)",
                )
            )
    if any(error.startswith("DATA.") for error in errs):
        return errs
    sections = set()
    for section in data.get("sections") or []:
        section_id = section.get("id") if isinstance(section, dict) else None
        if not isinstance(section_id, str) or not section_id:
            errs.append("section id must be a non-empty string")
        else:
            sections.add(section_id)
    required = ((contract.get("item") or {}).get("required")) or []
    for item in data.get("items") or []:
        if not isinstance(item, dict):
            errs.append("items holds a non-object entry")
            continue
        for key in required:
            if key not in item:
                errs.append("item %s missing “%s”" % (item.get("n", "?"), key))
        if "section" in item and not isinstance(item["section"], str):
            errs.append("item %s section must be a string" % item.get("n", "?"))
        elif item.get("section") and item["section"] not in sections:
            errs.append(
                "item %s section “%s” not in sections"
                % (item.get("n", "?"), item["section"])
            )
        # item.field — every fields[] entry carries each declared key
        for entry in (item.get("fields") if isinstance(item.get("fields"), list) else []):
            for key in ((contract.get("item") or {}).get("field")) or []:
                if not isinstance(entry, dict) or key not in entry:
                    errs.append(
                        "item %s field entry missing “%s”" % (item.get("n", "?"), key)
                    )
        # perSection — section-specific refinements (rewriteWhen · needFields)
        per = (contract.get("perSection") or {}).get(item.get("section")) if isinstance(item.get("section"), str) else None
        if isinstance(per, dict):
            when = per.get("rewriteWhen")
            if when and item.get("verdict") in when.split("|"):
                rewrite = item.get("rewrite")
                if not (isinstance(rewrite, list) and rewrite):
                    errs.append(
                        "item %s verdict “%s” needs rewrite[]"
                        % (item.get("n", "?"), item.get("verdict"))
                    )
            fields = item.get("fields") if isinstance(item.get("fields"), list) else []
            for need in (per.get("needFields") or []):
                if not any(isinstance(f, dict) and f.get("k") == need for f in fields):
                    errs.append(
                        "item %s missing “%s” field" % (item.get("n", "?"), need)
                    )
    doc = data.get("resumeDoc") if isinstance(data.get("resumeDoc"), dict) else {}
    for key in ((contract.get("resumeDoc") or {}).get("required")) or []:
        if not doc.get(key):
            errs.append("resumeDoc missing “%s”" % key)
    # resumeDoc.experienceRow — every experience[] entry carries each declared key
    experience = doc.get("experience") if isinstance(doc.get("experience"), list) else []
    for idx, row in enumerate(experience):
        for key in ((contract.get("resumeDoc") or {}).get("experienceRow")) or []:
            if not isinstance(row, dict) or not row.get(key):
                errs.append("resumeDoc.experience[%s] missing “%s”" % (idx, key))

    # v2 decision/editorial contract. Keep this order mirrored in template JS.
    mode = meta.get("mode")
    if mode not in MODE_VALUES:
        errs.append("meta.mode must be quick-scan|standard|rewrite|skillmatch")
    decision = meta.get("decision") if isinstance(meta.get("decision"), dict) else {}
    gates = decision.get("gates") if isinstance(decision.get("gates"), dict) else {}
    for key, values in (("ats", ATS_VALUES), ("screener", SCREENER_VALUES), ("manager", MANAGER_VALUES)):
        if gates.get(key) not in values:
            errs.append("meta.decision.gates.%s has invalid value" % key)
    if decision.get("moveForward") not in ("yes", "not yet", "no"):
        errs.append("meta.decision.moveForward has invalid value")
    if not isinstance(decision.get("reason"), str) or not decision.get("reason", "").strip():
        errs.append("meta.decision.reason must be non-empty")
    quote = decision.get("urgencyQuote")
    if quote is not None and (not isinstance(quote, str) or not quote.strip()):
        errs.append("meta.decision.urgencyQuote must be null or non-empty string")
    if all(gates.get(k) in v for k, v in (("ats", ATS_VALUES), ("screener", SCREENER_VALUES), ("manager", MANAGER_VALUES))):
        expected = derive_decision(gates["ats"], gates["screener"], gates["manager"], quote)
        if decision.get("mustTalk") != expected["mustTalk"]:
            errs.append("meta.decision.mustTalk disagrees with gate rule")
        if decision.get("moveForward") != expected["moveForward"]:
            errs.append("meta.decision.moveForward disagrees with gate rule")
    reason = decision.get("reason", "") if isinstance(decision.get("reason"), str) else ""
    reason_lower = reason.lower()
    if reason and all(gates.get(k) in v for k, v in (("ats", ATS_VALUES), ("screener", SCREENER_VALUES), ("manager", MANAGER_VALUES))):
        decisive = derive_decision(gates["ats"], gates["screener"], gates["manager"], quote)["decidingGate"]
        if (decisive == "urgency" and not (quote and quote in reason)) or (decisive != "urgency" and decisive not in reason_lower):
            errs.append("meta.decision.reason must name the first deciding gate or quote urgency")

    readers = meta.get("readers")
    if not isinstance(readers, list) or len(readers) != 5:
        errs.append("meta.readers must contain exactly 5 reader passes")
    else:
        names = [r.get("name") if isinstance(r, dict) else None for r in readers]
        if tuple(names) != READER_NAMES:
            errs.append("meta.readers must remain in funnel order")
        for idx, reader in enumerate(readers):
            if not isinstance(reader, dict) or any(not isinstance(reader.get(k), str) or not reader.get(k).strip() for k in ("verdict", "evidence")):
                errs.append("meta.readers[%s] needs verdict and evidence" % idx)

    attention = data.get("getsAttention")
    if isinstance(attention, list) and len(attention) > 3:
        errs.append("getsAttention has more than 3 entries")

    item_list = data.get("items") if isinstance(data.get("items"), list) else []
    item_ids = set()
    resume_ids = set()
    targets = set()
    for item in item_list:
        if not isinstance(item, dict):
            continue
        n = item.get("n")
        if not isinstance(n, int) or isinstance(n, bool):
            errs.append("item n must be an integer, not boolean")
        elif n in item_ids:
            errs.append("duplicate item n %s" % n)
        else:
            item_ids.add(n)
            if item.get("section") == "resume":
                resume_ids.add(n)
        if item.get("status") not in STATUS_VALUES:
            errs.append("item %s status has invalid value" % (n if n is not None else "?"))
        if item.get("urgency") not in URGENCY_VALUES:
            errs.append("item %s urgency has invalid value" % (n if n is not None else "?"))
        if "severity" in item:
            # Mirror the page's Number.isInteger: 1|2|3, never a bool, and an
            # integer-valued float passes on both ports.
            severity = item.get("severity")
            if not (
                isinstance(severity, (int, float))
                and not isinstance(severity, bool)
                and float(severity).is_integer()
                and 1 <= severity <= 3
            ):
                errs.append("item %s severity must be 1|2|3" % (n if n is not None else "?"))
        if contract.get("version") == "2.4.0":
            presentation = item.get("meta")
            if not _exact_keys(presentation, ("scope", "visibility")):
                errs.append("item %s meta must have exactly scope,visibility" % (n if n is not None else "?"))
            else:
                if presentation.get("scope") not in ITEM_SCOPE_VALUES:
                    errs.append("item %s meta.scope has invalid value" % (n if n is not None else "?"))
                if presentation.get("visibility") not in ITEM_VISIBILITY_VALUES:
                    errs.append("item %s meta.visibility has invalid value" % (n if n is not None else "?"))
                if presentation.get("visibility") == "clean" and item.get("verdict") != "keep":
                    errs.append("item %s clean visibility requires keep verdict" % (n if n is not None else "?"))
                if presentation.get("visibility") == "hotspot":
                    for key, limit in (("title", 80), ("reason", 600), ("suggestion", 400)):
                        if not isinstance(item.get(key), str) or not item.get(key).strip() or len(item[key]) > limit:
                            errs.append("item %s hotspot %s exceeds %s characters or is empty" % (n if n is not None else "?", key, limit))
                    visible_copy = " ".join(str(item.get(key, "")) for key in ("title", "reason", "suggestion"))
                    for term in HOTSPOT_FORBIDDEN_TERMS:
                        if re.search(r"\b%s\b" % re.escape(term), visible_copy, re.I):
                            errs.append("item %s hotspot copy exposes internal term %s" % (n if n is not None else "?", term))
        effect = item.get("decisionEffect")
        if effect not in EFFECT_VALUES:
            errs.append("item %s decisionEffect has invalid value" % (n if n is not None else "?"))
        if effect == "none" and item.get("verdict") not in ("tighten", "cut"):
            errs.append("item %s decisionEffect none requires tighten|cut" % (n if n is not None else "?"))
        ctx = item.get("ctx")
        if not isinstance(ctx, dict):
            errs.append("item %s ctx must be an object" % (n if n is not None else "?"))
            ctx = {}
        if set(ctx) != set(CTX_KEYS):
            errs.append("item %s ctx must have exactly 13 keys" % (n if n is not None else "?"))
        if ctx.get("itemId") != n:
            errs.append("item %s ctx.itemId must equal n" % (n if n is not None else "?"))
        if ctx.get("decisionEffect") != effect:
            errs.append("item %s ctx.decisionEffect must equal item" % (n if n is not None else "?"))
        for key in CTX_STRING_KEYS:
            if not isinstance(ctx.get(key), str):
                errs.append("item %s ctx.%s must be a string" % (n if n is not None else "?", key))
            elif len(ctx[key]) > CTX_MAX_CHARS[key]:
                errs.append("item %s ctx.%s exceeds %s characters" % (n if n is not None else "?", key, CTX_MAX_CHARS[key]))
        for key in ("relatedIds", "decisions", "questions"):
            value = ctx.get(key)
            if not isinstance(value, list) or not all(isinstance(v, (int if key == "relatedIds" else str)) and not isinstance(v, bool) for v in value):
                errs.append("item %s ctx.%s has invalid type" % (n if n is not None else "?", key))
            elif len(value) > 20 or (key != "relatedIds" and any(len(v) > 400 for v in value)):
                errs.append("item %s ctx.%s exceeds capsule limits" % (n if n is not None else "?", key))
        contact_blob = " ".join(ctx.get(k, "") for k in CTX_STRING_KEYS if isinstance(ctx.get(k), str))
        if str(ctx.get("path", "")).startswith("resumeDoc.contact") or re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", contact_blob) or re.search(r"(?:\+?\d[\d(). -]{7,}\d)", contact_blob):
            errs.append("item %s ctx must not contain contact PII" % (n if n is not None else "?"))
        array_entries = [
            v
            for key in ("decisions", "questions")
            if isinstance(ctx.get(key), list)
            for v in ctx[key]
        ]
        if any(isinstance(ctx.get(key), str) and _contains_resume_doc(ctx.get(key)) for key in CTX_STRING_KEYS) or any(isinstance(v, str) and _contains_resume_doc(v) for v in array_entries):
            errs.append("item %s ctx must not embed resumeDoc" % (n if n is not None else "?"))
        actionable = item.get("verdict") != "keep"
        prompt = item.get("prompt")
        if actionable:
            if not isinstance(prompt, str) or not prompt.strip():
                errs.append("item %s actionable prompt must be non-empty" % (n if n is not None else "?"))
            else:
                expected_lines = {
                    "Atom:": str(ctx.get("atom", "")),
                    "Evidence:": str(ctx.get("evidence", "")), "Truth:": str(ctx.get("truth", "")),
                    "Decision effect:": str(effect),
                }
                expected_lines["Item:"] = str(n).lower() if isinstance(n, bool) else str(n)
                blocks = _prompt_blocks(prompt)
                for label in PROMPT_LABELS:
                    value = blocks.get(label, "")
                    if not value:
                        errs.append("item %s prompt missing %s value" % (n if n is not None else "?", label))
                    elif label in expected_lines and value != expected_lines[label]:
                        shown_n = str(n).lower() if isinstance(n, bool) else (n if n is not None else "?")
                        errs.append("item %s prompt %s value disagrees with ctx" % (shown_n, label))
        target = item.get("target")
        if target is not None:
            if not isinstance(target, str):
                errs.append("item %s target must be a string" % (n if n is not None else "?"))
            elif target and target in targets:
                errs.append("duplicate rewrite target %s" % target)
            elif target:
                targets.add(target)

    if contract.get("version") == "2.4.0":
        for item in item_list:
            if not isinstance(item, dict) or not isinstance(item.get("meta"), dict) or item["meta"].get("scope") != "context":
                continue
            ctx = item.get("ctx") if isinstance(item.get("ctx"), dict) else {}
            related = ctx.get("relatedIds") if isinstance(ctx.get("relatedIds"), list) else []
            related_ok = len(related) >= 2 and len(related) == len(set(related)) and all(v in item_ids and v != item.get("n") for v in related)
            path = ctx.get("path") if isinstance(ctx.get("path"), str) else ""
            group_path = bool(re.match(r"^resumeDoc\.(?:summary|experience\.\d+|coreTech|extras)$", path))
            evidence_parts = [part.strip() for part in re.split(r"\n+", ctx.get("evidence", "")) if part.strip()] if isinstance(ctx.get("evidence"), str) else []
            if not (related_ok or (group_path and len(evidence_parts) >= 2)):
                errs.append("item %s context scope needs two related items or two group evidence lines" % item.get("n", "?"))
        errs.extend(_validate_target_decode(meta, item_ids))
        errs.extend(_validate_parse_status(meta))
        errs.extend(_validate_jd_set(data))
        errs.extend(_validate_rubric(data, meta))
        errs.extend(_validate_open_bars(data, meta))
        errs.extend(_validate_resume_sections(data))
        errs.extend(_validate_craft(data, item_ids))
        errs.extend(_validate_linkedin_doc(data))

    section_ids = [s.get("id") for s in (data.get("sections") or []) if isinstance(s, dict)]
    allowed_orders = (
        (SKILLMATCH_SECTIONS, SKILLMATCH_LINKEDIN_SECTIONS)
        if mode == "skillmatch"
        else (STANDARD_SECTIONS, STANDARD_LINKEDIN_SECTIONS)
    )
    if tuple(section_ids) not in allowed_orders:
        errs.append("sections do not match canonical order for mode")
    for item in item_list:
        if isinstance(item, dict) and item.get("section") == "linkedin":
            related = (item.get("ctx") or {}).get("relatedIds")
            if not isinstance(related, list) or not related or not all(r in resume_ids for r in related):
                errs.append("linkedin item %s needs related resume item IDs" % item.get("n", "?"))

    outcomes = data.get("outcomes")
    if isinstance(outcomes, list):
        required_outcome = {"resumeVersion", "itemIds", "window", "applications", "callbacks", "interviews", "note"}
        for idx, outcome in enumerate(outcomes):
            if not isinstance(outcome, dict) or set(outcome) != required_outcome:
                errs.append("outcome %s must have exactly 7 keys" % idx)
                continue
            if not isinstance(outcome["resumeVersion"], str) or not outcome["resumeVersion"].strip():
                errs.append("outcome %s resumeVersion must be non-empty" % idx)
            ids = outcome["itemIds"]
            if not isinstance(ids, list) or not ids or any(not isinstance(v, int) or isinstance(v, bool) for v in ids) or len(set(ids)) != len(ids) or any(v not in item_ids for v in ids):
                errs.append("outcome %s itemIds must be unique existing integers" % idx)
            window = outcome["window"]
            try:
                if not isinstance(window, dict) or set(window) != {"start", "end"}:
                    raise ValueError
                start = datetime.strptime(window["start"], "%Y-%m-%d").date()
                end = datetime.strptime(window["end"], "%Y-%m-%d").date()
                if start > end:
                    raise ValueError
            except (TypeError, ValueError):
                errs.append("outcome %s window must be closed YYYY-MM-DD range" % idx)
            counts = [outcome[k] for k in ("applications", "callbacks", "interviews")]
            if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in counts) or not (counts[2] <= counts[1] <= counts[0]):
                errs.append("outcome %s counts must satisfy interviews <= callbacks <= applications" % idx)
            if not isinstance(outcome["note"], str):
                errs.append("outcome %s note must be a string" % idx)
            else:
                note = outcome["note"].strip()
                artifact = r"\b(edit|rewrite|rewrote|change|resume|summary|bullet|skill|wording)\b"
                outcome_word = r"\b(applications?|callbacks?|interviews?|calls?|recruiters?|screeners?|response rate)\b"
                causal_verb = r"(?:\b(caus(?:e|ed)|prov(?:e|ed)|drove|driven|produced|generated|yielded|triggered|boosted|increased|improved|lifted|doubled|raised|converted|secured|earned|affected|delivered|explains)\b|\bled to\b|\bbrought in\b|\bwas the reason\b|\bresponsible for\b|\bis why\b)"
                causal_claim = re.search(artifact + r".{0,80}" + causal_verb + r".{0,80}" + outcome_word, note, re.I) or re.search(artifact + r".{0,80}\b(made|got)\b.{0,30}\b(call|interview)\b", note, re.I) or re.search(outcome_word + r".{0,80}\b(because|thanks to|due to|as a result of|resulted from|flowed from|caused by|attributed to|attributable to|on account of)\b.{0,80}" + artifact, note, re.I) or re.search(r"\bcredit\b.{0,40}" + artifact + r".{0,50}" + outcome_word, note, re.I)
                safe_negation = re.search(artifact + r".{0,100}\b(did not|does not|cannot|can't|never)\s+(?:be said to have\s+|have\s+)?\b(cause|caused|prove|drive|lead|produce|generate|yield|trigger|result|increase|improve|boost|lift|affect)\b", note, re.I) or re.search(outcome_word + r".{0,50}\b(?:(?:was|were) not (?:caused|proved|driven|produced|generated|yielded|triggered) by|cannot be attributed to)\b.{0,30}" + artifact, note, re.I) or re.search(r"\bno evidence\b.{0,100}" + artifact + r".{0,50}\b(caus|prov|driv|lead|produc|generat|yield|trigger|result|increase|improve|boost|lift|affect)", note, re.I) or re.search(r"\b(causation is not established|no attribution|observed after, not attributed to)\b", note, re.I)
                if causal_claim and not safe_negation:
                    errs.append("outcome %s note must not claim causation" % idx)
    return errs


def _escape_island(text):
    """Neutralize the two sequences that let text escape a <script> element —
    `</` → `<\\/` and `<!--` → `\\u003c!--`, both identical to the browser on
    parse. Shared by the first render and every durable write, so the island a
    fresh render writes and the island a durable verb rewrites are byte-identical."""
    return text.replace("</", "<\\/").replace("<!--", "\\u003c!--")


def _atomic_write(path, text):
    """Write `text` to `path` through a temp file in the same directory and
    os.replace it in — a reader sees the old file or the new one, never a
    partial. Shared by render and ReportStore._write.

    newline="\\n" pins the line ending, because Windows text mode would otherwise
    translate every \\n to \\r\\n on the way out: a report rendered there would not
    be byte-identical to the same report rendered anywhere else, and the island
    the browser reads would not be the island a durable verb wrote."""
    real = os.path.realpath(path)
    directory = os.path.dirname(real) or "."
    handle, temp = tempfile.mkstemp(
        dir=directory, prefix=".%s." % os.path.basename(real)
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp, real)
    except BaseException:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise


def render_report(template_html, data):
    """Fill a verbatim template with `data`'s island and return the merged HTML.

    The FIRST write of a report, gated exactly as every later durable write is:
    validate the island against the template's OWN shipped `#report-contract`
    and, on any breach, raise ReportError having produced nothing — fail closed,
    the caller falls back to the inline report. `meta.contractVersion` is stamped
    to the contract's version so the caller never has to. Only the `#report-data`
    text node is filled; every other byte of the template is carried through."""
    cm = _CONTRACT_RE.search(template_html)
    if cm is None:
        raise ReportError("template has no #report-contract — cannot validate")
    try:
        contract = json.loads(cm.group(1))
    except ValueError as exc:
        raise ReportError("template #report-contract is not valid JSON: %s" % exc)
    if not isinstance(data, dict):
        raise ReportError("contract breach — nothing written: DATA root must be an object")
    source_version = (data.get("meta") or {}).get("contractVersion") if isinstance(data.get("meta"), dict) else None
    target_version = contract.get("version")
    if source_version not in (target_version, "2.0.0", "2.1.0", "2.2.0", "2.3.0") or (source_version != target_version and target_version != "2.4.0"):
        raise ReportError("contract breach — nothing written: unsupported report contract %s" % (source_version or "‹none›"))
    rendered_data = migrate_report(data, target_version)
    errs = validate_island(rendered_data, contract)
    if errs:
        raise ReportError("contract breach — nothing written: %s" % "; ".join(errs))
    match = _ISLAND_RE.search(template_html)
    if match is None:
        raise ReportError("template has no #report-data island to fill")
    island = _escape_island(json.dumps(rendered_data, ensure_ascii=False, indent=1))
    return (
        template_html[: match.start(2)]
        + "\n"
        + island
        + "\n"
        + template_html[match.end(2) :]
    )


# ---------------------------------------------------------------------------
# Tool directory — ONE self-describing structure surfaced three identical ways:
# printed at `serve` start, returned by GET /tools, and printed by the `tools`
# CLI command. All three serialize this single literal through _tools_json(),
# so the three surfaces are byte-identical by construction (never hand-copied).
# It is complete over the bridge's whole surface: every CLI command, every HTTP
# endpoint, and every page verb the report exposes on window.AGUIrun — each with
# a signature and a one-line semantics string.
#
# The page verbs live in the report template's AGUI_VERBS list, which the bridge
# cannot import at runtime (it serves reports it did not author). So the "verbs"
# group below is a STATIC MIRROR of that list, reconciled by hand against the
# current report-template.html (including getContext and acceptRewrite). The live verb list
# is still available from the page itself: hello returns verbs[] straight from
# AGUI_VERBS, so a client never has to trust this mirror to learn what a given
# page actually supports.
# ---------------------------------------------------------------------------
TOOL_DIRECTORY = {
    "bridge": "agui_bridge.py",
    "port": PORT,
    "cli": {
        "render": {
            "signature": "render --island <json> --out <html> [--template <html>] [--serve] [--idle N] [--port N]",
            "semantics": "Build a report HTML from an island JSON and the report "
            "template: validate the island against the template's shipped "
            "#report-contract (fail-closed — on breach, write nothing and exit 1), "
            "splice it into a verbatim template copy, and write --out atomically. "
            "With --serve, host the written file via serve --report (session-scoped).",
        },
        "serve": {
            "signature": "serve [--report <html-file>] [--dir <static-dir>] [--idle N] [--port N]",
            "semantics": "Run the bridge on localhost:8917 unless --port names "
            "another; one report per port, so a second report served at the "
            "same time needs its own --port, and every client command reaching "
            "it needs the same --port. Host the --report"
            "file at / and its basename (durable verbs write it in place, "
            "#report-contract-gated), serve --dir static files to report pages, "
            "and self-exit after N seconds of inactivity (default 300).",
        },
        "list": {
            "signature": "list",
            "semantics": "Print the running bridge's connection registry as "
            "JSON.",
        },
        "cmd": {
            "signature": "cmd [--to <target>] --verb <verb> [--args <json-array>]",
            "semantics": "Route a verb to connected page(s) via the running "
            "bridge and print the JSON result; --to targets a name, instanceId, "
            "reportId, or 'all', --verb names the AGUIrun verb, --args is a JSON "
            "array of arguments.",
        },
        "export": {
            "signature": "export --report <html> [--doc resume|linkedin|island] [--format md|json] [--out <path>]",
            "semantics": "The round trip out of the island: read the report's current "
            "resumeDoc or linkedinDoc and write it back out as a document (markdown by "
            "default, JSON with --format json); --doc island emits the whole island. "
            "Read-only on the report, needs no running bridge, validates before emitting, "
            "and exits 2 when the requested document is absent. Exported résumés carry "
            "contact fields — local only.",
        },
        "stop": {
            "signature": "stop",
            "semantics": "Ask the running bridge to acknowledge and shut down.",
        },
        "tools": {
            "signature": "tools",
            "semantics": "Print this tool directory (identical to the serve-start "
            "banner and GET /tools).",
        },
    },
    "http": {
        "/heartbeat": {
            "signature": "GET /heartbeat",
            "semantics": "Identity probe returning {alive:true,report:<realpath|null>,reportId:<id|null>}; the one request "
            "that never resets the inactivity timer.",
        },
        "/events": {
            "signature": "GET /events?name=<name>&wasDefault=<bool>",
            "semantics": "SSE dial-in: a page registers under "
            "resume:<reportId>:<instanceId>:<encoded-realpath> and receives CONNECT_ACK then its "
            "tool-call event stream.",
        },
        "/list": {
            "signature": "GET /list",
            "semantics": "Return the connection registry as JSON.",
        },
        "/disconnect": {
            "signature": "GET|POST /disconnect?name=<name>&type=intentional|unload",
            "semantics": "Drop a connection by name; intentional keeps the entry "
            "as disconnected, unload removes it outright.",
        },
        "/command": {
            "signature": "POST /command {to?, verb, args?, artifact?}",
            "semantics": "Route the verb to page(s), emit AG-UI tool calls, await "
            "and return their results.",
        },
        "/result": {
            "signature": "POST /result {tool_call_id, result}",
            "semantics": "A page posts a tool-call result back to correlate with "
            "its pending call.",
        },
        "/stop": {
            "signature": "POST /stop",
            "semantics": "Acknowledge, then shut the bridge down.",
        },
        "/tools": {
            "signature": "GET /tools",
            "semantics": "Return this tool directory as JSON.",
        },
        "/ (report host)": {
            "signature": "GET / or /<report basename>",
            "semantics": "Serve the --report HTML file byte-identical (the "
            "durable artifact durable verbs write to); absent --report, 404.",
        },
        "static fallback": {
            "signature": "GET <other path>",
            "semantics": "Serve a file from --dir byte-identical and read-only, "
            "else 404.",
        },
    },
    "verbs": {
        "hello": {
            "signature": "hello()",
            "semantics": "Advertise reportId, instanceId, name, role, mode, and "
            "the live verbs[] list.",
        },
        "getState": {
            "signature": "getState()",
            "semantics": "Report snapshot: meta, items (n, status, verdict, "
            "target), and the resume doc.",
        },
        "exportData": {
            "signature": "exportData()",
            "semantics": "The full island-shaped data object with each item's live "
            "status folded in, for saving as the new island.",
        },
        "setStatus": {
            "signature": 'setStatus(n, "open"|"done"|"ignore")',
            "semantics": "Durably set item n's status; disk is validated and "
            "atomically replaced before any connected page repaints.",
        },
        "patchResume": {
            "signature": "patchResume(path, text)",
            "semantics": "Set resumeDoc at a resumeDoc.* data-path and re-render "
            "the preview.",
        },
        "patchLinkedin": {
            "signature": "patchLinkedin(path, text)",
            "semantics": "Set linkedinDoc at a linkedinDoc.* data-path and re-render "
            "the preview. Fails when the report carries no LinkedIn document.",
        },
        "applyRewrite": {
            "signature": "applyRewrite(n, index=0)",
            "semantics": "Write item n's rewrite[index].txt into the résumé or "
            "LinkedIn node at its target.",
        },
        "listChanges": {
            "signature": "listChanges()",
            "semantics": "The list of mutations applied this session.",
        },
        "getItem": {
            "signature": "getItem(n)",
            "semantics": "The full island item for n (every key incl. "
            "target/rewrite when present) plus live status; unknown n errors.",
        },
        "updateItem": {
            "signature": "updateItem(n, patch)",
            "semantics": "Merge patch's fields into item n's content and repaint "
            "its row; refuses n and status (n is the address, status has its own "
            "verb). A durable verb: through a --report bridge it writes the "
            "on-disk island #report-contract-gated (fail-closed), then broadcasts.",
        },
        "acceptRewrite": {
            "signature": "acceptRewrite(n, index=0)",
            "semantics": "Atomically write the selected rewrite to its unique "
            "resume target, append ctx.decisions, and set status done. Marks the "
            "item's assessed parent section stale.",
        },
        "rereadSection": {
            "signature": "rereadSection(sectionId, patch)",
            "semantics": "The post-accept re-read: rewrite a résumé section's "
            "whole-read (verdict/status/assessment) and clear staleness to fresh. "
            "staleness is system-managed and cannot be set through the patch.",
        },
        "getContext": {
            "signature": "getContext(n)",
            "semantics": "Return only item n's exact thirteen-key ctx capsule; "
            "unknown n errors and no resumeDoc/status is included.",
        },
        "listRubric": {
            "signature": "listRubric()",
            "semantics": "One line per rubric row — index, competency, grade, standing, "
            "the postings that named it, and whether a cited résumé line has been "
            "edited since the grade was set.",
        },
        "getRubricContext": {
            "signature": "getRubricContext(i)",
            "semantics": "Rubric row i's capsule — competency, grade, bar, standing, gaps, "
            "each cited résumé path with its current text, and the findings that sit on "
            "those paths — wrapped in the instruction that improvement is written with "
            "patchResume on a cited path, patchLinkedin on a LinkedIn path, and that the "
            "grade is never set directly.",
        },
    },
}


def _tools_json():
    """Serialize the tool directory. The single serializer behind all three
    surfaces — serve-start print, GET /tools, and the `tools` CLI — so they are
    byte-identical: same literal, same dump, same indentation."""
    return json.dumps(TOOL_DIRECTORY, indent=2)


class Connection:
    """One registry entry: a page holding (or having held) an event stream."""

    __slots__ = ("name", "state", "is_default", "connected_at", "events")

    def __init__(self, name, is_default):
        self.name = name
        self.state = "connected"  # connected | disconnected | broken
        self.is_default = is_default
        self.connected_at = datetime.now(timezone.utc).isoformat()
        self.events = queue.Queue()  # per-client outbound event queue

    def to_dict(self):
        return {
            "name": self.name,
            "state": self.state,
            "isDefault": self.is_default,
            "connectedAt": self.connected_at,
        }


class _PendingCall:
    """One emitted tool call awaiting its /result post."""

    __slots__ = ("event", "result")

    def __init__(self):
        self.event = threading.Event()
        self.result = None


class Bridge:
    """Connection registry (in memory) + the durable report it hosts.

    The registry is ephemeral by design and stays that way; `store` — the
    ReportStore for the `--report` file, None when the bridge hosts no report —
    is the durable half. Knows nothing about HTTP.
    """

    def __init__(self, store=None):
        self._lock = threading.Lock()
        self._connections = {}  # name -> Connection
        self._pending = {}  # tool_call_id -> _PendingCall
        self._notes = []  # queued _note strings (auto-promotion riders)
        self.store = store  # the hosted report, or None

    def connect(self, name, was_default):
        """Register a dialing-in page.

        Returns (Connection, None) on acceptance, (None, reason) on
        rejection. Rejection happens only when another live stream actively
        holds the exact name; a disconnected or broken entry is stale and is
        replaced. The first connection with no default in place becomes the
        default; a returning `wasDefault` client reclaims the slot only when
        it is free, and yields when another default already holds it.
        """
        hosted_id = self.store.report_id() if self.store else None
        if hosted_id:
            parts = name.split(":", 3)
            claim = unquote(parts[3]) if len(parts) == 4 else None
            if parts[:2] != ["resume", hosted_id] or os.path.realpath(claim or "") != self.store.path:
                return None, "report_mismatch"
        with self._lock:
            existing = self._connections.get(name)
            if existing is not None and existing.state == "connected":
                return None, "name_taken"
            if existing is not None:
                del self._connections[name]
            has_default = any(c.is_default for c in self._connections.values())
            connected = sum(
                1 for c in self._connections.values() if c.state == "connected"
            )
            is_default = not has_default and (was_default or connected == 0)
            conn = Connection(name, is_default)
            self._connections[name] = conn
            return conn, None

    def disconnect(self, name, kind):
        """Apply a disconnect signal and end the entry's stream.

        intentional: keep the entry as `disconnected`, default flag dropped
        (the page may reconnect under the same name). unload: the tab is
        gone — remove the entry outright. Either way, a departing default
        triggers the fallback rules: exactly one connected peer remaining is
        auto-promoted and a `_note` is queued to ride the next successful
        command; with zero or 2+ peers nothing is promoted (routing errors
        or the pick-one prompt surface it at the point of use). Returns
        False for an unknown name.
        """
        with self._lock:
            conn = self._connections.get(name)
            if conn is None:
                return False
            was_default = conn.is_default
            was_broken = conn.state == "broken"
            conn.is_default = False
            if kind == "unload":
                del self._connections[name]
            else:  # intentional
                conn.state = "disconnected"
            if was_default:
                remaining = [
                    c
                    for c in self._connections.values()
                    if c.name != name and c.state == "connected"
                ]
                if len(remaining) == 1:
                    remaining[0].is_default = True
                    self._notes.append(
                        '"%s" %s. "%s" is now the default page.'
                        % (
                            name,
                            "had a broken connection and was disconnected"
                            if was_broken
                            else "disconnected",
                            remaining[0].name,
                        )
                    )
            conn.events.put(_CLOSE)
            return True

    def mark_broken(self, conn):
        """A stream died without a disconnect signal: mark the entry broken.

        Applies only while this exact record is still current and connected,
        so it never tramples a processed disconnect or a replacing reconnect.
        """
        with self._lock:
            if (
                self._connections.get(conn.name) is conn
                and conn.state == "connected"
            ):
                conn.state = "broken"

    def snapshot(self):
        """Registry listing, oldest connection first."""
        with self._lock:
            entries = sorted(
                self._connections.values(), key=lambda c: c.connected_at
            )
            return [c.to_dict() for c in entries]

    # -- routing --------------------------------------------------------

    @staticmethod
    def _name_parts(name):
        """(reportId, instanceId) of a `resume:<rid>:<iid>[:<encoded-realpath>]`
        name, else Nones. The realpath segment is optional: names carry it so a
        copied report cannot cross-write, and addressing must see past it."""
        parts = name.split(":")
        if len(parts) in (3, 4):
            return parts[1], parts[2]
        return None, None

    def resolve(self, to):
        """Resolve a command address to targets, emma precedence ported.

        Targeted: exact name > bare instanceId (the one page owning it) >
        reportId (every connected tab of that report) — with `all` as the
        broadcast literal. A broken or disconnected target prompts
        wait/switch/abort; an unknown name errors with the current roster.
        Untargeted: default > sole connection > pick-one prompt error.

        Returns one of:
            {"targets": [...], "skipped"?: [...]}      execute these
            {"error": msg}                             hard error
            {"error": msg, "prompt": True, ...}        pick-one / unreachable
        """
        with self._lock:
            conns = list(self._connections.values())
        connected = [c for c in conns if c.state == "connected"]
        roster = ", ".join(c.name for c in connected) or "none"

        if to == "all":
            if not connected:
                return {"error": "No pages are connected to broadcast to."}
            skipped = [c for c in conns if c.state != "connected"]
            return {"targets": connected, "skipped": skipped}

        if to:
            for conn in conns:
                if conn.name == to:
                    return self._single(conn, connected)
            iid_hits = [
                c for c in conns if self._name_parts(c.name)[1] == to
            ]
            if len(iid_hits) > 1:
                names = ", ".join(c.name for c in iid_hits)
                return {
                    "error": 'Instance id "%s" is ambiguous (%s). '
                    "Target a full name." % (to, names)
                }
            if iid_hits:
                return self._single(iid_hits[0], connected)
            rid_hits = [
                c for c in conns if self._name_parts(c.name)[0] == to
            ]
            if rid_hits:
                live = [c for c in rid_hits if c.state == "connected"]
                if live:
                    skipped = [
                        c for c in rid_hits if c.state != "connected"
                    ]
                    return {"targets": live, "skipped": skipped}
                return self._single(rid_hits[0], connected)
            return {
                "error": 'Page "%s" not found. Connected: %s.' % (to, roster)
            }

        # Untargeted: default beats everything except an explicit target.
        if not connected:
            return {"error": "No pages are connected."}
        if len(connected) == 1:
            return {"targets": [connected[0]]}
        for conn in connected:
            if conn.is_default:
                return {"targets": [conn]}
        listing = "\n".join(
            "%d) %s" % (i + 1, c.name) for i, c in enumerate(connected)
        )
        return {
            "error": "Multiple pages are connected but no default is set. "
            "Which one should I use?\n%s\n"
            'Pick one and retarget with "to".' % listing,
            "prompt": True,
            "options": [c.name for c in connected],
        }

    def _single(self, conn, connected):
        """A single resolved entry: usable when connected, else a prompt."""
        if conn.state == "connected":
            return {"targets": [conn]}
        return self._unreachable_prompt(conn, connected)

    @staticmethod
    def _unreachable_prompt(conn, connected):
        """The wait/switch/abort prompt for a broken or disconnected target."""
        healthy = [c.name for c in connected if c.name != conn.name]
        listing = "\n".join("   - %s" % n for n in healthy) or (
            "   (none available)"
        )
        return {
            "error": 'Page "%s" is not responding (%s connection). '
            "What would you like to do?\n"
            "1) Wait - give the page time to reconnect, then retry\n"
            "2) Switch - target another connected page:\n%s\n"
            "3) Abort - tell me what to do next"
            % (conn.name, conn.state, listing),
            "prompt": True,
            "unreachable": conn.name,
            "state": conn.state,
            "healthy": healthy,
        }

    # -- command round-trip ----------------------------------------------

    def command(self, to, verb, args, artifact=None):
        """Route a verb. Durable verbs land on disk first; the rest pass
        through to the pages.

        A DURABLE_VERB is executed by the bridge against the hosted report —
        written, or refused with nothing written — and only then broadcast to
        every connected tab, so no tab renders a change that failed to persist.
        The write does not depend on a tab being open, but an explicit `to`
        must identify the hosted report (or one of its connected tabs). Zero connected tabs is a
        complete success, not an error. Everything else is a pure passthrough,
        routed by `to` per the addressing doctrine.
        """
        if verb in DURABLE_VERBS:
            hosted_id = self.store.report_id() if self.store else None
            if artifact is not None and (
                not isinstance(artifact, str)
                or self.store is None
                or os.path.realpath(artifact) != self.store.path
            ):
                return {
                    "ok": False,
                    "error": "artifact does not own hosted report %s"
                    % (self.store.path if self.store else "null"),
                }
            if to not in (None, "all", hosted_id):
                with self._lock:
                    conn = self._connections.get(to)
                if conn is None or hosted_id is None or not conn.name.startswith("resume:%s:" % hosted_id):
                    return {
                        "ok": False,
                        "error": "durable target %s does not own hosted report %s" % (to, hosted_id or "null"),
                    }
            return self._durable(verb, args)
        if verb in STORE_READ_VERBS and self.store is not None and to is None:
            return self._store_read(verb, args)
        resolution = self.resolve(to)
        if "error" in resolution:
            out = {"ok": False, "error": resolution["error"]}
            for key in ("prompt", "options", "unreachable", "state", "healthy"):
                if key in resolution:
                    out[key] = resolution[key]
            return out
        return self._dispatch(resolution, verb, args)

    def _store_read(self, verb, args):
        """Answer a read verb from the report file itself.

        The store is the copy of record, so a read is answered from it whenever
        the bridge owns one — no tab required. Reads never touched the store
        before, which left the CLI able to write the report but not to inspect
        it, and pushed callers into hand-rolled parsing of the island."""
        try:
            data = self.store.validate()
        except (ReportError, OSError) as exc:
            return {"ok": False, "verb": verb, "error": str(exc)}
        items = data.get("items") or []
        by_n = {it.get("n"): it for it in items if isinstance(it, dict)}
        if verb == "exportData":
            return {"ok": True, "verb": verb, "result": data}
        if verb == "getState":
            return {"ok": True, "verb": verb, "result": {
                "reportId": self.store.report_id(),
                "meta": data.get("meta"),
                "items": [{"n": it.get("n"), "status": it.get("status"), "verdict": it.get("verdict")} for it in items],
                "resumeDoc": data.get("resumeDoc"),
            }}
        if verb in ("getItem", "getContext"):
            n = verb_arg(args, 0, "n")
            item = by_n.get(n)
            if item is None:
                return {"ok": False, "verb": verb, "error": "no item %s" % n}
            return {"ok": True, "verb": verb, "result": item if verb == "getItem" else item.get("ctx")}
        rubric = data.get("rubric") or []
        if verb == "listRubric":
            return {"ok": True, "verb": verb, "result": [{
                "i": i,
                "competency": r.get("competency"),
                "grade": r.get("grade"),
                "standing": r.get("standing"),
                "sources": list((r.get("bar") or {}).get("sources") or []),
                "stale": None,
            } for i, r in enumerate(rubric)]}
        # getRubricContext
        i = verb_arg(args, 0, "i")
        if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(rubric):
            return {"ok": False, "verb": verb, "error": "no rubric row %s" % i}
        row = rubric[i]
        paths = row.get("evidenceIds") or []
        related = [{"n": it.get("n"), "section": it.get("section"), "title": it.get("title")}
                   for it in items
                   if isinstance((it.get("ctx") or {}).get("path"), str)
                   and any(_same_path(it["ctx"]["path"], p) for p in paths)][:12]
        return {"ok": True, "verb": verb, "result": {
            "instruction": "Discuss only this competency. Improve it by rewriting a "
            "résumé line it cites: call patchResume(path,text) with a path from "
            "evidence[]. Never set the grade — a grade moves only when the rewritten "
            "line proves it." + (" The same claim on LinkedIn is rewritten with "
            "patchLinkedin(path,text) against a linkedinDoc.* path."
            if isinstance(data.get("linkedinDoc"), dict) else ""),
            "context": {
                "rubricIndex": i,
                "competency": row.get("competency"),
                "grade": row.get("grade"),
                "standing": row.get("standing"),
                "bar": row.get("bar"),
                "gaps": row.get("gaps") or [],
                "evidence": [{"path": p, "text": _evidence_text(_get_path(data, p))} for p in paths],
                "relatedItems": related,
                "stale": None,
            },
        }}

    def _durable(self, verb, args):
        """Write the report, then broadcast the same verb to the open tabs.

        Fail closed: a ReportError means the file on disk is untouched and the
        pages never hear about it. On success the broadcast carries the page's
        matching in-memory handler, so an open tab's render converges on what
        the file now says; the broadcast's own results ride along under
        `broadcast` but cannot un-write the disk — `ok` reports the WRITE.
        """
        if self.store is None:
            return {
                "ok": False,
                "verb": verb,
                "error": '"%s" needs a bridge launched with --report <path>'
                % verb,
            }
        try:
            written = self.store.apply(verb, args)
        except (ReportError, OSError) as exc:
            return {"ok": False, "verb": verb, "error": str(exc)}
        out = {
            "ok": True,
            "verb": verb,
            "written": written,
            "report": self.store.path,
        }
        resolution = self.resolve("all")
        if "error" not in resolution:  # no tabs connected — the write still stands
            echo = self._dispatch(resolution, verb, args)
            out["broadcast"] = echo.get("results", {})
            if echo.get("_note"):
                out["_note"] = echo["_note"]
        return out

    def _dispatch(self, resolution, verb, args):
        """Emit tool-call events to the resolved targets, collect results.

        Every resolved target gets a TOOL_CALL_START / ARGS / END sequence
        (ARGS delta is {"command", "params"}) and RESULT_TIMEOUT_SECS —
        shared across targets — to post back to /result. Responsive results
        return alongside timed-out markers; a lone target that goes broken
        mid-call answers with the wait/switch/abort prompt instead of a
        generic timeout. Queued `_note` riders drain onto the response when
        at least one result came back.
        """
        calls = []
        payload = json.dumps({"command": verb, "params": args})
        for conn in resolution["targets"]:
            call_id = "tc_%s" % uuid.uuid4().hex[:12]
            pending = self._register_call(call_id)
            conn.events.put(
                {
                    "type": "TOOL_CALL_START",
                    "tool_call_id": call_id,
                    "tool_call_name": TOOL_CALL_NAME,
                }
            )
            conn.events.put(
                {
                    "type": "TOOL_CALL_ARGS",
                    "tool_call_id": call_id,
                    "delta": payload,
                }
            )
            conn.events.put(
                {"type": "TOOL_CALL_END", "tool_call_id": call_id}
            )
            calls.append((conn, call_id, pending))

        deadline = time.monotonic() + RESULT_TIMEOUT_SECS
        results = {}
        broke = []
        any_ok = False
        all_ok = True
        for conn, call_id, pending in calls:
            kind, value = self._await_result(conn, pending, deadline)
            self._release_call(call_id)
            if kind == "result":
                results[conn.name] = {"ok": True, "result": value}
                any_ok = True
            elif kind == "broken":
                broke.append(conn)
                all_ok = False
                results[conn.name] = {
                    "ok": False,
                    "broken": True,
                    "error": 'Page "%s" dropped its stream during the call.'
                    % conn.name,
                }
            else:  # timeout
                all_ok = False
                results[conn.name] = {
                    "ok": False,
                    "timedOut": True,
                    "error": "No result within %d seconds."
                    % int(RESULT_TIMEOUT_SECS),
                }

        if len(calls) == 1 and broke:
            # The lone target broke mid-call: same prompt it would have
            # gotten at resolve time, not a generic timeout.
            with self._lock:
                connected = [
                    c
                    for c in self._connections.values()
                    if c.state == "connected"
                ]
            out = {"ok": False}
            out.update(self._unreachable_prompt(broke[0], connected))
            return out

        response = {"ok": all_ok, "verb": verb, "results": results}
        if resolution.get("skipped"):
            response["skipped"] = [
                {"name": c.name, "state": c.state}
                for c in resolution["skipped"]
            ]
        if any_ok:
            notes = self.consume_notes()
            if notes:
                response["_note"] = "\n".join(notes)
        return response

    def _await_result(self, conn, pending, deadline):
        """Wait for one call against the shared deadline.

        Returns ("result", value) | ("broken", None) | ("timeout", None).
        Polls so a target that breaks mid-call is answered promptly. A
        result that already landed is never reported as a timeout: the
        shared deadline may be spent entirely on an earlier silent target,
        so exhaustion alone only speaks for targets still pending.
        """
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                if pending.event.is_set():
                    return "result", pending.result
                return "timeout", None
            if pending.event.wait(min(POLL_SECS, remaining)):
                return "result", pending.result
            if conn.state != "connected":
                if pending.event.is_set():
                    return "result", pending.result
                return "broken", None

    def _register_call(self, call_id):
        pending = _PendingCall()
        with self._lock:
            self._pending[call_id] = pending
        return pending

    def _release_call(self, call_id):
        with self._lock:
            self._pending.pop(call_id, None)

    def post_result(self, call_id, result):
        """Correlate a posted result to its waiting call.

        False for an unknown id — late posts after a timeout land here and
        are dropped.
        """
        with self._lock:
            pending = self._pending.get(call_id)
        if pending is None:
            return False
        pending.result = result
        pending.event.set()
        return True

    def consume_notes(self):
        """Drain the `_note` queue (onto the next successful command)."""
        with self._lock:
            notes = self._notes
            self._notes = []
        return notes

    def close_all_streams(self):
        """Push the _CLOSE sentinel onto every registered stream so each SSE
        handler returns from its pump loop and lets the connection close —
        the client sees a normal end-of-stream, not a dropped socket or a
        traceback. Used on idle expiry to release pages held open by
        heartbeats. Sentinels for already-departed entries are harmless.
        """
        with self._lock:
            conns = list(self._connections.values())
        for conn in conns:
            conn.events.put(_CLOSE)


class BridgeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    @property
    def bridge(self):
        return self.server.bridge

    def _touch_activity(self):
        """Reset the idle timer. Called on every inbound request except
        /heartbeat, so a page that only heartbeats can still idle out."""
        self.server.last_activity = time.monotonic()

    # -- dispatch -----------------------------------------------------------

    def do_GET(self):
        path = urlparse(self.path).path
        if path != "/heartbeat":
            self._touch_activity()
        if path == "/heartbeat":
            self._send_json(200, {
                "alive": True,
                "report": self.bridge.store.path if self.bridge.store else None,
                "reportId": self.bridge.store.report_id() if self.bridge.store else None,
            })
        elif path == "/events":
            self._handle_events()
        elif path == "/list":
            self._send_json(200, {"connections": self.bridge.snapshot()})
        elif path == "/tools":
            # Same document `serve` prints and the `tools` CLI prints; routed
            # through _send_json so it resets the idle timer like any inbound
            # non-heartbeat request (the _touch_activity above already fired).
            self._send_json(200, TOOL_DIRECTORY)
        elif path == "/disconnect":
            self._handle_disconnect()
        else:
            self._handle_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        self._touch_activity()  # no POST endpoint is /heartbeat
        if path == "/command":
            self._handle_command()
        elif path == "/result":
            self._handle_result()
        elif path == "/disconnect":
            self._handle_disconnect()
        elif path == "/stop":
            self._handle_stop()
        else:
            self._send_json(404, {"error": "not found: %s" % path})

    # -- endpoints ----------------------------------------------------------

    def _handle_events(self):
        """SSE dial-in: acknowledge (or reject) the connect, then pump this
        client's event queue onto the stream, keepalives in the gaps."""
        params = parse_qs(urlparse(self.path).query)
        name = (params.get("name") or [""])[0]
        was_default = (params.get("wasDefault") or [""])[0] == "true"

        self._send_sse_headers()

        if not name:
            self._write_sse(
                {"type": "CONNECT_ACK", "accepted": False, "reason": "missing_name"}
            )
            return

        conn, reason = self.bridge.connect(name, was_default)
        if conn is None:
            self._write_sse(
                {"type": "CONNECT_ACK", "accepted": False, "reason": reason}
            )
            return

        try:
            self._write_sse(
                {
                    "type": "CONNECT_ACK",
                    "accepted": True,
                    "name": conn.name,
                    "isDefault": conn.is_default,
                }
            )
        except OSError:
            self.bridge.mark_broken(conn)
            return

        while True:
            if self._client_gone():
                self.bridge.mark_broken(conn)
                return
            try:
                event = conn.events.get(timeout=KEEPALIVE_SECS)
            except queue.Empty:
                event = None  # keepalive turn
            if event is _CLOSE:
                return  # /disconnect ended this stream cleanly
            try:
                if event is None:
                    self._write_raw(b": keepalive\n\n")
                else:
                    self._write_sse(event)
            except OSError:
                self.bridge.mark_broken(conn)
                return

    def _handle_command(self):
        """POST /command {"to"?,"verb","args"?,"artifact"?} — route, emit, collect."""
        body = self._read_json_body()
        if body is None:
            return
        verb = body.get("verb")
        if not verb or not isinstance(verb, str):
            self._send_json(400, {"ok": False, "error": 'missing "verb"'})
            return
        to = body.get("to")
        if to is not None and not isinstance(to, str):
            self._send_json(
                400, {"ok": False, "error": '"to" must be a string'}
            )
            return
        args = body.get("args", [])
        artifact = body.get("artifact")
        if artifact is not None and not isinstance(artifact, str):
            self._send_json(400, {"ok": False, "error": '"artifact" must be a string'})
            return
        self._send_json(200, self.bridge.command(to, verb, args, artifact))

    def _handle_result(self):
        """POST /result {"tool_call_id","result"} — correlate to its call."""
        body = self._read_json_body()
        if body is None:
            return
        call_id = body.get("tool_call_id")
        if not call_id or not isinstance(call_id, str):
            self._send_json(
                400, {"ok": False, "error": 'missing "tool_call_id"'}
            )
            return
        if self.bridge.post_result(call_id, body.get("result")):
            self._send_json(200, {"ok": True})
        else:
            self._send_json(200, {"ok": False, "reason": "unknown_call"})

    def _handle_disconnect(self):
        params = parse_qs(urlparse(self.path).query)
        name = (params.get("name") or [""])[0]
        kind = (params.get("type") or ["intentional"])[0]
        if kind not in ("intentional", "unload"):
            self._send_json(
                400, {"ok": False, "error": "unknown disconnect type: %s" % kind}
            )
            return
        if self.bridge.disconnect(name, kind):
            self._send_json(200, {"ok": True, "name": name, "type": kind})
        else:
            self._send_json(200, {"ok": False, "reason": "unknown_name", "name": name})

    def _handle_stop(self):
        """POST /stop: acknowledge, then shut the bridge down.

        shutdown() blocks until the accept loop exits, so it runs on a side
        thread after the acknowledgment is already on the wire; the process
        then falls out of serve_forever and exits (stream threads are
        daemonic and die with it). Nothing to flush: durable writes already
        landed on disk as they happened, and the registry is memory-only, so a
        stop takes the connections with it and leaves the report standing.
        """
        self._send_json(200, {"ok": True, "stopping": True})
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def _handle_static(self, path):
        """GET fallback: the hosted report, else a file from --dir.

        The `--report` file answers at `/` and at its own basename — the page
        the bridge serves and the file it durably rewrites are one artifact, so
        a reload after a durable write shows exactly what was written. Beyond
        that, --dir files stream back byte-identical. No --report and no --dir,
        an escape from the --dir root, or a non-file all answer 404. The bytes
        go out exactly as read: no templating, no charset rewriting.
        """
        store = self.bridge.store
        rel_path = unquote(path).lstrip("/")
        if store is not None and rel_path in ("", os.path.basename(store.path)):
            try:
                body = store.read_bytes()
            except OSError:
                self._send_json(404, {"error": "report unreadable: %s" % store.path})
                return
            self._send_bytes(body, "text/html")
            return

        root = getattr(self.server, "static_dir", None)
        rel = unquote(path).lstrip("/")
        if root is None or not rel:
            self._send_json(404, {"error": "not found: %s" % path})
            return
        full = os.path.realpath(os.path.join(root, rel))
        if not full.startswith(root + os.sep) or not os.path.isfile(full):
            self._send_json(404, {"error": "not found: %s" % path})
            return
        try:
            with open(full, "rb") as fh:
                body = fh.read()
        except OSError:
            self._send_json(404, {"error": "not found: %s" % path})
            return
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        self._send_bytes(body, ctype)

    def _send_bytes(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    # -- plumbing -----------------------------------------------------------

    def _read_json_body(self):
        """Parse the request's JSON object body.

        Answers 400 and returns None when the body is missing, malformed,
        or not an object.
        """
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        if not raw:
            self._send_json(400, {"ok": False, "error": "missing JSON body"})
            return None
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            self._send_json(
                400, {"ok": False, "error": "malformed JSON body"}
            )
            return None
        if not isinstance(body, dict):
            self._send_json(
                400, {"ok": False, "error": "JSON body must be an object"}
            )
            return None
        return body

    def _send_json(self, status, obj):
        body = (json.dumps(obj, indent=2) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_sse_headers(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        # No Content-Length: the socket must close when the stream ends,
        # or the client would wait forever on a finished response.
        self.send_header("Connection", "close")
        self.end_headers()

    def _write_sse(self, event):
        self._write_raw(b"data: " + json.dumps(event).encode("utf-8") + b"\n\n")

    def _write_raw(self, data):
        self.wfile.write(data)
        self.wfile.flush()

    def _client_gone(self):
        """True when the client has closed its end of the SSE socket."""
        try:
            readable, _, _ = select.select([self.connection], [], [], 0)
            if not readable:
                return False
            return self.connection.recv(1, socket.MSG_PEEK) == b""
        except (OSError, ValueError):
            return True

    def log_message(self, fmt, *args):
        if getattr(self, "path", "").startswith("/heartbeat"):
            return  # pages poll this every 15 s — keep the log readable
        sys.stderr.write(
            "[bridge] %s %s\n" % (self.log_date_time_string(), fmt % args)
        )


def _idle_watchdog(server, idle):
    """Shut the bridge down after `idle` seconds without a non-heartbeat
    request. The timer runs from launch (last_activity is seeded before
    serve_forever) and BridgeHandler resets it on every inbound request bar
    /heartbeat, so a page that merely heartbeats can never keep the bridge
    alive. On expiry: close every SSE stream cleanly, log exactly one line,
    then stop the accept loop so run_serve returns 0 the normal way —
    daemonic so a /stop-driven shutdown just kills this sleeper instead.

    Sleeps straight to the deadline and re-checks: fresh activity only moves
    last_activity forward, so a woken watchdog finds the deadline pushed out
    and sleeps again. sleep never undershoots, so it can wake early but never
    fire early.
    """
    while True:
        idle_for = time.monotonic() - server.last_activity
        if idle_for >= idle:
            break
        time.sleep(idle - idle_for)
    server.bridge.close_all_streams()
    print(
        "[bridge] idle timeout reached — no non-heartbeat request for %ds; "
        "closing streams and shutting down" % idle,
        flush=True,
    )
    server.shutdown()


def _bridge_heartbeat():
    """Heartbeat document when a bridge answers; None otherwise."""
    try:
        with urllib.request.urlopen(
            "http://localhost:%d/heartbeat" % PORT, timeout=2
        ) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body if body.get("alive") is True else None
    except (OSError, ValueError):
        return None


def _bridge_alive():
    """Compatibility boolean for existing callers/tests."""
    return _bridge_heartbeat() is not None


def run_render(args):
    """Build a report file from an island JSON and the report template, then
    optionally serve it.

    The one repeatable mechanism behind a disk render: the caller (the skill's
    resume run) produces ONLY the island JSON — the analysis — and this validates
    it against the template's shipped #report-contract, splices it into a verbatim
    template copy, and writes the file. Fail closed: on any contract breach it
    prints the breaches, writes nothing, and exits 1 so the caller falls back to
    the inline report. With --serve it chains straight into `serve --report` on
    the file just written (session-scoped, self-exiting on idle — the report on
    disk is the durable artifact, the bridge is not)."""
    here = os.path.dirname(os.path.realpath(__file__))
    template_path = args.template or os.path.join(here, "report-template.html")
    try:
        with open(template_path, encoding="utf-8") as fh:
            template_html = fh.read()
    except OSError as exc:
        sys.stderr.write("[bridge] cannot read template %s: %s\n" % (template_path, exc))
        return 2
    try:
        with open(args.island, encoding="utf-8") as fh:
            data = json.loads(fh.read())
    except OSError as exc:
        sys.stderr.write("[bridge] cannot read --island %s: %s\n" % (args.island, exc))
        return 2
    except ValueError as exc:
        sys.stderr.write("[bridge] --island is not valid JSON: %s\n" % exc)
        return 2
    try:
        merged = render_report(template_html, data)
    except ReportError as exc:
        sys.stderr.write("[bridge] %s\n" % exc)
        sys.stderr.write(
            "[bridge] wrote nothing — fall back to the inline report\n"
        )
        return 1
    out_dir = os.path.dirname(os.path.realpath(args.out)) or "."
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        sys.stderr.write("[bridge] cannot create %s: %s\n" % (out_dir, exc))
        return 2
    _atomic_write(args.out, merged)
    items = data.get("items") if isinstance(data.get("items"), list) else []
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    was = meta.get("contractVersion")
    # Report the contract the written file carries, not the one the input had:
    # render_report migrates a legacy island and leaves the caller's dict alone,
    # so echoing the input tells a migrating user nothing happened.
    try:
        now = json.loads(_ISLAND_RE.search(merged).group(2))["meta"]["contractVersion"]
    except (AttributeError, KeyError, TypeError, ValueError):
        now = was
    print(
        "[bridge] rendered %s — %d items, contract %s%s"
        % (args.out, len(items), now, "" if now == was else " (migrated from %s)" % was),
        flush=True,
    )
    if args.serve:
        return run_serve(
            argparse.Namespace(
                report=args.out, dir=None, idle=args.idle, port=PORT
            )
        )
    return 0


def run_serve(args):
    """Start a bridge — or defer to one already answering on the port.

    Identity-aware reuse, no reclamation: a live heartbeat is reused only for
    the same report realpath (or when both sides have no report). Every other
    identity pair is a nonzero conflict. A dead port that still refuses the
    bind is reported and left alone (exit 1).
    """
    static_dir = None
    if args.dir:
        static_dir = os.path.realpath(args.dir)
        if not os.path.isdir(static_dir):
            sys.stderr.write(
                "[bridge] --dir is not a directory: %s\n" % args.dir
            )
            return 2
    store = None
    if args.report:
        store = ReportStore(args.report)  # realpath: a symlink resolves to its target
        if not os.path.isfile(store.path):
            sys.stderr.write(
                "[bridge] --report is not a file: %s\n" % args.report
            )
            return 2
        try:
            store.validate()
        except ReportError as exc:
            sys.stderr.write("[bridge] invalid --report: %s\n" % exc)
            return 2
    heartbeat = _bridge_heartbeat()
    if heartbeat is not None:
        hosted = heartbeat.get("report")
        requested = store.path if store else None
        if requested is not None and hosted == requested:
            print(
                "[bridge] a bridge already hosts %s on http://localhost:%d "
                "— reusing it, registry untouched" % (requested, PORT),
                flush=True,
            )
            return 0
        if requested is None and hosted is None:
            print(
                "[bridge] a report-less bridge already answers on http://localhost:%d "
                "— reusing it, registry untouched" % PORT,
                flush=True,
            )
            return 0
        sys.stderr.write(
            "[bridge] report ownership conflict: requested %s; hosted %s — not reusing\n"
            % (requested if requested is not None else "null", hosted if hosted is not None else "null")
        )
        return 1
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), BridgeHandler)
    except OSError as exc:
        sys.stderr.write(
            "[bridge] port %d is taken but no bridge heartbeat answers: %s\n"
            % (PORT, exc)
        )
        return 1
    server.bridge = Bridge(store)
    server.static_dir = static_dir
    server.last_activity = time.monotonic()
    threading.Thread(
        target=_idle_watchdog, args=(server, args.idle), daemon=True
    ).start()
    print("[bridge] serving on http://localhost:%d" % PORT, flush=True)
    if store:
        print(
            "[bridge] hosting report %s — served at / and durably rewritten by "
            "%s" % (store.path, ", ".join(DURABLE_VERBS)),
            flush=True,
        )
    if static_dir:
        print("[bridge] static files from %s" % static_dir, flush=True)
    # Self-describing tool directory — the same JSON GET /tools and the `tools`
    # CLI emit (all three go through _tools_json, so they are byte-identical).
    print(
        "[bridge] tool directory (also at GET /tools and the `tools` command):",
        flush=True,
    )
    print(_tools_json(), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def run_cmd(args):
    """POST a command to the running bridge and print its response JSON.

    Exit 0 whenever the bridge answered (routing errors and prompts are
    application outcomes, printed as-is for the caller to read); 1 when no
    bridge is reachable on the port; 2 for unusable --args.
    """
    try:
        verb_args = json.loads(args.args)
    except ValueError as exc:
        sys.stderr.write("[bridge] --args is not valid JSON: %s\n" % exc)
        return 2
    payload = {"verb": args.verb, "args": verb_args}
    if args.to:
        payload["to"] = args.to
    request = urllib.request.Request(
        "http://localhost:%d/command" % PORT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            request, timeout=RESULT_TIMEOUT_SECS + 5
        ) as response:
            sys.stdout.write(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        sys.stdout.write(exc.read().decode("utf-8", "replace"))
    except OSError as exc:
        sys.stderr.write(
            "[bridge] no bridge answering on port %d: %s\n" % (PORT, exc)
        )
        return 1
    return 0


def _cli_request(path, method="GET"):
    """Hit the running bridge and print its response body.

    Exit 0 whenever the bridge answered, 1 when none is reachable —
    the same convention `cmd` uses.
    """
    request = urllib.request.Request(
        "http://localhost:%d%s" % (PORT, path),
        data=b"" if method == "POST" else None,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            sys.stdout.write(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        sys.stdout.write(exc.read().decode("utf-8", "replace"))
    except OSError as exc:
        sys.stderr.write(
            "[bridge] no bridge answering on port %d: %s\n" % (PORT, exc)
        )
        return 1
    return 0


def run_list(args):
    """GET /list from the running bridge and print the listing JSON."""
    return _cli_request("/list")


def _md_experience(roles, stack_key):
    """Experience entries as markdown. Shared by both documents; `stack_key`
    names the trailing line résumé roles carry and LinkedIn roles do not."""
    out = []
    for role in roles or []:
        if not isinstance(role, dict):
            continue
        head = " — ".join(p for p in (role.get("role"), role.get("org")) if p)
        out.append("### %s" % head if head else "###")
        if role.get("dates"):
            out.append("*%s*" % role["dates"])
        out.append("")
        for bullet in role.get("bullets") or []:
            out.append("- %s" % bullet)
        stack = role.get(stack_key) if stack_key else None
        if stack:
            out.append("")
            out.append("Stack: %s" % (", ".join(stack) if isinstance(stack, list) else stack))
        out.append("")
    return out


def _md_titled(groups, label_key, items_key):
    out = []
    for group in groups or []:
        if not isinstance(group, dict):
            continue
        items = group.get(items_key) or []
        out.append("- **%s** — %s" % (group.get(label_key, ""), ", ".join(items)))
    return out


def resume_markdown(doc):
    """The résumé document as markdown — the island's `resumeDoc`, rendered back
    into something a person sends. Contact fields are included: this is the
    candidate's own résumé, written to a local file and nowhere else."""
    lines = ["# %s" % doc.get("name", "")]
    if doc.get("headline"):
        lines += ["", "**%s**" % doc["headline"]]
    contact = doc.get("contact") or {}
    line = " · ".join(str(contact.get(k)) for k in ("location", "phone", "email") if contact.get(k))
    if line:
        lines += ["", line]
    for link in contact.get("links") or []:
        lines.append(link)
    if doc.get("summary"):
        lines += ["", "## Summary", "", doc["summary"]]
    core = _md_titled(doc.get("coreTech"), "label", "items")
    if core:
        lines += ["", "## Core technologies", ""] + core
    if doc.get("experience"):
        lines += ["", "## Experience", ""] + _md_experience(doc["experience"], "stack")
    extras = doc.get("extras") or []
    if extras:
        lines += ["", "## Additional"]
        for extra in extras:
            if isinstance(extra, dict):
                lines += ["", "### %s" % extra.get("title", ""), ""]
                lines += ["- %s" % i for i in extra.get("items") or []]
    return "\n".join(lines).rstrip() + "\n"


def linkedin_markdown(doc):
    """The LinkedIn document as markdown, in the shape it was read in."""
    lines = []
    if doc.get("headline"):
        lines += ["**%s**" % doc["headline"], ""]
    if doc.get("about"):
        lines += ["## About", "", doc["about"], ""]
    if doc.get("experience"):
        lines += ["## Experience", ""] + _md_experience(doc["experience"], None)
    if doc.get("skills"):
        lines += ["## Skills", ""] + ["- %s" % s for s in doc["skills"]] + [""]
    for extra in doc.get("extras") or []:
        if isinstance(extra, dict):
            lines += ["## %s" % extra.get("title", ""), ""]
            lines += ["- %s" % i for i in extra.get("items") or []] + [""]
    return "\n".join(lines).rstrip() + "\n"


def run_export(args):
    """Read the report's island and write one document back out. Read-only on
    the report, and local-only: no bridge, no network, no page involved, so an
    export works whether or not a bridge is running."""
    try:
        data = ReportStore(args.report).validate()
    except ReportError as exc:
        sys.stderr.write("[bridge] cannot export %s: %s\n" % (args.report, exc))
        return 2
    if args.doc == "island":
        text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    else:
        key = "resumeDoc" if args.doc == "resume" else "linkedinDoc"
        doc = data.get(key)
        if not isinstance(doc, dict):
            sys.stderr.write("[bridge] this report carries no %s\n" % key)
            return 2
        if args.format == "json":
            text = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
        else:
            text = resume_markdown(doc) if args.doc == "resume" else linkedin_markdown(doc)
    if args.out:
        _atomic_write(args.out, text)
        sys.stderr.write(
            "[bridge] wrote %s — %s, %s. Candidate data: keep it local.\n"
            % (args.out, args.doc, "json" if args.doc == "island" else args.format)
        )
    else:
        sys.stdout.write(text)
    return 0


def run_stop(args):
    """POST /stop to the running bridge and print the acknowledgment."""
    return _cli_request("/stop", method="POST")


def run_tools(args):
    """Print the tool directory JSON — the same document GET /tools returns and
    `serve` prints at startup, all serialized from the one TOOL_DIRECTORY literal
    via _tools_json(). A pure local print: it describes the static surface, so it
    needs no running bridge."""
    print(_tools_json())
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="agui_bridge.py",
        description="AG-UI bridge and durable host for resume report pages.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    render = commands.add_parser(
        "render",
        help="build a report HTML from an island JSON + the template "
        "(contract-gated, fail-closed), optionally serving it",
    )
    render.add_argument(
        "--island",
        required=True,
        metavar="PATH",
        help="the #report-data island as a JSON file (the run's analysis)",
    )
    render.add_argument(
        "--out",
        required=True,
        metavar="PATH",
        help="where to write the report HTML "
        "(agents/reports/resume/<UTC-timestamp>.html)",
    )
    render.add_argument(
        "--template",
        metavar="PATH",
        help="report template to fill (default: report-template.html beside "
        "this script)",
    )
    render.add_argument(
        "--serve",
        action="store_true",
        help="after writing, host the report on the bridge (session-scoped)",
    )
    render.add_argument(
        "--idle",
        type=int,
        default=300,
        metavar="N",
        help="with --serve, idle seconds before the bridge self-exits "
        "(default 300)",
    )
    serve = commands.add_parser(
        "serve", help="run the bridge on localhost:%d, or --port" % PORT
    )
    serve.add_argument(
        "--report",
        metavar="PATH",
        help="the report page to host: served at / and owned as the durable "
        "store — %s rewrite its #report-data island on disk"
        % ", ".join(DURABLE_VERBS),
    )
    serve.add_argument(
        "--dir", help="directory of static files to serve alongside the bridge"
    )
    serve.add_argument(
        "--idle",
        type=int,
        default=300,
        metavar="N",
        help="seconds without a non-heartbeat request before the bridge "
        "closes streams and exits (default 300)",
    )
    list_ = commands.add_parser(
        "list", help="list the running bridge's connections"
    )
    cmd = commands.add_parser(
        "cmd", help="send a verb to connected pages via the running bridge"
    )
    cmd.add_argument(
        "--to",
        help="target: exact name, instanceId, reportId, or 'all' "
        "(omit for default routing)",
    )
    cmd.add_argument("--verb", required=True, help="AGUIrun verb to invoke")
    cmd.add_argument(
        "--args", default="[]", help="verb arguments as a JSON array"
    )
    export = commands.add_parser(
        "export",
        help="write the report's current résumé or LinkedIn document back out "
        "as a document — the round trip out of the island",
    )
    export.add_argument("--report", required=True, metavar="PATH", help="the report page to read")
    export.add_argument(
        "--doc",
        default="resume",
        choices=("resume", "linkedin", "island"),
        help="which document to emit (default resume)",
    )
    export.add_argument(
        "--format",
        default="md",
        choices=("md", "json"),
        help="markdown document or raw JSON (default md; island is always json)",
    )
    export.add_argument(
        "--out", metavar="PATH", help="write here instead of stdout"
    )
    stop = commands.add_parser("stop", help="stop the running bridge")
    tools = commands.add_parser(
        "tools",
        help="print the self-describing tool directory (JSON) — the same "
        "document serve prints at start and GET /tools returns",
    )
    # Every subcommand that binds or reaches a bridge takes the port. `export`
    # does not: it reads the report file directly and never opens a socket.
    for sub in (render, serve, list_, cmd, stop, tools):
        sub.add_argument(
            "--port",
            type=int,
            default=PORT,
            metavar="N",
            help="bridge port (default %d) — one report per port" % PORT,
        )
    args = parser.parse_args(argv)
    if getattr(args, "port", PORT) != PORT:
        _set_port(args.port)
    if args.command == "render":
        return run_render(args)
    if args.command == "serve":
        return run_serve(args)
    if args.command == "list":
        return run_list(args)
    if args.command == "cmd":
        return run_cmd(args)
    if args.command == "export":
        return run_export(args)
    if args.command == "stop":
        return run_stop(args)
    if args.command == "tools":
        return run_tools(args)


if __name__ == "__main__":
    sys.exit(main())
