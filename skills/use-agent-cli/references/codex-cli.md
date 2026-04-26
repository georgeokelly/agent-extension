# Codex CLI Reference

Verified against `codex-cli 0.125.0`. If `codex --version` reports a different
version, re-check `codex --help` and `codex exec --help` before copying a
recipe unchanged.

## Environment Check

```bash
command -v codex
codex --version
codex --help
codex exec --help
```

If Codex CLI reports an authentication problem, stop and ask the user to
authenticate in their own shell. Do not run `codex login` for the user.

## Output Model

For agent-driven execution, prefer `codex exec`. Use:

- `--output-last-message <file>` for the final human-readable answer.
- `--json` with stdout redirected or tee'd to JSONL when a supervisor needs
  progress events.
- `--output-schema <schema>` when another script or agent must parse the final
  answer.

`--output-last-message` writes the last agent message, not the full transcript.

## Read-Only Repository Analysis

```bash
codex exec \
  -C /absolute/path/to/repo \
  --sandbox read-only \
  --output-last-message /tmp/codex-analysis.md \
  "$(cat <<'EOF'
You are a delegated Codex CLI agent.

Analyze the repository for <question>. Do not modify files.
Return:
- relevant files inspected
- findings with file references
- recommended next steps
EOF
)"
```

## Independent Code Review

```bash
codex exec \
  -C /absolute/path/to/repo \
  --sandbox read-only \
  review \
  --uncommitted \
  --output-last-message /tmp/codex-review.md
```

If the built-in review subcommand is too broad, use `codex exec` with a
focused prompt and the same `--sandbox read-only` setting.

## Bounded Implementation

```bash
codex exec \
  -C /absolute/path/to/repo \
  --sandbox workspace-write \
  --ask-for-approval never \
  --output-last-message /tmp/codex-result.md \
  "$(cat <<'EOF'
You are a delegated Codex CLI agent.

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
```

## Execution Modes

- `--full-auto` is not YOLO. In `codex-cli 0.125.0`, it uses
  `approval: never` with `sandbox: workspace-write`.
- `--yolo` is accepted in `codex-cli 0.125.0` even though it is not shown in
  `codex exec --help`; it expands to no approval prompts and no Codex sandbox.
- The documented long flag for YOLO behavior is
  `--dangerously-bypass-approvals-and-sandbox`.
- Use `--yolo` or the long bypass flag only when an external sandbox is the
  real containment boundary.

## Docker + YOLO Implementation

Use this only when Docker is the external sandbox. The container must not mount
host `$HOME`, SSH keys, cloud credentials, the Docker socket, or unrelated
source trees.

This recipe assumes the image already contains `bash`, `git`, `cp`, and
`codex`, and the user has an existing Codex auth/config directory on the host.
Do not run `codex login` inside this flow. Do not mount the source
`CODEX_HOME` directly as read-only; `codex exec --ephemeral` still writes
session/state files in `codex-cli 0.125.0`.

Mount classes:

- `/refs`: read-only source workspace. It may be a non-Git directory containing
  many Git repositories and large untracked files.
- `/workspace`: read-write mirror workspace prepared by the parent before
  launching Docker.
- `/logs`: read-write log area. Store final Markdown, JSONL event streams, and
  other audit records here.

Workspace preparation contract:

- The parent traverses the source workspace before launching Docker.
- For every Git repository found under the source workspace, the parent creates
  a Git clone at the same relative path under `/workspace`.
- Tracked dirty changes from each source Git repository are replayed into that
  clone.
- Files not tracked by any discovered Git repository are not materialized up
  front.
- The child may read untracked files directly from `/refs`.
- If the child needs to write a file that only exists under `/refs`, it must
  copy that file or containing directory into the mirrored path under
  `/workspace` first, then write the `/workspace` copy.
- Final review is based on Git status/diff inside the cloned repositories under
  `/workspace`, plus logs under `/logs`.

