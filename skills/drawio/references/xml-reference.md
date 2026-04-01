# draw.io XML Reference

> Adapted from [drawio-mcp](https://github.com/jgraph/drawio-mcp) by JGraph Ltd (Apache-2.0). Copyright 2025 JGraph Ltd. Modified by georgel.

Detailed reference for styles, edge routing, and containers. Consult this when generating complex diagrams.

## Common styles

**Rounded rectangle:**
```xml
<mxCell id="2" value="Label" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
</mxCell>
```

**Diamond (decision):**
```xml
<mxCell id="3" value="Condition?" style="rhombus;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="120" height="80" as="geometry"/>
</mxCell>
```

**Arrow (edge):**
```xml
<mxCell id="4" value="" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="2" target="3" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Labeled arrow:**
```xml
<mxCell id="5" value="Yes" style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="3" target="6" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

## Style properties

| Property | Values | Use for |
|----------|--------|---------|
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

draw.io does **not** have built-in collision detection for edges. Plan layout and routing carefully:

- Use `edgeStyle=orthogonalEdgeStyle` for right-angle connectors (most common)
- **Space nodes generously** — at least 60px apart, prefer 200px horizontal / 120px vertical gaps
- Use `exitX`/`exitY` and `entryX`/`entryY` (values 0–1) to control which side of a node an edge connects to. Spread connections across different sides to prevent overlap
- **Leave room for arrowheads**: The final straight segment must be long enough to fit the arrowhead (default size 6, configurable via `startSize`/`endSize`). If the final segment is too short, the arrowhead overlaps the bend. Ensure at least 20px of straight segment before the target and after the source
- When using `orthogonalEdgeStyle`, the auto-router places bends automatically — if source and target are close or nearly aligned, the router may place a bend too close to a shape. Fix by increasing node spacing or adding explicit waypoints
- Add explicit **waypoints** when edges would overlap:
  ```xml
  <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="a" target="b">
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
<mxCell id="svc1" value="User Service" style="swimlane;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="300" height="200" as="geometry"/>
</mxCell>
<mxCell id="api1" value="REST API" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="svc1">
  <mxGeometry x="20" y="40" width="120" height="60" as="geometry"/>
</mxCell>
<mxCell id="db1" value="Database" style="shape=cylinder3;whiteSpace=wrap;" vertex="1" parent="svc1">
  <mxGeometry x="160" y="40" width="120" height="60" as="geometry"/>
</mxCell>
```

### Example: Invisible group container

```xml
<mxCell id="grp1" value="" style="group;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="300" height="200" as="geometry"/>
</mxCell>
<mxCell id="c1" value="Component A" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="grp1">
  <mxGeometry x="10" y="10" width="120" height="60" as="geometry"/>
</mxCell>
```

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
