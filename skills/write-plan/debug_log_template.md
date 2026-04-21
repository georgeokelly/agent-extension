<!--
  Debug log template — copyable starting point for execution-time debug logs.

  Usage (at the moment the debug loop is entered):
    cp debug_log_template.md debug.<contract-profile>.<task-type>.<MMDDHHMM>.md
    # <contract-profile> and <task-type> mirror the plan's values.
    # <MMDDHHMM> is the local start time, zero-padded (e.g. 04171630).

  Rules, session numbering, and ordering constraints live in `reference.md` → Debug Log Format.
  This file is the shape only; the validator does NOT enforce debug logs.
-->

# DEBUG: plan.<profile>.<task-type>

**Plan:** `plan.<profile>.<task-type>.md`
**Started:** <MMDDHHMM>
**Context:** <one-sentence description of why the debug loop was entered>

---

## Session 1 — <MMDDHHMM>

**Blocker:** <one-sentence symptom>
**Hypothesis:** <root-cause hypothesis being tested>
**Approach:** <concise approach summary>
**Diff from previous:** N/A

### Patch

```diff
--- a/<file>
+++ b/<file>
@@ ... @@
<unified diff>
```

### Recovery

<git command, file backup path, or natural-language instructions that fully undo the patch>

### Result

<success, failure + reason, or partial + what was learned>

<!--
  Session 2+: duplicate the `## Session N` block above and fill `**Diff from
  previous:**` with how this attempt differs from the prior session (required).
  See `reference.md` → Debug Log Format for session numbering rules.
-->

<!--
  Optional sections below — include in this order when applicable, otherwise
  delete the unused blocks. See `reference.md` → Debug Log Format for ordering.
-->

## Stage Reprioritization — <MMDDHHMM>

**Blocked node:** `<id>` — <label>
**Unblocked alternatives:**
- `<id>` — <label> (reason it is independent from the blocker)
**Chosen next node:** `<id>`
**Notes:** <why the switch is safe>

## Analysis Report — <MMDDHHMM>

**Root cause hypothesis:** <consolidated view across failed sessions>
**Per-node blocker mapping:**
- `<id>` — blocked by <X>
- `<id>` — blocked by <Y>
**Candidate new directions:**
- <direction 1>
- <direction 2>

## Self-Review — <MMDDHHMM>

**New approaches found:** <yes + list | no>
**Action:** <continue with new approach | escalate to user>
