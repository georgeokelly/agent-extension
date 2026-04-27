---
# Spec (required)
name: render-html
description: >-
  Render self-contained HTML documents from Markdown or rendered HTML sources,
  including local image asset embedding and scholarly academic document styling.

# Spec (optional)
license: MIT
compatibility: Cross-tool (Cursor, Claude Code, Codex). Requires filesystem access.
metadata:
  author: georgel
  version: "1.0"
  predecessor: convert-md2html

# Spec (claude-only)
when_to_use: >-
  Use when the user asks to render Markdown or existing HTML into a polished
  standalone HTML document, package local image assets into a single HTML file,
  produce offline/shareable HTML, generate scholarly academic document pages,
  or render technical documents with figures, captions, code blocks, tables,
  footnotes, and math.
argument-hint: "[source.md|source.html] [output.html] [assets root optional]"
---

# Render HTML Documents

This skill produces complete HTML documents, not raw HTML fragments. The main
path is:

```text
Markdown or HTML source -> rendered fragment -> custom scholarly shell -> embedded local assets -> verified standalone document
```

`render-html` replaces the legacy `convert-md2html` skill name. Do not preserve
the old behavior as a primary workflow; use legacy conversion notes only as
tactical renderer guidance.

## Primary Outcomes

- Render Markdown or existing HTML into a complete `<!doctype html>` document.
- Resolve local image references from the source document location or supplied asset root.
- Embed local images as `data:` URIs for single-file delivery.
- Apply `scholarly-3col` academic layout when the source reads like a paper,
  technical report, research note, or evidence-rich Markdown report.
- Preserve accessible figures, captions, tables, code blocks, links, footnotes, and math.
- Render inspectable figures with stable paper-column viewports and inline
  scale/drag when close image inspection helps the reader.
- Verify the rendered artifact before handing it back.

## Default Workflow

1. Identify inputs:
   - Source Markdown or HTML file.
   - Output HTML path.
   - Asset root, defaulting to the source file directory.
   - Whether strict offline output is required.

2. Inspect source:
   - Infer title from frontmatter `title`, first `h1` / `#` heading, or filename.
   - Collect local image references from Markdown image syntax and raw `<img>`.
   - Note external URLs, math delimiters, code blocks, tables, and footnotes.
   - Collect optional frontmatter or sidecar metadata for `sources`,
     `shape_config`, `key_findings`, `caveats`, `version_matrix`, run date, and
     renderer notes.

3. Render document:
   - Prefer existing project tooling when the repo documents a Markdown pipeline.
   - Prefer `pandoc` for rich Markdown, footnotes, tables, and math.
   - Prefer `marked` for lightweight Node.js workflows.
   - Treat renderer output as a fragment that feeds the final document shell.
   - Use the `scholarly-3col` shell from
     [scholarly-html-document.md](references/scholarly-html-document.md).
   - Use [scholarly-3col-template.md](references/scholarly-3col-template.md)
     when a concrete template contract is needed.

4. Embed local image assets:
   - Use [scripts/embed_assets.py](scripts/embed_assets.py) after HTML rendering.
   - Preserve `alt` attributes.
   - Preserve or add intrinsic image `width` / `height` metadata when available
     so figure viewports can keep a stable aspect ratio before interaction.
   - Treat missing files, unsupported image types, missing `alt`, and oversized assets as errors.

5. Verify:
   - Confirm the output opens locally.
   - Confirm no unresolved local image `src` remains.
   - Confirm desktop and mobile widths reflow without body text overflow.
   - Confirm strict offline outputs contain no unintended remote CSS, JS, image, or font dependencies.

## Renderer Guidance

### Pandoc

Use when document fidelity matters. For `scholarly-3col`, Pandoc should render
the body fragment and table of contents; the custom template owns the page
shell, side rails, metadata placement, and CSS.

```bash
pandoc input.md \
  --from=gfm+footnotes+tex_math_dollars \
  --to=html5 \
  --toc \
  --mathml \
  --output body-fragment.html
```

Avoid using Pandoc's default `--standalone` output as the final document for
this layout; it mixes Pandoc's page shell and default CSS with the skill's
custom shell.

Then run asset embedding:

```bash
python3 skills/render-html/scripts/embed_assets.py final.html \
  --base-dir "$(dirname input.md)" \
  --output final.html
```

### Marked

Use for lightweight JavaScript rendering:

