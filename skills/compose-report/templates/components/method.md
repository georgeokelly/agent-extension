<!-- COMPONENT: method | applies to: research-findings, technical-evaluation, design-solution -->

## ⟨N⟩. Method (or: Solution Design)

**Intro-Summary**: ⟨what this section will prove / describe — 1-2 sentences⟩

### ⟨N⟩.1 Overall approach
⟨Core method 1-3 paragraphs, organized as What → Why → How three tiers. For design-solution, this is the chosen architecture overview; for research-findings, the proposed method; for technical-evaluation, the evaluation framework.⟩

### ⟨N⟩.2 Key design decisions (What → Why → How)

> Use a three-column table to organize evolution paths or decision points; surface readers extract the global picture from the What column, deep readers follow the How column into code or appendix.

<!-- DEMO from [examples.md Sec. B.7.3 Decision evolution table](../../examples.md#b73-decision-evolution-table) — REPLACE.
     For design-solution: rows are "API contract / data flow / failure handling / etc." design decisions.
     For research-findings: rows are "V1 → V5" optimization stages.
     For technical-evaluation: rows are evaluation dimensions and their measurement choice.
-->
> | Version / decision | What | Why | How |
> |---|---|---|---|
> | **V1 朴素** | 每个 thread 处理 1 元素，shared memory 树形归约 | 直观、易调试；建立 baseline | Listing 1 |
> | **V4 warp shuffle** | 用 `__shfl_down_sync` 替代 shared memory | 寄存器级交换，省 5 次 `__syncthreads` | Listing 4 |

### ⟨N⟩.3 Implementation details (linked to appendix or repository)
⟨Provide appendix / repo / commit entry; do not stack code in main text. For design-solution, link to design-doc / RFC / migration plan. For technical-evaluation, link to benchmark scripts.⟩

**Takeaway**: ⟨core value of the method⟩
