# reference.md

> compose-report skill bundle — full methodology, organized by topic.
>
> **Purpose**: gives the "phenomenon → method → applicability boundary" three-part deep dive for each topic. **SKILL.md** is the decision entry and quick reference; **examples.md** is the Before/After rewrite shapes; **templates/** are the copyable section skeletons; this file is the **theoretical anchor** between them.
>
> **Jump**: [SKILL.md](SKILL.md) · [examples.md](examples.md) · [templates/manifest.md](templates/manifest.md) · [templates/components/](templates/components/)
>
> **Terminology**: uses the unified glossary throughout ("Intro-Summary / Details / Takeaway three-part", "What → Why → How", "Benchmark 7-item disclosure", "Argument-style caption", "C4 model", "Five Gates", "CODER workflow", "Amazon 6-Pager", "Google Design Doc"). See [SKILL.md](SKILL.md) Sec. 11 Glossary.
>
> **Language convention**: English methodology and commentary; Chinese **before / after demo passages** are retained because the skill primarily targets Chinese-language report writing. The cross-language analogy table in Sec. C.2.3 retains Chinese to model the cognitive mapping for Chinese readers.
>
> **Table of contents**:
>
> - [Sec. A Readers and Goals](#a-readers-and-goals) — Sec. A.2 / Sec. A.3 / Sec. A.4
> - [Sec. B Overall Structure](#b-overall-structure) — Sec. B.1 / Sec. B.2 / Sec. B.3
> - [Sec. C Content Granularity](#c-content-granularity) — Sec. C.1 / Sec. C.2 / Sec. C.3 / Sec. C.4 / Sec. C.5 ★ / Sec. C.6
> - [Sec. D Visualization](#d-visualization) — Sec. D.1 / Sec. D.2 ★ / Sec. D.3 / Sec. D.4 / Sec. D.5 / Sec. D.6
> - [Sec. E Benchmark](#e-benchmark) — Sec. E.1 ★ / Sec. E.2 / Sec. E.3
> - [Sec. F Multi-Audience](#f-multi-audience) — Sec. F.1 / Sec. F.2 / Sec. F.3
> - [Sec. G Workflow](#g-workflow) — Sec. G.1 / Sec. G.2 / Sec. G.3 / Sec. G.4 / Sec. G.5
> - [Sec. H Self-check (5 categories, including Anti-shortcut sentinel)](#h-self-check-five-categories)
> - [Sec. I Writing-layer anti-patterns](#i-writing-layer-anti-patterns)
> - [Sec. J Recommended Resources](#j-recommended-resources)

---

## A Readers and Goals

### A.2 Reader Persona (Three Types)

**Phenomenon**: when writing without a concrete reader in mind, the report tends to be "for everyone" — and ends up readable by no one. The most common failure signal is "uniform terminology density" — domain experts find it verbose, while cross-domain readers find it leaping.

**Method**: before writing, write the "imagined reader" in 1-2 sentences and pin it to the top of the draft. The reader persona MUST cover at least 4 dimensions; missing any one creates a blind spot during writing:

| Dimension | Mandatory question | What it affects |
|---|---|---|
| **Background-knowledge layer** | Which prerequisites can be assumed? Which MUST be explained or linked out? | Whether terminology needs first-occurrence expansion; whether a background section is needed |
| **Goal / motivation** | Why is the reader reading this report? (Reproduce / borrow / review / decide) | Section ordering; for which audience the key numbers are written |
| **Reading path** | Sequential reading / skimming / figures-only / abstract-only? | Completeness of TL;DR; how self-contained figures need to be |
| **Trust premise** | Why should the reader believe your conclusions? (Data / code / peer review / authoritative citation) | Completeness of experimental disclosure; citation source |

Throughout the writing process, every few paragraphs ask yourself: "**Where would this imagined reader get stuck?**" This is the fundamental mechanism of "depth made accessible" — turning abstract "readability" into actionable "writing for one specific person".

**Typical reader-persona example** (what to pin at the top of a draft):

```text
> Imagined reader: an engineer with 3 years of experience / a 2nd-year PhD student,
>                 familiar with linear algebra and parallel-computing fundamentals,
>                 has never used CUDA and has not seen reduction-style kernel optimization,
>                 reads this report to apply similar optimization patterns in their own code.
```

**Default assumption** (the most robust working assumption): every reader is "**smart but busy, and possibly unfamiliar with your sub-field**". This simultaneously avoids underestimating intelligence and overestimating context.

**Applicability boundary**:

- When the target reader is highly homogeneous (e.g. an internal team report), the persona MAY shrink to a single class; but **at least** write one paragraph — do not skip it.
- When the reader population is cross-language or cross-jurisdiction, add a "Chinese-English terminology mapping" plus a "cultural default assumptions" dimension.
- Marketing / tutorial / decision-recommendation reports require different dimensions (purchase-decision path / operational context / objection rehearsal) — this skill does not adapt to those.

> Three reader types' attention differences → Sec. F.1; multi-audience path-based reading → Sec. F.2.

---

### A.3 Multi-Audience Layering Strategy

**Phenomenon**: real-world readers are never of just one type. Forcing all of them to read the same content is a failure mode — surface readers get pushed away, deep readers feel diluted.

**Method**: **Layered Disclosure** — slice the same report into 4 independently readable layers L1-L4; each layer is a self-contained closed loop. This is Jakob Nielsen's "progressive disclosure" principle landed onto technical reports.

```text
┌──────────────────────────────────────────────────────┐
│  L1  TL;DR / abstract / key figure       ← 80% of readers stop here │
├──────────────────────────────────────────────────────┤
│  L2  Body: motivation, method, key results ← engineers stop here │
├──────────────────────────────────────────────────────┤
│  L3  Method details, benchmark, ablation   ← researchers care here │
├──────────────────────────────────────────────────────┤
│  L4  Appendix: code, raw data, derivations, configs ← only reproducers │
└──────────────────────────────────────────────────────┘
```

What "self-contained closed loop" means specifically for each layer:

- **After reading L1**: can decide whether to continue; knows "what was done + key results + main limitation".
- **After reading L2**: can understand the overall solution; can answer "why this approach" and "can I reuse it".
- **After reading L3**: can judge whether the method is sound; can answer "do the ablations support the conclusion; is the differentiation from prior work valid".
- **After reading L4**: can reproduce independently; can answer "given the same hardware / software / data / configuration, can I get the same numbers".

**Applicability boundary**:

- L1-L4 is **report-level** layering; at the **section level**, an additional layer of Intro-Summary three-part (Sec. C.5) is stacked — the reader can "brake" at any granularity in "report → chapter → section → paragraph" four-tier progressive disclosure.
- Very short reports (< 1500 字) MAY merge L3-L4 into a single appendix section; L1 MUST NOT be merged.
- Long-form white papers sometimes need an L0 "Executive Summary" as a standalone page (~1 page) for decision-makers to archive at a glance.

> Section-level Intro-Summary three-part → Sec. C.5; report-level information layering L1-L4 and progressive-disclosure principles → Sec. B.2.

---

### A.4 Report Primary Purpose

**Phenomenon**: "what kind of report should this be" is **not** the most important question to ask before writing. The most important question is "**which type of report is this**" — the four types differ entirely in section ordering, evidence focus, and common pitfalls; if you discover the wrong type after writing, the rewrite cost is 5-10× the skeleton-stage rewrite cost.

**Method**: at the top of the draft write `Report type = ⟨one of four⟩`, then order sections by reverse-engineering from the "MUST front-load" column in the table below.

| Primary purpose | Reader's first question | MUST front-load | Evidence focus | Most common error |
|---|---|---|---|---|
| **Convey research findings** | Are the results trustworthy, novel, verifiable? | Research question / methodology overview / main results / limitations | Method transparency / experimental setup / error and reproducibility conditions | Stacking results without explaining significance and boundaries |
| **Propose design solution** | Why this approach instead of alternatives? | Requirements / constraints / solution comparison / trade-off rationale | Architecture diagrams / interface boundaries / alternative comparison matrix | Only describing "how to do" without "why this way" |
| **Feasibility analysis** | Can it be done; is it worth doing? | Assumptions / cost / risk / validation path / go-no-go criteria | Constraints / risk inventory / pilot metrics | Writing vision as conclusion; writing assumptions as facts |
| **Technical evaluation** | Which solution is better under what conditions? | Evaluation criteria / baseline / data sources / metric semantics | Controlled experiments / measurement methodology / unified evaluation calibration | Inconsistent metric calibration; charts that fail to support the recommendation |

**Typical evidence-focus differences between the 4 report types**:

- **Research-findings type**: method transparency takes priority over length. Benchmark 7-item disclosure (Sec. E.1) is a hard constraint.
- **Design-solution type**: MUST contain a "Considered Alternatives" section — design docs without alternatives almost always miss key trade-offs (see Sec. F.3 Google Design Doc paradigm).
- **Feasibility type**: clearly distinguish "assumptions" from "facts"; every assumption is paired with a validation path.
- **Technical-evaluation type**: a unified evaluation calibration is the lifeline. An evaluation report that uses "relative speedup" for one item and "end-to-end latency" for another cannot be holistically judged by the reader.

**Composite primary purposes**: when a report carries two primary purposes simultaneously (e.g. "design + feasibility"), use the more urgent one as the main thread and embed the other as a sub-section. For example:

- Main thread = design solution (Sec. 4 Method / Sec. 5 Architecture);
- Sub-section = feasibility analysis (Sec. 4.6 Risk and go-no-go), but NOT a standalone chapter — a standalone chapter would force the two threads to compete for the TL;DR.

**Applicability boundary**:

- The 4 types do **not** apply to tutorial / marketing / decision-recommendation reports — those are about "the reader's next action" rather than "record and explain"; this skill does not optimize them.
- Academic papers are almost always "research-findings type"; ADRs (Architecture Decision Records) are a lightweight variant of "design-solution"; technical-survey reports are typically "technical-evaluation" + "feasibility" composite.

> Two industrial paradigms for decision-type reports (Amazon 6-Pager / Google Design Doc) → Sec. F.3.

---

## B Overall Structure

### B.1 IMRaD vs Pyramid vs Diataxis (three mainstream structures)

**Phenomenon**: each structure has a scenario it excels at. Forcing the wrong structure is a common cause of headache in technical reports — writing a decision-type report as IMRaD makes the CEO see the conclusion only at Sec. 5; writing an academic experiment as Pyramid leaves the reviewer unable to find the methods section.

**Method**: first identify the report's primary purpose, then choose the appropriate structure. The three structures' core differences:

| Structure | Origin | Order | Best for | Worst for |
|---|---|---|---|---|
| **IMRaD** | Academic papers | Introduction → Methods → Results → Discussion | Reproducibility-heavy, rigor-required experiments | Business reporting, decision recommendation |
| **Pyramid Principle** | McKinsey / Minto | Conclusion → Argument → Detail | Decisions and reporting; time-pressed readers | Methods sections requiring deductive derivation |
| **Diataxis** | Documentation framework (Daniele Procida) | 4 doc types (Tutorial / How-to / Reference / Explanation) strictly separated | Software documentation systems (**full set**) | A single report (granularity too coarse) |

The best practice for "record-and-explain" reports is **mixed strategy** — different layers use different structures:

```text
Top tier (L1-L2): Pyramid    — fastest path for surface readers to reach the conclusion
Middle tier (L3): IMRaD       — rigorous reproducibility for the methods part
Bottom tier (L4): Diataxis Explanation — background knowledge and concept explanations as standalone sections
```

**Concrete chapter form of the mixed strategy**:

```text
1.  TL;DR                          ← Pyramid top
2.  Background & problem statement ← IMRaD-Introduction
3.  Method / system design          ← IMRaD-Methods
4.  Experiments / Benchmark         ← IMRaD-Results
5.  Discussion & trade-offs         ← IMRaD-Discussion
6.  Conclusion & future work        ← Pyramid closing
A.  Concept explanations (standalone appendix or external link) ← Diataxis-Explanation
B.  Reproduction guide              ← Diataxis-How-to
```

**Applicability boundary**:

- When the primary purpose is **decision-making** (Sec. A.4 "design solution / feasibility" + main reader is an executive), prefer Pyramid over IMRaD; further consider Amazon 6-Pager (→ Sec. F.3).
- When the primary purpose is **reproduction** (academic papers / engineering experiment reports), IMRaD is the default; deviating from IMRaD usually loses reviewer trust.
- Diataxis's 4 types are categorization for an **entire documentation system**, not section ordering for a single report — using it as section ordering is a common misuse.

---

### B.2 Information Layering L1-L4 and Progressive Disclosure

**Phenomenon**: "one-shot dump" is the #1 anti-pattern in technical reports — throwing all details, terminology, and derivations at the reader at once; surface readers immediately turn away, and even deep readers cannot find the main thread.

**Method**: **Progressive Disclosure** — Jakob Nielsen's cognitive-load management principle: present a small amount of essential information first, let the reader expand on demand. In technical reports, this lands as three concrete actions:

1. **Lead with the conclusion**: open each section with one sentence stating the conclusion, then expand with arguments.
2. **Complexity progression**: state the simplest version first, then add constraints, then add optimizations. Never give the final version directly.
3. **Recursive layering**: one concept → one formula → one piece of code → one batch of data. Each layer adds precision but starts from the same argument.

**Anti-example vs positive example** (two ways to write the same paragraph):

> **Anti-example (one-shot dump)**: "We propose FlashAttention-3, which fuses the softmax normalization with the GEMM epilogue, combined with warp specialization and the pipelined producer-consumer model, leveraging the Hopper TMA to achieve…"
>
> **Positive example (progressive)**:
> 1. "Attention is essentially: *compute scores → normalize → weighted sum*."
> 2. "The naive implementation's bottleneck is that the intermediate matrix S = QKᵀ is too large; writing it back to HBM costs far more than the computation."
> 3. "FlashAttention's core idea is to fuse these three steps into SRAM, avoiding the writeback."
> 4. "FlashAttention-3 builds on this by leveraging Hopper's TMA and warp specialization to further hide latency…"

**Content protocol for L1-L4** (what each layer SHOULD have, what it SHOULD NOT have):

| Layer | SHOULD have | SHOULD NOT have |
|---|---|---|
| **L1** | One-sentence conclusion + key numbers + main limitation | Any undefined term; any detail path |
| **L2** | Motivation, method overview, key results, Roofline position | Complete code, derivations, raw data |
| **L3** | Method details, ablations, differences from prior work | Large blocks of uncompressed raw logs |
| **L4** | Complete code, raw data, derivation steps, all configurations | Main-thread arguments (those should already be settled in L1-L3) |

**Applicability boundary**:

- Progressive disclosure is a **report-level** mechanism; combined with section-level Intro-Summary three-part (Sec. C.5), it forms the "report → chapter → section → paragraph" four-tier progressive-disclosure system.
- Very short reports (< 1500 字) MAY merge L3-L4 into a single appendix section; but L1 and L2 MUST stay separated, otherwise surface readers cannot brake.
- Do NOT write progressive disclosure as "mystification" — L1 MUST be an honest condensation; do not hide key numbers in L3 expecting the reader to "dig".

> Section-level Intro-Summary three-part → Sec. C.5; multi-audience path-based reading → Sec. F.2.

---

### B.3 Abstract / Introduction / TL;DR Conventions

**Phenomenon**: abstract / introduction / TL;DR are the entirety for surface readers and MUST work independently; but they are also the most easily mis-written — in many drafts these three sections overlap by 80%, wasting space and exposing that the author has not thought through their content differences.

**Method**: clearly separate the role / word-count budget for each.

| Segment | Word count | Main question to answer | Audience | Key constraint |
|---|---|---|---|---|
| **TL;DR** | 3-5 lines | What was done + key results + why it matters | All readers (especially those who close after this section) | Do not use undefined terms; do not hide key numbers |
| **Abstract** | 150-300 字 | TL;DR content + method overview + experimental setup + main numbers + limitations | Search engines, peer reviewers, archival systems | Self-contained, independently retrievable; contains at least 1 key number |
| **Introduction** | 1-2 pages | Background, why the problem is hard, gaps in prior work, contribution list | Readers deciding whether to continue to L2 | The end MUST contain a bullet-list of contributions |

**Three-segment independent-read check**: pull the TL;DR, abstract, and introduction out and read them on their own — do they form a **complete story**? If not, the conclusion and arguments are disconnected and need a return pass. This is a hard constraint of Sec. G.3 G1 self-check.

**Common TL;DR anti-patterns**:

- **Too long**: > 5 lines / 200 字 → trim to 3-5 lines.
- **Uses undefined terminology**: "FlashAttention-3 + warp specialization + TMA" is gibberish to a non-domain reader → use What-only descriptions ("Attention's GEMM-fusion optimization on Hopper").
- **Hides key numbers**: "significant speedup" instead of "6.4× speedup" → write specific numbers.
- **No limitations**: a TL;DR without limitations looks polished but the reader will think "this is marketing copy" → give the single most important boundary.

**Applicability boundary**:

- Some contexts (e.g. internal weekly reports) do not need a formal abstract; keep only TL;DR + introduction.
- Academic-paper abstracts have journal word-count limits (typically 150-250 words), which may conflict with the guidance here — follow journal norms.
- TL;DR is NOT a "subtitle" — a subtitle is promotion; TL;DR is honest condensed content (including limitations).

> TL;DR / abstract evolution-form examples → [examples.md](examples.md) Sec. B.7.1.

---

## C Content Granularity

### C.1 What → Why → How Layering

**Phenomenon**: technical explanations are most easily inverted — directly giving the deepest How (instruction names, register allocation, mask semantics), driving surface readers away before they can see "what problem this paragraph is solving".

**Method**: every technical paragraph can be decomposed into three causal layers. **The core rule of "depth made accessible" is: What and Why serve all readers; How serves only deep readers.**

```text
What  : factual statement      (this code does X)
Why   : motivation & trade-off (why X instead of Y)
How   : implementation detail  (how X is implemented)
```

**Concrete operations**:

- One What sentence at the start of each paragraph.
- Immediately follow with a Why sentence (state principle / trade-off / constraint).
- Push How into code blocks, appendices, or collapsible regions.

**Key principles**:

1. **The three layers are independently readable** — surface readers reading only What works; mid-level readers reading What + Why works; deep readers read all three.
2. **Why MUST NOT be omitted** — if you cannot write the Why, you have not actually understood the decision; this is an efficient cognitive-blindspot check during writing.
3. **How MAY be linked out** — long code, exhaustive derivations MAY go to Listings / appendix / code repository; the main text need not be packed.

**Applicability boundary**:

- Very short factual statements (e.g. "we use PyTorch 2.5") need not be decomposed into three layers — that is configuration, not a technical decision.
- In pure-algorithm derivation sub-sections, What and How nearly overlap — write Why at the top of the section, develop How in the body.
- Analogies / metaphors are an "auxiliary means of Why", not a substitute — see Sec. C.2.

> Complete Before/After rewrite → [examples.md](examples.md) Sec. B.2.

---

### C.2 Terminology / Definition / Analogy Engineering

**Phenomenon**: term count is a first-order term in cognitive load — a 5,000-字 report with 20+ undefined abbreviations causes cross-domain readers to give up; but zero terminology makes domain experts find it verbose.

**Method**: govern by three dimensions — terminology, definition, analogy.

#### C.2.1 Terminology

- **First occurrence MUST give a definition or a clickable link.** This is the **only** hard constraint.
- **Abbreviations write the full form on first occurrence**: `FMA (Fused Multiply-Add)`.
- **A whole report SHOULD have a Glossary**, while keeping the term count within reason — for a 5,000-字 report, new terms **SHOULD** be ≤ ~15.

#### C.2.2 Definition

- **Prefer differential definitions**: "**X is Y, in contrast to Z**". Differential definitions are more precise than standalone definitions because they force you to clarify the boundary between X and the closest concept.
- **Provide a minimal example**: immediately follow the definition with a 1-2 line tiny example so the reader knows "in what scenario I would use this concept".
- **For ambiguous terms, mark "the semantics intended here"**: e.g. "throughput" means different things in different contexts (throughput / rate / IO bandwidth) — disambiguate.

#### C.2.3 Analogies and Metaphor Engineering

An analogy is a **scaffold**, not a conclusion. Immediately after stating an analogy, add **the analogy's boundary**.

- **Anti-example**: "A GPU warp is like a CPU thread" — wildly wrong; will mislead the reader for years.
- **Positive example**: "A GPU warp can be roughly viewed as 32 micro-threads forever executing the same instruction in lockstep; unlike CPU threads, branches inside a warp cause lane serialization (divergence), whereas CPU threads are independent."

Two prompts for constructing analogies:

- The object I am studying — what does it look like / what is its structure like in everyday life? ("A cell is like a machine"; "a neural network is like a circuit diagram".)
- The process I am studying — how does it operate similarly to a daily phenomenon? ("Magnetic attraction is like personalities-complement attracting each other"; "a cache miss is like going to the warehouse to fetch goods instead of grabbing them from the shelf".)

Good analogies have replicable patterns:

| Abstract concept | Analogy | Why it works | Boundary (the mandatory follow-up) |
|---|---|---|---|
| **Network congestion control / packetization** | 「数据包 = 鞋盒大小的包裹，链路 = 高速公路上行驶的卡车」 | 把抽象的「带宽 / 延迟 / MTU」映射到读者熟悉的物理运输 | 类比不解释丢包重传与拥塞窗口的反馈控制——这是 TCP 的真正复杂性 |
| **Elastic memory of a rubber gasket** | 「像橡皮筋——无论怎么拉扭都试图恢复原形」 | 直接调用读者已有的肌肉记忆 | 类比不解释温度对弹性模量的非线性影响——高温下材料会丧失「记忆」 |
| **Cellular network seamless handoff** | 「像田径接力赛——接力棒（信号）在跑者（基站）之间传递，比赛（通话）从不中断」 | 把同步切换的难点替换成易理解的「交接动作」 | 类比不解释切换失败时的重连开销与上下文丢失 |

**The biggest pitfall of metaphor engineering**: using the analogy as the conclusion. Analogies should only be used to **kick-start the reader's cognition**, not as a precise guide for engineering implementation. Once an analogy extends past its boundary (e.g. using warp ≈ CPU thread to derive warp scheduling behavior), you have planted a misconception that will be remembered for years.

**Applicability boundary**:

- Internal communication MAY skip the "analogy boundary" follow-up; **public-facing reports MUST include it** — once an analogy spreads, it leaves its original context.
- Mathematical definitions, physical formulas, and protocol specifications do not need analogies; analogies suit "wanting non-domain readers to gain intuition".
- The same report MUST NOT use **conflicting analogies for the same concept** (analogizing one concept as different things in two places) — this destroys the reader's mental model.

---

### C.3 Signal-to-Noise Ratio and Paragraph Structure

**Phenomenon**: the most common "visibly low quality" in technical reports is noise — adjective and adverb pile-ups ("significantly", "very", "substantially"), passive-voice flooding, ambiguous chained pronouns. Deleting these noise paragraphs would not break the conclusion — but they consume the attention budget for truly critical information.

**Method**: govern at paragraph, sentence, and overall granularity.

#### C.3.1 Paragraph level

- **One argument per paragraph**. The argument goes in the paragraph's first sentence (topic sentence).
- **Paragraph length controlled at 4-6 sentences**. Split when over.
- **A paragraph SHOULD be skeleton-readable from its first sentence alone** — this is the fastest check on paragraph quality.

#### C.3.2 Sentence level

- **Subject explicit; avoid pronoun chains**. Ambiguous "it" is the #1 killer in technical writing.
- **Active voice preferred** (unless the passive party truly needs emphasis).
- **Split long sentences, but do not deliberately shorten to lose logical connection**.

#### C.3.3 Signal-to-noise ratio

- **After reading each paragraph, ask**: "If this paragraph is deleted, does the report's conclusion fall apart?" If no, delete or merge.
- **Adjectives and adverbs are noise heavyweights**: "significantly", "very", "substantially" — replace with specific numbers when possible.
- **Transition words MAY be deleted**: "Regarding this issue, we did some research and found…" → just "Our research shows…" (or directly give the number).

**Applicability boundary**:

- Mathematical derivations and code listings do not follow the "4-6 sentence" rule — their "paragraphs" are divided by formula / function.
- Abstract / TL;DR MAY have one paragraph over 6 sentences (because it is condensed conclusion).
- In long-form white-paper "executive summary" sections, some noise is allowed for narrative; the body MUST stay strict.

> Complete Before/After rewrite → [examples.md](examples.md) Sec. B.3.

---

### C.4 Limitations Honest Expression

**Phenomenon**: many authors write limitations like a "self-criticism" — afraid of making the method look ineffective and afraid of giving reviewers ammunition. The result is something like "performs slightly worse in some cases", which conveys no information.

**Method**: position limitations as the **entry point to future work**, not as self-criticism. The mark of professionalism is **the ability to describe failure boundaries with specific numbers**, not "in some cases".

| Phrasing | Information density | Qualified? |
|---|---|---|
| "Our method underperforms in some scenarios." | 0 | ✗ |
| "When input sequence length > 8192, due to SRAM capacity limits on tile size, our method degrades to 1.2× of baseline; for short-sequence (seq_len ≤ 1024) scenarios, it stably reaches 3.5×. This is the tile-size upper-bound issue discussed in Sec. 6.3; future work (Sec. 7.2) will mitigate via hierarchical tiling." | High | ✓ |

**Concrete practice for honest expression**:

1. **Use specific numbers to describe failure boundaries**: not "in some cases", but "when input > 8192, degrades to baseline 1.2×".
2. **Categorize limitations**: known / unknown; given (dataset / hardware-inherent limits) / improvable (implementation-level optimizations).
3. **Leave entry points for follow-up readers**: "Future Work" or "Open Problems", anchored by section number or external link.

**Why honest limitations actually raise professionalism**:

- The reader assumes "details you do not actively disclose hide unfavorable factors" (see Sec. E.3 fair-comparison golden rule). Specific failure boundaries dispel suspicion.
- Reviewers will hunt the worst-case themselves; pre-listing it brings the "attack surface" into manageable scope.
- The act of writing failure boundaries exposes places the method has not been thought through — a cognitive bonus triggered by writing.

**Applicability boundary**:

- Under data-confidentiality / commercially-sensitive contexts, you MAY use relative values instead of absolute (e.g. "degrades 30% on input class X"), but you **MUST NOT** omit "on input class X" — that condition.
- Early exploratory reports (POC) MAY use "not yet tested" as a limitation, but MUST list **tested** vs. **untested** boundaries explicitly.
- Do NOT write "no obvious limitations" in the TL;DR — that effectively declares the report as marketing copy.

> Complete Before/After rewrite → [examples.md](examples.md) Sec. B.1; GPU reduction limitations passage → [examples.md](examples.md) Sec. B.7.6.

---

### C.5 Intro-Summary Three-Part

> ★ **Core section** ★ — "Intro-Summary / Details / Takeaway three-part" yields the highest single-point rewrite gain. (Also covers Clarity Four Pillars; the heading uses the short form to keep the cross-bundle anchor stable.)

**Phenomenon**: "clarity" is often discussed as a feeling, but it actually rests on 4 independently checkable pillars — each pillar corresponds to a specific failure mode. Among them, **"brevity" is the most often misused** — most authors misread it as "writing paragraphs short / cutting details", losing the report's core value.

**Method**: first identify the 4 pillars, then use Intro-Summary three-part to land "layered brevity".

#### C.5.1 The 4 Clarity Pillars

| Pillar | Failure mode | Repair |
|---|---|---|
| **Precision** | Substituting vague terms for concrete values ("improved", "significantly", "faster") | Replace with numbers or verifiable definitions |
| **Brevity** | Misinterpreting brevity as "cut details" | Use Intro-Summary three-part (Sec. C.5.2) |
| **Familiarity** | Overuse of unfamiliar terms; pile-up of abbreviations | First-occurrence definition for every new term; same concept named consistently throughout |
| **Necessity** | Writing content that does not affect the conclusion | Delete paragraphs / figures / citations that do not contribute to the conclusion |

#### C.5.2 Brevity ≠ cutting details (core method)

In technical reports, **details are often the report's value itself** — readers come to your report because they cannot get such details elsewhere. Reading "brevity" as "writing paragraphs short / cutting details" is the most common mis-reading in technical writing.

The correct reading of brevity is:

> **Give every detail passage a concise entry and exit, not write the passage itself short.**

The concrete actionable pattern = **Intro-Summary / Details / Takeaway three-part**:

```text
┌─────────────────────────────────────────────────────┐
│  Intro-Summary  (1-3 sentences)                     │  ← brief
│    • What problem this section solves /             │
│      what the argument is                           │
│    • A surface reader can decide here whether       │
│      to continue                                    │
├─────────────────────────────────────────────────────┤
│  Details  (body, as deep as needed)                 │  ← not brief, but necessary
│    • Complete technical details, derivations,       │
│      code, parameters, edge conditions              │
│    • Never cut for brevity — this is the            │
│      report's hard currency                         │
├─────────────────────────────────────────────────────┤
│  Takeaway  (1-3 sentences)                          │  ← brief
│    • The single most valuable conclusion of         │
│      this section                                   │
│    • Bridge to the next section / overall argument  │
└─────────────────────────────────────────────────────┘
```

This pattern has three core gains:

1. **Surface readers get a free skeleton**: stringing together every section's Intro-Summary + Takeaway gives the entire argument chain.
2. **Deep readers are not forcibly simplified**: the middle Details can go as deep as needed, adapting per section from instruction-level to distributed-system-level.
3. **The author benefits in reverse**: before writing the Intro-Summary, you must answer "what is this section's actual argument" — this exercise itself exposes things that were unclear during writing.

#### C.5.3 Complete Before / After comparison

> A GPU-kernel-optimization sub-section demonstrates the correct shape of "details unchanged, wrapped in a concise entry and exit".

**Before** (raw details; surface readers immediately turn away):

> ### 5.3 Warp Shuffle 优化
>
> 我们使用 `__shfl_down_sync(0xffffffff, val, offset)`，offset 从 16 递减到 1，每次将 lane (i+offset) 的值加到 lane i 上。该指令需要 SM ≥ 70，在 Volta 之前的架构上需要使用旧的 `__shfl_down`。注意 mask 必须包含所有参与 reduce 的 lane……（继续 200 字）

**After** (Intro-Summary entry → Details → Takeaway exit):

> ### 5.3 Warp Shuffle 优化
>
> **Intro-Summary**：本节将最后一轮 reduction 从 shared memory 路径迁移到 warp 寄存器路径，省去 5 次 `__syncthreads`，是 V1 → V4 加速的主要来源。
>
> **Details**：（原来的 200 字技术细节，**一字未删**，包括 mask、SM 版本、回退路径）……
>
> **Takeaway**：warp shuffle 的本质收益不是「指令更快」，而是「省掉同步」。任何 reduction 类 kernel 的最末 5 轮都值得检查是否能改写为 shuffle。

**Key observation**: After's Details section is **identical to Before** — no detail was cut, only a concise entry and exit were wrapped around it.

> Exhaustive Before/After comparison (with word-count tables / different-granularity tables / multi-scenario demonstrations) → [examples.md](examples.md) Sec. B.5.

#### C.5.4 Intro-Summary Three-Part Across Granularities

| Granularity | Intro-Summary form | Details form | Takeaway form |
|---|---|---|---|
| **Whole report** | TL;DR (Sec. B.3) | All chapters | Conclusion & future work |
| **Chapter** | Chapter-opening paragraph | Sub-sections | "Chapter summary" at the end |
| **Section** | First 1-3 sentences | Section-internal details | Closing 1-3 sentences |
| **Paragraph** | Topic sentence | Paragraph-internal argumentation | Closing bridge sentence (optional) |

**Minimum**: **every section** MUST have Intro-Summary and Takeaway. Chapter-level and paragraph-level are bonus.

**When omission is allowed**:

- Very short sub-sections (< 100 字).
- Pure-definition sub-sections (e.g. glossary entries).
- Pure code listings.

All other cases MUST include them.

**Applicability boundary**:

- Intro-Summary is NOT a "subtitle expansion" — a subtitle names; Intro-Summary states an argument.
- Takeaway is NOT a "content summary" — a summary repeats what has been said; Takeaway is "the single sentence most worth carrying across sections".
- Relationship to Sec. B.2 report-level progressive disclosure: Sec. B.2 is L1-L4 report-level; this section is section-level. Together they form the "report → chapter → section → paragraph" four-tier progressive-disclosure system — the reader can "brake" at any level.

---

### C.6 RFC 2119 Modal Verbs

**Phenomenon**: in technical reports (especially design solutions, requirement specifications, compliance reports), authors mix "should", "needed", "recommended" — at acceptance time, arguments are inevitable: is it "mandatory" or "recommended"? The strength is unrecognizable.

**Method**: strictly distinguish modal-verb semantics per RFC 2119 / ISO/IEC Directives Part 2. A professional report **MUST hold this distinction throughout**.

| Modal verb | Strict semantics | Consequence on violation | Application example |
|---|---|---|---|
| **MUST / SHALL** | Absolutely mandatory | System acceptance fails; compliance fails; safety risk | "When the system temperature exceeds 85°C, the control module **MUST** trigger automatic shutdown" |
| **SHOULD** | Strongly recommended; deviation requires justification | Deviation requires written rationale | "Logs **SHOULD** auto-rotate every 24 hours" |
| **MAY** | Grants permission / optional | Not implementing is also compliant | "Advanced users **MAY** export configuration as JSON via CLI" |
| **WILL** | Statement about a future fact (not a requirement) | Does not constitute a requirement constraint | "The satellite **WILL** encounter high-intensity cosmic radiation in this orbit" |
| **MUST NOT / SHALL NOT** | Absolutely forbidden | Treated as an immediate error | "The reset flow **MUST NOT** clear encrypted key shards" |

#### C.6.1 Practical points

- **Do NOT mix**: in the same report, if one item uses MUST, another item of equal importance **MUST NOT** be written as should or will.
- **Chinese-writing equivalents**:
  - MUST / SHALL → 「必须」 / 「应当」 (recommended to keep the English ALL-CAPS form to avoid ambiguity)
  - SHOULD → 「应」 / 「宜」
  - MAY → 「可」 / 「允许」
  - WILL → 「将」 / 「会」 (neutral statement)
- **Declare on first occurrence**: in the introduction or appendix glossary, state explicitly "this report uses MUST/SHOULD/MAY with the semantics defined in RFC 2119 / ISO/IEC Directives Part 2".
- **Avoid MUST/SHOULD in Results & Discussion sections**: MUST/SHOULD is requirement semantics and should not appear in "we observed X" descriptive prose — there, use "is / was" / "observed".

#### C.6.2 Implicit pitfalls in Chinese writing

「应当」 in Chinese can be read **either** as SHOULD (recommendation) **or** as MUST (mandatory). If your reader population is cross-language or cross-jurisdiction, **strongly recommend** parenthesizing the English equivalent in Chinese reports: 「应当（**MUST**）触发自动断电」.

**Applicability boundary**:

- Academic papers / exploratory research reports usually do not need strict modal-verb distinction (those are not requirement specifications).
- Design solutions / requirement specifications / compliance reports / API documentation **MUST** strictly distinguish.
- Using MUST/SHOULD in "Results & Discussion" sections is a common error — replace with neutral statements (is / was / observed).

> Complete Before/After rewrite → [examples.md](examples.md) Sec. B.6.

---

## D Visualization

### D.1 Three Criteria for Good Technical Visualization

**Phenomenon**: the standard for judging whether a figure is qualified is often simplified to "aesthetics" and "professionalism", but these two words are not actionable — what is wrong with the figure, how to fix it, the author themselves cannot articulate.

**Method**: use three independently checkable criteria to evaluate every figure.

| Criterion | Core question | Failure signal |
|---|---|---|
| **Information density** | Does each square centimeter convey enough effective information? | Too sparse → can be merged; too dense → should be split |
| **Abstraction level** | Does the figure's granularity match the reader's cognitive layer? | Drawing instruction-level details for a non-domain reader = wasting paper |
| **Misreading risk** | What is the reader most likely to misread? | Color encoding, axes, missing legend, visual misalignment |

**"One Figure, One Point"**: every figure MUST be capable of answering "what does this figure show" in one sentence. If you cannot, do not draw it. This is the core quality-check rule of Sec. D.5 anti-patterns and Sec. D.2 4-step flow.

**Applicability boundary**:

- Decorative illustrations (e.g. chapter-opening cover) do not apply this criterion — but MUST be labeled "decorative / non-data figure" in the caption.
- "Aesthetics" is not a criterion — aesthetics is a by-product of doing visualization right; it is not the goal.

---

### D.2 Code → Information → Model → Visualization 4-Step Flow

> ★ **Core section** ★ — downgrade "drawing figures" from an inspiration task to a repeatable engineering task.

**Phenomenon**: many authors faced with a piece of code / a system do not know what to draw, so they either skip drawing or draw an ad-hoc "screenshot + arrows" figure — and the figure itself becomes the report's weakness.

**Method**: a 4-step flow decomposes "from code to figure" into independently completable engineering actions. **MUST follow the order; do not skip steps.**

```text
                 ┌─────────────────────────────────────────┐
                 │  ① Raw code (high entropy, low abstraction, domain-bound) │
                 └──────────────┬──────────────────────────┘
                                │  Read: scan structure, identify roles
                                ▼
                 ┌─────────────────────────────────────────┐
                 │  ② Annotated code + key variable / invariant list │
                 └──────────────┬──────────────────────────┘
                                │  Distill: drop noise, retain signal
                                ▼
                 ┌─────────────────────────────────────────┐
                 │  ③ Key fact list (5±2 items)            │
                 │     - Who is the hotspot / bottleneck / decision point │
                 │     - How data flows / how state transitions │
                 └──────────────┬──────────────────────────┘
                                │  Model: pick abstraction layer & metaphor
                                ▼
                 ┌─────────────────────────────────────────┐
                 │  ④ Mental model (pipeline / state machine / hierarchy tree) │
                 └──────────────┬──────────────────────────┘
                                │  Visualize: choose chart type
                                ▼
                 ┌─────────────────────────────────────────┐
                 │  ⑤ Final figure (one figure, one point) │
                 └─────────────────────────────────────────┘
```

#### D.2.1 Step 1: Read the code — structured reading

**Not from line 1 to the last line**, but scan along three dimensions:

- **Control flow**: branches, loops, jumps, parallel / serial structure.
- **Data flow**: what data comes from where, flows where, gets modified by whom.
- **Dependencies**: synchronization, calls, sharing among modules / functions / threads.

Tooling tips:

- Use the IDE's outline / symbol viewer to get the skeleton.
- Use `cflow` / `pycallgraph` / static analyzers to auto-generate call graphs as a draft.
- Profilers (Nsight Compute, perf, py-spy) tell you which paths are **actually** hot rather than **apparently** hot.

#### D.2.2 Step 2: Distill information — what is "signal"

Not all information is worth drawing. **Signal** means:

- **Decision points**: branch conditions, configuration parameters, mode switches.
- **Bottlenecks**: memory bandwidth, synchronization, cache misses, long-tail latency.
- **Invariants**: loop invariants, data-structure constraints, safety guarantees.
- **Phase-change points**: locations where behavior qualitatively changes (capacity threshold, parallelism threshold).

**Practical tip**: write a 5±2 bullet list describing "the things I most want the reader to know about this code". This list is the figure's skeleton.

#### D.2.3 Step 3: Build a mental model — choose the abstraction layer

The same code can be drawn at different layers. **Layer mismatch is the most common visualization error** — drawing instruction-level timing diagrams for non-domain readers is gibberish; drawing algorithm-level abstraction for an experienced GPU engineer wastes paper.

| Layer | Concerns | Suitable scenarios |
|---|---|---|
| **Instruction level** | SIMT, warp scheduler, pipeline | Compiler / micro-architecture research |
| **Operator level** | Kernel launch, tile, shared memory | GPU kernel optimization reports (most common layer) |
| **Algorithm level** | Control-flow graph, state transitions, complexity | Algorithm explanations, research papers |
| **System level** | Services, queue, storage, network | Architecture design documents (→ Sec. D.6 C4 model) |
| **Semantic level** | User-perspective state / operations | Product documentation, UX design |

Selection strategy:

1. First match the imagined reader's cognitive layer.
2. At that layer, abstract the model to **3-5 basic elements + relationships among them**.
3. Elements MUST be able to "move" in the head — pipelines flow, states switch, hierarchies expand.

Common mental-model templates:

- **Pipeline / Dataflow**: boxes + arrows; data flows left to right.
- **State machine**: circles + transition arrows; temporal states.
- **Hierarchy / Tree**: layered structure, component containment.
- **Heatmap / Map**: 2D quantity field (heat, memory, latency).
- **Timeline / Gantt**: events on a time axis, concurrency.
- **Scatter / Line**: performance-parameter relationship.

#### D.2.4 Step 4: Implement the visualization — choose the chart type

**Only at this step do you start drawing. Choose the type first, then choose the tool.**

| What you want to express | Recommended chart |
|---|---|
| Flow / algorithm steps | flowchart (Mermaid `graph LR`) |
| Call relationship / dependency | call graph, Mermaid `graph TD` |
| Sequence / concurrency | sequence diagram, timeline, Gantt |
| State transitions | state diagram |
| Performance vs. parameter | line plot / scatter plot |
| Performance vs. theoretical upper bound | Roofline plot |
| CPU hotspot distribution | flame graph |
| Memory layout / cache behavior | ASCII grid, heatmap |
| System architecture | block diagram + interface protocols; multi-layer abstraction uses C4 (→ Sec. D.6) |
| Complexity evolution | multi-curve line plot (log scale) |

**5 design principles**:

1. **Data-Ink Ratio (Tufte)**: reduce decoration, gridlines, shadows, 3D effects.
2. **Functional color**: each color MUST encode one variable; do not use color for aesthetics. Color-blind-friendly (avoid red-green pair carrying information alone).
3. **Legend and units complete**: x-axis, y-axis, units, ticks, legend — none MAY be missing.
4. **Self-contained**: figure + title + annotations + legend MUST let the reader understand the gist **without reading the body**.
5. **Caption states the argument, not the description**: caption SHOULD say "this figure shows X" rather than "the x-axis is Y".

#### D.2.5 Feedback loop

If the final figure cannot be summarized in one sentence, **return to Step 2 to re-distill the signal — do NOT patch the figure piecemeal**. A Step 4 failure is almost always an incomplete Step 2 / Step 3.

**Applicability boundary**:

- Data figures (line / bar / scatter) reduce the 4-step flow to "data cleaning → axis & unit selection → chart selection → caption" — but the first two steps still cannot be skipped.
- Profiler-built-in figures (Nsight, perf flame graph) usually have walked through Step 1-3; the author only walks Step 4 — but the caption MUST be self-written.
- The 4 steps are a one-way flow; do NOT reverse-adjust Step 2's fact list at Step 4 — this means the figure is dictating the argument, which is backwards.

> Complete 4-step derivation (walked through with the GPU reduction kernel) → [examples.md](examples.md) Sec. B.9.

---

### D.3 Common Visualization Patterns Catalog

**Phenomenon**: authors know they need a figure but do not know which type to choose; or they always default to one type (e.g. bar chart), so every problem looks like something a bar chart can solve.

**Method**: choose the most appropriate chart type by problem domain.

| Pattern | Best for | Not for |
|---|---|---|
| **Flowchart** | Decision trees, configuration choices, report-section navigation | Scenarios with cycles or concurrency between states |
| **Dataflow diagram** | ETL, signal processing, ML pipeline | Control-flow-dominant scenarios |
| **Call graph** | Code organization, dependency analysis | Performance analysis (use flame graph instead) |
| **Class / component diagram** | System architecture (→ Sec. D.6 C4 model) | Business processes |
| **Roofline** | Memory vs. compute bottleneck (GPU, SIMD, AI) | Single-point performance numbers (use a table) |
| **Flame graph** | CPU profile, sampling profile | Async / event-driven scenarios (use timeline) |
| **Timeline / Gantt** | Async tasks, kernel stream, distributed | Single-thread pure-compute scenarios |
| **State diagram** | Protocols, lifecycle, algorithm states | Data transformation / compute flow (use dataflow) |
| **Memory layout** | Cache line, padding, SoA vs. AoS | Control flow |
| **Pipeline diagram** | Pipeline depth, stalls, bubbles | Non-pipelined architectures |
| **Heatmap** | Access pattern, attention weights, performance vs. config matrix | 1D data (use line) |
| **Complexity-evolution plot** | Algorithm scaling as N grows | Single-point performance |

**ASCII catalog mini-figures** (for embedding small inline diagrams):

```text
                   ┌──── Roofline ─────┐  ← performance vs. arithmetic intensity
                   │  ▲                │     (suits: GPU optimization, SIMD, AI compute)
                   │  │ ░ /            │
                   │  │░/              │
                   │  /                │
                   │  └─────────►      │
                   └───────────────────┘

                   ┌──── Flame graph ────┐ ← CPU-time distribution
                   │ █████████ a()      │   (suits: performance analysis, hotspot localization)
                   │ ████░░░░░ b() c()  │
                   │ ██░░░░░░░ d()      │
                   └────────────────────┘

                   ┌──── Timeline ───────┐ ← concurrent activities
                   │ T0 ▒▒▒▒▒▒▒░░▒▒▒    │   (suits: kernel stream, distributed, network)
                   │ T1 ░░▒▒▒▒▒▒▒▒░░    │
                   │ T2 ▒▒▒▒░░░░▒▒▒▒    │
                   └────────────────────┘

                   ┌──── State machine ────────┐ ← algorithm state / protocol
                   │  (init) ──► running ──► done │   (suits: protocol, lifecycle)
                   │             │  ▲             │
                   │             ▼  │             │
                   │           paused             │
                   └──────────────────────────────┘
```

**Applicability boundary**:

- Within a single report, **SHOULD** keep the chart-type variety to ≤ 5; otherwise readers must re-learn the visual grammar each time.
- Chart type is independent of abstraction layer (Sec. D.2.3) — the same type can be drawn at different layers (e.g. a timeline can be drawn at kernel level or at distributed level).

---

### D.4 Toolchain (condensed)

**Phenomenon**: figure tools are over-abundant (Visio, PowerPoint, drawing apps, professional drafting IDEs), causing team-collaboration issues — inconsistent formats, undiffable versions, hard to be modified by an LLM.

**Method**: filter tools by three standards: **"diffable, version-controllable, LLM-comprehensible"**.

| Use | Preferred | Backup | Note |
|---|---|---|---|
| Flow / state / sequence | **Mermaid** | d2 | Markdown-native; supported by Cursor / GitHub; version-diffable |
| System architecture / topology | **d2** | draw.io / excalidraw | d2 is a newer text-based tool |
| Publication-quality figure | **TikZ / PGFPlots** | matplotlib + tikzplotlib | LaTeX ecosystem has the highest control |
| Data figures | **matplotlib / plotly** | seaborn | matplotlib is static; plotly is interactive |
| Roofline | **Empirical Roofline Tool / Nsight Compute** | Don't hand-draw | Industry standard |
| GPU profile | **Nsight Systems / Compute, `ncu`, `nsys`** | — | Industry standard |
| CPU profile | **perf, py-spy, Linux flame graph** | VTune | Pair with `flamegraph.pl` |
| Trace | **Perfetto / Chrome Tracing / VizTracer** | — | Browser-interactive |
| ASCII figure | **handwritten / asciiflow.com** | — | Suits small inline figures; version-diff-friendly |

**3 rules of thumb**:

1. **Prefer plain-text tools** (Mermaid, d2, TikZ, ASCII) — diffable, version-controllable, LLM-comprehensible-and-modifiable.
2. **Use the profiler's built-in figure when the profiler ships one** — do not redraw; redrawing wastes time and introduces distortion.
3. **Hand-drawn figures cite the source**: when copying a figure from a paper, mark the source; for self-redrawn versions also write "Redrawn from [X] Fig. 3".

#### D.4.1 Image-format selection

| Figure type | Recommended format | Why |
|---|---|---|
| Schematics, flowcharts, architecture diagrams, vector illustrations | **SVG / PDF** (vector) | Scales without quality loss; works in papers and webpages |
| High-contrast screenshots, ASCII-rendered figures, pixel-precise requirements | **PNG** (lossless) | No JPEG-compression artifacts |
| Photography, natural images, color photos | **JPG** (lossy) | Small file size; visual differences hard to perceive |
| Data figures (line/scatter/bar) | **SVG / PDF** (preferred); backup PNG (≥ 300 dpi) | Vector for papers; PNG OK for slides |
| Animation / temporal demonstration | **GIF / WebM** | Avoid in static reports; use multi-frame PNG instead |

**Applicability boundary**:

- When the company has a mandatory tool standard, follow it (even if the tool is not in this table).
- One-shot brain-dump figures MAY use any tool, but archived versions SHOULD be converted to a diffable format.

---

### D.5 Visualization Anti-Patterns (8)

**Phenomenon**: figure-failure modes are highly enumerable — the following 8 cover 90% of cases.

**Method**: each item is paired with "symptom / repair", to be used as a visualization checklist.

| # | Anti-pattern | Symptom | Repair |
|---|---|---|---|
| **1** | **Over-decoration** | 3D bar charts, shadows, gradients, unnecessary icons | Remove all visual elements that do not carry information |
| **2** | **Wrong abstraction layer** | Drawing PTX-instruction timing for non-domain readers | First confirm the imagined reader, then choose the layer (→ Sec. D.2.3) |
| **3** | **Misleading colors** | Red simultaneously means "high" and "danger" | Color encodes a single variable; color-blind-friendly |
| **4** | **Missing legend / units** | "Performance" as the y-axis label (what's the unit?) | x-y axis + unit + legend + scale (log/linear), all complete |
| **5** | **Caption is a description, not an argument** | "Figure 3: test results on A100" ← useless | Write the argument: "Figure 3: FlashAttention achieves 7.6× speedup over the naive implementation when seq_len > 4K" |
| **6** | **Poor figure independence** | Have to read 3 paragraphs of the body to understand the figure | Figure + caption + on-figure annotations MUST be self-sufficient |
| **7** | **Screenshot used as a figure** | Direct paste of an IDE screenshot, profiler screenshot, no cropping | Crop the key region; overlay arrows / annotations; or redraw cleanly |
| **8** | **Overload in one figure** | One figure, 12 curves, 6 marker types | Split, facet (small multiples), highlight the main curve |

**Anti-pattern 5 is the most lethal** — a description-style caption is no caption. **Argument-style caption** sentence patterns:

- ✓ "This figure shows that X" / "本图表明 X"
- ✗ "Figure 3: test results on A100. The x-axis is batch size."

**Applicability boundary**:

- ASCII figures / early sketches MAY deviate from anti-pattern 1 (decoration), but the other 7 still apply.
- Internal-communication ad-hoc figures MAY relax the caption requirement, but published versions MUST be argument-style.

> Argument-style caption complete Before/After → [examples.md](examples.md) Sec. B.4.

---

### D.6 C4 Model (4-layer abstraction for system architecture diagrams)

**Phenomenon**: the most common failure mode in system architecture diagrams is **"drawing all abstraction layers in one figure"** — cross-service call arrows, class names, and database schemas all in one image; nobody understands it.

**Method**: the **C4 model** ([c4model.com](https://c4model.com/), Simon Brown) splits architecture diagrams into 4 independent layers; each layer draws only that granularity's elements. It is essentially Sec. B.2 progressive disclosure applied to architecture diagrams.

| Layer | Abstraction depth | Main elements | Target audience | Answers |
|---|---|---|---|---|
| **L1: Context** | Bird's-eye view | The system + external users + external systems | Executives, PMs, cross-team interface | "What is this system's boundary? Who uses it? What external systems does it depend on?" |
| **L2: Container** | Deployment unit | Microservices, frontends, database instances, message queues | Architects, SREs | "What independently running processes / services does the system consist of? How do they communicate?" |
| **L3: Component** | Module level | Internal modules of a container, interfaces, layers | Front-line developers | "What components make up this service? How are responsibilities divided?" |
| **L4: Code** | Class / function | Class diagrams, ER diagrams | Algorithm / data-model authors | "How are this component's key classes / tables organized?" (Usually omitted; the IDE auto-generates.) |

**4 core usage rules**:

1. **Do NOT cross layers in one figure** — L1 figures contain no microservices; L2 figures contain no class names.
2. **Each figure has a one-sentence caption**: "This figure is the ⟨L1/L2/L3/L4⟩ view of ⟨system name⟩".
3. **L1 and L2 are required; L3 on demand; L4 almost always omitted**.
4. **Unified legend**: box = container / component, arrow = dependency / call, color = inside vs. outside.

#### D.6.1 ASCII illustration (same system's L1 and L2)

```text
L1 Context (bird's-eye view; 1 box = 1 complete system):

┌─────────┐      ┌────────────────────┐      ┌──────────┐
│ User    │ ───▶ │ Inference Service  │ ◀──▶ │ Object   │
│ (browser)│      │ Platform (this sys)│      │ Store(S3)│
└─────────┘      └────────────────────┘      └──────────┘
                          ▲
                          │
                  ┌───────┴────────┐
                  │ Upstream biz    │
                  │ system          │
                  └────────────────┘


L2 Container (Inference Service Platform internals; 1 box = 1 independent run unit):

┌──────────────────────────────────────────────┐
│              Inference Service Platform       │
│                                              │
│   ┌────────┐   ┌─────────┐   ┌──────────┐   │
│   │ Front- │──▶│ API     │──▶│ Schedule │   │
│   │ end    │   │ Gateway │   │ Service  │   │
│   └────────┘   └─────────┘   └────┬─────┘   │
│                                   │          │
│                              ┌────▼─────┐    │
│                              │ Model    │    │
│                              │ Inference│    │
│                              │ Worker   │    │
│                              └────┬─────┘    │
│                                   │          │
│                              ┌────▼─────┐    │
│                              │ Redis    │    │
│                              │ Cache    │    │
│                              └──────────┘    │
└──────────────────────────────────────────────┘
```

**Applicability boundary**:

- Relationship between C4 and UML: UML has strict semantics but a complex rule set; beginners draw line spaghetti. C4 deliberately specifies only 4 abstraction layers + 4 basic element types (system / container / component / relationship), driving the cost of "drawing it right" to a minimum. **If your report is mainly for cross-functional teams, prefer C4 over UML.**
- Single-microservice / algorithm reports usually need only L1 (external interface); L2 / L3 MAY be omitted.
- Full product-architecture white papers need L1 + L2 + multiple L3s (one per key service).

---

## E Benchmark

### E.1 Experiment Prerequisites: 7-Item Disclosure

> ★ **Core section** ★ — any benchmark report MUST disclose these 7 items; missing any one means failure.

**Phenomenon**: the most common "reader-cannot-judge" failure in benchmark reports is **incomplete prerequisites** — the reader does not know the hardware / CUDA version / batch size / number of measurements / statistic / what was compared against, and so cannot decide "does this number hold for my case".

**Method**: **MUST simultaneously disclose the 7 items below**. Missing any one robs the reader of judgment — this is not a "style issue" but the integrity of the benchmark itself.

#### E.1.1 The 7 Prerequisites

1. **Hardware**: CPU model, GPU model, memory, interconnect (NVLink / PCIe?), node count.
2. **Software**: OS, kernel version, driver version, CUDA / cuDNN / compiler version, key library versions.
3. **Input**: dataset / data distribution / input scale (batch size, seq len, N), data type (fp16 / fp32 / bf16).
4. **Configuration**: compile options, runtime parameters, parallelism, key hyperparameters.
5. **Measurement / Sampling**: number of runs, warm-up runs, outliers discarded, timing method (CUDA events / `time.perf_counter` / etc.).
6. **Statistics**: used mean / median / p99 / max? Why? (Prefer median + IQR; see Sec. E.2.)
7. **Baseline**: compared against whom? Which version / implementation? Equally optimized? Same input / same hardware?

#### E.1.2 Recommended writing form

> Should appear in Sec. Experiments / Sec. Setup.

```text
> Hardware:    NVIDIA A100-SXM4-80GB, NVLink, 1× node
> Software:    Ubuntu 22.04, CUDA 12.4, PyTorch 2.5.0, cuDNN 9.1
> Workload:    GPT-2 layer forward, batch=32, seq=2048, fp16
> Config:      blockDim=256, gridDim=auto, -O3 -arch=sm_80
> Measurement: 100 runs after 10 warm-up; report median (IQR
>              in parentheses); CUDA events for timing
> Statistics:  median + IQR (long-tail robust)
> Baseline:    PyTorch native attention with same shape/dtype
```

#### E.1.3 The "Golden Rule"

> **Whatever details you do not actively disclose, the skeptic will assume you hid an unfavorable factor.**

Concrete manifestations:

- Not stating the GPU model → reader assumes it is some old-generation GPU you do not want to disclose.
- Not stating how many runs → reader assumes you tested once and cherry-picked the favorable number.
- Not stating whether the baseline is equally optimized → reader assumes you compared an optimized version against an unoptimized one.

**Applicability boundary**:

- Exploratory POCs MAY omit some items (e.g. statistics), but MUST explicitly mark "**not measured**" rather than silently omitting.
- Under commercially-sensitive contexts the hardware model MAY be redacted ("NVIDIA H-series flagship"), but the **category** cannot be omitted — readers MUST at least know whether it is GPU or CPU and which generation.
- The 7 prerequisites SHOULD be disclosed in one section, not scattered through the body. Centralized disclosure lets reviewers see at a glance whether it is complete.

> Benchmark 7-item filling form (GPU reduction complete example) → [examples.md](examples.md) Sec. B.7.4.

---

### E.2 Error / Variance / Confidence Interval

**Phenomenon**: a common statistical error in technical reports is **only giving point estimates** — "our method is 3× faster" — with no variance, no confidence interval. The reader cannot judge whether this 3× is stable or one-time luck.

**Method**: use median + IQR instead of mean + std (unless there is a specific reason), and report worst-case.

| Phrasing | Information density | Qualified? |
|---|---|---|
| "Our method is 3× faster." | 0 | ✗ |
| "Over 100 runs, median speedup 3.12× (IQR 3.05–3.18); worst case 2.91×." | High | ✓ |

#### E.2.1 Four statistical tips

1. **Prefer median + IQR over mean + std** — long-tail-robust, especially for GPU kernel / network latency scenarios with long tails.
2. **Report worst-case**, especially for latency-sensitive scenarios (inference SLA, real-time systems).
3. **Confidence interval beats point estimate**; for small samples (< 30) MUST be given.
4. **When the variance is too large to ignore** (IQR / median > 10%), use box plots or violin plots instead of bar charts.

#### E.2.2 When to use mean + std

mean + std applies when:

- Data is approximately normal (multiple independent physical measurements, sensor readings).
- Aligning with existing literature (e.g. a benchmark suite mandates mean + std).
- Doing parametric tests (t-test / ANOVA).

But even so, **SHOULD also give median + IQR** as a reference — an honest report gives both sets.

**Applicability boundary**:

- Single-run non-repeatable experiments (e.g. real-production sampling) MAY give only point estimates, but MUST mark "single run / not repeatable".
- Marketing-style numbers in promotional materials are out of scope (marketing MAY use the maximum) — but **academic / engineering reports MUST use median**.

---

### E.3 Common Pitfalls in Fair Comparison

**Phenomenon**: what readers trust the least is "your-optimized-version vs. the baseline's unoptimized version". Once they detect any unfair-comparison trick, the entire report's credibility goes to zero.

**Method**: 6 hard constraints for fair comparison (**MUST satisfy all**).

| # | Check question | Failure manifestation |
|---|---|---|
| **1** | **Did you optimize the opponent?** | Comparing your optimized method against the baseline's unoptimized version is fraud |
| **2** | **Same input?** | Precision (fp16 / fp32), batch, seq MUST be consistent |
| **3** | **Same hardware?** | Cross-generation GPU / different memory must be explicitly noted |
| **4** | **End-to-end vs. kernel-only?** | The two differ enormously; MUST be explicit |
| **5** | **Includes data loading?** | Some scenarios MUST include it; others MUST NOT |
| **6** | **Cold start vs. warm run?** | JIT compile, cache warm-up have huge effects |

**Golden rule (repeating Sec. E.1.3)**:

> Whatever details you do not actively disclose, the skeptic will assume you hid an unfavorable factor.

#### E.3.1 Practical practices

- If the baseline is an open-source project, **SHOULD** give commit hash / version.
- If the baseline cannot be strictly aligned with your method on some dimension, **MUST** explicitly state which dimension cannot align and why (e.g. "the baseline does not support fp16; comparison is done at fp32").
- Speedup numerator and denominator MUST be at the same dimension (do not compare your kernel-only method against an end-to-end baseline).

**Applicability boundary**:

- Exploratory POCs MAY compare against a rough baseline, but MUST mark "preliminary comparison; not strictly aligned".
- Cross-architecture comparison (CPU vs. GPU; different GPU generations) MAY be done, but **MUST** explicitly mark the architectural difference and discuss its impact.

---

## F Multi-Audience

### F.1 Three Reader-Type Differences

**Phenomenon**: "writing for engineers" is too coarse — technical-report readers almost always fall into three categories; their concerns, reading paths, and attitudes toward failure differ.

**Method**: identify the three reader-type perspectives and serve each explicitly in the report's design.

| Dimension | Engineer perspective | Researcher perspective | Decision-maker perspective |
|---|---|---|---|
| **What they want after reading** | Reuse, decide whether to ship, compare solutions | Reproduce, extend, compare with prior work | Approve / reject; allocate resources |
| **Key numbers** | End-to-end latency, cost, stability | Speedup, complexity, ablation | ROI, risk level, time window |
| **What they want from the method** | Simple / general / debuggable | Novel / rigorous / generalizable | Risk-controllable / team can absorb |
| **Attitude toward failure** | Failure affects production SLA | Failure itself is a finding | Failure = sunk cost |
| **What part they read** | Method + deployment recommendation + limitations | Method + ablation + comparison with prior work | TL;DR + recommendation + one key figure |
| **What they cite** | Internal systems, production data | Academic literature, benchmark suites | Business cases, competitor data |

**Applicability boundary**:

- Academic papers primarily serve researchers, but reviewers often have engineering backgrounds — academic reports SHOULD therefore also cover the engineer-perspective "can I reuse" conclusion.
- Internal technical reports primarily serve engineers and decision-makers; cross-team review brings in the researcher perspective.
- The three perspectives are NOT "three reader types each occupying 1/3 of the length" — they mean **opening one reading path per reader type within the same report** (see Sec. F.2).

---

### F.2 Path-based Reading

**Phenomenon**: if the three-reader-type differences (Sec. F.1) are not explicitly surfaced to the reader, they will read top-to-bottom and then give up. **Letting the three reader types each find their own path** is more effective than forcing them to read the same content.

**Method**: after the TL;DR, add a "Quick Navigation" paragraph that explicitly tells the three reader types their entry sections.

```text
TL;DR
  ├── Decision-maker path: jump to Sec. Conclusion → Sec. Recommendation → Sec. Risk and boundaries
  ├── Engineer path:        jump to Sec. Results summary → Sec. Deployment recommendations → Sec. Cost analysis
  └── Researcher path:      jump to Sec. Method → Sec. Ablation → Sec. Comparison with prior work
```

#### F.2.1 Four concrete practices

1. **After the TL;DR give a "Quick Navigation" paragraph**, explicitly telling the three reader types their entry sections.
2. **Section names friendly on multiple sides**: "Sec. 5 Method (incl. engineering implementation)" — instead of just "Sec. 5 Algorithm".
3. **Give multiple sets of key numbers**: relative speedup (researcher) + absolute latency (engineer) + cost savings (decision-maker).
4. **Multiple appendices**: reproduction script (engineer-friendly) + derivations / proofs (researcher-friendly) + one-page abstract (decision-maker-friendly).

#### F.2.2 Path-based reading example

> The same selection table opens one path for each of the three reader types — engineers read the "□" boxes for specific scenarios; researchers read complexity bounds; decision-makers read the evolution plan.

```text
Engineer perspective:
  □ K ≪ N + streaming / limited memory       → min-heap
  □ Offline + memory available + exact        → QuickSelect (introselect)

Researcher perspective:
  □ Worst-case guarantee                      → median-of-medians (deterministic O(N))

Decision-maker perspective:
  □ Distribution unknown / requirements may change → start with min-heap; controllable, explainable
```

**Applicability boundary**:

- Very short reports (< 1500 字) do not need Quick Navigation — the TL;DR itself is the navigation.
- Single-audience reports (e.g. internal team reports) MAY skip Quick Navigation, but **SHOULD still give a "core numbers" paragraph after the TL;DR** as the minimum skeleton.
- Do NOT write Quick Navigation as a "table of contents" — the TOC is structural; navigation is by reader intent.

> Complete path-based selection table → [examples.md Sec. B.8.5 Three-perspective selection](examples.md#b85-three-perspective-selection).

---

### F.3 Two Industrial Paradigms for Decision-Type Reports: Amazon 6-Pager / Google Design Doc

**Phenomenon**: the traditional academic structure (IMRaD) does not work well for "decision-type reports" — decision-makers cannot wait until Sec. 5 for the conclusion; engineering peers need to quickly recognize "is this the right thing to do".

**Method**: when the report leans toward Sec. A.4's "design solution / feasibility analysis" and the main reader is a decision-maker or engineering peer, use the **Amazon 6-Pager** or **Google Design Doc** paradigm. Both share a common feature: **forcing the author to write thinking through completely, rather than masking blanks with slides**.

#### F.3.1 Amazon 6-Pager (six-page memo)

Amazon internally bans slides for decision reporting and uses 6 pages (A4) of pure-text memos. At the start of a meeting, all attendees silent-read for 20 minutes before discussion.

| Section | Content | Word-count share |
|---|---|---|
| 1. Introduction (What & Why) | Current problem and its direct impact on the business bottom line | ~10% |
| 2. Goals | Measurable expected state: "what does success look like" | ~10% |
| 3. Tenets | Trade-off principles guiding this design (e.g. "consistency over availability") | ~10% |
| 4. State of the Business | Data snapshot: current metrics, latency, error rate; **anchored on data, not opinion** | ~25% |
| 5. Lessons Learned | Retrospectives on past attempts / failures | ~15% |
| 6. Strategic Priorities | Concrete action plan derived from the above | ~25% |
| Appendix | Detailed data, references | (not counted in body) |

**Why effective**:

- Pure text forces the author to complete the reasoning chain; slides can hide logical jumps with "I'll explain on the next slide".
- "State of the Business + Lessons Learned" force the author to write contrary evidence, reducing confirmation bias.
- Silent reading eliminates PPT-performance dynamics; everyone has equal reading time.

**Suitable scenarios**: cross-team / cross-level design or strategic decisions; "ship or not" type high-risk judgments; architecture-change reviews.

#### F.3.2 Google Design Doc (engineering design document)

Google promotes writing a design doc before writing code, as a tool to **reach organizational consensus + expose architectural defects + solidify organizational memory**.

| Section | Necessity | Description |
|---|---|---|
| Title + Authors + Status | Required | Status is Draft / In Review / Approved / Implemented |
| Context & Scope | Required | What problem is being solved; what is not (non-goals) |
| Goals & Non-Goals | Required | Explicitly list non-goals to prevent late scope creep |
| Design | Required | Overall architecture + key decision points + alternative comparison |
| API & Data Model | Conditional | Interface contracts, schemas, message formats |
| Considered Alternatives | **Strongly recommended** | List at least 2 alternatives and why they were not chosen |
| Cross-cutting Concerns | Required | Security, privacy, observability, rollback strategy |
| Phased Rollout | Conditional | Canary / pilot / rollout path |

**3 core principles**:

- **Write the doc first, code second**: before coding or experimentation, the design doc can expose fatal architectural defects at the lowest cost.
- **Include Considered Alternatives**: a design doc without alternatives almost certainly misses key trade-offs.
- **Doc and code co-evolve**: when facing many unknowns in a new feature, the design doc and a proof-of-concept code MAY interleave (assumption → verify → revise the doc), forming an agile loop.

#### F.3.3 Amazon 6-Pager vs. Google Design Doc differences

| Dimension | Amazon 6-Pager | Google Design Doc |
|---|---|---|
| Main audience | Decision-makers (executives, PMs) | Engineering peers |
| Main goal | "Approve or not" | "Is this the right thing to do" |
| Length | Strict 6 pages | Unlimited (typical 5-30 pages) |
| Alternatives | Included but brief | Must be detailed |
| Reading rhythm | 20-minute pre-meeting silent reading | Asynchronous review, repeated iteration |

**Applicability boundary**:

- One-shot decision reporting → Amazon 6-Pager.
- Pre-engineering design consensus → Google Design Doc.
- Academic or reproducibility-type reports → still IMRaD (→ Sec. B.1).

---

## G Workflow

### G.1 CODER Workflow

**Phenomenon**: the most common stuck point in technical writing is "facing a blank page, not knowing where to start" — essentially mixing "thinking" and "putting words on the page" into one cognitive action.

**Method**: the **CODER workflow** forces these two acts apart, into 5 independent actions. Each has a clear input, output, and forbidden mode.

```text
C  Collect   ─→  Gather all ideas, data, arguments, references (regardless of quality)
O  Outline   ─→  Organize raw material; build section skeleton and argument flow
D  Draft     ─→  Fill skeleton into prose, ignore grammar and formatting
E  Edit      ─→  Polish structure, content, style
R  Release   ─→  Handle formatting, figures, citations, metadata
```

| Stage | Input | Output | Core rule |
|---|---|---|---|
| **C** Collect | Task + existing data / code / literature | A pool of raw material | Do not judge during Collect; throw into the pool first, filter later |
| **O** Outline | Collection pool | Section skeleton + argument flow | Do not Draft until Outline is complete |
| **D** Draft | Outline | Complete first draft | Do not edit during Draft — let thoughts flow; typos and ungrammatical sentences are E's job |
| **E** Edit | Draft | Final-draft candidate | If a structural issue appears, return to Outline; do not patch on top of Draft |
| **R** Release | Final draft | Released version | Handle metadata, figure clarity, citation format |

**4 core rules**:

- **Do not judge during Collect**: throw into the pool first, filter later.
- **Do not edit during Draft**: let thoughts flow; typos and ungrammatical sentences go to E.
- **Do not re-conceive during Edit**: if you find a structural issue, return to Outline; do not patch on top of D's output.
- **The CODER workflow is iterative**: D-E typically loops 2-3 times; O may regress as needed.

**Applicability boundary**:

- Very short reports (< 500 字) MAY skip the Outline stage.
- Long reports SHOULD first write a "short-form skeleton" (~1,500 字) at stage D, let the team review once, then expand — to avoid mid-stream structural problems requiring a full rewrite.
- When LLM-assisting writing (→ Sec. G.5), the LLM mainly accelerates D and E; C and O SHOULD remain author-led.

---

### G.2 Drafting Order: Body → Conclusion → Introduction → Abstract

**Phenomenon**: a common rookie mistake is writing in reading order — first the abstract, then the introduction, finally the conclusion. This is wrong.

**Method**: drafting order is **completely opposite** to reading order. This is a counter-intuitive but **time-saving-the-most** rule.

> **Core reason**: the abstract must condense the entire text, but when you write the abstract you do not yet have the entire text.

| Stage | Order | Reason |
|---|---|---|
| 1 | **Method / experiment / results** (body main content) | This part is based on actually-completed work; most concrete, least uncertain |
| 2 | **Discussion / limitations** | Significance and boundaries can only be accurately assessed after the body is written |
| 3 | **Conclusion** | At this point the argument is clearest; can produce a truly self-sufficient conclusion |
| 4 | **Introduction** | At this point you most clearly know "where the report leads"; backwards introduction writes most accurately |
| 5 | **Abstract / TL;DR** | Last, because only now do you truly know what the most important thing in the entire text is |
| 6 | **Title** | Last; extract the most identifying keywords from the entire text |

**Rule of thumb**: rewrite the abstract at least twice — once during draft, once after the entire text is finalized. The larger the difference between the two versions, the more insight was gained during writing.

**Applicability boundary**:

- Scenarios with an explicit brief / template (e.g. standardized ADRs) MAY write in order, but the abstract / TL;DR SHOULD still be last.
- Academic-paper abstracts have journal-mandated word counts — but the order "write the body first, then compress to abstract" stays.
- Do NOT use "write body first" as an excuse to skip Outline — the CODER workflow's O stage (Sec. G.1) MUST still be completed before Draft.

---

### G.3 Five Gates Review

**Phenomenon**: "review" is often simplified to "ask a colleague to look it over", but **truly effective review is structured — five different perspectives in scan**. Five Gates: G1 author self-check / G2 technical peer / G3 cross-domain readability / G4 evidence and compliance / G5 final sign-off. Failing any one gate means the work should not be released.

**Method**: the Five Gates structured review decomposes "general review" into 5 different-perspective checks.

| Gate | Core question | Reviewer | Typical time | Output |
|---|---|---|---|---|
| **G1** Author self-check | Are reader / purpose / scope / assumptions / conclusions clearly stated? Sec. H self-check passed? | Author | 1-2 hours | A structurally complete first draft |
| **G2** Technical peer review | Method correctness, conclusions strongly supported by data, accurate differentiation from prior work | Domain engineer / researcher | 2-4 hours | Technical-issue list |
| **G3** Cross-domain readability | Can a technical reader from an adjacent field understand TL;DR + introduction + key figures | Adjacent-domain reader | 30-60 minutes | Wording / terminology issue list |
| **G4** Evidence and compliance | Figures complete, data traceable, citations standardized, confidential information handled | Author + editor / PM | 1 hour | Final-draft candidate |
| **G5** Final sign-off | Delivery goals met, reusable, archival requirements met | Project lead | 30 minutes | Released version |

#### G.3.1 How to write review comments

The value of review comments depends on **actionability**, not length.

| Phrasing | Qualified? |
|---|---|
| ✗ "This part is unclear" | Not actionable |
| ✓ "This claims X is not valid because of Y, but Sec. 6 gives Z data — recommend adding a sentence 'the relationship between Y and Z is …' to bridge" | "Problem + cause + recommendation" three-part |

#### G.3.2 Relationship to the self-check list

G1's core is running the Sec. H self-check (5 categories: before-writing / during-writing / visualization / data / after-writing). Completing it only passes G1 — G2 / G3 / G4 / G5 still need external perspectives.

**Applicability boundary**:

- Internal low-risk reports (e.g. weekly reports) MAY merge G2 + G3 into one gate; but G1 (self-check) and G5 (sign-off) MUST NOT be omitted.
- Academic paper peer review corresponds to G2 + G3; G4 / G5 are executed by the editorial board.
- High-risk architecture-change / safety / compliance reports **MUST** execute all 5 gates; do not merge.

---

### G.4 Docs-as-Code (condensed)

**Phenomenon**: technical reports not under version control suffer collaboration runaway — multiple versions everywhere, nobody knows the latest, and documents drift asynchronously from code.

**Method**: bring technical reports into the same engineering process as code. **5 practices**:

| Practice | Benefit |
|---|---|
| Plain-text formats: Markdown / LaTeX / AsciiDoc | Diffable, mergeable, greppable |
| Reports and code in the same repository | Doc and implementation co-evolve; avoids "doc trailing code" |
| Pull-request review of reports | Review records preserved and traceable |
| CI automation (spell-check, link-check, citation-format check) | Removes mechanical checks from manual review |
| Templating (YAML front-matter, citation style, figure style) | Avoid reinventing the wheel each time |

**Particularly recommended**: for deep technical reports with complex math, frequent literature citation, and cross-format output, **LaTeX or Markdown + Pandoc is almost the only sustainable engineering solution**.

**Applicability boundary**:

- When the team has not yet adopted version control, do not introduce a separate git for docs-as-code — git-ify the code first.
- One-shot brain-dump / drafts MAY use Word / Notion, but the archived version SHOULD be converted to plain-text format.

---

### G.5 LLM-assisted Writing

**Phenomenon**: LLMs significantly accelerate the path from "thinking clearly" to "putting it on the page", but without bounded use, they introduce hallucinated citations / wrong data / insight-less filler paragraphs.

**Method**: explicitly bound **what to let the LLM do** vs. **what NOT to let it do**.

| ✓ Let the LLM do | ✗ Do NOT let the LLM do |
|---|---|
| Draft boilerplate paragraphs (background, related work) | Think the argument through for you |
| Rewrite obscure sentences, check grammar | Fabricate citations / data / experimental results |
| Distill abstracts; generate Takeaway candidates | Make structural judgment for you (which section should contain what) |
| Check terminology consistency, expand abbreviations | Skip Sec. E.1 experimental disclosure |
| Generate Mermaid / table drafts | Judge result significance or meaning for you |

**Core principle**:

> Humans handle **insight, structure, judgment**; LLMs handle **acceleration, polish, coverage check**.

A technical report fully generated by an LLM almost certainly lacks unique insight — and unique insight is the technical report's core value.

**Applicability boundary**:

- LLM-drafted paragraphs MUST undergo author technical review — especially those involving numbers, citations, or mechanism explanations.
- LLMs do NOT replace Sec. G.3 Five Gates — LLMs cannot do G2 (technical peer review) or G5 (final sign-off).
- Any LLM-generated citation MUST be personally verified by the author (LLM citation fabrication is a high-frequency hallucination mode).

> **CODER workflow summary**: mature technical writing is not "write once and done"; it is **the CODER workflow drafting → reverse drafting order → Five Gates review → docs-as-code archival** — a complete engineering flow. Each stage has dedicated goals and check lists; mixing them lowers the quality at each stage.

---

## H Self-check Five Categories

> Pin this list at the bottom of your draft; run through it after each draft. **This is the concrete landing of Sec. G.3 G1 author self-check** — the first of the Five Gates is running these 5 categories.

### H.1 Before writing

- [ ] Is the imagined reader written down? Are the three reader-type personas (primary technical / secondary technical / decision) explicit? (→ Sec. A.2)
- [ ] Is the report primary purpose (research findings / design solution / feasibility / technical evaluation) chosen? (→ Sec. A.4)
- [ ] Is "what the reader can do after reading" written in one sentence?
- [ ] Has the section outline been MECE-checked? Any duplication or omission?
- [ ] Is the length form (short / medium / long) decided?

### H.2 During writing

- [ ] Does each section have an Intro-Summary at the start and a Takeaway at the end? (→ Sec. C.5)
- [ ] Does each paragraph have a topic sentence?
- [ ] Are terms defined or linked on first occurrence? (→ Sec. C.2)
- [ ] Is the What → Why → How layering clear? (→ Sec. C.1)
- [ ] Is the analogy followed by an "analogy boundary" sentence? (→ Sec. C.2.3)
- [ ] Are paragraphs kept to 4-6 sentences? Are long ones split? (→ Sec. C.3.1)
- [ ] Can adjectives / adverbs be replaced with numbers? (→ Sec. C.3.3)
- [ ] Are modal verbs used consistently (MUST / SHOULD / MAY strictly distinguished)? (→ Sec. C.6)

### H.3 Visualization check

- [ ] Can each figure's argument be stated in one sentence? (→ Sec. D.1 One Figure One Point)
- [ ] Does each figure's abstraction layer match the imagined reader? (→ Sec. D.2.3)
- [ ] Are the legend, units, axes complete? (→ Sec. D.5 anti-pattern 4)
- [ ] Does the caption state the argument, not the description? (→ Sec. D.5 anti-pattern 5)
- [ ] Is the figure self-contained (largely understandable without the body)? (→ Sec. D.5 anti-pattern 6)
- [ ] Is color encoding unambiguous and color-blind-friendly? (→ Sec. D.5 anti-pattern 3)
- [ ] Is the image format appropriate (vector vs. raster)? (→ Sec. D.4.1)
- [ ] Are system architecture diagrams layered per the C4 model (no cross-layer in one figure)? (→ Sec. D.6)

### H.4 Data and Benchmark

- [ ] **Benchmark 7-item disclosure** (hardware / software / input / config / sampling / statistics / baseline) all disclosed? (→ Sec. E.1)
- [ ] Median + IQR or mean + std? Why? (→ Sec. E.2)
- [ ] Fair-comparison six constraints checked: (1) opponent optimized? (2) same input (precision / batch / seq)? (3) same hardware? (4) end-to-end vs. kernel-only? (5) data loading included or excluded consistently? (6) cold-start vs. warm-run? (→ Sec. E.3)
- [ ] Are limitations **specific** (numbers describing failure boundaries)? (→ Sec. C.4)

### H.5 After writing (subtraction)

- [ ] Delete any paragraphs / figures / citations that do not contribute to the conclusion.
- [ ] Pull TL;DR, abstract, introduction out and read independently — does the story cohere? (→ Sec. B.3)
- [ ] String all Intro-Summaries together — does it form a complete skeleton? (→ Sec. C.5)
- [ ] Length control: any redundant expressions? Merge synonymous paragraphs.
- [ ] Have a **non-domain colleague** read TL;DR and Sec. 1—Sec. 3 — can they paraphrase the main argument? (Corresponds to Sec. G.3 G3.)
- [ ] Have a **domain expert** review Sec. Method + appendices — pick technical errors. (Corresponds to Sec. G.3 G2.)

---

### H.6 Anti-shortcut Sentinel

> **This skill ships no validator script.** Any script-style automated check (line count / field count / contains-keyword) is only an auxiliary signal; **validator pass ≠ qualified report** — content quality MUST be honestly reviewed by the author / reviewer. Claiming "passed lint / form check" does **NOT** constitute completion.
>
> Sec. H.1-Sec. H.5 above are NOT checkboxes but honest content reviews; any item answered "I'm not sure" is treated as not passed — return to the corresponding sub-section to repair. Common shortcut-gaming counter-examples (uniformly treated as unqualified): submitting an unreplaced templates demo placeholder, captions written as descriptions instead of arguments, limitations stated as "in some cases", benchmark sections missing any one of the 7 prerequisites, sections piling Details without Intro-Summary / Takeaway — all explicitly forbidden by this skill.
>
> The final criterion of the self-check is: **can the reader, without reading the body, follow the argument chain by reading the figures, captions, numbers, Intro-Summaries / Takeaways alone?**

---

## I Writing-layer Anti-Patterns

**Phenomenon**: the 15 items below cover 90% of writing-layer failures. Each pairs "symptom → repair" with the corresponding sub-section anchor.

**Method**: use as a quick-diagnosis checklist.

| # | Anti-pattern | Symptom | Repair |
|---|---|---|---|
| 1 | **Large blocks without sub-headings** | A whole page of unbroken text | Slice with sub-sections, lists, tables |
| 2 | **Terminology bombardment** | A paragraph contains 5+ undefined abbreviations | Glossary + first-occurrence expansion (→ Sec. C.2) |
| 3 | **Passive-voice flooding** | "Can be considered as", "has been proven" | Rewrite in active voice (→ Sec. C.3.2) |
| 4 | **Adjectives modify everything** | "Significantly accelerates", "very efficient", "vastly improves" | Replace with numbers (→ Sec. C.3.3) |
| 5 | **Figures as decoration** | Figure repeats what the body has said | One Figure One Point; delete redundant figures (→ Sec. D.1) |
| 6 | **Missing comparison** | Only your numbers; no baseline | Add baseline or same-scenario comparison (→ Sec. E.3) |
| 7 | **Hidden prerequisites** | No mention of hardware / version / parameters | Benchmark 7-item disclosure MUST be present (→ Sec. E.1) |
| 8 | **Conclusion inconsistent with abstract** | Abstract says X; conclusion says Y | Three-segment independent-read check (→ Sec. B.3) |
| 9 | **Too-long TL;DR** | Over 200 字 | Trim to 3-5 lines (→ Sec. B.3) |
| 10 | **Long code without annotations** | 200-line listing with no key annotations | Annotate key lines + paired explanatory text |
| 11 | **Future Work platitudes** | "Will extend to more scenarios in the future" | Give specific direction + expected challenge (→ Sec. C.4) |
| 12 | **No failure cases** | Only success cases | Add Sec. Limitations, quantified (→ Sec. C.4) |
| 13 | **Brevity misread as cutting details** | Detail-bearing paragraphs written too short | Use Intro-Summary three-part (→ Sec. C.5) |
| 14 | **Architecture diagram layer-mixed** | Services and class names in the same figure | Use C4 to split into L1 / L2 / L3 figures (→ Sec. D.6) |
| 15 | **Modal verbs mixed** | MUST and SHOULD used synonymously | Strict distinction; declare semantics on first occurrence (→ Sec. C.6) |

**Applicability boundary**:

- The anti-pattern list overlaps with Sec. H self-check — Sec. H is a "checks at each writing stage" perspective; this section is a "failure-mode enumeration" perspective. Complementary.
- Internal drafts MAY temporarily contain anti-patterns; the published version **MUST** be cleared.

---

## J Recommended Resources

> Filtered from the original 5-category resources (writing books / visualization / style guides / documentation frameworks / academic norms) down to the 5-8 most core items. Full lists in each origin.

**Method**: the 7 items below are "reading any one will step-change report quality" core resources.

1. **Edward Tufte, *The Visual Display of Quantitative Information*** — classic on data visualization. After reading, the figure anti-patterns (Sec. D.5) disappear naturally.
2. **Barbara Minto, *The Pyramid Principle*** — McKinsey-style conclusion-first thinking. After reading, TL;DR and Pyramid structure (Sec. B.1) become instinctive.
3. **Justin Zobel, *Writing for Computer Science*** — handbook for academic writing; required for CS students.
4. **[Diataxis](https://diataxis.fr/)** — framework dividing documentation into Tutorial / How-to / Reference / Explanation. The benchmark for documentation-system design.
5. **[c4model.com](https://c4model.com/) (Simon Brown)** — official C4 model docs (→ Sec. D.6). The minimum-cost specification for system architecture diagrams.
6. **[IETF RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)** — standard definition of MUST / SHOULD / MAY (→ Sec. C.6).
7. **[Google Technical Writing Course](https://developers.google.com/tech-writing)** — free online course covering actionable techniques across technical-writing layers.

**Applicability boundary**:

- This is a "minimum learnable resource set", not a complete reading list. If time allows, see each resource's domain for further reading.
- The above resources complement this skill — this skill is the reference and decision entry; the originals are deep dives on each topic.

---

> **End of reference.md** — compose-report skill bundle / s3 sub-agent.
>
> Jump: [SKILL.md](SKILL.md) · [examples.md](examples.md) · [templates/manifest.md](templates/manifest.md) · [templates/components/](templates/components/)
