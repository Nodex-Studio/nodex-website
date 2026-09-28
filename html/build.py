#!/usr/bin/env python3
"""Build one fresh studio proposal; legacy specifications are not inputs.

The same fragment renders locally and in the built-in visualization preview.
No network access or deployment is performed.
"""
import argparse
import html
from html.parser import HTMLParser
from pathlib import Path
import re

import markdown

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '00-executive-summary.md'
DIST = ROOT / 'dist'

SECTIONS = [
    ('product', 'The product'),
    ('bipp', 'The bipp foundation'),
    ('experience', 'The experience'),
    ('flexibility', 'Dashboard flexibility'),
    ('architecture', 'Architecture'),
    ('delivery', 'Embedding & deployment'),
    ('trust', 'Trustworthy results'),
    ('proof', 'The first proof'),
    ('evidence', 'Evidence & limits'),
]

LAYERS = [
    ('studio', 'Nodex Studio', 'Chat + dashboard canvas · embedded or independent',
     'The proposed customer experience: describe a business need, inspect the result, refine it through conversation or direct editing, and save a useful dashboard.', True),
    ('ai', 'Conversation & planning', 'Understand intent · propose changes',
     'Uses permitted bipp model context and the current dashboard. Clarifies business meaning and plans edits; it cannot grant access or silently redefine a shared metric.', False),
    ('state', 'Shared dashboard state', 'Inspect · edit · save · recover',
     'Chat and visual editing need the same saved representation. Inspect bipp’s existing report and dashboard definitions before introducing another format.', False),
    ('integration', 'Nodex–bipp integration', 'Validate changes · invoke supported operations',
     'Proposed integration services apply authorized dashboard changes through supported bipp interfaces. API availability, embedding of authoring, and extension boundaries require verification.', True),
    ('data', 'bipp analytics', 'Models · generated queries · dashboards',
     'Reuse business definitions, query generation, permission enforcement, and existing visualizations where interfaces permit. Extend rendering only for demonstrated gaps, including snapshot compatibility.', False),
    ('distribution', 'bipp delivery', 'Filtered schedules · PDF/JPG · recipients',
     'The demonstration shows scheduled, filtered dashboard snapshots and email delivery. Nodex can connect to these capabilities after authoring is proven; it must resolve recipients, access, timing, and output support.', False),
    ('platform', 'Customer databases', 'Business data queried through bipp',
     'The demonstrated in-database approach executes queries against the underlying data source. This does not imply zero data transfer or guarantee a particular query latency.', True),
]


def architecture():
    parts = ['<div class="architecture" aria-label="Proposed studio architecture">',
             '<p class="architecture-label">Select a layer to explore its role.</p>',
             '<div class="architecture-map">']
    for i, (key, title, subtitle, detail, full) in enumerate(LAYERS):
        if i == 1:
            parts.append('<div class="architecture-connector">↓ Requests and direct edits</div>')
        if i == 3:
            parts.append('<div class="architecture-connector">↓ Proposed dashboard changes</div>')
        if i == 4:
            parts.append('<div class="architecture-connector">↓ Authorized analytics and delivery operations</div>')
        if i == 6:
            parts.append('<div class="architecture-connector">bipp analytics ↔ database queries and results</div>')
        parts.append(
            f'<button type="button" class="architecture-node{" full" if full else ""}" '
            f'data-layer="{key}" data-detail="{html.escape(detail, quote=True)}" '
            f'aria-pressed="{"true" if i == 0 else "false"}" aria-controls="architecture-detail">'
            f'<span>{html.escape(title)}</span><small>{html.escape(subtitle)}</small></button>'
        )
    parts.extend(['</div>', '<div class="architecture-detail" id="architecture-detail" aria-live="polite">',
                  f'<h3 data-layer-title>{LAYERS[0][1]}</h3>',
                  f'<p data-layer-description>{LAYERS[0][3]}</p>', '</div></div>'])
    return '\n'.join(parts)


class CheckMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.anchors = []
        self.controls = []
        self.words = []
        self.ignore_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.ignore_depth += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                raise ValueError(f'Duplicate id: {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag == 'a':
            self.anchors.append(attrs.get('href', ''))
        if 'aria-controls' in attrs:
            self.controls.extend(attrs['aria-controls'].split())

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.ignore_depth -= 1

    def handle_data(self, data):
        if not self.ignore_depth:
            self.words.extend(data.split())

    def verify(self):
        for href in self.anchors:
            if href.startswith('#') and href[1:] not in self.ids:
                raise ValueError(f'Broken anchor: {href}')
        for target in self.controls:
            if target not in self.ids:
                raise ValueError(f'Broken control target: {target}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', type=Path, help='Also write the visualization fragment to this path')
    args = parser.parse_args()
    raw = SOURCE.read_text(encoding='utf-8')
    chunks = re.split(r'^## (.+)$', raw, flags=re.M)
    if (len(chunks) - 1) // 2 != len(SECTIONS):
        raise ValueError('Document headings do not match navigation')
    sections, navigation = [], []
    for index, (sid, label) in enumerate(SECTIONS):
        title, body = chunks[2 * index + 1:2 * index + 3]
        content = markdown.markdown(body.strip(), extensions=['md_in_html'])
        content = content.replace('<!--ARCHITECTURE-->', architecture())
        number = f'{index + 1:02}'
        sections.append(
            f'<section class="document-section" id="{sid}" aria-labelledby="{sid}-title">'
            f'<div class="section-heading"><span class="section-number" aria-hidden="true">{number}</span>'
            f'<h2 id="{sid}-title">{html.escape(title)}</h2></div>{content}</section>'
        )
        navigation.append(
            f'<li><a href="#{sid}"' + (' aria-current="location"' if index == 0 else '') +
            f'><span aria-hidden="true">{number}</span>{html.escape(label)}</a></li>'
        )
    content_check = CheckMarkup()
    content_check.feed('\n'.join(sections))
    word_count = len(content_check.words) + len(chunks[0].split())
    fragment = ROOT.joinpath('template.html').read_text(encoding='utf-8')
    for key, value in {
        '<!--NAV-->': '<ol>' + '\n'.join(navigation) + '</ol>',
        '<!--SECTIONS-->': '\n'.join(sections),
        '<!--WORD_COUNT-->': f'{word_count:,}',
        '<!--READ_TIME-->': str(max(1, round(word_count / 220))),
        '/*STYLES*/': ROOT.joinpath('styles.css').read_text(encoding='utf-8'),
        '/*SCRIPT*/': ROOT.joinpath('app.js').read_text(encoding='utf-8'),
    }.items():
        fragment = fragment.replace(key, value)
    check = CheckMarkup()
    check.feed(fragment)
    check.verify()
    if re.search(r'<!--(?:NAV|SECTIONS|ARCHITECTURE|WORD_COUNT|READ_TIME)-->', fragment):
        raise ValueError('Unresolved build placeholder')
    if re.search(r'<(?:html|head|body)\b|<!doctype', fragment, re.I):
        raise ValueError('Preview must be a fragment')
    if len(fragment.encode('utf-8')) >= 1_000_000:
        raise ValueError('Preview exceeds visualization size limit')
    document = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="color-scheme" content="light dark">'
        '<title>Nodex Studio — Build dashboards through conversation</title>'
        '<meta name="description" content="Nodex is a proposed conversational dashboard studio built on bipp’s modeling, analytics, and delivery foundation. Embed the studio or deploy it independently.">'
        '<style>html,body{margin:0;padding:0;color-scheme:light dark}</style>'
        '</head><body>' + fragment + '</body></html>\n'
    )
    DIST.mkdir(exist_ok=True)
    DIST.joinpath('index.html').write_text(document, encoding='utf-8')
    # The compatibility route contains none of the superseded architecture.
    DIST.joinpath('technical.html').write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=index.html">'
        '<title>Studio proposal</title></head><body>'
        '<a href="index.html">Read the current studio proposal</a></body></html>\n', encoding='utf-8')
    DIST.joinpath('CNAME').write_text('nodex.studio\n', encoding='utf-8')
    DIST.joinpath('.nojekyll').touch()
    if args.preview:
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        args.preview.write_text(fragment, encoding='utf-8')
    print(f'Built studio proposal: {len(SECTIONS)} sections, approximately {word_count:,} words. No deployment performed.')


if __name__ == '__main__':
    main()
