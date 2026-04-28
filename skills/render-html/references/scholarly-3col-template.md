# Scholarly 3-Column Template Spec

This template spec defines the local `scholarly-3col` DOM contract used by the
render-html skill. It is intentionally local: Pandoc may render Markdown
fragments and metadata, but this template owns the shell, CSS, outline, right
rail, and final verification surface.

## DOM Contract

The required top-level body structure is:

```html
<body>
  <div class="document-shell">
    <aside class="left-outline" aria-label="Document outline">
      <nav class="outline-nav">
        <h2 class="rail-heading">Contents</h2>
        <!-- Generated links to headings inside main.paper-column -->
      </nav>
    </aside>

    <main class="paper-column" id="paper">
      <article class="paper-article">
        <header class="paper-title-block">
          <p class="paper-meta">Run or publication metadata</p>
          <h1>Document title</h1>
          <p class="paper-authors">Optional author list</p>
          <p class="deck"><strong>Abstract.</strong> Optional abstract-like summary.</p>
        </header>

        <!-- Pandoc-rendered HTML5 body fragment -->
      </article>
    </main>

    <aside class="right-rail" aria-label="Document notes">
      <section class="margin-note">
        <p class="note-label">Metadata label</p>
        <p class="note-value">Metadata value</p>
        <p>Short explanatory note.</p>
      </section>
    </aside>
  </div>
</body>
```

Contract rules:

- `body > div.document-shell > aside.left-outline + main.paper-column + aside.right-rail`
  is the required sibling order.
- `left-outline` links only to headings in `paper-column`.
- `paper-column` is the only owner of article prose, appendices, references,
  formulas, tables, and figures.
- `paper-column` is a hard inline-size boundary: figures, images, tables, code
  blocks, and formulas must fit within it or scroll inside it. They must never
  paint into `left-outline` or `right-rail`.
- `right-rail` owns margin notes and compact metadata only; it must not become a
  dashboard, fact card column, or second article column.
- The default table of contents must not appear as a folded in-flow block at the
  top of `paper-column`.
- The first paper body section should be the abstract/executive text, not a
  large figure gallery or technical dashboard.

## Template Inputs

Normalize frontmatter and optional sidecar data into this shape before
rendering:

```yaml
title: "Document Title"
authors: ["Ada Lovelace", "Grace Hopper"]
date: "2026-04-27"
summary: "Abstract-like paper summary."
body_html: "<section>...</section>"
toc_html: "<ol>...</ol>"
sources:
  - label: "Source notebook"
    url: "file:notebooks/analysis.ipynb"
    kind: "local-source"
shape_config:
  layout: "scholarly-3col"
  math: "mathml"
  section_numbering: true
  figure_mode_default: "normal"
key_findings:
  - "Finding with a traceable location in the paper body."
caveats:
  - "Known limitation or interpretation boundary."
version_matrix:
  renderer: "render-html"
  pandoc: "3.x"
  source_revision: "abc123"
run_date: "2026-04-27T10:30:00+08:00"
renderer_notes:
  - "Rendered with Pandoc as an HTML5 fragment."
```

Rendering rules:

- Use `title`, `authors`, `date`, and `summary` in the title block.
- Render a paper-first title block: a restrained metadata line, normal-weight
  centered `h1`, optional authors, and an abstract-like `.deck`.
- Do not render a report/landing hero, uppercase product kicker, metric strip,
  or fact grid above the first prose section.
- Use `toc_html` to build `left-outline`; remove entries that do not resolve to
  IDs inside `paper-column`.
- Prefer numbered outline labels for paper-like documents, for example
  `0.1 Executive Finding` and `A Appendix`.
- Use `body_html` inside `paper-article` after the title block.
- Render right-rail blocks in this order: `sources`, `shape_config`,
  `key_findings`, `caveats`, `version_matrix`, `run_date`, `renderer_notes`.
- Render right-rail content as margin notes, not cards.
- Omit empty metadata blocks.

## Pandoc Fragment Pipeline

Pandoc should not produce the final standalone page. Use it to render an HTML5
fragment, TOC, MathML, and normalized metadata, then inject those values into
the local shell.

