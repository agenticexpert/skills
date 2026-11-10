"""A venue: its file in venues/, read for its index.md and series.md templates and the scene its
flow closes on."""

import datetime
import re
from pathlib import Path

from storyfile import TimelineError, cell, put_frontmatter, replace_section, sections

VENUES = Path(__file__).resolve().parent.parent / 'venues'


def venue_text(venue):
    """The venue file's text; empty when the venue has no file."""
    doc = VENUES / f'{venue or "youtube"}.md'
    return doc.read_text(encoding='utf-8') if doc.is_file() else ''


def template(venue, doc, title):
    """The venue's `doc` template (index.md or series.md), dated today, its `# {…}` heading set to
    `title` or left out, its other placeholder lines emptied."""
    m = re.search(rf'^## {re.escape(doc)} template\s*```markdown\n(.*?)^```', venue_text(venue), re.DOTALL | re.MULTILINE)
    if not m:
        known = ', '.join(sorted(p.stem for p in VENUES.glob('*.md')))
        raise TimelineError(f'the venue {venue} has no {doc} template' if venue_text(venue) else
                            f'no venue {venue}; the venues are {known}')
    text = m.group(1).replace('{date}', datetime.date.today().isoformat())
    heading = re.compile(r'^# \{[^}\n]*\}\n+' if not title else r'^# \{[^}\n]*\}$', re.MULTILINE)
    text = heading.sub(lambda _: f'# {title}' if title else '', text, count=1)
    return re.sub(r'^\{[^}\n]*\}$', '', text, flags=re.MULTILINE)


def started(venue, doc, title, premise, fields):
    """A new story's index.md or series' series.md from the venue's template: the premise in its
    frontmatter and `## Premise`, each of `fields` (frontmatter key → value) set when given."""
    text = template(venue, doc, title)
    if cell(premise):
        text = replace_section(put_frontmatter(text, 'premise', f'"{cell(premise)}"'), 'Premise', cell(premise))
    for key, value in fields.items():
        text = put_frontmatter(text, key, f'"{cell(value)}"') if cell(value) else text
    return text


def first_scenes(venue):
    """The venue's starting scenes, in order: each markdown block that opens on a `# <name>` line, as
    (name, the scene file's text)."""
    blocks = re.findall(r'^```markdown\n(# (?!\{)([^\n]+)\n.*?)^```', venue_text(venue), re.DOTALL | re.MULTILINE)
    return [(title.strip(), text) for text, title in blocks]


def closing_scene(venue):
    """The name of the scene the venue's flow ends on (`intro → … → wrapup`), or None."""
    flow = ' '.join(sections(venue_text(venue)).get('scene flow', []))
    m = re.search(r'`([^`]*→[^`]*)`', flow)
    return m.group(1).split('→')[-1].strip() if m else None
