#!/usr/bin/env python3
"""
Generate a tabular view of sections from a storypad.md or series.md file.

Usage:
    python table.py <storypad.md>
    python table.py <series.md> --series
"""

import math
import re
import sys
from pathlib import Path


FILL_COUNT = 20

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
                'premise': premise.strip(),
            })
    return episodes


def parse_threads(text):
    threads = []
    valid = {'active', 'resolved', 'dormant', 'recurring'}
    for line in text.splitlines():
        m = re.match(
            r'\|\s*([^|]+?)\s*\|'
            r'\s*([^|]*?)\s*\|'
            r'\s*([^|]*?)\s*\|'
            r'\s*([^|]*?)\s*\|'
            r'\s*([^|]*?)\s*\|',
            line,
        )
        if m:
            name, status = m.group(1).strip(), m.group(2).strip()
            if name and status in valid:
                threads.append({
                    'name': name, 'status': status,
                    'episodes': m.group(5).strip(),
                })
    return threads


# ── Table rendering ───────────────────────────────────────────────

def render_storypad(text):
    fm = parse_frontmatter(text)
    sections = parse_sections(text)
    if not sections:
        return '(no sections to visualize)'

    premise = fm.get('premise', '') or 'Untitled Storypad'
    venue = fm.get('venue', 'unknown')
    status = fm.get('status', 'unknown')

    out = []
    out.append(f'  {premise}')
    out.append(f'  [{venue}] — {status}')
    out.append('')

    # Column widths
    name_w = max(len(s['name']) for s in sections)
    name_w = max(name_w, 7)  # "Section"

    header = f"  {'#':<4}  {'Section':<{name_w}}  {'Beats':>7}  {'Prep':>6}  {'Script':>6}  Progress"
    out.append(header)
    out.append('  ' + '─' * (len(header) - 2))

    total_beats = 0
    total_done = 0

    for i, sec in enumerate(sections, 1):
        b_total = len(sec['beats'])
        b_done = sum(1 for b in sec['beats'] if b['done'])
        p_total = len(sec['prep'])
        p_done = sum(1 for p in sec['prep'] if p['done'])
        has_script = bool([l for l in sec['script'] if l.strip()])

        total_beats += b_total + p_total
        total_done += b_done + p_done

        beats_str = f'{b_done}/{b_total}'
        prep_str = f'{p_done}/{p_total}' if p_total > 0 else '—'
        script_str = '✎' if has_script else '—'

        # Mini progress bar (5 chars)
        all_total = b_total + p_total
        all_done = b_done + p_done
        if all_total > 0:
            filled = round(all_done / all_total * 5)
        else:
            filled = 0
        mini_bar = '█' * filled + '░' * (5 - filled)

        out.append(f'  {i:<4}  {sec["name"]:<{name_w}}  {beats_str:>7}  {prep_str:>6}  {script_str:>6}  {mini_bar}')

    out.append('  ' + '─' * (len(header) - 2))

    # Overall progress
    if total_beats > 0:
        pct = math.floor(total_done / total_beats * 100)
        filled = math.floor(total_done / total_beats * FILL_COUNT)
    else:
        pct = 0
        filled = 0

    bar = '█' * filled + '░' * (FILL_COUNT - filled)
    out.append(f'  [{bar}] {pct}%  {total_done}/{total_beats} total')

    return '\n'.join(out)


def render_series(text):
    fm = parse_frontmatter(text)
    episodes = parse_episodes(text)
    threads = parse_threads(text)

    series_name = fm.get('series-name', '') or 'Untitled Series'
    venue = fm.get('venue', 'unknown')
    status = fm.get('status', 'unknown')

    out = []
    out.append(f'  {series_name}')
    out.append(f'  [{venue}] — {status}')
    out.append('')

    if not episodes:
        out.append('  (no episodes)')
        return '\n'.join(out)

    title_w = max(len(e['title']) for e in episodes)
    title_w = max(min(title_w, 30), 10)

    header = f"  {'Ep':>4}  {'Title':<{title_w}}  {'Status':<14}  {'Arc':<12}"
    out.append(header)
    out.append('  ' + '─' * (len(header) - 2))

    for ep in episodes:
        icon = EPISODE_ICON.get(ep['status'], '?')
        title = ep['title'] or '(untitled)'
        if len(title) > title_w:
            title = title[:title_w - 1] + '…'
        out.append(f"  {ep['ep']:>4}  {icon} {title:<{title_w - 2}}  {ep['status']:<14}  {ep['arc']:<12}")

    out.append('  ' + '─' * (len(header) - 2))

    if threads:
        thread_icons = {'active': '●', 'resolved': '✓', 'dormant': '○', 'recurring': '↻'}
        out.append('')
        out.append('  Continuity Threads')
        for t in threads:
            icon = thread_icons.get(t['status'], '?')
            eps = t['episodes'] or '—'
            out.append(f"  {icon} {t['name']}  [{t['status']}]  ep: {eps}")

    out.append('')
    total = len(episodes)
    done = sum(1 for e in episodes if e['status'] == 'final')
    pct = math.floor(done / total * 100) if total else 0
    filled = math.floor(done / total * FILL_COUNT) if total else 0
    bar = '█' * filled + '░' * (FILL_COUNT - filled)
    out.append(f'  [{bar}] {pct}%  {done}/{total} episodes complete')

    return '\n'.join(out)


def main():
    if len(sys.argv) < 2:
        print('Usage: table.py <storypad.md>')
        print('       table.py <series.md> --series')
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
