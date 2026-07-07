#!/usr/bin/env python3
"""
validate.py — Mechanical drift detection for the tasky project tree.

Usage:
  python validate.py                        # full validation
  python validate.py --project <slug>       # scope to a single project
  python validate.py --json                 # output as JSON

Checks:
  1. Tasks marked DONE with unchecked criteria
  2. Tasks marked DONE with empty Criteria section
  3. Dependencies bypassed (task DONE but a declared dependency isn't)
  4. References in task files pointing to paths that don't exist
"""

import os
import sys
import json
import re
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasky_config import TASKY_ROOT


# ---------------------------------------------------------------------------
# project.json helpers
# ---------------------------------------------------------------------------

def load_project_json(project):
    pjson = os.path.join(TASKY_ROOT, project, "project.json")
    if not os.path.isfile(pjson):
        return {"roadmaps": [], "tracks": {}, "milestones": {}, "tasks": {}}
    with open(pjson) as f:
        data = json.load(f)
    data.setdefault("roadmaps", [])
    data.setdefault("tracks", {})
    data.setdefault("milestones", {})
    data.setdefault("tasks", {})
    data.setdefault("oob_roadmaps", {})
    data.setdefault("oob_tracks", {})
    data.setdefault("oob_milestones", {})
    data.setdefault("oob_tasks", {})
    return data

