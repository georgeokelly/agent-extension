# compose-report

> A reusable AI-agent skill for composing **record-and-explain** technical reports — experiment reports, benchmark reports, design docs, white papers, kernel optimization writeups, algorithm evaluations, feasibility studies, technical evaluations.

**Status**: ready for release (codex round-7 Approve, 28/28 carry-over closed across 7 review rounds)
**Bundle**: 5 top-level files + 32 components + 1 manifest = 37 files, ~2,800 lines

---

## What this skill does

Routes an agent through a 4-stage methodology for authoring documents that **record findings, justify design choices, evaluate alternatives, or report measurements with honest limitation disclosure**:

1. **Identify report primary purpose** (1 of 4: research-findings / design-solution / feasibility-analysis / technical-evaluation) — see [`SKILL.md`](SKILL.md) Sec. 3.
2. **Identify reader persona and length** (imagined reader; short / medium / long form) — [`SKILL.md`](SKILL.md) Sec. 4-5.
3. **Look up the manifest sequence** for `(report-type × length)` in [`templates/manifest.md`](templates/manifest.md) (12 sequences).
4. **Assemble template by component sequence** + fill DEMO placeholders + pass `SKILL.md` Sec. 9 6-item content self-check.

The skill is **language-agnostic on methodology** and **primarily targets Chinese-language reports**. Demo passages in `examples.md` and demo placeholders in components retain Chinese to model Chinese-report writing; English methodology and section headings ensure cross-language consistency.

## When to use

Use when authoring documents that:

- Record experimental findings, benchmark results, or measured behavior
- Justify a design or architectural decision (with quantified trade-offs)
- Evaluate alternatives with criteria-based comparison
- Assess feasibility with assumption / cost / risk analysis
- Disclose limitations honestly with quantified failure boundaries

**NOT for**: marketing copy, tutorials, how-to guides — these have different rhetoric and are out of this skill's scope.

## Quick start

```
1. Read SKILL.md
2. Decide report type + length per SKILL.md Sec. 3 + Sec. 5
3. Open templates/manifest.md → find your (type, length) sequence
4. Read the listed components from templates/components/ in order
5. Concatenate components (blank-line separators) → assembled template
6. Fill DEMO placeholders + actual content; adjust section ordinals ⟨N⟩
7. Run the 6-item content self-check at the bottom of self-check-base.md
```

## File layout

```
.
├── README.md                          # this file
├── SKILL.md                           # entry: decision tables, jump table, Glossary
├── reference.md                       # full methodology (Sec. A–J, ~1,400 lines)
├── examples.md                        # Before/After rewrite demos (Sec. B.1–B.9)
└── templates/
    ├── manifest.md                    # 12 sequences (4 types × 3 lengths)
    └── components/                    # 32 section-scoped components
        # Common (all sequences)
        ├── top-declaration.md         # warning + meta-instruction
        ├── tldr.md
        ├── background.md
        ├── conclusion.md
        ├── limitations.md
        ├── self-check-base.md         # 8 items mirroring SKILL Sec. 9
        # Method-stage
        ├── method.md                              # research / eval / design
        ├── considered-alternatives.md             # design / feasibility (medium+)
        ├── trade-off-matrix.md                    # design (medium+)
        ├── experiment-setup.md                    # research / eval (Benchmark 7-item)
        ├── results.md                             # research / eval
        ├── ablation.md                            # research / eval (medium+)
        ├── risk-register.md                       # design + feasibility
        ├── cost-analysis.md                       # feasibility
        ├── validation-path.md                     # feasibility
        ├── go-no-go.md                            # feasibility
        # Length-additive (long-only or medium+)
        ├── front-matter.md                        # long (cover / abstract / TOC)
        ├── system-overview-c4.md                  # long (research / eval / design)
        ├── related-work.md                        # long (research / eval / design)
        ├── scaling.md                             # long (research / eval)
        ├── robustness-cost.md                     # long (research / eval)
        ├── operations.md                          # long (research / eval / design)
        ├── references-appendices.md               # long
        # Quick navigation (medium+, type-specific)
        ├── quick-navigation-research.md           # research / eval (medium+)
        ├── quick-navigation-design.md             # design (medium)
        ├── quick-navigation-design-long.md        # design (long)
        ├── quick-navigation-feasibility.md        # feasibility (medium+)
        # Self-check extras
        ├── self-check-medium-extra.md             # medium+
        ├── self-check-long-extra.md               # long
        ├── self-check-research-extra.md           # research / eval
        ├── self-check-design-extra.md             # design
        └── self-check-feasibility-extra.md        # feasibility
```