```javascript
import { marked } from "marked";
import { readFileSync } from "node:fs";

const markdown = readFileSync("input.md", "utf8");
const htmlFragment = marked.parse(markdown, {
  gfm: true,
  breaks: false,
});
```

Marked does not sanitize HTML. For untrusted Markdown, sanitize rendered output
before writing the final document.

## Asset Embedding Rules

Supported local image types:

- `.png` -> `image/png`
- `.jpg`, `.jpeg` -> `image/jpeg`
- `.gif` -> `image/gif`
- `.webp` -> `image/webp`
- `.svg` -> `image/svg+xml`

Default constraints:

- Skip existing `data:` URLs and remote `http://` / `https://` URLs.
- Require an `alt` attribute on every embedded image.
- Reject image files larger than 5 MB unless the user explicitly accepts the size.
- Reject local paths that resolve outside the asset root.
- Treat untrusted SVG as unsafe unless sanitized before embedding.
- Add missing `width`, `height`, `data-intrinsic-width`, and
  `data-intrinsic-height` for supported local images when dimensions can be read.

## Design Direction

Use scholarly HTML papers as layout inspiration, not as a brand template.
Inspiration-source names, class names, and page chrome must not become local
template dependencies. The default academic mode is `scholarly-3col`; its
specific DOM and CSS rules are defined by
[scholarly-3col-template.md](references/scholarly-3col-template.md) and should
be treated as the implementation contract:

- `body > div.document-shell > aside.left-outline + main.paper-column + aside.right-rail`.
- `left-outline` for persistent numbered section navigation on desktop; hide or
  collapse it on narrow mobile viewports so article prose appears first.
- `paper-column` for a paper-first title block, abstract-like summary, article
  body, appendices, and references.
- `right-rail` for margin-note style sources, shape/config facts, key findings,
  caveats, version matrix, run date, and renderer notes; do not render a
  dashboard/facts-card rail.
- `figure` plus `figcaption` for normal, wide, and margin-caption figures; avoid
  leading with a large figure gallery before the first prose section.
- Interactive figures use `.figure-viewport[data-figure-viewport]`: normal
  figures match paper-column width, height comes from intrinsic aspect ratio,
  `max-height: 70vh` clamps very tall images, and scale/drag transforms only the
  inner image without moving captions or surrounding prose.
- Figure controls include zoom in, zoom out, reset, and an expanded-viewer
  button. The expanded viewer is optional for reading; inline zoom/drag remains
  the primary inspection path when the reader needs surrounding prose visible.
- Normalize Markdown/Pandoc `figure > img` output into that viewport wrapper
  unless the image is a small inline icon or badge.
- Tables use GitHub Markdown-style borders, padding, zebra rows, centered narrow
  tables, and horizontal overflow containment for wide tables.
- Code blocks use GitHub Markdown-style light/dark backgrounds, 16px padding,
  6px radius, 85% monospace text, and horizontal scroll.
- Math rendered as MathML for strict offline output, or via MathJax/KaTeX only
  when the user accepts the dependency model.
- `prefers-color-scheme` dark mode support.

See [scholarly-html-document.md](references/scholarly-html-document.md) for
the reference policy and use [scholarly-3col-template.md](references/scholarly-3col-template.md)
as the strict template contract.

## Non-Goals

- Do not build a full static site generator.
- Do not clone arXiv branding, navigation chrome, or service identity.
- Do not name public reference, template, or example files after inspiration sources.
- Do not make Jekyll or Hugo the primary path.
- Do not guarantee perfect offline TeX rendering when the source needs advanced
  MathJax/KaTeX behavior and no local renderer is available.

## Acceptance Criteria

A finished artifact should satisfy:

- Complete `<!doctype html>` document.
- Valid UTF-8 metadata and viewport tag.
- Source title represented in `<title>` and visible heading.
- Local images embedded or explicitly justified as external.
- All embedded images include `alt`.
- Local embedded images include intrinsic dimensions when the format exposes
  them.
- Inspectable figures have stable viewports and inline zoom/drag that does not
  alter article flow.
- Inspectable figure controls expose an expanded-viewer button without making
  modal viewing mandatory.
- CSS is inline unless the user requested separate files.
- `scholarly-3col` outputs include `document-shell`, `left-outline`,
  `paper-column`, and `right-rail`.
- Layout is readable at desktop and mobile widths.
- No obvious broken image icons or unresolved local paths.
- No copied arXiv branding, page chrome, hosted CSS imports, or service metadata identity.
- Verification commands and results are reported to the user.
