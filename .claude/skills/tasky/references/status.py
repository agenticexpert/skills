#!/usr/bin/env python3
"""
Update a task or milestone status and cascade all index files.

Usage (task):
    python3 status.py <task-file-path> done
    python3 status.py <task-file-path> undone

Usage (milestone):
    python3 status.py <milestone-file-path> active
    python3 status.py <milestone-file-path> planned
    python3 status.py <milestone-file-path> completed

Auto-detected by path: task files live under tasks/{feature}/tasks/,
milestone files live under roadmaps/{roadmap}/milestones/.
"""

import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Status logic
# ---------------------------------------------------------------------------

STATUS_DONE   = 'completed'
STATUS_UNDONE = 'active'  # reverting completed → active

TASK_ACTIONS      = {'done', 'undone'}
MILESTONE_ACTIONS = {'active', 'planned', 'completed'}

# Maps task/milestone status → issue status
ISSUE_STATUS_MAP = {
    'completed': 'complete',
    'active':    'active',
    'pending':   'backburner',
    'planned':   'backburner',
}


def new_status(action):
    return STATUS_DONE if action == 'done' else STATUS_UNDONE


def is_milestone_path(path):
    """Return True if path is a milestone file (under roadmaps/.../milestones/)."""
    return 'milestones' in path.parts and 'roadmaps' in path.parts


# ---------------------------------------------------------------------------
# Generic file helpers
# ---------------------------------------------------------------------------

def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')
    print(f'  updated  {path}')


def set_bold_field(text, field, value):
    """Replace **Field**: <value> line."""
    return re.sub(
        rf'^\*\*{re.escape(field)}\*\*:.*$',
        f'**{field}**: {value}',
        text,
        flags=re.MULTILINE,
    )


def get_bold_field(text, field):
    """Extract value of **Field**: <value>."""
    m = re.search(rf'^\*\*{re.escape(field)}\*\*:\s*(.+)$', text, re.MULTILINE)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------------------
# Task manifest helpers
# ---------------------------------------------------------------------------

def update_manifest_status(manifest_path, task_id, status):
    """Update the Status column for a task row in tasks/index.md."""
    text = read(manifest_path)

    def replace_row(m):
        row = m.group(0)
        # Replace last column (status) — table row ends with | status |
        return re.sub(r'\|\s*\S+\s*\|?\s*$', f'| {status} |', row)

    # Match table row whose first cell is the task ID (e.g. | 01 | or | 01.5 |)
    pattern = rf'^\|[ \t]*{re.escape(task_id)}[ \t]*\|.*$'
    new_text = re.sub(pattern, replace_row, text, flags=re.MULTILINE)
    write(manifest_path, new_text)
    return new_text


def compute_feature_status(manifest_text):
    """Derive feature status from all task rows in the manifest."""
    statuses = re.findall(r'\|\s*(completed|active|pending)\s*\|', manifest_text)
    if not statuses:
        return 'pending'
    if any(s == 'active' for s in statuses):
        return 'active'
    if all(s == 'completed' for s in statuses):
        return 'completed'
    return 'active' if any(s == 'active' for s in statuses) else 'pending'


# ---------------------------------------------------------------------------
# Index table helpers
# ---------------------------------------------------------------------------

def update_index_status(index_path, name_value, status):
    """Update Status column for a row matching name_value in any index table."""
    text = read(index_path)

    def replace_status(m):
        row = m.group(0)
        return re.sub(r'\|\s*(?:completed|active|pending|planned)\s*\|', f'| {status} |', row, count=1)

    pattern = rf'^\|[^|]*\b{re.escape(name_value)}\b[^|]*\|.*$'
    new_text = re.sub(pattern, replace_status, text, flags=re.MULTILINE)
    write(index_path, new_text)


# ---------------------------------------------------------------------------
# Milestone helpers
# ---------------------------------------------------------------------------

def parse_milestone_ref(task_text):
    """Return (roadmap, milestone_id) or None. Handles **Milestone** and **Milestones**."""
    m = get_bold_field(task_text, 'Milestone') or get_bold_field(task_text, 'Milestones')
    if not m:
        return None
    # Take first entry if multiple: "product-v1/02-beta, product-v1/03-ga"
    first = m.split(',')[0].strip()
    parts = first.split('/')
    if len(parts) != 2:
        return None
    return parts[0].strip(), parts[1].strip()


