---
name: compose-report
description: |
  Compose record-and-explain technical reports (experiment reports, benchmark
  reports, design docs, white papers, kernel optimization writeups, algorithm
  evaluations, feasibility studies, GPU optimization writeups). Primarily
  targets Chinese-language reports while remaining methodology-agnostic on
  output language.

  Integrates: 4-purpose decision matrix, 3-audience routing, layered
  Intro-Summary/Details/Takeaway, What→Why→How decomposition, RFC 2119 modal
  verbs, claim-driven visualization (Code→Info→Model→Viz 4-step, C4 model),
  Benchmark 7-item disclosure, median+IQR statistics, multi-audience routing
  (Amazon 6-Pager / Google Design Doc), CODER workflow + Five Gates review.

  Use when authoring documents that record findings, justify design choices,
  evaluate alternatives, or report measurements with honest limitation
  disclosure—not for marketing copy, tutorials, or how-to guides.
---

# compose-report

> **Decision entry and quick-reference skeleton.** Full methodology → [reference.md](reference.md); rewrite examples → [examples.md](examples.md); copyable section skeletons → section-skeleton assembly via [templates/manifest.md](templates/manifest.md) + components in [templates/components/](templates/components/).
>
> **Note on language scope**: This skill (SKILL.md, reference.md, templates/, IA-NOTES.md) is written in English. `examples.md` retains Chinese demo content and templates retain Chinese demo placeholders, because the skill primarily targets the composition of **Chinese-language technical reports**. Word-count units use `字` (Chinese characters) where the target output is Chinese.

---

## 2 Overview

This skill serves **record-and-explain** technical reports — a single document that simultaneously satisfies two **multiplicative** properties:

- **Recording**: key facts about the experiment / system are documented, reproducible, and auditable.
- **Explaining**: non-domain experts can understand the motivation, key decisions, and trade-offs.

If either dimension drops to zero, the entire document collapses in value. Covers: experiment reports, benchmark reports, kernel optimization writeups, design docs, white papers, feasibility studies, technical evaluations, ADRs.

**Out of scope**: marketing copy (focuses on "why trust us"), tutorials (focuses on "follow these steps"), how-to guides (focuses on "operational steps") — these three use different paradigms.

---

## 3 Quick decision: report primary purpose (pick 1 of 4, mandatory before writing)

The most important question before writing is not "what to write" but "**which type of report is this**" — the four types differ entirely in section ordering, evidence focus, and common pitfalls. Write **Report type = ⟨one of four⟩** at the top of the draft, and order sections by reverse-engineering from the "MUST front-load" column in the table below.

| Primary purpose | Reader's question | MUST front-load | Evidence focus | Most common error |
|---|---|---|---|---|
| **Convey research findings** | Are the results trustworthy, novel, verifiable? | Research question / methodology overview / main results / limitations | Method transparency, experimental setup, error and reproducibility conditions | Stacking results without explaining significance and boundaries |
| **Propose design solution** | Why this approach instead of alternatives? | Requirements / constraints / solution comparison / trade-off rationale | Architecture diagrams, interface boundaries, alternative comparison matrix | Only describing "how to do" without "why this way" |
| **Feasibility analysis** | Can it be done; is it worth doing? | Assumptions / cost / risk / validation path / go-no-go criteria | Constraints, risk inventory, pilot metrics | Writing vision as conclusion, writing assumptions as facts |
| **Technical evaluation** | Which solution is better under what conditions? | Evaluation criteria / baseline / data sources / metric semantics | Controlled experiments, unified evaluation calibration, benchmarks | Inconsistent metric calibration; charts that fail to support recommendation conclusions |

