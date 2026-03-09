#!/usr/bin/env python3
"""
Compile section scripts from a storypad.md into a clean script.md.

Reads all sections in narrative order, extracts their script: blocks,
and writes a linear script ready for voice recording, read-through,
or handing off to a voice AI.

Usage:
    python compile.py <storypad.md>
    python compile.py <storypad.md> --output <script.md>
    python compile.py <storypad.md> --stdout
"""

import re
import sys
from pathlib import Path


# ── Parsing ────────────────────────────────────────────────────────

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
    """Parse sections, extracting beats, prep, and script blocks."""
    sections_match = re.search(r'^## Sections\s*\n(.*?)(?=\n## |\Z)', text,
                               re.MULTILINE | re.DOTALL)
    if not sections_match:
        return []

    body = sections_match.group(1)
    sections = []
    current = None
    in_prep = False
    in_script = False

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


# ── Compile ────────────────────────────────────────────────────────

def compile_script(storypad_path, output_path=None, stdout=False):
    text = Path(storypad_path).read_text(encoding='utf-8')
    fm = parse_frontmatter(text)
    sections = parse_sections(text)

    title = fm.get('premise', '') or Path(storypad_path).stem
    venue = fm.get('venue', 'youtube')
    created = fm.get('created', '')

    out_lines = []

    # Header
    out_lines.append(f'# {title}')
    out_lines.append('')
    if created:
        out_lines.append(f'venue: {venue}  |  compiled from: {Path(storypad_path).name}')
        out_lines.append('')
    out_lines.append('---')
    out_lines.append('')

    sections_with_script = 0
    sections_missing_script = []

    for sec in sections:
        script_lines = [l for l in sec['script'] if l.strip() or l == '']
        # Trim leading/trailing blank lines
        while script_lines and not script_lines[0].strip():
            script_lines.pop(0)
        while script_lines and not script_lines[-1].strip():
            script_lines.pop()

        out_lines.append(f'## {sec["name"]}')
        out_lines.append('')

        if script_lines:
            sections_with_script += 1
            # Dedent: remove common leading whitespace
            min_indent = min(
                (len(l) - len(l.lstrip()) for l in script_lines if l.strip()),
                default=0,
            )
            for l in script_lines:
                out_lines.append(l[min_indent:] if len(l) > min_indent else l)
            out_lines.append('')
        else:
            sections_missing_script.append(sec['name'])
            out_lines.append('[ no script yet ]')
            out_lines.append('')

        out_lines.append('---')
        out_lines.append('')

    compiled = '\n'.join(out_lines)

    if stdout:
        print(compiled)
    else:
        if output_path is None:
            storypad_dir = Path(storypad_path).parent
            output_path = storypad_dir / 'script.md'
        Path(output_path).write_text(compiled, encoding='utf-8')
        print(f'Script compiled → {output_path}')
        print(f'  Sections with script: {sections_with_script}/{len(sections)}')
        if sections_missing_script:
            print(f'  Missing script: {", ".join(sections_missing_script)}')


# ── CLI ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print('Usage: compile.py <storypad.md>')
        print('       compile.py <storypad.md> --output <script.md>')
        print('       compile.py <storypad.md> --stdout')
        sys.exit(1)

    storypad_path = sys.argv[1]
    output_path = None
    stdout = '--stdout' in sys.argv

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    compile_script(storypad_path, output_path=output_path, stdout=stdout)


if __name__ == '__main__':
    main()
