# Handoff Spec

Use this when the current agent can plan a visual artifact but cannot execute
the required owner skill or generator.

## Consumer Model

| Case | Consumer | Output |
| --- | --- | --- |
| Current agent can execute | Current agent calls the owning skill/tool directly. | Source and delivery artifacts. |
| Current agent can delegate | Child agent or agent CLI receives the handoff spec. | Child result with files, commands, and limits. |
| Current agent cannot execute | User or next agent receives the handoff YAML. | A portable request to run elsewhere. |

## YAML Shape

```yaml
visual_artifact_request:
  intent: "What the visual must communicate"
  profile: "technical-diagram | data-chart | benchmark-chart | hybrid-diagram | ai-background | large-raster | cutout-sprite | logo-icon"
  owner:
    primary: "visualize-data | drawio | imagegen | deterministic-renderer | user"
    secondary:
      - "optional second owner for hybrid layers"
  source_of_truth:
    required: true
    expected_files:
      - "path or description of editable/reproducible source"
  delivery:
    formats:
      - "svg | png | webp | pdf | html"
    exact_size: "optional WIDTHxHEIGHT"
    scale: "optional 2x or other scale"
    transparency: "none | alpha-required | alpha-preferred"
  layers:
    - name: "background"
      owner: "imagegen"
      requirements: "AI raster background, no text"
    - name: "overlay"
      owner: "deterministic-renderer"
      requirements: "exact labels, arrows, nodes"
  constraints:
    must:
      - "preserve source artifact"
    must_not:
      - "duplicate neighboring skill internals"
  runtime:
    current_limit: "why the current agent cannot execute"
    suggested_tool: "tool, skill, or agent CLI to use"
  output_contract:
    report:
      - "source files"
      - "delivery files"
      - "conversion commands"
      - "known limits"
```

## Required Fields

- `intent`
- `profile`
- `owner.primary`
- `source_of_truth.required`
- `delivery.formats`
- `constraints.must_not`
- `output_contract.report`

Every list-typed required field above (`delivery.formats`, `constraints.must_not`,
`output_contract.report`) MUST contain at least one non-empty entry; an empty
list does not satisfy the requirement.

## Handoff Rules

- Keep handoff bounded. Name the owner and what it should produce.
- For data-backed charts, do not include chart type decisions unless they came
  from `visualize-data`.
- For AI raster, do not restate `imagegen internals` (see SKILL.md Boundary
  Contract); ask `imagegen` to use its current workflow.
- For hybrid artifacts, list layers and owners separately.
- Include no secrets, API keys, or local auth assumptions.
- Include destination paths only when the receiving runtime can write there.
- State whether the result is preview-only or project-bound.

## Example: Hybrid Diagram Background

```yaml
visual_artifact_request:
  intent: "Create a visual background for a pipeline diagram while preserving exact labels in an overlay."
  profile: "hybrid-diagram"
  owner:
    primary: "imagegen"
    secondary:
      - "deterministic-renderer"
  source_of_truth:
    required: true
    expected_files:
      - "background source raster"
      - "overlay SVG or HTML source"
  delivery:
    formats:
      - "png"
      - "webp"
    exact_size: "1920x1080"
    transparency: "none"
  layers:
    - name: "background"
      owner: "imagegen"
      requirements: "abstract system atmosphere, no text, no labels, no arrows"
    - name: "overlay"
      owner: "deterministic-renderer"
      requirements: "exact node labels, arrows, and layout"
  constraints:
    must:
      - "save source raster and overlay source separately"
    must_not:
      - "put exact labels in the AI-generated raster"
  runtime:
    current_limit: "current agent cannot call image generation"
    suggested_tool: "agent with imagegen"
  output_contract:
    report:
      - "background source path"
      - "overlay source path"
      - "flattened delivery path"
      - "conversion commands"
```
