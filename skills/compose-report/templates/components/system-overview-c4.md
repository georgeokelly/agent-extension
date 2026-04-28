<!-- COMPONENT: system-overview-c4 | applies to: research-findings, technical-evaluation, design-solution (long) -->

## ⟨N⟩. System Overview (C4 model 4-layer overview)

**Intro-Summary**: ⟨a top-down view of the system at the highest abstraction — 1-2 sentences⟩

### ⟨N⟩.1 C4 L1 — Context (system in its external environment)
⟨Context diagram placeholder: upstream users / downstream consumers / external dependencies⟩

### ⟨N⟩.2 C4 L2 — Container (top-level components / service split)
⟨Container diagram placeholder: processes / services / databases / queues⟩

### ⟨N⟩.3 C4 L3 — Component (internals of containers)
⟨Component diagram placeholder: module level. Include only for components that are core to this report's argument.⟩

### ⟨N⟩.4 C4 L4 — Code (class / function level for key modules, on demand)
⟨L4 typically only for key modules; skip for most.⟩

> **Expansion guidance**: each layer SHOULD have ≥ 1 diagram + 1 paragraph; not all 4 C4 layers are mandatory — pick 2-3 based on system complexity. L1 + L2 are required when this component is included by the manifest sequence. For research-findings reports with minimal system context (the studied artifact stands largely alone), fill L1 with a brief "Subject-only" diagram (single box for the studied artifact + ≤ 2 immediate dependencies) + a one-sentence note explaining the minimal scope — do NOT skip the section.

**Chapter summary**: ⟨1 sentence summarizing the overall architecture + entry point to the argumentation chain⟩
