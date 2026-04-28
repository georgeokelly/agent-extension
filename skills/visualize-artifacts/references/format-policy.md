# Format Policy

Choose formats from the artifact's source-of-truth and delivery constraints. Do
not rely on AI image generation to satisfy exact size, text, chart, or vector
requirements.

## Format Defaults

| Format | Use When | Source Policy | Delivery Notes |
| --- | --- | --- | --- |
| SVG | Technical diagrams, icons, vector charts, or exact text/line work from trusted sanitized sources. | Keep source SVG or generator source. | Best for zoom/sharpness; sanitize untrusted SVG before embedding. |
| PNG | Fixed static chart, screenshot, diagram export, or review image where pixel layout must not change. | Keep deterministic source where possible. | Export at 2x for reports/slides when text clarity matters. |
| WebP | Large raster, screenshot bundle, heatmap, photo-like asset, or web delivery where size matters. | Keep original PNG/SVG/photo/source separately. | Use lossy or lossless settings based on inspection needs. |
| PDF | Printable or archival diagram/report page. | Keep editable source such as draw.io, SVG, HTML, notebook, or slide. | Good for documents; not ideal as sole editing source. |
| HTML | Interactive plot, inspectable diagram, or standalone visual report. | Keep HTML source and local assets when needed. | Prefer self-contained HTML when portability matters. |
| Alpha PNG/WebP | Cutouts, sprites, foreground assets, or compositing inputs. | Source raster is owned by `imagegen` when AI-generated. | Transparency workflow is part of `imagegen internals` (see SKILL.md Boundary Contract); this skill only requests and packages output. |

## Exact Size And Format

- Treat exact pixel size and final format as deterministic post-processing.
- Use the generator output as source, then convert/resize/crop with a deterministic
  tool.
- Do not promise native exact-size or native WebP output from built-in image
  generation.
- Record both source dimensions and final delivery dimensions when they differ.

## Common Deterministic Tools

These are examples, not bundled requirements:

- ImageMagick: resize, crop, convert, inspect image metadata.
- `cwebp`: WebP conversion and quality control.
- Python/Pillow: scripted resizing, alpha inspection, sprite sheets.
- draw.io CLI or equivalent: `.drawio` export to PNG/SVG/PDF.
- Browser/Playwright or HTML renderer: HTML/SVG screenshot export.

Do not bundle conversion scripts in this skill. If none of the needed tools are
available, document the requirement instead of adding a new script here.

## Source-Master Rules

- For data-backed charts, source-master belongs to `visualize-data` outputs.
- For AI raster assets, source raster belongs to `imagegen` outputs.
- For draw.io diagrams, source-master is `.drawio` or an export with embedded
  diagram data.
- For hybrid artifacts, keep each layer's source and the composition recipe or
  manifest.
- Never leave only a flattened PNG/WebP when future edits are likely.

## SVG Safety

SVG is preferred for sharp technical diagrams and charts when the source is
trusted or sanitized. If the source is untrusted, sanitize or export to PNG/PDF
for delivery while preserving a vetted source separately.

## PNG 2x Guidance

Use PNG at 2x resolution when:

- the layout contains labels or annotations
- SVG font/layout differences are a risk
- the artifact must render identically in slides, docs, or review tools
- the chart is static and does not need interactive inspection

## WebP Guidance

Use WebP when:

- the artifact is a large raster, screenshot, heatmap, or photo-like asset
- delivery size matters more than universal editability
- the source-master is preserved separately

Avoid WebP as the only source for exact diagrams, data charts, or assets that
will need frequent edits.

## Hybrid Overlay Guidance

For hybrid visuals:

1. Generate or obtain the raster background/source layer.
2. Create exact overlays with deterministic tooling.
3. Save the overlay source separately.
4. Export a flattened delivery artifact only after source files exist.
5. Report each layer owner and final conversion path.
