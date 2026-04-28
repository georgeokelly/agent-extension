# B Before/After Rewrites and Complete Example Slices

> The example library of the compose-report skill bundle. Pairs with reference.md for concrete rewrite shapes; pairs with templates/ for reusable section-skeleton demos.
>
> **Cross-reference convention**: each section's first line declares the corresponding reference Sec. X.Y; demo passages in Sec. B.7 / Sec. B.8 / Sec. B.4 are referenced directly by templates.
>
> **Language convention**: English commentary / methodology explanation / rewriting rules. Chinese **before / after demo passages** are retained because the skill primarily targets Chinese-language report writing — the demos model the actual prose of a Chinese report.

---

## B.1 Vague → Specific

> Demonstrates the concrete rewrite shape of reference Sec. C.4 honest limitation expression.

The most common failure mode in "uncertainty / limitations" passages is using vague phrases like "in some cases", "in most scenarios", "significantly accelerates" to substitute for specific values. The two phrasings look semantically equivalent, but the gap in decision-making value for the reader is enormous — the reader cannot answer "can I use this in my scenario?".

**Before** (so vague that the applicability boundary is unrecognizable):

> 我们的方法在大多数情况下表现良好，相比之前的方案有显著加速；当输入规模较大时性能可能会下降，未来会进一步改进。

**After** (specific, verifiable numbers + failure boundary + future-work entry):

> 在 ResNet-50 端到端训练（A100, batch=256, fp16, seq_len=512）上，本方法相比 PyTorch native attention 端到端加速 **3.12×**（IQR 3.05–3.18，median over 100 runs）。
>
> **失败边界**：当 seq_len > 8192 时因 SRAM 容量限制 tile size 上界，加速比退化到 **1.2×**；short-sequence (seq_len ≤ 1024) 场景能稳定达到 **3.5×**（见 Sec. 6.3 tile size 分析）。
>
> **未来工作入口**：分层 tiling（Sec. 7.2）目标是把 seq_len > 8192 时的加速比拉回 2.5× 以上。

**Rewriting rules**:

- Vague terms "significantly", "may degrade" → specific numbers (3.12× / 1.2×).
- "In most cases" → bound by 5±2 specific conditions (hardware / batch / seq_len / dtype).
- "Will be improved in the future" → name a specific entry section + quantified target (raise back to 2.5×).

---

## B.2 Inverted hierarchy → What → Why → How

> Demonstrates the concrete rewrite shape of reference Sec. C.1 What → Why → How layering.

"Implementation details first, motivation last" is the most common structural error in technical paragraphs. The reader gets drowned in API calls before figuring out *why this is being done*.

**Before** (implementation first, What/Why buried at the end):

> 我们使用了 `__shfl_down_sync(0xffffffff, val, offset)`，offset 从 16 递减到 1，每次将 lane (i+offset) 的值加到 lane i 上，从而在 warp 内完成最后阶段的 reduction，省掉对 shared memory 的访问与 `__syncthreads`。

**After** (What → Why → How, three tiers explicit):

> **What**：用 warp shuffle 替代 shared memory，在最后 32 个元素上做 reduction。
>
> **Why**：shared memory 路径每轮需要 `__syncthreads`（约 5 个周期），warp 内寄存器交换无同步开销，且释放 shared memory 给其他 kernel 使用。
>
> **How**：`__shfl_down_sync(0xffffffff, val, offset)`，offset = 16 → 8 → 4 → 2 → 1，5 次完成 32 元素归约（详见 Listing 4）。

**Rewriting rules**:

- The first sentence is What — a surface reader gets the gist after reading just this sentence.
- Immediately follow with Why — explain "why this API and not shared memory".
- Push How to the end or link out to a code listing — deep readers expand on demand; surface readers can skip.

---

## B.3 Noise → Signal

> Demonstrates the concrete rewrite shape of reference Sec. C.3 signal-to-noise ratio.

