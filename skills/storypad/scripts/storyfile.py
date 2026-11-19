"""The story files' format: frontmatter, the `# Name` line, `## Section` bodies, checklists and
markdown tables read by their header, the one check of a name or value, keys for new files,
and the one writer every file goes through.
"""

import datetime
import os
import re
import shutil
from pathlib import Path

META = re.compile(r'^[a-z][a-z0-9-]*$')
ROW = re.compile(r'^\s*\|')
RULE = re.compile(r'^\s*\|[\s:|-]+\|\s*$')
FM = re.compile(r'\A---[ \t]*\n(.*?)^---[ \t]*$', re.DOTALL | re.MULTILINE)
TOP = re.compile(r'\s*^#[ \t]+(.+?)[ \t]*$', re.MULTILINE)
CHECK = re.compile(r'^\s*-\s*\[([ xX])\]\s*(.*)')
FIXED = ('status', 'updated', 'removed', 'type', 'series', 'when')


class TimelineError(ValueError):
    pass


def name(text):
    """A name or value as storypad keeps it: trimmed, on one line, without |, never empty."""
    text = (text or '').strip()
    if not text:
        raise TimelineError('a name or value is empty; give it words')
    if any(c in text for c in '|\n\r'):
        raise TimelineError(f'{text!r} has a | or a line break; names and values stay on one line, without |')
    return text


def cell(text):
    """Free text for a table cell or a frontmatter value; empty is allowed."""
    return name(text) if (text or '').strip() else ''


def same(a, b):
    """Whether two names are one: compared trimmed and case-folded."""
    return (a or '').strip().casefold() == (b or '').strip().casefold()


def meta_pairs(pairs, known):
    """`key=value` meta fields, all checked before any is used: a lowercase word that isn't a field
    storypad keeps, and a value; `key=` empties one."""
    out = []
    for pair in pairs or []:
        key, eq, value = (part.strip() for part in pair.partition('='))
        if not eq or not META.match(key) or key in known:
            raise TimelineError(f'not a meta field: {pair!r}; use key=value with a lowercase word for the key'
                                + (f'; {key} has a flag of its own' if key in known else ''))
        out.append((key, cell(value)))
    return out


def cells(line):
    line = line.strip()
    line = line[1:-1] if len(line) > 1 and line.endswith('|') else line[1:]
    return [c.strip() for c in line.split('|')]


def table(lines, columns):
    """A markdown table read by its header → (header, rows), each row a dict by lowercased column
    name. A column storypad doesn't know is kept with its values; a known one missing is added
    after the known column before it."""
    found = [cells(line) for line in lines or [] if ROW.match(line) and not RULE.match(line)]
    if not found:
        return list(columns), []
    head = found[0]
    keys = [h.lower() for h in head]
    if len(set(keys)) < len(keys):
        raise TimelineError(f"a table names a column twice: | {' | '.join(head)} |")
    long = next((r for r in found[1:] if len(r) > len(head)), None)
    if long:
        raise TimelineError(f"a row has more cells than its table has columns: | {' | '.join(long)} |")
    rows = [dict(zip(keys, r)) for r in found[1:]]
    for i, c in enumerate(columns):
        if c.lower() not in keys:
            at = keys.index(columns[i - 1].lower()) + 1 if i else 0
            head.insert(at, c)
            keys.insert(at, c.lower())
    return head, [{k: r.get(k, '') for k in keys} for r in rows]


def table_text(head, rows, known):
    """The table: `head`, then a column for each field a row adds. A column storypad doesn't know
    is left out once no row has a value in it. Every cell is checked before it is written."""
    known = {k.lower() for k in known}
    keys = [h.lower() for h in head]
    extra = [k for k in dict.fromkeys(k for r in rows for k in r) if k not in keys]
    cols = [(h, k) for h, k in zip(head + extra, keys + extra) if k in known or any(r.get(k) for r in rows)]
    return '\n'.join(['| ' + ' | '.join(h for h, _ in cols) + ' |',
                      '|' + '|'.join('-' * (len(h) + 2) for h, _ in cols) + '|']
                     + ['| ' + ' | '.join(cell(r.get(k, '')) for _, k in cols) + ' |' for r in rows])


def frontmatter(text):
    m = FM.match(text)
    fm = {}
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fm


def put_frontmatter(text, key, value):
    """Set a frontmatter key, adding it (and the frontmatter) when missing; None removes it, and the
    frontmatter with its last key."""
    m = FM.match(text)
    lines = m.group(1).splitlines() if m else []
    at = next((i for i, line in enumerate(lines) if line.split(':', 1)[0] == key and ':' in line), None)
    if value is None:
        if at is None:
            return text
        del lines[at]
        if not lines:
            return text[m.end():].lstrip('\n')
    elif at is None:
        lines.append(f'{key}: {value}')
    else:
        lines[at] = f'{key}: {value}'
    block = ''.join(f'{line}\n' for line in lines)
    return text[:m.start(1)] + block + text[m.end(1):] if m else f'---\n{block}---\n\n{text}'


