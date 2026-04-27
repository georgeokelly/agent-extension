# Scholarly HTML Document Reference

Use this reference when producing a self-contained scholarly HTML document from
Markdown or rendered HTML fragments. The target output is a local
`scholarly-3col` reading layout: persistent section outline on the left, a
restrained paper column in the middle, and document metadata in a right rail.

This document records public web observations as inspiration, then defines a
local adaptation. The local output must not copy external service branding,
site chrome, exact stylesheet namespaces, hosted assets, or metadata identity.
For the concrete DOM and template contract, see
`references/scholarly-3col-template.md`.

## Real Observations

> **WARNING**: The class names and page identifiers in this section are
> evidence from real public pages. Do not copy these names into local templates,
> CSS selectors, examples, or generated output.

Observed public sources:

- Official HTML sample paper:
  <https://arxiv.org/html/2402.08954v1>
- Abstract page with experimental HTML link:
  <https://arxiv.org/abs/2402.08954>
- Accessible HTML information page:
  <https://info.arxiv.org/about/accessible_HTML.html>
- HTML CSS wrapper:
  <https://arxiv.org/static/browse/0.3.4/css/arxiv-html-papers-20260131.css>
- Base CSS referenced by the wrapper:
  <https://arxiv.org/static/browse/0.3.4/css/ar5iv.0.8.5.css>
- Theme CSS referenced by the wrapper:
  <https://arxiv.org/static/browse/0.3.4/css/arxiv-html-papers-theme-20250131.css>

Structural observations from the public sample:

- The page has service chrome outside the article, including
  `header.arxiv-html-header`.
- Navigation is separated from article prose with
  `nav.ltx_page_navbar > nav.ltx_TOC`.
- Main content is grouped under `div.ltx_page_main`, with an information area
  such as `div#infobox`, body container `div.ltx_page_content`, and article
  root `article.ltx_document`.
- The generated article preserves paper semantics: title, authors, numbered
  section headings, figures with captions, formulas, bibliography, and document
  metadata.
- Math is represented with accessible HTML output, including MathML-backed
  formula structures where available.
- The content column is restrained, with CSS variables and rules that keep the
  main article near a paper-reading width rather than a marketing or dashboard
  width.
- The table of contents is page navigation, not a large in-flow folded block at
  the top of the article.
- Figures are contained within the reading surface, and wider displays can
  support adjacent navigation or metadata without widening the prose measure.
- Responsive behavior changes navigation and metadata prominence instead of
  forcing all side content into the paper prose.

Things that must not be copied into local output:

- External service logo, red header, beta badge, report controls, or site
  footer.
- External service paper identifiers, license box, comments box, hosted CSS
  paths, or asset URLs as if they belonged to the local document.
- The observed class namespace above, including the page and document classes
  shown in the warning section.
- Exact CSS, typography scale, color palette, or page chrome from the public
  service.

## Local Adaptation

The local `scholarly-3col` output is inspired by scholarly reading behavior,
not by external branding. It should look like a compact, durable research
document produced by the local renderer.

The required DOM contract is
`body > div.document-shell > aside.left-outline + main.paper-column + aside.right-rail`.

The required shell is:

```html
<body>
  <div class="document-shell">
    <aside class="left-outline" aria-label="Document outline">
      <!-- Generated section navigation -->
    </aside>
    <main class="paper-column" id="paper">
      <!-- Title block and rendered scholarly body -->
    </main>
    <aside class="right-rail" aria-label="Document metadata">
      <!-- Sources, configuration, findings, caveats, versions, run notes -->
    </aside>
  </div>
</body>
```

The layout has three durable responsibilities:

- `left-outline`: persistent desktop navigation generated from document
  headings; collapsible or top-positioned navigation on small screens.
- `paper-column`: the scholarly article surface with title block, optional
  abstract-like summary, rendered Markdown body, sections, appendices,
  references, figures, tables, code blocks, and formulas.
- `right-rail`: compact margin notes for source and rendering facts that should
  remain visible without dominating the paper. Use rule-separated notes, not
  bordered cards, chips, dashboards, or large metric panels.