```bash
pandoc source.md \
  --from=gfm+tex_math_dollars+yaml_metadata_block \
  --to=html5 \
  --section-divs \
  --toc \
  --mathml \
  --metadata=layout:scholarly-3col
```

Template ownership:

- Pandoc owns conversion from Markdown to semantic HTML fragments.
- The local template owns `<html>`, `<head>`, `<body>`, layout CSS, outline
  placement, rail rendering, and asset embedding integration.
- Avoid Pandoc default standalone CSS as the final authority for layout.
- Prefer MathML for offline formulas. Use MathJax or KaTeX only when the user
  accepts bundled or remote dependencies.

## CSS Baseline

Use this as the strict structural baseline. Adapt only small color accents and
content-specific spacing unless the user asks for another visual language. Keep
the paper-first reading measure, white page surface, numbered outline behavior,
margin-note rail, and GitHub-style code/table rendering.

```css
:root {
  color-scheme: light dark;
  --page-bg: #ffffff;
  --text: #202020;
  --muted: #766f65;
  --rule: #cfc7bb;
  --subtle: #f7f6f3;
  --accent: #16679a;
  --code-bg: #f6f8fa;
  --table-border: #d0d7de;
  --table-row-alt: #f6f8fa;
  --main-width: 52rem;
  --nav-width: 18rem;
  --rail-width: 18rem;
}

@media (prefers-color-scheme: dark) {
  :root {
    --page-bg: #111111;
    --text: #eeeeee;
    --muted: #bbb3a8;
    --rule: #4b443d;
    --subtle: #1a1a1a;
    --accent: #8bc9ee;
    --code-bg: #161b22;
    --table-border: #30363d;
    --table-row-alt: #161b22;
  }
}

* {
  box-sizing: border-box;
}

html {
  background: var(--page-bg);
  color: var(--text);
}

body {
  margin: 0;
  background: var(--page-bg);
  font-family: "Helvetica Neue", Arial, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  line-height: 1.5;
  text-rendering: optimizeLegibility;
}

.document-shell {
  display: grid;
  grid-template-columns: minmax(13rem, var(--nav-width)) minmax(0, var(--main-width)) minmax(13rem, var(--rail-width));
  grid-template-areas: "outline paper rail";
  gap: 2rem;
  justify-content: center;
  align-items: start;
  padding: 1.7rem 1rem 6rem;
}

.left-outline {
  grid-area: outline;
  position: sticky;
  top: 10vh;
  max-height: 88vh;
  overflow: auto;
  padding-right: 1rem;
  color: var(--muted);
  font-size: 0.84rem;
  line-height: 1.45;
  user-select: none;
}

.left-outline .rail-heading {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.left-outline ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.left-outline li {
  margin: 0 0 0.72rem;
}

.left-outline a {
  color: inherit;
  font-weight: 600;
  text-decoration: none;
}

.left-outline a:hover,
.left-outline a:focus {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 0.18em;
}

.paper-column {
  grid-area: paper;
  min-width: 0;
  width: min(100%, var(--main-width));
  max-width: var(--main-width);
  justify-self: stretch;
  overflow-wrap: break-word;
}

.paper-article {
  min-width: 0;
  max-width: 100%;
  background: transparent;
}

.paper-article > * {
  max-width: 100%;
}

.paper-title-block {
  margin: 2.1rem auto 2.5rem;
  text-align: center;
}

.paper-meta {
  margin: 0 0 1rem;
  color: var(--muted);
  font-size: 0.95rem;
  line-height: 1.35;
}

h1 {
  max-width: 44rem;
  margin: 0 auto 1.2rem;
  color: var(--text);
  font-size: 1.78rem;
  font-weight: 400;
  line-height: 1.28;
  letter-spacing: 0;
}

.paper-authors {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.6rem 4.8rem;
  margin: 0.6rem auto 1.2rem;
  color: var(--text);
  font-size: 0.95rem;
}

.deck {
  max-width: 43rem;
  margin: 1.15rem auto 0;
  color: var(--text);
  font-size: 0.95rem;
  line-height: 1.5rem;
  text-align: justify;
  hyphens: auto;
}

.deck strong {
  font-weight: 700;
}

h2,
h3,
h4,
h5,
h6 {
  color: var(--text);
  font-family: inherit;
  line-height: 1.25;
  letter-spacing: 0;
}

h2 {
  margin: 2.3rem 0 1.1rem;
  font-size: 1.24rem;
  font-weight: 700;
}

h3 {
  margin: 1.8rem 0 0.8rem;
  font-size: 1.06rem;
  font-weight: 700;
}

h4,
h5 {
  margin: 1.45rem 0 0.65rem;
  font-size: 0.98rem;
  font-weight: 700;
}

p {
  margin: 0 0 1.35rem;
  text-align: justify;
  hyphens: auto;
}

ul,
ol {
  margin: 0 0 1.35rem 1.35rem;
  padding: 0;
}

li {
  margin: 0.28rem 0;
}

a {
  color: var(--accent);
  text-underline-offset: 0.16em;
}

code {
  border: 0;
  background: var(--code-bg);
  padding: 0.03em 0.22em;
  border-radius: 2px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.86em;
  overflow-wrap: anywhere;
}

pre {
  overflow: auto;
  margin: 1.1rem 0 1.6rem;
  padding: 16px;
  border: 0;
  border-radius: 6px;
  background: var(--code-bg);
  color: var(--text);
  font-size: 85%;
  line-height: 1.45;
  word-wrap: normal;
}

pre code {
  display: inline;
  overflow: visible;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: inherit;
  font-size: 100%;
  line-height: inherit;
  white-space: pre;
  overflow-wrap: normal;
}

.table-scroll {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  margin: 1rem 0 1.5rem;
}

table {
  display: block;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
  border-spacing: 0;
  border-collapse: collapse;
  margin: 1rem 0 1.5rem;
  font-size: 0.9rem;
}

.table-scroll table {
  display: table;
  max-width: none;
  margin: 0;
  overflow: visible;
}

tr {
  background-color: var(--page-bg);
  border-top: 1px solid var(--table-border);
}

tr:nth-child(2n) {
  background-color: var(--table-row-alt);
}

th,
td {
  max-width: min(34rem, calc(var(--main-width) - 2rem));
  padding: 6px 13px;
  border: 1px solid var(--table-border);
  vertical-align: top;
  overflow-wrap: break-word;
}

th {
  font-weight: 600;
  text-align: left;
}

figure {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin: 2.25rem auto 2.5rem;
}

figure img {
  display: block;
  width: auto;
  max-width: 100%;
  height: auto;
  margin: 0 auto;
  border: 0;
  background: transparent;
}

.figure-viewport {
  position: relative;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  aspect-ratio: var(--figure-aspect-ratio, 16 / 9);
  max-height: 70vh;
  overflow: hidden;
  border: 1px solid var(--rule);
  background: var(--subtle);
  cursor: grab;
  touch-action: none;
}

.figure-viewport:focus {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.figure-viewport.is-dragging {
  cursor: grabbing;
}

.figure-viewport img {
  width: 100%;
  height: 100%;
  max-width: none;
  margin: 0;
  object-fit: contain;
  transform: translate3d(var(--figure-pan-x, 0px), var(--figure-pan-y, 0px), 0) scale(var(--figure-scale, 1));
  transform-origin: center center;
  user-select: none;
  pointer-events: none;
}

.figure-controls {
  position: absolute;
  right: 0.55rem;
  bottom: 0.55rem;
  z-index: 2;
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  border: 1px solid var(--rule);
  background: var(--page-bg);
}

.figure-controls button {
  min-width: 2rem;
  min-height: 2rem;
  border: 1px solid var(--rule);
  background: var(--page-bg);
  color: var(--text);
  font: 600 0.82rem/1 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  cursor: pointer;
}

.figure-controls button:hover,
.figure-controls button:focus {
  border-color: var(--accent);
  color: var(--accent);
}

.figure-viewer {
  width: min(96vw, 92rem);
  height: min(94vh, 64rem);
  max-width: none;
  max-height: none;
  padding: 1rem;
  border: 1px solid var(--rule);
  background: var(--page-bg);
  color: var(--text);
}

.figure-viewer::backdrop {
  background: rgba(17, 24, 39, 0.68);
}

.figure-viewer-shell {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 0.75rem;
  height: 100%;
}

.figure-viewer-toolbar {
  display: flex;
  justify-content: flex-end;
}

.figure-viewer-close {
  min-width: 2rem;
  min-height: 2rem;
  border: 1px solid var(--rule);
  background: var(--page-bg);
  color: var(--text);
  font: 600 1rem/1 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  cursor: pointer;
}

.figure-viewer-close:hover,
.figure-viewer-close:focus {
  border-color: var(--accent);
  color: var(--accent);
}

.figure-viewer-canvas {
  min-height: 0;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--rule);
  background: var(--subtle);
}

.figure-viewer-canvas img {
  display: block;
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  margin: auto;
  object-fit: contain;
}

figcaption {
  max-width: 44rem;
  margin: 0.75rem auto 0;
  color: var(--text);
  font-size: 0.92rem;
  line-height: 1.45;
  text-align: center;
}

.figure-grid {
  display: block;
  margin: 0;
}

.figure-grid figure {
  margin: 2.25rem auto 2.5rem;
}

.figure-wide {
  width: 100%;
  max-width: 100%;
}

.math {
  overflow-x: auto;
}

.right-rail {
  grid-area: rail;
  position: sticky;
  top: 10vh;
  max-height: 88vh;
  overflow: auto;
  padding-left: 0.6rem;
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.45;
}

.margin-note {
  margin: 0 0 0.55rem;
  padding: 0.85rem 0 2.1rem;
  border-top: 1px solid var(--text);
}

.margin-note p {
  margin: 0.15rem 0 0;
  text-align: left;
  hyphens: none;
}

.note-label {
  color: var(--muted);
  font-size: 0.78rem;
}

.note-value {
  color: var(--text);
  font-weight: 600;
}

.note-mono {
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.78rem;
}

.source-list code {
  display: block;
  margin: 0.18rem 0;
  padding: 0;
  background: transparent;
  word-break: break-word;
}

@media (max-width: 1279px) {
  .document-shell {
    grid-template-columns: minmax(0, var(--main-width)) minmax(13rem, var(--rail-width));
    grid-template-areas:
      "outline outline"
      "paper rail";
  }

  .left-outline {
    position: static;
    max-height: none;
    padding: 0 0 1rem;
  }

  .left-outline nav > ul {
    columns: 2;
    column-gap: 2rem;
  }
}

@media (max-width: 860px) {
  body {
    font-size: 16px;
  }

  .document-shell {
    display: block;
    padding: 1rem;
  }

  .left-outline,
  .right-rail {
    display: none;
  }

  h1 {
    font-size: 1.45rem;
  }
	}
	```