Adverbs, adjectives, and vague quantifiers are the noise heavyweights; replace with specific numbers wherever possible.

**Before** (stacked adverbs and unfalsifiable vague judgments):

> 关于这个优化技巧，我们做了一些初步尝试，发现可能在某些情况下能够带来一定程度的性能提升，因此值得进一步研究。

**After** (signal concentrated: boundary + numbers + verification conditions):

> 在 5 个测试样本（batch ∈ {16, 32, 64, 128, 256}）上，该优化在 batch ≥ 64 时稳定带来 **1.8–2.3×** 加速；batch < 16 时与 baseline 无显著差异（差距 < 2%，落在 IQR 内）。建议在更大数据集上复核。

**Rewriting rules**:

- "May / should / probably" → sample size + range expression (5 samples / batch ≥ 64).
- "Significantly / clearly / to some extent" → numbers (1.8–2.3×).
- "Worth further investigation" → leave a specific verification condition (larger dataset), not a generic "worth studying".

---

## B.4 Argument-style caption

> *Topic*: Decorative figure → Argument figure. Demonstrates the concrete rewrite shape of reference Sec. D.5 visualization anti-patterns (Argument-style caption). **This section provides templates with the directly-quotable Argument-style caption examples.**

**Anti-pattern symptom**: the caption restates the figure's axes or test conditions, instead of answering "what does this figure show".

**Before** (descriptive caption — the reader still does not know what the conclusion is):

> 图 3：A100 上的实验结果。横轴为 batch size，纵轴为时间（ms）。蓝线为 baseline，红线为本方法。

