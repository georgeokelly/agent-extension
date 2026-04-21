"""Smoke test: SKILL.md YAML frontmatter stays well-formed and cross-tool.

The skill frontmatter is parsed by Cursor, Claude Code, and Codex — all via the
agentskills.io specification. A regression where `name:` is accidentally
written as `## name:` (a YAML comment disguised as a Markdown heading) ships
the skill into all three tools without a discoverable `name`, silently
breaking routing. This file guards the fixture without adding a PyYAML
dependency — the frontmatter shape is deliberately narrow so a regex-driven
smoke test covers the regressions that actually matter.

Checks:
- Frontmatter is present and properly delimited by `---` fences.
- The required top-level keys (`name`, `description`) exist with non-empty
  values.
- `name` equals the canonical `write-executable-plan`; changing the skill
  name requires updating this test *and* the downstream tooling that
  dispatches on it.
- No stale `## name:` (heading-as-comment) lines slip into the frontmatter
  body, which is the concrete regression fixed earlier in this skill.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"

_FRONTMATTER_FENCE = re.compile(r"^---\s*$", flags=re.MULTILINE)


def _extract_frontmatter(text: str) -> str:
    """Return the YAML frontmatter body (between the two `---` fences)."""
    fences = [m.start() for m in _FRONTMATTER_FENCE.finditer(text)]
    if len(fences) < 2:
        raise AssertionError(
            f"SKILL.md at {SKILL_PATH} is missing a `---`-delimited "
            f"frontmatter block (found {len(fences)} fence lines; need >= 2)."
        )
    # Body sits between the first fence's line and the second fence's line.
    first_fence_end = text.index("\n", fences[0]) + 1
    second_fence_start = fences[1]
    return text[first_fence_end:second_fence_start]


_TOP_LEVEL_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_FOLD_INDICATORS = frozenset({"", ">-", ">", "|-", "|", ">+", "|+"})


def _top_level_keys(body: str) -> dict[str, str]:
    """Collect `key: value` pairs at the top level only.

    We intentionally do not try to parse full YAML (nested mappings, list
    literals, etc.). The frontmatter shape is small and flat; a regex-based
    scan is enough for the smoke-test invariants without a PyYAML dep.
    Lines indented with spaces belong to the previous key's body (e.g.
    `metadata:`'s nested pairs); they are skipped here.
    """
    keys: dict[str, str] = {}
    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$")
    for line in body.splitlines():
        if not line or line.startswith(" ") or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        keys[match.group(1)] = match.group(2)
    return keys


def _top_level_block_body(body: str, key: str) -> tuple[str, list[str]]:
    """Return ``(inline_value, continuation_lines)`` for a top-level ``key``.

    Scoped specifically to ONE key's body. The scan stops at the next
    sibling top-level key (``^foo:``), a ``#`` comment line at column 0,
    or EOF — so a sibling's indented children (e.g. ``metadata:``'s
    nested ``author: ...`` / ``version: ...`` pairs) can never masquerade
    as continuation lines for the queried key. This is what makes
    "description is non-empty" testable without a PyYAML dependency.

    - ``inline_value``: text on the ``key: ...`` line itself, stripped.
      Empty string, ``">-"``, ``">"``, ``"|-"``, etc. mean the value
      lives in the folded block below, not on this line.
    - ``continuation_lines``: stripped, non-empty indented lines that
      belong to this key.

    Raises AssertionError if ``key`` is not found at the top level.
    """
    key_line_re = re.compile(rf"^{re.escape(key)}:\s*(.*?)\s*$")
    inline: str | None = None
    cont: list[str] = []
    for line in body.splitlines():
        if inline is None:
            match = key_line_re.match(line)
            if match:
                inline = match.group(1)
            continue
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("\t"):
            cont.append(line.strip())
            continue
        if _TOP_LEVEL_KEY_PATTERN.match(line) or line.startswith("#"):
            break
        break
    if inline is None:
        raise AssertionError(
            f"Top-level key {key!r} not found in SKILL.md frontmatter body."
        )
    return inline, cont


class SkillFrontmatterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = SKILL_PATH.read_text(encoding="utf-8")
        self.body = _extract_frontmatter(self.text)
        self.keys = _top_level_keys(self.body)

    def test_frontmatter_has_required_name(self) -> None:
        self.assertIn(
            "name",
            self.keys,
            "SKILL.md frontmatter is missing the required `name` key. "
            "agentskills.io tools use it for dispatching — an absent "
            "`name` breaks skill routing across Cursor, Claude Code, "
            "and Codex simultaneously.",
        )
        # Pin the canonical value. If a future rename is intentional the
        # test must be updated in the same change as the renaming.
        self.assertEqual(
            self.keys["name"],
            "write-executable-plan",
            f"Unexpected `name` value {self.keys['name']!r}; the canonical "
            f"skill name is `write-executable-plan`.",
        )

    def test_frontmatter_has_non_empty_description(self) -> None:
        self.assertIn(
            "description",
            self.keys,
            "SKILL.md frontmatter is missing the required `description` key.",
        )
        # Scope the scan to `description`'s own folded block. A sibling
        # key's indented children (e.g. ``metadata:``'s ``author`` /
        # ``version``) used to make a loose "any indented line counts"
        # scan pass even when ``description: >-`` carried no body — that
        # was the regression CF-FM1 flagged. Using the scoped helper
        # makes this test actually discriminating: empty the folded
        # block and it fails even with ``metadata:`` still present.
        inline, cont = _top_level_block_body(self.body, "description")
        inline_has_value = inline not in _FOLD_INDICATORS
        has_folded_body = bool(cont)
        self.assertTrue(
            inline_has_value or has_folded_body,
            "SKILL.md `description` is empty. Either give it a same-line "
            "value (`description: ...`) or a folded body (`description: "
            ">-` followed by indented continuation lines).",
        )

    def test_no_stale_heading_style_name_comment(self) -> None:
        # Regression guard for the earlier mis-formatted `## name: ...`
        # shape. That line was a *Markdown heading* that YAML parses as
        # a comment (because `#` starts YAML comments too), which
        # silently broke tool dispatch while looking superficially
        # correct in plain-text diffs. ``re.MULTILINE`` is required so
        # the ``^`` anchor applies to every line of the frontmatter,
        # not only the body's first character — without it a stale
        # ``## name:`` on any line past the first would slip through.
        self.assertNotRegex(
            self.body,
            re.compile(r"^##\s*name\s*:", flags=re.MULTILINE),
            "SKILL.md frontmatter contains a stale `## name:` heading-as-"
            "comment line; it MUST be a plain `name:` key-value pair "
            "instead (YAML parses `##` as a comment, which silently "
            "drops the name across tools).",
        )


class FrontmatterHelperDiscriminationTests(unittest.TestCase):
    """Direct unit tests that prove the smoke checks would actually fail
    if the regressions they guard against ever came back.

    The production smoke tests above always run against a *real*
    SKILL.md; they pass if the fixture is healthy. These tests feed
    synthetic frontmatter bodies to the helpers to pin the
    discrimination the Round 5 fixes introduced (CF-FM1 / CF-FM2).
    """

    def test_description_helper_rejects_empty_folded_body_with_sibling_metadata(
        self,
    ) -> None:
        # Hand-crafted regression: description folded body is empty, but
        # ``metadata:`` still carries indented children. A loose "any
        # indented line counts" scan would be fooled; the scoped helper
        # must NOT.
        body = (
            "name: write-executable-plan\n"
            "description: >-\n"
            "when_to_use: >-\n"
            "  Use when you want a plan.\n"
            "metadata:\n"
            "  author: georgel\n"
            '  version: "0.1"\n'
        )
        inline, cont = _top_level_block_body(body, "description")
        self.assertIn(inline, _FOLD_INDICATORS)
        self.assertEqual(
            cont,
            [],
            "description body must be empty — metadata's children must "
            "NOT leak into description's continuation lines.",
        )

    def test_description_helper_collects_real_folded_body(self) -> None:
        body = (
            "name: write-executable-plan\n"
            "description: >-\n"
            "  Line one.\n"
            "  Line two.\n"
            "metadata:\n"
            "  author: georgel\n"
        )
        inline, cont = _top_level_block_body(body, "description")
        self.assertIn(inline, _FOLD_INDICATORS)
        self.assertEqual(cont, ["Line one.", "Line two."])

    def test_stale_name_heading_anywhere_in_body_is_caught(self) -> None:
        # Round 5 CF-FM2: without ``re.MULTILINE`` the ``^`` anchor
        # matches only the string's first character. A stale
        # ``## name:`` on any subsequent line would slip through — the
        # exact regression the test was supposed to guard.
        body = (
            "description: >-\n"
            "  Something.\n"
            "## name: write-executable-plan\n"
        )
        pattern = re.compile(r"^##\s*name\s*:", flags=re.MULTILINE)
        self.assertIsNotNone(
            pattern.search(body),
            "MULTILINE pattern must find `## name:` on a non-first line.",
        )
        # Prove the naive (non-MULTILINE) form would have missed it —
        # this is the discrimination CF-FM2 introduces.
        naive = re.compile(r"^##\s*name\s*:")
        self.assertIsNone(
            naive.search(body),
            "Naive pattern (no MULTILINE) unexpectedly matched — the "
            "discrimination premise of CF-FM2 no longer holds.",
        )


if __name__ == "__main__":
    unittest.main()
