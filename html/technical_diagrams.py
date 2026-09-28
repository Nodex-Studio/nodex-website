"""Accessible, theme-aware SVG diagrams for the native architecture reference."""
import html


class Graph:
    def __init__(self, key, width, height, title, description):
        self.key = key
        self.width = width
        self.height = height
        self.parts = [f'<svg class="architecture-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{key}-title {key}-desc">',
                      f'<title id="{key}-title">{html.escape(title)}</title>',
                      f'<desc id="{key}-desc">{html.escape(description)}</desc>',
                      f'<defs><marker id="{key}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="svg-arrowhead"/></marker></defs>']

    def text(self, x, y, lines, css='svg-label', anchor='middle'):
        if isinstance(lines, str):
            lines = [lines]
        for index, line in enumerate(lines):
            self.parts.append(f'<text x="{x}" y="{y + index * 18}" text-anchor="{anchor}" class="{css}">{html.escape(line)}</text>')

    def box(self, x, y, width, title, subtitle='', height=72, accent=False, href=None):
        if href:
            self.parts.append(f'<a href="{html.escape(href, quote=True)}" aria-label="{html.escape(title + ": " + subtitle + " — read explanation", quote=True)}">')
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" class="svg-node{" svg-active" if accent else ""}"/>')
        self.text(x + width/2, y+29, title, 'svg-title')
        if subtitle:
            self.text(x+width/2, y+50, subtitle, 'svg-subtitle')
        if href:
            self.parts.append('</a>')

    def edge(self, points, label=None, lx=None, ly=None, dashed=False, both=False):
        d = 'M ' + ' L '.join(f'{x} {y}' for x,y in points)
        start = f' marker-start="url(#{self.key}-arrow)"' if both else ''
        self.parts.append(f'<path d="{d}" class="svg-edge{" svg-dashed" if dashed else ""}" marker-end="url(#{self.key}-arrow)"{start}/>')
        if label:
            self.text(lx, ly, label, 'svg-edge-label')

    def finish(self):
        return ''.join(self.parts) + '</svg>'


def vertical(key, title, description, entries, labels=None, feedback=None, links=None):
    height = len(entries)*118 + 24
    graph = Graph(key, 340, height, title, description)
    width = 254 if feedback else 300
    for i, (name, sub) in enumerate(entries):
        y = 14+i*118
        graph.box(20, y, width, name, sub, accent=i == len(entries)-1, href=(links or {}).get(name))
        if i < len(entries)-1:
            graph.edge([(20+width/2,y+72),(20+width/2,y+118)],
                       labels[i] if labels else None, 20+width/2+64, y+100)
    if feedback:
        begin,end,label = feedback
        a,b=14+begin*118+36,14+end*118+36
        graph.edge([(274,a),(318,a),(318,b),(274,b)], dashed=True)
        graph.text(308, (a+b)/2, label, 'svg-subtitle', 'end')
    return graph.finish()


def pair(desktop, mobile):
    return f'<div class="svg-wide">{desktop}</div><div class="svg-narrow">{mobile}</div>'


def topology_svg():
    desc = 'Studio requests reach the control API and isolated build workers. Approved bundles flow from private artifacts to the native host. Runtime requests pass through the gateway to bipp. The host and dashboard share browser privileges.'
    g = Graph('system-wide',760,636,'Native system connections',desc)
    g.text(40,24,'AUTHORING', 'svg-kicker','start')
    g.text(430,24,'DELIVERY & EXECUTION', 'svg-kicker','start')
    g.box(40,44,280,'Studio chat','Prompt + base revision')
    g.box(430,44,280,'Persistent native host','DOM canvas + runtime SDK',accent=True)
    g.box(40,204,280,'Control API + orchestrator','Identity · runs · approval')
    g.box(430,204,280,'Registered dashboard factory','Create → mount → dispose')
    g.box(40,364,280,'Isolated build + test workers','Pinned source · bounded repair')
    g.box(430,364,280,'Private release artifacts','Approved IIFE bundle + CSS')
    g.edge([(180,116),(180,204)],'authoring request',180,165)
    g.edge([(180,276),(180,364)],'queue / worker lease',180,325)
    g.edge([(320,400),(430,400)],'persist',375,386)
    g.edge([(570,364),(570,276)],'load script',570,325)
    g.edge([(570,204),(570,116)],'register + mount',570,165)
    g.edge([(320,240),(375,240),(375,80),(430,80)],None,dashed=True)
    g.text(375,192,'release event','svg-edge-label')
    g.box(430,536,280,'Authorized gateway','Named operation + current identity')
    g.box(40,536,280,'bipp / approved services','Backend analytics only')
    g.edge([(710,80),(742,80),(742,572),(710,572)])
    g.edge([(430,572),(320,572)],'query / result',375,555,both=True)
    g.text(570,488,'Runtime calls bypass the agent','svg-subtitle')
    g.text(40,488,'Dashed: approved-release notification','svg-subtitle','start')
    mobile=vertical('system-narrow','Native system connections',desc,[
        ('Studio chat','Prompt + base revision'),('Control + orchestrator','Authorize · plan · queue'),
        ('Build + tests','Isolated execution'),('Approved release','Persist bundle + notify host'),
        ('Native dashboard host','Register → mount in studio DOM'),('Gateway → bipp','Authorized runtime queries')])
    return pair(g.finish(),mobile)


