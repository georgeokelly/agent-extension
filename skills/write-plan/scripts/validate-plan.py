#!/usr/bin/env python3
"""Lightweight validator for executable-plan markdown files."""

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
    "Flow Graph",
    "Stages",
    "Verification",
    "Stop Conditions",
    "Decision Log",
    "Handoff",
]

STAGE_REQUIRED_FIELDS = [
    "Purpose",
]

STAGE_RECOMMENDED_FIELDS = [
    "Files",
    "Exit Signal",
]

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

CONTRACT_PROFILE_EXTRA_HEADINGS = {
    "migration": [
        "Rollout / Rollback",
        "Compatibility / Migration",
        "Risks & Mitigations",
    ],
}

GLOBAL_PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
]

LINE_LEVEL_PLACEHOLDER_PATTERNS = [
    r"^\s*[-*]\s*implement later\s*$",
    r"^\s*[-*]\s*fill in later\s*$",
    r"^\s*[-*]\s*write tests\s*$",
    r"^\s*[-*]\s*add tests\s*$",
    r"^\s*[-*]\s*handle edge cases\s*$",
]

# Plan file basename must look like `plan.<profile>.<task-type>.md`.
# `<profile>` is constrained to a single lowercase word so the dot-separated
# structure stays unambiguous (task-type may contain hyphens).
PLAN_FILENAME_PATTERN = re.compile(r"^plan\.[a-z]+\.[a-z0-9-]+\.md$")


def has_metadata(text: str, field: str) -> bool:
    pattern = rf"^\*\*{re.escape(field)}:\*\*\s*.+$"
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def has_heading(text: str, heading: str) -> bool:
    pattern = rf"^##+\s+{re.escape(heading)}\s*$"
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def extract_metadata_value(text: str, field: str) -> str | None:
    match = re.search(
        rf"^\*\*{re.escape(field)}:\*\*\s*`?(.+?)`?\s*$",
        text,
        flags=re.MULTILINE,
    )
    if match:
        return match.group(1).strip()
    return None


def iter_non_code_lines(text: str) -> list[str]:
    lines = text.splitlines()
    in_fence = False
    result: list[str] = []

    for line in lines:
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(line)

    return result


def find_soft_placeholders(text: str) -> list[str]:
    """Return soft placeholders (TODO / TBD) that agent should clarify with user.

    Soft placeholders are explicit markers used at plan-writing time to flag
    information gaps the agent could not resolve alone. They surface as
    warnings so a downstream agent can confirm the detail with the user
    before finalization, rather than blocking plan validation outright.
    """
    findings: list[str] = []
    lines = iter_non_code_lines(text)

    for line in lines:
        for pattern in GLOBAL_PLACEHOLDER_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(f"`{pattern}` on line: {line.strip()}")

    # Preserve order while deduplicating.
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

    # Preserve order while deduplicating.
    return list(dict.fromkeys(findings))


def recommended_stage_warnings(stages_section: str, mode: str | None) -> list[str]:
    warnings: list[str] = []
    blocks = split_stage_blocks(stages_section)

    if mode == "budget-limited":
        return warnings

    for index, block in enumerate(blocks, start=1):
        for field in STAGE_RECOMMENDED_FIELDS:
            if not re.search(rf"^\*\*{re.escape(field)}:\*\*\s*.+$", block, flags=re.MULTILINE):
                warnings.append(f"Stage {index} is missing recommended field `**{field}:**`.")

    return warnings


def validate_filename(path: Path) -> list[str]:
    if PLAN_FILENAME_PATTERN.match(path.name):
        return []
    return [
        (
            f"Filename `{path.name}` does not match required pattern "
            f"`plan.<contract-profile>.<task-type>.md` "
            f"(profile: single lowercase word; task-type: lowercase kebab-case slug)."
        )
    ]


def validate(text: str, path: Path | None = None) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []

    if path is not None:
        issues.extend(validate_filename(path))

    for field in REQUIRED_METADATA:
        if not has_metadata(text, field):
            issues.append(f"Missing metadata line: `**{field}:**`.")

    for heading in REQUIRED_HEADINGS:
        if not has_heading(text, heading):
            issues.append(f"Missing heading: `## {heading}`.")

    contract_profile = extract_metadata_value(text, "Contract Profile")
    mode = extract_metadata_value(text, "Mode")

    if contract_profile is None:
        issues.append("Could not extract `**Contract Profile:**`.")
    elif contract_profile not in ALLOWED_CONTRACT_PROFILES:
        issues.append(
            f"Unknown contract profile `{contract_profile}`. Allowed values: {sorted(ALLOWED_CONTRACT_PROFILES)}."
        )

    if mode is None:
        issues.append("Could not extract `**Mode:**`.")
    elif mode not in ALLOWED_MODES:
        issues.append(
            f"Unknown mode `{mode}`. Allowed values: {sorted(ALLOWED_MODES)}."
        )

    if contract_profile in CONTRACT_PROFILE_EXTRA_HEADINGS:
        for heading in CONTRACT_PROFILE_EXTRA_HEADINGS[contract_profile]:
            if not has_heading(text, heading):
                issues.append(
                    f"Contract profile `{contract_profile}` requires `## {heading}`."
                )

    for finding in find_hard_placeholders(text):
        issues.append(f"Hard placeholder (lazy list item): {finding}.")

    for finding in find_soft_placeholders(text):
        warnings.append(
            f"Soft placeholder {finding} — agent should clarify with user before finalization."
        )

    stages_section = extract_stages_section(text)
    if stages_section is None:
        issues.append("Could not extract `## Stages` section.")
    else:
        issues.extend(validate_stage_blocks(stages_section))
        warnings.extend(recommended_stage_warnings(stages_section, mode))

    return issues, warnings


def extract_stages_section(text: str) -> str | None:
    match = re.search(
        r"^##\s+Stages\s*$([\s\S]*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE,
    )
    if match:
        return match.group(1)
    return None


def split_stage_blocks(stages_section: str) -> list[str]:
    matches = list(re.finditer(r"^###\s+Stage\s+\d+:\s+.+$", stages_section, flags=re.MULTILINE))
    if not matches:
        return []

    blocks: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(stages_section)
        blocks.append(stages_section[start:end])
    return blocks


def validate_stage_blocks(stages_section: str) -> list[str]:
    issues: list[str] = []
    blocks = split_stage_blocks(stages_section)

    if not blocks:
        issues.append("No `### Stage N: ...` blocks found inside `## Stages`.")
        return issues

    for index, block in enumerate(blocks, start=1):
        for field in STAGE_REQUIRED_FIELDS:
            if not re.search(rf"^\*\*{re.escape(field)}:\*\*\s*.+$", block, flags=re.MULTILINE):
                issues.append(f"Stage {index} is missing `**{field}:**`.")
        if not re.search(r"^\s*[-*+]\s+\[[ xX]\]\s+.+$", block, flags=re.MULTILINE):
            issues.append(f"Stage {index} is missing checklist items.")
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
