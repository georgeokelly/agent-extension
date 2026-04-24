---
# Spec (required)
name: write-executable-plan
description: >-
  Generate implementation plans as executable contracts with contract profiles,
  dependency graph, checkpoints, verification, decision points, and a runtime
  stage-claims ledger. Use when the user wants an actionable plan another agent
  can follow directly.

# Spec (optional)
license: MIT
compatibility: Cross-tool (Cursor, Claude Code, Codex). Requires filesystem access for reading repository context. The validator `scripts/validate-plan.py` is mandatory (run it at Step 10 of the composer workflow); all it needs is Python 3 available locally.
metadata:
  author: georgel
  version: "0.1"

# Spec (experimental)
# allowed-tools: Bash(git add *) Bash(git commit *) Read  # support claude only
# disable-model-invocation: true                          # support cursor + claude

# Spec (claude-only)
when_to_use: >-
  Use when the user asks for an actionable implementation plan, execution contract,
  explicit tasks, checkpoints, verification, decision points, or a reusable plan
  artifact another agent can execute.
# argument-hint: "[issue-number] [branch]"
# arguments: [issue, branch]
# user-invocable: true
# model: sonnet        # sonnet / opus / haiku / id / inherit
# effort: medium       # low / medium / high / xhigh / max
# context: fork        # When forking, run the body in an independent subagent context
# agent: general-purpose
# hooks:
#   PreToolUse: ./hooks/<pre.sh>
#   PostToolUse: ./hooks/<post.sh>
#   Stop: ./hooks/<stop.sh>
# paths:
#   - "src/**/*.ts"
# shell: bash          # bash / powershell
---

# Write Executable Plan

## Overview

Write plans as execution contracts, not planning notes. When this skill is invoked, you are the **composer** of the plan; a separate downstream agent — the **executor** — will run it later. The output MUST give the executor enough structure to act confidently while still leaving room for implementation creativity.

## Two Regimes before Everything

Now that you know what you're producing, keep this in mind while reading the rest: this skill describes **two different activities** with different rules.

- **Plan-writing rules (composer)** — what you do while drafting: workflow, clarifying questions, output format, self-review. You PERFORM these.
- **Plan-execution rules (executor)** — what the executor does later when running your plan: debug loop, retry budgets, patch discipline, escalation thresholds. You REFERENCE these so you can write correct plans. You do NOT run them yourself.

Red flag — you are mixing the two if you catch yourself:

- running a "debug loop" to recover from a drafting obstacle (the debug loop is an execution-time rule)
- applying the per-stage 15-turn budget to your own context-gathering (that budget governs the executor, not you)
- reading a `Decision Points` bullet as a halt-and-ask-user command (it is a trigger for the executor to pause and re-evaluate via the debug loop, not a terminal stop)

When unsure, ask: *am I performing this action, or describing it for the executor to perform later?*