## Figure Interaction Script

Use inline pan and zoom for figures that need close inspection while the reader
keeps surrounding prose visible. The interaction must transform only the image
inside `.figure-viewport`; it must not resize the `figure`, `figcaption`, or
article flow after initial layout.

Include this script when the document emits `.figure-viewport[data-figure-viewport]`:
wheel zoom activates after the figure viewport is focused, so ordinary page
scrolling over an unzoomed figure remains usable.

```html
<script>
(() => {
  const selector = ".figure-viewport[data-figure-viewport]";
  const minScale = 1;
  const maxScale = 5;
  let figureDialog = null;

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function closeDialog(dialog) {
    if (typeof dialog.close === "function") {
      dialog.close();
    } else {
      dialog.removeAttribute("open");
    }
  }

  function getFigureDialog() {
    if (figureDialog) {
      return figureDialog;
    }

    const dialog = document.createElement("dialog");
    dialog.className = "figure-viewer";
    dialog.innerHTML = `
      <div class="figure-viewer-shell">
        <div class="figure-viewer-toolbar">
          <button
            class="figure-viewer-close"
            type="button"
            aria-label="Close expanded viewer"
            title="Close"
          >×</button>
        </div>
        <div class="figure-viewer-canvas" tabindex="0">
          <img alt="">
        </div>
      </div>
    `;
    dialog
      .querySelector(".figure-viewer-close")
      .addEventListener("click", () => closeDialog(dialog));
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        closeDialog(dialog);
      }
    });
    document.body.appendChild(dialog);
    figureDialog = dialog;
    return figureDialog;
  }

  function openExpandedViewer(sourceImage) {
    const dialog = getFigureDialog();
    const targetImage = dialog.querySelector(".figure-viewer-canvas img");
    targetImage.src = sourceImage.currentSrc || sourceImage.src;
    targetImage.alt = sourceImage.alt || "";

    const width = sourceImage.dataset.intrinsicWidth || sourceImage.getAttribute("width");
    const height = sourceImage.dataset.intrinsicHeight || sourceImage.getAttribute("height");
    if (width) {
      targetImage.setAttribute("width", width);
    } else {
      targetImage.removeAttribute("width");
    }
    if (height) {
      targetImage.setAttribute("height", height);
    } else {
      targetImage.removeAttribute("height");
    }

    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
  }

  function setupViewport(viewport) {
    const image = viewport.querySelector("img");
    if (!image || viewport.dataset.figureReady === "true") {
      return;
    }
    viewport.dataset.figureReady = "true";
    if (!viewport.hasAttribute("tabindex")) {
      viewport.tabIndex = 0;
    }

    let scale = 1;
    let panX = 0;
    let panY = 0;
    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    function setAspectRatio() {
      const width = Number(
        image.dataset.intrinsicWidth || image.getAttribute("width") || image.naturalWidth
      );
      const height = Number(
        image.dataset.intrinsicHeight || image.getAttribute("height") || image.naturalHeight
      );
      if (width > 0 && height > 0) {
        viewport.style.setProperty("--figure-aspect-ratio", `${width} / ${height}`);
      }
    }

    function clampPan() {
      const rect = viewport.getBoundingClientRect();
      const maxX = Math.max(0, (rect.width * (scale - 1)) / 2);
      const maxY = Math.max(0, (rect.height * (scale - 1)) / 2);
      panX = clamp(panX, -maxX, maxX);
      panY = clamp(panY, -maxY, maxY);
    }

    function applyTransform() {
      clampPan();
      viewport.style.setProperty("--figure-scale", scale.toFixed(3));
      viewport.style.setProperty("--figure-pan-x", `${panX.toFixed(1)}px`);
      viewport.style.setProperty("--figure-pan-y", `${panY.toFixed(1)}px`);
      viewport.dataset.scale = scale.toFixed(2);
    }

    function zoomBy(multiplier) {
      scale = clamp(scale * multiplier, minScale, maxScale);
      if (scale === minScale) {
        panX = 0;
        panY = 0;
      }
      applyTransform();
    }

    function reset() {
      scale = 1;
      panX = 0;
      panY = 0;
      applyTransform();
    }

    function addControls() {
      if (viewport.querySelector(".figure-controls")) {
        return;
      }
      const controls = document.createElement("div");
      controls.className = "figure-controls";
      controls.setAttribute("aria-label", "Figure controls");
      controls.addEventListener("pointerdown", (event) => event.stopPropagation());

      function button(text, label, handler) {
        const element = document.createElement("button");
        element.type = "button";
        element.textContent = text;
        element.setAttribute("aria-label", label);
        element.title = label;
        element.addEventListener("click", handler);
        controls.appendChild(element);
      }

      button("+", "Zoom in", () => zoomBy(1.2));
      button("-", "Zoom out", () => zoomBy(1 / 1.2));
      button("1x", "Reset zoom", reset);
      button("⛶", "Open expanded viewer", () => openExpandedViewer(image));
      viewport.appendChild(controls);
    }

    viewport.addEventListener(
      "wheel",
      (event) => {
        if (document.activeElement !== viewport && scale === 1) {
          return;
        }
        event.preventDefault();
        zoomBy(event.deltaY < 0 ? 1.12 : 1 / 1.12);
      },
      { passive: false }
    );

    viewport.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) {
        return;
      }
      viewport.focus({ preventScroll: true });
      dragging = true;
      lastX = event.clientX;
      lastY = event.clientY;
      viewport.classList.add("is-dragging");
      viewport.setPointerCapture(event.pointerId);
    });

    viewport.addEventListener("pointermove", (event) => {
      if (!dragging || scale <= 1) {
        return;
      }
      panX += event.clientX - lastX;
      panY += event.clientY - lastY;
      lastX = event.clientX;
      lastY = event.clientY;
      applyTransform();
    });

    function stopDrag(event) {
      dragging = false;
      viewport.classList.remove("is-dragging");
      if (viewport.hasPointerCapture(event.pointerId)) {
        viewport.releasePointerCapture(event.pointerId);
      }
    }

    viewport.addEventListener("pointerup", stopDrag);
    viewport.addEventListener("pointercancel", stopDrag);
    viewport.addEventListener("keydown", (event) => {
      if (event.key === "+" || event.key === "=") {
        event.preventDefault();
        zoomBy(1.2);
      } else if (event.key === "-" || event.key === "_") {
        event.preventDefault();
        zoomBy(1 / 1.2);
      } else if (event.key === "0") {
        event.preventDefault();
        reset();
      }
    });

    if (image.complete) {
      setAspectRatio();
    } else {
      image.addEventListener("load", setAspectRatio, { once: true });
    }
    addControls();
    applyTransform();
  }

  function setupAll() {
    document.querySelectorAll(selector).forEach(setupViewport);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupAll, { once: true });
  } else {
    setupAll();
  }
})();
</script>
```

