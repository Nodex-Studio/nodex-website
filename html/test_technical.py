"""Static regression checks for the documentation, not the proposed platform."""
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from build import CheckMarkup
from technical_build import SECTIONS, ENDPOINTS

ROOT = Path(__file__).resolve().parent

class Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.json_blocks = []
        self.in_json = False
        self.buffer = ''
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a': self.links.append(attrs.get('href', ''))
        if tag == 'code' and attrs.get('class') == 'language-json':
            self.in_json = True
            self.buffer = ''
    def handle_data(self, value):
        if self.in_json: self.buffer += value
    def handle_endtag(self, tag):
        if tag == 'code' and self.in_json:
            self.json_blocks.append(json.loads(self.buffer))
            self.in_json = False

class TechnicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT/'dist/technical.html').read_text()
        cls.parsed = Extract(); cls.parsed.feed(cls.page)
    def test_markup_and_sections(self):
        check = CheckMarkup(); check.feed(self.page); check.verify()
        self.assertEqual(len(re.findall('<section id=', self.page)), len(SECTIONS))
        self.assertNotIn('http-equiv="refresh"', self.page)
        self.assertNotIn('<!--SWITCHER-->', self.page)
    def test_local_links(self):
        for link in self.parsed.links:
            if link and not link.startswith(('https:', 'http:', '#')):
                self.assertTrue((ROOT/'dist'/link.split('#')[0]).is_file(), link)
    def test_json_examples(self):
        self.assertGreaterEqual(len(self.parsed.json_blocks), 5)
        manifest = self.parsed.json_blocks[0]
        self.assertEqual(manifest['format'], 'iife-register')
        self.assertEqual(manifest['runtimeApiMajor'], 1)
        asset_paths = {item['path'] for item in manifest['assets']}
        self.assertIn(manifest['entry'], asset_paths)
        self.assertTrue(set(manifest['styles']) <= asset_paths)
    def test_contract_download_matches(self):
        self.assertEqual((ROOT/'technical-contracts.ts').read_bytes(), (ROOT/'dist/technical-contracts.ts').read_bytes())
    def test_contracts_and_diagrams(self):
        self.assertEqual(len(ENDPOINTS), 16)
        self.assertEqual(len(set((method,path) for method,path,_ in ENDPOINTS)), 16)
        self.assertEqual(self.page.count('<figure class="diagram">'), 6)
        for label in ['NodexBundleRegistry', 'restoreState', 'release.revoked', 'Idempotency-Key', 'shared page privileges']:
            self.assertIn(label.lower(), self.page.lower())
    def test_end_to_end_workflow(self):
        self.assertIn('href="#workflow"', self.page)
        section = re.search(r'<section id="workflow".*?</section>', self.page, re.S).group()
        steps = re.findall(r'<h3>(\d+)\. ', section)
        self.assertEqual(steps, [str(i) for i in range(1, 13)])
        for phrase in ['reviewer approval', 'NodexRuntime.register', 'not a publication', 'empty canvas']:
            self.assertIn(phrase, section)
        self.assertNotIn('<!--PROMPT_WORKFLOW-->', self.page)
    def test_accessible_svg_graphs(self):
        svgs = re.findall(r'<svg\b.*?</svg>', self.page, re.S)
        self.assertEqual(len(svgs), 16)  # Five static graphs + three scenarios, wide/narrow.
        for source in svgs:
            svg = ET.fromstring(source)
            self.assertEqual(svg.attrib['role'], 'img')
            self.assertEqual(len(svg.attrib['aria-labelledby'].split()), 2)
            ns = {'s': 'http://www.w3.org/2000/svg'}
            self.assertIsNotNone(svg.find('s:title', ns))
            self.assertIsNotNone(svg.find('s:desc', ns))
            self.assertTrue(svg.findall('.//s:path', ns))
            ids = {element.attrib['id'] for element in svg.iter() if 'id' in element.attrib}
            for reference in re.findall(r'url\(#([^)]*)\)', source):
                self.assertIn(reference, ids)
        for scenario in ['success', 'failure', 'stale']:
            self.assertIn(f'data-revision-graph="{scenario}"', self.page)
    def test_pinned_toolchain_explanation(self):
        self.assertIn('id="pinned-toolchain"', self.page)
        self.assertEqual(self.page.count('href="#pinned-toolchain"'), 2)
        for phrase in ['Exact Node.js', 'Configuration hash', 'Pinned does not mean permanently frozen', 'npm ci']:
            self.assertIn(phrase, self.page)

if __name__ == '__main__':
    unittest.main()
