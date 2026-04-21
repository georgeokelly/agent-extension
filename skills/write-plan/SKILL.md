---
# Frontmatter fields follow the agentskills.io specification (https://agentskills.io/specification).
# Cross-tool: Cursor, Claude Code, and Codex all parse `name` + `description`.
# Extra fields such as `when_to_use` are additive guidance and degrade safely on tools that ignore them.
name: write-executable-plan
description: >-
  Generate implementation plans as executable contracts with contract profiles,
  checkpoints, verification, stop conditions, and handoff guidance. Use when the
  user wants an actionable plan another agent can follow directly.
when_to_use: >-
  Use when the user asks for an actionable implementation plan, execution contract,
  explicit tasks, checkpoints, verification, stop conditions, or a reusable plan
  artifact another agent can execute.
compatibility: Cross-tool (Cursor, Claude Code, Codex). Requires filesystem access for reading repository context and optional local validation via `scripts/validate-plan.py`.
metadata:
  author: georgel
  version: "0.1"
---

# Write Executable Plan

## Overview

Write plans as execution contracts, not planning notes. The output must give a downstream agent enough structure to act confidently while still leaving room for implementation creativity.

## When to Use

Use when:

- The user asks for an implementation plan another agent can follow directly.
- The user wants explicit tasks, files, verification, checkpoints, or stop conditions.
- The request is implementation-oriented and the requirements are already mostly known.
- The work needs a reusable plan artifact rather than a chat-only recommendation.

Do not use when:

- The user is still brainstorming the problem or comparing approaches.
- The output should be a PRD, RFC, ADR, or GitHub issue rather than an execution plan.
- The task is so small that a one-paragraph answer is enough.
- The user wants code changes immediately and does not want a plan artifact.

## Core Principle

Every plan uses:

- One `core contract` shared by all plans.
- One open-ended `Task Type` label describing the work.
- One `contract profile` chosen for the specific work.
- One execution mode: `credit-rich` by default, `budget-limited` when requested or clearly necessary.

The contract constrains output quality and safety boundaries. It should not micromanage every implementation decision.

## Required Inputs

Before writing the plan, make sure you have:

- A clear goal.
- Enough context to identify the affected area.
- At least one usable context source: user-provided paths, repo files, a spec, a design doc, or equivalent material.

If critical ambiguity remains, stop and ask focused questions before generating the plan.

## Workflow

1. **Intake & Preflight**
   Confirm the goal, choose a free-form task type label, choose a contract profile, and choose the execution mode.

2. **Context Assembly**
   Read the provided context first. If the user already attached relevant files or paths, treat that as the primary grounding source. Define a bounded `Context Scope` before delegating or expanding.

3. **Clarify Gaps**
   Ask only the questions that materially change the plan. In `budget-limited` mode, prefer defaults over long interviews.

4. **Build the Flow Graph**
   Define the major phases and transition points. Insert checkpoints as review jobs on transitions, not as ordinary implementation steps.

5. **Define Stages**
   Group the work into stages. Each stage must include a checklist describing the jobs that belong in that stage. Stages describe job groupings, not a mandatory execution order.

6. **Generate the Plan**
   Produce the plan using the `core contract` plus the chosen `contract profile`.

7. **Self-Review & Handoff**
   Remove placeholders, verify section completeness, record key decisions, and finish with a clear handoff for the next agent.

## Checkpoints

Model checkpoints as transition-level review jobs:

- Default mode: `auto_review`
- Optional modes: `human_review`, `hybrid`

Use checkpoints when:

- The work crosses a major architecture boundary.
- The next phase would be expensive to redo.
- There is unresolved design ambiguity with meaningful downstream impact.
- The user explicitly wants intermediate review points.

By default, prefer automatic review over asking the human to intervene.

## Context Scope

Always define what the plan is allowed to rely on.

- If the user provided specific paths, files, or excerpts, treat them as the primary context scope.
- If additional grounding is needed, expand scope deliberately instead of letting a sub-agent explore freely.
- In test or evaluation scenarios, prefer allowlisted context packets over broad repository access.

If you delegate to a sub-agent while preparing a plan, pass only the allowlisted context needed for that task.

## Modes

### `credit-rich`

Default mode.

- Use fuller context assembly.
- Include richer rationale where useful.
- Allow more checkpoints for complex work.
- Prefer thoroughness over token minimization.

### `budget-limited`

Use when the user requests a cheaper/faster path or when the situation clearly demands restraint.

- Keep context gathering minimal.
- Reduce checkpoint frequency.
- Prefer the smallest sufficient contract.
- Only add optional sections when risk clearly justifies them.

## Execution Policy: Debug Loop

Plans produced by this skill are executed under a **resilient-by-default** contract. Downstream agents MUST NOT stop and ask the user at the first obstacle. They MUST run the bounded debug-and-fallback loop below before escalating.

### Loop steps

