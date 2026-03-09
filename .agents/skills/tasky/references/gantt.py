#!/usr/bin/env python3
"""
Generate an ASCII Gantt chart from a tasky milestones/index.md file.

Usage:
    python gantt.py <milestones/index.md>
    python gantt.py <roadmap-name> <milestones/index.md>
"""

import math
import re
import sys
from pathlib import Path

# Bar fill characters per status
BAR_CHAR = {
    'completed': '█████',
    'active':    '▓▓▓▓▓',
    'at-risk':   '▒▒▒▒▒',
    'planned':   '░░░░░',
}

LEGEND = '█ completed  ▓ active  ▒ at risk  ░ planned'
FILL_COUNT = 20  # number of chars in the progress bar fill


def parse_phase(phase_str):
    """Parse '3' or '2–10' or '2-10' into (start, end)."""
    s = phase_str.strip().replace('–', '-').replace('—', '-')
    if '-' in s:
        a, b = s.split('-', 1)
        return float(a.strip()), float(b.strip())
    v = float(s.strip())
    return v, v


def parse_index(path):
    """Parse milestones/index.md. Returns (roadmap_name, milestones)."""
    text = Path(path).read_text(encoding='utf-8')

    # Roadmap name from heading: "# Blocky — Milestone Index"
    name_match = re.search(r'^#\s+(.+?)\s+[—–-]+\s+Milestone Index', text, re.MULTILINE)
    roadmap_name = name_match.group(1).strip() if name_match else 'Roadmap'

    milestones = []
    for line in text.splitlines():
        m = re.match(
            r'\|\s*(\d[\d.]*)\s*\|'   # ID
            r'\s*([^|]+?)\s*\|'        # Name
            r'\s*([^|]+?)\s*\|'        # Phase
            r'\s*([^|]+?)\s*\|'        # File
            r'\s*([^|]+?)\s*\|'        # Status
            r'\s*(\d+)\s*\|'           # Done
            r'\s*(\d+)\s*\|',          # Total
            line,
        )
        if m:
            id_, name, phase_str, _file, status, done, total = m.groups()
            phase_start, phase_end = parse_phase(phase_str)
            milestones.append({
                'id':          id_.strip().zfill(2),
                'name':        name.strip(),
                'phase_start': phase_start,
                'phase_end':   phase_end,
                'status':      status.strip(),
                'done':        int(done),
                'total':       int(total),
            })

    return roadmap_name, milestones


def render(roadmap_name, milestones):
    if not milestones:
        return '(no milestones)'

    # --- Layout dimensions ---

    # Phase range — collect all integer phases min..max plus any fractional boundaries
    min_phase = min(m['phase_start'] for m in milestones)
    max_phase = max(m['phase_end']   for m in milestones)
    all_phases = set(range(int(math.floor(min_phase)), int(math.ceil(max_phase)) + 1))
    for m in milestones:
        all_phases.add(m['phase_start'])
        all_phases.add(m['phase_end'])
    phases = sorted(all_phases)
    n = len(phases)

    # Label column display width.
    # Prefix: 1 space — no status dot rendered (dots hidden for now)
    max_id_name = max(len(m['id']) + 1 + len(m['name']) for m in milestones)
    label_w = 1 + max_id_name + 2   # 1 prefix + content + 2 trailing padding

    # Trailing column width: 8 if any done/total value has 3+ digits, else 6
    max_val = max(max(m['done'], m['total']) for m in milestones)
    trailing_w = 8 if max_val >= 100 else 6

    # Total line width:
    #   label_w  +  (│ + 5 chars) × n phases  +  (│ + trailing_w chars)
    line_w = label_w + 6 * n + 1 + trailing_w

    # Key column positions (0-indexed character positions in the line)
    pos_1st  = label_w          # 1st ┴  →  ] sits here
    pos_2nd  = label_w + 6      # 2nd ┴  →  % sits here (last char of pct string)
    pos_last = line_w - 1       # last char of line  →  last digit of count sits here

    INDENT2 = '  '    # 2-space indent (title)
    INDENT6 = ' '     # 1-space indent (header, border, legend)
    DASHES  = label_w - len(INDENT6)

    out = []

    # Title
    out.append(f'{INDENT2}{roadmap_name}')
    out.append('')

    # Header: phase numbers sit at ┬/┴ positions
    header = INDENT6 + 'Milestone' + ' ' * (label_w - len(INDENT6) - len('Milestone'))
    for p in phases:
        ps = str(p)
        header += ps + ' ' * (6 - len(ps))
    out.append(header.rstrip())
    out.append('')

    # Top border
    out.append(INDENT6 + '─' * DASHES + ('┬─────') * n + '┬' + '─' * trailing_w)

    # Data rows
    for m in milestones:
        status  = m['status']
        id_name = f"{m['id']} {m['name']}"

        # Label (display width = label_w)
        prefix    = ' '
        display_w = 1

        padding = label_w - display_w - len(id_name)
        label = prefix + id_name + ' ' * padding

        # Phase bars
        content = ''
        for p in phases:
            if m['phase_start'] <= p <= m['phase_end']:
                bar = BAR_CHAR.get(status, '░░░░░')
            elif p < m['phase_start']:
                bar = '· · ·'  # leader dots — guide eye to where the bar starts
            else:
                bar = '     '
            content += f'│{bar}'
        content += '│'

        # Trailing count — right-justified in trailing_w chars
        count = f'{m["done"]}/{m["total"]}'
        trailing = count.rjust(trailing_w)

        out.append(label + content + trailing)

    # Bottom border
    out.append(INDENT6 + '─' * DASHES + ('┴─────') * n + '┴' + '─' * trailing_w)

    # --- Progress bar ---
    total_done  = sum(m['done']  for m in milestones)
    total_tasks = sum(m['total'] for m in milestones)

    if total_tasks > 0:
        filled = math.floor(total_done / total_tasks * FILL_COUNT)
        pct    = math.floor(total_done / total_tasks * 100)
    else:
        filled = 0
        pct    = 0

    bar_str   = '█' * filled + '░' * (FILL_COUNT - filled)
    pct_str   = f'{pct}%'
    count_str = f'{total_done}/{total_tasks}'

    # [ at bracket_pos, ] at pos_1st
    bracket_pos = pos_1st - FILL_COUNT - 1

    prog = ' ' * bracket_pos
    prog += f'[{bar_str}]'
    # pct_str: last char (%) sits at pos_2nd
    pct_start = pos_2nd - len(pct_str) + 1
    gap1 = pct_start - (pos_1st + 1)
    prog += ' ' * gap1 + pct_str
    # count_str: last char sits at pos_last
    count_start = pos_last - len(count_str) + 1
    gap2 = count_start - (pos_2nd + 1)
    prog += ' ' * gap2 + count_str

    out.append(prog)
    out.append('')

    # Legend — always show all symbols
    out.append(f'{INDENT6}{LEGEND}')

    return '\n'.join(out)


def main():
    if len(sys.argv) == 2:
        path = sys.argv[1]
        roadmap_name, milestones = parse_index(path)
    elif len(sys.argv) == 3:
        roadmap_name = sys.argv[1]
        _, milestones = parse_index(sys.argv[2])
    else:
        print('Usage: gantt.py <milestones/index.md>')
        print('   or: gantt.py <roadmap-name> <milestones/index.md>')
        sys.exit(1)

    print(render(roadmap_name, milestones))


if __name__ == '__main__':
    main()