```bash
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
REF_WORKSPACE="/absolute/path/to/source-workspace"
WORKSPACE_DIR="/absolute/path/to/codex-workspace"
LOG_DIR="/absolute/path/to/codex-logs"
CODEX_RUN_HOME="$LOG_DIR/codex-home"
mkdir -p "$WORKSPACE_DIR" "$LOG_DIR" "$CODEX_RUN_HOME"

# Parent-side Codex home preparation. Copy auth/config context into a writable
# run home so Codex can create state/session files without mutating the source
# CODEX_HOME. Treat LOG_DIR as sensitive because this may copy auth material.
chmod 700 "$CODEX_RUN_HOME"
for item in auth.json config.toml AGENTS.md skills rules memories; do
  if [ -e "$CODEX_HOME_DIR/$item" ]; then
    cp -a "$CODEX_HOME_DIR/$item" "$CODEX_RUN_HOME/"
  fi
done

REF_WORKSPACE="$(cd "$REF_WORKSPACE" && pwd -P)"

clone_repo() {
  repo="$1"
  rel="$2"
  target="$WORKSPACE_DIR"
  if [ "$rel" != "." ]; then
    target="$WORKSPACE_DIR/$rel"
  fi

  mkdir -p "$(dirname "$target")"
  git clone --no-hardlinks "$repo" "$target"

  if git -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
    patch_file="$target/.parent-tracked-dirty.patch"
    git -C "$repo" diff --binary HEAD > "$patch_file"
    if [ -s "$patch_file" ]; then
      git -C "$target" apply "$patch_file"
    fi
    rm -f "$patch_file"
  fi
}

# Parent-side mirror preparation. Clone each Git repo to the same relative
# path. Do not copy untracked files up front.
if git -C "$REF_WORKSPACE" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  repo_root="$(git -C "$REF_WORKSPACE" rev-parse --show-toplevel)"
  repo_root="$(cd "$repo_root" && pwd -P)"
else
  repo_root=""
fi

if [ "$repo_root" = "$REF_WORKSPACE" ]; then
  clone_repo "$REF_WORKSPACE" "."
else
  find "$REF_WORKSPACE" -name .git -print -prune | while read -r git_marker; do
    repo="${git_marker%/.git}"
    if [ "$repo" = "$REF_WORKSPACE" ]; then
      rel="."
    else
      rel="${repo#"$REF_WORKSPACE"/}"
    fi
    clone_repo "$repo" "$rel"
  done
fi

docker run --rm -i \
  --cap-drop=ALL \
  --security-opt no-new-privileges \
  --pids-limit 512 \
  --memory 8g \
  -e CODEX_HOME=/codex-home \
  -v "$CODEX_RUN_HOME:/codex-home" \
  -v "$REF_WORKSPACE:/refs:ro" \
  -v "$WORKSPACE_DIR:/workspace" \
  -v "$LOG_DIR:/logs" \
  -w /workspace \
  <codex-image> \
  codex exec \
    -C /workspace \
    --ephemeral \
    --skip-git-repo-check \
    --yolo \
    --json \
    --output-last-message /logs/final.md \
    "$(cat <<'EOF'
You are a delegated Codex CLI agent running inside a Docker sandbox.

Task:
- Implement <specific behavior>.

Allowed edits:
- Files under /workspace only.

Workspace contract:
- /refs is read-only source context.
- /workspace is the writable mirror prepared by the parent.
- Git repositories from /refs have been cloned to matching relative paths under
  /workspace.
- Tracked dirty changes from /refs Git repositories have been replayed into
  those clones.
- Files that are not tracked by those Git repositories were intentionally not
  copied into /workspace.
- You may read untracked files directly from /refs.
- If you need to modify an untracked file, first copy it from /refs to the same
  relative path under /workspace, then edit the /workspace copy.
- Do not write to /refs.
- Do not commit, push, create branches, or modify remotes.

Workflow:
1. Inspect the relevant code.
2. Make the smallest coherent change.
3. Run targeted verification.
4. Report changed files, verification results, and remaining risks.
EOF
)" | tee "$LOG_DIR/events.jsonl"
```