def top(text):
    """The `# Name` line right after any frontmatter, or None."""
    m = FM.match(text)
    return TOP.match(text, m.end() if m else 0)


def named(text, name):
    """`text` with the `# Name` line after its frontmatter set to `name`; empty removes the line."""
    h = top(text)
    if h:
        start = text.rfind('\n', 0, h.start(1)) + 1
        if name:
            return text[:start] + f'# {name}' + text[h.end():]
        return text[:start] + re.sub(r'^\n\n?', '', text[h.end():])
    if not name:
        return text
    m = FM.match(text)
    at = m.end() if m else 0
    return text[:at] + ('\n\n' if m else '') + f'# {name}\n\n' + text[at:].lstrip('\n')


def sections(text):
    """`## Heading` → its body lines, lowercased heading."""
    out, current = {}, None
    for line in text.splitlines():
        h = re.match(r'^##\s+(.+?)\s*$', line)
        if h:
            current = h.group(1).lower()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


def checks(lines):
    return [{'done': m.group(1) != ' ', 'text': m.group(2).strip()}
            for m in map(CHECK.match, lines or []) if m]


def listing(lines, columns, key, present):
    """A table that orders a folder's items, read by its header → (header, the items in order, each
    listed item's row, the rows naming nothing there or one listed above as (index, row), the
    unlisted items, which come last)."""
    head, rows = table(lines, columns)
    order, found, odd = [], {}, []
    for i, r in enumerate(rows):
        if r[key] in present and r[key] not in found:
            found[r[key]] = r
            order.append(r[key])
        else:
            odd.append((i, r))
    unlisted = sorted(set(present) - set(found))
    return head, order + unlisted, found, odd, unlisted


def listing_problems(table_name, doc, key, present, where):
    """Each item missing from its table, and each row naming nothing there or one listed above."""
    out = [f"{where}{n} isn't in the {table_name} table; it shows last" for n in doc['unlisted']]
    return out + [f"{table_name} table row {i + 1}: " + (f'{r[key]} is listed twice' if r[key] in present else
                                                       f'there is no {where}{r[key]}' if r[key] else f'no {key}')
                  for i, r in doc['odd']]


def save(path, data):
    """Write text, bytes, a copy of a file, or what `data(tmp)` writes, to a temp sibling of `path`
    with its suffix, then move it into place; returns what `data(tmp)` returned."""
    tmp = path.with_name(f'.{path.stem}.tmp{path.suffix}')
    try:
        out = None
        if callable(data):
            out = data(tmp)
        elif isinstance(data, Path):
            shutil.copyfile(data, tmp)
        elif isinstance(data, bytes):
            tmp.write_bytes(data)
        else:
            tmp.write_text(data, encoding='utf-8')
        os.replace(tmp, path)
        return out
    finally:
        if tmp.exists():
            tmp.unlink()


def dated(old_text, text):
    """`text`, its `updated:` set to today when it differs from `old_text`."""
    if text != old_text and 'updated' in frontmatter(text):
        return put_frontmatter(text, 'updated', datetime.date.today().isoformat())
    return text


def replace_section(text, heading, body, before=None):
    """Set a section's body; None removes it. A new section goes above `## <before>` when present."""
    pattern = re.compile(rf'(^## {re.escape(heading)}[ \t]*\n)(.*?)(?=^## |\Z)', re.MULTILINE | re.DOTALL)
    if body is None:
        return pattern.sub('', text, count=1)
    if pattern.search(text):
        return pattern.sub(lambda m: m.group(1) + '\n' + body + ('\n' if m.end() == len(text) else '\n\n'), text, count=1)
    anchor = before and re.search(rf'^## {re.escape(before)}[ \t]*$', text, re.MULTILINE)
    if anchor:
        return text[:anchor.start()] + f'## {heading}\n\n{body}\n\n' + text[anchor.start():]
    return text.rstrip() + f'\n\n## {heading}\n\n{body}\n'


def put_sections(text, order, bodies):
    """Set each section of `bodies`, a new one going above the first of the sections after it in `order` the
    text holds."""
    for i, heading in enumerate(order):
        if heading in bodies:
            text = replace_section(text, heading, bodies[heading], before=next(
                (h for h in order[i + 1:] if re.search(rf'^## {h}[ \t]*$', text, re.MULTILINE)), None))
    return text


def listed(head, rows, odd, columns):
    """The table of `rows`, each row of `odd` back at its index."""
    rows = list(rows)
    for i, r in odd:
        rows.insert(min(i, len(rows)), r)
    return table_text(head, rows, columns)


def unique(base, taken):
    """`base`, or the first of `base-2`, `base-3` … that `taken` doesn't claim."""
    key, n = base, 1
    while taken(key):
        n += 1
        key = f'{base}-{n}'
    return key


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
