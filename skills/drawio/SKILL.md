---
# Frontmatter fields follow the agentskills.io specification (https://agentskills.io/specification).
# Cross-tool: Cursor, Claude Code, and Codex all parse name + description.
# Codex constraints (as of rust-v0.118.0): name ≤64 chars kebab-case, description ≤1024 chars.
# CC-specific fields (when_to_use, etc.) are ignored by Cursor/Codex; Codex-unknown fields are ignored by CC.
name: drawio
description: >-
  Generate draw.io diagrams as native .drawio files with optional PNG/SVG/PDF export
  and inline canvas preview in Cursor. Use when asked to create diagrams, flowcharts,
  architecture diagrams, ER diagrams, sequence diagrams, network diagrams, or any
  visual diagram using draw.io.
when_to_use: >-
  Use when the user asks to create diagrams, flowcharts, architecture diagrams,
  ER diagrams, sequence diagrams, network diagrams, or any visual diagram.
argument-hint: "[format] diagram description"
compatibility: Cross-tool (Cursor, Claude Code, Codex). Requires filesystem access. Canvas preview requires Cursor with browser tools.
metadata:
  author: georgel
  version: "1.4"
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

- **`html=1` required**: Always include `html=1` in every `mxCell` style string. This ensures labels render HTML tags (`<br>`, `<b>`, `<i>`) correctly; plain text is unaffected
- **Line breaks**: Use `<br>` (with `html=1`) for multi-line labels — NOT `&#xa;`. `&#xa;` causes JSON parse errors when XML is embedded in HTML `data-mxgraph` attributes
- **Grid**: align all nodes to multiples of 10
- **Spacing**: ≥200px horizontal, ≥120px vertical between nodes
- **Edge style**: use `edgeStyle=orthogonalEdgeStyle` for right-angle connectors
- **Connection ports**: use `exitX`/`exitY`/`entryX`/`entryY` (0–1) to control which side of a node an edge connects to; spread connections across different sides
- **Arrowhead clearance**: ensure ≥20px straight segment before target/after source for arrowheads
- **Waypoints**: add explicit waypoints (`<Array as="points"><mxPoint x="..." y="..."/></Array>` inside mxGeometry) when edges would overlap or cross through nodes
- **Edge labels**: do NOT wrap in HTML markup — default edge font is already 11px (smaller than vertex 12px). Just set the `value` attribute directly

#### Edge routing fundamentals

**The draw.io auto-router has NO obstacle avoidance.** Edges are routed using simple orthogonal paths between source and target, ignoring all intermediate nodes. If any non-source/non-target vertex lies in the path, the edge WILL cross through it.

- **MUST manually verify every edge path** after generating XML. For each edge, mentally trace the orthogonal route and check if any intermediate node would be crossed — add waypoints to route around it
- **Direction consistency**: All edges MUST flow in a consistent primary direction (typically top-to-bottom). Never place a flow target above its source. For every edge, verify `target.y >= source.y` (top-down) or `target.x >= source.x` (left-to-right). Decision branches go right/down or left/down, never upward

#### Fan-out / fan-in ports

When a node has 2+ outgoing or incoming edges, MUST spread connection ports to prevent overlap:

| Edge count | Port positions |
|-----------|---------------|
| 2 edges | `0.25` and `0.75` |
| 3 edges | `0.25`, `0.5`, `0.75` |
| 4+ edges | Evenly distributed from `0.1` to `0.9` |

Common patterns: Fork (1→2 below) uses `exitX=0.25;exitY=1` and `exitX=0.75;exitY=1`. Join (2→1 below) uses `entryX=0.25;entryY=0` and `entryX=0.75;entryY=0`.

#### No orphan elements

Every visible element MUST have at least one edge connecting it to the diagram flow. Floating annotations should use a dashed edge (`dashed=1;endArrow=open;endFill=0`).

### Containers

