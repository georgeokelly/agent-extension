# opencode Reference

Verified against `opencode 1.14.21`. If `opencode --version` reports a
different version, re-check `opencode --help`, `opencode run --help`, and
`opencode models --help` before copying a recipe unchanged.

This public reference uses only the generic `opencode` command. Provider,
wrapper command, and model ids may be private to a deployment; keep them out of
this shared skill and set them only through deployed/local
`model-config.yaml` overrides.

The verified version applies only to the public `opencode` command. If
`local_overrides.opencode_command` is set in a deployed/local config, verify
that command's `--version`, `--help`, and `run --help` independently; do not
compare its version string to `1.14.21`.

## Environment Check

```bash
command -v opencode
opencode --version
opencode --help
opencode run --help
opencode models --help
```

If opencode reports an authentication/provider problem, stop and ask the user
to authenticate or configure providers in their own shell. Do not run
`opencode providers` or `opencode auth` for the user.

## Output Model

Use `opencode run` for non-interactive operation. In the verified version:

- `--dir <path>` sets the working directory.
- `--format json` emits raw JSON events.
- `--model <provider/model>` selects a model when a public or local model id is
  configured.
- `--variant <variant>` is provider-specific reasoning effort.
- `--dangerously-skip-permissions` auto-approves permissions and should only be
  used inside an external sandbox.

If no public model is configured, omit `--model` and use opencode's local
default. If opencode requires an explicit model and none is configured, stop
and ask for a local override.

## Read-Only Repository Analysis

```bash
opencode run \
  --dir /absolute/path/to/repo \
  --format json \
  "$(cat <<'EOF'
You are a delegated opencode child agent.

Analyze the repository for <question>. Do not modify files.
Return:
- relevant files inspected
- findings with file references
- recommended next steps
EOF
)" > /tmp/opencode-analysis.jsonl
```

## Bounded Implementation

```bash
opencode run \
  --dir /absolute/path/to/repo \
  --format json \
  "$(cat <<'EOF'
You are a delegated opencode child agent.

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
)" > /tmp/opencode-result.jsonl
```

## External Sandbox Autonomy

Use `--dangerously-skip-permissions` only when Docker or another external
sandbox is the containment boundary.

```bash
opencode run \
  --dir /workspace \
  --format json \
  --dangerously-skip-permissions \
  "<prompt>" > /logs/opencode-result.jsonl
```

## Local Overrides

When deployed/local `model-config.yaml` provides opencode overrides:

- If `local_overrides.opencode_command` is non-empty, use that command instead
  of `opencode`.
- If `local_overrides.opencode_model_prepend` is non-empty, pass it with
  `--model`.
- If `local_overrides.opencode_provider` is also non-empty and the model value
  has no `/`, pass `--model` as `<provider>/<model>`.
- Keep provider and model ids out of the shared skill config.

## Interactive Session

```bash
opencode /absolute/path/to/repo
```

Use this only when a human will interact with opencode directly. For
agent-driven delegation, prefer `opencode run`.

## Resume

```bash
opencode run --continue "<prompt>"
opencode run --session <session-id> "<prompt>"
```

Resume only when the prior session is known to match the current task and
workspace.
