#!/usr/bin/env python3
"""
manage_refs.py — Attach references (a spec, a design doc) to a roadmap, a track or a milestone.

Usage:
  python manage_refs.py add    <project> <roadmap> <name> <path> [--track <track>] [--milestone <milestone>] [--slots 1,2]
  python manage_refs.py remove <project> <roadmap> <name>

A reference shows in its own band in the track and milestone views. --slots draws it under those
milestone positions; without it its cells stay blank.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasky_config import TASKY_ROOT, validate_slug
import refs


def fail(message):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_slots(value):
    try:
        slots = sorted({int(s) for s in value.split(",")})
    except ValueError:
        fail(f"--slots '{value}' must be comma-separated positions, such as 1,2")
    if slots[0] < 1:
        fail("--slots positions start at 1")
    return slots


def cmd_add(args):
    for value, what in [(args.project, "project slug"), (args.roadmap, "roadmap slug"), (args.name, "reference name")]:
        validate_slug(value, what)
    roadmap_dir = os.path.join(TASKY_ROOT, args.project, args.roadmap)
    if not os.path.isdir(roadmap_dir):
        fail(f"roadmap '{args.project}/{args.roadmap}' does not exist")
    if args.milestone and not args.track:
        fail("--milestone needs --track")
    where = roadmap_dir
    if args.track:
        validate_slug(args.track, "track slug")
        where = os.path.join(where, args.track)
        if not os.path.isdir(where):
            fail(f"track '{args.roadmap}/{args.track}' does not exist")
    if args.milestone:
        validate_slug(args.milestone, "milestone slug")
        where = os.path.join(where, args.milestone)
        if not os.path.isdir(where):
            fail(f"milestone '{args.roadmap}/{args.track}/{args.milestone}' does not exist")
    ref = {"name": args.name, "path": args.path}
    if args.slots:
        ref["slots"] = parse_slots(args.slots)
    try:
        refs.add(roadmap_dir, where, ref)
    except ValueError as e:
        fail(str(e))
    print(f"Added reference {refs.MARK} {refs.label(dict(ref, scope=args.milestone or args.track))} → {ref['path']}")


def cmd_remove(args):
    try:
        refs.remove(os.path.join(TASKY_ROOT, args.project, args.roadmap), args.name)
    except ValueError as e:
        fail(str(e))
    print(f"Removed reference {args.name}")


def main():
    parser = argparse.ArgumentParser(description="Manage tasky references.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_add = sub.add_parser("add", help="Attach a reference to a roadmap, track or milestone")
    for a in ("project", "roadmap", "name", "path"):
        p_add.add_argument(a)
    p_add.add_argument("--track", help="Attach to this track")
    p_add.add_argument("--milestone", help="Attach to this milestone (needs --track)")
    p_add.add_argument("--slots", help="Milestone positions to draw it under, such as 1,2")
    p_remove = sub.add_parser("remove", help="Remove a reference")
    for a in ("project", "roadmap", "name"):
        p_remove.add_argument(a)
    args = parser.parse_args()
    {"add": cmd_add, "remove": cmd_remove}[args.command](args)


if __name__ == "__main__":
    main()