Use parent-child containment (`parent="containerId"`) for nested elements. Children use **relative coordinates** within the container.

| Type | Style | When to use |
|------|-------|-------------|
| **Group** (invisible) | `group;` | No visual border, no connections on container. Includes `pointerEvents=0` |
| **Swimlane** (titled) | `swimlane;startSize=30;` | Container needs header/border, or has its own connections |
| **Custom container** | Add `container=1;pointerEvents=0;` to any shape | Shape acting as container without own connections |

Always add `pointerEvents=0;` on containers that should not capture child connections.

#### Cross-container edge routing

Cross-container edges (source and target in different containers) ALWAYS require explicit routing — the auto-router cannot navigate around intermediate containers:

1. **Specify exit/entry ports** (`exitX`, `exitY`, `entryX`, `entryY`) to control which side of each node the edge connects to
2. **Add explicit waypoints** to route along the canvas perimeter, bypassing all intermediate containers
3. Waypoint coordinates are **absolute** (canvas coordinates), even when source/target use relative coordinates within their parent

Standard bypass pattern: exit right → waypoint at `(canvas_right + 30, source_y)` → waypoint at `(canvas_right + 30, target_y)` → enter target from right. Mirror for left-side bypass.

### Dark mode

Set `adaptiveColors="auto"` on `<mxGraphModel>`. Colors behave as:
- Default (`strokeColor`, `fillColor`, `fontColor` unset) → adapts automatically
- Explicit color (e.g. `fillColor=#DAE8FC`) → auto-inverted for dark mode
- `light-dark(lightColor,darkColor)` → precise control over both modes

### XML well-formedness

- **NEVER include ANY XML comments (`<!-- ... -->`) in the output.** XML comments are strictly forbidden — they waste tokens, can cause parse errors, and serve no purpose in diagram XML.
- Escape special characters in attribute values: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Always use unique `id` values for each `mxCell`

### Post-generation verification

Verify before outputting XML:

1. **`html=1`** present in every `mxCell` style
2. **`<br>`** used for line breaks (not `&#xa;`)
3. **No backward edges**: For every edge, `target.y >= source.y` (top-down) or `target.x >= source.x` (left-to-right)
4. **No edge-through-vertex**: Trace every edge's orthogonal path — no intermediate node crossed; add waypoints if needed
5. **Fan-out/fan-in ports**: Any node with 2+ edges on the same side has spread `exitX`/`entryX` values
6. **No orphan elements**: Every visible node has at least one connecting edge
7. **Cross-container edges**: All edges between different containers have explicit exit/entry ports and waypoints

Consult `references/xml-reference.md` for complete style properties, edge routing details, and container examples.

## HTML embedding

Embed generated diagrams in HTML pages for interactive display (zoom, pan, layers, dark mode) without installing draw.io. This works in any modern browser.

### Embedding modes

| Mode | Mechanism | Interactivity | Use case |
|------|-----------|---------------|----------|
| **HTML viewer** (this section) | `data-mxgraph` + GraphViewer CDN | Zoom, pan, layers, lightbox | Documentation, dashboards, reports |
| **IFrame** | `<iframe src="https://viewer.diagrams.net/...">` | Same as viewer | Quick embed, strict CSP environments |
| **Embedded editor** | `embed=1` + postMessage protocol | Full editing | Collaborative apps |
| **Static image** | SVG/PNG export | None | Email, PDF, universal compatibility |

This section covers the **HTML viewer** approach — the recommended default for interactive embedding.

### Quick start

Use `references/embed-template.html` as the base template. Populate it by replacing:
- `PASTE_DIAGRAM_XML_HERE` with the generated draw.io XML (paste verbatim — no escaping needed inside `<script type="text/xml">`)
- `PASTE_TITLE_HERE` with a descriptive title

The template automatically:
- Loads the viewer from the diagrams.net CDN with async loading and timeout fallback
- Detects multi-page diagrams and adds the page switcher toolbar
- Supports dark mode via `color-scheme` and `dark-mode: auto`
- Scales responsively to container width

