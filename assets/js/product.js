/* Typing Mastery product page — downloads, lightbox, demo expand */
(() => {
  "use strict";

  const REPO = "Nodex-Studio/typing-mastery";
  const RELEASES = `https://github.com/${REPO}/releases`;
  const LATEST = `${RELEASES}/latest`;
  const API = `https://api.github.com/repos/${REPO}/releases/latest`;

  /* platform catalogue: each platform lists every build format it ships,
     so every artifact (e.g. Linux .AppImage / .deb / .rpm) gets its own link */
  const PLATFORMS = {
    mac: {
      label: "macOS",
      builds: [{ exts: [".dmg"], label: ".dmg" }],
    },
    win: {
      label: "Windows",
      builds: [
        { exts: [".msi"], label: ".msi" },
        { exts: ["-setup.exe", ".exe"], label: ".exe" },
      ],
    },
    linux: {
      label: "Linux",
      builds: [
        { exts: [".appimage"], label: ".AppImage" },
        { exts: [".deb"], label: ".deb" },
        { exts: [".rpm"], label: ".rpm" },
      ],
    },
  };

  /* ---- detect OS ---- */
  function detectOS() {
    const ua = (navigator.userAgentData?.platform || navigator.platform || navigator.userAgent || "").toLowerCase();
    if (/mac|iphone|ipad|ipod/.test(ua)) return "mac";
    if (/win/.test(ua)) return "win";
    if (/linux|android|x11/.test(ua)) return "linux";
    return "mac";
  }

  const os = detectOS();
  const state = { assets: null, tag: null, url: LATEST }; // url = where buttons point

  /* find the release asset matching a build's extensions */
  function findAsset(exts) {
    if (!state.assets) return null;
    for (const ext of exts) {
      const e = ext.replace(/^-/, "").toLowerCase();
      const hit = state.assets.find((a) => a.name.toLowerCase().endsWith(e));
      if (hit) return hit;
    }
    return null;
  }

  /* the recommended (primary) asset for a platform = its first available build */
  function primaryAsset(key) {
    for (const bld of PLATFORMS[key].builds) {
      const a = findAsset(bld.exts);
      if (a) return a;
    }
    return null;
  }

  /* ---- render the primary (detected) download button + others ---- */
  function render() {
    document.querySelectorAll("[data-dl-primary]").forEach((btn) => {
      const p = PLATFORMS[os];
      const a = primaryAsset(os);
      btn.href = a ? a.browser_download_url : (state.tag ? LATEST : RELEASES);
      btn.querySelector("[data-dl-label]").textContent = `Download for ${p.label}`;
    });

    document.querySelectorAll("[data-dl-note]").forEach((note) => {
      if (state.tag) {
        const ver = state.tag.replace(/^app[-_]?/i, "");
        note.innerHTML = `Latest release <b>${ver}</b> · free &amp; open source · macOS · Windows · Linux`;
      } else {
        note.innerHTML = `Builds are published to <b>GitHub Releases</b> — open-source, no account needed.`;
      }
    });

    /* download chips — one per build format, so Linux shows .AppImage, .deb & .rpm */
    document.querySelectorAll("[data-dl-others]").forEach((row) => {
      row.innerHTML = "";
      Object.keys(PLATFORMS).forEach((key) => {
        const p = PLATFORMS[key];
        p.builds.forEach((bld) => {
          const a = findAsset(bld.exts);
          const chip = document.createElement("a");
          chip.className = "dl-chip";
          chip.href = a ? a.browser_download_url : (state.tag ? LATEST : RELEASES);
          chip.target = a ? "_self" : "_blank";
          chip.rel = "noopener";
          chip.innerHTML =
            `${ICON[key]}<span>${p.label} ${bld.label}</span>` +
            (a ? `<small>${prettySize(a.size)}</small>` : "");
          if (key === os) chip.style.borderColor = "var(--accent)";
          row.appendChild(chip);
        });
      });
    });
  }

  function prettySize(b) {
    if (!b) return "";
    const mb = b / 1048576;
    return mb >= 1 ? `${mb.toFixed(0)} MB` : `${(b / 1024).toFixed(0)} KB`;
  }

  const ICON = {
    mac: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.5 3c.1 1.2-.4 2.3-1.1 3.1-.8.9-2 1.6-3.2 1.5-.1-1.1.5-2.3 1.2-3 .8-.9 2.1-1.5 3.1-1.6zM20 17.2c-.5 1.2-.8 1.7-1.5 2.7-1 1.5-2.4 3.3-4.1 3.3-1.5 0-1.9-1-4-1-2 0-2.5 1-4 1-1.7 0-3-1.7-4-3.1-2.7-3.9-3-8.5-1.3-11 1.2-1.7 3-2.7 4.8-2.7 1.8 0 2.9 1 4.4 1 1.4 0 2.3-1 4.4-1 1.5 0 3.2.8 4.3 2.3-3.8 2-3.2 7.4.5 8.5z"/></svg>`,
    win: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 5.5 10.5 4.5v7H3zM11.5 4.4 21 3v8.5h-9.5zM3 12.5h7.5v7L3 18.5zM11.5 12.5H21V21l-9.5-1.4z"/></svg>`,
    linux: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c2 0 3 1.7 3 4 0 1.5.5 2.4 1.4 3.7 1 1.4 1.6 2.6 1.6 4.3 0 .8.4 1.3 1 2 .6.6 1 1 1 1.7 0 .9-.9 1.3-2 1.3-1 0-1.7-.4-2.4-.4-.5 0-.7.3-2.1.3h-1c-1.4 0-1.6-.3-2.1-.3-.7 0-1.4.4-2.4.4-1.1 0-2-.4-2-1.3 0-.7.4-1.1 1-1.7.6-.7 1-1.2 1-2 0-1.7.6-2.9 1.6-4.3C8.5 8.4 9 7.5 9 6c0-2.3 1-4 3-4zm-1.4 4.8c-.5 0-.8.4-.8.9s.3.9.8.9.8-.4.8-.9-.3-.9-.8-.9zm2.8 0c-.5 0-.8.4-.8.9s.3.9.8.9.8-.4.8-.9-.3-.9-.8-.9z"/></svg>`,
  };

  /* ---- try the GitHub API; degrade gracefully ---- */
  fetch(API, { headers: { Accept: "application/vnd.github+json" } })
    .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
    .then((rel) => {
      state.tag = rel.tag_name || rel.name;
      state.assets = Array.isArray(rel.assets) ? rel.assets : [];
      render();
    })
    .catch(() => { /* no published release yet — keep links to /releases */ })
    .finally(render);

  render(); // paint immediately with fallbacks

  /* ---- lightbox for screenshots ---- */
  const lb = document.getElementById("lightbox");
  if (lb) {
    const img = lb.querySelector("img");
    const cap = lb.querySelector(".lightbox-cap");
    const open = (src, caption) => {
      img.src = src; cap.textContent = caption || "";
      lb.classList.add("open"); document.body.style.overflow = "hidden";
    };
    const close = () => { lb.classList.remove("open"); document.body.style.overflow = ""; img.src = ""; };

    document.addEventListener("click", (e) => {
      const z = e.target.closest("[data-zoom] img, .shot img, .theme-card img");
      if (z) {
        const fig = z.closest("figure, .shot");
        open(z.currentSrc || z.src, z.getAttribute("alt") || (fig && fig.dataset.cap) || "");
        return;
      }
      if (e.target.closest("[data-lb-close]") || e.target === lb) close();
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  }

  /* ---- demo: click to expand into the lightbox / fullscreen ---- */
  const demoBtn = document.querySelector("[data-demo-expand]");
  if (demoBtn) {
    const frame = demoBtn.closest(".demo-frame");
    const video = frame && frame.querySelector("video");
    demoBtn.addEventListener("click", () => {
      if (!video) return;
      if (video.requestFullscreen) {
        video.muted = false; video.controls = true;
        video.requestFullscreen().catch(() => { video.muted = true; });
        video.addEventListener("fullscreenchange", () => {
          if (!document.fullscreenElement) { video.controls = false; video.muted = true; }
        }, { once: true });
      }
    });
  }

  /* ---- themes carousel: prev/next arrows + gentle autoplay ---- */
  const rail = document.querySelector("[data-carousel-rail]");
  if (rail) {
    const stepSize = () => {
      const card = rail.querySelector(".theme-card");
      const gap = parseFloat(getComputedStyle(rail).columnGap || getComputedStyle(rail).gap) || 18;
      return card ? card.getBoundingClientRect().width + gap : rail.clientWidth * 0.8;
    };
    const atEnd = () => rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4;
    const go = (dir) => {
      if (dir > 0 && atEnd()) rail.scrollTo({ left: 0, behavior: "smooth" });
      else rail.scrollBy({ left: dir * stepSize(), behavior: "smooth" });
    };
    const prev = document.querySelector("[data-carousel-prev]");
    const next = document.querySelector("[data-carousel-next]");
    prev && prev.addEventListener("click", () => go(-1));
    next && next.addEventListener("click", () => go(1));

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let timer = null, visible = false;
    const stop = () => { clearInterval(timer); timer = null; };
    const start = () => { if (reduce || !visible || timer) return; timer = setInterval(() => go(1), 3800); };
    const carousel = rail.closest(".theme-carousel");
    if (carousel) {
      carousel.addEventListener("mouseenter", stop);
      carousel.addEventListener("mouseleave", start);
      carousel.addEventListener("focusin", stop);
      carousel.addEventListener("touchstart", stop, { passive: true });
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => entries.forEach((e) => {
        visible = e.isIntersecting; visible ? start() : stop();
      }), { threshold: 0.25 }).observe(rail);
    } else { visible = true; start(); }
  }
})();