See [Cross-Regime Terms](reference.md#cross-regime-term-disambiguation) for terms whose meaning shifts across the two rule sets.

## The Plan Skeleton

Every plan uses these building blocks. For full semantics, see
[Notation](reference.md#notation).


| Term               | Role                                                                                                                                                                                   |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `core contract`    | The fixed skeleton of headings every plan MUST contain.                                                                                                                                |
| `Task Type`        | A free-form kebab-case slug describing the work (e.g. `search-suggestions-cache`, `payment-read-migration`, `reporting-service-split`). Drives filename and debug log naming.          |
| `contract profile` | One of `delivery` / `refactor` / `migration` / `exploration`; selects the conditional sections to include.                                                                             |
| `Mode`             | `credit-rich` (default) or `budget-limited`; controls verbosity, clarifying questions, and debug-loop budgets.                                                                         |
| `Decision Points`  | Triggers for the executor's debug loop (not terminal stops).                                                                                                                           |
| `DAG node`         | A unit that takes a claim and produces an outcome — shape dispatched by id prefix: stage `s*`, checkpoint `ck*`, or handoff `h`. See [Node Content Templates](reference.md#node-content-templates). |
| `Checkpoints`      | Two kinds — implicit **stage autopilot** and explicit **checkpoint nodes** (`ck*`) in the dependency graph. See [Checkpoints](reference.md#checkpoints) for full semantics.        |


The contract constrains output quality and safety boundaries. It does not
micromanage every implementation decision.

## Required Inputs

Before writing the plan, make sure you have:

- A clear goal.
- Enough context to identify the affected area.
- At least one usable context source: user-provided paths, repo files, a spec, a design doc, or equivalent material.

If critical ambiguity remains, stop and ask focused questions before generating the plan.

## Composer Workflow

1. **Intake & Preflight**
  Confirm the goal, choose a free-form task type label, choose a contract profile, and choose the execution mode. Default to `credit-rich`; pick `budget-limited` only when the user asks for a leaner path or the task is clearly simple.
2. **Context Assembly**
  Read the provided context first. If the user already attached relevant files or paths, treat that as the primary grounding source. Define a bounded `Context Scope` before delegating or expanding.
3. **Problem Framing**
  Build a coarse conceptual model of the task from assembled context before decomposing it. The model is the artifact you carry into later steps; see a concrete [Problem Framing example](examples.md#example-8--problem-framing) in examples.md. Produce a sketch covering:
  - **Objective** — what this task is actually solving, in one sentence.
  - **Inputs / environment** — what the task depends on, at capability level rather than specific configuration.
  - **Expected output** — what artifact/data the executor will produce, at sketch granularity.
  - **Back-match to requirement** — how that output is supposed to satisfy the original ask.
  - **Assumptions & unknowns** — explicit list; these feed directly into the next step.
  Stay coarse — it is a solution sketch, not implementation detail.
4. **Clarify Gaps**
  Share the current coarse model with the user first, so they can sanity-check the frame before answering specific questions. Then ask only the questions that materially change the plan, focusing on the gaps surfaced during problem framing — places where the context does not supply what the model needs, or where the expected output does not map back to the requirement. In `budget-limited` mode, prefer defaults over long interviews.
5. **Top-down Decompose**
  Break the task down into checklist-level items — the smallest actionable units a downstream executor can perform in one bounded attempt (roughly a commit-sized change or a single test-validated step). Every item should trace back to the problem-framing artifact: preparing **Inputs / environment**, contributing to the **Objective**, producing part of the **Expected Output**, or resolving an **Assumption / Unknown**. Stop when further splits stop adding executability — granularity is a ceiling, not a goal. These items are the leaves of the plan hierarchy and the raw material for bottom-up assembly.
6. **Bottom-up: Define Stages**
  Group the checklist items into **stages** — cohesive work units. Items inside a stage share files, intent, or a verification boundary, together achieving one sub-goal. A stage should be the smallest unit you'd want to review or re-execute as a whole.
  Stages describe *what bundles together*, not *when it runs*. Dependencies between stages are expressed later in the dependency graph (Step 7), where stages become the nodes.
7. **Bottom-up: Build Dependency Graph**
  Arrange the stages into a **dependency graph**:
  - **Nodes** are stages; assign each a short id using the prefix convention `s1`, `s2`, … (stages) — see [Node id convention](reference.md#dependency-graph) for the full scheme once checkpoints and handoff are added.
  - **Edges** express "X depends on Y's output" — direction matters.
  - **No edge** between two stages means they are independent (structurally parallelizable).
  - **Terminal node**: add a single `h` handoff node as the DAG's only sink — every other node must flow into it.
  The composer **declares structure only** (who depends on who). The **executor decides the execution pattern** at runtime — serial, fork-join parallel, sub-agent dispatch, best-of-N, or split across multiple executors. Your plan must hold under any of these.
  Recommended: render the DAG as a Mermaid flowchart and tint nodes by prefix (blue stages / amber checkpoints / green handoff) via `classDef` — it makes the id convention visible at a glance. See [Dependency Graph](reference.md#dependency-graph) for the palette.
8. **Insert Checkpoints**
  Checkpoints come in two kinds:
  - **Stage autopilot** — implicit per-stage verification (tests pass, outputs exist), always present, not declared.
  - **Explicit checkpoint node** — a `ck1`, `ck2`, … node inserted into the graph; its content block under `## Stages` uses the [checkpoint-shape](reference.md#checkpoint-shape-ck) template.
  Insert an explicit `ck*` node where branches **merge** (join), **immediately upstream of an irreversible node**, or at a **fork** where upstream output chooses the downstream branch — i.e., when proceeding wrong costs more than the stage autopilot catches.
9. **Write Node Content Blocks**
  Under `## Stages`, write one content block per DAG node with header `### <id>: <label>`. The shape (required/recommended fields) is dispatched by the id prefix:
  - `s*` → [stage-shape](reference.md#stage-shape-s) (work unit)
  - `ck*` → [checkpoint-shape](reference.md#checkpoint-shape-ck) (review gate)
  - `h` → [handoff-shape](reference.md#handoff-shape-h) (terminal sign-off)
  Assemble the full plan by starting from [`plan_template.md`](plan_template.md) (`cp plan_template.md plan.<contract-profile>.<task-type>.md`) and filling in every placeholder, then add any conditional sections required by the chosen `contract profile`. Seed `## Stage Claims` with one `- [ ] <id>: <label>` entry per DAG node in topological order, ending with `- [ ] h: Handoff`.
10. **Self-Review & Finalize**
  Run through the [Self-Review Checklist](#self-review-checklist), then run `python3 scripts/validate-plan.py <plan-file>`. Resolve every error before handing off. If a warning is intentionally left in (e.g. a `TODO` the user must answer), surface it to the next agent.

## Context Scope

Every plan declares a `Context Scope` — the set of files, paths, or information the executor is allowed to rely on while running the plan. As composer, you decide that scope while drafting.

Guidelines:

- Treat user-provided paths, files, or excerpts as the primary scope; do not silently expand past what was handed to you.
- If you need more grounding to write the plan, expand scope deliberately — name the specific files or areas you are adding. Do **not** delegate the expansion decision to a sub-agent by giving it an unbounded task like "figure out what's relevant".
- In test or evaluation scenarios, prefer allowlisted context packets (pre-approved context bundles) over broad repository access.
- When delegating to a sub-agent during drafting, pass only the allowlisted context the sub-task actually needs.

## Output Rules

> Items below are **semantic** — `scripts/validate-plan.py` covers structural shape.

Always:

- Make the **`h` handoff node** carry concrete sign-off content — what "done" looks like for THIS plan, not a generic boilerplate copy. It is the terminal DAG node, not just a marker.
- Place **explicit checkpoint nodes** (`ck*`) at the structural landmarks identified in Step 8 — joins, pre-irreversible steps, decision forks — if any exist.
- Write **verification criteria** as concrete pass/fail conditions per stage and checkpoint (what defines success), not as restatements of the stage purpose.
- Distinguish **`Proposed Deliverables`** from **`Committed Deliverables`** when artifact shape is not yet frozen.
- When a piece of information is genuinely unknown at plan-writing time, mark the gap inline with `TODO` or `TBD`. Do not invent alternative wording (e.g. "待定", "to decide", "?") — stick to `TODO` / `TBD` so the validator's warning detector picks them up.

Never:

- Leave lazy list items such as `- implement later`, `- write tests`, or `- handle edge cases`. These starve the executor of intent — replace with concrete, actionable tasks.
- Bind the plan to a single executor's internal workflow (specific tools, IDE features, agent personalities, hard-coded turn budgets).
- Treat the plan as a static artifact when major decisions change during drafting — update the plan, do not let it drift from current intent.

Should:

- Resolve all `TODO` / `TBD` markers before finalizing — treat them as clarification prompts for the user, not acceptable final state.
- Treat external knowledge sources (wiki, docs, research) as optional context inputs, not default dependencies.
- Prefer exact repo-relative paths whenever the context makes them knowable.

## Self-Review Checklist

Diagnostic questions for finalizing — validator covers shape; this catches semantic defects.

### Task shape

- Plan has enough execution detail — a polished overview alone is not enough for an executor to act.
- Contract profile fits THIS task's shape, not copy-pasted from a previous plan.

### Structural soundness

- Stages are cohesion-based groupings (shared sub-goal, files, or verification boundary), not a rigid sequential list.
- Every stage's checklist is concrete and actionable — no lazy placeholders that *evade* the validator's pattern list (paraphrased "implement later", "TODO-ish" tasks dressed up as bullets, etc.).
- Explicit checkpoints (if any) act as review gates that wait-and-judge, not ordinary build steps that do-and-continue.
- Every structural landmark in the DAG (merge, pre-irreversible step, decision fork) has an explicit checkpoint, or has a conscious reason not to.

### Executor freedom

- Plan declares structure only — no prescribed execution pattern (serial / parallel / sub-agent / best-of-N).
- Plan does not bind to a single executor's internal workflow.
- Implementation creativity is preserved; the plan does not micromanage decisions the executor can make.

### Context hygiene

- `Context Scope` lists specific files or areas — not vague phrases like "relevant code".
- Every scope expansion beyond user-provided material is named deliberately.
- Wiki / research / external knowledge is pulled in only when user context is insufficient.

### Evolution readiness

- `Proposed Deliverables` vs `Committed Deliverables` distinguished when artifact shape is not yet frozen.
- Plan is updated if major design decisions changed during drafting — no stale state.

## Quick Reference

- **Node id convention**: `s1..sN` stages · `ck1..ckN` checkpoints · `h` the single handoff sink. Ids MUST be identical across `## Dependency Graph`, `## Stages`, and `## Stage Claims` — labels can differ for display.
- **Plan starting point** (composer): `cp plan_template.md plan.<contract-profile>.<task-type>.md` — see [plan_template.md](plan_template.md).
- **Debug log starting point** (executor at debug-loop entry): `cp debug_log_template.md debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` — see [debug_log_template.md](debug_log_template.md).
- Contract details: see [reference.md](reference.md)
- Concrete examples and fallback guidance: see [examples.md](examples.md)
- Validator (required by Step 10): `python3 scripts/validate-plan.py <plan-file>` — see [scripts/validate-plan.py](scripts/validate-plan.py)