def update_milestone_index(milestone_index_path, task_title, task_status, task_id=None):
    """Update Done/Total and Status in milestones/index.md."""
    text = read(milestone_index_path)

    # --- Update task row status in Assigned Tasks section ---
    def replace_task_row(m):
        row = m.group(0)
        return re.sub(r'\|\s*(?:completed|active|pending)\s*\|',
                      f'| {task_status} |', row, count=1)

    # Match by task_id (second column = Task ID) if provided, else fall back to title
    if task_id:
        pattern = rf'^\|[^|]*\|\s*{re.escape(task_id)}\s*\|.*$'
        text = re.sub(pattern, replace_task_row, text, flags=re.MULTILINE)
    elif task_title:
        pattern = rf'^\|[^|]*\b{re.escape(task_title)}\b[^|]*\|.*$'
        text = re.sub(pattern, replace_task_row, text, flags=re.MULTILINE)

    # --- Recompute Done/Total from the milestone index table row ---
    # The milestone index table has: | ID | Name | Phase | File | Status | Done | Total |
    # We need to recount from the Assigned Tasks table instead.
    # Assigned Tasks table has 4 cols: Feature | Task ID | Title | Status
    # Skip 3 non-pipe segments to reach the Status column
    assigned = re.findall(
        r'^\|[^|]+\|[^|]+\|[^|]+\|\s*(completed|active|pending)\s*\|',
        text, re.MULTILINE
    )
    # Filter out header rows (they won't match status pattern)
    done_count  = sum(1 for s in assigned if s == 'completed')
    total_count = len(assigned)

    # Recompute milestone status
    if total_count == 0:
        ms_status = 'planned'
    elif done_count == total_count:
        ms_status = 'completed'
    elif done_count > 0 or any(s == 'active' for s in assigned):
        ms_status = 'active'
    else:
        ms_status = 'planned'

    write(milestone_index_path, text)
    return done_count, total_count, ms_status


def update_milestone_index_row(milestones_index_path, milestone_id, status, done=None, total=None):
    """Update Status (and optionally Done/Total) columns in the roadmap's milestones/index.md."""
    text = read(milestones_index_path)

    def replace_row(m):
        row = m.group(0)
        row = re.sub(r'\|\s*(?:completed|active|planned)\s*\|',
                     f'| {status} |', row, count=1)
        if done is not None and total is not None:
            row = re.sub(r'\|\s*\d+\s*\|\s*\d+\s*\|',
                         f'| {done} | {total} |', row, count=1)
        return row

    pattern = rf'^\|\s*{re.escape(milestone_id)}\s*\|.*$'
    new_text = re.sub(pattern, replace_row, text, flags=re.MULTILINE)
    write(milestones_index_path, new_text)
    return new_text


# ---------------------------------------------------------------------------
# Issue helpers
# ---------------------------------------------------------------------------

def parse_issue_ref(text):
    """Return issue ID string (e.g. '001') or None."""
    m = get_bold_field(text, 'Issue')
    return m.strip().lstrip('0').zfill(3) if m else None


def find_issue_file(issues_dir, issue_id):
    """Find issues/NNN-slug.md, supporting zero-padded variants."""
    candidates = list(issues_dir.glob(f'{issue_id}*.md'))
    candidates = [f for f in candidates if f.name != 'index.md']
    return candidates[0] if candidates else None


def cascade_issue(text, tasky_root, status):
    """If text has **Issue** field, update issue file + index. Returns issue_id or None."""
    issue_id = parse_issue_ref(text)
    if not issue_id:
        return None

    issues_dir  = tasky_root / 'issues'
    issues_idx  = issues_dir / 'index.md'
    issue_file  = find_issue_file(issues_dir, issue_id)

    if not issue_file:
        print(f'  warning: no issue file found for {issue_id} in {issues_dir}')
        return issue_id

    issue_status = ISSUE_STATUS_MAP.get(status, 'backburner')

    # Update issue file status
    issue_text = read(issue_file)
    issue_text = set_bold_field(issue_text, 'Status', issue_status)
    write(issue_file, issue_text)

    # Update issues/index.md row
    update_index_status(issues_idx, issue_id, issue_status)

    return issue_id


def compute_roadmap_status(milestones_index_text):
    """Derive roadmap status from milestone statuses."""
    statuses = re.findall(
        r'\|\s*(completed|active|planned)\s*\|\s*\d+\s*\|\s*\d+\s*\|',
        milestones_index_text
    )
    if not statuses:
        return 'planned'
    if all(s == 'completed' for s in statuses):
        return 'completed'
    if any(s == 'active' for s in statuses):
        return 'active'
    return 'planned'


# ---------------------------------------------------------------------------
# Task cascade
# ---------------------------------------------------------------------------