## Right-Rail Rendering

Right-rail blocks should be compact margin notes. They should look like
scholarly margin material: top rule, small label, short value, and one optional
explanatory line. Do not use bordered cards, dashboard panels, chips, or large
metrics in the rail.

```html
<aside class="right-rail" aria-label="Document notes">
  <section class="margin-note" id="rail-best-result">
    <p class="note-label">Best source-local kernel</p>
    <p class="note-value">v4 / 46.5 us</p>
    <p>load-ahead fast path</p>
  </section>

  <section class="margin-note source-list" id="rail-sources">
    <p class="note-label">Sources</p>
    <code>experiment/kernels.cu</code>
    <code>bench_compare.py</code>
  </section>
</aside>
```

Rules:

- Use the schema field names as source keys, but render human-readable headings.
- Keep rail headings out of the left outline.
- Keep long values wrapped or truncated with accessible full text.
- Preserve URLs and local references without presenting them as external service
  metadata.
- Hide the rail on narrow mobile viewports unless the user explicitly asks for
  mobile metadata above the article.

## Figure Modes

Renderer rules:

- Normalize Markdown/Pandoc `figure > img` output into the
  `.figure-viewport[data-figure-viewport]` wrapper unless the image is a small
  inline icon or badge.
- Normal figures occupy the same width as `.paper-column` prose: `width: 100%`,
  `max-width: 100%`, and no viewport-relative widths.
