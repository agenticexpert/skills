#!/usr/bin/env python3
"""
Generate an ASCII Gantt chart from a storypad.md or series.md file.

Sections are rows, the timeline columns represent progress through beats.
Modeled after tasky/references/gantt.py but adapted for storypad sections.

Usage:
    python gantt.py <storypad.md>
    python gantt.py <series.md> --series
"""

import math
import re
import sys
from pathlib import Path


# Bar fill characters per completion level
BAR_FULL  = '█████'
BAR_MOST  = '▓▓▓▓▓'
BAR_SOME  = '▒▒▒▒▒'
BAR_NONE  = '░░░░░'

FILL_COUNT = 20
LEGEND = '█ done  ▓ most  ▒ some  ░ none'

EPISODE_ICON = {
    'planning':      '░',
    'brainstorming': '▒',
    'outlining':     '▓',
    'refining':      '█',
    'final':         '★',
}


# ── Parsing (shared logic) ────────────────────────────────────────

def parse_frontmatter(text):
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if kv:
            fm[kv.group(1).strip()] = kv.group(2).strip().strip('"').strip("'")
    return fm


def parse_sections(text):
    sections_match = re.search(r'^## Sections\s*\n(.*?)(?=\n## |\Z)', text,
                               re.MULTILINE | re.DOTALL)
    if not sections_match:
        return []

    body = sections_match.group(1)
    sections = []
    current = None
    in_prep = False

    for line in body.splitlines():
        h3 = re.match(r'^###\s+(.+)', line)
        if h3:
            if current:
                sections.append(current)
            current = {'name': h3.group(1).strip(), 'beats': [], 'prep': [], 'script': []}
            in_prep = False
            in_script = False
            continue
        if current is None:
            continue
        if re.match(r'^\s*prep\s*:\s*$', line, re.IGNORECASE):
            in_prep = True
            in_script = False
            continue
        if re.match(r'^\s*script\s*:\s*$', line, re.IGNORECASE):
            in_script = True
            in_prep = False
            continue
        if in_script:
            if line and not line.startswith(' ') and not line.startswith('\t'):
                in_script = False
            else:
                current['script'].append(line.rstrip())
                continue
        cb = re.match(r'^\s*-\s*\[([ xX])\]\s*(.*)', line)
        if cb:
            done = cb.group(1).lower() == 'x'
            item = {'done': done, 'text': cb.group(2).strip()}
            if in_prep:
                current['prep'].append(item)
            else:
                current['beats'].append(item)
    if current:
        sections.append(current)
    return sections


def parse_episodes(text):
    episodes = []
    for line in text.splitlines():
        m = re.match(
            r'\|\s*(\d+)\s*\|'
            r'\s*([^|]*?)\s*\|'
            r'\s*([^|]*?)\s*\|'
            r'\s*([^|]*?)\s*\|'
            r'\s*([^|]*?)\s*\|',
            line,
        )
        if m:
            ep, title, status, arc, premise = m.groups()
            episodes.append({
                'ep': int(ep.strip()), 'title': title.strip(),
                'status': status.strip(), 'arc': arc.strip(),
            })
    return episodes


# ── Gantt rendering ───────────────────────────────────────────────

def _bar_for_pct(pct):
    """Choose bar fill based on completion percentage."""
    if pct >= 100:
        return BAR_FULL
    elif pct >= 60:
        return BAR_MOST
    elif pct > 0:
        return BAR_SOME
    else:
        return BAR_NONE


