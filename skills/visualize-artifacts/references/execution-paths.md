# Execution Paths

Use this reference to decide what the current runtime can do directly, what must
be delegated, and what should be returned as a handoff spec.

## Runtime Capability Matrix

| Runtime | Can Plan | Can Generate AI Raster | Can Produce Deterministic Visuals | Recommended Action |
| --- | --- | --- | --- | --- |
| Codex app with built-in image tool | Yes | Yes, through built-in image generation when available. | Yes, through files, SVG/HTML/Mermaid, local tools, or delegated skills. | Use `imagegen` for raster work; use deterministic files for exact overlays and diagrams. |
| Codex CLI with built-in image access | Yes | Sometimes. Re-verify in the session. | Yes, for filesystem outputs and command-line renderers. | Treat built-in image generation as source raster creation only; post-process exact size/format deterministically. |
| Other agent CLI with same skills/tools | Yes | Only if that CLI exposes image generation or can delegate to one that does. | Usually yes for text/files; depends on local tools. | Use [handoff-spec.md](handoff-spec.md) when the agent cannot call the needed generator. |
| Deterministic renderer only | Yes | No. | Yes, for SVG, Mermaid, HTML/CSS, draw.io XML, slides, Python plots if data tooling exists. | Avoid AI raster generation; produce source files and list unmet raster needs. |
| No image or rendering tool | Yes | No. | Limited. | Return a handoff YAML/spec and explain required owner/tool. |

## Built-In Image Generation: Re-Verify Before Relying

Built-in image generation tools (e.g. Codex CLI `image_gen`) are not a reliable
contract for exact native size or native WebP format output. Any session-local
observation is evidence for that session only, not a platform contract. Before
writing current runtime behavior into an artifact:

1. Re-verify whether built-in image generation is available in this runtime.
2. Re-verify native size and format behavior if exact delivery is required.
3. If native control is missing or uncertain, generate a source raster first and
   satisfy exact dimensions or output format with deterministic conversion.

## Execution Decision Tree

1. **Is the request data-backed?**
   - Yes: route generation to `visualize-data`.
   - This skill may specify desired outputs, such as SVG plus 2x PNG.
2. **Is the request a structural diagram?**
   - If native editable draw.io source is needed, route to `drawio`.
   - Otherwise use a deterministic source such as Mermaid, SVG, HTML, or slides.
3. **Is the request AI raster generation or editing?**
   - If current runtime exposes image generation, use `imagegen`.
   - If not, create a handoff request.
4. **Is the request hybrid?**
   - Produce a layer manifest.
   - Route raster layer to `imagegen`.
   - Route exact overlays to deterministic tooling or `drawio`.
5. **Is the request only final format or size?**
   - Preserve the current source artifact.
   - Use deterministic conversion or document required tools.

## Handoff Modes

- **Direct call**: current agent has the owning skill/tool; call it and report
  source plus delivery artifacts.
- **Delegated agent/CLI**: current agent can call a child agent or other agent CLI with a bounded
  prompt; pass the owner, source requirements, destination, and no-touch paths.
- **Spec only**: current agent cannot execute; return a YAML handoff using
  [handoff-spec.md](handoff-spec.md).

## Cross-Tool Compatibility Notes

- Keep source artifacts in repo-native formats where possible.
- Do not assume the next agent has the same built-in image tool.
- Use a no API-key assumption: do not assume an OpenAI API key exists; API/CLI image fallback belongs to
  `imagegen` and requires explicit user/config support.
- Do not route a downstream owner back to `visualize-artifacts` for the same
  decision. This skill chooses the owner once, then exits the routing loop.
