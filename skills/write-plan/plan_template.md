

# PLAN: 

**Goal:** 
**Task Type:** `<free-form label such as search-enhancement, payment-read-migration, reporting-refactor, feasibility-experiment>`
**Contract Profile:** `<delivery|refactor|migration|exploration>`
**Mode:** `<credit-rich|budget-limited>`
**Primary Success Signal:** 

---

## Inputs / Context Sources



## Context Scope



## Output

<artifact / data the plan produces, at sketch level; detailed artifact tree belongs in Proposed / Committed Deliverables if needed>

## Dependency Graph

<DAG nodes with id prefixes — `s*` stage, `ck*` checkpoint, `h` handoff — connected by directed edges; absent edges mean structural independence. See `reference.md` → Dependency Graph for the id convention and a Mermaid example with `classDef` color coding.>

## Stages

<one content block per DAG node with header `### <id>: <label>`; shape dispatched by id prefix — see `reference.md` → Node Content Templates.>

## Verification



## Decision Points

<conditions that trigger the next agent to pause and re-evaluate via the debug loop (retry / reprioritize / escalate), not terminal stops>

## Decision Log



## Debug Log Standard

> **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
>
> Format: `debug_log_template.md` (see also `reference.md` → Debug Log Format). Trigger: debug loop (`reference.md` → Execution Policy: Debug Loop). Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

## Stage Claims

> **Runtime coordination ledger** — composer seeds one `- [ ]` entry per DAG node (stages `s*`, checkpoints `ck*`, handoff `h`). Executors update in place:
>
> - `- [ ] <id>: <label>` — unclaimed
> - `- [~] <id>: <label> — <agent-id> @ <MMDDHHMM>` — claimed, in progress
> - `- [x] <id>: <label> — <agent-id> @ <MMDDHHMM>` — done
>
> See `reference.md` → Stage Claims for the full claim protocol.

- [ ] s1: <stage label>
- [ ] s2: <stage label>
- [ ] h: Handoff