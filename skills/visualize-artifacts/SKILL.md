---
name: visualize-artifacts
description: >-
  Decide owners, source-of-truth, output format, and handoff for project
  visual artifacts spanning data charts, structural diagrams, AI raster
  assets, screenshots, and hybrid raster-plus-overlay workflows.
---

# Visualize Artifacts

Route project visual work to the correct owner and preserve both source
artifacts and delivery artifacts. This skill is a policy and handoff layer; it
does not generate charts, draw native diagrams, or create AI raster images by
itself. Do not invoke as a substitute for data analysis (`visualize-data`),
draw.io diagram construction (`drawio`), or AI raster image generation
(`imagegen`).

## Workflow

1. **Classify the request**
   - Data-backed visual or benchmark chart
   - Structural diagram or workflow
   - AI raster asset
   - Hybrid raster plus deterministic overlay
   - Format/package-only request
   - Runtime cannot perform the needed generation
2. **Choose the owner**
   - Use the Boundary Contract below first.
   - Read [profiles.md](references/profiles.md) when the request needs a
     profile-specific source/delivery decision.
   - Read [execution-paths.md](references/execution-paths.md) when runtime
     capability or agent handoff matters.
   - Read [format-policy.md](references/format-policy.md) when exact format,
     size, raster/vector, or source-master policy matters.
   - Read [handoff-spec.md](references/handoff-spec.md) when the current agent
     cannot execute the needed generation step.
3. **Preserve source-of-truth**
   - Name the editable/source artifact separately from the final delivery
     artifact.
   - Prefer deterministic source formats for exact text, arrows, nodes, plots,
     or data-backed content.
   - Use AI raster only where approximate bitmap generation is appropriate.
4. **Handoff or execute**
   - If the current runtime has the needed tool or skill, route directly.
   - If another agent/CLI has the needed tool, produce a bounded handoff.
   - If no agent can execute, return the handoff spec and tool requirements.
5. **Report outputs**
   - State the owner used for each layer or artifact.
   - State source file(s), delivery file(s), conversions, and unresolved limits.

## Boundary Contract

`imagegen internals` in this contract means: prompt taxonomy, model choice /
fallback rules, and transparency workflow. The same definition is referenced
from the other reference files.

| Area | `visualize-data` owns | `drawio` owns | `imagegen` owns | `visualize-artifacts` owns | `visualize-artifacts` must not do |
| --- | --- | --- | --- | --- | --- |
| Data-backed charts | Dataset loading, profiling, EDA, chart intent classification, chart type recommendation, Python plotting, dashboards, benchmark chart rendering. | None. | None, unless the user explicitly wants an AI raster illustration rather than a data-faithful chart. | Delivery policy for chart artifacts: source-of-truth, export format, 2x PNG/SVG/WebP/PDF packaging, and handoff to `visualize-data`. | Pick chart types from data, interpret datasets, write plotting code, or duplicate `visualize-data` examples/tables. |
| Structural diagrams | None. | Native editable `.drawio` / mxGraph source and draw.io exports with embedded diagram data. | None, unless an explicitly raster mood/concept image is requested. | Pick the right deterministic carrier — route to `drawio` when native editability is required; allow Mermaid/SVG/HTML/slides otherwise — and own delivery packaging. | Redraw exact diagrams here, bundle a draw.io engine, or treat AI raster as the primary source for labelled structural visuals. |
| AI raster assets | None, except data-derived plots that should not be generated as approximate imagery. | None. | Bitmap generation/editing, stylized backgrounds, raster mockups, sprites, cutouts, image variants, plus all `imagegen internals`. | Decide when AI raster is appropriate, request shape, final artifact packaging, post-processing expectations, and handoff when current runtime cannot call image generation. | Restate any `imagegen internals` or implement raster generation/editing here. |
| Hybrid visuals | Data layers remain with `visualize-data` when data-backed. | Exact overlay layer when native editable diagram source is required. | Raster layer generation/editing when an AI image is part of the hybrid. | A hybrid manifest: which layer/tool owns each piece, source/delivery artifact list, deterministic overlay requirement, and composition handoff. | Own exact overlay rendering, redraw structural diagrams, or merge all hybrid work into a single approximate raster. |
| Format/package decisions | Produces source chart artifacts when data-driven. | Produces `.drawio` source and draw.io exports as deterministic diagram carriers. | Produces source raster assets when AI generation is appropriate. | Cross-skill source-master versus delivery-artifact policy, exact size/format via deterministic conversion, and reporting conventions. | Promise exact built-in `image_gen` size/format controls or bundle renderer/post-processing scripts. |

## Routing Rules

- Route requests to analyze data, inspect distributions, choose chart types,
  generate plots, perform EDA, or build dashboards to `visualize-data`.
- Route requests for native editable draw.io diagrams, mxGraph source, or
  draw.io exports with embedded diagram data to `drawio`.
- Route AI raster creation or editing to `imagegen` when the runtime exposes
  built-in image generation or an explicitly configured fallback.
- Keep Mermaid, SVG, HTML, Slides, or code-native diagrams available for
  deterministic structural visuals when native draw.io editability is not
  required.
- For hybrid workflows, produce a layer manifest. Name the owner for each layer
  and use deterministic overlays for exact labels, arrows, nodes, and layout.
  When elaborating the plan, consult `references/profiles.md` →
  `references/format-policy.md` → `references/handoff-spec.md` in that order.
- Never route the same decision back to `visualize-artifacts` after a downstream
  owner has been chosen.

## Output Convention

For each visual deliverable, report:

- **Intent**: what the user needs the visual to communicate.
- **Owner**: `visualize-data`, `drawio`, `imagegen`, deterministic renderer,
  or external handoff.
- **Source artifact**: editable or reproducible source file.
- **Delivery artifact**: final file format and size/quality expectation.
- **Conversions**: deterministic post-processing needed, if any.
- **Limits**: runtime gaps, missing tools, or precision risks.

## Examples

| Request | Owner | Source artifact | Delivery artifact | Notes |
| --- | --- | --- | --- | --- |
| "Render a benchmark chart from this CSV" | `visualize-data` | Dataset + plotting source | SVG (preferred) or 2x PNG | This skill only sets export packaging; chart selection stays with `visualize-data`. |
| "Editable architecture diagram" | `drawio` | `.drawio` mxGraph source | SVG / PNG / PDF export | Routed to `drawio` when native editability is required; otherwise allow Mermaid / SVG / HTML / slides. |
| "Hybrid diagram with AI background and labelled overlay" | `imagegen` (raster) + deterministic renderer or `drawio` (overlay) | Raster source + overlay source, kept separate | Flattened PNG / WebP plus retained editable overlay | Layer manifest required; never bake exact labels into the AI raster. |
| "Convert this PNG chart to WebP at 1600x900" | deterministic renderer (post-process) | Original chart source (do not flatten) | WebP at requested size | Format/package-only request; preserve source-master. |
| "Transparent product sprite" | `imagegen` | Generated raster source with alpha | Alpha PNG / WebP | Transparency workflow stays inside `imagegen`; this skill only requests and packages output. |

## Skill Maintenance

Do not create auxiliary README, installation, quick-reference, changelog, or
script files for this skill.
