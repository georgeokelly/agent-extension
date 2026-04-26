# Claude Code Reference

Verified against `claude 2.1.112 (Claude Code)` by reading `--help`; this
environment was not auth-run-verified. If `claude --version` reports a
different version, re-check `claude --help` before copying a recipe unchanged.

## Environment Check

```bash
command -v claude
claude --version
claude --help
```

If Claude Code reports an authentication problem, stop and ask the user to
authenticate in their own shell. Do not run `claude auth` or
`claude setup-token` for the user.

## Output Model

Use `-p/--print` for non-interactive output. The verified help lists
`--output-format text`, `json`, and `stream-json`; use `json` for ordinary
delegation and redirect stdout to a result file.

Use `--no-session-persistence` for one-shot delegated tasks unless resuming is
part of the explicit request.

## Read-Only Repository Analysis

Use `--permission-mode plan` for read-only planning/review work.

```bash
(
  cd /absolute/path/to/repo
  claude \
    -p \
    --permission-mode plan \
    --output-format json \
    --no-session-persistence \
    "$(cat <<'EOF'
You are a delegated Claude Code child agent.

Analyze the repository for <question>. Do not modify files.
Return:
- relevant files inspected
- findings with file references
- recommended next steps
EOF
)"
) > /tmp/claude-analysis.json
```

## Bounded Implementation

For local headless edits, use an explicit permission mode only after the user
has authorized child-agent edits. Use `--add-dir` for extra allowed context
directories outside the current workspace, and add narrow `--allowedTools`
entries only when the task requires specific tool permissions.

```bash
(
  cd /absolute/path/to/repo
  claude \
    -p \
    --permission-mode acceptEdits \
    --output-format json \
    --no-session-persistence \
    "$(cat <<'EOF'
You are a delegated Claude Code child agent.

Task:
- Implement <specific behavior>.

Allowed edits:
- src/foo/**
- tests/foo/**

Do not touch:
- package manager lockfiles unless required by tests
- unrelated formatting
- commits, branches, tags, remotes

Workflow:
1. Inspect the relevant code.
2. Make the smallest coherent change.
3. Run targeted verification.
4. Stop and report if a required dependency, secret, network call, or broad
   refactor is needed.

Final response:
- changed files
- verification commands and results
- remaining risks
EOF
)"
) > /tmp/claude-result.json
```

## External Sandbox Bypass Mode

`--dangerously-skip-permissions` bypasses Claude Code permission checks. The
verified help recommends it only for sandboxes with no internet access.

```bash
(
  cd /workspace
  claude \
    -p \
    --dangerously-skip-permissions \
    --output-format json \
    --no-session-persistence \
    "<prompt>"
) > /logs/claude-result.json
```

## Interactive Session

```bash
(
  cd /absolute/path/to/repo
  claude "<initial prompt>"
)
```

Use this only when a human will interact with Claude Code directly. For
agent-driven delegation, prefer `claude -p`.

## Resume

```bash
claude --continue
claude --resume <session-id>
```

Resume only when the prior session is known to match the current task and
workspace.
