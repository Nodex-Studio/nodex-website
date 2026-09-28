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
from technical_build import build_technical

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / '00-executive-summary.md'
DIST = ROOT / 'dist'

SECTIONS = [
    ('product', 'The product'),
    ('bipp', 'The bipp foundation'),
    ('experience', 'The experience'),
    ('flexibility', 'Dashboard flexibility'),
    ('architecture', 'Architecture'),
    ('source', 'Source & storage'),
    ('updates', 'Incremental updates'),
    ('interactions', 'Graphs & widgets'),
    ('delivery', 'Embedding & deployment'),
    ('trust', 'Trustworthy results'),
    ('proof', 'The first proof'),
    ('evidence', 'Evidence & limits'),
]

LAYERS = [
    ('studio', 'Chat → versioned application source', 'Authoring · durable Nodex project storage',
     'An orchestrator and coding agent inspect source and permitted model context, plan targeted edits, and repair from test diagnostics within limits. Trusted services check and approve releases. Source revisions—not chat alone—record the application.', True),
    ('build', 'Isolated backend build', 'Pinned dependencies · compile · test',
     'A temporary worker builds a source revision and checks rendering, interactions, and data access. Generated code runs outside the main Nodex server. Failed builds leave the working dashboard available.', True),
    ('assets', 'Versioned application artifacts', 'Disposable IIFE bundle + CSS + assets + manifest',
     'Successful builds enter durable artifact storage. Load approved classic script bundles rather than a new native ES-module import per revision. Revision-specific dependencies stay inside the bundle; shared runtime dependencies stay pinned. History remains on the backend.', True),
    ('runtime', 'Native dashboard host', 'Register · mount in DOM · update · dispose · unregister',
     'The persistent host creates an instance from the registered factory, transfers compatible state, and switches when ready. Retired factories, instances, and side effects are released so they can be garbage-collected; collection is not guaranteed or immediate. Shared-page privileges remain.', True),
    ('data', 'Authorized data gateway', 'Server-side permissions · approved operations',
     'Applications call the Nodex SDK directly; it invokes the backend gateway. Every operation is authorized server-side. Service credentials stay on the backend. The SDK is an integration contract, not a browser security boundary.', True),
    ('analytics', 'bipp analytics', 'Approved models → queries → customer data',
     'Reuse bipp’s business definitions, query generation, and access controls where supported interfaces permit. Rendering a metric differently does not change its shared definition. API availability still needs verification.', False),
    ('services', 'Approved external services', 'Connector-backed data and actions',
     'Additional APIs can support specialized graphs or widgets. New server logic, jobs, and write operations require separately authorized backend capabilities; generated frontend code alone does not provide them.', False),
]


def architecture():
    parts = ['<div class="architecture" aria-label="Proposed studio architecture">',
             '<p class="architecture-label">Select a layer to explore its role.</p>',
             '<div class="architecture-map">']
    for i, (key, title, subtitle, detail, full) in enumerate(LAYERS):
        connectors = {
            1: '↓ Build the requested source revision',
            2: '↓ Store successful build outputs',
            3: '↓ Notify studio · load bundle · register factory · mount',
            4: '↕ Direct SDK calls and authorized results — no rebuild',
            5: '↕ Invoke supported analytics or service operations',
        }
        if i in connectors:
            parts.append(f'<div class="architecture-connector">{connectors[i]}</div>')
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
    # Fresh native reference; historical numbered specifications remain excluded.
    build_technical(DIST, CheckMarkup)
    DIST.joinpath('CNAME').write_text('nodex.studio\n', encoding='utf-8')
    DIST.joinpath('.nojekyll').touch()
    if args.preview:
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        args.preview.write_text(fragment, encoding='utf-8')
    print(f'Built studio proposal: {len(SECTIONS)} sections, approximately {word_count:,} words. No deployment performed.')


if __name__ == '__main__':
    main()
