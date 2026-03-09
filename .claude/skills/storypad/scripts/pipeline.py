#!/usr/bin/env python3
"""
Generate a pipeline visualization from a storypad.md file.

Renders a horizontal pipeline bar of sections with prep dependencies
dangling below (aligned to their parent section), followed by expanded
section detail with beats and prep checklists.

Usage:
    python pipeline.py <storypad.md>
    python pipeline.py <series.md> --series
"""

import math
import re
import sys
from pathlib import Path


# ── Status indicators ──────────────────────────────────────────────

EPISODE_ICON = {
    'planning':      '░',
    'brainstorming': '▒',
    'outlining':     '▓',
    'refining':      '█',
    'final':         '★',
}

FILL_COUNT = 20


# ── Parsing ────────────────────────────────────────────────────────

def parse_frontmatter(text):
    """Extract YAML frontmatter as a dict of key: value strings."""
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
    """Parse ## Sections into a list of section dicts.

    Each section has:
      name: str
      beats: list of (done: bool, text: str)
      prep:  list of (done: bool, text: str)
    """
    # Find the ## Sections block
    sections_match = re.search(r'^## Sections\s*\n(.*?)(?=\n## |\Z)', text,
                               re.MULTILINE | re.DOTALL)
    if not sections_match:
        return []

    body = sections_match.group(1)
    sections = []
    current = None
    in_prep = False

    for line in body.splitlines():
        # New section heading: ### Name
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

        # Prep marker
        if re.match(r'^\s*prep\s*:\s*$', line, re.IGNORECASE):
            in_prep = True
            in_script = False
            continue

        # Script marker
        if re.match(r'^\s*script\s*:\s*$', line, re.IGNORECASE):
            in_script = True
            in_prep = False
            continue

        # Script content (indented lines under script:)
        if in_script:
            # Stop script capture on unindented non-empty lines that aren't content
            if line and not line.startswith(' ') and not line.startswith('\t'):
                in_script = False
                # fall through to check for other markers below
            else:
                current['script'].append(line.rstrip())
                continue

        # Checklist item
        cb = re.match(r'^\s*-\s*\[([ xX])\]\s*(.*)', line)
        if cb:
            done = cb.group(1).lower() == 'x'
            item_text = cb.group(2).strip()
            if in_prep:
                current['prep'].append({'done': done, 'text': item_text})
            else:
                current['beats'].append({'done': done, 'text': item_text})

    if current:
        sections.append(current)

    return sections


def parse_episodes(text):
    """Parse the episode arc table from series.md."""
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
                'ep':      int(ep.strip()),
                'title':   title.strip(),
                'status':  status.strip(),
                'arc':     arc.strip(),
                'premise': premise.strip(),
            })
    return episodes


def parse_threads(text):
    """Parse the continuity threads table from series.md."""
    threads = []
    valid_statuses = {'active', 'resolved', 'dormant', 'recurring'}
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
            name, status, intro, last_ref, eps = m.groups()
            name = name.strip()
            status = status.strip()
            if name and status in valid_statuses:
                threads.append({
                    'name':     name,
                    'status':   status,
                    'intro':    intro.strip(),
                    'last_ref': last_ref.strip(),
                    'episodes': eps.strip(),
                })
    return threads


# ── Layout constants ───────────────────────────────────────────────

PREP_LABEL_MAX = 15   # max chars for a prep label (inside cell)
CELL_GAP = 2          # minimum spaces between adjacent prep labels
CELL_PAD = 2          # padding inside cell borders (1 each side)


# ── Pipeline bar rendering ─────────────────────────────────────────

def _calc_cell_widths(sections):
    """Calculate cell widths driven by the widest content in each column.

    Width = max(section name, widest prep label capped at PREP_LABEL_MAX)
    plus CELL_PAD, plus CELL_GAP contribution so neighbors don't clash.
    """
    widths = []
    for sec in sections:
        name_w = len(sec['name'])
        prep_w = 0
        if sec['prep']:
            prep_w = min(
                max(len(p['text']) for p in sec['prep']),
                PREP_LABEL_MAX,
            )
        inner = max(name_w, prep_w)
        # cell width = inner content + padding + gap margin
        widths.append(inner + CELL_PAD + CELL_GAP)
    return widths


