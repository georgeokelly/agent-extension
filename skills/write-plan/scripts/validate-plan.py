#!/usr/bin/env python3
"""Lightweight validator for executable-plan markdown files.

See `reference.md` for the plan contract this validator enforces. At a glance:

- Structural metadata, required sections, and contract-profile extras.
- Dependency Graph: acyclic; `h` is the single sink; every node reaches `h`.
- Node Content Templates: each `### <id>: <label>` block's shape is dispatched
  by the node id prefix — `s*` stage, `ck*` checkpoint, `h` handoff.
- Id alignment across `## Dependency Graph`, `## Stages`, and `## Stage Claims`.
- Stage Claims ledger: three-state markers, unclaimed at composer time, last
  entry references the `h` handoff.
- Plan filename.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_METADATA = [
    "Goal",
    "Task Type",
    "Contract Profile",
    "Mode",
    "Primary Success Signal",
]

REQUIRED_HEADINGS = [
    "Inputs / Context Sources",
    "Context Scope",
    "Output",
    "Dependency Graph",
    "Stages",
    "Verification",
    "Decision Points",
    "Decision Log",
    "Debug Log Standard",
    "Stage Claims",
]

# Per-shape content block fields. Shapes are internal names dispatched from
# the node id prefix via `classify_node_id`.
SHAPE_REQUIRED_FIELDS: dict[str, list[str]] = {
    "stage":      ["Purpose", "Checklist"],
    "checkpoint": ["Purpose", "Checklist", "Mode"],
    "handoff":    ["Purpose", "Checklist"],
}
SHAPE_RECOMMENDED_FIELDS: dict[str, list[str]] = {
    "stage":      ["Files", "Exit Signal"],
    "checkpoint": ["Exit Signal", "On Fail"],
    "handoff":    ["Exit Signal"],
}

# Node id prefix conventions. Strict on purpose — unknown prefixes
# fail loud so composers do not silently drift from the contract.
STAGE_ID_PATTERN = re.compile(r"^s\d+$")
CHECKPOINT_ID_PATTERN = re.compile(r"^ck\d+$")
HANDOFF_ID_PATTERN = re.compile(r"^h$")

ALLOWED_CONTRACT_PROFILES = {
    "delivery",
    "refactor",
    "migration",
    "exploration",
}

ALLOWED_MODES = {
    "credit-rich",
    "budget-limited",
}

# Checkpoint-shape `**Mode:**` enum.
ALLOWED_CHECKPOINT_MODES = {
    "auto_review",
    "human_review",
    "hybrid",
}

CONTRACT_PROFILE_EXTRA_HEADINGS = {
    "migration": [
        "Rollout / Rollback",
        "Compatibility / Migration",
        "Risks & Mitigations",
    ],
}

# Conditional `##` sections that are allowed to appear in a plan even when
# not required by a particular profile. Listed in `reference.md` →
# Contract Profiles (Recommended column) and Required vs Conditional matrix.
# Any `##` heading not in REQUIRED_HEADINGS ∪ the profile's extras ∪ this
# set is treated as a composer mistake (typically a sub-heading written at
# the wrong level), and `extract_stages_section` would otherwise truncate
# silently at the first unexpected `##`.
KNOWN_OPTIONAL_HEADINGS = {
    "Non-Goals",
    "Compatibility / Migration",
    "Rollout / Rollback",
    "Risks & Mitigations",
    "Sources / Rationale",
    "Proposed Deliverables",
    "Committed Deliverables",
    "Checkpoint Notes",
    # `Metrics / KPI` is listed as a Conditional plan section in
    # `reference.md` (Required vs Conditional matrix). Without the entry,
    # the L4 orphan-heading detector would reject every plan that
    # legitimately adds observable success metrics.
    "Metrics / KPI",
}

GLOBAL_PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
]

# Bullet may carry an optional checkbox (`- [ ]`, `- [x]`, `- [~]`), so `- [ ] implement later`
# is treated as a hard placeholder just like `- implement later`.
#
# CommonMark §5.2 recognizes three unordered-list bullet characters: `-`, `*`,
# and `+`. The earlier pattern only covered `-` and `*`, so a composer who
# happened to use `+` bullets (including in the Checklist section — which
# `_CHECKLIST_BULLET_RE` accepts for exactly this reason) could slip a
# `+ implement later` past the placeholder check. Adding `+` keeps the
# placeholder sweep and the Checklist bullet reader in sync.
LINE_LEVEL_PLACEHOLDER_PATTERNS = [
    r"^\s*[-*+](?:\s*\[[ xX~]\])?\s*implement later\s*$",
    r"^\s*[-*+](?:\s*\[[ xX~]\])?\s*fill in later\s*$",
    r"^\s*[-*+](?:\s*\[[ xX~]\])?\s*write tests\s*$",
    r"^\s*[-*+](?:\s*\[[ xX~]\])?\s*add tests\s*$",
    r"^\s*[-*+](?:\s*\[[ xX~]\])?\s*handle edge cases\s*$",
]

# Plan file basename must look like `plan.<profile>.<task-type>.md`. `<profile>`
# is a single lowercase word so the dot-separated structure stays unambiguous.
PLAN_FILENAME_PATTERN = re.compile(r"^plan\.[a-z]+\.[a-z0-9-]+\.md$")

# Content block header: `### <id>: <label>`. Id is a word-ish token; we
# classify shape via `classify_node_id` after extraction so the regex can stay
# permissive and still produce a useful "unknown prefix" error downstream.
CONTENT_HEADER_PATTERN = re.compile(
    r"^###\s+([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$",
    flags=re.MULTILINE,
)

# Stage Claims ledger entries: permissive line match first (any `- [ ]` bullet),
# then strict `<id>: <label>` body parse. This lets us distinguish "malformed
# entry" from "wrong marker state" in error messages.
LEDGER_LINE_PATTERN = re.compile(r"^-\s+\[([ xX~])\]\s+(.+?)\s*$")
LEDGER_BODY_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$")

# Reference pointers used in error/warning messages. Named by the destination
# heading; decoupled from reference.md's section numbering.
REF_CORE_CONTRACT = "plan_template.md (copyable shape); reference.md → Core Contract (schema rules)"
REF_NODE_TEMPLATES = "reference.md → Node Content Templates"
REF_STAGE_SHAPE = "reference.md → Stage shape"
REF_CHECKPOINT_SHAPE = "reference.md → Checkpoint shape"
REF_HANDOFF_SHAPE = "reference.md → Handoff shape"
REF_UNKNOWN_PREFIX = "reference.md → Node Content Templates"
REF_CONTRACT_PROFILES = "reference.md → Contract Profiles"
REF_REQUIRED_MATRIX = "reference.md → Required vs Conditional"
REF_DEPENDENCY_GRAPH = "reference.md → Dependency Graph"
REF_CHECKPOINTS = "reference.md → Checkpoints"
REF_STAGE_CLAIMS = "reference.md → Stage Claims"
REF_EXECUTION_MODES = "reference.md → Execution Modes"
REF_PLAN_NAMING = "reference.md → Plan File Naming"


def classify_node_id(nid: str) -> str:
    """Return the shape name for a node id.

    Shape names mirror the keys of `SHAPE_REQUIRED_FIELDS` (`stage` /
    `checkpoint` / `handoff`). An id that does not match any known prefix
    returns `"unknown"` so callers can emit a targeted error.
    """
    if STAGE_ID_PATTERN.match(nid):
        return "stage"
    if CHECKPOINT_ID_PATTERN.match(nid):
        return "checkpoint"
    if HANDOFF_ID_PATTERN.match(nid):
        return "handoff"
    return "unknown"


def shape_reference(shape: str) -> str:
    """Map a shape name to the reference.md anchor error messages cite."""
    return {
        "stage": REF_STAGE_SHAPE,
        "checkpoint": REF_CHECKPOINT_SHAPE,
        "handoff": REF_HANDOFF_SHAPE,
    }.get(shape, REF_NODE_TEMPLATES)


def has_metadata(text: str, field: str) -> bool:
    # Require a non-whitespace value on the same line as the field label.
    # Rejects `**Goal:**` bare-colon and trailing-space-only variants like
    # `**Goal:**   ` that would otherwise silently pass as "present".
    # Use `[ \t]*` (not `\s*`) so the whitespace-hop between label and value
    # does not leak across a newline into the next field's content.
    #
    # Fence-aware: only lines OUTSIDE code fences count. Without this guard,
    # a composer who writes an example plan inside a fenced code block (for
    # example in `Sources / Rationale`) would satisfy the presence check
    # even when the real plan body is missing the field — the validator
    # would silently approve a metadata-less plan because the fenced sample
    # happens to mention `**Contract Profile:**` on one of its lines.
    pattern = re.compile(rf"^\*\*{re.escape(field)}:\*\*[ \t]*\S.*$")
    for line in iter_non_code_lines(text):
        if pattern.match(line):
            return True
    return False


def has_heading(text: str, heading: str) -> bool:
    # Match exactly `## <heading>` (top-level section), not `### <heading>`
    # or deeper. Sub-section headings that happen to share a required name
    # (e.g. a nested `### Risks & Mitigations` inside another section) must
    # not satisfy the required-heading check.
    #
    # Fence-aware for the same reason as `has_metadata`: a `## Stages`
    # quoted inside a fenced example must not be accepted as the real
    # required heading.
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$")
    for line in iter_non_code_lines(text):
        if pattern.match(line):
            return True
    return False


def extract_metadata_value(text: str, field: str) -> str | None:
    # Same-line value only: `[ \t]*` prevents the value-capturing group from
    # crossing a newline into the next line's content if this field were left
    # blank (e.g. `**Mode:**\n**Primary Success Signal:** ...`).
    #
    # Fence-aware: a fenced example's `**Contract Profile:** \`delivery\``
    # must not be returned as the real plan's value when the real body
    # omits the field (or conflicts with it). Walking non-code lines in
    # document order also preserves first-match semantics — the real
    # metadata block is at the top of the plan, above any fenced examples.
    pattern = re.compile(
        rf"^\*\*{re.escape(field)}:\*\*[ \t]*`?(.+?)`?[ \t]*$"
    )
    for line in iter_non_code_lines(text):
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


# Per CommonMark §4.5, a fence opener may be preceded by at most 3 spaces
# of indentation; a 4th space would make the line an indented code block
# instead. Previously `^\s*` matched arbitrarily-indented `\`\`\``
# sequences (including deeply-indented ones inside list items), which
# could toggle the fence stack where CommonMark would not.
_FENCE_TOKEN_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _update_fence_stack(line: str, fence_stack: list[str]) -> bool:
    """Return True when `line` changes the fence stack (opens / closes).

    Per CommonMark §4.5 the only marker that closes an open fence is one
    that uses the same fence character and is at least as long as the
    opener; every other marker inside an open fence is literal content,
    NOT a nested opener. Earlier versions pushed mismatched tokens onto
    the stack, which leaked depth: a literal `~~~` inside a ``` fence, or
    a short-of-length `` `` inside a 4-backtick fence, would stick around
    and keep the tracker "inside a fence" well past the real closer.

    Additional rules enforced to stay faithful to CommonMark §4.5:

    - A **closing** fence may be followed only by horizontal whitespace.
      Any trailing non-whitespace content (an info-string–shaped
      suffix) disqualifies the line as a closer; it reverts to literal
      content inside the open fence. Without this, an in-fence literal
      like ```` ``` hello ```` would incorrectly pop the stack and let
      downstream validators see content that is really inside the
      fence.
    - A backtick **opener**'s info string may not contain any backtick
      characters. A line whose "info string" already holds a `` ` ``
      is therefore not a legal opener either; it falls through as
      literal text. (Tilde fences have no such restriction.)

    Returns False when `line` is either not a fence marker at all, or is
    a fence-shaped token appearing as literal content inside an open
    fence, or fails one of the CommonMark suffix rules above. Callers
    treat `False` as "this line is not a fence edge"; combined with
    inspecting `fence_stack` after the call, they can distinguish plain
    prose (empty stack) from in-fence content (non-empty stack).
    """
    match = _FENCE_TOKEN_PATTERN.match(line)
    if not match:
        return False
    token = match.group(1)
    trailing = line[match.end():]
    if fence_stack:
        if token[0] == fence_stack[-1][0] and len(token) >= len(fence_stack[-1]):
            # CommonMark §4.5: a closer may only be followed by spaces/tabs
            # (and the line terminator, already stripped by splitlines()).
            # Any non-whitespace after the fence token downgrades the line
            # to literal content inside the still-open fence.
            if trailing.strip():
                return False
            fence_stack.pop()
            return True
        return False
    # Opener path: reject backtick-fence openers whose info string
    # contains a backtick. The info string is everything after the
    # fence token on the same line; per CommonMark §4.5 such a line is
    # not a valid opener, so we treat it as literal content (caller
    # then sees an empty stack and processes the line normally).
    if token[0] == "`" and "`" in trailing:
        return False
    fence_stack.append(token)
    return True


def iter_non_code_lines(text: str) -> list[str]:
    """Return every line of `text` outside fenced code blocks.

    The fence tracker is stack-based and length-aware, so nested fences
    (e.g. a 4-backtick wrapper containing a 3-backtick Mermaid block) are
    resolved correctly. Without this, a 3-backtick token inside a
    4-backtick wrapper would flip the simple toggle off and misclassify
    downstream lines as plain prose.
    """
    fence_stack: list[str] = []
    result: list[str] = []
    for line in text.splitlines():
        if _update_fence_stack(line, fence_stack):
            continue
        if not fence_stack:
            result.append(line)
    return result


def find_soft_placeholders(text: str) -> list[str]:
    """Return soft placeholders (TODO / TBD) that agent should clarify with user.

    Soft placeholders are explicit markers used at plan-writing time to flag
    information gaps the agent could not resolve alone. They surface as
    warnings so a downstream agent can confirm the detail with the user
    before finalization, rather than blocking plan validation outright.

    Case handling: both `find_soft_placeholders` and
    `find_hard_placeholders` run their patterns with `re.IGNORECASE`.
    That shared choice is deliberate but for slightly different reasons,
    spelled out here to discourage accidentally "unifying" one to the
    other in a future cleanup:

    - `TODO` / `TBD` are acronym markers that are almost always written
      uppercase in practice, but composers and pasted content sometimes
      drop the caps (`todo`, `tbd`, `Todo`). Treating them as
      case-insensitive keeps the reminder visible across those variants
      without forcing a style fight, because the downstream behaviour is
      the same regardless of capitalisation (a downstream agent will
      still need to surface the gap to the user).
    - Hard placeholders (`- implement later`, `- fill in later`, …) are
      whole-phrase bullet items; real content that happens to contain
      one of those phrases in prose is extremely rare, and the bullet
      anchor already makes the match narrow. Keeping IGNORECASE on that
      path is primarily about tolerating `Implement Later` / casing
      drift in bulleted checklists; the reminder semantics are the same.
    """
    findings: list[str] = []
    lines = iter_non_code_lines(text)

    for line in lines:
        for pattern in GLOBAL_PLACEHOLDER_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(f"`{pattern}` on line: {line.strip()}")

    return list(dict.fromkeys(findings))


def find_hard_placeholders(text: str) -> list[str]:
    """Return hard placeholders (lazy list items) that must be replaced.

    Hard placeholders are bullet list items whose entire content is a generic
    verb phrase with no concrete task (for example: `- implement later`).
    These are rejected outright because they indicate the plan has not been
    written, not that a known gap needs user input.
    """
    findings: list[str] = []
    lines = iter_non_code_lines(text)

    for line in lines:
        for pattern in LINE_LEVEL_PLACEHOLDER_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(f"`{pattern}` on line: {line.strip()}")

    return list(dict.fromkeys(findings))


def validate_filename(path: Path) -> list[str]:
    # Two-stage check: (1) shape matches the overall pattern, (2) the profile
    # segment is one of the four allowed contract profiles. Structural-only
    # matches like `plan.foo.task.md` would otherwise look well-formed but
    # carry a meaningless profile label.
    if not PLAN_FILENAME_PATTERN.match(path.name):
        return [
            (
                f"Filename `{path.name}` does not match required pattern "
                f"`plan.<contract-profile>.<task-type>.md` "
                f"(profile: single lowercase word; task-type: lowercase kebab-case slug). "
                f"Reference: {REF_PLAN_NAMING}."
            )
        ]

    profile_segment = path.name.split(".")[1]
    if profile_segment not in ALLOWED_CONTRACT_PROFILES:
        return [
            (
                f"Filename `{path.name}` profile segment `{profile_segment}` is not "
                f"a recognized contract profile. "
                f"Expected one of: {sorted(ALLOWED_CONTRACT_PROFILES)}. "
                f"Reference: {REF_PLAN_NAMING} and {REF_CONTRACT_PROFILES}."
            )
        ]

    return []


def _detect_unclosed_fence(text: str) -> tuple[str, int] | None:
    """Return `(opener_token, line_no)` for an unclosed fence, else None.

    An unclosed fence is a code fence opener with no matching closer
    before end-of-file. Downstream this is catastrophic: every line
    from the opener onward is treated as in-fence content, so `##`
    headings, `### <id>: <label>` content blocks, metadata lines,
    and ledger entries are all hidden from the validator. The
    resulting error cascade ("missing heading `## Stages`", "no
    content blocks", etc.) points nowhere near the root cause, which
    is often a single stray fence in a fenced example.

    Fires a dedicated warning so the composer can find the broken
    fence directly. Kept as a warning (not a hard error) because
    `validate()` still runs the rest of its checks afterwards and
    surfaces whichever structural issues happen to survive; the
    unclosed-fence warning at the top of the output points the
    composer at the real fix.
    """
    fence_stack: list[str] = []
    opener_line: int | None = None
    prev_stack_depth = 0
    for idx, line in enumerate(text.splitlines(), start=1):
        if _update_fence_stack(line, fence_stack):
            # Track the FIRST unmatched opener's line number. When the
            # stack grows we just opened a fence; when it shrinks we
            # closed one, so reset the tracker if the shrink empties
            # the stack (every opener has since been matched).
            if len(fence_stack) > prev_stack_depth and opener_line is None:
                opener_line = idx
            if not fence_stack:
                opener_line = None
            prev_stack_depth = len(fence_stack)
    if fence_stack and opener_line is not None:
        return fence_stack[0], opener_line
    return None


def validate(text: str, path: Path | None = None) -> tuple[list[str], list[str]]:
    # Normalize line endings before any regex / line-scan logic runs.
    # Plans authored on Windows editors (CRLF) or copy-pasted from
    # mixed-EOL sources otherwise leave a stray `\r` at end-of-line,
    # which breaks anchored `$` matches (`^...$` under re.MULTILINE sees
    # `\r` as a non-newline character before `$`) and fence-trailing
    # checks (the `\r` counts as non-whitespace for our closer rule in
    # `_update_fence_stack`). Doing it once at entry means every
    # downstream helper can assume LF-only input.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    issues: list[str] = []
    warnings: list[str] = []

    # Detect unclosed fence BEFORE running the rest of the checks so the
    # warning appears alongside (and is easier to correlate with) the
    # downstream cascade it produces. Implemented as a warning rather
    # than an early-return error because the downstream checks still
    # provide useful signal on the already-closed portion of the plan.
    unclosed = _detect_unclosed_fence(text)
    if unclosed is not None:
        opener_token, opener_line = unclosed
        warnings.append(
            f"Unclosed code fence: opener `{opener_token}` at line "
            f"{opener_line} has no matching closer before end-of-file. "
            f"Every subsequent line is treated as in-fence content, so "
            f"downstream errors (missing headings, missing content "
            f"blocks, id mismatches) are likely symptoms of this one "
            f"unclosed fence rather than independent problems. Close "
            f"the fence with a matching "
            f"`{opener_token[0] * len(opener_token)}` line at the "
            f"intended end of the fenced block and re-run the validator."
        )

    if path is not None:
        issues.extend(validate_filename(path))

    for field in REQUIRED_METADATA:
        if not has_metadata(text, field):
            issues.append(
                f"Missing metadata line: `**{field}:**`. Reference: {REF_CORE_CONTRACT}."
            )

    for heading in REQUIRED_HEADINGS:
        if not has_heading(text, heading):
            issues.append(
                f"Missing heading: `## {heading}`. Reference: {REF_CORE_CONTRACT}."
            )

    contract_profile = extract_metadata_value(text, "Contract Profile")
    mode = extract_metadata_value(text, "Mode")

    if contract_profile is None:
        issues.append(
            f"Could not extract `**Contract Profile:**`. Reference: {REF_CONTRACT_PROFILES}."
        )
    elif contract_profile not in ALLOWED_CONTRACT_PROFILES:
        issues.append(
            f"Unknown contract profile `{contract_profile}`. "
            f"Expected one of: {sorted(ALLOWED_CONTRACT_PROFILES)}. "
            f"Reference: {REF_CONTRACT_PROFILES}."
        )

    if mode is None:
        issues.append(
            f"Could not extract `**Mode:**`. Reference: {REF_EXECUTION_MODES}."
        )
    elif mode not in ALLOWED_MODES:
        issues.append(
            f"Unknown mode `{mode}`. "
            f"Expected one of: {sorted(ALLOWED_MODES)}. "
            f"Reference: {REF_EXECUTION_MODES}."
        )

    if contract_profile in CONTRACT_PROFILE_EXTRA_HEADINGS:
        for heading in CONTRACT_PROFILE_EXTRA_HEADINGS[contract_profile]:
            if not has_heading(text, heading):
                issues.append(
                    f"Contract profile `{contract_profile}` requires `## {heading}`. "
                    f"Reference: {REF_REQUIRED_MATRIX}."
                )

    # Orphan `##` detection runs after profile extraction so that the
    # allowed-heading set can include the profile's required sections.
    issues.extend(validate_top_level_headings(text, contract_profile))

    for finding in find_hard_placeholders(text):
        issues.append(
            f"Hard placeholder (lazy list item): {finding}. "
            f"Replace with a concrete, actionable task."
        )

    for finding in find_soft_placeholders(text):
        warnings.append(
            f"Soft placeholder {finding} — agent should clarify with user before finalization."
        )

    # Content block + DAG + Stage Claims validation. We do these together so
    # we can run the id-alignment check once all three id sets are known.
    stages_section = extract_stages_section(text)
    content_blocks: list[tuple[str, str, str]] = []
    if stages_section is None:
        issues.append(
            f"Could not extract `## Stages` section. Reference: {REF_NODE_TEMPLATES}."
        )
    else:
        content_blocks = split_content_blocks(stages_section)
        if not content_blocks:
            issues.append(
                f"`## Stages` contains no `### <id>: <label>` content blocks. "
                f"Reference: {REF_NODE_TEMPLATES}."
            )
        else:
            issues.extend(validate_content_blocks(content_blocks))
            issues.extend(validate_last_block_is_handoff(content_blocks))
            warnings.extend(recommended_content_warnings(content_blocks, mode))

    dag_issues, dag_nodes = validate_dependency_graph(text)
    issues.extend(dag_issues)

    claim_issues, claim_ids = validate_stage_claims(text)
    issues.extend(claim_issues)

    # Id alignment is only meaningful if all three inputs exist and parsed to
    # at least one id; otherwise upstream errors above already describe the
    # shape of the problem.
    if dag_nodes and content_blocks and claim_ids is not None:
        block_ids = {nid for (nid, _label, _text) in content_blocks}
        issues.extend(validate_id_alignment(set(dag_nodes), block_ids, claim_ids))

    return issues, warnings


def _extract_section(text: str, heading: str) -> str | None:
    """Return the body of a top-level section between its heading and the
    next top-level section, fence-aware.

    "Fence-aware" means a `##` line appearing inside a fenced code block
    does NOT terminate the section, and a `## <heading>` line appearing
    inside a code fence does NOT open one either. Composers routinely
    illustrate markdown inside a fenced block (for example a sample
    heading quoted in `Sources / Rationale` or a plan that discusses its
    own structure in a prose section); a naïve regex would misread those
    lines as section boundaries and either truncate the wanted section
    or skip past its real header.

    Two-phase scan:

    1. Walk lines with a fresh fence stack until we see the heading
       line outside any fence. Record the first body line index.
    2. Walk from there with a second fresh fence stack, collecting body
       lines until the next `## <word>` heading outside any fence.

    Fence edge lines themselves are preserved in the output so downstream
    helpers (e.g. `split_content_blocks`, `parse_dag`) still see the full
    block they would read on their own.

    Returns `None` when the heading is not found outside any fence,
    matching the previous behaviour of the specialized extractors it
    replaces.
    """
    heading_re = re.compile(rf"^##\s+{re.escape(heading)}\s*$")
    lines = text.splitlines()

    start_idx: int | None = None
    start_fence_stack: list[str] = []
    for idx, line in enumerate(lines):
        if _update_fence_stack(line, start_fence_stack):
            continue
        if start_fence_stack:
            continue
        if heading_re.match(line):
            start_idx = idx + 1
            break
    if start_idx is None:
        return None

    body_lines: list[str] = []
    body_fence_stack: list[str] = []
    for line in lines[start_idx:]:
        if _update_fence_stack(line, body_fence_stack):
            body_lines.append(line)
            continue
        if not body_fence_stack and re.match(r"^##\s+\S", line):
            break
        body_lines.append(line)
    return "\n".join(body_lines)


def extract_stages_section(text: str) -> str | None:
    """Return the body of `## Stages`. See `_extract_section`."""
    return _extract_section(text, "Stages")


_CONTENT_HEADER_LINE_RE = re.compile(
    r"^###\s+([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$"
)


def split_content_blocks(stages_section: str) -> list[tuple[str, str, str]]:
    """Return [(id, label, block_text)] for each `### <id>: <label>` block.

    The block_text starts at the header line and runs up to the next content
    header or the end of the section, so field-presence checks can regex
    against it directly. A composer who quotes a markdown plan sample inside
    a fenced code block (e.g. illustrating node shape in a sub-section)
    previously had the sample's inner `### s2: ...` line treated as a real
    structural header, silently splitting the outer block in two and
    cascading into bogus "duplicate id" / "missing field" errors.

    Fence-aware scan: walk the section line-by-line with the same
    `_update_fence_stack` tracker used elsewhere. Only `### <id>: <label>`
    lines that appear OUTSIDE any code fence are treated as real headers;
    inner fenced headers fall through as literal content of the enclosing
    block, which is what the composer intended when they wrote the fenced
    example.

    The returned `block_text` still contains the raw lines (including any
    fenced samples) so error messages can quote surrounding context; the
    downstream field-presence helpers (`_field_present`,
    `_checklist_*`) are themselves fence-aware so they will not be fooled
    by labels inside those fenced samples.
    """
    lines = stages_section.splitlines()
    header_positions: list[tuple[int, str, str]] = []
    fence_stack: list[str] = []
    for idx, line in enumerate(lines):
        if _update_fence_stack(line, fence_stack):
            continue
        if fence_stack:
            continue
        match = _CONTENT_HEADER_LINE_RE.match(line)
        if match:
            header_positions.append(
                (idx, match.group(1).strip(), match.group(2).strip())
            )

    if not header_positions:
        return []

    blocks: list[tuple[str, str, str]] = []
    for i, (start_idx, nid, label) in enumerate(header_positions):
        end_idx = (
            header_positions[i + 1][0]
            if i + 1 < len(header_positions)
            else len(lines)
        )
        block_text = "\n".join(lines[start_idx:end_idx])
        # Preserve the trailing newline if the original section ended with
        # one, so fence-aware line iteration inside the block continues to
        # behave identically whether this is the last block or not.
        if end_idx == len(lines) and stages_section.endswith("\n"):
            block_text += "\n"
        blocks.append((nid, label, block_text))
    return blocks


_CHECKLIST_LABEL_RE = re.compile(r"^\*\*Checklist:\*\*[ \t]*$", flags=re.MULTILINE)
# Accept any inline content after `**Checklist:**`, with or without a space
# before it. `**Checklist:**foo` is the same mistake as `**Checklist:** foo`
# semantically — both treat Checklist as a scalar field — and should be
# flagged identically. Earlier versions required at least one space (`[ \t]+`)
# and silently missed the no-space variant, falling through to the weaker
# "missing label" diagnostic.
_CHECKLIST_INLINE_RE = re.compile(
    r"^\*\*Checklist:\*\*[ \t]*\S.*$", flags=re.MULTILINE
)
# Bullet content must start with a non-whitespace character after the
# marker + checkbox + separator. The earlier `\s+.+$` permitted a single
# trailing space to satisfy the content clause (via regex backtracking),
# so a placeholder bullet like `- [ ]    ` would be treated as having
# content when in fact nothing was written. Anchoring to `\S` ensures at
# least one visible character exists; the remainder of the line is
# unconstrained so multi-word items remain valid.
_CHECKLIST_BULLET_RE = re.compile(
    r"^\s*[-*+]\s+\[[ xX~]\]\s+\S.*$", flags=re.MULTILINE
)


def _non_code_block_text(block_text: str) -> str:
    """Return `block_text` with fenced code lines elided.

    Content blocks routinely embed fenced samples (e.g. a Mermaid snippet
    inside a checkpoint's Purpose, or a quoted bullet in a handoff's
    rationale). The field-presence and checklist helpers below must not
    be fooled by labels / bullets that live inside those samples; walking
    only the non-code lines gives the same answer the composer's eye
    would give.

    The returned string preserves the relative order of non-code lines
    so `_checklist_bullets_after_label`'s "bullets AFTER the label"
    anchoring still works (if the label and all bullets are inside a
    fence, they are all elided together and the block correctly reads
    as having no Checklist; if they are outside a fence, their relative
    order is preserved).
    """
    return "\n".join(iter_non_code_lines(block_text))


def _checklist_label_present(block_text: str) -> bool:
    """Return True if the block contains a `**Checklist:**` label line.

    The label is written as a standalone line, e.g. `**Checklist:**`
    possibly followed by horizontal whitespace. It MUST appear above the
    bullets; otherwise the executor tooling cannot distinguish Checklist
    items from, say, the handoff's sign-off bullets in a different
    section. Fence-aware — a `**Checklist:**` appearing inside a fenced
    example does not satisfy the real block's requirement.
    """
    return bool(_CHECKLIST_LABEL_RE.search(_non_code_block_text(block_text)))


def _checklist_inline_value_present(block_text: str) -> bool:
    """Return True if the block uses the (rejected) inline form.

    Targets `**Checklist:** some text` on a single line. The core
    contract carves out Checklist as the one exception to the single-
    line field rule: the label must stand alone, with `- [ ]` bullets
    beneath. Flagging inline usage with its own diagnostic is more
    actionable than the generic "missing Checklist label" message —
    the composer sees exactly which line to restructure. Fence-aware:
    an inline form quoted inside a fenced example is literal prose,
    not a real block violation.
    """
    return bool(_CHECKLIST_INLINE_RE.search(_non_code_block_text(block_text)))


def _checklist_bullets_after_label(block_text: str) -> bool:
    """Return True if `- [ ]` bullets appear *after* the `**Checklist:**` label.

    Anchoring to the label position prevents unrelated bullets earlier
    in the block (for example a `- [ ]`-shaped line mistakenly placed
    under Purpose, or a pre-seeded handoff checklist appearing before a
    fresh Checklist section) from satisfying the presence check when
    the Checklist section itself is empty. Fence-aware — a fenced
    example's checklist neither provides nor consumes the anchor.
    """
    non_code = _non_code_block_text(block_text)
    label_match = _CHECKLIST_LABEL_RE.search(non_code)
    if not label_match:
        return False
    after = non_code[label_match.end() :]
    return bool(_CHECKLIST_BULLET_RE.search(after))


def _field_present(block_text: str, field: str) -> bool:
    # Require non-whitespace value on the same line as the field label.
    # `[ \t]*` keeps the whitespace hop bounded to the same line so that
    # `**Purpose:**  \n**Files:** ...` does not treat `*Files:** ...` on
    # the next line as the Purpose value (which `\s*` would allow, because
    # `\s` greedily consumes newlines). Fence-aware: a fenced example's
    # `**Purpose:** ...` line must not satisfy the real block's field
    # requirement.
    return bool(
        re.search(
            rf"^\*\*{re.escape(field)}:\*\*[ \t]*\S.*$",
            _non_code_block_text(block_text),
            flags=re.MULTILINE,
        )
    )


def collect_top_level_headings(text: str) -> list[str]:
    """Return every `## <heading>` text outside code fences, in document order.

    Uses `iter_non_code_lines` so headings inside fenced code blocks (for
    example a markdown example illustrated in `Sources / Rationale`) are
    excluded. Matches exactly two leading `#` followed by at least one
    whitespace then non-whitespace content; `###` or deeper falls through.
    """
    headings: list[str] = []
    pattern = re.compile(r"^##\s+(\S.*?)\s*$")
    for line in iter_non_code_lines(text):
        match = pattern.match(line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def _allowed_top_level_headings(contract_profile: str | None) -> set[str]:
    """Return the union of required, profile-extra, and optional ``##`` names."""
    allowed: set[str] = set(REQUIRED_HEADINGS)
    allowed.update(KNOWN_OPTIONAL_HEADINGS)
    if contract_profile and contract_profile in CONTRACT_PROFILE_EXTRA_HEADINGS:
        allowed.update(CONTRACT_PROFILE_EXTRA_HEADINGS[contract_profile])
    return allowed


def _find_misplaced_heading_in_stages(
    text: str,
) -> tuple[int, str, bool] | None:
    """Return ``(line_no, heading, handoff_after)`` for a ``## X`` that
    truncates Stages early, or ``None`` when the scan should stay silent.

    ``extract_stages_section`` terminates the Stages body at the first
    ``##`` that follows the ``## Stages`` header. That termination is
    *legal* when Stages has been walked to completion — i.e. the
    ``### h: ...`` handoff content block has already appeared. When it
    has NOT, the ``##`` is a misplacement: the composer intended it as
    a plan-level section but wrote it at a point that cuts Stages
    short, leaving some content blocks (including potentially the
    handoff itself) outside the section. Downstream this surfaces as
    confusing "missing node" / "last block is not handoff" errors with
    no pointer to the root cause; flagging the offending heading by
    name lets the composer move it below the handoff or demote it to
    ``###``.

    The third return field, ``handoff_after``, tells the caller
    whether a ``### h: ...`` block exists anywhere *after* the
    candidate ``##`` line (fence-aware). It enables two distinct
    diagnostics: when the handoff still lives below the misplaced
    heading, "move the heading below the handoff" is the correct fix;
    when the plan has no ``### h: ...`` anywhere (neither before nor
    after), the heading is merely a secondary symptom and the
    composer needs to add the handoff first.

    Two trigger modes:

    1. **Content-before case**: at least one ``### <id>: <label>``
       content block was collected inside Stages before the ``##``.
       The composer clearly started writing Stages and then wrote a
       plan-level heading that truncated the section. Fire.
    2. **Empty-stages-with-content-below case**: no content block has
       been collected yet, but the scan can see at least one
       ``### <id>: <label>`` further down the file. Stages *does*
       have content, just sitting below a misplaced ``##`` that
       silently truncated it away. Fire.
    3. **Truly empty Stages**: no content block before the ``##`` and
       none afterwards either. Other validators (``no content
       blocks``, ``missing handoff``) already describe that state
       with clearer messages; reporting it here would only add
       noise. Stay silent.

    The failure is positional, not name-based: a *known* name like
    ``Non-Goals`` written here is just as bad as an unknown one. The
    unknown-heading sweep reports unknown names with its own message,
    so the two diagnostics naturally complement each other — if both
    fire on the same line they describe the same mistake from two
    angles, which is fine (the composer fixes once, both clear).
    """
    lines = text.splitlines()
    heading_re = re.compile(r"^##\s+(\S.*?)\s*$")
    stages_re = re.compile(r"^##\s+Stages\s*$")
    # Strictly the `### <id>: <label>` content-block header shape. The
    # loose `^###\s+\S` version used to fire on any `### Something`
    # sub-heading that composers sometimes place under Stages (e.g. a
    # transient `### Smoke Tests` note), which both (a) falsely counted
    # as a content block for the `seen_content_block` trigger and (b)
    # suppressed the misplaced-`##` diagnostic when Stages *really* had
    # no content blocks yet. Mirroring `CONTENT_HEADER_PATTERN` keeps
    # this scan in lockstep with the main content-block parser.
    content_block_re = re.compile(r"^###\s+[A-Za-z][A-Za-z0-9_-]*\s*:\s*.+$")
    handoff_block_re = re.compile(r"^###\s+h\s*:")

    # First pass: collect events (fence-aware) so the second pass can
    # cheaply decide whether a ``### <id>: ...`` appears later without
    # re-scanning. ``kind`` is "stages" / "h2" / "handoff" / "h3".
    events: list[tuple[int, str, str]] = []
    fence_stack: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if _update_fence_stack(line, fence_stack):
            continue
        if fence_stack:
            continue
        if stages_re.match(line):
            events.append((idx, "stages", "Stages"))
            continue
        if handoff_block_re.match(line):
            events.append((idx, "handoff", ""))
            continue
        if content_block_re.match(line):
            events.append((idx, "h3", ""))
            continue
        match = heading_re.match(line)
        if match:
            events.append((idx, "h2", match.group(1).strip()))

    in_stages = False
    seen_content_block = False
    seen_handoff_block = False
    for i, (idx, kind, value) in enumerate(events):
        if kind == "stages":
            in_stages = True
            seen_content_block = False
            seen_handoff_block = False
            continue
        if not in_stages:
            continue
        if kind == "handoff":
            seen_content_block = True
            seen_handoff_block = True
            continue
        if kind == "h3":
            seen_content_block = True
            continue
        # Any other ``##`` line inside Stages while walking is a
        # candidate boundary/misplacement.
        if kind != "h2":
            continue
        # Lookahead: does the remainder of the document contain any
        # more ``### <id>: ...`` (content block or handoff) outside of
        # code fences? If so, Stages was cut short — whether the
        # composer "wrote nothing yet" or "wrote some blocks" matters
        # only for the diagnostic wording, not for whether to fire.
        later = events[i + 1 :]
        content_after = any(ev[1] in ("h3", "handoff") for ev in later)
        handoff_after = any(ev[1] == "handoff" for ev in later)
        if seen_handoff_block:
            return None
        if seen_content_block or content_after:
            return idx, value, handoff_after
        return None
    return None


def validate_top_level_headings(
    text: str, contract_profile: str | None
) -> list[str]:
    """Reject any `## <heading>` that is not a known top-level plan section.

    An unknown `## Xxx` heading is almost always a composer mistake — a
    sub-heading written at the wrong level. Because `extract_stages_section`
    terminates the Stages body at the first subsequent `##`, a stray
    top-level heading *inside* a content block silently truncates every
    later stage block and surfaces downstream as confusing "missing node"
    or "last block is not handoff" errors with no pointer to the true
    cause. Flagging the unknown heading by name lets the composer fix the
    heading level directly.

    Allowed set: `REQUIRED_HEADINGS` ∪ the active profile's extras ∪
    `KNOWN_OPTIONAL_HEADINGS`.

    Additionally flags the complementary failure mode: a *legal* `##`
    heading placed inside the Stages body (e.g. `## Non-Goals` written
    after `### s1: ...` instead of before it). Without this branch, the
    composer would see only a cascade of missing-block / wrong-handoff
    errors produced by the silent truncation, with no indication that
    the root cause is a misplaced section heading.
    """
    allowed = _allowed_top_level_headings(contract_profile)

    issues: list[str] = []
    # Two-phase walk so duplicate reporting can span the full document in
    # one pass. `counts` tallies every allowed `##` occurrence so we can
    # fire a single aggregated error per duplicated name; `unknown_seen`
    # debounces the unknown-heading branch (so the same typo reported
    # twice does not produce two error lines).
    counts: dict[str, int] = {}
    unknown_seen: set[str] = set()
    for heading in collect_top_level_headings(text):
        if heading in allowed:
            counts[heading] = counts.get(heading, 0) + 1
            continue
        if heading in unknown_seen:
            continue
        unknown_seen.add(heading)
        issues.append(
            f"Unknown top-level heading `## {heading}`. Expected one of the "
            f"required/profile/optional sections, or a sub-heading (`###` or "
            f"deeper) nested under an existing section. A stray `##` inside "
            f"a content block will silently truncate `## Stages` and surface "
            f"as confusing downstream errors. "
            f"Reference: {REF_CORE_CONTRACT}."
        )

    # Duplicate required/profile/optional heading: without this check the
    # second `## Stages` (or any other allowed name) would silently
    # truncate the first one's body at the duplicate's line, giving the
    # composer the same confusing "missing node" / "last block is not
    # handoff" cascade that the misplaced-heading branch already tries
    # to prevent. Each section is expected to appear exactly once; if a
    # composer needs to iterate (e.g. replacing content), they should
    # edit in place rather than appending a second heading.
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    for name in duplicates:
        issues.append(
            f"Top-level heading `## {name}` appears {counts[name]} times. "
            f"Each allowed plan section must occur exactly once; a second "
            f"occurrence silently truncates the first at that line and "
            f"surfaces as confusing downstream errors (missing nodes, "
            f"wrong handoff, etc). Keep a single `## {name}` section and "
            f"consolidate its body. Reference: {REF_CORE_CONTRACT}."
        )

    misplaced = _find_misplaced_heading_in_stages(text)
    if misplaced is not None:
        line_no, heading, handoff_after = misplaced
        if handoff_after:
            issues.append(
                f"Top-level heading `## {heading}` appears inside the "
                f"`## Stages` body at line {line_no}, before the handoff "
                f"block `### h: ...` is reached. This silently truncates "
                f"Stages at that line, leaving later content blocks (and "
                f"possibly the handoff itself) outside the section. Move "
                f"the heading below the handoff, or demote it to `###` if "
                f"it was meant as a sub-heading. Reference: {REF_CORE_CONTRACT}."
            )
        else:
            # Without a `### h: ...` anywhere after the candidate
            # heading, "move below the handoff" is misleading advice:
            # the handoff does not exist yet. Point at the real root
            # cause (missing handoff) and describe the heading as a
            # secondary effect.
            issues.append(
                f"Top-level heading `## {heading}` appears inside the "
                f"`## Stages` body at line {line_no} and truncates the "
                f"section early, but no `### h: <label>` handoff block "
                f"exists later in the plan either. Add the `h` handoff "
                f"as the final content block under `## Stages`, and "
                f"either move this heading below it or demote it to "
                f"`###` if it was meant as a sub-heading. "
                f"Reference: {REF_CORE_CONTRACT}."
            )

    return issues


def validate_content_blocks(
    blocks: list[tuple[str, str, str]],
) -> list[str]:
    """Validate each content block's shape against its id-prefix template.

    Rules enforced:
    - Unknown id prefixes are rejected.
    - Non-handoff ids are unique across content blocks (duplicate `s*` / `ck*`
      blocks would otherwise be silently deduped by set-based id alignment).
    - Exactly one `h` handoff block exists; multiple `h` blocks are rejected.
    - Per-shape required fields are present (stage / checkpoint / handoff).
    - Checkpoint `**Mode:**` value is one of the allowed enum.
    """
    issues: list[str] = []
    handoff_blocks: list[str] = []

    # Detect duplicate non-handoff ids up front. Handoff duplicates are
    # caught with a more targeted message later in this function.
    counts: dict[str, int] = {}
    for nid, _label, _text in blocks:
        if classify_node_id(nid) == "handoff":
            continue
        counts[nid] = counts.get(nid, 0) + 1
    duplicate_ids = sorted(nid for nid, count in counts.items() if count > 1)
    if duplicate_ids:
        items = ", ".join(f"`{n}`" for n in duplicate_ids)
        issues.append(
            f"Duplicate content block ids under `## Stages`: {items}. "
            f"Every DAG node must have exactly one `### <id>: <label>` block. "
            f"Reference: {REF_NODE_TEMPLATES}."
        )

    for nid, label, block_text in blocks:
        shape = classify_node_id(nid)
        ref = shape_reference(shape)

        if shape == "unknown":
            issues.append(
                f"Content block `### {nid}: {label}` uses unknown id prefix. "
                f"Expected: `s<N>` (stage), `ck<N>` (checkpoint), or `h` (handoff). "
                f"Reference: {REF_UNKNOWN_PREFIX}."
            )
            continue

        if shape == "handoff":
            handoff_blocks.append(nid)

        for field in SHAPE_REQUIRED_FIELDS[shape]:
            if field == "Checklist":
                # Three failure modes, ordered from most specific to least:
                # (1) inline form `**Checklist:** some text` — the composer
                #     treated Checklist as a single-line field, forgetting
                #     the carve-out in the core contract. Flag it directly
                #     so the fix ("split into label + bullets") is obvious.
                # (2) missing label — bullets may exist below but lack
                #     anchor; executors cannot unambiguously attribute them.
                # (3) label present but no bullets beneath it — an empty
                #     Checklist section is a stub, not a completed block.
                if _checklist_inline_value_present(block_text):
                    issues.append(
                        f"`### {nid}: {label}` uses the inline form "
                        f"`**Checklist:** <value>`. Per the core contract, "
                        f"`**Checklist:**` is the single exception to the "
                        f"single-line field rule: the label must stand "
                        f"alone with `- [ ] ...` bullets on the lines "
                        f"below. Reference: {ref}."
                    )
                elif not _checklist_label_present(block_text):
                    issues.append(
                        f"`### {nid}: {label}` is missing the `**Checklist:**` "
                        f"label line. Even when items exist below, the label "
                        f"is required so executors can locate the checklist "
                        f"unambiguously. Reference: {ref}."
                    )
                elif not _checklist_bullets_after_label(block_text):
                    issues.append(
                        f"`### {nid}: {label}` has a `**Checklist:**` label "
                        f"but no `- [ ] ...` bullets beneath it. Add at least "
                        f"one concrete item directly under the label. "
                        f"Reference: {ref}."
                    )
            elif not _field_present(block_text, field):
                issues.append(
                    f"`### {nid}: {label}` is missing required field `**{field}:**`. "
                    f"Reference: {ref}."
                )

        if shape == "checkpoint":
            # Fence-aware + `[ \t]*` (not `\s*`) for consistency with
            # `_field_present`: a `**Mode:** foo` quoted inside a fenced
            # example is not the real checkpoint mode, and the value
            # must live on the same line as the label.
            mode_match = re.search(
                r"^\*\*Mode:\*\*[ \t]*`?([A-Za-z_][A-Za-z0-9_-]*)`?[ \t]*$",
                _non_code_block_text(block_text),
                flags=re.MULTILINE,
            )
            if mode_match:
                mode_value = mode_match.group(1)
                if mode_value not in ALLOWED_CHECKPOINT_MODES:
                    issues.append(
                        f"`### {nid}: {label}` has unknown checkpoint `**Mode:**` `{mode_value}`. "
                        f"Expected one of: {sorted(ALLOWED_CHECKPOINT_MODES)}. "
                        f"Reference: {REF_CHECKPOINTS}."
                    )

    if len(handoff_blocks) > 1:
        names = ", ".join(f"`{n}`" for n in handoff_blocks)
        issues.append(
            f"Multiple handoff content blocks found: {names}. "
            f"Expected exactly one `h` block per plan. "
            f"Reference: {REF_HANDOFF_SHAPE}."
        )

    return issues


def recommended_content_warnings(
    blocks: list[tuple[str, str, str]], mode: str | None
) -> list[str]:
    """Non-blocking warnings for recommended shape fields."""
    if mode == "budget-limited":
        return []

    warnings: list[str] = []
    for nid, label, block_text in blocks:
        shape = classify_node_id(nid)
        if shape == "unknown":
            # Already reported as an error; do not double-warn on fields.
            continue
        for field in SHAPE_RECOMMENDED_FIELDS[shape]:
            if not _field_present(block_text, field):
                warnings.append(
                    f"`### {nid}: {label}` is missing recommended field `**{field}:**`. "
                    f"Reference: {shape_reference(shape)}."
                )
    return warnings


def validate_last_block_is_handoff(
    blocks: list[tuple[str, str, str]],
) -> list[str]:
    """Require the last content block under `## Stages` to be the `h` handoff."""
    if not blocks:
        return []
    last_id, last_label, _ = blocks[-1]
    if last_id != "h":
        return [
            f"Last content block under `## Stages` is not the handoff node. "
            f"Found: `### {last_id}: {last_label}`. "
            f"Expected: `### h: <label>` as the terminal sign-off block. "
            f"Reference: {REF_HANDOFF_SHAPE}."
        ]
    return []


def extract_dependency_graph_section(text: str) -> str | None:
    """Return the body of `## Dependency Graph`. See `_extract_section`.

    Previously used a plain regex that was NOT fence-aware; a composer
    who quoted `## Dependency Graph` or `## ...` inside a fenced block
    anywhere above the real section could have had the wrong slice
    returned. The shared extractor closes that gap without changing the
    happy-path slice.
    """
    return _extract_section(text, "Dependency Graph")


def parse_dag(
    dg_section: str,
) -> tuple[dict[str, str | None], list[tuple[str, str]]]:
    """Parse nodes and edges from the Dependency Graph section.

    Supports two surface forms:
    - Mermaid flowchart lines with optional labels (`s1[Schema Setup]`).
    - Plain arrow prose (`a -> b`, `a --> b`, or simple chains `a --> b --> c`).

    Returns:
        nodes: ordered dict mapping node id -> optional label (None if no label
            declaration was seen). First-seen order is preserved to give stable
            error messages.
        edges: list of (from, to) pairs in the order they were read.
    """
    nodes: dict[str, str | None] = {}
    edges: list[tuple[str, str]] = []

    def record_node(nid: str, label: str | None) -> None:
        if nid not in nodes:
            nodes[nid] = label
        elif label is not None and nodes[nid] is None:
            nodes[nid] = label

    label_pattern = re.compile(r"(\w[\w-]*)\s*[\[\(\{]([^\]\)\}]+)[\]\)\}]")
    # Alternation order matters: longer arrow forms (`-->`, `->`) MUST precede
    # the identifier pattern, otherwise the hyphen in `->` is consumed as part
    # of a word token. The identifier pattern itself permits internal dashes
    # (e.g. `dual-read`) but disallows trailing hyphens.
    token_pattern = re.compile(r"(-->|->|\w+(?:-\w+)*)")

    lines = dg_section.splitlines()
    # Fence-priority rule: ONLY a fenced block whose info string begins
    # with `mermaid` is treated as the authoritative DAG surface. Other
    # fenced blocks (e.g. ```text``` illustrations, ``` ``` shell
    # snippets, or unlabelled fences) are still skipped for their body
    # — a bare `s1 -> s2` inside ```text``` should not emit edges — but
    # their presence no longer suppresses plain-arrow prose outside
    # every fence.
    #
    # The single-pass loop below tracks three things line by line:
    # - `fence_stack`  : CommonMark-faithful fence state (via
    #   `_update_fence_stack`).
    # - `in_mermaid`   : True only while inside a mermaid-labelled
    #   fence; bodies of other fences go unparsed.
    # - `mermaid_seen` : True once any mermaid fence has been opened
    #   anywhere in the section. Once set, prose lines *outside* every
    #   fence are ignored for the remainder of the section — the
    #   mermaid body is the single source of truth.
    #
    # Two fenced mermaid blocks in one section are both parsed
    # (independently); prose between them is dropped. Two fenced
    # *non*-mermaid blocks keep plain-arrow prose legal. A section
    # with no mermaid fence at all falls back to plain-arrow prose
    # parsing everywhere outside fences.
    #
    # Fence info string detection mirrors CommonMark §4.5: the info
    # string is everything on the opener line after the fence token,
    # whitespace-trimmed; the language tag is its first whitespace-
    # delimited word, case-insensitive. `_update_fence_stack` already
    # rejects malformed openers (backtick openers with a backtick in
    # the info string, closers with trailing prose, etc.), so we only
    # inspect openers it accepted.
    mermaid_seen = False
    # Pre-pass: know whether the section contains at least one mermaid
    # fence before we start emitting edges. Without this, prose that
    # appears *before* a later-in-section mermaid fence would leak
    # phantom edges. The pre-pass uses the same fence tracker so its
    # notion of "mermaid fence" matches the parse pass below exactly.
    _detect_stack: list[str] = []
    for line in lines:
        _prev_depth = len(_detect_stack)
        changed = _update_fence_stack(line, _detect_stack)
        if changed and len(_detect_stack) > _prev_depth:
            match = _FENCE_TOKEN_PATTERN.match(line)
            if match is not None:
                info = line[match.end():].strip()
                lang = info.split()[0].lower() if info else ""
                if lang == "mermaid":
                    mermaid_seen = True
                    break

    fence_stack: list[str] = []
    in_mermaid = False
    for raw_line in lines:
        prev_depth = len(fence_stack)
        changed = _update_fence_stack(raw_line, fence_stack)
        new_depth = len(fence_stack)
        if changed:
            if new_depth > prev_depth:
                match = _FENCE_TOKEN_PATTERN.match(raw_line)
                info = raw_line[match.end():].strip() if match else ""
                lang = info.split()[0].lower() if info else ""
                in_mermaid = lang == "mermaid"
            else:
                in_mermaid = False
            continue
        if fence_stack and not in_mermaid:
            continue
        if not fence_stack and mermaid_seen:
            continue
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        # Skip mermaid directives (flowchart, graph, subgraph, classDef, style, etc.).
        # Only node declarations and edges matter for structural validation.
        if re.match(
            r"^(flowchart|graph|subgraph|end|classDef|class|style|click|%%)\b",
            stripped,
            flags=re.IGNORECASE,
        ):
            continue

        def _label_sub(m: re.Match[str]) -> str:
            record_node(m.group(1), m.group(2).strip())
            return m.group(1)

        clean = label_pattern.sub(_label_sub, stripped)

        # Drop mermaid edge annotations. Two shapes:
        # - `-->|text|`  : pipe-delimited label on a directed edge
        # - `-- text -->`: inline-labelled directed edge (mermaid's
        #   verbose form; the label sits between `--` and `-->` and
        #   may be space- or non-space-separated). Dropping the label
        #   normalises the edge down to ` --> ` so downstream
        #   tokenisation does not emit a phantom `text` node.
        # The negative lookahead `(?!>)` after the opening `--`
        # prevents matching `--` that is actually the tail of an
        # already-present `-->` (e.g. in `A --> B --> C`).
        clean = re.sub(r"(?:-->|->)\|[^|]*\|", " --> ", clean)
        clean = re.sub(r"--(?!>)\s*.+?\s*-->", " --> ", clean)

        tokens = token_pattern.findall(clean)
        i = 0
        while i < len(tokens) - 2:
            if (
                tokens[i + 1] in ("-->", "->")
                and tokens[i] not in ("-->", "->")
                and tokens[i + 2] not in ("-->", "->")
            ):
                src, dst = tokens[i], tokens[i + 2]
                record_node(src, None)
                record_node(dst, None)
                edges.append((src, dst))
                i += 2
            else:
                i += 1

    return nodes, edges


def _build_adjacency(
    node_ids: list[str], edges: list[tuple[str, str]]
) -> dict[str, list[str]]:
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for src, dst in edges:
        adjacency.setdefault(src, []).append(dst)
        adjacency.setdefault(dst, adjacency.get(dst, []))
    return adjacency


def find_cycle(adjacency: dict[str, list[str]]) -> list[str] | None:
    """Return a cycle (list of node ids starting and ending on the same node)
    if one exists, otherwise None.

    Three-color DFS: nodes currently on the recursion stack are GRAY; hitting
    another GRAY node means we closed a back-edge into an ancestor.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {nid: WHITE for nid in adjacency}
    parent: dict[str, str | None] = {nid: None for nid in adjacency}
    cycle_start: str | None = None
    cycle_end: str | None = None

    def dfs(u: str) -> bool:
        nonlocal cycle_start, cycle_end
        color[u] = GRAY
        for v in adjacency.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                cycle_start = v
                cycle_end = u
                return True
            if color[v] == WHITE:
                parent[v] = u
                if dfs(v):
                    return True
        color[u] = BLACK
        return False

    for start in adjacency:
        if color[start] == WHITE and dfs(start):
            break

    if cycle_start is None:
        return None

    path: list[str] = [cycle_end]  # type: ignore[list-item]
    current = cycle_end
    while current != cycle_start and parent.get(current) is not None:
        current = parent[current]  # type: ignore[assignment]
        path.append(current)
    path.reverse()
    path.append(cycle_start)
    return path


def _reverse_reachable(target: str, adjacency: dict[str, list[str]]) -> set[str]:
    reverse: dict[str, list[str]] = {nid: [] for nid in adjacency}
    for u, vs in adjacency.items():
        for v in vs:
            reverse.setdefault(v, []).append(u)
            reverse.setdefault(u, reverse.get(u, []))

    visited: set[str] = {target}
    stack = [target]
    while stack:
        u = stack.pop()
        for v in reverse.get(u, []):
            if v not in visited:
                visited.add(v)
                stack.append(v)
    return visited


def validate_dependency_graph(text: str) -> tuple[list[str], list[str]]:
    """Run structural checks on the Dependency Graph.

    Enforces:
    - graph is acyclic,
    - exactly one sink node whose id is `h`,
    - every other node reaches `h`,
    - every non-`h` node id matches a known prefix (`s*` or `ck*`). Unknown
      prefixes are reported here because the DAG layer is where the id
      convention lives; content-block and ledger validators cross-reference
      the same error via alignment mismatches.

    Returns:
        issues: error messages (empty if the graph is structurally valid).
        node_ids: ids parsed from the DAG (empty if the section is missing or
            the DAG has no recognizable nodes/edges).
    """
    issues: list[str] = []
    section = extract_dependency_graph_section(text)
    if section is None:
        return issues, []

    nodes, edges = parse_dag(section)
    if not nodes:
        issues.append(
            f"`## Dependency Graph` contains no recognizable nodes or edges. "
            f"Expected at least one arrow expression (mermaid `-->` or prose `->`) "
            f"ending in an `h` handoff sink. "
            f"Reference: {REF_DEPENDENCY_GRAPH}."
        )
        return issues, []

    node_ids = list(nodes.keys())

    # Unknown id prefixes are an id-convention violation. Report them here so
    # downstream alignment errors do not stack on the same root cause.
    unknown_ids = [nid for nid in node_ids if classify_node_id(nid) == "unknown"]
    if unknown_ids:
        items = ", ".join(f"`{n}`" for n in unknown_ids)
        issues.append(
            f"DAG nodes with unknown id prefixes: {items}. "
            f"Expected ids to match `s<N>` (stage), `ck<N>` (checkpoint), or `h` (handoff). "
            f"Reference: {REF_DEPENDENCY_GRAPH} and {REF_UNKNOWN_PREFIX}."
        )

    adjacency = _build_adjacency(node_ids, edges)

    cycle = find_cycle(adjacency)
    if cycle is not None:
        pretty = " → ".join(cycle)
        issues.append(
            f"`## Dependency Graph` contains a cycle: {pretty}. "
            f"Dependency graphs must be acyclic. "
            f"Reference: {REF_DEPENDENCY_GRAPH}."
        )
        # A cyclic graph has no meaningful sinks; skip the rest but still
        # return the ids so alignment can surface downstream mismatches.
        return issues, node_ids

    sinks = [nid for nid in node_ids if not adjacency.get(nid)]
    handoff_sinks = [nid for nid in sinks if nid == "h"]

    if not sinks:
        issues.append(
            f"`## Dependency Graph` has no sink node (every node has outgoing edges). "
            f"Expected exactly one sink with id `h`. "
            f"Reference: {REF_DEPENDENCY_GRAPH} and {REF_HANDOFF_SHAPE}."
        )
    elif len(sinks) > 1:
        sink_repr = ", ".join(f"`{nid}`" for nid in sinks)
        issues.append(
            f"`## Dependency Graph` has multiple sinks: {sink_repr}. "
            f"Expected exactly one sink with id `h`; add edges so the other "
            f"terminal nodes flow into `h`. "
            f"Reference: {REF_DEPENDENCY_GRAPH} and {REF_HANDOFF_SHAPE}."
        )
    elif not handoff_sinks:
        only_sink = sinks[0]
        label = nodes.get(only_sink)
        label_part = f" (label: `{label}`)" if label else ""
        issues.append(
            f"`## Dependency Graph` single sink is `{only_sink}`{label_part}, "
            f"but its id is not `h`. "
            f"Expected the terminal node to be the mandatory `h` handoff. "
            f"Reference: {REF_HANDOFF_SHAPE} and {REF_DEPENDENCY_GRAPH}."
        )
    else:
        target = handoff_sinks[0]
        reachable = _reverse_reachable(target, adjacency)
        unreachable = [nid for nid in node_ids if nid not in reachable]
        if unreachable:
            items = ", ".join(f"`{nid}`" for nid in unreachable)
            issues.append(
                f"`## Dependency Graph` has nodes that do not reach the `h` "
                f"handoff sink: {items}. Every node must flow into `h`. "
                f"Reference: {REF_DEPENDENCY_GRAPH}."
            )

    return issues, node_ids


def extract_stage_claims_section(text: str) -> str | None:
    """Return the body of `## Stage Claims`. See `_extract_section`.

    Fence-aware for the same reason as the other section extractors;
    see `_extract_section` for the scan strategy.
    """
    return _extract_section(text, "Stage Claims")


def extract_stage_claims_entries(
    section: str,
) -> list[tuple[str, str, str | None, str | None, str]]:
    """Return (raw_line, marker, id, label, body_after_bracket) for each entry.

    Entries inside blockquotes (the template key) are skipped. For each `- [ ]`
    bullet we try to parse `<id>: <label>` off the body; if parsing fails both
    id and label are None so callers can surface a "malformed" error while
    still keeping the marker/body text for the message.

    Fence-aware: a composer who illustrates a ledger snippet inside a
    fenced code block (for example to show the expected shape before
    seeding real entries) previously had those sample bullets picked
    up as live ledger entries, which cascaded into "duplicate id" /
    "last entry is not handoff" / "pre-filled marker" noise. Walking
    the section through `_update_fence_stack` tracks the fence state
    so only bullets outside fences contribute to the ledger.
    """
    entries: list[tuple[str, str, str | None, str | None, str]] = []
    fence_stack: list[str] = []
    for raw_line in section.splitlines():
        if _update_fence_stack(raw_line, fence_stack):
            continue
        if fence_stack:
            continue
        stripped = raw_line.lstrip()
        if stripped.startswith(">"):
            continue
        line_match = LEDGER_LINE_PATTERN.match(stripped)
        if not line_match:
            continue
        marker = line_match.group(1)
        body = line_match.group(2)
        body_match = LEDGER_BODY_PATTERN.match(body)
        if body_match:
            nid = body_match.group(1)
            label = body_match.group(2)
        else:
            nid = None
            label = None
        entries.append((raw_line.rstrip(), marker, nid, label, body))
    return entries


def validate_stage_claims(text: str) -> tuple[list[str], set[str] | None]:
    """Verify the `## Stage Claims` ledger is seeded correctly.

    Rules enforced:
    - ledger is non-empty,
    - every entry is shaped `- [ ] <id>: <label>`,
    - composer seeds only `[ ]` (runtime markers `[~]` / `[x]` are rejected),
    - the last ledger entry references `h`,
    - entry ids are unique (duplicates would break runtime coordination).

    Returns:
        issues: error messages.
        claim_ids: set of ledger entry ids when the ledger is non-empty, or
            None when the section is missing (so alignment validation can
            skip gracefully — the missing-heading error upstream is enough).
    """
    issues: list[str] = []
    section = extract_stage_claims_section(text)
    if section is None:
        return issues, None

    entries = extract_stage_claims_entries(section)
    if not entries:
        issues.append(
            f"`## Stage Claims` has no ledger entries. "
            f"Seed one `- [ ] <id>: <label>` per DAG node, ending with `- [ ] h: Handoff`. "
            f"Reference: {REF_STAGE_CLAIMS}."
        )
        return issues, set()

    malformed_entries = [
        (raw, body) for (raw, _m, nid, _l, body) in entries if nid is None
    ]
    if malformed_entries:
        samples = "; ".join(
            f"`{raw.strip()}` (body: `{body}`)" for (raw, body) in malformed_entries
        )
        issues.append(
            f"`## Stage Claims` has malformed entries: {samples}. "
            f"Expected `- [ ] <id>: <label>` where `<id>` matches `s<N>` / `ck<N>` / `h`. "
            f"Reference: {REF_STAGE_CLAIMS}."
        )

    non_empty = [
        (raw, marker, nid, label, body)
        for (raw, marker, nid, label, body) in entries
        if marker.strip() != ""
    ]
    if non_empty:
        offenders = "; ".join(
            f"`[{marker}] {body}`" for (_r, marker, _nid, _l, body) in non_empty
        )
        issues.append(
            f"`## Stage Claims` contains pre-filled markers: {offenders}. "
            f"Composer must seed only `- [ ]`; executors flip markers to `[~]` / `[x]` "
            f"at runtime. "
            f"Reference: {REF_STAGE_CLAIMS}."
        )

    # Id-level checks only make sense on well-formed entries.
    well_formed = [nid for (_r, _m, nid, _l, _b) in entries if nid is not None]
    if well_formed:
        seen: dict[str, int] = {}
        for nid in well_formed:
            seen[nid] = seen.get(nid, 0) + 1
        duplicates = sorted(nid for nid, count in seen.items() if count > 1)
        if duplicates:
            items = ", ".join(f"`{n}`" for n in duplicates)
            issues.append(
                f"`## Stage Claims` has duplicate entry ids: {items}. "
                f"Every DAG node must have exactly one ledger entry. "
                f"Reference: {REF_STAGE_CLAIMS}."
            )

        unknown = [nid for nid in set(well_formed) if classify_node_id(nid) == "unknown"]
        if unknown:
            items = ", ".join(f"`{n}`" for n in sorted(unknown))
            issues.append(
                f"`## Stage Claims` entries with unknown id prefixes: {items}. "
                f"Expected ids to match `s<N>` / `ck<N>` / `h`. "
                f"Reference: {REF_UNKNOWN_PREFIX}."
            )

    last_raw, _marker, last_id, last_label, last_body = entries[-1]
    if last_id != "h":
        issues.append(
            f"Last `## Stage Claims` entry is not the `h` handoff. "
            f"Found: `{last_raw.strip()}`. "
            f"Expected: `- [ ] h: <label>` as the final ledger entry. "
            f"Reference: {REF_STAGE_CLAIMS} and {REF_HANDOFF_SHAPE}."
        )

    return issues, set(well_formed)


def validate_id_alignment(
    dag_ids: set[str],
    block_ids: set[str],
    claim_ids: set[str],
) -> list[str]:
    """Ensure DAG ↔ Stages ↔ Stage Claims id sets are identical.

    The three sets are expected to be byte-for-byte the same set of ids.
    Mismatches are surfaced as four targeted errors (one per direction) so
    composers can fix the specific missing/extra entries instead of guessing.
    """
    issues: list[str] = []

    missing_blocks = sorted(dag_ids - block_ids)
    if missing_blocks:
        items = ", ".join(f"`{n}`" for n in missing_blocks)
        issues.append(
            f"DAG nodes without a matching `## Stages` content block: {items}. "
            f"Every DAG node id must have a `### <id>: <label>` block. "
            f"Reference: {REF_NODE_TEMPLATES}."
        )

    extra_blocks = sorted(block_ids - dag_ids)
    if extra_blocks:
        items = ", ".join(f"`{n}`" for n in extra_blocks)
        issues.append(
            f"`## Stages` content blocks with ids not in `## Dependency Graph`: {items}. "
            f"Every content block id must appear as a DAG node. "
            f"Reference: {REF_NODE_TEMPLATES} and {REF_DEPENDENCY_GRAPH}."
        )

    missing_claim = sorted(dag_ids - claim_ids)
    if missing_claim:
        items = ", ".join(f"`{n}`" for n in missing_claim)
        issues.append(
            f"DAG nodes without a matching `## Stage Claims` entry: {items}. "
            f"Seed one `- [ ] <id>: <label>` per DAG node. "
            f"Reference: {REF_STAGE_CLAIMS}."
        )

    extra_claim = sorted(claim_ids - dag_ids)
    if extra_claim:
        items = ", ".join(f"`{n}`" for n in extra_claim)
        issues.append(
            f"`## Stage Claims` entries with ids not in `## Dependency Graph`: {items}. "
            f"Every entry id must match a DAG node. "
            f"Reference: {REF_STAGE_CLAIMS} and {REF_DEPENDENCY_GRAPH}."
        )

    return issues


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    if len(args) != 1:
        print("Usage: validate-plan.py path/to/plan.md", file=sys.stderr)
        return 2

    path = Path(args[0])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    issues, warnings = validate(text, path)

    if issues:
        print("PLAN VALIDATION FAILED")
        for issue in issues:
            print(f"- {issue}")
        if warnings:
            print("")
            print("Warnings (non-blocking):")
            for warning in warnings:
                print(f"- {warning}")
        return 1

    if warnings:
        print("PLAN VALIDATION OK WITH WARNINGS")
        for warning in warnings:
            print(f"- {warning}")
        return 0

    print("PLAN VALIDATION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
