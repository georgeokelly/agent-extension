# draw.io XML Reference

> Adapted from [drawio-mcp](https://github.com/jgraph/drawio-mcp) by JGraph Ltd (Apache-2.0). Copyright 2025 JGraph Ltd. Modified by georgel.

Detailed reference for styles, edge routing, containers, layers, tags, metadata, and dark mode. Consult this when generating draw.io XML diagrams.

## General principles

- **Use proper draw.io shapes and connectors** — choose the semantically correct shape for each element (e.g., `shape=cylinder3` for databases and tanks, `rhombus` for decisions, `shape=mxgraph.pid2valves.*` for valves in P&IDs). draw.io has extensive shape libraries; prefer domain-appropriate shapes over generic rectangles.
- **Decide whether to search for shapes** — before generating a diagram, decide if it needs domain-specific shapes from draw.io's extended libraries. **Skip shape search** for standard diagram types that use basic geometric shapes: flowcharts, UML (class, sequence, state, activity), ERD, org charts, mind maps, Venn diagrams, timelines, wireframes, and any diagram using only rectangles, diamonds, circles, cylinders, and arrows. Also skip if the user explicitly asks to use basic/simple shapes. **Search for shapes** when the diagram requires industry-specific or branded icons: cloud architecture (AWS, Azure, GCP), network topology (Cisco, rack equipment), P&ID (valves, instruments, vessels), electrical/circuit diagrams, Kubernetes, BPMN with specific task types, or any domain where the user expects realistic/standardized symbols rather than labeled boxes.
- **Match the language of labels to the user's language** — if the user writes in German, French, Japanese, etc., all diagram labels, titles, and annotations should be in that same language.
- **Always include `html=1` in every `mxCell` style string.** This ensures labels render HTML tags (`<br>`, `<b>`, `<i>`) correctly. Plain text is unaffected by the flag.
- **Use `<br>` for multi-line labels** (requires `html=1`). Do NOT use `&#xa;` — it causes JSON parse errors when the XML is embedded in HTML `data-mxgraph` attributes, because the browser decodes `&#xa;` into a literal newline before JSON.parse sees it.

## Common styles

**Rounded rectangle:**
```xml
<mxCell id="2" value="Label" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

**Diamond (decision):**
```xml
<mxCell id="3" value="Condition?" style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="120" height="80" as="geometry"/>
</mxCell>
```

**Arrow (edge):**
```xml
<mxCell id="4" value="" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Labeled arrow:**
```xml
<mxCell id="5" value="Yes" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="3" target="6" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Style properties

| Property | Values | Use for |
|----------|--------|---------|
| `html=1` | 0 or 1 | Enable HTML rendering in labels — MUST be set on every cell |
| `rounded=1` | 0 or 1 | Rounded corners |
| `whiteSpace=wrap` | wrap | Text wrapping |
| `fillColor=#dae8fc` | Hex color | Background color |
| `strokeColor=#6c8ebf` | Hex color | Border color |
| `fontColor=#333333` | Hex color | Text color |
| `fontSize=14` | Number | Font size in pixels |
| `fontStyle=1` | 0=normal, 1=bold, 2=italic, 3=bold+italic | Font weight/style |
| `shape=cylinder3` | Shape name | Database cylinders |
| `shape=mxgraph.flowchart.document` | Shape name | Document shapes |
| `ellipse` | Style keyword | Circles/ovals |
| `rhombus` | Style keyword | Diamonds |
| `triangle` | Style keyword | Triangles |
| `edgeStyle=orthogonalEdgeStyle` | Style keyword | Right-angle connectors |
| `edgeStyle=elbowEdgeStyle` | Style keyword | Elbow connectors |
| `curved=1` | 0 or 1 | Curved edges |
| `dashed=1` | 0 or 1 | Dashed lines |
| `dashPattern=8 8` | Pattern | Custom dash pattern |
| `opacity=50` | 0–100 | Transparency |
| `shadow=1` | 0 or 1 | Drop shadow |
| `swimlane` | Style keyword | Swimlane containers |
| `group` | Style keyword | Invisible container (pointerEvents=0) |
| `container=1` | 0 or 1 | Enable container behavior on any shape |
| `pointerEvents=0` | 0 or 1 | Prevent container from capturing child connections |
| `collapsible=0` | 0 or 1 | Prevent container from being collapsed |

## Edge routing

**CRITICAL: Every edge `mxCell` must contain a `<mxGeometry relative="1" as="geometry" />` child element**, even when there are no waypoints. Self-closing edge cells (e.g. `<mxCell ... edge="1" ... />`) are invalid and will not render correctly. Always use the expanded form:
```xml
<mxCell id="e1" edge="1" parent="1" source="a" target="b" style="...">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**CRITICAL: The draw.io auto-router has NO obstacle avoidance.** Edges are routed using simple orthogonal paths between source and target, ignoring all intermediate nodes. If any non-source/non-target vertex lies in the path, the edge WILL cross through it. You MUST mentally verify every edge path after generating XML.

- Use `edgeStyle=orthogonalEdgeStyle` for right-angle connectors (most common)
- **Space nodes generously** — at least 60px apart, prefer 200px horizontal / 120px vertical gaps
- Use `exitX`/`exitY` and `entryX`/`entryY` (values 0–1) to control which side of a node an edge connects to. Spread connections across different sides to prevent overlap
- **Leave room for arrowheads**: ensure at least 20px of straight segment before the target and after the source
- The auto-router places bends automatically — if source and target are close or nearly aligned, a bend may be placed too close to a shape. Fix by increasing node spacing or adding explicit waypoints
- Add explicit **waypoints** when edges would overlap or cross through intermediate nodes:
  ```xml
  <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" parent="1" source="a" target="b">
    <mxGeometry relative="1" as="geometry">
      <Array as="points">
        <mxPoint x="300" y="150"/>
        <mxPoint x="300" y="250"/>
      </Array>
    </mxGeometry>
  </mxCell>
  ```
- Use `rounded=1` on edges for cleaner bends
- Use `jettySize=auto` for better port spacing on orthogonal edges
- Align all nodes to a grid (multiples of 10)

### Connection port reference

| Port | Position | Typical use |
|------|----------|-------------|
| `exitX=0.5;exitY=0` | Top center | Upward connections |
| `exitX=1;exitY=0.5` | Right center | Right-flowing connections |
| `exitX=0.5;exitY=1` | Bottom center | Downward connections |
| `exitX=0;exitY=0.5` | Left center | Left-flowing connections |
| `exitX=0;exitY=0` | Top-left corner | Diagonal connections |

Same pattern for `entryX`/`entryY` on the target side.

### Direction consistency

All edges MUST flow in a consistent primary direction (typically top-to-bottom). Never place a flow target above its source node in a top-down diagram.

- For every edge, verify `target.y >= source.y` (top-down) or `target.x >= source.x` (left-to-right)
- Decision branches go **right/down** or **left/down**, never upward
- If a decision has "skip" and "compute" outcomes, the skip path goes to the side or below, not above the diamond

### Fan-out / fan-in ports

When a node has 2+ outgoing or incoming edges on the same side, you MUST spread connection ports to prevent overlap:

| Edge count | Port positions |
|-----------|---------------|
| 2 edges | `0.25` and `0.75` |
| 3 edges | `0.25`, `0.5`, `0.75` |
| 4+ edges | Evenly distributed from `0.1` to `0.9` |

Apply `exitX`/`exitY` for fan-out and `entryX`/`entryY` for fan-in. Common patterns:

- **Fork** (1 node → 2 targets below): `exitX=0.25;exitY=1` and `exitX=0.75;exitY=1`
- **Join** (2 sources → 1 target below): `entryX=0.25;entryY=0` and `entryX=0.75;entryY=0`
- **Side fan-out** (from right side to 2 targets): `exitX=1;exitY=0.3` and `exitX=1;exitY=0.7`

### Cross-container edge routing

Cross-container edges (source and target in different containers, or one at root level) ALWAYS require explicit routing — the auto-router cannot navigate around intermediate containers:

1. **Specify exit/entry ports** (`exitX`, `exitY`, `entryX`, `entryY`) to control which side of each node the edge connects to
2. **Add explicit waypoints** to route along the canvas perimeter, bypassing all intermediate containers
3. Waypoint coordinates are **absolute** (canvas coordinates), even when source/target use relative coordinates within their parent

Standard bypass pattern: exit right → waypoint at `(canvas_right + 30, source_y)` → waypoint at `(canvas_right + 30, target_y)` → enter target from right. Mirror for left-side bypass.

```xml
<mxCell id="e1" edge="1" parent="1" source="nodeInSwimA" target="nodeInSwimC"
    style="edgeStyle=orthogonalEdgeStyle;html=1;rounded=1;exitX=1;exitY=0.5;entryX=1;entryY=0.5;">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="790" y="230"/>
      <mxPoint x="790" y="480"/>
    </Array>
  </mxGeometry>
</mxCell>
```

## Containers and groups

For architecture diagrams or any diagram with nested elements, use draw.io's proper parent-child containment — do **not** just place shapes on top of larger shapes.

### How containment works

Set `parent="containerId"` on child cells. Children use **relative coordinates** within the container.

### Container types

| Type | Style | When to use |
|------|-------|-------------|
| **Group** (invisible) | `group;` | Container has no connections and needs no visual border. Includes `pointerEvents=0` so child connections are not captured |
| **Swimlane** (titled) | `swimlane;startSize=30;` | Container needs a visible title bar/header, or the container itself has connections |
| **Custom container** | `container=1;pointerEvents=0;` added to any shape style | Any shape acting as a container without its own connections |

### Key rules

- **Always add `pointerEvents=0;`** to container styles that should not capture connections being rewired between children
- Only omit `pointerEvents=0` when the container itself needs to be connectable — use `swimlane` which handles this correctly (client area is transparent for mouse events while header remains connectable)
- Children must set `parent="containerId"` and use coordinates **relative to the container**

### Example: Architecture container with swimlane

```xml
<mxCell id="svc1" value="User Service" style="swimlane;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="300" height="200" as="geometry"/>
</mxCell>
<mxCell id="api1" value="REST API" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="svc1">
  <mxGeometry x="20" y="40" width="120" height="60" as="geometry"/>
</mxCell>
<mxCell id="db1" value="Database" style="shape=cylinder3;whiteSpace=wrap;html=1;" vertex="1" parent="svc1">
  <mxGeometry x="160" y="40" width="120" height="60" as="geometry"/>
</mxCell>
```

### Example: Invisible group container

```xml
<mxCell id="grp1" value="" style="group;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="300" height="200" as="geometry"/>
</mxCell>
<mxCell id="c1" value="Component A" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="grp1">
  <mxGeometry x="10" y="10" width="120" height="60" as="geometry"/>
</mxCell>
```

## Layers

Layers control visibility and z-order. Every cell belongs to exactly one layer. Use layers to manage diagram complexity — viewers can toggle layer visibility to show or hide groups of elements (e.g., "Physical Infrastructure" vs "Logical Network" vs "Security Zones").

Cell `id="0"` is the root and cell `id="1"` is the default layer — both always exist. Additional layers are `mxCell` elements with `parent="0"`:

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="Annotations" parent="0"/>
    <mxCell id="10" value="Server" style="rounded=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="20" value="Note: deprecated" style="text;" vertex="1" parent="2">
      <mxGeometry x="100" y="170" width="120" height="30" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

- A layer is an `mxCell` with `parent="0"` and no `vertex` or `edge` attribute
- Assign shapes to a layer by setting `parent` to the layer's id
- Later layers render on top of earlier layers (higher z-order)
- Add `visible="0"` as an attribute on the layer cell to hide it by default
- Use layers when the diagram has distinct conceptual groupings that viewers may want to toggle independently

## Tags

Tags are visual filters that let viewers show or hide elements by category. Unlike layers, a single element can have multiple tags, making tags ideal for cross-cutting concerns (e.g., tagging shapes as "critical", "v2", or "backend").

Tags require wrapping `mxCell` in an `<object>` element. Tags are assigned via the `tags` attribute as a space-separated string:

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <object id="2" label="Auth Service" tags="critical v2">
      <mxCell style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
        <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
      </mxCell>
    </object>
    <object id="3" label="Legacy API" tags="critical deprecated">
      <mxCell style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
        <mxGeometry x="300" y="100" width="120" height="60" as="geometry"/>
      </mxCell>
    </object>
  </root>
</mxGraphModel>
```

- Tags require the `<object>` wrapper — a plain `mxCell` cannot have tags
- The `label` attribute on `<object>` replaces `value` on `mxCell`
- Tags are space-separated in the `tags` attribute
- Viewers filter the diagram by selecting tags in the draw.io UI (Edit > Tags)
- Tags do not affect z-order or structural grouping — they are purely a visibility filter

## Metadata and placeholders

Metadata stores custom key-value properties on shapes as additional attributes on the `<object>` wrapper element. Combined with placeholders, metadata values can be displayed in labels — useful for data-driven diagrams showing status, owner, IP addresses, or versions on each shape.

Set `placeholders="1"` on the `<object>` to enable `%propertyName%` substitution in the `label`:

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <object id="2" label="&lt;b&gt;%component%&lt;/b&gt;&lt;br&gt;Owner: %owner%&lt;br&gt;Status: %status%"
            placeholders="1" component="Auth Service" owner="Team Backend" status="Active">
      <mxCell style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
        <mxGeometry x="100" y="100" width="160" height="80" as="geometry"/>
      </mxCell>
    </object>
  </root>
</mxGraphModel>
```

- Custom properties are plain XML attributes on `<object>` (e.g., `component="Auth Service"`)
- Set `placeholders="1"` to enable `%key%` substitution in the label and tooltip
- The label must use `html=1` style when using HTML formatting with placeholders
- Placeholders resolve by walking up the containment hierarchy: shape → parent container → layer → root (first match wins)
- Predefined placeholders (work without custom properties): `%id%`, `%width%`, `%height%`, `%date%`, `%time%`, `%timestamp%`, `%page%`, `%pagenumber%`, `%pagecount%`, `%filename%`
- Use `%%` for a literal percent sign in labels
- Tags, metadata, and placeholders can all be combined on the same `<object>` element

## Color palettes

Common draw.io color combinations (fill / stroke):

| Theme | Fill | Stroke | Use for |
|-------|------|--------|---------|
| Blue | `#dae8fc` | `#6c8ebf` | Default, general-purpose |
| Green | `#d5e8d4` | `#82b366` | Success, approved, active |
| Orange | `#ffe6cc` | `#d6b656` | Warning, pending |
| Red | `#f8cecc` | `#b85450` | Error, critical, denied |
| Purple | `#e1d5e7` | `#9673a6` | External, third-party |
| Grey | `#f5f5f5` | `#666666` | Disabled, background |
| Yellow | `#fff2cc` | `#d6b656` | Highlight, notes |

## Dark mode colors

draw.io supports automatic dark mode rendering. How colors behave depends on the property:

- **`strokeColor`, `fillColor`, `fontColor`** default to `"default"`, which renders as black in light theme and white in dark theme. When no explicit color is set, colors adapt automatically.
- **Explicit colors** (e.g. `fillColor=#DAE8FC`) specify the light-mode color. The dark-mode color is computed automatically by inverting the RGB values (blending toward the inverse at 93%) and rotating the hue by 180° (via `mxUtils.getInverseColor`).
- **`light-dark()` function** — to specify both colors explicitly, use `light-dark(lightColor,darkColor)` in the style string, e.g. `fontColor=light-dark(#7EA6E0,#FF0000)`. The first argument is used in light mode, the second in dark mode.

To enable dark mode color adaptation, the `mxGraphModel` element must include `adaptiveColors="auto"`.

When generating diagrams, you generally do not need to specify dark-mode colors — the automatic inversion handles most cases. Use `light-dark()` only when the automatic inverse color is unsatisfactory.

## Multi-page diagrams

Use `<diagram>` elements inside `<mxfile>` for multiple pages:

```xml
<mxfile>
  <diagram name="Overview">
    <mxGraphModel adaptiveColors="auto">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <!-- Page 1 cells -->
      </root>
    </mxGraphModel>
  </diagram>
  <diagram name="Detail">
    <mxGraphModel adaptiveColors="auto">
      <root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <!-- Page 2 cells -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

For single-page diagrams, the bare `<mxGraphModel>` format (without `<mxfile>` wrapper) is preferred for simplicity.

## HTML embedding reference

When embedding draw.io diagrams in HTML pages, the GraphViewer library renders `<div>` elements with a `data-mxgraph` attribute containing a JSON configuration object.

### Viewer script

```html
<script src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
```

After the script loads, call `GraphViewer.processElements()` to render all `data-mxgraph` divs on the page. For dynamic DOM insertion (SPAs), call this manually after adding the div.

Set `GraphViewer.darkBackgroundColor = getComputedStyle(document.body).backgroundColor` before `processElements()` to enable automatic dark mode detection.

### `data-mxgraph` configuration options

Source: [drawio.com/doc/faq/embed-html-options](https://www.drawio.com/doc/faq/embed-html-options)

#### Data source

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `xml` | XML string | — | Inline diagram XML. Use this for agent-generated diagrams |
| `url` | URL string | — | Public URL to load diagram from. **Takes precedence over `xml`** — do not set both |

#### Display

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `zoom` | number | `1` | Initial zoom level |
| `border` | number | `8` | Padding around diagram in pixels |
| `center` | boolean | `false` | Center diagram in container |
| `max-height` | number | — | Maximum initial height of diagram container |
| `auto-fit` | boolean | `true` | Auto-zoom to fit container. Set `false` to preserve 1:1 scale |
| `allow-zoom-in` | boolean | `false` | Allow zoom level > 1 |
| `resize` | boolean | — | Container resizes after changes (layer toggle, page switch) |
| `check-visible-state` | boolean | `true` | Delayed rendering for hidden containers. Set `false` for tabs/accordions |

#### Toolbar

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `toolbar` | space-separated tokens | — | Toolbar buttons: `pages`, `zoom`, `layers`, `lightbox`, `custom` |
| `toolbar-nohide` | boolean | `false` | Always show toolbar (default: show on hover) |
| `toolbar-position` | `top` / `inline` / `bottom` | `top` | Toolbar placement |
| `toolbar-buttons` | object | — | Custom button definitions: `{key: {title, image, handler}}` |
| `title` | string | — | Toolbar title or tooltip if no toolbar visible |

#### Interaction

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `nav` | boolean | `true` | Enable collapse/expand navigation |
| `lightbox` | `false` / `open` | — | Disable lightbox or force open in new window |
| `editable` | boolean | `true` | Allow editing from lightbox. Set `false` for read-only embeds |
| `edit` | URL / `_blank` | — | Custom edit link in lightbox. `_blank` opens a copy in draw.io |
| `target` | `self` / `blank` | auto | Link target behavior |
| `highlight` | hex color | — | Border highlight color for shapes with links |
| `tooltips` | boolean | `true` | Show tooltips on hover |

#### Multi-page

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `page` | number | `0` | Initial page index (0-based) |

Include `pages` in `toolbar` to show the page switcher. Source XML must use the `<mxfile><diagram>...</diagram></mxfile>` wrapper.

#### Dark mode

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `dark-mode` | `auto` / `dark` / `light` | — | Diagram appearance. `auto` follows system theme |

Complement with CSS `html { color-scheme: light dark; }` for page chrome adaptation.

#### Layers

| Key | Values | Default | Description |
|-----|--------|---------|-------------|
| `layers` | space-separated indices | all visible | Initially visible layers (e.g. `0 1 3`) |
| `auto-crop` | boolean | `false` | Auto-crop diagram when toggling layers |

### Recommended XML delivery pattern

Always store XML in a `<script type="text/xml">` sidecar element and build the `data-mxgraph` attribute at runtime via `JSON.stringify`. This avoids the double-encoding trap (XML → JSON → HTML attribute) that causes silent rendering failures:

```html
<script type="text/xml" id="diagram-data">
  <!-- paste raw XML here — no escaping needed -->
</script>
<script>
  var xml = document.getElementById('diagram-data').textContent;
  div.setAttribute('data-mxgraph', JSON.stringify({ xml: xml, ... }));
  GraphViewer.processElements();
</script>
```

## Style reference

- Complete draw.io style reference: https://github.com/jgraph/drawio-mcp/blob/main/shared/style-reference.md
- XML Schema Definition (XSD): https://github.com/jgraph/drawio-mcp/blob/main/shared/mxfile.xsd

## CRITICAL: XML well-formedness

When generating draw.io XML, the output **must** be well-formed XML:
- **NEVER include ANY XML comments (`<!-- ... -->`) in the output.** XML comments are strictly forbidden — they waste tokens, can cause parse errors, and serve no purpose in diagram XML.
- Escape special characters in attribute values: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Always use unique `id` values for each `mxCell`