1. **Debug attempts** — when execution is blocked (implementation fails, tests fail, a `Stop Condition` fires, or any other technical obstacle), try up to **three distinct approaches**. Each attempt:
   - MUST declare an explicit hypothesis materially different from previous attempts.
   - MUST be performed as a reversible patch (unified diff + recovery instruction).
   - MUST be recorded as a `## Session N` entry in `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md`.
2. **Stage reprioritization** — if all three attempts fail, evaluate which stages are not blocked by the current obstacle and switch to an unblocked stage. Record the decision in the debug log under `## Stage Reprioritization`.
3. **Analysis report** — when no stage can proceed, write `## Analysis Report` in the debug log covering root cause, per-stage blocker mapping, and candidate new directions.
4. **Self-review** — immediately review the analysis and record the outcome in `## Self-Review`. If a new approach surfaces, re-enter the loop at step 1.
5. **Ask user** — escalate ONLY after steps 1–4 have been exhausted.

### Budget

These values override the global workspace defaults when executing a plan produced by this skill:

- Same-action retries: max **3**
- Same-hypothesis retries: max **3**
- Tool turns per stage: max **15** (each stage carries its own 15-turn budget; total task budget is `stages × 15`)

Exhausting the per-stage turn budget is treated as equivalent to an unsuccessful self-review — escalate.

### `Stop Conditions` semantics

`Stop Conditions` declared in a plan are **entry conditions for the debug loop**, not immediate ask-user triggers. The only hard-stop signals are:

- the user explicitly requests a stop
- the full loop above has been exhausted

### Patch discipline

Every debug attempt MUST be reversible:

- A unified-diff `### Patch` block in the debug log.
- A `### Recovery` entry describing exactly how to undo the patch (git command, backup path, or clear natural-language instruction).
- Irreversible changes are forbidden inside the loop; if unavoidable, escalate BEFORE performing the change.

### Budget-limited mode

Under `budget-limited`, the loop compresses:

- Try **1** approach per blocker (not 3).
- Skip `Analysis Report` + `Self-Review` if no stage can be reprioritized; escalate directly.

See [reference §16](reference.md#16-execution-policy-debug-loop) and [§17](reference.md#17-debug-log-format) for the full contract and debug log format.

## Output Rules

Always:

- Use the `core contract`.
- Apply exactly one `contract profile`.
- Include an explicit `Context Scope`.
- Include a `Flow Graph`.
- Include `Stages`.
- Include a checklist inside every stage.
- Include explicit verification.
- Include explicit stop conditions.
- Distinguish `Proposed Deliverables` from `Committed Deliverables` when artifact shape is not yet frozen.
- Keep a `Decision Log`.
- End with a handoff section.
- Save the plan file with basename `plan.<contract-profile>.<task-type>.md` (see [reference §15](reference.md#15-plan-file-naming)).
- When a piece of information is genuinely unknown at plan-writing time, mark the gap inline with `TODO` or `TBD`. The validator detects these as warnings so a downstream agent can surface them to the user for clarification. Do not invent alternative wording (e.g. "待定", "to decide", "?") — stick to `TODO` / `TBD` so the gap is reliably detected.

Never:

- Leave lazy list items such as `- implement later`, `- write tests`, or `- handle edge cases` — these must be replaced with concrete, actionable tasks.
- Force wiki-specific steps unless wiki context is actually available and helpful.
- Bind the plan to a single executor's internal workflow.
- Treat the plan as a static artifact when major decisions change during execution.

Should:

- Resolve all `TODO` / `TBD` markers before final handoff — treat them as clarification prompts for the user, not acceptable final state.

Execution-time output:

- When execution hits a blocker, produce a debug log named `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` and follow the format in [reference §17](reference.md#17-debug-log-format).
- Every debug attempt MUST be logged as a `## Session N` block with hypothesis, patch, recovery, and result.

## Quick Reference

- Contract details: see [reference.md](reference.md)
- Concrete examples and fallback guidance: see [examples.md](examples.md)
- Optional validator: see [`scripts/validate-plan.py`](scripts/validate-plan.py)

## Common Mistakes

- Writing a polished overview without enough task detail to execute.
- Using one contract profile for every kind of work.
- Omitting `Context Scope` and letting downstream agents guess what local material they may rely on.
- Turning checkpoints into ordinary build steps instead of review gates.
- Using stages as rigid step order instead of job groupings.
- Creating stages without checklists.
- Freezing the final file or artifact layout too early instead of separating proposed deliverables from committed ones.
- Making wiki or research mandatory when user-provided context is already enough.
- Over-constraining execution and removing all agent creativity.
- Forgetting to update the plan after a major design change.
- Using a plan filename that does not match `plan.<contract-profile>.<task-type>.md`.
- Stopping and asking the user at the first obstacle instead of running the bounded debug loop.
- Producing debug attempts without a reversible patch and a `### Recovery` instruction.

## Additional Notes

- Plans should remain structurally consumable by downstream execution workflows without binding to a single host-specific process.
- External knowledge sources are optional context inputs, not default dependencies.
- Prefer exact repo-relative paths whenever the context makes them knowable.