After the run, inspect each nested Git repo independently:

```bash
find "$WORKSPACE_DIR" -name .git -print | while read -r gitdir; do
  repo="${gitdir%/.git}"
  echo "== $repo =="
  git -C "$repo" status --short
  git -C "$repo" diff --stat
done
```

## Container-Internal Orchestrator

Use this when the parent agent is already inside a restricted container and
cannot start another Docker container. This is a supervision pattern, not a
hard isolation pattern. The parent gives child autonomy inside an explicit
path contract, records child output, and rejects out-of-contract results.

`RUNNING_IN_CONTAINER=1` is a useful environment hint for this mode. If
`RUNNING_IN_CONTAINER` is unset, treat it as "not configured", not proof that
the parent is outside a container.

```bash
WORKSPACE_DIR="/workspace"
LOG_DIR="/logs"
mkdir -p "$LOG_DIR"
touch "$LOG_DIR/start.marker"

timeout 30m codex exec \
  -C "$WORKSPACE_DIR" \
  --ephemeral \
  --skip-git-repo-check \
  --yolo \
  --json \
  --output-last-message "$LOG_DIR/final.md" \
  "$(cat <<'EOF'
You are a delegated Codex CLI child agent supervised by a parent agent.

Task:
- Implement <specific behavior>.

Writable paths:
- /workspace/<allowed-repo-or-dir>
- /logs

Read-only/context paths:
- /refs
- /workspace/<context-only-dir>

Rules:
- Write only under the writable paths above.
- Read context files from read-only/context paths as needed.
- If a context-only file must be modified, copy it to the corresponding
  writable path first and edit the writable copy.
- Do not commit, push, create branches, modify remotes, or edit credentials.
- If the task requires writing outside the writable paths, stop and report the
  required path.

Final response:
- changed files
- verification commands and results
- files read from context-only paths
- remaining risks
EOF
)" | tee "$LOG_DIR/events.jsonl"

find "$WORKSPACE_DIR" -type f -newer "$LOG_DIR/start.marker" \
  > "$LOG_DIR/files-newer-than-start.txt"
```

After child exits, the parent must inspect:

```bash
find "$WORKSPACE_DIR" -name .git -print | while read -r gitdir; do
  repo="${gitdir%/.git}"
  echo "== $repo =="
  git -C "$repo" status --short
  git -C "$repo" diff --stat
done
```

If any changed file is outside the declared writable paths, reject the child
result or copy only the acceptable diffs forward.

## Structured Final Message

Use `--output-schema` when another script or agent must parse Codex's final
answer.

```bash
cat > /tmp/codex-result.schema.json <<'EOF'
{
  "type": "object",
  "additionalProperties": false,
  "required": ["changed_files", "tests", "summary", "risks"],
  "properties": {
    "changed_files": {
      "type": "array",
      "items": { "type": "string" }
    },
    "tests": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["command", "result"],
        "properties": {
          "command": { "type": "string" },
          "result": { "type": "string" }
        }
      }
    },
    "summary": { "type": "string" },
    "risks": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
EOF

codex exec \
  -C /absolute/path/to/repo \
  --sandbox workspace-write \
  --ask-for-approval never \
  --output-schema /tmp/codex-result.schema.json \
  --output-last-message /tmp/codex-result.json \
  "<prompt>"
```

## JSONL Event Stream

Use `--json` when a supervising process needs progress events.

```bash
codex exec \
  -C /absolute/path/to/repo \
  --sandbox read-only \
  --json \
  "<prompt>" | tee /tmp/codex-events.jsonl
```

## Interactive Session

```bash
codex -C /absolute/path/to/repo "<initial prompt>"
```

Use this only when a human will interact with Codex directly. For agent-driven
delegation, prefer `codex exec`.

## Resume

```bash
codex resume --last
codex exec resume --last --output-last-message /tmp/codex-resume.md
```

Resume only when the prior session is known to match the current task and
workspace.
