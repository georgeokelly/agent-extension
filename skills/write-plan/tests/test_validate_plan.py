from __future__ import annotations

import importlib.util
import textwrap
import unittest
from pathlib import Path


def load_validator_module():
    script_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "validate-plan.py"
    )
    spec = importlib.util.spec_from_file_location("validate_plan", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validator module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


def valid_feature_plan() -> str:
    return textwrap.dedent(
        """\
        # Add Cached Search Suggestions

        **Goal:** Add cached suggestions.
        **Task Type:** `search-suggestions-cache`
        **Contract Profile:** `delivery`
        **Mode:** `credit-rich`
        **Primary Success Signal:** Suggestions are cached and still correct.

        ## Inputs / Context Sources
        - `src/search/SearchBox.tsx`

        ## Context Scope
        - Use only the listed search files.

        ## Flow Graph
        analysis -> implementation -> handoff

        ## Stages
        ### Stage 1: Add cache behavior
        **Purpose:** Introduce cached suggestion behavior.
        **Files:** `src/search/SearchBox.tsx`, `src/search/__tests__/SearchBox.test.tsx`
        **Exit Signal:** Cache behavior is ready for validation.
        **Checklist:**
        - [ ] Add cache-aware fetch behavior
        - [ ] Confirm the cache boundary is still valid

        ## Verification
        - Run the relevant tests for search suggestions.

        ## Stop Conditions
        - Stop if the available context does not show who owns invalidation.

        ## Decision Log
        - Decision: Keep cache ownership in the API layer
          Why: It is shared across multiple consumers.

        ## Handoff
        Start with the cache boundary decision, then implement the fetch path.
        """
    )


class ValidatePlanTests(unittest.TestCase):
    def test_valid_feature_plan_passes_without_errors(self) -> None:
        issues, warnings = VALIDATOR.validate(valid_feature_plan())
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    def test_migration_requires_risks_mitigations(self) -> None:
        plan = textwrap.dedent(
            """\
            # Migrate Reads

            **Goal:** Migrate reads safely.
            **Task Type:** `payment-read-migration`
            **Contract Profile:** `migration`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Cutover remains reversible.

            ## Inputs / Context Sources
            - `src/data/read_path.ts`

            ## Context Scope
            - Use only the listed migration files.

            ## Flow Graph
            dual-read -> cutover

            ## Stages
            ### Stage 1: Enter dual-read
            **Purpose:** Compare old and new reads.
            **Files:** `src/data/read_path.ts`
            **Exit Signal:** Parity is understood well enough for cutover review.
            **Checklist:**
            - [ ] Compare representative reads in staging
            - [ ] Stop if mismatch exceeds tolerance

            ## Verification
            - Compare representative reads.

            ## Stop Conditions
            - Stop if rollback is not available.

            ## Rollout / Rollback
            - Rollout: dual-read before cutover
            - Rollback: restore old path

            ## Compatibility / Migration
            - Keep the old path authoritative until parity passes.

            ## Decision Log
            - Decision: Use dual-read first
              Why: It reduces cutover risk.

            ## Handoff
            Do not start cleanup before parity is verified.
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertIn(
            "Contract profile `migration` requires `## Risks & Mitigations`.",
            issues,
        )

    def test_write_tests_phrase_does_not_trigger_placeholder_failure(self) -> None:
        plan = textwrap.dedent(
            """\
            # Improve Cache Coverage

            **Goal:** Improve cache coverage.
            **Task Type:** `cache-validation-improvement`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Cache behavior is verified.

            ## Inputs / Context Sources
            - `src/cache/cache.ts`

            ## Context Scope
            - Use only the cache module and the stated test path.

            ## Flow Graph
            tests -> implementation -> handoff

            ## Stages
            ### Stage 1: Improve test coverage
            **Purpose:** Add verification around cache invalidation.
            **Files:** `src/cache/cache.ts`, `tests/cache/test_cache.py`
            **Exit Signal:** Cache invalidation behavior is covered.
            **Checklist:**
            - [ ] Write tests for cache invalidation in `tests/cache/test_cache.py`
            - [ ] Run the new invalidation checks

            ## Verification
            - Run cache invalidation tests.

            ## Stop Conditions
            - Stop if the cache invalidation owner is unclear.

            ## Decision Log
            - Decision: Add a focused cache invalidation test
              Why: The change needs regression protection.

            ## Handoff
            Add the regression test before changing invalidation logic.
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])

    def test_missing_recommended_stage_fields_warn(self) -> None:
        plan = textwrap.dedent(
            """\
            # Add Suggestions

            **Goal:** Add suggestions.
            **Task Type:** `search-suggestions`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Suggestions appear.

            ## Inputs / Context Sources
            - `src/search/SearchBox.tsx`

            ## Context Scope
            - Use only the listed search file.

            ## Flow Graph
            analysis -> implementation

            ## Stages
            ### Stage 1: Add suggestion behavior
            **Purpose:** Add suggestion behavior.
            **Checklist:**
            - [ ] Implement suggestion behavior
            - [ ] Run the relevant UI test

            ## Verification
            - Run the relevant UI test.

            ## Stop Conditions
            - Stop if ownership is unclear.

            ## Decision Log
            - Decision: Keep scope small
              Why: The feature is incremental.

            ## Handoff
            Start with the UI boundary.
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertIn(
            "Stage 1 is missing recommended field `**Files:**`.",
            _warnings,
        )

    def test_unknown_contract_profile_fails(self) -> None:
        plan = textwrap.dedent(
            """\
            # Run Experiment

            **Goal:** Run an experiment.
            **Task Type:** `feasibility-experiment`
            **Contract Profile:** `experiment`
            **Mode:** `credit-rich`
            **Primary Success Signal:** A bounded recommendation exists.

            ## Inputs / Context Sources
            - `src/experiment.py`

            ## Context Scope
            - Use only the listed experiment file.

            ## Flow Graph
            context -> trial -> handoff

            ## Stages
            ### Stage 1: Run trial
            **Purpose:** Run the smallest useful trial.
            **Files:** `src/experiment.py`
            **Checklist:**
            - [ ] Run the trial
            - [ ] Confirm the trial can produce a bounded outcome

            ## Verification
            - Run the prototype trial.

            ## Stop Conditions
            - Stop if scope expands.

            ## Decision Log
            - Decision: Keep scope narrow
              Why: This is an experiment, not implementation.

            ## Handoff
            Produce a bounded recommendation.
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Unknown contract profile `experiment`" in issue for issue in issues)
        )

    def test_budget_limited_mode_suppresses_recommended_field_warnings(self) -> None:
        plan = textwrap.dedent(
            """\
            # Prototype Search

            **Goal:** Evaluate a search prototype.
            **Task Type:** `search-feasibility-experiment`
            **Contract Profile:** `exploration`
            **Mode:** `budget-limited`
            **Primary Success Signal:** The prototype yields a bounded recommendation.

            ## Inputs / Context Sources
            - `src/help/search.ts`

            ## Context Scope
            - Use only the listed exploration files.

            ## Flow Graph
            context -> prototype -> recommendation

            ## Stages
            ### Stage 1: Run bounded prototype
            **Purpose:** Produce enough evidence to recommend proceed, defer, or reject.
            **Checklist:**
            - [ ] Record one quality comparison
            - [ ] Record one complexity observation

            ## Verification
            - Execute the prototype and record the result.

            ## Stop Conditions
            - Stop if the bounded recommendation cannot be produced.

            ## Decision Log
            - Decision: Use budget-limited mode
              Why: Fast feasibility matters more than completeness.

            ## Handoff
            End with a bounded recommendation.
            """
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    def test_missing_context_scope_fails(self) -> None:
        plan = textwrap.dedent(
            """\
            # Missing Context Scope

            **Goal:** Validate a broken plan.
            **Task Type:** `broken-example`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** The validator catches the broken shape.

            ## Inputs / Context Sources
            - `src/example.ts`

            ## Flow Graph
            discovery -> implementation

            ## Stages
            ### Stage 1: Do work
            **Purpose:** Do the work.
            **Checklist:**
            - [ ] Perform the work

            ## Verification
            - Run the example check.

            ## Stop Conditions
            - Stop if the context is unclear.

            ## Decision Log
            - Decision: Keep this broken on purpose
              Why: It is a test fixture.

            ## Handoff
            Continue with the fix.
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertIn("Missing heading: `## Context Scope`.", issues)

    def test_todo_produces_warning_not_issue(self) -> None:
        plan = textwrap.dedent(
            """\
            # Add Feature

            **Goal:** Add the feature.
            **Task Type:** `feature-add`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Feature ships.

            ## Inputs / Context Sources
            - `src/feature.ts`

            ## Context Scope
            - Use the listed file only.

            ## Flow Graph
            analysis -> implementation

            ## Stages
            ### Stage 1: Implement
            **Purpose:** Implement feature behavior. TODO: confirm exact spec with user.
            **Files:** `src/feature.ts`
            **Exit Signal:** Feature is ready for review.
            **Checklist:**
            - [ ] Implement the main path
            - [ ] Run relevant tests

            ## Verification
            - Run the relevant test.

            ## Stop Conditions
            - Stop if the spec is unclear.

            ## Decision Log
            - Decision: Keep scope narrow
              Why: Small incremental change.

            ## Handoff
            Start with the implementation.
            """
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertTrue(any("TODO" in w for w in warnings))

    def test_tbd_produces_warning_not_issue(self) -> None:
        plan = textwrap.dedent(
            """\
            # Add Feature

            **Goal:** Add the feature.
            **Task Type:** `feature-add`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Feature ships.

            ## Inputs / Context Sources
            - `src/feature.ts`

            ## Context Scope
            - Use the listed file only. Owner: TBD (pending user confirmation).

            ## Flow Graph
            analysis -> implementation

            ## Stages
            ### Stage 1: Implement
            **Purpose:** Implement feature behavior.
            **Files:** `src/feature.ts`
            **Exit Signal:** Feature is ready for review.
            **Checklist:**
            - [ ] Implement the main path
            - [ ] Run relevant tests

            ## Verification
            - Run the relevant test.

            ## Stop Conditions
            - Stop if the spec is unclear.

            ## Decision Log
            - Decision: Keep scope narrow
              Why: Small incremental change.

            ## Handoff
            Start with the implementation.
            """
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertTrue(any("TBD" in w for w in warnings))

    def test_todo_in_code_block_is_ignored(self) -> None:
        plan = textwrap.dedent(
            """\
            # Add Feature

            **Goal:** Add the feature.
            **Task Type:** `feature-add`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Feature ships.

            ## Inputs / Context Sources
            - `src/feature.ts`

            ## Context Scope
            - Use the listed file only.

            ## Flow Graph
            analysis -> implementation

            ## Stages
            ### Stage 1: Implement
            **Purpose:** Implement feature behavior.
            **Files:** `src/feature.ts`
            **Exit Signal:** Feature is ready for review.
            **Checklist:**
            - [ ] Implement the main path
            - [ ] Run relevant tests

            Sample snippet that must be preserved verbatim:

            ```python
            # TODO: replace with real implementation
            pass
            ```

            ## Verification
            - Run the relevant test.

            ## Stop Conditions
            - Stop if the spec is unclear.

            ## Decision Log
            - Decision: Keep scope narrow
              Why: Small incremental change.

            ## Handoff
            Start with the implementation.
            """
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertEqual([w for w in warnings if "TODO" in w], [])

    def test_lazy_list_items_still_produce_issue(self) -> None:
        plan = textwrap.dedent(
            """\
            # Add Feature

            **Goal:** Add the feature.
            **Task Type:** `feature-add`
            **Contract Profile:** `delivery`
            **Mode:** `credit-rich`
            **Primary Success Signal:** Feature ships.

            ## Inputs / Context Sources
            - `src/feature.ts`

            ## Context Scope
            - Use the listed file only.

            ## Flow Graph
            analysis -> implementation

            ## Stages
            ### Stage 1: Implement
            **Purpose:** Implement feature behavior.
            **Files:** `src/feature.ts`
            **Exit Signal:** Feature is ready for review.
            **Checklist:**
            - [ ] Implement the main path

            ## Verification
            - Run the relevant test.
            - implement later

            ## Stop Conditions
            - Stop if the spec is unclear.

            ## Decision Log
            - Decision: Keep scope narrow
              Why: Small incremental change.

            ## Handoff
            Start with the implementation.
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("implement later" in i for i in issues),
            f"Expected hard placeholder issue, got: {issues}",
        )


class ValidateFilenameTests(unittest.TestCase):
    def test_canonical_filename_passes(self) -> None:
        issues = VALIDATOR.validate_filename(
            Path("plan.delivery.search-suggestions-cache.md")
        )
        self.assertEqual(issues, [])

    def test_all_four_profiles_pass(self) -> None:
        for profile in ("delivery", "refactor", "migration", "exploration"):
            with self.subTest(profile=profile):
                issues = VALIDATOR.validate_filename(
                    Path(f"plan.{profile}.sample-task.md")
                )
                self.assertEqual(issues, [])

    def test_profile_with_hyphen_fails(self) -> None:
        issues = VALIDATOR.validate_filename(
            Path("plan.some-profile.foo.md")
        )
        self.assertEqual(len(issues), 1)
        self.assertIn("does not match required pattern", issues[0])

    def test_uppercase_profile_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("plan.Delivery.foo.md"))
        self.assertEqual(len(issues), 1)

    def test_uppercase_task_type_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("plan.delivery.Foo_Bar.md"))
        self.assertEqual(len(issues), 1)

    def test_missing_plan_prefix_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("delivery.foo.md"))
        self.assertEqual(len(issues), 1)

    def test_too_few_segments_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("plan.delivery.md"))
        self.assertEqual(len(issues), 1)

    def test_too_many_segments_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("plan.delivery.foo.bar.md"))
        self.assertEqual(len(issues), 1)

    def test_empty_profile_segment_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("plan..foo.md"))
        self.assertEqual(len(issues), 1)

    def test_empty_task_type_segment_fails(self) -> None:
        issues = VALIDATOR.validate_filename(Path("plan.delivery..md"))
        self.assertEqual(len(issues), 1)

    def test_directory_prefix_is_ignored(self) -> None:
        # basename-only check: directory components must not affect validation.
        issues = VALIDATOR.validate_filename(
            Path("plans/subdir/plan.delivery.foo.md")
        )
        self.assertEqual(issues, [])

    def test_validate_merges_filename_issues_when_path_provided(self) -> None:
        issues, _warnings = VALIDATOR.validate(
            valid_feature_plan(), Path("wrong-name.md")
        )
        self.assertTrue(
            any("does not match required pattern" in issue for issue in issues)
        )

    def test_validate_without_path_skips_filename_check(self) -> None:
        # Backward-compatible: existing callers that pass text only must not regress.
        issues, warnings = VALIDATOR.validate(valid_feature_plan())
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
