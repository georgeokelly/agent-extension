---
# Spec (required)
name: use-agent-cli
description: >-
  Use local agent CLIs such as OpenAI Codex CLI, Cursor Agent, Claude Code, or
  opencode as delegated coding agents or reviewers from another agent. Use when
  the user asks to run/delegate to an agent CLI, automate a child agent
  non-interactively, compare agent CLIs, invoke `codex exec`, `cursor-agent
  -p`, `claude -p`, or `opencode run`, run an agent review, use Docker/YOLO
  mode, or prepare safe agent CLI commands for implementation, refactor,
  debugging, test repair, or repository analysis.

# Spec (optional)
license: MIT
compatibility: Cross-tool (Codex, Claude Code, Cursor Agent, OpenCode). Requires the selected CLI on PATH and local auth for actual execution.
metadata:
  author: georgel
  version: "0.1"
  verified_codex_cli: "0.125.0"
  verified_cursor_agent: "2026.04.17-787b533"
  verified_claude_code: "2.1.112"
  verified_opencode_cli: "1.14.21"

# Spec (experimental)
# allowed-tools: Bash(codex *) Bash(cursor-agent *) Bash(claude *) Bash(opencode *) Bash(command -v *) Bash(git status *) Read

# Spec (claude-only)
when_to_use: >-
  Use when operating a local agent CLI from an agent session: selecting Codex
  CLI, Cursor Agent, Claude Code, or opencode; checking installation/auth;
  drafting or running `codex exec`, `cursor-agent -p`, `claude -p`, or
  `opencode run` commands; delegating bounded coding work; obtaining an
  independent review; running an agent in an externally sandboxed Docker/YOLO
  mode; or integrating child-agent output back into the current workspace.
argument-hint: "[agent CLI and task or target path]"
# user-invocable: true
# model: sonnet
# effort: medium
# context: inline
# agent: general-purpose
# shell: bash
---

# Use Agent CLI

Operate a local agent CLI as a child agent from another AI coding agent. This
skill keeps the common parent/child contract here and puts CLI-specific details
in separate references. Load only the reference for the selected CLI.

Verified command references:

- Codex CLI: `codex-cli 0.125.0`, see
  [`references/codex-cli.md`](references/codex-cli.md)
- Cursor Agent: `cursor-agent 2026.04.17-787b533`, see
  [`references/cursor-agent.md`](references/cursor-agent.md)
- Claude Code: `claude 2.1.112`, see
  [`references/claude-code.md`](references/claude-code.md)
- opencode: `opencode 1.14.21`, see
  [`references/opencode.md`](references/opencode.md)
- Model/effort recommendations: see
  [`references/model-config.yaml`](references/model-config.yaml) only when the
  task requires choosing or overriding model/effort, including fallback choices
  when the preferred CLI is unavailable.

If the installed CLI version differs, run that CLI's `--help` first and treat
option or subcommand drift as version related until checked.

## Reference Routing

- If the user names Codex, `codex`, `codex exec`, Codex review, or Codex
  Docker/YOLO mode, read only
  [`references/codex-cli.md`](references/codex-cli.md).
- If the user names Cursor Agent or `cursor-agent`, read only
  [`references/cursor-agent.md`](references/cursor-agent.md).
- If the user names Claude Code or `claude`, read only
  [`references/claude-code.md`](references/claude-code.md).
- If the user names opencode or `opencode`, read only
  [`references/opencode.md`](references/opencode.md).
- If comparing multiple CLIs, read only the references for the CLIs being
  compared.
- If choosing or overriding model, effort, reasoning, or thinking level, also
  read [`references/model-config.yaml`](references/model-config.yaml).
- If Claude Code is requested but unavailable and Cursor Agent is available,
  read [`references/model-config.yaml`](references/model-config.yaml) and use
  Cursor Agent's configured `backup_for_missing_claude_code` model.
- If the user asks for general orchestration guidance and no concrete CLI is
  needed, use this `SKILL.md` only.

## Scope

Use an agent CLI when at least one is true:

- The user explicitly asks to use a local agent CLI as a child agent.
- A bounded coding task benefits from an independent implementation or review
  pass.
- The current agent needs a non-interactive child agent with a file/process
  boundary.
- The user asks for Docker/YOLO or another external sandbox pattern.
- The user needs structured child-agent output for downstream scripting.

Avoid child-agent CLI delegation when:

- The task is small enough to do directly.
- The task needs secrets, privileged network access, or broad filesystem access
  that the user has not explicitly approved.
- The workspace has unrelated uncommitted changes and the child would write
  into the same files without a clear boundary.
- The user asked only for an explanation, not delegated execution.

## Parent Contract

Before running a child agent, identify:

- **Target CLI**: exactly one of `codex`, `cursor-agent`, `claude`, or
  `opencode`, unless the task is explicitly a comparison.
- **Workspace**: exact working directory or CLI workspace flag.
- **Authority**: read-only/review, bounded edits, or external-sandbox autonomy.
- **Writable paths**: what the child may change.
- **No-touch paths**: credentials, unrelated source trees, remotes, branches,
  lockfiles, generated artifacts, or user work outside scope.
- **Output handling**: final report file/stdout JSON, optional event log, and
  any structured artifacts.
- **Verification**: commands the child should run and how the parent will
  verify or inspect results.

If the user did not authorize file edits by a nested agent, either ask or run
the child in read-only/review mode.

## Authentication Boundary

If the selected CLI reports an authentication problem, stop and ask the user to
authenticate in their own shell. Do not run interactive account operations for
the user, including:

- `codex login`
- `cursor-agent login`
- `claude auth`
- `claude setup-token`
- `opencode providers`
- `opencode auth`

## Prompt Contract

The prompt passed to the child agent must be self-contained. Include:

- Current role: "You are a delegated child agent."
- Scope: allowed files/directories and explicit no-touch areas.
- Required steps: inspect first, implement second, verify third.
- Output contract: changed files, tests run, failures, and residual risks.
- Safety: do not commit, push, install global packages, or rewrite unrelated
  work unless explicitly requested.

Do not assume the child sees the parent agent's conversation.

## Integration

After the child returns:

1. Inspect `git status --short` in every affected repo.
2. Review diffs for files the child changed.
3. Run or confirm the verification commands the child reported.
4. Fix small integration issues locally if they are in scope.
5. Treat the child output as evidence, not as unquestioned truth.

Do not commit child-agent changes unless the user explicitly asked for a
commit.

## Output To User

When you run a child agent CLI, summarize:

- command shape used, excluding secrets;
- files the child changed;
- verification commands and results;
- any manual integration you performed;
- unresolved risks or follow-up commands.

If you only draft a command, make it copy-pasteable and explain the chosen
permission/sandbox settings in one sentence.
