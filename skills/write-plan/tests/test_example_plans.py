"""Regression: every full plan embedded in `examples.md` must pass the validator.

Guards against doc drift — if the contract moves but the hand-written examples
are not refreshed, CI fails here instead of letting the skill ship with
demonstrably-invalid positive examples.

Extraction rules:
- Only 4-backtick ```` ```markdown ```` fences are considered plan bodies;
  3-backtick fences are reserved for partial snippets in examples.md.
- A fence that lacks both `**Contract Profile:**` and `**Task Type:**` is
  skipped (likely the debug-log illustration, which is not a plan).
- Every remaining block is written to a temp path whose basename follows the
  canonical `plan.<profile>.<task-type>.md` pattern so the validator's
  filename check does not spuriously fire.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import unittest
from pathlib import Path


def _load_validator():
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "validate-plan.py"
    )
    spec = importlib.util.spec_from_file_location("validate_plan", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validator module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator()

EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples.md"

# Non-greedy match between the opening 4-backtick fence and its mate. The
# anchor `^` + `$` in MULTILINE ensure we only pick up fence lines, not
# 4-backtick sequences embedded in prose.
FENCE_PATTERN = re.compile(
    r"^````markdown\s*$\n(.*?)\n^````\s*$",
    flags=re.MULTILINE | re.DOTALL,
)

PROFILE_PATTERN = re.compile(
    r"^\*\*Contract Profile:\*\*\s*`([^`]+)`", flags=re.MULTILINE
)
TASK_PATTERN = re.compile(
    r"^\*\*Task Type:\*\*\s*`([^`]+)`", flags=re.MULTILINE
)


def extract_plan_blocks() -> list[tuple[str, str]]:
    """Return `[(canonical_filename, body)]` for every full plan in examples.md."""
    text = EXAMPLES_PATH.read_text(encoding="utf-8")
    results: list[tuple[str, str]] = []
    for match in FENCE_PATTERN.finditer(text):
        body = match.group(1)
        profile_match = PROFILE_PATTERN.search(body)
        task_match = TASK_PATTERN.search(body)
        if not (profile_match and task_match):
            # Snippet or debug-log example — skip (not a full plan).
            continue
        fname = f"plan.{profile_match.group(1)}.{task_match.group(1)}.md"
        results.append((fname, body + "\n"))
    return results


ALLOWED_CONTRACT_PROFILES = {
    "delivery",
    "refactor",
    "migration",
    "exploration",
}


class ExamplePlanTests(unittest.TestCase):
    def test_examples_cover_every_contract_profile(self) -> None:
        # The four contract profiles (`delivery`, `refactor`,
        # `migration`, `exploration`) are the backbone of the skill —
        # the skeleton differs per profile, so we want at least one
        # worked example of each. A laxer `>= 1` check would have
        # silently accepted an examples.md that dropped three profiles
        # while the documentation continued to promise coverage. This
        # assertion fails loudly if a refactor accidentally removes a
        # full-plan block.
        blocks = extract_plan_blocks()
        self.assertGreaterEqual(
            len(blocks),
            4,
            f"examples.md must contain at least one full plan per "
            f"contract profile (4 total); found {len(blocks)}: "
            f"{[fname for fname, _ in blocks]}.",
        )
        profiles_seen: set[str] = set()
        for fname, _body in blocks:
            segments = fname.split(".")
            self.assertGreaterEqual(
                len(segments), 4, f"Unexpected filename shape: {fname}"
            )
            profiles_seen.add(segments[1])
        missing = ALLOWED_CONTRACT_PROFILES - profiles_seen
        self.assertEqual(
            missing,
            set(),
            f"examples.md is missing full plans for contract profile(s) "
            f"{sorted(missing)}; each of {sorted(ALLOWED_CONTRACT_PROFILES)} "
            f"must appear.",
        )

    def test_every_example_plan_validates(self) -> None:
        blocks = extract_plan_blocks()
        failures: list[str] = []
        for fname, body in blocks:
            with self.subTest(plan=fname):
                issues, _warnings = VALIDATOR.validate(body, pathlib.Path(fname))
                if issues:
                    failures.append(f"{fname}: {issues}")
                    self.fail(f"{fname} failed validation: {issues}")
        # Belt-and-suspenders: if subTest swallows intermittent failures on
        # some runners, the aggregate list re-surfaces them.
        self.assertEqual(
            failures, [], f"Example plans failed validation: {failures}"
        )


if __name__ == "__main__":
    unittest.main()
