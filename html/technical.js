(() => {
  const scenarios = {
    success: {
      label: 'Successful revision',
      steps: [
        ['Release 42 approved', 'Server persists the manifest and emits an event for the desired run.'],
        ['Host reconciles state', 'Re-fetch status, verify access and runtime major; keep revision 41 visible.'],
        ['Register and stage 42', 'Load the authorized bundle; verify registration and mount a read-only candidate.'],
        ['Capture compatible state', 'Briefly pause input and restore current selections using the agreed schema.'],
        ['Activate 42; retire 41', 'Check the load token, switch containers, abort old requests, dispose and unregister unused factories.']
      ], result: 'Visible: revision 42 · old instance disposed'
    },
    failure: {
      label: 'Candidate fails',
      steps: [
        ['Release 42 approved', 'Revision 41 continues to serve the current dashboard.'],
        ['Candidate begins mounting', 'Registration succeeds; initial required data rendering fails.'],
        ['Readiness rejects', 'Host records diagnostics and disposes candidate resources.'],
        ['Keep revision 41', 'Resume input and show the failure without replacing the working view.']
      ], result: 'Visible: revision 41 · ordinary failure recovered, not a security sandbox'
    },
    stale: {
      label: 'Newer revision wins',
      steps: [
        ['Start loading revision 42', 'Desired release is 42; load token is 7.'],
        ['User requests revision 43', 'Host advances its desired release and load token to 8.'],
        ['Revision 43 becomes ready', 'Current token matches; activate 43 and dispose revision 41.'],
        ['Revision 42 finishes late', 'Token 7 is obsolete. Dispose the candidate; never replace 43.']
      ], result: 'Visible: revision 43 · late revision 42 ignored'
    }
  };
  // Export pure walkthrough data for static tests; this is not a runtime loader.
  if (typeof module !== 'undefined' && module.exports) module.exports = scenarios;
  if (typeof document === 'undefined') return;
  const root = document.getElementById('technical-document');
  if (!root) return;
  const links = [...root.querySelectorAll('.sidebar ol a')];
  const sections = [...root.querySelectorAll('main section')];
  const mark = () => {
    let active = sections[0];
    for (const section of sections) if (section.getBoundingClientRect().top <= 130) active = section;
    for (const link of links) {
      if (link.hash === '#' + active.id) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    }
  };
  let pending = false;
  window.addEventListener('scroll', () => {
    if (!pending) { pending = true; requestAnimationFrame(() => { mark(); pending = false; }); }
  }, { passive: true });
  window.addEventListener('resize', mark);
  mark();
  const search = root.querySelector('#section-search');
  search.addEventListener('input', () => {
    const term = search.value.trim().toLowerCase();
    for (const link of links) link.parentElement.hidden = !link.textContent.toLowerCase().includes(term);
    root.querySelector('#search-empty').hidden = links.some(link => !link.parentElement.hidden);
  });
  for (const button of root.querySelectorAll('.node')) {
    button.addEventListener('click', () => {
      const figure = button.closest('figure');
      for (const node of figure.querySelectorAll('.node')) node.setAttribute('aria-pressed', String(node === button));
      figure.querySelector('.diagram-detail').textContent = button.dataset.detail;
    });
  }
  for (const pre of root.querySelectorAll('pre')) {
    const code = pre.querySelector('code');
    const copy = document.createElement('button');
    copy.type = 'button'; copy.className = 'copy'; copy.textContent = 'Copy';
    copy.setAttribute('aria-label','Copy code example');
    copy.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(code.textContent); copy.textContent = 'Copied'; }
      catch { copy.textContent = 'Select to copy'; }
      setTimeout(() => { copy.textContent = 'Copy'; }, 1800);
    });
    pre.append(copy);
  }
  const showScenario = key => {
    const scenario = scenarios[key];
    const sequence = root.querySelector('#switch-sequence');
    sequence.replaceChildren();
    for (const [title, description] of scenario.steps) {
      const item = document.createElement('li');
      const content = document.createElement('div');
      const label = document.createElement('strong'); label.textContent = title;
      const detail = document.createElement('small'); detail.textContent = description;
      content.append(label, detail); item.append(content); sequence.append(item);
    }
    root.querySelector('#switch-result').textContent = scenario.result;
    for (const graph of root.querySelectorAll('[data-revision-graph]')) graph.hidden = graph.dataset.revisionGraph !== key;
    for (const button of root.querySelectorAll('[data-scenario]')) button.setAttribute('aria-pressed', String(button.dataset.scenario === key));
  };
  for (const button of root.querySelectorAll('[data-scenario]')) button.addEventListener('click', () => showScenario(button.dataset.scenario));
  showScenario('success');
})();
