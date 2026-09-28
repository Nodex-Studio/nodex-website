/* bipps architecture — living document */
(function () {
  "use strict";
  // Preserve bookmarks from the previous single-page specification.
  var appendixIds = /*APPENDIX_IDS*/;
  if (document.body.classList.contains("page-proposal") &&
      appendixIds.indexOf(location.hash.slice(1).split("--")[0]) !== -1) {
    location.replace("technical.html" + location.hash);
    return;
  }
  var IDENTS = /*IDENTS*/;
  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------------------------------------------------------- theme */
  var root = document.documentElement;
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("bipps-arch-theme", t); } catch (e) {}
    var btn = $("#theme-toggle");
    if (btn) {
      btn.textContent = t === "dark" ? "Light" : "Dark";
      btn.setAttribute("aria-label", "Switch to " + (t === "dark" ? "light" : "dark") + " theme");
    }
  }
  var stored = null;
  try { stored = localStorage.getItem("bipps-arch-theme"); } catch (e) {}
  setTheme(stored || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  $("#theme-toggle").addEventListener("click", function () {
    setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
  });

  /* ---------------------------------------------------- heading anchors */
  $$(".doc h2[id], .doc h3[id], .doc-title").forEach(function (h) {
    if (!h.id && h.parentElement) h.id = h.parentElement.id + "--top";
    var a = document.createElement("a");
    a.className = "anchor"; a.href = "#" + h.id; a.textContent = "#";
    a.setAttribute("aria-label", "Link to this section");
    h.appendChild(a);
  });

  /* ------------------------------------------------------- nav + outline */
  var sections = $$("section.doc");
  var navLinks = {};
  $$(".rail a[data-nav]").forEach(function (a) { navLinks[a.getAttribute("data-nav")] = a; });
  var outlineBox = $("#outline-list");

  function buildOutline(sec) {
    var heads = $$("h2[id]", sec);
    outlineBox.innerHTML = heads.map(function (h) {
      return '<li><a href="#' + h.id + '" data-out="' + h.id + '">' +
             h.firstChild.textContent.trim() + "</a></li>";
    }).join("");
  }

  var activeSection = null;
  function markActive() {
    var y = window.scrollY + 180, cur = sections[0], i;
    for (i = 0; i < sections.length; i++) if (sections[i].offsetTop <= y) cur = sections[i];
    if (cur !== activeSection) {
      activeSection = cur;
      $$(".rail a.active").forEach(function (a) { a.classList.remove("active"); });
      $$(".rail li.open").forEach(function (l) { l.classList.remove("open"); });
      var link = navLinks[cur.id];
      if (link) { link.classList.add("active"); if (link.parentElement) link.parentElement.classList.add("open"); }
      buildOutline(cur);
    }
    var heads = $$("h2[id]", cur), curH = null;
    for (i = 0; i < heads.length; i++) if (heads[i].offsetTop <= y) curH = heads[i];
    // Keep the parent section open and highlight the current subsection on both pages.
    var currentId = curH && navLinks[curH.id] ? curH.id : cur.id;
    $$(".rail a[data-nav]").forEach(function (a) {
      var id = a.getAttribute("data-nav");
      a.classList.toggle("active", id === cur.id || id === currentId);
      if (id === currentId) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
    });
    $$("#outline-list a").forEach(function (a) {
      a.classList.toggle("active", !!curH && a.getAttribute("data-out") === curH.id);
    });
    var max = document.body.scrollHeight - innerHeight;
    $("#progress").style.width = (max > 0 ? (scrollY / max) * 100 : 0) + "%";
  }

  var ticking = false;
  addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { markActive(); ticking = false; });
  }, { passive: true });
  markActive();
  addEventListener("resize", markActive, { passive: true });
  addEventListener("load", markActive);
  if (document.fonts) document.fonts.ready.then(markActive);

  /* Visibility is owned by CSS at the mobile breakpoint; JS only toggles the
     class, so a stale measurement can never strip the rail out of the grid. */
  var navToggle = $("#nav-toggle");
  function setNav(open) {
    document.body.classList.toggle("nav-open", open);
    navToggle.setAttribute("aria-expanded", String(open));
  }
  navToggle.addEventListener("click", function () {
    setNav(!document.body.classList.contains("nav-open"));
  });
  $$(".rail a").forEach(function (a) { a.addEventListener("click", function () { setNav(false); }); });
  addEventListener("resize", function () { if (innerWidth > 900) setNav(false); }, { passive: true });

  /* ------------------------------------------------- identifier popover */
  var pop = $("#ident-pop"), popFor = null;
  function closePop() {
    pop.hidden = true;
    if (popFor) { popFor.setAttribute("aria-expanded", "false"); popFor = null; }
  }
  function openPop(btn) {
    var d = IDENTS[btn.getAttribute("data-ident")];
    if (!d) return;
    pop.classList.toggle("is-open", d.id.charAt(0) === "O");
    pop.innerHTML = '<span class="p-id">' + d.id + '</span>' +
                    '<span class="p-rule">' + d.rule + '</span>' +
                    '<span class="p-detail">' + d.detail + "</span>";
    pop.hidden = false;
    var r = btn.getBoundingClientRect(), pw = pop.offsetWidth;
    var left = Math.min(Math.max(8, r.left + scrollX - 10), scrollX + innerWidth - pw - 12);
    var below = r.bottom + 8 + pop.offsetHeight < innerHeight;
    pop.style.left = left + "px";
    pop.style.top = (below ? r.bottom + scrollY + 8 : r.top + scrollY - pop.offsetHeight - 8) + "px";
    if (popFor) popFor.setAttribute("aria-expanded", "false");
    popFor = btn; btn.setAttribute("aria-expanded", "true");
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest ? e.target.closest(".ident") : null;
    if (btn) { e.preventDefault(); (popFor === btn) ? closePop() : openPop(btn); return; }
    if (!e.target.closest || !e.target.closest("#ident-pop")) closePop();
  });
  document.addEventListener("mouseover", function (e) {
    var btn = e.target.closest ? e.target.closest(".ident") : null;
    if (btn && btn !== popFor && matchMedia("(hover: hover)").matches) openPop(btn);
  });
  addEventListener("scroll", closePop, { passive: true });

  /* ------------------------------------------------------- diagram zoom */
  var lb = $("#lightbox"), lbInner = $("#lightbox .lb-inner");
  function openLb(name) {
    var src = $('.diagram-frame[data-diagram="' + name + '"] svg');
    if (!src) return;
    lbInner.innerHTML = "";
    lbInner.appendChild(src.cloneNode(true));
    lb.hidden = false;
    $("#lightbox .lb-close").focus();
  }
  document.addEventListener("click", function (e) {
    var z = e.target.closest ? e.target.closest("[data-zoom]") : null;
    if (z) { openLb(z.getAttribute("data-zoom")); return; }
    if (e.target === lb || (e.target.closest && e.target.closest(".lb-close"))) lb.hidden = true;
  });

  /* ------------------------------------------------------------ search */
  var index = [];
  function textOf(el) {          // heading anchors must not enter the index
    var c = el.cloneNode(true);
    c.querySelectorAll(".anchor").forEach(function (a) { a.remove(); });
    return c.textContent.replace(/\s+/g, " ").trim();
  }
  sections.forEach(function (sec) {
    var secName = $(".doc-title", sec).firstChild.textContent.trim();
    $$("p, li, h2, h3, td", sec).forEach(function (el) {
      if (el.closest(".table-wrap") && el.tagName !== "TD") return;
      var t = textOf(el);
      if (t.length < 12) return;
      var head = el.closest("section").id;
      var prev = el.previousElementSibling;
      while (prev && !/^H[23]$/.test(prev.tagName)) prev = prev.previousElementSibling;
      index.push({ text: t, low: t.toLowerCase(), sec: secName, id: (prev && prev.id) || head, el: el });
    });
  });

  var box = $("#search"), results = $("#results"), lastHits = [];
  function clearHits() {
    lastHits.forEach(function (el) {
      el.querySelectorAll("mark.hit").forEach(function (m) {
        m.replaceWith(document.createTextNode(m.textContent));
      });
      el.normalize();
    });
    lastHits = [];
  }
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  function escHtml(s) { return s.replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }

  function run(q) {
    clearHits();
    if (q.length < 2) { results.innerHTML = ""; return; }
    var low = q.toLowerCase();
    var hits = index.filter(function (r) { return r.low.indexOf(low) !== -1; }).slice(0, 40);
    if (!hits.length) { results.innerHTML = '<p class="r-none">No match for “' + escHtml(q) + '”.</p>'; return; }
    var re = new RegExp("(" + esc(q) + ")", "ig");
    results.innerHTML = hits.slice(0, 12).map(function (r, i) {
      var at = r.low.indexOf(low);
      var snip = r.text.slice(Math.max(0, at - 45), at + 105);
      if (at > 45) snip = "…" + snip;
      return '<a href="#" data-hit="' + i + '"><span class="r-where">' + escHtml(r.sec) + "</span>" +
             escHtml(snip).replace(re, "<mark>$1</mark>") + "</a>";
    }).join("");
    results.dataset.hits = "1";
    results._hits = hits;
    hits.forEach(function (r) {
      r.el.innerHTML = r.el.innerHTML.replace(
        new RegExp("(" + esc(q) + ")(?![^<]*>)", "ig"), '<mark class="hit">$1</mark>'
      );
      lastHits.push(r.el);
    });
  }

  var t;
  box.addEventListener("input", function () {
    clearTimeout(t);
    t = setTimeout(function () { run(box.value.trim()); }, 130);
  });
  results.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-hit]");
    if (!a) return;
    e.preventDefault();
    var r = results._hits[+a.getAttribute("data-hit")];
    r.el.scrollIntoView({ block: "center", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    r.el.classList.add("flash");
    setTimeout(function () { r.el.classList.remove("flash"); }, 1200);
    results.innerHTML = "";
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== box) { e.preventDefault(); box.focus(); box.select(); }
    if (e.key === "Escape") {
      if (!lb.hidden) { lb.hidden = true; return; }
      if (!pop.hidden) { closePop(); return; }
      if (document.body.classList.contains("nav-open")) { setNav(false); return; }
      if (document.activeElement === box) { box.value = ""; run(""); box.blur(); }
      results.innerHTML = "";
    }
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest(".search-wrap")) results.innerHTML = "";
  });

  /* -------------------------------------------------- hero entrance */
  $$(".inv-list li").forEach(function (li, i) {
    li.style.animationDelay = (0.05 + i * 0.045) + "s";
  });
})();