def cascade(task_path, action):
    task_path = Path(task_path).resolve()
    status    = new_status(action)

    print(f'\ntasky status: {action} → {task_path.name}\n')

    # --- Derive paths from task file location ---
    # Expected structure:
    #   <root>/agents/docs/tasky/tasks/<feature>/tasks/<NN-task.md>
    tasks_dir      = task_path.parent                        # .../tasks/
    feature_dir    = tasks_dir.parent                        # .../auth/
    feature_name   = feature_dir.name
    tasky_root     = feature_dir.parent.parent               # .../agents/docs/tasky/
    manifest_path  = tasks_dir / 'index.md'
    feature_index  = feature_dir / 'index.md'
    global_index   = tasky_root / 'tasks' / 'index.md'
    roadmaps_dir   = tasky_root / 'roadmaps'

    # --- 1. Task file ---
    task_text = read(task_path)
    task_text = set_bold_field(task_text, 'Status', status)
    write(task_path, task_text)

    # --- 2. Task manifest ---
    task_id = task_path.stem.split('-')[0]  # "01" from "01-login-flow"
    manifest_text = update_manifest_status(manifest_path, task_id, status)

    # --- 3. Feature overview ---
    feature_status = compute_feature_status(manifest_text)
    feat_text = read(feature_index)
    feat_text = set_bold_field(feat_text, 'Status', feature_status)
    write(feature_index, feat_text)

    # --- 4. Global tasks index ---
    update_index_status(global_index, feature_name, feature_status)

    # --- 4b. Issue cascade (if task references an issue) ---
    issue_id = cascade_issue(task_text, tasky_root, status)

    # --- 5. Milestone cascade (if task is assigned) ---
    milestone_ref = parse_milestone_ref(task_text)
    if milestone_ref:
        roadmap_name, milestone_id = milestone_ref
        milestone_dir   = roadmaps_dir / roadmap_name / 'milestones'
        # Support both "01.md" and "01 - name.md" filename conventions
        candidates = list(milestone_dir.glob(f'{milestone_id}*.md'))
        candidates = [f for f in candidates if f.name != 'index.md']
        if not candidates:
            print(f'  warning: no milestone file found for {milestone_id} in {milestone_dir}')
            milestone_file = milestone_dir / f'{milestone_id}.md'  # fallback (will fail gracefully)
        else:
            milestone_file = candidates[0]
        milestones_idx  = milestone_dir / 'index.md'
        roadmap_idx     = roadmaps_dir / 'index.md'

        # Update assigned tasks table in the milestone file
        task_title = get_bold_field(task_text, 'Title') or task_path.stem
        done, total, ms_status = update_milestone_index(milestone_file, task_title, status, task_id=task_id)

        # Update milestones/index.md row
        mi_text = update_milestone_index_row(milestones_idx, milestone_id, ms_status, done=done, total=total)

        # --- 6. Roadmap index ---
        roadmap_status = compute_roadmap_status(mi_text)
        update_index_status(roadmap_idx, roadmap_name, roadmap_status)
    else:
        print('  (no milestone assigned — skipping milestone + roadmap cascade)')

    print(f'\ndone. feature={feature_status}', end='')
    if milestone_ref:
        print(f'  milestone={ms_status}  roadmap={roadmap_status}', end='')
    if issue_id:
        print(f'  issue={issue_id}→{ISSUE_STATUS_MAP.get(status, "backburner")}', end='')
    print()


# ---------------------------------------------------------------------------
# Milestone cascade
# ---------------------------------------------------------------------------

def milestone_cascade(milestone_path, status):
    milestone_path = Path(milestone_path).resolve()

    print(f'\ntasky status: {status} → {milestone_path.name}\n')

    # --- Derive paths from milestone file location ---
    # Expected structure:
    #   <root>/agents/docs/tasky/roadmaps/<roadmap>/milestones/<NN - name.md>
    milestones_dir = milestone_path.parent               # .../milestones/
    roadmap_dir    = milestones_dir.parent               # .../blocky/
    roadmap_name   = roadmap_dir.name
    roadmaps_dir   = roadmap_dir.parent                  # .../roadmaps/
    milestones_idx = milestones_dir / 'index.md'
    roadmap_idx    = roadmaps_dir / 'index.md'

    # Milestone ID: "02 - containers-nodes.md" → "02"
    milestone_id = milestone_path.stem.split(' ')[0]

    tasky_root = roadmaps_dir.parent                     # .../agents/docs/tasky/

    # --- 1. Milestone file ---
    ms_text = read(milestone_path)
    ms_text = set_bold_field(ms_text, 'Status', status)
    write(milestone_path, ms_text)

    # --- 2. Milestones index row (Status only — Done/Total unchanged) ---
    mi_text = update_milestone_index_row(milestones_idx, milestone_id, status)

    # --- 3. Roadmap index ---
    roadmap_status = compute_roadmap_status(mi_text)
    update_index_status(roadmap_idx, roadmap_name, roadmap_status)

    # --- 4. Issue cascade (if milestone references an issue) ---
    issue_id = cascade_issue(ms_text, tasky_root, status)

    print(f'\ndone. milestone={status}  roadmap={roadmap_status}', end='')
    if issue_id:
        print(f'  issue={issue_id}→{ISSUE_STATUS_MAP.get(status, "backburner")}', end='')
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print('Usage: status.py <task-file-path> done|undone')
        print('   or: status.py <milestone-file-path> active|planned|completed')
        sys.exit(1)

    path   = Path(sys.argv[1]).resolve()
    action = sys.argv[2]

    if is_milestone_path(path):
        if action not in MILESTONE_ACTIONS:
            print(f'Milestone actions: {", ".join(sorted(MILESTONE_ACTIONS))}')
            sys.exit(1)
        milestone_cascade(path, action)
    else:
        if action not in TASK_ACTIONS:
            print(f'Task actions: {", ".join(sorted(TASK_ACTIONS))}')
            sys.exit(1)
        cascade(path, action)


if __name__ == '__main__':
    main()
