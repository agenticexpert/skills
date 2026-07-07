"""Mem lifecycle hooks. Usage: lifecycle.py {clear|compact|startup|sessionend}

Wired into Claude Code hooks by /mem install (references/install.md).
"""
import json
import os
import shutil
import sys
import time

# CLAUDE_PROJECT_DIR anchors paths to the repo root even when the session
# launched from a subdirectory; hooks otherwise run cwd-relative.
PROJECT = os.environ.get("CLAUDE_PROJECT_DIR", ".")
ROOT = os.path.join(PROJECT, ".agents", "mem")
SUMMARY = os.path.join(ROOT, "summary", "SUMMARY.md")
ARCHIVE_DIR = os.path.join(ROOT, "summary", "archive")
TRIGGERS_STATE = os.path.join(ROOT, "triggers.md")
TRANSCRIPT_DIR = os.path.join(ROOT, "transcripts")
EXPORT_SOURCE = os.path.join(PROJECT, "EXPORT.txt")


def read_summary():
    if not os.path.exists(SUMMARY):
        return None
    with open(SUMMARY, "r", encoding="utf-8") as f:
        return f.read()


HEADER = ("[mem checkpoint from a previous session follows. Its analysis and "
          "decisions are established — don't re-derive or re-open them; verify "
          "volatile state (files, branches) before acting on it. Honor "
          "<triggers>; if <current-step> records interrupted work, offer to "
          "resume it.]")


def clear():
    """Print the checkpoint into the fresh context, then consume it into archive."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    content = read_summary()
    if content is None:
        print(f"[No summary file found at {SUMMARY}]")
    else:
        print(HEADER)
        print(content)
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        archived = os.path.join(ARCHIVE_DIR, f"SUMMARY_{timestamp}.md")
        os.rename(SUMMARY, archived)
        print(f"\n[Archived: {archived}]")

    if os.path.exists(EXPORT_SOURCE):
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        export_archived = os.path.join(ARCHIVE_DIR, f"EXPORT_{timestamp}.txt")
        os.rename(EXPORT_SOURCE, export_archived)
        print(f"[Archived: {export_archived}]")


def startup():
    """Read-only: load the checkpoint into a fresh launch. Never rotates."""
    content = read_summary()
    if content is not None:
        print(HEADER)
        print(content)


def compact():
    """Re-inject the live-trigger block so active triggers survive compaction.

    Source is the state file, not SUMMARY.md — the clear hook consumes
    SUMMARY.md, and triggers activated after the last summarize were never
    in it. /mem trigger on/off keeps the state file current.
    """
    if not os.path.exists(TRIGGERS_STATE):
        return
    with open(TRIGGERS_STATE, "r", encoding="utf-8") as f:
        print(f.read())


def sessionend():
    """Archive the raw transcript under a sortable timestamp — same
    %Y%m%d_%H%M%S format as the summary rotation — so a transcript sorts
    alongside the summary written at the same session boundary and the two
    can be paired by nearest timestamp."""
    payload = json.load(sys.stdin)
    transcript = payload.get("transcript_path", "")
    if transcript and os.path.exists(transcript):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
        shutil.copy2(transcript, os.path.join(TRANSCRIPT_DIR, f"{timestamp}.jsonl"))


EVENTS = {"clear": clear, "compact": compact, "startup": startup, "sessionend": sessionend}

if __name__ == "__main__":
    try:
        EVENTS[sys.argv[1]]()
    except Exception as e:
        # Never break a session over a lifecycle problem
        print(f"[mem lifecycle error: {e}]", file=sys.stderr)
        sys.exit(0)
