# Cursor Agent Reference

Verified against `cursor-agent 2026.04.17-787b533`. If
`cursor-agent --version` reports a different version, re-check
`cursor-agent --help` before copying a recipe unchanged.

## Environment Check

```bash
command -v cursor-agent
cursor-agent --version
cursor-agent --help
```

If Cursor Agent reports an authentication problem, stop and ask the user to
authenticate in their own shell. Do not run `cursor-agent login` for the user.

## Output Model

Use `-p/--print` for non-interactive operation. In the verified version,
`--output-format json` writes one JSON object whose `result` field contains the
final text result.

Use `--output-format stream-json` only when a supervising process needs event
streaming. For ordinary delegated tasks, redirect the single JSON result to a
repo-external file.

Use result names that identify the task and run. Avoid generic paths such as
`/tmp/cursor-result.json` in real runs because parallel tasks can overwrite each
other. Prefer `/tmp/cursor-<task>-<timestamp>-<pid>.json`, or add a random
suffix.

## Background Review Run

For long read-only reviews, run Cursor Agent in the background only after
choosing result/log paths and a poll/termination plan. Use `--mode ask` for
read-only review output.

```bash
task_slug="review-auth-flow"
run_id="$(date +%Y%m%d-%H%M%S)-${RANDOM}-$$"
result_path="/tmp/cursor-${task_slug}-${run_id}.json"
log_path="/tmp/cursor-${task_slug}-${run_id}.log"

cursor-agent \
  -p \
  --trust \
  --mode ask \
  --workspace /absolute/path/to/repo \
  --model grok-4-20-thinking \
  --output-format json \
  "$(cat <<'EOF'
You are a delegated Cursor Agent child agent.

Analyze the repository for <question>. Do not modify files.
Return:
- relevant files inspected
- findings with file references
- recommended next steps
EOF
)" > "$result_path" 2> "$log_path" &

child_pid="$!"
printf 'cursor-agent pid=%s result=%s log=%s\n' \
  "$child_pid" "$result_path" "$log_path"
```

Poll the process id and parse the result file only after the process exits. If
the run exceeds the expected duration, ask whether to continue waiting, stop the
process, or leave it running and collect the result later.

## Read-Only Repository Analysis

Use `--mode ask` for Q&A/review output, or `--mode plan` when the expected
result is a plan.

```bash
task_slug="analysis-question"
run_id="$(date +%Y%m%d-%H%M%S)-${RANDOM}-$$"
result_path="/tmp/cursor-${task_slug}-${run_id}.json"

cursor-agent \
  -p \
  --trust \
  --mode ask \
  --workspace /absolute/path/to/repo \
  --output-format json \
  "$(cat <<'EOF'
You are a delegated Cursor Agent child agent.

Analyze the repository for <question>. Do not modify files.
Return:
- relevant files inspected
- findings with file references
- recommended next steps
EOF
)" > "$result_path"
```

## Bounded Implementation

Use `--sandbox enabled` for local bounded edits. Do not add `--force` or
`--yolo` unless the user explicitly authorized non-interactive command approval
or an external sandbox is the real containment boundary.

```bash
task_slug="implementation-foo"
run_id="$(date +%Y%m%d-%H%M%S)-${RANDOM}-$$"
result_path="/tmp/cursor-${task_slug}-${run_id}.json"

cursor-agent \
  -p \
  --trust \
  --workspace /absolute/path/to/repo \
  --sandbox enabled \
  --output-format json \
  "$(cat <<'EOF'
You are a delegated Cursor Agent child agent.

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
)" > "$result_path"
```

## External Sandbox Force Mode

`cursor-agent --yolo` is an alias for `--force` in the verified version. Use it
only when Docker or another external sandbox is the containment boundary.

```bash
cursor-agent \
  -p \
  --trust \
  --workspace /workspace \
  --sandbox disabled \
  --yolo \
  --output-format json \
  "<prompt>" > /logs/cursor-result.json
```

## Interactive Session

```bash
cursor-agent --workspace /absolute/path/to/repo "<initial prompt>"
```

Use this only when a human will interact with Cursor Agent directly. For
agent-driven delegation, prefer `cursor-agent -p`.

## Resume

```bash
cursor-agent --continue
cursor-agent --resume <chat-id>
```

Resume only when the prior session is known to match the current task and
workspace.