## Anti-shortcut posture

The anti-shortcut layer is this bundle's central invariant:

- **No validator script ships.** Any claim of "passed lint / form check / manifest assembly" is **necessary but not sufficient**.
- **6 mandatory content self-checks** (in [`templates/components/self-check-base.md`](templates/components/self-check-base.md), mirroring [`SKILL.md`](SKILL.md) Sec. 9):
  - (a) Report primary purpose explicitly chosen + skeleton aligned
  - (b) At least one fully developed **What → Why → How** three-tier passage
  - (c) Major sections all carry **Intro-Summary + Takeaway**
  - (d) **Benchmark 7-item disclosure** complete (if benchmarks)
  - (e) At least one **Argument-style** figure caption
  - (f) Limitations quantified with specific numbers
- **Forbidden alias enforcement** ([`SKILL.md`](SKILL.md) Sec. 11): canonical names MUST be used in body text; aliases enumerated only in the Glossary itself.

## Architecture (one-paragraph)

Components-based template assembly pattern. The original 3 single-file templates (`short.md` / `medium.md` / `long.md`) were research / measurement-flavored and could not route the four primary purposes per SKILL Sec. 3. The current architecture decomposes into **32 small section-scoped components** + **1 manifest with 12 ordered sequences** for `(4 types × 3 lengths)`. Maintenance cost: editing wrapper-shared text now touches 1 component file rather than 3+ single-file templates (or 9+ in a fully-static expansion). Anti-shortcut risk from indirection is mitigated by an explicit manifest contract + `self-check-base.md` mirroring SKILL Sec. 9.

## Cross-renderer compatibility

- All anchors are **ASCII-only**. Different markdown renderers (GitHub web, Cursor preview, mkdocs, pandoc) handle non-ASCII anchor segments inconsistently — some strip, some URL-encode, some preserve raw — leading to broken anchor jumps. ASCII-only avoids the cross-renderer fragility.
- Section headings **omit any `Sec.` prefix** (slug derived from heading text alone, e.g. `## C.5 Intro-Summary three-part` → slug `c5-intro-summary-three-part`). Body cross-references use the `Sec. C.5` form for readability — `Sec.` prefix exists in body text but NOT in headings.

## Maintenance

When updating the skill:

1. **Methodology changes**: edit `reference.md` + sync `SKILL.md` (Glossary, jump table, decision tables).
2. **New examples**: add to `examples.md`; if templates' DEMO refs need updating, also touch relevant components in `templates/components/`.
3. **New section types**: add a new component file + update `templates/manifest.md` to reference it in the appropriate sequences.
4. **Glossary additions**: update `SKILL.md` Sec. 11 + ensure forbidden aliases are NOT used in body text of any file (a single global grep catches violations).
5. **Anchor changes**: ensure GitHub-style auto-slug stability; ASCII-only.

After significant changes, optionally re-verify with a single-model codex review:

```bash
codex exec --skip-git-repo-check --sandbox read-only "<review prompt>"
```

## Provenance

This bundle was distilled from a 1,714-line Chinese deep-research report (`final-deep-research-report.md` in the upstream workspace). The original design-time decision archive (`IA-NOTES.md`) is preserved in the upstream workspace for audit but excluded from this release bundle as it is runtime-irrelevant. Methodology fidelity was verified across multiple codex review rounds — record-and-explain dual nature, 4 report purposes, Intro-Summary three-part, Benchmark 7-item disclosure, CODER workflow + Five Gates review all map cleanly to the source.

## License / attribution

Add per your repository's conventions when integrating.