### Recommended `data-mxgraph` defaults

The template constructs the `data-mxgraph` JSON at runtime via `JSON.stringify` (avoiding the double-encoding trap of hand-writing JSON inside an HTML attribute). Recommended baseline:

| Key | Default | Rationale |
|-----|---------|-----------|
| `xml` | *(required)* | Always inline — never use `url` for agent-generated diagrams (avoids CORS and network dependency) |
| `toolbar` | `"zoom layers lightbox"` | Core interactive controls; add `pages` for multi-page diagrams |
| `nav` | `true` | Collapse/expand for complex diagrams |
| `center` | `true` | Better visual presentation |
| `editable` | `false` | Read-only by default — prevents unexpected editor popups |
| `border` | `8` | Padding around diagram |
| `highlight` | `"#0000ff"` | Visual feedback for linked shapes |
| `dark-mode` | `"auto"` | Respects system theme preference |

### Optional configuration

See `references/xml-reference.md` for the complete `data-mxgraph` options reference. Common optional settings:

| Option | When to use |
|--------|-------------|
| `page=N` | Set initial page for multi-page diagrams (0-based) |
| `layers=[0 1 ...]` | Show only specific layers on load |
| `max-height=600` | Constrain height in documentation/blog layouts |
| `allow-zoom-in=true` | Permit zoom beyond 100% for fine-detail diagrams |
| `toolbar-nohide=true` | Always show toolbar (default: show on hover) |
| `toolbar-position=bottom` | Move toolbar below diagram |
| `lightbox=open` | Click opens full-screen lightbox |
| `auto-crop=true` | Auto-crop when toggling layers |

### Dark mode

Dark mode involves two independent layers:

1. **Diagram layer**: `adaptiveColors="auto"` on `<mxGraphModel>` — draw.io auto-inverts colors. No extra work needed if the XML generation rules are followed
2. **Page chrome layer**: CSS `html { color-scheme: light dark; }` adapts browser UI. The viewer reads `dark-mode: auto` and calls `GraphViewer.darkBackgroundColor` to detect the page background

Both layers are handled automatically by the template.

### Responsive sizing and pan

The template uses `width: 100%; max-width: 100%` on the `.mxgraph` container with `max-height: 80vh` and `overflow: auto`. Key rules:

- **`max-height`** constrains the container so zoom-in produces scrollable overflow instead of expanding the page
- **Drag-to-pan**: the template includes a mousedown/mousemove handler — grab and drag to scroll the zoomed diagram (`cursor: grab` → `grabbing`)
- **Do NOT use `resize: true`** — it makes the container grow with zoom, preventing pan entirely
- **`<meta name="viewport">`** is included in the template for mobile responsiveness

### CDN and offline

The viewer is loaded from `https://viewer.diagrams.net/js/viewer-static.min.js` (~200KB). The template handles failure gracefully:

- **Timeout**: 8-second async load with fallback message if CDN is unreachable
- **`onerror`**: immediate fallback on script load failure
- **Fallback content**: message with link to open draw.io and instructions to paste XML or open the `.drawio` file directly

For environments with strict Content Security Policy, add to CSP headers:

```
script-src 'self' https://viewer.diagrams.net;
```

For fully offline/air-gapped environments, the viewer JS can be self-hosted — download `viewer-static.min.js` and serve it locally.

### Multi-page diagrams

The template auto-detects multi-page diagrams (multiple `<diagram>` elements inside `<mxfile>`) and adds the `pages` toolbar button automatically. Use `page=N` (0-based) in the config to set the initial page.

### Gotchas

