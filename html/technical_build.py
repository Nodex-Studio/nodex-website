"""Generate the native architecture reference; no network or deployment."""
from pathlib import Path
import html
import re
import markdown
from technical_diagrams import topology_svg, workflow_svg, authoring_svg, records_svg, data_svg, switching_graphs

ROOT = Path(__file__).resolve().parent
SECTIONS = [
    ('decisions', 'Architecture decisions'), ('topology', 'System topology'),
    ('workflow', 'Prompt → visible dashboard'),
    ('authoring', 'Agentic authoring'), ('records', 'Source & release records'),
    ('build', 'Build & artifacts'), ('runtime', 'Native runtime'),
    ('delivery', 'Fresh-code delivery'), ('http', 'HTTP contracts'),
    ('events', 'Events & reconnection'), ('data', 'Data & bipp adapter'),
    ('security', 'Security & operations'), ('implementation', 'Implementation plan'),
    ('references', 'Downloads & references'),
]

ENDPOINTS = [
    ('POST', '/projects', 'Editor · {name} → 201 Project; initializes empty source and project ETag.'),
    ('GET', '/projects/{p}', 'Authorized member → 200 Project + ETag; published pointer visible to viewers, draft details to editors.'),
    ('POST', '/projects/{p}/runs', 'Editor · AuthoringRequest + project If-Match → 202 AuthoringRun.'),
    ('GET', '/projects/{p}/runs/{r}', 'Editor → 200 AuthoringRun; includes run ETag.'),
    ('POST', '/projects/{p}/runs/{r}/cancel', 'Editor · {} + run If-Match → 202 AuthoringRun; terminal incompatible states return 409.'),
    ('GET', '/projects/{p}/revisions/{v}', 'Editor → 200 SourceRevision; does not expose an unauthenticated source archive.'),
    ('GET', '/projects/{p}/releases/{r}', 'Editor/reviewer, or viewer for an eligible published release → 200 Release + ETag.'),
    ('POST', '/projects/{p}/releases/{r}/review', 'Reviewer · {decision, reason} + release If-Match → 200 Release.'),
    ('POST', '/projects/{p}/releases/{r}/revoke', 'Reviewer · {reason} + release If-Match → 200 Release; emits release.revoked.'),
    ('POST', '/projects/{p}/publication', 'Publisher · {releaseId, configVersion} + project If-Match → 200 Project; atomic pointer update.'),
    ('GET', '/projects/{p}/configuration', 'Authorized reader · ?releaseId=…&configVersion=… (version optional) → 200 RuntimeConfiguration + ETag; viewers restricted to published pair.'),
    ('PUT', '/projects/{p}/configuration', 'Editor · {releaseId, values} + config If-Match → 200 updated configuration.'),
    ('GET', '/projects/{p}/events', 'Authorized member → 200 text/event-stream; role-filtered updates, resume with Last-Event-ID.'),
    ('GET', '/projects/{p}/releases/{r}/assets/{path}', 'Eligible reader → 200 asset bytes or authenticated 304; 404 for inaccessible/revoked assets.'),
    ('GET', '/projects/{p}/models', 'Editor → 200 permitted model descriptors; normalized adapter metadata.'),
    ('POST', '/projects/{p}/releases/{r}/queries', 'Eligible viewer/editor · QueryRequest → 200 QueryResult; read-only query, CSRF required, no If-Match.'),
]


def node(title, sub, detail):
    return (f'<button class="node" type="button" aria-pressed="false" '
            f'aria-controls="topology-detail" data-detail="{html.escape(detail, quote=True)}">'
            f'{html.escape(title)}<small>{html.escape(sub)}</small></button>')


def topology():
    rows = [
        ('BROWSER · SHARED PAGE PRIVILEGES', [
            ('Studio shell', 'Chat + project controls', 'Owns the user session and authoring UX. It never contains bipp service credentials.'),
            ('Native dashboard host', 'Register / mount / retire', 'Loads approved classic bundles, manages bounded factories and coordinates state transfer. This is not a sandbox.'),
            ('Generated module', 'React root + Nodex SDK', 'Owns its application state and rendering. SDK calls reach the authorized backend; native code shares page privileges.')]),
        ('CONTROL BACKEND · AUTHORIZED OPERATIONS', [
            ('Project & run API', 'Session + ETag checks', 'Creates tenant-scoped runs, stores revisions, and guards concurrent changes.'),
            ('Authoring orchestrator', 'Plan / edit / repair', 'Controls tools, budgets, cancellation, worker leases, and the coding agent.'),
            ('Release service', 'Approval + event stream', 'Checks provenance, records review, and emits release events. A build is not automatically an approved release.')]),
        ('ISOLATED EXECUTION · NO PRODUCTION CREDENTIALS', [
            ('Worker queue', 'Leases + retry', 'At-least-once delivery requires idempotent stage results and cancelled-run checks.'),
            ('Build sandbox', 'Pinned source + toolchain', 'Compiles the exact revision with resource limits and controlled dependency/network access.'),
            ('Browser test worker', 'Render + interaction tests', 'Executes candidate code away from production users using fixtures or scoped read-only data.')]),
        ('DURABLE STORAGE & DATA SERVICES', [
            ('Metadata + source', 'Projects / revisions / audit', 'Separate mutable pointers from immutable source trees and execution evidence.'),
            ('Private artifacts', 'Manifest / JS / CSS', 'The release service persists immutable artifacts; authenticated delivery serves eligible bytes to the host.'),
            ('Gateway → bipp', 'Approved queries + identity', 'Independently authorizes each request, then translates permitted operations through the verified backend adapter.')]),
    ]
    out = ['<figure class="diagram"><figcaption>01 / System connections and ownership</figcaption>', topology_svg(),
           '<details class="diagram-explorer"><summary>Explore component responsibilities</summary>']
    for label, entries in rows:
        out.append(f'<div class="lane"><span class="lane-label">{label}</span><div class="nodes">')
        out.extend(node(*entry) for entry in entries)
        out.append('</div></div>')
    out.append('<div class="diagram-detail" id="topology-detail" aria-live="polite">Select a component to inspect its responsibility. Authoring flows from the shell through the control backend to workers; approved artifacts return to the native host. Runtime queries travel separately to the gateway.</div></details></figure>')
    return ''.join(out)