def render_pipeline_bar(sections, indent=2):
    """Render the horizontal pipeline bar. Returns (lines, midpoints, cell_widths).

    The bottom border uses ┬ at midpoints of sections that have prep,
    so pipes can flow downward from those points.
    """
    names = [s['name'] for s in sections]
    has_prep = [bool(s['prep']) for s in sections]
    cell_widths = _calc_cell_widths(sections)

    pad = ' ' * indent

    # Calculate midpoints (character position of center of each cell)
    midpoints = []
    pos = indent + 1  # after the initial border char
    for w in cell_widths:
        center = pos + w // 2
        midpoints.append(center)
        pos += w + 1  # +1 for separator

    # Top border
    top = pad + '┌'
    for i, w in enumerate(cell_widths):
        top += '─' * w
        top += '┬' if i < len(cell_widths) - 1 else '┐'

    # Content row
    mid_line = pad + '│'
    for i, (name, w) in enumerate(zip(names, cell_widths)):
        mid_line += name.center(w)
        mid_line += '│'

    # Bottom border — embed ┬ at midpoints of sections with prep
    bot_chars = list(pad + '└')
    cursor = len(bot_chars)
    for i, w in enumerate(cell_widths):
        for j in range(w):
            if has_prep[i] and (cursor + j) == midpoints[i]:
                bot_chars.append('┬')
            else:
                bot_chars.append('─')
        cursor += w
        if i < len(cell_widths) - 1:
            bot_chars.append('┴')
        else:
            bot_chars.append('┘')
        cursor += 1

    bot = ''.join(bot_chars)

    return [top, mid_line, bot], midpoints, cell_widths


# ── Prep diagram rendering ────────────────────────────────────────