Avoid the following anti-patterns:

- A large report-card header that pushes the article below document metadata.
- An uppercase product/report kicker or hero-style title block.
- A folded in-flow table of contents as the first article section.
- A dashboard-style `Run Facts` rail or facts grid.
- A technical-figure gallery before the first prose section.
- Landing-page hero styling, oversized decorative gradients, or product-doc
  feature grids.
- Treating Pandoc standalone output as the final shell owner.

## Metadata Schema

Metadata should be supplied in Markdown frontmatter first. A sidecar JSON or
YAML file may be used when the source format cannot carry frontmatter. The
renderer should normalize both inputs into the same schema before templating.

```yaml
title: "Document Title"
authors:
  - "Ada Lovelace"
  - "Grace Hopper"
date: "2026-04-27"
summary: "One paragraph abstract-like summary for the paper column."
sources:
  - label: "Primary experiment log"
    url: "file:experiments/run-42.json"
    kind: "local-data"
shape_config:
  layout: "scholarly-3col"
  figure_mode_default: "normal"
  math: "mathml"
key_findings:
  - "Finding written as a concise, evidence-backed statement."
caveats:
  - "Known limitation, missing dataset, or interpretation boundary."
version_matrix:
  renderer: "render-html"
  pandoc: "3.x"
  source_revision: "abc123"
run_date: "2026-04-27T10:30:00+08:00"
renderer_notes:
  - "Local SVG assets embedded as data URIs."
```

Required right-rail slots:

- `sources`: source references, datasets, notes, or source documents used to
  produce the artifact.
- `shape_config`: layout and rendering choices that affect interpretation.
- `key_findings`: concise claims the reader should be able to check in the
  paper body.
- `caveats`: known limitations, omissions, or assumptions.
- `version_matrix`: renderer, converter, dependency, source, and data versions
  relevant to reproducibility.
- `run_date`: timestamp for when the artifact was produced.
- `renderer_notes`: asset embedding, math rendering, fallback, or verification
  notes.

If a slot is empty, omit that rail block rather than rendering a placeholder.
Do not move these slots into a large top-of-document fact grid.

## Pandoc Role

Pandoc is a fragment renderer. It should convert Markdown into an HTML5 body
fragment and generated metadata, then the local template owns the document
shell, CSS, side rails, and verification hooks.

Recommended baseline:

```bash
pandoc source.md \
  --from=gfm+tex_math_dollars+yaml_metadata_block \
  --to=html5 \
  --section-divs \
  --toc \
  --mathml \
  --metadata=layout:scholarly-3col
```

Use Pandoc output variables such as the rendered body, title, metadata, and TOC
as inputs to the local template. Do not let Pandoc default standalone HTML or
default CSS decide the final layout.

Formula strategy:

- Prefer `--mathml` for strict offline formula support.
- Allow MathJax or KaTeX only when the user accepts bundled or remote script
  dependencies.
- Keep formulas inside the paper column by default, with horizontal overflow
  containment for long display equations.

## Sections, Appendices, And References

Section behavior:

- Generate stable heading IDs for all headings included in the outline.
- Number sections when the source requests numbering or already uses numbered
  headings.
- Keep the left outline synchronized with the heading hierarchy shown in the
  paper column.
- Avoid adding outline entries for metadata rail headings.

Appendix behavior:

- Treat `Appendix`, `Appendices`, or source-specific appendix metadata as the
  boundary where section labels may switch from numeric to alphabetic.
- Keep appendices in the paper column and include them in the outline.
- Preserve appendix figures, tables, code, and formulas with the same styling
  rules as main sections.

References behavior:

- Detect common headings such as `References`, `Bibliography`, or `Works Cited`.
- Keep references in the paper column and include the section in the outline.
- Use compact hanging or block-style entries when the source already emits a
  bibliography list.
- Preserve source links and local citations without impersonating external
  service metadata.

## Figures And Tables

Supported figure modes:

- `normal`: figure stays within the paper column and uses a caption below the
  asset.