def svg_figure(caption, graphic, note):
    return f'<figure class="diagram"><figcaption>{html.escape(caption)}</figcaption>{graphic}<p class="caption">{html.escape(note)}</p></figure>'


def build_technical(dist, checker):
    source = ROOT.joinpath('technical.md').read_text()
    chunks = re.split(r'^## (.+)$', source, flags=re.M)
    if (len(chunks)-1)//2 != len(SECTIONS):
        raise ValueError('Technical sections and navigation differ')
    contracts = ROOT.joinpath('technical-contracts.ts').read_text()
    runtime = contracts[contracts.index('export interface SavedState'):contracts.index('/** Server-only adapter')]
    adapter = contracts[contracts.index('/** Server-only adapter'):]
    replacements = {
        '<!--TOPOLOGY-->': topology(),
        '<!--PROMPT_WORKFLOW-->': svg_figure('End-to-end sequence / Prompt → visible dashboard', workflow_svg(), 'Approval and publication are separate gates. The numbered groups correspond to the twelve steps below.'),
        '<!--AUTHORING-->': svg_figure('02 / Authoring and repair', authoring_svg(), 'Dashed arrows show bounded repair or stopping without promotion. Approval follows successful checks.'),
        '<!--RECORDS-->': svg_figure('03 / Durable relationships', records_svg(), 'Source and artifacts are immutable; project pointers are mutable. Viewer state is separate from the application source.'),
        '<!--RUNTIME_CONTRACT-->': '<pre><code class="language-typescript">'+html.escape('export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };\nexport type Id = string;\n'+runtime)+'</code></pre>',
        '<!--ADAPTER_CONTRACT-->': '<pre><code class="language-typescript">'+html.escape(adapter)+'</code></pre>',
        '<!--SWITCHER-->': '<figure class="diagram"><figcaption>04 / Revision switching · explore three outcomes</figcaption><div class="scenario-controls" role="group" aria-label="Revision switching scenario"><button type="button" data-scenario="success" aria-pressed="true" aria-controls="switch-sequence switch-result">Successful revision</button><button type="button" data-scenario="failure" aria-pressed="false" aria-controls="switch-sequence switch-result">Candidate fails</button><button type="button" data-scenario="stale" aria-pressed="false" aria-controls="switch-sequence switch-result">Newer revision wins</button></div><ol class="sequence" id="switch-sequence"><li>Approved release → import → stage → transfer state → activate → dispose previous module.</li></ol><div class="result" id="switch-result" aria-live="polite">Revision 41 stays visible until revision 42 is ready.</div></figure>',
        '<!--DATA_FLOW-->': svg_figure('05 / Runtime interaction — no AI call or rebuild', data_svg(), 'Solid arrows show the request and result. The dashed return represents the next user interaction. Cancel stale requests and ignore stale responses.'),
        '<!--API_TABLE-->': '<table class="api-table"><thead><tr><th>Endpoint · /api/v1 prefix</th><th>Contract</th></tr></thead><tbody>'+''.join(f'<tr><td><span class="method">{method}</span><code>{html.escape(path)}</code></td><td>{html.escape(description)}</td></tr>' for method,path,description in ENDPOINTS)+'</tbody></table>',
    }
    replacements['<!--SWITCHER-->'] = replacements['<!--SWITCHER-->'].replace('<ol class="sequence"', switching_graphs() + '<ol class="sequence"')
    sections, nav = [], []
    for index,(sid,label) in enumerate(SECTIONS):
        title,body = chunks[2*index+1:2*index+3]
        content = markdown.markdown(body, extensions=['fenced_code','tables','md_in_html'])
        for key,value in replacements.items():
            content = content.replace(key,value)
        sections.append(f'<section id="{sid}" aria-labelledby="{sid}-title"><h2 id="{sid}-title"><span class="number">{index+1:02}</span>{html.escape(title)}</h2>{content}</section>')
        nav.append(f'<li><a href="#{sid}"><span>{index+1:02}</span>{html.escape(label)}</a></li>')
    page = ROOT.joinpath('technical-template.html').read_text()
    for key,value in {'<!--NAV-->': ''.join(nav), '<!--CONTENT-->': ''.join(sections), '/*STYLES*/': ROOT.joinpath('technical.css').read_text(), '/*SCRIPT*/': ROOT.joinpath('technical.js').read_text()}.items():
        page = page.replace(key,value)
    page = page.replace('Approved release → import → stage → transfer state → activate → dispose previous module.',
                        'Approved release → register bundle → stage → transfer state → activate → dispose and unregister previous release.')
    check = checker(); check.feed(page); check.verify()
    if re.search(r'<!--(?:NAV|CONTENT|TOPOLOGY|PROMPT_WORKFLOW|AUTHORING|RECORDS|RUNTIME_CONTRACT|SWITCHER|API_TABLE|DATA_FLOW|ADAPTER_CONTRACT)-->',page):
        raise ValueError('Unresolved technical placeholder')
    dist.joinpath('technical.html').write_text(page)
    dist.joinpath('technical-contracts.ts').write_text(contracts)
    print(f'Built native technical reference: {len(SECTIONS)} sections, {len(ENDPOINTS)} API operations, 6 diagrams.')