- `wide` figures are still bounded by `.paper-column` in this three-column
  shell. Use a different rail-free shell for true page-wide figures.
- Figure height is stable after initial layout. Set
  `--figure-aspect-ratio: intrinsic_width / intrinsic_height` on
  `.figure-viewport` whenever intrinsic dimensions are known.
- If intrinsic dimensions are unknown, use the CSS fallback `16 / 9` rather than
  allowing layout shift.
- Apply `max-height: 70vh` to the viewport. If the intrinsic aspect ratio would
  exceed that height, keep the viewport clamped and use `object-fit: contain` for
  the initial image view.
- Inline zoom and drag must transform only the image inside `.figure-viewport`;
  never change the outer `figure`, `figcaption`, or article flow during
  interaction.
- The expanded viewer button opens a modal clone of the figure image. Inline
  constrained pan/zoom remains the default for technical documents where prose
  and figure details are read together.

## Tables

Tables should match GitHub Markdown table behavior inside the paper column:
left-aligned block tables, 1px borders, `6px 13px` cells, alternating rows, and
horizontal scroll for wide tables. Do not stretch narrow tables to the full
paper width unless the source table itself needs it.

Renderer rules:

- Emit plain `<table>` for ordinary Markdown tables; the CSS baseline handles
  GitHub-style display and horizontal overflow.