- `wide`: figure may expand to the available middle reading area while keeping
  margins and side rails stable.
- `margin-caption`: figure asset stays in the paper column; caption may move
  into the right rail only on wide viewports where the rail is visible and the
  association remains accessible.

Recommended Markdown authoring:

```markdown
![Training curve](assets/curve.svg)

*Figure 1: Validation loss across training steps.*
```

Recommended normalized HTML:

```html
<figure class="figure figure-normal figure-interactive" id="fig-training-curve">
  <div
    class="figure-viewport"
    data-figure-viewport
    style="--figure-aspect-ratio: 1200 / 720;"
  >
    <img
      src="data:image/svg+xml;base64,..."
      alt="Training curve"
      width="1200"
      height="720"
      data-intrinsic-width="1200"
      data-intrinsic-height="720"
    >
  </div>
  <figcaption>
    <span class="figure-label">Figure 1.</span>
    Validation loss across training steps.
  </figcaption>
</figure>
```

Rules:

- Resolve local assets relative to the source file or configured asset root.
- Embed local image assets as data URIs for self-contained output.
- Normalize Markdown/Pandoc `figure > img` output into a
  `.figure-viewport[data-figure-viewport]` wrapper unless the image is a small
  inline icon or badge.
- Add intrinsic `width`, `height`, `data-intrinsic-width`, and
  `data-intrinsic-height` when the local asset format exposes dimensions.
- Keep the figure viewport width equal to the paper column for `normal` figures;
  use `wide` only when explicitly useful.
- Use the image aspect ratio to set the viewport height, with `max-height: 70vh`
  and `object-fit: contain` as the overflow fallback.
- Support inline scale and drag inside `.figure-viewport` for close inspection.
  The interaction must not resize the `figure`, move the caption, or cover
  nearby prose.
- Include an expanded-viewer button in figure controls when image details may
  require a larger view. Treat it as optional; normal reading and inline
  zoom/drag must work without opening the modal.
- Preserve meaningful alt text.
- Keep remote `https://` images external unless strict offline output is
  requested and the user approves fetching remote assets.
- Tables remain in the paper column, with horizontal overflow containment on
  narrow screens.

## Responsive Behavior

Desktop behavior:

- Use the three-column shell when there is enough width for outline, paper, and
  rail without widening the prose measure.
- Keep `left-outline` sticky or otherwise persistently reachable.
- Keep `right-rail` compact and scannable.

Tablet behavior:

- Preserve the paper column as the primary reading surface.
- Move the outline above or into a disclosure control if the side column would
  crowd the prose.
- Keep the right rail after the paper or as a secondary collapsible block.

Mobile behavior:

- Render a single readable column.
- Put outline and metadata in explicit collapsible regions outside the article
  prose.
- Preserve heading IDs, figure captions, references, code overflow, and MathML
  formula readability.

## Branding Boundary

The local renderer may adapt these ideas:

- Scholarly article measure and typography.
- Persistent outline separate from article prose.
- Accessible formulas, figures, references, and section structure.
- Compact metadata outside the primary reading flow.

The local renderer must not adapt these identities:

- External service logo, color identity, header, footer, or action buttons.
- External service IDs, license boxes, comments boxes, or issue links as local
  metadata.
- Hosted stylesheets or asset paths.
- Public page class names from the observation section.

## Verification

Run these checks when updating references, templates, or examples:

```bash
find agent-extension/skills/render-html/references \
  -print | rg -i "(arxiv|ar5iv)"
```

Expected result: no public reference or template filenames contain the external
service names.

```bash
rg -n \
  "document-shell|left-outline|paper-column|right-rail|scholarly-3col|MathML|version_matrix|margin-caption|figure-viewport" \
  agent-extension/skills/render-html/references
```

Expected result: the reference and template specs contain the required contract
terms.

Check the external page class names listed in `Real Observations`.

Expected result: those exact observed class names appear only in this file's
`Real Observations` section. They must not appear in local adaptation snippets,
templates, examples, or generated output.
