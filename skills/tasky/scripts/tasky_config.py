#!/usr/bin/env python3
"""
tasky_config.py — Reads Agentic Expert configuration from tasky.md.

Root resolution (first match wins): the TASKY_ROOT environment variable, then an
upward search from the current working directory, then an upward search from this
script's own location. A directory is a project root if it holds tasky.md or .git
(file or directory, so linked worktrees resolve to themselves). No project in
either search exits 1.

Config lookup within the found root (first match wins): .agents/tasky/tasky.md,
then repo-root tasky.md.

Exported:
    TASKY_ROOT  — absolute path to the project data directory
"""

import atexit
import os
import re
import sys


_SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def _find_repo_root(start):
    current = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(current, "tasky.md")):
            return current
        if os.path.exists(os.path.join(current, ".git")):
            return current

        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def _resolve_root(repo_root):
    config_candidates = [
        os.path.join(repo_root, ".agents", "tasky", "tasky.md"),
        os.path.join(repo_root, "tasky.md"),
    ]
    for config_file in config_candidates:
        if not os.path.isfile(config_file):
            continue
        with open(config_file) as f:
            for line in f:
                m = re.match(r"^root:\s*(.+)$", line.strip())
                if m:
                    configured_root = m.group(1).strip()
                    if configured_root:
                        return os.path.abspath(os.path.join(repo_root, configured_root))

    return os.path.abspath(os.path.join(repo_root, ".agents", "tasky"))


def _find_root():
    env_root = os.environ.get("TASKY_ROOT", "").strip()
    if env_root:
        resolved = os.path.abspath(os.path.expanduser(env_root))
        # Announced unconditionally, and deliberately not gated on
        # TASKY_NO_BANNER: an override pins the root regardless of where the
        # user is standing, which is the exact silent-wrong-root failure this
        # module exists to prevent. Silence here would reintroduce it.
        print(f"[tasky] TASKY_ROOT override in effect: {resolved}", file=sys.stderr)
        return resolved

    cwd_start = os.path.abspath(os.getcwd())
    script_start = os.path.dirname(os.path.abspath(__file__))
    for start in (cwd_start, script_start):
        repo_root = _find_repo_root(start)
        if repo_root:
            return _resolve_root(repo_root)

    print(
        f"Error: no tasky project found. Searched upward from cwd '{cwd_start}' "
        f"and from script location '{script_start}'. "
        "Set TASKY_ROOT to the data directory to resolve it explicitly.",
        file=sys.stderr,
    )
    sys.exit(1)


def validate_slug(slug, label="slug"):
    if not slug or not _SLUG_RE.fullmatch(slug):
        print(
            f"Error: invalid {label} '{slug}'. Only lowercase letters, numbers, and hyphens are allowed.",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_slash_path(value, parts, label="path"):
    items = value.split("/")
    if len(items) != parts:
        print(f"Error: invalid {label} '{value}'. Expected {parts} slash-separated slug parts.", file=sys.stderr)
        sys.exit(1)
    for idx, item in enumerate(items, start=1):
        validate_slug(item, f"{label} part {idx}")
    return items


TASKY_ROOT = _find_root()


def _print_banner():
    if os.environ.get("TASKY_NO_BANNER"):
        return
    print()
    print(
        f"[tasky] Route every action on {TASKY_ROOT}/ through a "
        f"references/*.md playbook. Structural intent → structure.md, even mid-flow."
    )


atexit.register(_print_banner)
