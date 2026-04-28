<!-- COMPONENT: limitations | applies to: all types / all lengths -->

## ⟨N⟩. Limitations (or: Risks & Applicability Boundaries)

> Standard sentence pattern: "**Condition + impact number + suggested path**", three-part construct. Do NOT use vague phrases like "in some cases" or "significantly degraded".

<!-- DEMO from [examples.md Sec. B.7.6 Limitations passage demo](../../examples.md#b76-limitations-passage-demo) — REPLACE.
     Type-appropriate framing:
     - research-findings: untested regimes + measurement limits + future-work entry
     - design-solution: failure modes + scaling limits + non-goal scenarios
     - feasibility-analysis: assumption-violation scenarios + decision-reversal triggers
     - technical-evaluation: scope of comparison + non-comparable dimensions
-->
> **L1**：⟨触发条件，如「输入 < 64 KB 时」⟩ → ⟨影响数字，如「退化到 ~45 μs，优势消失」⟩ → ⟨建议路径，如「dispatcher size-based fallback」⟩。
> **L2**：⟨未测试场景，如「fp16 路径未测试」⟩ → ⟨潜在风险数字，如「累加误差 > 1e-3」⟩ → ⟨建议路径⟩。
> **L3** (long-form only) ：⟨未涵盖场景，如「多 GPU 未涵盖」⟩ → ⟨结论不适用范围⟩ → ⟨建议路径⟩。

**Future directions**: ⟨give specific entry sections + quantified targets; avoid empty "worth further investigation" phrasing⟩
