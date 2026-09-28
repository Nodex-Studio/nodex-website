(() => {
  const root = document.getElementById('studio-document');
  if (!root) return;
  const links = Array.from(root.querySelectorAll('.document-nav a'));
  const sections = Array.from(root.querySelectorAll('.document-section'));
  const activate = id => links.forEach(link => {
    if (link.getAttribute('href') === '#' + id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  const markPosition = () => {
    let current = sections[0];
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= 160) current = section;
    }
    if (current) activate(current.id);
  };
  links.forEach(link => link.addEventListener('click', event => {
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: 'instant', block: 'start' });
    activate(target.id);
  }));
  root.querySelector('.wordmark').addEventListener('click', event => {
    event.preventDefault();
    root.scrollIntoView({ behavior: 'instant', block: 'start' });
    activate(sections[0].id);
  });
  let scheduled = false;
  window.addEventListener('scroll', () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { markPosition(); scheduled = false; });
  }, { passive: true });
  window.addEventListener('resize', markPosition);
  window.addEventListener('load', markPosition);
  if (document.fonts) document.fonts.ready.then(markPosition);
  markPosition();

  const detailTitle = root.querySelector('[data-layer-title]');
  const detailBody = root.querySelector('[data-layer-description]');
  const nodes = Array.from(root.querySelectorAll('[data-layer]'));
  nodes.forEach(node => node.addEventListener('click', () => {
    nodes.forEach(other => other.setAttribute('aria-pressed', String(other === node)));
    detailTitle.textContent = node.querySelector('span').textContent;
    detailBody.textContent = node.getAttribute('data-detail');
  }));

  if (globalThis.Tweak) {
    const style = { readingWidth: 'Comfortable' };
    const tweak = new Tweak({ container: root, onChange: () => {
      root.style.setProperty('--doc-reader-width', style.readingWidth === 'Focused' ? '670px' : '760px');
    }});
    tweak.addSelect(style, 'readingWidth', { label: 'Reading width', options: ['Comfortable', 'Focused'] });
  }
})();
