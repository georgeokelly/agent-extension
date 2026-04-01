---
name: drawio
description: >-
  Generate draw.io diagrams as native .drawio files with optional PNG/SVG/PDF export
  and inline canvas preview in Cursor. Use when asked to create diagrams, flowcharts,
  architecture diagrams, ER diagrams, sequence diagrams, network diagrams, or any
  visual diagram using draw.io.
compatibility: Cross-tool (Cursor, Claude Code, Codex). Requires filesystem access. Canvas preview requires Cursor with browser tools.
metadata:
  author: georgel
  version: "1.0"
  upstream: https://github.com/jgraph/drawio-mcp
license: Apache-2.0
---

# Draw.io Diagram Skill

> **Attribution**: Adapted from [drawio-mcp](https://github.com/jgraph/drawio-mcp) (skill-cli) by JGraph Ltd, licensed under Apache-2.0.
> Original copyright: Copyright 2025 JGraph Ltd. Modified by georgel for cross-tool integration with agent-rules/agent-toolkit.

Generate draw.io diagrams as native `.drawio` files. Optionally export to PNG, SVG, or PDF with embedded diagram XML (so the exported file remains editable in draw.io). In Cursor, diagrams are previewed inline via canvas.

## Workflow

1. **Generate draw.io XML** in mxGraphModel format for the requested diagram
2. **Write the XML** to a `.drawio` file in the current working directory
3. **[Cursor] Canvas preview** — if canvas/browser tools are available, create an inline preview (see [Canvas preview](#cursor-canvas-preview))
4. **[Optional] Export** — if the user requested a format (png, svg, pdf) and draw.io CLI is available, export with `--embed-diagram`, then delete the source `.drawio` file. If CLI not found, keep `.drawio` and inform user
5. **Open the result** — the exported file if exported, or the `.drawio` file otherwise. If `open`/`xdg-open` fails or is unavailable (remote environment), print the file path

## Output format

Check the user's request for a format preference:

- `/drawio create a flowchart` → `flowchart.drawio`
- `/drawio png flowchart for login` → `login-flow.drawio.png`
- `/drawio svg: ER diagram` → `er-diagram.drawio.svg`
- `/drawio pdf architecture overview` → `architecture-overview.drawio.pdf`

If no format mentioned, write `.drawio` and preview/open it.

## XML generation rules

### IMPORTANT: XML only

Always generate XML directly. Do **not** use Mermaid, PlantUML, or CSV — these formats require server-side conversion and cannot be saved as native `.drawio` files.

### Basic structure

Every diagram must have this structure:

```xml
<mxGraphModel adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- Diagram cells go here with parent="1" -->
  </root>
</mxGraphModel>
```

- Cell `id="0"` is the root layer; cell `id="1"` is the default parent layer
- All diagram elements use `parent="1"` unless nested in a container

### CRITICAL: Edge geometry

**Every edge `mxCell` MUST contain a `<mxGeometry relative="1" as="geometry" />` child element**, even when there are no waypoints. Self-closing edge cells are invalid and will not render:

```xml
<!-- CORRECT -->
<mxCell id="e1" edge="1" parent="1" source="a" target="b" style="edgeStyle=orthogonalEdgeStyle;">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- WRONG — will not render -->
<mxCell id="e1" edge="1" parent="1" source="a" target="b" style="..." />
```

### Layout rules

- **Grid**: align all nodes to multiples of 10
- **Spacing**: ≥200px horizontal, ≥120px vertical between nodes
- **Edge style**: use `edgeStyle=orthogonalEdgeStyle` for right-angle connectors
- **Connection ports**: use `exitX`/`exitY`/`entryX`/`entryY` (0–1) to control which side of a node an edge connects to; spread connections across different sides
- **Arrowhead clearance**: ensure ≥20px straight segment before target/after source for arrowheads
- **Waypoints**: add explicit waypoints (`<Array as="points"><mxPoint x="..." y="..."/></Array>` inside mxGeometry) when edges would overlap
- **Edge labels**: do NOT wrap in HTML markup — default edge font is already 11px (smaller than vertex 12px). Just set the `value` attribute directly

### Containers

Use parent-child containment (`parent="containerId"`) for nested elements. Children use **relative coordinates** within the container.

| Type | Style | When to use |
|------|-------|-------------|
| **Group** (invisible) | `group;` | No visual border, no connections on container. Includes `pointerEvents=0` |
| **Swimlane** (titled) | `swimlane;startSize=30;` | Container needs header/border, or has its own connections |
| **Custom container** | Add `container=1;pointerEvents=0;` to any shape | Shape acting as container without own connections |

Always add `pointerEvents=0;` on containers that should not capture child connections.

### Dark mode

Set `adaptiveColors="auto"` on `<mxGraphModel>`. Colors behave as:
- Default (`strokeColor`, `fillColor`, `fontColor` unset) → adapts automatically
- Explicit color (e.g. `fillColor=#DAE8FC`) → auto-inverted for dark mode
- `light-dark(lightColor,darkColor)` → precise control over both modes

### XML well-formedness

- **NEVER** use `--` inside XML comments (illegal per XML spec)
- Escape special characters: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Use unique `id` values for each `mxCell`

Consult `references/xml-reference.md` for complete style properties, edge routing details, and container examples.

## Cursor canvas preview

**Applies only in Cursor** when canvas/browser tools are available. Claude Code and Codex skip this section.

After writing the `.drawio` file, create an inline preview:

1. Read `references/canvas-template.html` for the HTML structure
2. Construct the HTML:
   - Replace the content of `<script type="text/xml" id="diagram-data">PASTE_DIAGRAM_XML_HERE</script>` with the generated XML (paste verbatim — no escaping needed since `<script type="text/xml">` treats content as raw text; the only sequence that would break it is a literal `</script>` tag, which never appears in draw.io XML)
   - Replace `PASTE_TITLE_HERE` with a descriptive diagram title
3. Create a canvas with title `"drawio: <descriptive-name>"` and the constructed HTML as content

The canvas provides interactive zoom, pan, layer toggle, dark mode support, and an "Open in draw.io" button that generates a compressed URL for the full editor.

## draw.io CLI export

### Locating the CLI

Detect the environment, then locate the CLI:

| Environment | Detection | CLI path |
|-------------|-----------|----------|
| **WSL2** | `/proc/version` contains `microsoft` or `WSL` | `` `/mnt/c/Program Files/draw.io/draw.io.exe` `` |
| **macOS** | `uname -s` = `Darwin` | `/Applications/draw.io.app/Contents/MacOS/draw.io` |
| **Linux** | Default | `drawio` (on PATH via snap/apt/flatpak) |
| **Windows** | Native | `"C:\Program Files\draw.io\draw.io.exe"` |

Use `which drawio` to check PATH first; fall back to platform-specific path.

### Export command

```bash
drawio -x -f <format> -e -b 10 -o <output> <input.drawio>
```

Key flags:
- `-x` — export mode
- `-f` — format: `png`, `svg`, `pdf`, `jpg`
- `-e` — embed diagram XML in output (PNG, SVG, PDF only)
- `-o` — output file path
- `-b 10` — border width (recommended: 10)
- `-p <index>` — page index (0-based) for multi-page diagrams; omit for single-page

### Supported formats

| Format | Embed XML | Notes |
|--------|-----------|-------|
| `png`  | Yes (`-e`) | Viewable everywhere, editable in draw.io |
| `svg`  | Yes (`-e`) | Scalable, editable in draw.io |
| `pdf`  | Yes (`-e`) | Printable, editable in draw.io |
| `jpg`  | No | Lossy, no embedded XML support |

After successful export with `-e`, delete the intermediate `.drawio` file — the exported file contains the full editable diagram.

If draw.io CLI is not found: keep the `.drawio` file and inform the user they can install the draw.io desktop app to enable export, or open the `.drawio` file directly.

## File naming

- Use a descriptive name based on diagram content (e.g., `login-flow`, `database-schema`)
- Lowercase with hyphens for multi-word names
- For export, use double extensions: `name.drawio.png`, `name.drawio.svg`, `name.drawio.pdf` — this signals the file contains embedded diagram XML

## Opening the result

| Environment | Command |
|-------------|---------|
| macOS | `open <file>` |
| Linux (native) | `xdg-open <file>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <file>)"` |
| Remote / no display | Print file path for user to download |

## Style reference

- Complete draw.io style reference: https://www.drawio.com/doc/faq/drawio-style-reference.html
- XML Schema Definition (XSD): https://www.drawio.com/assets/mxfile.xsd

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Blank diagram | Missing root cells `id="0"` and `id="1"` | Ensure basic mxGraphModel structure is complete |
| Edges not rendering | Edge mxCell is self-closing (no child mxGeometry) | Every edge must have `<mxGeometry relative="1" as="geometry" />` |
| Export produces empty file | Invalid XML (`--` in comments, unescaped chars) | Fix XML well-formedness |
| draw.io CLI not found | Desktop app not installed | Keep `.drawio` file, inform user |
| Canvas preview blank | GraphViewer CDN failed to load | Fall back to `.drawio` file only |