def render_storypad(text):
    fm = parse_frontmatter(text)
    sections = parse_sections(text)
    if not sections:
        return '(no sections to visualize)'

    premise = fm.get('premise', '') or 'Untitled Storypad.
    venue = fm.get('venue', 'unknown')
    status = fm.get('status', 'unknown')

    out = []
    out.append(f'  {premise}')
    out.append(f'  [{venue}] — {status}')
    out.append('')

    # Layout dimensions
    n_sections = len(sections)
    label_w = max(len(s['name']) for s in sections) + 3
    label_w = max(label_w, 10)
    trailing_w = 8  # for "done/total"

    # Section numbers as column headers
    header = ' ' + ' ' * label_w
    for i in range(1, n_sections + 1):
        s = str(i)
        header += s + ' ' * (6 - len(s))
    out.append(header.rstrip())
    out.append('')

    # Top border
    out.append(' ' + '─' * (label_w - 1) + ('┬─────') * n_sections + '┬' + '─' * trailing_w)

    # Data rows — one bar per section, spanning its position
    for i, sec in enumerate(sections):
        b_total = len(sec['beats']) + len(sec['prep'])
        b_done = (sum(1 for b in sec['beats'] if b['done']) +
                  sum(1 for p in sec['prep'] if p['done']))
        pct = (b_done / b_total * 100) if b_total > 0 else 0

        label = ' ' + sec['name'].ljust(label_w - 1)

        content = ''
        for j in range(n_sections):
            if j == i:
                content += '│' + _bar_for_pct(pct)
            else:
                content += '│     '
        content += '│'

        count = f'{b_done}/{b_total}'
        trailing = count.rjust(trailing_w)

        out.append(label + content + trailing)

    # Bottom border
    out.append(' ' + '─' * (label_w - 1) + ('┴─────') * n_sections + '┴' + '─' * trailing_w)

    # Progress bar
    total = sum(len(s['beats']) + len(s['prep']) for s in sections)
    done = sum(
        sum(1 for b in s['beats'] if b['done']) +
        sum(1 for p in s['prep'] if p['done'])
        for s in sections
    )
    if total > 0:
        filled = math.floor(done / total * FILL_COUNT)
        pct = math.floor(done / total * 100)
    else:
        filled = 0
        pct = 0

    bar = '█' * filled + '░' * (FILL_COUNT - filled)
    # Align progress bar
    bracket_pos = label_w - FILL_COUNT - 1
    bracket_pos = max(1, bracket_pos)
    out.append(f"{' ' * bracket_pos}[{bar}] {pct}%  {done}/{total}")
    out.append('')
    out.append(f' {LEGEND}')

    return '\n'.join(out)


def render_series(text):
    fm = parse_frontmatter(text)
    episodes = parse_episodes(text)
    if not episodes:
        return '(no episodes to visualize)'

    series_name = fm.get('series-name', '') or 'Untitled Series'
    venue = fm.get('venue', 'unknown')
    status = fm.get('status', 'unknown')

    # Map statuses to progress percentages for the gantt bars
    status_pct = {
        'planning': 0, 'brainstorming': 20,
        'outlining': 50, 'refining': 80, 'final': 100,
    }

    out = []
    out.append(f'  {series_name}')
    out.append(f'  [{venue}] — {status}')
    out.append('')

    n_eps = len(episodes)
    label_w = max(len(e['title']) for e in episodes) + 6
    label_w = max(label_w, 12)
    trailing_w = 10

    # Episode number headers
    header = ' ' + ' ' * label_w
    for ep in episodes:
        s = f'Ep{ep["ep"]:02d}'
        header += s + ' ' * (6 - len(s))
    out.append(header.rstrip())
    out.append('')

    out.append(' ' + '─' * (label_w - 1) + ('┬─────') * n_eps + '┬' + '─' * trailing_w)

    for i, ep in enumerate(episodes):
        pct = status_pct.get(ep['status'], 0)
        label = ' ' + f"Ep{ep['ep']:02d} {ep['title']}".ljust(label_w - 1)

        content = ''
        for j in range(n_eps):
            if j == i:
                content += '│' + _bar_for_pct(pct)
            else:
                content += '│     '
        content += '│'

        trailing = ep['status'].rjust(trailing_w)
        out.append(label + content + trailing)

    out.append(' ' + '─' * (label_w - 1) + ('┴─────') * n_eps + '┴' + '─' * trailing_w)

    total = n_eps
    done = sum(1 for e in episodes if e['status'] == 'final')
    if total > 0:
        filled = math.floor(done / total * FILL_COUNT)
        pct_val = math.floor(done / total * 100)
    else:
        filled = 0
        pct_val = 0
    bar = '█' * filled + '░' * (FILL_COUNT - filled)
    out.append(f' [{bar}] {pct_val}%  {done}/{total} episodes')
    out.append('')
    out.append(f' {LEGEND}')

    return '\n'.join(out)


def main():
    if len(sys.argv) < 2:
        print('Usage: gantt.py <storypad.md>')
        print('       gantt.py <series.md> --series')
        sys.exit(1)

    path = sys.argv[1]
    is_series = '--series' in sys.argv
    text = Path(path).read_text(encoding='utf-8')

    if is_series:
        print(render_series(text))
    else:
        print(render_storypad(text))


if __name__ == '__main__':
    main()