| Gotcha | Detail |
|--------|--------|
| `url` overrides `xml` | If both are set, `url` takes precedence — the inline XML is silently ignored |
| `tags` not officially documented | Not in the official `toolbar` token list; use only if diagram has tags and you have verified it works |
| `pako` is optional | Only needed for "Open in draw.io" URL generation; not required for viewer rendering |
| Large XML in attributes | Browsers may truncate HTML attributes >64KB; always use the `<script type="text/xml">` sidecar pattern instead |
| SPA integration | After dynamic DOM insertion, call `GraphViewer.processElements()` manually |
| Hidden containers | Diagrams in tabs/accordions need `check-visible-state=false` or re-render on show |

## [Cursor-only] Canvas preview

> This section extends the [HTML embedding](#html-embedding) approach with Cursor-specific canvas integration. **Skip if not running in Cursor.** Claude Code and Codex skip this step.

After writing the `.drawio` file, create an inline preview:

1. Read `references/canvas-template.html` for the HTML structure (this is a Cursor-enhanced variant of `embed-template.html` with "Copy XML" and "Open in draw.io" buttons)
2. Construct the HTML:
   - Replace the content of `<script type="text/xml" id="diagram-data">PASTE_DIAGRAM_XML_HERE</script>` with the generated XML (paste verbatim — no escaping needed since `<script type="text/xml">` treats content as raw text; the only sequence that would break it is a literal `</script>` tag, which never appears in draw.io XML)
   - Replace `PASTE_TITLE_HERE` with a descriptive diagram title
3. Create a canvas with title `"drawio: <descriptive-name>"` and the constructed HTML as content

The canvas provides interactive zoom, pan, layer toggle, dark mode support, and an "Open in draw.io" button that generates a compressed URL for the full editor.

## draw.io CLI export

### Locating the CLI

First, detect the environment, then locate the CLI:

| Environment | Detection | CLI path |
|-------------|-----------|----------|
| **macOS** | `uname -s` = `Darwin` | `/Applications/draw.io.app/Contents/MacOS/draw.io` |
| **Linux (desktop)** | X11/Wayland available | `drawio` (on PATH via snap/apt/flatpak) |
| **Linux (headless)** | No display (remote server) | `gl-drawio` — Docker-based headless exporter (see below) |
| **WSL2** | `/proc/version` contains `microsoft` or `WSL` | `` `/mnt/c/Program Files/draw.io/draw.io.exe` `` |
| **Windows** | Native | `"C:\Program Files\draw.io\draw.io.exe"` |

Use `which drawio` (or `where drawio` on Windows) to check PATH first; fall back to platform-specific path.

#### WSL2 details

Detect WSL2:

```bash
grep -qi microsoft /proc/version 2>/dev/null && echo "WSL2"
```

If draw.io is installed in a non-default location, check per-user install:

```bash
# Default install path
`/mnt/c/Program Files/draw.io/draw.io.exe`
# Per-user install (if the above does not exist)
`/mnt/c/Users/$WIN_USER/AppData/Local/Programs/draw.io/draw.io.exe`
```

The backtick quoting handles the space in `Program Files` in bash.

#### Linux headless: `gl-drawio`

On headless Linux servers (no X11/Wayland), the native `drawio` CLI cannot run. Use `gl-drawio` instead — it runs drawio inside a Docker container with xvfb:

```bash
gl-drawio [options] <input.drawio> [input2.drawio ...]
```

Key flags:
- `-f`, `--format` — output format: `svg` (default), `png`, `pdf`, `jpg`
- `-s`, `--scale` — scale factor (e.g. `1.5`, `2`)
- `-p`, `--page` — page index (0-based); default: all pages
- `-t`, `--transparent` — transparent background
- `-o`, `--outdir` — output directory (default: same dir as input)
- `--crop` — crop to diagram bounds (PDF only)

Output naming: `<stem>-<PageName>.<format>` (or `<stem>.<format>` for single-page files).

Requires Docker daemon access. The underlying image is `rlespinasse/drawio-export:latest`.

### Export command

#### macOS / Linux desktop / Windows / WSL2

```bash
drawio -x -f <format> -e -b 10 -o <output> <input.drawio>
```

Key flags:
- `-x` / `--export` — export mode
- `-f` / `--format` — format: `png`, `svg`, `pdf`, `jpg`
- `-e` / `--embed-diagram` — embed diagram XML in output (PNG, SVG, PDF only)
- `-o` / `--output` — output file path
- `-b` / `--border` — border width around diagram (recommended: 10)
- `-p <index>` — page index (0-based) for multi-page diagrams; omit for single-page
- `-t` / `--transparent` — transparent background (PNG only)
- `-s` / `--scale` — scale the diagram size (e.g. `2` for 2x)
- `--width` / `--height` — fit into specified dimensions (preserves aspect ratio)
- `-a` / `--all-pages` — export all pages (PDF only)

**WSL2 example:**

```bash
`/mnt/c/Program Files/draw.io/draw.io.exe` -x -f png -e -b 10 -o diagram.drawio.png diagram.drawio
```

#### Linux headless (remote server)

```bash
gl-drawio -f <format> <input.drawio>
```

`gl-drawio` does not support `--embed-diagram` — the `.drawio` source file should be kept alongside the export. Typical usage:

```bash
gl-drawio -f png -s 2 architecture.drawio
gl-drawio -f svg -o ./images/ *.drawio
gl-drawio -f pdf -p 0 multi-page.drawio
```

### Supported formats

| Format | Embed XML | Notes |
|--------|-----------|-------|
| `png`  | Yes (`-e`) | Viewable everywhere, editable in draw.io |
| `svg`  | Yes (`-e`) | Scalable, editable in draw.io |
| `pdf`  | Yes (`-e`) | Printable, editable in draw.io |
| `jpg`  | No | Lossy, no embedded XML support |

After successful export with `-e` (native drawio CLI), delete the intermediate `.drawio` file — the exported file contains the full editable diagram.

When using `gl-drawio` (headless), keep the `.drawio` file alongside the export since `gl-drawio` does not embed XML.

If no export CLI is found: keep the `.drawio` file and inform the user they can install the draw.io desktop app or Docker (for `gl-drawio`) to enable export, or open the `.drawio` file directly.

## File naming

- Use a descriptive name based on diagram content (e.g., `login-flow`, `database-schema`)
- Lowercase with hyphens for multi-word names
- For export, use double extensions: `name.drawio.png`, `name.drawio.svg`, `name.drawio.pdf` — this signals the file contains embedded diagram XML

## Opening the result

| Environment | Command |
|-------------|---------|
| macOS | `open <file>` |
| Linux (desktop) | `xdg-open <file>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <file>)"` |
| Remote / no display | Print file path for user to download |

**WSL2 notes:**
- `wslpath -w <path>` converts a WSL2 path (e.g. `/home/user/diagram.drawio`) to a Windows path (e.g. `C:\Users\...`). Required because `cmd.exe` cannot resolve `/mnt/c/...` style paths.
- The empty string `""` after `start` prevents `start` from interpreting the filename as a window title.

## Style reference

- Complete draw.io style reference: https://www.drawio.com/doc/faq/drawio-style-reference.html
- XML Schema Definition (XSD): https://www.drawio.com/assets/mxfile.xsd

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Blank diagram | Missing root cells `id="0"` and `id="1"` | Ensure basic mxGraphModel structure is complete |
| Edges not rendering | Edge mxCell is self-closing (no child mxGeometry) | Every edge must have `<mxGeometry relative="1" as="geometry" />` |
| Export produces empty file | Invalid XML (comments, unescaped chars) | Remove all XML comments; fix well-formedness |
| draw.io CLI not found | Desktop app not installed | On headless Linux try `gl-drawio`; otherwise keep `.drawio` file, inform user |
| Canvas preview blank | GraphViewer CDN failed to load | Fall back to `.drawio` file only |