- For custom HTML tables or tables with very wide cells, wrap the table in
  `<div class="table-scroll">...</div>` and keep the table itself
  `width: max-content`.
- Keep table overflow inside `.paper-column`; table content must not widen the
  grid or overlap `right-rail`.
- Wrap long path-like inline `code` tokens inside cells with `overflow-wrap:
  anywhere`, but preserve fenced code blocks with horizontal scroll.

Normal figure:

```html
<figure class="figure figure-normal figure-interactive" id="fig-loss">
  <div
    class="figure-viewport"
    data-figure-viewport
    style="--figure-aspect-ratio: 1200 / 720;"
  >
    <img
      src="data:image/svg+xml;base64,..."
      alt="Training and validation loss"
      width="1200"
      height="720"
      data-intrinsic-width="1200"
      data-intrinsic-height="720"
    >
  </div>
  <figcaption>
    <span class="figure-label">Figure 1.</span>
    Training and validation loss across epochs.
  </figcaption>
</figure>
```

Wide figure:

```html
<figure class="figure figure-wide figure-interactive" id="fig-system-map">
  <div
    class="figure-viewport"
    data-figure-viewport
    style="--figure-aspect-ratio: 1600 / 700;"
  >
    <img
      src="data:image/svg+xml;base64,..."
      alt="System map"
      width="1600"
      height="700"
      data-intrinsic-width="1600"
      data-intrinsic-height="700"
    >
  </div>
  <figcaption>
    <span class="figure-label">Figure 2.</span>
    End-to-end system map.
  </figcaption>
</figure>
```