> **Composite reports**: when carrying two primary purposes simultaneously (e.g. "design + feasibility"), use the more urgent one as the main thread and embed the other as a sub-section. Detailed methodology → [reference.md#a4-report-primary-purpose](reference.md#a4-report-primary-purpose).

---

## 4 Quick decision: reader persona (3 types, determines information density and ordering)

Before writing, write your "imaginary reader" in 1-2 sentences and pin it to the top of the draft. **Default assumption**: the reader is "smart but busy, and possibly unfamiliar with your sub-field" — neither underestimate intelligence nor overestimate domain context.

| Reader type | Typical identity | Cares about | Reading mode | What to give them |
|---|---|---|---|---|
| **Primary technical reader** (in-domain) | Peer experts, same-team colleagues, reviewers | Method soundness, ablation completeness, differentiation from prior work | Reads methods + experiments sequentially, skims introduction | Complete methods, ablations, precise comparison with prior work |
| **Secondary technical reader** (cross-domain) | Cross-disciplinary engineers, PhDs in adjacent fields, technical PMs | What this is; why it matters; whether it can be reused | Reads TL;DR, introduction, key figures, conclusion | Self-contained figures, necessary background, term definitions on first appearance, clear "can I reuse" verdict |
| **Management / decision reader** | Engineering leads, product owners, external reporting audiences | Cost-benefit, risk, recommend or not, ship or not | Reads only TL;DR + conclusion + key numbers | One-sentence verdict + quantified benefit + risk and boundaries |

> Path-based reading and multi-audience layering for each type → [reference.md#a2-reader-persona-three-types](reference.md#a2-reader-persona-three-types) · [reference.md#f2-path-based-reading](reference.md#f2-path-based-reading).

---

## 5 Quick decision: short / medium / long form section skeleton

| Template | Typical deliverable | Recommended section skeleton | Word count (字 = Chinese chars) | Use case |
|---|---|---|---|---|
| **Short** | Technical memo, design brief, evaluation memo | TL;DR; Introduction & scope; Method/proposal; Results/evaluation; Conclusion & recommendation; Necessary citations | 1,800–4,500 字 | Rapid synchronization of conclusion, solution selection, driving a single meeting decision |
| **Medium** | Formal technical report, project phase report, research summary | Cover/title; TL;DR + abstract; Introduction; Background & requirements; Method/design; Experiment or evaluation; Results & discussion; Limitations; Conclusion & recommendation; Citations; Short appendix | 5,000–18,000 字 | **Most common**; balances "make it readable" and "make it verifiable" |
| **Long** | White paper, complete R&D report, external technical statement, project summary | Front matter; TL;DR + abstract; Introduction; Background/related work/requirements; Method & implementation; Experiments & data; Results; Discussion; Limitations, risks & applicability; Conclusion; References; Multiple appendices | ≥ 18,000 字 | Complete archival, reuse, audit, external statement, or follow-up secondary research |

**Single rule for length**: short form merges sections; medium form keeps the main spine intact; long form systematically outsources "verifiability" to the appendix.

**Writing economics**: the longer the form, the more expensive a rewrite. For medium/long form, first draft a ~1,500-字 short-form skeleton, do one team review of structure and arguments, then expand to target length; rewriting mid-way through a long-form draft costs >10× the skeleton-stage rewrite.

Copyable skeletons → [templates/manifest.md](templates/manifest.md) (12 sequences for 4 types × 3 lengths) + [templates/components/](templates/components/) (32 components).

---

## 6 Information layering L1-L4 + Intro-Summary / Details / Takeaway three-part

"Layered supply" is this skill's core mechanism — **report level** uses L1-L4, **section level** uses Intro-Summary / Details / Takeaway three-part. Together they form a "report → chapter → section → paragraph" four-tier progressive-disclosure system, allowing the reader to "brake" at any level.

```
L1  TL;DR / abstract / key figure              ← 80% of readers stop here
L2  Body: motivation, method, key results      ← engineers usually stop here
L3  Method details, benchmark, ablation        ← researchers care about this
L4  Appendix: code, raw data, derivations,     ← only reproducers expand
    configurations
```

Each layer MUST be a self-contained closed loop: L1 decides whether to keep reading, L2 conveys the overall solution, L3 lets the reader judge method soundness, L4 enables reproduction.

**Section level = Intro-Summary / Details / Takeaway three-part** (the most broadly applicable, most easily executed pattern):

| Segment | Length | Role |
|---|---|---|
| **Intro-Summary** | 1-3 sentences | What problem this section solves / what the argument is; surface readers can decide whether to continue |
| **Details** | Body, as deep as needed | Complete technical content — derivations, code, parameters, edge conditions — **never cut for brevity** |
| **Takeaway** | 1-3 sentences | The single most valuable conclusion; bridge to the next section / overall argument |

**When to omit**: very short sub-sections (< 100 字), purely definitional sub-sections, pure code listings. All other cases MUST include it. **Brevity ≠ cutting details** — brevity means giving details a "concise entry and exit".

Detailed → [reference.md#c5-intro-summary-three-part](reference.md#c5-intro-summary-three-part); before/after rewrites → [examples.md#b5-layered-brevity-intro-summary-three-part](examples.md#b5-layered-brevity-intro-summary-three-part).

---

## 7 Ten core best practices

Each principle gives a one-sentence operational guide + counter-example trigger words + detail anchor. **Mentally run through these 10 before submitting** — saves ~70% rework versus reviewing after the draft is complete.

1. **One Figure, One Point**: every figure / table MUST answer "what does this show" in one sentence; if it cannot, delete it. Caption MUST state the **argument**, not the description (counter-example triggers: "Figure 3: Test results" / "Figure 4: Performance comparison chart"). → reference Sec. D.1 Sec. D.5 / examples Sec. B.4

2. **What → Why → How**: open each paragraph with a What sentence, immediately follow with a Why sentence (state principle / trade-off / constraint), push How down into code blocks, appendices, or collapsible regions. Reading backwards is the fastest way to spot a derailed report (counter-example trigger: opening with implementation details like `__shfl_sync(0xffffffff, ...)` without motivation). → reference Sec. C.1 / examples Sec. B.2 Sec. B.7

3. **Pyramid principle**: start with the conclusion, then expand to evidence; each layer satisfies MECE. Report level (L1-L2 top tier) + section level (Intro-Summary) — dual deployment lets surface readers extract 80% of the cognitive value from just the top tier. → reference Sec. B.1 Sec. B.2

4. **Define terms on first appearance**: first occurrence MUST give a definition or clickable link; abbreviations MUST give the full form on first occurrence (e.g. `FMA (Fused Multiply-Add)`). A 5,000-字 report SHOULD NOT introduce more than ~15 new terms; term count is a first-order term in cognitive load. → reference Sec. C.2

5. **Analogies need boundaries**: an analogy is a scaffold, not a conclusion. Immediately follow each analogy with "where this analogy breaks: X" — e.g. "A GPU warp can be roughly viewed as 32 micro-threads forever executing the same instruction in lockstep; unlike CPU threads, branches inside a warp cause lane serialization (divergence)." Analogies extended past their boundaries become misconceptions remembered for years. → reference Sec. C.2

6. **Visualization is a modeling process, not decoration**: code-to-figure follows 4 steps — read code → distill signals (5±2 bullets) → build mental model → choose chart type. Match the reader's cognitive layer (instruction / operator / algorithm / system / semantic level); layer mismatch is the most common visualization error. System architecture diagrams use the **C4 model** (L1 Context / L2 Container / L3 Component / L4 Code) for layered separation. → reference Sec. D.2 Sec. D.6 / examples Sec. B.9

7. **Benchmark 7-item disclosure complete**: hardware / software / input / configuration / sampling / statistic / baseline — **missing any one item is a fail**, the reader will assume an unfavorable factor was hidden. The preferred statistic is median + IQR (long-tail robust); samples < 30 MUST include confidence intervals; do not draw strong conclusions from mean + std. → reference Sec. E.1 Sec. E.2 / examples Sec. B.7

8. **Limitations stated honestly**: use specific numbers to describe failure boundaries ("when input sequence length > 8192, performance degrades to 1.2× of baseline") instead of "underperforms in some scenarios" (counter-example triggers: "in some cases" / "in most scenarios" / "significantly"). Failure cases and known weaknesses are signs of professionalism; position limitations as "entry points to future work" rather than apologies. → reference Sec. C.4 / examples Sec. B.1 Sec. B.7

9. **Subtraction after drafting**: delete any paragraph / figure / citation that does not contribute to the conclusion. Adjectives and adverbs are noise heavyweights ("significantly" / "very" / "substantially"); replace with concrete numbers when possible. The cost of redundancy is drowning the truly critical signal. → reference Sec. C.3 Sec. I / examples Sec. B.3

10. **Detail with concise entry/exit (Intro-Summary three-part)**: wrap every detail-bearing sub-section with **Intro-Summary → Details → Takeaway** three-part. The Details section is **never cut**; only a concise entry and exit are added around it. At minimum — every section MUST have Intro-Summary and Takeaway. → reference Sec. C.5 / examples Sec. B.5

> **Priority signal**: dry-runs most frequently flag principles 7, 8, and 10 (missing benchmark prerequisites / vague "in some cases" limitations / skipping Intro-Summary and going straight to details) — treat these three as the minimum delivery threshold. Modal verbs (MUST / SHOULD / MAY) MUST follow **RFC 2119** strictly in Sec. Requirements / Sec. Design sections, and MUST NOT be misused in descriptive sections like Sec. Results. → reference Sec. C.6 / examples Sec. B.6

---

## 8 CODER workflow + Five Gates review (quick reference)

This downgrades "writing a report" from a one-time inspiration task to a repeatable engineering process: ① **CODER workflow** drafting → ② reverse drafting order → ③ **Five Gates** review.

**CODER workflow** (forces "thinking" and "writing" into separate cognitive acts):

| Stage | Action | Core rule |
|---|---|---|
| **C** ollect | Gather all ideas, data, arguments, references (regardless of quality) | Do NOT judge during Collect |
| **O** utline | Organize raw material into section skeleton and argument flow | Reverse-engineer section order from the Sec. 3 report primary purpose |
| **D** raft | Fill the skeleton into prose, ignoring grammar and formatting | Do NOT edit during Draft |
| **E** dit | Polish structure, content, style | If a structural issue appears, return to Outline; do NOT patch on top of Draft |
| **R** elease | Handle formatting, figures, citations, metadata | D-E typically iterates 2-3 times |

**Reverse drafting order**: Method/Experiment/Results → Discussion/Limitations → Conclusion → Introduction → Abstract/TL;DR → Title. Rewrite the abstract at least twice (once during draft + once after the full text is finalized); the larger the gap between the two versions, the more insight was gained while writing.

**Five Gates** review (no release until every gate passes):

| Gate | Core question | Reviewer | Time | Output |
|---|---|---|---|---|
| **G1** Author self-check | Reader / purpose / scope / assumptions / conclusions clearly stated; Sec. 9 self-check passed | Author | 1-2h | Structurally complete first draft |
| **G2** Technical peer review | Method correctness, conclusions strongly supported by data, accurate differentiation from prior work | Domain engineer / researcher | 2-4h | Technical issue list |
| **G3** Cross-domain readability | Can a technical reader from an adjacent field understand TL;DR + introduction + key figures | Adjacent-domain reader | 30-60m | Wording / terminology issue list |
| **G4** Evidence and compliance | Figures complete, data traceable, citations standardized, confidential information handled | Author + editor / PM | 1h | Final-draft candidate |
| **G5** Final sign-off | Delivery goals met, can be reused later, meets archival requirements | Project lead | 30m | Released version |

Detailed → [reference.md#g1-coder-workflow](reference.md#g1-coder-workflow) · [reference.md#g3-five-gates-review](reference.md#g3-five-gates-review).

---

## 9 Anti-shortcut: validator pass ≠ qualified report

**This skill ships no validator script.** Any script-style check (line count / keyword existence / frontmatter fields) is auxiliary at best; **script-pass ≠ qualified report**. The sole criterion for qualification is the 6 **content self-checks** below — the agent MUST mentally run through them before every submission:

- **(a)** Report primary purpose explicitly chosen (Sec. 3, one of four), section skeleton aligned;
- **(b)** At least one fully developed What → Why → How three-tier passage (Sec. 7 principle 2);
- **(c)** Major sections all carry Intro-Summary + Takeaway (Sec. 6);
- **(d)** If the report contains benchmarks, the Benchmark 7-item disclosure is complete (Sec. 7 principle 7);
- **(e)** At least one figure caption states an argument rather than a description (Sec. 7 principle 1);
- **(f)** Limitations are quantified ("when N > 8K, degrades to 1.2×", not "in some cases"; Sec. 7 principle 8).

**Counter-examples (universally treated as unqualified / shortcut-gaming submissions)**:

- Submitting an unreplaced version of templates/ (preserving `<!-- DEMO from examples Sec. B.X — REPLACE -->` comments or demo sentences as-is);
- Captions written as "Figure N: Test results / Performance comparison chart" — this is a description, not an argument, no matter how polished the prose;
- Limitations stated as "in some cases" / "in most scenarios" / "may have performance issues" without specific thresholds or numbers;
- Benchmark sections missing hardware model / software version / sample count yet still reporting speedup ratios;
- Using MUST / SHOULD / MAY without declaring RFC 2119 semantics, or misusing them in descriptive sections like Sec. Results ("the system MUST be fast").

**No-shortcut declaration**: self-check is not a checkbox exercise but an honest content review. Any "form-passes-but-substance-fails" submission will be returned at G2 / G3 review; the sunk cost greatly exceeds an honest self-check.

---

## 10 Progressive-disclosure jump table

Jump by topic, **single-hop depth** — only jump to the corresponding section of reference / examples / templates, no further nesting.

**Entry files**:

- Full methodology → [reference.md](reference.md)
- Before / after rewrite examples → [examples.md](examples.md)
- Section skeleton templates → [templates/manifest.md](templates/manifest.md) (12 sequences for 4 types × 3 lengths) + [templates/components/](templates/components/) (32 components)

**Topic mapping**:

| Topic | Detailed → reference | Rewrite example → examples |
|---|---|---|
| 4 report primary purposes | Sec. A.4 | — |
| 3 reader personas / multi-audience layering | Sec. A.2 / Sec. A.3 | — |
| IMRaD / Pyramid / Diataxis structure comparison | Sec. B.1 | — |
| Information layering L1-L4 / progressive disclosure | Sec. B.2 | — |
| Abstract / introduction / TL;DR conventions | Sec. B.3 | — |
| What → Why → How layering | Sec. C.1 | Sec. B.2 Sec. B.7 |
| Terminology / definition / analogy engineering | Sec. C.2 | — |
| Signal-to-noise ratio / paragraph structure | Sec. C.3 | Sec. B.3 |
| Limitations honest expression | Sec. C.4 | Sec. B.1 Sec. B.7 |
| **Intro-Summary three-part (Clarity Four Pillars)** | Sec. C.5 | Sec. B.5 |
| RFC 2119 modal verbs | Sec. C.6 | Sec. B.6 |
| Visualization three criteria | Sec. D.1 | Sec. B.4 |
| Code → Info → Model → Viz 4-step | Sec. D.2 | Sec. B.9 |
| Chart catalog + toolchain | Sec. D.3 Sec. D.4 | — |
| 8 visualization anti-patterns (incl. Argument-style caption) | Sec. D.5 | Sec. B.4 |
| **C4 model** 4 layers | Sec. D.6 | — |
| **Benchmark 7-item disclosure** | Sec. E.1 | Sec. B.7 |
| Error / variance / confidence interval (median + IQR) | Sec. E.2 | Sec. B.7 |
| Fair comparison pitfalls | Sec. E.3 | — |
| Amazon 6-Pager / Google Design Doc | Sec. F.3 | — |
| GPU Reduction / Top-K complete example slices | — | Sec. B.7 Sec. B.8 |
| 5-category self-check / anti-pattern quick reference | Sec. H Sec. I | — |
| **CODER workflow** / drafting order / **Five Gates** | Sec. G.1 Sec. G.2 Sec. G.3 | — |

---

## 11 Glossary (consistent naming throughout)

The terms below are used **with consistent naming** across SKILL.md / reference.md / examples.md / templates/. Forbidden aliases as marked.

- **Intro-Summary / Details / Takeaway three-part**: the standard section-level progressive-disclosure pattern. Intro-Summary (1-3 sentences) states the argument; Details holds full content; Takeaway (1-3 sentences) gives the conclusion and bridge. **Forbidden aliases**: three-part alone / three-layer structure / TL;DR-Body-Summary / Intro-Body-Summary / 三段式 / 三层结构.
- **What → Why → How**: paragraph-level three-tier causality — What (factual statement) / Why (motivation, trade-off) / How (implementation detail). What and Why serve all readers; How serves only deep readers. **Forbidden aliases**: WWH / W-W-H layering.
- **Benchmark 7-item disclosure**: the seven mandatory disclosed items — hardware / software / input / configuration / sampling / statistic / baseline; missing any one is a fail. **Forbidden aliases**: experiment disclosure / bare "7-item disclosure" (always include "Benchmark") / 7 项前提.
- **C4 model**: four-layer system architecture abstraction — Context / Container / Component / Code. L1 and L2 are mandatory, L3 on demand, L4 almost always omitted. **Forbidden aliases**: bare "C4" / Context-Container-Component-Code spelled out.
- **CODER workflow**: five-stage drafting order — Collect → Outline → Draft → Edit → Release. Do not judge during Collect; do not edit during Draft; do not re-conceive during Edit. **Forbidden aliases**: bare "CODER" / 5-step workflow.
- **Five Gates**: G1 author self-check / G2 technical peer / G3 cross-domain readability / G4 evidence and compliance / G5 final sign-off — no release until every gate passes. **Forbidden aliases**: bare "G1-G5" / 5-gate review / 五道门.
- **Amazon 6-Pager / Google Design Doc**: two industrial paradigms for decision-type reports; first occurrence MUST include the vendor prefix. **Forbidden aliases**: bare "6-Pager" / bare "Design Doc".
- **Argument-style caption**: a figure caption that states a specific argument (e.g. "FlashAttention achieves 7.6× speedup at seq_len > 4K") rather than a description ("Figure 3: Test results"). **Forbidden aliases**: claim-driven caption / argumentative caption / 论点式 caption.