def render_prep_diagram(sections, midpoints, cell_widths, line_width):
    """Render prep items dangling below the pipeline bar, aligned to midpoints.

    Each section's prep items stack vertically below that section's
    midpoint. Labels are truncated to fit the cell width (PREP_LABEL_MAX)
    and centered on the midpoint. Pipes (│) connect levels.
    """
    # Gather columns: (section_index, midpoint, max_label_width, [labels])
    prep_cols = []
    for i, sec in enumerate(sections):
        if sec['prep']:
            max_w = min(cell_widths[i] - CELL_GAP, PREP_LABEL_MAX)
            labels = [p['text'] for p in sec['prep']]
            prep_cols.append((i, midpoints[i], max_w, labels))

    if not prep_cols:
        return []

    max_depth = max(len(col[3]) for col in prep_cols)
    out = []

    for depth in range(max_depth):
        # Pipe row: │ at each midpoint that has an item at this depth
        pipe_line = [' '] * line_width
        for _, mid, _, labels in prep_cols:
            if depth < len(labels) and mid < line_width:
                pipe_line[mid] = '│'
        out.append(''.join(pipe_line).rstrip())

        # Label row: centered on midpoint, truncated to max_w
        label_line = [' '] * line_width
        for _, mid, max_w, labels in prep_cols:
            if depth < len(labels):
                label = labels[depth]
                if len(label) > max_w:
                    label = label[:max_w - 1] + '…'
                start = max(0, mid - len(label) // 2)
                for j, ch in enumerate(label):
                    pos = start + j
                    if pos < line_width:
                        label_line[pos] = ch
        out.append(''.join(label_line).rstrip())

    return out


# ── Section detail rendering ──────────────────────────────────────

def render_section_detail(sections):
    """Render expanded section details with beats and prep checklists."""
    out = []

    for sec in sections:
        total_beats = len(sec['beats'])
        done_beats = sum(1 for b in sec['beats'] if b['done'])

        script_lines = [l for l in sec['script'] if l.strip()]
        script_tag = '  ✎' if script_lines else ''
        out.append(f"  {sec['name']} ({done_beats}/{total_beats}){script_tag}")

        for beat in sec['beats']:
            check = 'x' if beat['done'] else ' '
            out.append(f"   [{check}] {beat['text']}")

        if sec['prep']:
            total_prep = len(sec['prep'])
            done_prep = sum(1 for p in sec['prep'] if p['done'])
            out.append(f"   prep: ({done_prep}/{total_prep})")
            for prep in sec['prep']:
                check = 'x' if prep['done'] else ' '
                out.append(f"    [{check}] {prep['text']}")

        if script_lines:
            # Show first line of script as preview
            preview = script_lines[0][:60] + ('…' if len(script_lines[0]) > 60 else '')
            out.append(f"   script: \"{preview}\"")

        out.append('')

    return out


# ── Progress bar ───────────────────────────────────────────────────

def render_progress(sections):
    """Render progress bar from beat completion."""
    total = sum(len(s['beats']) + len(s['prep']) for s in sections)
    done = sum(
        sum(1 for b in s['beats'] if b['done']) +
        sum(1 for p in s['prep'] if p['done'])
        for s in sections
    )

    if total > 0:
        pct = math.floor(done / total * 100)
        filled = math.floor(done / total * FILL_COUNT)
    else:
        pct = 0
        filled = 0

    bar = '█' * filled + '░' * (FILL_COUNT - filled)
    return f'  [{bar}] {pct}%  {done}/{total} beats'


# ── Single sketch rendering ───────────────────────────────────────

def render_storypad(text):
    """Render a single storypad as pipeline + detail."""
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

    # Pipeline bar
    bar_lines, midpoints, cell_widths = render_pipeline_bar(sections)
    out.extend(bar_lines)

    # Calculate line width for prep diagram
    line_width = max(len(l) for l in bar_lines) + 10

    # Prep diagram
    prep_lines = render_prep_diagram(sections, midpoints, cell_widths, line_width)
    if prep_lines:
        out.extend(prep_lines)

    out.append('')

    # Section details
    out.extend(render_section_detail(sections))

    # Progress
    out.append(render_progress(sections))

    return '\n'.join(out)


# ── Series rendering ──────────────────────────────────────────────

def render_series(text):
    """Render a series overview."""
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

    # Episode pipeline bar — treat episodes as sections
    ep_sections = [{'name': e['title'] or f"Ep {e['ep']:02d}"} for e in episodes]
    names = [s['name'] for s in ep_sections]
    cell_widths = [max(len(n) + 2, 5) for n in names]

    pad = '  '
    top = pad + '┌'
    for i, w in enumerate(cell_widths):
        top += '─' * w
        top += '┬' if i < len(cell_widths) - 1 else '┐'

    mid = pad + '│'
    for i, (name, w) in enumerate(zip(names, cell_widths)):
        mid += name.center(w)
        mid += '│'

    bot = pad + '└'
    for i, w in enumerate(cell_widths):
        bot += '─' * w
        bot += '┴' if i < len(cell_widths) - 1 else '┘'

    out.extend([top, mid, bot])
    out.append('')

    # Episode detail
    for ep in episodes:
        icon = EPISODE_ICON.get(ep['status'], '?')
        title = ep['title'] or '(untitled)'
        out.append(f"  {icon} Ep {ep['ep']:02d}: {title}  [{ep['status']}]  {ep['arc']}")

    out.append('')

    # Continuity threads
    if threads:
        thread_icons = {
            'active': '●', 'resolved': '✓',
            'dormant': '○', 'recurring': '↻',
        }
        out.append('  Continuity Threads')
        for t in threads:
            icon = thread_icons.get(t['status'], '?')
            eps = t['episodes'] or '—'
            out.append(f"  {icon} {t['name']}  [{t['status']}]  episodes: {eps}")
        out.append('')

    # Progress
    total = len(episodes)
    done = sum(1 for e in episodes if e['status'] == 'final')
    if total > 0:
        pct = math.floor(done / total * 100)
        filled = math.floor(done / total * FILL_COUNT)
    else:
        pct = 0
        filled = 0
    bar = '█' * filled + '░' * (FILL_COUNT - filled)
    out.append(f'  [{bar}] {pct}%  {done}/{total} episodes complete')

    return '\n'.join(out)


# ── CLI ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print('Usage: pipeline.py <storypad.md>')
        print('       pipeline.py <series.md> --series')
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