**After (Argument-style caption example 1 — referenced by templates' figure-caption block)**:

> 图 3：随 batch size 增大，本方法的加速比从 **1.4×** 收敛到 **3.5×**（B ≥ 256 后饱和）；baseline 在 B ≥ 512 时因 HBM 带宽 bound 而停止 scaling，是本方法相对优势的根本来源。

**After (Argument-style caption example 2 — Roofline argument variant, also referenced by templates)**:

> 图 5：V5（grid-stride）距 A100 HBM 理论带宽 **1555 GB/s** 仅差 10.5%（实测 **1390 GB/s, 89.5%**），说明 reduction kernel 已逼近内存带宽墙；进一步优化空间需从算法层（如 hierarchical reduction）而非 kernel 层挖掘。

**Rewriting rules**:

- The first sentence of the caption MUST be a conclusion or argument, not a description.
- Key numbers (speedup, bandwidth utilization) go *into* the caption — a surface reader who only reads the caption still walks away with the conclusion.
- Length 1–2 sentences is enough; over 3 sentences usually signals the argument should split into two figures.

**Reusable skeleton for templates (≤ 3 lines)**:

> 图 N：⟨主结果数字⟩ 在 ⟨条件 X 范围⟩ 时 ⟨变化趋势 / 饱和点⟩；⟨baseline 行为 / 失败模式⟩ 是 ⟨该现象 / 优势⟩ 的根本来源。

---

## B.5 Layered Brevity (Intro-Summary Three-Part)

> Demonstrates the concrete rewrite shape of reference Sec. C.5 Intro-Summary Three-Part (Clarity Pillars). **This is the most central slice of examples; the TL;DR and section skeletons in templates directly reuse the patterns here.**

"Brevity" is most often misread as "cut details". But in technical reports, **the details are the value itself** — the reader reads your report *for* the details. The correct reading of brevity is: **give every detail passage a concise entry and exit, not write the passage itself short**. Below is a complete section-level Before / After comparison.

### Before (details intact, but surface readers immediately turn away; high noise, scrambled hierarchy)

> Sec. 5.3 Warp Shuffle 优化
>
> 我们使用 `__shfl_down_sync(0xffffffff, val, offset)`，offset 从 16 递减到 1，每次将 lane (i+offset) 的值加到 lane i 上。该指令需要 SM ≥ 70（Volta 及以后）；在 Volta 之前的架构上需要回退到旧的 `__shfl_down`，但旧 API 不支持 mask 控制，遇到非满 warp 会读到未定义值。注意 mask 必须包含所有参与 reduce 的 lane——常见错误是直接用 `0xffffffff` 但实际只有前 16 个 lane 活跃，导致后 16 个 lane 读到无效数据被算入归约。在 fp16 / bf16 路径下还需要注意精度问题，建议用 fp32 累加再 cast 回去。这一节是 V1 → V4 加速的主要来源，因为省掉了 5 次 `__syncthreads`。

**Why Before fails**:

- A surface reader gets drowned in SM version / mask error / fp16 precision in the first 3 sentences and gives up.
- The most important argument — "this section is the main source of V1 → V4 speedup" — is **buried at the end**; surface readers never reach it.
- No takeaway — the reader does not know what comes next or how the context bridges.
- Hierarchy is scrambled: motivation / implementation / boundary / precision are mixed in one paragraph.

### After (details unchanged, wrapped in a concise entry and exit)

> Sec. 5.3 Warp Shuffle 优化
>
> **Intro-Summary**：本节将最后一轮 reduction 从 shared memory 路径迁移到 warp 寄存器路径，省去 5 次 `__syncthreads`，是 V1 → V4 加速 **5.4×** 的主要来源。浅读者读到这里即可决定是否继续往下；若不优化 reduction kernel，可跳过 Details 直接看 Takeaway。
>
> **Details**：我们使用 `__shfl_down_sync(0xffffffff, val, offset)`，offset 从 16 递减到 1，每次将 lane (i+offset) 的值加到 lane i 上。该指令需要 SM ≥ 70（Volta 及以后）；在 Volta 之前的架构上需要回退到旧的 `__shfl_down`，但旧 API 不支持 mask 控制，遇到非满 warp 会读到未定义值。注意 mask 必须包含所有参与 reduce 的 lane——常见错误是直接用 `0xffffffff` 但实际只有前 16 个 lane 活跃，导致后 16 个 lane 读到无效数据被算入归约。在 fp16 / bf16 路径下还需要注意精度问题，建议用 fp32 累加再 cast 回去。
>
> **Takeaway**：warp shuffle 的本质收益不是「指令更快」，而是「省掉同步」。任何 reduction 类 kernel 的最末 5 轮都值得检查是否能改写为 shuffle；下一节 Sec. 5.4 grid-stride loop 会进一步把带宽利用率从 35.6% 拉到 89.5%（接近 A100 HBM 理论上限）。

### Why After is qualified

| Dimension | Before | After |
|---|---|---|
| What a surface reader gets in 1 minute | Drowned, 0 takeaway | Intro-Summary + Takeaway = 5.4× speedup / main cause is sync elimination / next chapter pursues bandwidth |
| Technical detail for deep readers | Complete | Complete (not a word cut) |
| Bridge to the next section | Missing | Takeaway tail bridges to Sec. 5.4 |
| Argument a decision-maker can grab from this section | None | "warp shuffle's essential value is sync elimination" — directly usable in upper-level reporting |

**Note**: After's Details section is **identical to Before** — no detail was cut, only a concise entry and exit were wrapped around it. This is the essence of "layered brevity".

### Three core gains

1. **Surface readers get a free skeleton**: stringing together every section's Intro-Summary + Takeaway gives the entire argument chain of the report.
2. **Deep readers are not forcibly simplified**: the middle Details can go as deep as needed, adapting per section from instruction-level to distributed-system-level.
3. **The author benefits in reverse**: before writing the Intro-Summary, you must answer "what is this section's actual argument" — this exercise itself exposes many things that were unclear during writing.

### Application granularity quick-reference

| Granularity | Intro-Summary form | Details form | Takeaway form |
|---|---|---|---|
| Whole report | TL;DR / Abstract | All chapters | Conclusion & future work |
| Chapter | Chapter-opening paragraph | Sub-sections | "Chapter summary" at end |
| Section | First 1–3 sentences | Section-internal details | Closing 1–3 sentences takeaway |
| Paragraph | Topic sentence | Paragraph-internal argumentation | Closing bridge sentence (optional) |

Minimum: **every section** MUST have Intro-Summary and Takeaway. Very short sub-sections (< 100 字), pure-definition paragraphs, pure code listings MAY omit them.

---

## B.6 Mixed modal verbs → Strict distinction (RFC 2119)

> Demonstrates the concrete rewrite shape of reference Sec. C.6 industrial-grade modal verb specification.

In requirement / design / compliance reports, modal verbs determine the **legal strength of the semantics**. The Chinese 「应当」 can be read as either SHOULD (recommendation) or MUST (mandatory), and is the most common source of ambiguity.

### Before (vague semantics; three items all use 「应当」, the strength cannot be distinguished)

> - 系统应当对所有外部请求做身份验证。
> - 日志应当每天轮转。
> - 用户应当能够导出配置。
> - 重置流程不能清空已加密的密钥分片。

**Why Before fails**: item 1 is absolutely mandatory (security-related), item 2 is a recommendation (compliance preference), item 3 is an optional permission. The strength gap is enormous, but the reader sees three identical 「应当」 with no way to tell which is a hard requirement vs. nice-to-have — this is a direct liability risk in compliance audit and system acceptance.

### After (strict RFC 2119 distinction with English-Chinese cross-reference)

> - 系统 **MUST**（必须）对所有外部请求做身份验证。
> - 日志 **SHOULD**（应）每天轮转，偏离需提供书面理由。
> - 用户 **MAY**（可）通过 CLI 导出配置为 JSON。
> - 重置流程 **MUST NOT**（绝不）清空已加密的密钥分片。
>
> **声明**：本报告 MUST / SHOULD / MAY / MUST NOT / SHALL / SHALL NOT 的语义遵循 IETF RFC 2119 与 ISO/IEC Directives Part 2 的定义。

### Rewriting rules

- **No mixing within the same report**: MUST and SHOULD are not interchangeable under equal conditions.
- For Chinese writing, parenthesize the English equivalent: 「应当（MUST）触发自动断电」, avoiding cross-language ambiguity.
- **Do NOT** use MUST / SHOULD in "Results & discussion" sections (those are requirement semantics); use "is / was / observed / measured".
- On first occurrence of MUST / SHOULD, declare RFC 2119 conformance in the introduction or appendix glossary.

---

## B.7 GPU Reduction Kernel slices

> *Topic*: GPU reduction kernel optimization report key-section slices. Demonstrates the integrated form of reference Sec. E.1 Benchmark 7-item disclosure + Sec. C.1 What → Why → How + Sec. C.4 Limitations + Sec. C.5 Intro-Summary three-part. **This section provides templates with directly-quotable demo passages** — each sub-section is sliced at templates' citation granularity (≤ 3–7 lines).

**Scenario**: on an A100, perform a sum reduction over 1M floats; optimize from a naive implementation to warp shuffle + grid-stride loop, and write up a "record-and-explain" short report.

### B.7.1 TL;DR demo

> *Reference source*: templates' TL;DR section.

> 在 A100 上对 4 MB float 数组做 sum reduction，**从朴素 shared-memory 实现优化到 warp shuffle + grid-stride loop，端到端时延从 245 μs 降到 38 μs（6.4× 加速）**。最后版本接近内存带宽上限（理论 1555 GB/s，实测 1390 GB/s，**89.5%**）。报告记录每一步的动机、Roofline 位置变化，以及未覆盖的边界（< 64 KB 输入退化、需要 SM ≥ 70）。

**Design points of this TL;DR**:

- One sentence covers all three things: "what was done + key numbers + limitation".
- "6.4×" and "89.5% bandwidth" serve the engineer's perspective and the researcher's perspective respectively.
- Limitation is placed last, establishing honesty.

### B.7.2 Background and Goals demo

> *Reference source*: templates' "Background & Goals" section.

> **问题**：reduction 是 GPU 编程最基础的 primitive 之一，但朴素实现往往只达到内存带宽 5–10%，是 large-scale workload 中容易被忽视的瓶颈。
>
> **范围（scope）**：单 GPU、fp32、N ∈ [10⁵, 10⁸]、device-to-device 时延（不含 host↔device 拷贝）。
>
> **非范围（non-scope）**：fp16 / bf16 精度路径、多 GPU all-reduce（NCCL）、cooperative groups。
>
> **成功判据**：在 N = 10⁶ 时端到端时延 ≤ 50 μs，且带宽利用率 ≥ 80%。

**Design points of this passage**: scope / non-scope are explicitly listed to prevent late-stage scope creep; success criteria are quantified (50 μs / 80%) instead of "fast" / "high".

### B.7.3 Decision evolution table

> *Reference source*: templates' "Method" section. Table header + 1 row directly reusable. Demonstrates What → Why → How layering across versions.

| Version | What | Why | How |
|---|---|---|---|
| **V1 朴素** | 每个 thread 处理 1 元素，shared memory 树形归约 | 直观、易调试；建立 baseline | Listing 1 |
| **V2 顺序索引** | 修改归约时 thread 索引顺序 | 避免 V1 中 warp 内 bank conflict 与 divergence | Listing 2 |
| **V3 unroll last warp** | 最后一个 warp 不再 `__syncthreads` | warp 内天然同步，省掉 5 次 sync | Listing 3 |
| **V4 warp shuffle** | 用 `__shfl_down_sync` 替代 shared memory | 寄存器级交换，避免 shared memory 访问 | Listing 4 |
| **V5 grid-stride** | 每个线程处理多个元素再做归约 | 更高 occupancy + 减少 grid 大小 | Listing 5 |

**Design points of this table**:

- One table covers the entire optimization story; one What / Why / How per row.
- The reader who only reads the What column still gets the global picture (Intro-Summary level).
- The How column gives only Listing numbers; deep readers flip to code on demand (Details level).

### B.7.4 Benchmark 7-item disclosure filling

> *Reference source*: templates' "Experiment Setup" section. Demonstrates how to fill the 7 mandatory disclosure items.

> **1. Hardware**：NVIDIA A100-SXM4-40GB；NVLink；1× node。
> **2. Software**：Ubuntu 22.04，kernel 5.15；驱动 535.129.03；CUDA 12.4；nvcc `-O3 -arch=sm_80`。
> **3. Workload (输入)**：sum-reduce 1M float32（4 MB），device-to-device，无 host↔device 拷贝。
> **4. Configuration**：blockDim = 256；gridDim 由 occupancy calculator 自适应；编译选项见 2。
> **5. Sampling (采样)**：1000 runs；前 100 次 warm-up；丢弃 > 3σ outlier；CUDA events 测时延。
> **6. Statistics (统计量)**：median + IQR——对长尾鲁棒，比 mean+std 更适合 GPU kernel 时延。
> **7. Baseline**：V1 naive（同等输入 / 同等 dtype / 同等 blockDim，无任何额外优化）。

**Design points of these 7 lines**: each line corresponds to one of the Benchmark 7-item disclosure entries; missing any one is a fail. Templates can directly reuse this skeleton, replacing only the specific values.

### B.7.5 Results table

```
Version           Time (μs)   Speedup    %BW (theory 1555 GB/s)
V1 naive          245 (±3)    1.00×       6.5%
V2 seq idx        128 (±2)    1.91×      12.5%
V3 unroll last     72 (±1)    3.40×      22.2%
V4 warp shuffle    45 (±1)    5.44×      35.6%
V5 grid-stride     38 (±1)    6.45×      89.5%
```

**Argument-style caption**: 「表 1：V5 在 89.5% 带宽利用率下逼近 A100 HBM 理论上限；V3 → V4 的 1.6× 跃升来自 warp shuffle 消除最末 5 次 `__syncthreads`，是单一最大优化收益。」

### B.7.6 Limitations passage demo

> *Reference source*: templates' "Limitations" section. Demonstrates quantified failure-boundary writing.

> **L1**：输入 < 64 KB 时 V5（grid-stride）的 occupancy 优势消失，性能退化到 V4 水平（约 45 μs），建议在 dispatcher 层做 size-based fallback。
>
> **L2**：fp16 / bf16 路径**未测试**；low-precision 累加可能引入 > 1e-3 相对误差，建议生产环境用 fp32 累加再 cast（Kahan 求和成本太高）。
>
> **L3**：多 GPU 场景**未涵盖**，跨 node all-reduce 的瓶颈在 NCCL 集合通信而非单 kernel；本结论不适用于 distributed training scaling 分析。
>
> **L4**：blockDim 固定为 256；在 H100 上未必最优（SM 数 / shared memory 容量不同），建议跨架构调参。

**Design points of this passage**: every limitation is "**condition + impact number + suggested path**", three-part construct, instead of vague "in some cases". Templates can directly reuse the L1–L4 writing skeleton.

---

## B.8 Top-K selection example (key-section slices)

> Demonstrates the integrated form of reference Sec. F.1 three-reader-type differences + Sec. E.3 fair comparison + Sec. C.4 limitations (Top-K selection slice). **This section provides templates with the directly-quotable complexity comparison table and three-perspective selection skeleton for "Related Work / Selection Comparison" and "Conclusion / Recommendation" sections.**

**Scenario**: from N = 10⁸ floats, take the top K (K = 100); compare four routes — full sort / heap / QuickSelect / streaming approximation.

### B.8.1 TL;DR demo (Top-K)

> 对 N = 10⁸ float 取 Top-100：**离线 + 内存够时 QuickSelect 最快**（O(N)，0.61 s）；**K ≪ N 时 min-heap 在 streaming / 有限内存场景更优**（O(N log K)，0.83 s）；**N 超内存（如分布式日志）时**用 Space-Saving 近似算法以 < 1% 误差换常数空间。

### B.8.2 Complexity comparison table

> *Reference source*: templates' "Related Work / Selection Comparison" section.

| Algorithm | Time | Space | Streaming | Error | When to use |
|---|---|---|---|---|---|
| **Full sort** | O(N log N) | O(N) | No | 0 | You already need to sort the whole dataset |
| **Min-heap of size K** | O(N log K) | O(K) | **Yes** | 0 | K ≪ N and streaming required |
| **QuickSelect (introselect)** | O(N) avg / O(N log N) worst | O(1) | No | 0 | Offline + memory available + exact required |
| **Space-Saving (approximate)** | O(N) | O(1/ε) | Yes | ε relative error | Massive stream + tolerate < 1% error |

**Design points of this table**:

- The 5 columns "Time / Space / Streaming / Error / When to use" cover all dimensions of the selection decision.
- The "When to use" column directly serves engineers in selection, sparing the reader from having to reverse-engineer applicable scenarios from complexity classes.
- The Error column places exact algorithms (0) alongside approximate (ε), avoiding confusion.

### B.8.3 Data-distribution sensitivity

**Before** (dishonest, hides worst case):

> QuickSelect O(N).

**After** (honest, gives worst-case + trigger condition + fallback):

> QuickSelect 期望 O(N)，但在最坏情况（每次 partition 极不平衡）退化到 O(N²)。
>
> 我们的实现使用 **median-of-3 pivot 选择 + introselect 兜底**（递归深度 > 2 log N 时切换到 heapsort，保证 O(N log N) worst-case）。在 IID 输入上 50 次实验未观察到退化；但对**已排序或反序输入** worst-case 仍可能触发，建议生产环境强制 introselect（参考 `std::nth_element`）。

**Rewriting rules**: stating only expected complexity misleads the reader about the worst-case scenario. **"expected + worst-case + trigger condition + fallback", a four-part construct**, is the floor for honesty.

### B.8.4 Benchmark table

```
Setup:    Intel Xeon 8380, 1 thread; gcc 13.2 -O3
Input:    N = 10⁸ uniform random float32; K = 100
Runs:     50 trials; report median (IQR)
Baseline: std::sort + take first K (same input / same compile options)

Algorithm           Time (s)        Memory      Notes
Full sort           4.21 (±0.05)    400 MB      baseline
Min-heap size K     0.83 (±0.02)    400 MB+8KB  streaming-friendly
QuickSelect (NTH)   0.61 (±0.02)    in-place    uses introselect
Space-Saving ε=1%   0.55 (±0.03)    16 KB       relative err ≤ 1%
```

**Fair-comparison key points**: all algorithms run on the same input, the same compile options, the same thread count, the same statistic — preventing the three common cheats of "baseline-not-optimized / different-input / different-thread-count".

### B.8.5 Three-perspective selection

> *Reference source*: templates' "Conclusion / Recommendation" section.

```
Engineer perspective:
  □ K ≪ N + streaming / limited memory      → min-heap
  □ Offline + memory available + exact       → QuickSelect (introselect)
  □ Massive stream / distributed / tolerate small error → Space-Saving (ε = 0.01 → max err 0.83%)
  □ Already sorting the whole dataset        → just sort, do not over-engineer

Researcher perspective:
  □ Worst-case guarantee                     → median-of-medians (deterministic O(N))
  □ Large K + ordered output required        → partial-sort variants
  □ Distribution-aware optimization          → radix-based selection

Decision-maker perspective:
  □ Distribution unknown / requirements may change → start with min-heap; controllable + explainable
  □ Distribution stable + extreme performance critical → invest in QuickSelect + introselect fallback
  □ Data scale grows exponentially            → adopt Space-Saving directly to avoid rewrites later
```

**Design points of this passage**: same set of algorithms, same dataset, three reader-type-specific selection recommendations. This is the concrete realization of "single report, multi-audience" layered supply — templates can directly reuse this skeleton, replacing only the algorithm names and decision conditions.

---

## B.9 4-step chart derivation (simplified)

> Demonstrates the simplified derivation of reference Sec. D.2 Code → Information → Model → Visualization 4-step methodology. **Vehicle**: GPU reduction kernel (V1 → V4 synchronization-trace comparison).

### Step 1: Code (raw code)

```cuda
__global__ void reduce_v1(const float* g_in, float* g_out, int N) {
    extern __shared__ float sdata[];
    int tid  = threadIdx.x;
    int gidx = blockIdx.x * blockDim.x + tid;
    sdata[tid] = (gidx < N) ? g_in[gidx] : 0.0f;
    __syncthreads();

    for (int s = 1; s < blockDim.x; s *= 2) {
        if (tid % (2*s) == 0) sdata[tid] += sdata[tid + s];
        __syncthreads();
    }
    if (tid == 0) g_out[blockIdx.x] = sdata[0];
}
```

**Scan three dimensions**: control flow (log₂(blockDim.x) rounds, active threads halve each round); data flow (global → shared → reduce → global); synchronization and dependencies (`__syncthreads` at each round's end; round s depends on round s/2).

### Step 2: Information (distill 5±2 key facts)

1. **Active thread count halves each round** (round s: blockDim.x / (2s) threads).
2. **Severe warp divergence**: in the first round, only 16 of 32 lanes are active.
3. **Bank conflict risk**: the `tid + s` pattern at s = 1 causes multiple lanes to hit the same bank.
4. **Synchronization overhead**: log₂(256) = 8 `__syncthreads` calls.
5. **Last-round waste**: when s ≤ 32, the kernel still goes through shared memory + sync path.

→ **Core improvement points**: reduce divergence; eliminate bank conflict; eliminate last-round sync.

### Step 3: Model (build mental model — "binary-tree merge")

Each block is a binary tree of height log(blockDim.x); leaves are the original data, each round merges "two leaves into a parent" until the root. **Abstraction layer**: operator level (intra-block reduction), neither dropping to instruction level nor rising to grid level — matches the cognitive layer of a reader for a "GPU kernel optimization" report.

```
Height 0 (leaves):  a0  a1  a2  a3  a4  a5  a6  a7
                     ↓     ↓     ↓     ↓
Height 1:         a0+a1  a2+a3  a4+a5  a6+a7
                       ↓             ↓
Height 2:           a0..3          a4..7
                          ↓
Height 3:                a0..7  ← root
```

### Step 4: Visualization (final figure — synchronization-trace comparison)

**Target reader question**: "Why is V4 faster than V1?" The figure that best answers this is a **two-version "sync points + data movement path" comparison** — not a plain performance bar chart.

Candidate-scheme trade-offs:

| Scheme | Pros | Cons | Choice |
|---|---|---|---|
| Performance bar chart | Direct | Does not explain mechanism | ✗ (already in benchmark table) |
| Roofline | Shows bandwidth bottleneck | Does not explain specific optimization | △ (supplementary) |
| Sync-trace comparison | Directly shows the sync difference | Labor-intensive | ✓ Main figure |
| Binary-tree model | Shows reduction's essence | Low information density | ✓ Auxiliary figure |

**Final figure (ASCII version)**:

```
V1 (every round goes through shared memory + sync):

┌────────┬────────┬────────┬────────┬────────┐
│ load   │ s=1    │ s=2    │ s=4    │  ...   │
│ + sync │ + sync │ + sync │ + sync │ + sync │
└────────┴────────┴────────┴────────┴────────┘
          ↑ divergence    ↑ bank conflict
          ↑ 8× __syncthreads

V4 (first log(N/32) rounds via shared memory; last 5 rounds via warp shuffle):

┌────────┬────────┬────────┬────────┐ ┌──────────────────┐
│ load   │ s≥32:  │ s≥32:  │ s≥32:  │ │ s<32: shfl_down  │
│ + sync │ + sync │ + sync │ + sync │ │ ×5 rounds, no    │
│        │        │        │        │ │ sync             │
└────────┴────────┴────────┴────────┘ └──────────────────┘
                                       ↑ register-level swap
                                       ↑ 0× __syncthreads
```

**Argument-style caption**: 「图：V1 在所有 log(blockDim.x) 轮都需要 `__syncthreads`；V4 把后 5 轮迁移到 warp shuffle，减少 5 次同步并消除最末轮的 divergence 与 bank conflict——这是 V1 → V4 5.4× 加速的主要来源。」

### 4-step output checklist (what was distilled from this code)

After running through 4 steps, from this code we have distilled:

- **5 key facts** (Step 2).
- **1 mental model**: binary-tree merge (Step 3).
- **1 main comparison figure + 1 auxiliary model figure** (Step 4).
- **1 line of Argument-style caption**.

> **Closed-loop check**: if the final figure cannot answer "what does this figure show" in one sentence, return to Step 2 and re-distill the signal — do not patch the figure piecemeal. The final goal of this methodology is: from the same piece of code, output visualizations at different abstraction layers per the section's needs (Step 3 model figure for design motivation; Step 4 comparison figure for results analysis).

---

> **End of Sec. B**
>
> This file pairs with reference.md (deep methodology) and templates/ (section skeletons) for usage. If during writing a particular section's example does not fit, return first to the corresponding sub-section in reference.md to re-check the methodology; the demo passages in templates/ all originate from this file — replace only the specific values.
