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
  version: "1.2"
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

- **NEVER include ANY XML comments (`<!-- ... -->`) in the output.** XML comments are strictly forbidden — they waste tokens, can cause parse errors, and serve no purpose in diagram XML.
- Escape special characters in attribute values: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Always use unique `id` values for each `mxCell`

Consult `references/xml-reference.md` for complete style properties, edge routing details, and container examples.

## [Cursor-only] Canvas preview

> **Skip this section if you are not running in Cursor.** This feature requires Cursor's browser/canvas tools. Claude Code and Codex skip this step.

After writing the `.drawio` file, create an inline preview:

1. Read `references/canvas-template.html` for the HTML structure
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