Margin-caption figure:

```html
<figure class="figure figure-margin-caption figure-interactive" id="fig-ablation">
  <div
    class="figure-viewport"
    data-figure-viewport
    style="--figure-aspect-ratio: 1000 / 760;"
  >
    <img
      src="data:image/png;base64,..."
      alt="Ablation table heatmap"
      width="1000"
      height="760"
      data-intrinsic-width="1000"
      data-intrinsic-height="760"
    >
  </div>
  <figcaption id="fig-ablation-caption">
    <span class="figure-label">Figure 3.</span>
    Ablation results by feature group.
  </figcaption>
</figure>
```

Margin-caption rules:

- Keep the `figcaption` in the DOM adjacent to the figure for accessibility.
- CSS may visually place the caption into the right rail area only on wide
  viewports where it does not collide with metadata.
- On tablet and mobile, caption returns below the figure.
- Do not use right-rail metadata blocks as the only caption location.

## Sections, Appendices, References

Sections:

- Use stable heading IDs for all outline targets.
- Preserve source-provided numbering when present.
- If automatic numbering is enabled, scope it to headings inside
  `paper-column`.

Appendices:

- Include appendices in the paper column and left outline.
- Support alphabetic appendix labels when the source marks an appendix
  boundary.
- Keep appendix figures, tables, code blocks, and formulas under the same
  layout rules as the main body.

References:

- Treat `References`, `Bibliography`, and `Works Cited` as bibliography
  boundaries.
- Keep bibliography entries compact and readable inside `paper-column`.
- Preserve source links, DOIs, and local citations.

## Verification Checklist

Run these from the workspace root after changing reference or template files:

```bash
find agent-extension/skills/render-html/references \
  -print | rg -i "(arxiv|ar5iv)"
```

Expected result: no matching filenames.

```bash
rg -n \
  "document-shell|left-outline|paper-column|right-rail|scholarly-3col|MathML|version_matrix|margin-caption|figure-viewport" \
  agent-extension/skills/render-html/references
```

Expected result: required terms appear in the scholarly reference and template
spec.

```bash
rg -n \
  "body > div.document-shell > aside.left-outline \\+ main.paper-column \\+ aside.right-rail|Pandoc|fragment|--mathml|sources|shape_config|key_findings|caveats|version_matrix|run_date|renderer_notes" \
  agent-extension/skills/render-html/references
```

Expected result: the DOM contract, Pandoc fragment role, MathML preference, and
metadata schema are all documented.