def save_project_json(project, data):
    pjson = os.path.join(TASKY_ROOT, project, "project.json")
    with open(pjson, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Parsing (mirrors scan.py)
# ---------------------------------------------------------------------------

def _normalize_ref(ref):
    """Strip quoting conventions and return a bare path, or '' to skip."""
    ref = ref.strip()
    if ref.startswith("[["):
        return ""
    ref = re.sub(r'\s*§.*$', '', ref)               # § section note
    ref = re.sub(r'\s*\([^)]*\)\s*$', '', ref)      # (lines 65-102) / (#18) / (CP1)
    ref = ref.strip('`\'"').lstrip('@').strip()      # strip ALL wrapping quotes, leading @
    ref = re.sub(r':\d[\d,\-]*$', '', ref)          # :line / :line-range
    ref = ref.split("#")[0].strip()
    if not ref or ' ' in ref:                       # space => prose, skip
        return ""
    return ref


def _ref_tokens(bullet_body):
    """Tokenize a References bullet into one or more normalized paths."""
    spans = re.findall(r'`([^`]+)`', bullet_body)
    raw = spans if spans else bullet_body.split(',')
    out, prev_dir = [], ""
    for tok in raw:
        r = _normalize_ref(tok)
        if not r:
            continue
        if '/' not in r and prev_dir:              # dir inheritance: `dir/a.ts`, `b.ts`
            r = f"{prev_dir}/{r}"
        if '/' in r:
            prev_dir = r.rsplit('/', 1)[0]
        out.append(r)
    return out


def parse_task_file(path):
    with open(path, "r") as f:
        content = f.read()

    task = {
        "path": path,
        "title": "",
        "status": "X",
        "dependencies": [],
        "references": [],
        "prose_references": [],
        "criteria": {"total": 0, "done": 0, "raw": ""},
    }

    lines = content.splitlines()

    for line in lines:
        if line.startswith("# "):
            task["title"] = line[2:].strip()
            break

    in_header = True
    for line in lines:
        if line.startswith("## "):
            in_header = False
            break
        m = re.match(r"^Status:\s*(.+)$", line)
        if m:
            task["status"] = m.group(1).strip()
        m = re.match(r"^Dependencies:\s*\[(.*)\]$", line)
        if m:
            raw = m.group(1).strip()
            task["dependencies"] = [d.strip() for d in raw.split(",") if d.strip()]

    total = len(re.findall(r"^\s*[-*+]\s+\[[ x]\]", content, re.MULTILINE))
    done = len(re.findall(r"^\s*[-*+]\s+\[x\]", content, re.MULTILINE))
    task["criteria"] = {"total": total, "done": done}

    # Capture Criteria section body
    in_criteria = False
    criteria_lines = []
    for line in lines:
        if line.strip() == "## Criteria":
            in_criteria = True
            continue
        if in_criteria:
            if line.startswith("## "):
                break
            criteria_lines.append(line)
    task["criteria"]["raw"] = "\n".join(criteria_lines).strip()

    # ## References section
    in_refs = False
    for line in lines:
        if line.strip() == "## References":
            in_refs = True
            continue
        if in_refs:
            if line.startswith("## "):
                break
            m = re.match(r"^\s*-\s+(.+)$", line)
            if m:
                body = m.group(1).split(" — ")[0].split(" - ")[0].strip()
                tokens = _ref_tokens(body)
                if tokens:
                    task["references"].extend(tokens)
                else:
                    raw = _normalize_ref(body)
                    if not raw and body.strip():
                        task["prose_references"].append(body.strip())

    return task


# ---------------------------------------------------------------------------
# Tree walk
# ---------------------------------------------------------------------------

def walk_tree(root, project_filter=None):
    flat = []

    if not os.path.isdir(root):
        return flat

    for project_name in sorted(os.listdir(root)):
        if project_filter and project_name != project_filter:
            continue
        project_path = os.path.join(root, project_name)
        if not os.path.isdir(project_path) or project_name.startswith("."):
            continue

        data = load_project_json(project_name)

        # Use project.json roadmap order
        roadmap_order = data["roadmaps"]
        oob_roadmap_set = set(data["oob_roadmaps"].get(project_name, []))
        fs_roadmaps = sorted([
            d for d in os.listdir(project_path)
            if os.path.isdir(os.path.join(project_path, d)) and not d.startswith(".") and d != "project.json"
        ])
        seq_roadmaps = roadmap_order + [r for r in fs_roadmaps if r not in roadmap_order and r not in oob_roadmap_set]
        all_roadmaps = seq_roadmaps + sorted(oob_roadmap_set)

        for roadmap_name in all_roadmaps:
            roadmap_path = os.path.join(project_path, roadmap_name)
            if not os.path.isdir(roadmap_path):
                continue

            rm_info = data["tracks"].get(roadmap_name, {})
            track_order = rm_info.get("order", [])
            oob_track_set = set(data["oob_tracks"].get(roadmap_name, []))
            fs_tracks = sorted([
                d for d in os.listdir(roadmap_path)
                if os.path.isdir(os.path.join(roadmap_path, d)) and not d.startswith(".")
            ])
            seq_tracks = track_order + [t for t in fs_tracks if t not in track_order and t not in oob_track_set]
            all_tracks = seq_tracks + sorted(oob_track_set)

            for track_name in all_tracks:
                track_path = os.path.join(roadmap_path, track_name)
                if not os.path.isdir(track_path):
                    continue

                m_key = f"{roadmap_name}/{track_name}"
                ms_order = data["milestones"].get(m_key, [])
                if not ms_order:
                    ms_order = sorted([
                        d for d in os.listdir(track_path)
                        if os.path.isdir(os.path.join(track_path, d)) and not d.startswith(".")
                    ])
                oob_ms = data["oob_milestones"].get(m_key, [])
                all_ms = list(ms_order) + [s for s in oob_ms if s not in ms_order]

                for milestone_slug in all_ms:
                    milestone_path = os.path.join(track_path, milestone_slug)
                    if not os.path.isdir(milestone_path):
                        continue

                    t_key = f"{roadmap_name}/{track_name}/{milestone_slug}"
                    task_order = data["tasks"].get(t_key, [])
                    oob_task_slugs = data["oob_tasks"].get(t_key, [])
                    all_task_slugs = list(task_order) + [s for s in oob_task_slugs if s not in task_order]
                    if not all_task_slugs:
                        all_task_slugs = sorted([
                            f.replace(".md", "")
                            for f in os.listdir(milestone_path)
                            if f.endswith(".md") and not f.startswith(".")
                        ])

                    for task_slug in all_task_slugs:
                        task_path = os.path.join(milestone_path, f"{task_slug}.md")
                        if not os.path.isfile(task_path):
                            continue
                        task = parse_task_file(task_path)
                        task["slug"] = task_slug
                        flat.append({
                            "task": task,
                            "project": project_name,
                            "roadmap": roadmap_name,
                            "track": track_name,
                            "milestone": milestone_slug,
                        })

    return flat


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_done_with_unchecked_criteria(flat):
    issues = []
    for entry in flat:
        t = entry["task"]
        if t["status"].upper() != "DONE":
            continue
        total = t["criteria"]["total"]
        done = t["criteria"]["done"]
        if total > 0 and done < total:
            issues.append({
                "check": "done-unchecked-criteria",
                "path": t["path"],
                "slug": t["slug"],
                "detail": f"{done}/{total} criteria checked",
            })
    return issues


def check_done_with_empty_criteria(flat):
    issues = []
    for entry in flat:
        t = entry["task"]
        if t["status"].upper() != "DONE":
            continue
        total = t["criteria"]["total"]
        raw = t["criteria"]["raw"]
        if total == 0 and not raw:
            issues.append({
                "check": "done-empty-criteria",
                "path": t["path"],
                "slug": t["slug"],
                "detail": "Criteria section is empty — nothing verifiable was done",
            })
    return issues


def check_bypassed_dependencies(flat):
    done_slugs = {e["task"]["slug"] for e in flat if e["task"]["status"].upper() == "DONE"}
    issues = []
    for entry in flat:
        t = entry["task"]
        if t["status"].upper() != "DONE":
            continue
        for dep in t["dependencies"]:
            if dep not in done_slugs:
                issues.append({
                    "check": "bypassed-dependency",
                    "path": t["path"],
                    "slug": t["slug"],
                    "detail": f"dependency '{dep}' is not DONE",
                })
    return issues


def check_broken_references(flat):
    issues = []
    for entry in flat:
        t = entry["task"]
        task_dir = os.path.dirname(t["path"])
        for ref in t["references"]:
            if os.path.exists(ref):
                continue
            # Try resolving relative to the task's directory (sibling refs)
            if os.path.exists(os.path.join(task_dir, ref)):
                continue
            sibling = os.path.join(task_dir, ref)
            if os.path.exists(sibling) or os.path.exists(sibling + ".md"):
                continue
            issues.append({
                "check": "broken-reference",
                "path": t["path"],
                "slug": t["slug"],
                "detail": f"reference path not found: {ref}",
            })
    return issues


def check_prose_references(flat):
    issues = []
    for entry in flat:
        t = entry["task"]
        for prose in t["prose_references"]:
            issues.append({
                "check": "prose-reference",
                "path": t["path"],
                "slug": t["slug"],
                "detail": f"prose in ## References (not a path): {prose!r}",
            })
    return issues


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

LABELS = {
    "done-unchecked-criteria": "DONE with unchecked criteria",
    "done-empty-criteria":     "DONE with empty Criteria",
    "bypassed-dependency":     "Bypassed dependency",
    "broken-reference":        "Broken reference path",
    "prose-reference":         "Prose in ## References (not a path)",
}

def print_report(issues):
    if not issues:
        print("  No issues found.")
        return

    by_check = {}
    for issue in issues:
        by_check.setdefault(issue["check"], []).append(issue)

    for check_key, group in by_check.items():
        label = LABELS.get(check_key, check_key)
        print(f"\n  {label} ({len(group)})")
        for issue in group:
            print(f"    {issue['slug']}")
            print(f"      {issue['detail']}")
            print(f"      {issue['path']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate tasky project integrity.")
    parser.add_argument("--project", help="Scope to a single project slug")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    flat = walk_tree(TASKY_ROOT, project_filter=args.project)

    issues = []
    issues += check_done_with_unchecked_criteria(flat)
    issues += check_done_with_empty_criteria(flat)
    issues += check_bypassed_dependencies(flat)
    issues += check_broken_references(flat)
    issues += check_prose_references(flat)

    if args.json:
        print(json.dumps(issues, indent=2))
        return

    if issues:
        print(f"\n  {len(issues)} issue(s) found\n")
    print_report(issues)

    if not issues:
        print()


if __name__ == "__main__":
    main()
