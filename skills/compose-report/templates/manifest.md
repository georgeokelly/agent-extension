# Template Assembly Manifest

This manifest defines the component sequence for each (report-type, length) pair. Agents using the compose-report skill MUST follow this exact procedure:

1. **Identify the report's primary purpose** from SKILL.md Sec. 3 (one of: `research-findings` / `design-solution` / `feasibility-analysis` / `technical-evaluation`).
2. **Identify the target length** from SKILL.md Sec. 5 (one of: `short` / `medium` / `long`).
3. **Locate your sequence** below and read it in order.
4. **Assemble the template** by reading each listed component file and concatenating them with blank-line separators.
5. **Fill in DEMO placeholders** + actual report content as you write.

## Anti-shortcut compliance for component assembly

> ⚠️ **The component assembly process is itself subject to SKILL.md Sec. 9 Anti-shortcut.**
>
> - Do NOT skip components listed in your manifest sequence. Skipping = unqualified delivery.
> - Do NOT add components NOT in the manifest without explicit justification (which MUST be recorded in your report's metadata or front-matter).
> - Do NOT silently substitute one component for another. If your case requires deviation, document the deviation explicitly in the assembled draft (so reviewers can see what changed and why).
> - "I assembled per manifest" is **not** sufficient — agents MUST also pass the 6 content self-checks in SKILL.md Sec. 9.

## Component categories

| Category | Components |
|---|---|
| Common (all types/lengths) | `top-declaration`, `tldr`, `background`, `conclusion`, `limitations`, `self-check-base` |
| Length-additive | `front-matter` (long), `quick-navigation-research` (medium+ research/eval), `quick-navigation-design` (medium design), `quick-navigation-design-long` (long design), `quick-navigation-feasibility` (medium+ feasibility), `system-overview-c4` (long, research/eval/design only), `related-work` (long research/eval/design), `scaling` (long research/eval), `robustness-cost` (long research/eval), `operations` (long research/eval/design), `references-appendices` (long), `self-check-medium-extra` (medium+), `self-check-long-extra` (long) |
| Method-stage | `method` (research/eval/design), `considered-alternatives` (design), `trade-off-matrix` (design medium+), `experiment-setup` (research/eval), `results` (research/eval), `ablation` (research/eval medium+), `cost-analysis` (feasibility), `validation-path` (feasibility), `go-no-go` (feasibility), `risk-register` (design + feasibility) |
| Type-specific self-check | `self-check-research-extra`, `self-check-design-extra`, `self-check-feasibility-extra` |

---

## research-findings × short

```
1. components/top-declaration.md
2. components/tldr.md
3. components/background.md
4. components/method.md
5. components/experiment-setup.md
6. components/results.md
7. components/conclusion.md
8. components/limitations.md
9. components/self-check-base.md
10. components/self-check-research-extra.md
```

## research-findings × medium

```
1. components/top-declaration.md
2. components/tldr.md
3. components/quick-navigation-research.md
4. components/background.md
5. components/method.md
6. components/experiment-setup.md
7. components/results.md
8. components/ablation.md
9. components/conclusion.md
10. components/limitations.md
11. components/self-check-base.md
12. components/self-check-medium-extra.md
13. components/self-check-research-extra.md
```

## research-findings × long

```
1. components/top-declaration.md
2. components/front-matter.md
3. components/tldr.md
4. components/quick-navigation-research.md
5. components/background.md
6. components/system-overview-c4.md
7. components/method.md
8. components/related-work.md
9. components/experiment-setup.md
10. components/results.md
11. components/ablation.md
12. components/scaling.md
13. components/robustness-cost.md
14. components/operations.md
15. components/conclusion.md
16. components/limitations.md
17. components/references-appendices.md
18. components/self-check-base.md
19. components/self-check-medium-extra.md
20. components/self-check-long-extra.md
21. components/self-check-research-extra.md
```

---

## technical-evaluation × {short, medium, long}

> Use the **same component sequence as `research-findings`** for the equivalent length, but adjust DEMO content focus:
>
> - TL;DR emphasizes **comparative recommendation** ("Recommend approach X over Y under conditions Z") rather than single-method speedup.
> - `method.md` becomes **"Evaluation criteria + measurement protocol"**.
> - `experiment-setup.md` MUST include **all baselines** (typically ≥ 2 alternatives), not just one.
> - `results.md` is replaced/expanded with **side-by-side comparison tables** (refer to `examples.md Sec. B.8.2 Complexity comparison table` for structural pattern).
> - `self-check-research-extra.md` items still apply.

---

## design-solution × short

```
1. components/top-declaration.md
2. components/tldr.md
3. components/background.md
4. components/considered-alternatives.md
5. components/method.md
6. components/risk-register.md
7. components/conclusion.md
8. components/limitations.md
9. components/self-check-base.md
10. components/self-check-design-extra.md
```

## design-solution × medium

```
1. components/top-declaration.md
2. components/tldr.md
3. components/quick-navigation-design.md
4. components/background.md
5. components/considered-alternatives.md
6. components/trade-off-matrix.md
7. components/method.md
8. components/risk-register.md
9. components/conclusion.md
10. components/limitations.md
11. components/self-check-base.md
12. components/self-check-medium-extra.md
13. components/self-check-design-extra.md
```

## design-solution × long

```
1. components/top-declaration.md
2. components/front-matter.md
3. components/tldr.md
4. components/quick-navigation-design-long.md
5. components/background.md
6. components/system-overview-c4.md
7. components/considered-alternatives.md
8. components/trade-off-matrix.md
9. components/method.md
10. components/related-work.md
11. components/risk-register.md
12. components/operations.md
13. components/conclusion.md
14. components/limitations.md
15. components/references-appendices.md
16. components/self-check-base.md
17. components/self-check-medium-extra.md
18. components/self-check-long-extra.md
19. components/self-check-design-extra.md
```

---

## feasibility-analysis × short

```
1. components/top-declaration.md
2. components/tldr.md
3. components/background.md
4. components/cost-analysis.md
5. components/risk-register.md
6. components/validation-path.md
7. components/go-no-go.md
8. components/conclusion.md
9. components/limitations.md
10. components/self-check-base.md
11. components/self-check-feasibility-extra.md
```

## feasibility-analysis × medium

```
1. components/top-declaration.md
2. components/tldr.md
3. components/quick-navigation-feasibility.md
4. components/background.md
5. components/considered-alternatives.md
6. components/cost-analysis.md
7. components/risk-register.md
8. components/validation-path.md
9. components/go-no-go.md
10. components/conclusion.md
11. components/limitations.md
12. components/self-check-base.md
13. components/self-check-medium-extra.md
14. components/self-check-feasibility-extra.md
```

## feasibility-analysis × long

```
1. components/top-declaration.md
2. components/front-matter.md
3. components/tldr.md
4. components/quick-navigation-feasibility.md
5. components/background.md
6. components/considered-alternatives.md
7. components/trade-off-matrix.md
8. components/cost-analysis.md
9. components/risk-register.md
10. components/validation-path.md
11. components/go-no-go.md
12. components/conclusion.md
13. components/limitations.md
14. components/references-appendices.md
15. components/self-check-base.md
16. components/self-check-medium-extra.md
17. components/self-check-long-extra.md
18. components/self-check-feasibility-extra.md
```

---

## Notes for assemblers

- **Component file paths** above are relative to the bundle's `templates/` directory (this file's location).
- **DEMO placeholders** within components reference `examples.md` via relative paths `../../examples.md#...` (works from `templates/components/*.md` location).
- **Section numbering** in the assembled output: components leave heading slots as `## ⟨N⟩. Section Name` so you adjust `⟨N⟩` to match the actual ordinal in your final assembled report. Numbering MUST be sequential (e.g., `## 1. ... ## 2. ... ## 3. ...`) without gaps.
- **Cross-references between sections** in components use placeholders like `Sec. ⟨N⟩.X` where `⟨N⟩` MUST be replaced with the section's actual ordinal in your assembled report.
- **DEMO replacement is independent of assembly**. After assembling components in sequence, you still MUST replace every `<!-- DEMO ... — REPLACE -->` block with your actual report content per SKILL.md Sec. 9.
