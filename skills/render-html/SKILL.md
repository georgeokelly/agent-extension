---
# Spec (required)
name: render-html
description: >-
  Render self-contained HTML documents from Markdown or rendered HTML sources,
  including local image asset embedding and arXiv-like academic document styling.

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
  produce offline/shareable HTML, generate arXiv-like academic document pages,
  or render technical documents with figures, captions, code blocks, tables,
  footnotes, and math.
argument-hint: "[source.md|source.html] [output.html] [assets root optional]"
---

# Render HTML Documents

This skill produces complete HTML documents, not raw HTML fragments. The main
path is:

```text
Markdown or HTML source -> rendered HTML -> embedded local assets -> styled standalone document -> verified artifact
```

`render-html` replaces the legacy `convert-md2html` skill name. Do not preserve
the old behavior as a primary workflow; use legacy conversion notes only as
tactical renderer guidance.

## Primary Outcomes

- Render Markdown or existing HTML into a complete `<!doctype html>` document.
- Resolve local image references from the source document location or supplied asset root.
- Embed local images as `data:` URIs for single-file delivery.
- Apply an academic, arXiv/ar5iv-inspired document layout.
- Preserve accessible figures, captions, tables, code blocks, links, footnotes, and math.
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

3. Render document:
   - Prefer existing project tooling when the repo documents a Markdown pipeline.
   - Prefer `pandoc` for rich Markdown, footnotes, tables, and math.
   - Prefer `marked` for lightweight Node.js workflows.
   - Use the arXiv-like document shell from
     [arxiv-like-html-document.md](references/arxiv-like-html-document.md).

4. Embed local image assets:
   - Use [scripts/embed_assets.py](scripts/embed_assets.py) after HTML rendering.
   - Preserve `alt` attributes.
   - Treat missing files, unsupported image types, missing `alt`, and oversized assets as errors.

5. Verify:
   - Confirm the output opens locally.
   - Confirm no unresolved local image `src` remains.
   - Confirm desktop and mobile widths reflow without body text overflow.
   - Confirm strict offline outputs contain no unintended remote CSS, JS, image, or font dependencies.

## Renderer Guidance

### Pandoc

Use when document fidelity matters:

```bash
pandoc input.md \
  --from=gfm+footnotes+tex_math_dollars \
  --to=html5 \
  --standalone \
  --metadata title="Document" \
  --mathml \
  --output output.html
```

Then run asset embedding:

```bash
python3 skills/render-html/scripts/embed_assets.py output.html \
  --base-dir "$(dirname input.md)" \
  --output output.html
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

## Design Direction

Use arXiv/ar5iv as a document layout reference, not as a brand template. The
useful patterns are:

- `article` as the main document container.
- Max content width around `52rem`.
- Serif body text and sans-serif headings.
- Clear title and optional metadata block.
- `figure` plus `figcaption` for images with captions.
- Tables with horizontal overflow containment.
- Code blocks with subtle background and horizontal scroll.
- Math rendered as MathML or via MathJax/KaTeX depending on offline needs.
- `prefers-color-scheme` dark mode support.

See [arxiv-like-html-document.md](references/arxiv-like-html-document.md) for
the baseline shell and CSS.

## Non-Goals

- Do not build a full static site generator.
- Do not clone arXiv branding, navigation chrome, or service identity.
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
- CSS is inline unless the user requested separate files.
- Layout is readable at desktop and mobile widths.
- No obvious broken image icons or unresolved local paths.
- Verification commands and results are reported to the user.