def workflow_svg():
    desc='A prompt passes through planning, code generation, build and repair, reviewer approval, script registration, mounting, initial queries and activation. The old dashboard remains visible until the candidate is ready.'
    g=Graph('workflow-wide',760,554,'Prompt to visible dashboard',desc)
    entries=[('1–3 · Request & plan','Studio → API → agent'),('4–6 · Edit, build & test','Candidate source + evidence'),('7 · Reviewer approval','Exact release; no self-approval'),('8–9 · Deliver & register','Event → manifest → classic script'),('10–11 · Mount & query','DOM staging → SDK → gateway'),('12 · Activate & retire','Restore state; dispose old view')]
    for i,(title,sub) in enumerate(entries):
        col=i%2; row=i//2
        g.box(30+col*390,30+row*178,310,title,sub,accent=i==5)
    g.edge([(340,66),(420,66)])
    g.edge([(575,102),(575,152),(185,152),(185,208)],'checks passed',380,140)
    g.edge([(340,244),(420,244)],'approve',380,230)
    g.edge([(575,280),(575,330),(185,330),(185,386)],'approved bytes',380,318)
    g.edge([(340,422),(420,422)])
    g.text(380,510,'Existing dashboard stays visible until the candidate is ready.','svg-subtitle')
    return pair(g.finish(),vertical('workflow-narrow','Prompt to visible dashboard',desc,entries))


def authoring_svg():
    desc='Plan, edit, build, test, then review. Failed tests return to editing within a bounded repair budget. Exhausted retries, cancellation, and conflicts stop promotion.'
    g=Graph('authoring-wide',760,408,'Agentic repair loop',desc)
    entries=[('Plan','Permitted context'),('Edit','Candidate workspace'),('Build','Pinned toolchain'),('Test','Rendering + behavior')]
    for i,(title,sub) in enumerate(entries):
        x=16+i*188
        g.box(x,38,164,title,sub,href='#pinned-toolchain' if title == 'Build' else None)
        if i<3:g.edge([(x+164,74),(x+188,74)])
    g.edge([(662,110),(662,174),(286,174),(286,110)],'failure → bounded repair',470,161,dashed=True)
    g.box(390,266,338,'Reviewer approves release','Persist exact source + build evidence',accent=True)
    g.edge([(704,110),(742,110),(742,302),(728,302)],'pass',720,224)
    g.box(16,266,294,'Stop without promotion','Budget exhausted · cancelled · conflict')
    g.edge([(286,174),(163,174),(163,266)],'cannot continue',154,225,dashed=True)
    return pair(g.finish(),vertical('authoring-narrow','Agentic repair loop',desc,entries+[('Review','Approve exact build')],feedback=(3,1,'repair'),links={'Build':'#pinned-toolchain'}))


