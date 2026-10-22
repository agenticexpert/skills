#!/usr/bin/env python3
"""
claims.py — Which session holds a task, and through its tasks a milestone.

A task file's `Session:` line names the session that last set it DOING. That session
holds the task while its status is DOING, PAUSED or READY and the file has changed
within HOLD_HOURS; past that the hold is stale and any session may start it. A
milestone is held by every session holding one of its tasks.

With no current session (tasky_config.SESSION), the process holds nothing and writes
no `Session:` line.
"""

import os
import re
import time

from tasky_config import SESSION

HOLD_HOURS = 2
HOLDING_STATUSES = {"DOING", "PAUSED", "READY"}

SESSION_RE = re.compile(r"^Session:[ \t]*(.*)$", re.MULTILINE)
STATUS_RE = re.compile(r"^Status:[ \t]*(.+)$", re.MULTILINE)


def holder(path):
    """The session holding the task file at path, or None."""
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        content = f.read()
    session, status = SESSION_RE.search(content), STATUS_RE.search(content)
    if not session or not session.group(1).strip() or not status:
        return None
    if status.group(1).strip().upper() not in HOLDING_STATUSES:
        return None
    if time.time() - os.path.getmtime(path) > HOLD_HOURS * 3600:
        return None
    return session.group(1).strip()


def other_holder(path):
    """The session holding the task when it is not this one, or None."""
    held = holder(path)
    return held if held and held != SESSION else None


def milestone_other_holder(milestone_dir):
    """(task slug, session) for a task in the milestone another session holds, or None."""
    for name in sorted(os.listdir(milestone_dir)):
        if name.endswith(".md") and not name.startswith("."):
            held = other_holder(os.path.join(milestone_dir, name))
            if held:
                return name[:-3], held
    return None


def describe(path, session):
    """'session <id>, changed N min ago' for a refusal line."""
    minutes = int((time.time() - os.path.getmtime(path)) // 60)
    return f"session {session}, changed {minutes} min ago; free after {HOLD_HOURS}h unchanged"


def with_session(content, session):
    """content with one `Session:` line under `Status:` naming session; none when session is None."""
    content = re.sub(r"^Session:.*\n?", "", content, flags=re.MULTILINE)
    if session:
        content = STATUS_RE.sub(lambda m: f"{m.group(0)}\nSession: {session}", content, count=1)
    return content