def records_svg():
    desc='Project pointers identify the current source revision and published release. A revision produces builds; a build produces a release, whose manifest identifies immutable assets. Publication pins a release and configuration version. Viewer state is separate.'
    g=Graph('records-wide',760,624,'Source and release relationships',desc)
    g.box(210,20,340,'Project','Mutable draft / publication pointers',accent=True)
    g.box(30,164,300,'Source revision','Immutable tree + parent + lockfile')
    g.box(430,164,300,'Published pair','Release ID + configuration version')
    g.edge([(300,92),(300,126),(180,126),(180,164)],'draft pointer',166,117)
    g.edge([(460,92),(460,126),(580,126),(580,164)],'published pointer',594,117)
    g.box(30,316,300,'Build','Toolchain + diagnostics + evidence')
    g.box(430,316,300,'Release','Approval status + immutable manifest')
    g.edge([(180,236),(180,316)],'one revision → many builds',180,279)
    g.edge([(330,352),(430,352)],'packages',380,339)
    g.edge([(580,236),(580,316)],'pins',580,279)
    g.box(430,492,300,'Immutable artifacts','Bundle · CSS · static assets')
    g.edge([(580,388),(580,492)],'manifest resolves',580,443)
    g.box(30,492,300,'User-scoped viewer state','Selections; not source or credentials')
    g.text(380,604,'Publication moves pointers; it never overwrites source or artifact history.','svg-subtitle')
    mobile=vertical('records-narrow','Source and release relationships',desc,[
        ('Project draft pointer','Selects a source revision'),('Source → build','One revision may have many builds'),
        ('Release','Exact build + approval status'),('Published pair','Release + configuration version'),
        ('Manifest → artifacts','Immutable bundle, CSS and assets')])
    return pair(g.finish(),mobile)


def data_svg():
    desc='Double-clicking a supplier invokes the SDK, then the authorized gateway and bipp adapter. Normalized results return to application state, expanding the graph without an AI call or rebuild.'
    g=Graph('data-wide',760,384,'Runtime query and render loop',desc)
    entries=[('Double-click','Selected supplier'),('Nodex SDK','Named operation'),('Gateway','Identity + permissions'),('bipp adapter','Supported analytics')]
    for i,(title,sub) in enumerate(entries):
        x=16+i*188
        g.box(x,38,164,title,sub)
        if i<3:g.edge([(x+164,74),(x+188,74)])
    g.box(180,244,400,'Update graph state → rerender','No agent call · no source edit · no build',accent=True)
    g.edge([(662,110),(662,280),(580,280)],'normalized results',639,185)
    g.edge([(180,280),(98,280),(98,110)],'next interaction',104,185,dashed=True)
    return pair(g.finish(),vertical('data-narrow','Runtime query and render loop',desc,entries+[('Rerender graph','No AI call or rebuild')]))


def revision_svg(scenario):
    choices={
        'success': [('Revision 41 visible','Keep the working dashboard'),('Stage revision 42','Register, mount, restore state'),('42 reports ready','Desired release still matches'),('Activate 42','Dispose 41; release unused factory')],
        'failure': [('Revision 41 visible','Keep the working dashboard'),('Stage revision 42','Required view fails to render'),('Readiness rejects','Dispose failed candidate'),('Keep revision 41','Resume input; report diagnostics')],
        'stale': [('Revision 42 loading','Desired token = 7'),('Revision 43 requested','Desired token advances to 8'),('Revision 43 ready','Activate the current candidate'),('42 completes late','Token mismatch → dispose; keep 43')],
    }
    entries=choices[scenario]
    desc='Revision switch outcome: '+'. '.join(title+': '+sub for title,sub in entries)+'.'
    g=Graph(f'switch-{scenario}-wide',760,180,'Revision switching: '+scenario,desc)
    for i,(title,sub) in enumerate(entries):
        x=10+i*190
        g.box(x,30,170,title,'',accent=i==3)
        # Long descriptions are outside the nodes and wrapped explicitly.
        words=sub.split(); cut=max(1,len(words)//2)
        g.text(x+85,124,[' '.join(words[:cut]),' '.join(words[cut:])],'svg-subtitle')
        if i<3:g.edge([(x+170,66),(x+190,66)])
    return pair(g.finish(),vertical(f'switch-{scenario}-narrow','Revision switching: '+scenario,desc,entries))


def switching_graphs():
    return ''.join(f'<div data-revision-graph="{key}"'+('' if key=='success' else ' hidden')+'>'+revision_svg(key)+'</div>' for key in ('success','failure','stale'))
