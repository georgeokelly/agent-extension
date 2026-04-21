from __future__ import annotations

import importlib.util
import re
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


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def valid_feature_plan() -> str:
    """A minimal plan that passes every validator check.

    Every negative test in this module starts from this base fixture and
    surgically corrupts one region to trigger a single new structural error.
    Keep `valid_feature_plan` changes additive so the negative tests stay
    scoped to the failure they are exercising.
    """
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

        ## Output
        - Artifact produced by this plan.

        ## Dependency Graph
        s1 -> h

        ## Stages

        ### s1: Add cache behavior
        **Purpose:** Introduce cached suggestion behavior.
        **Files:** `src/search/SearchBox.tsx`, `src/search/__tests__/SearchBox.test.tsx`
        **Exit Signal:** Cache behavior is ready for validation.
        **Checklist:**
        - [ ] Add cache-aware fetch behavior
        - [ ] Confirm the cache boundary is still valid

        ### h: Handoff
        **Purpose:** Final sign-off — confirm all earlier work is complete and the Primary Success Signal holds.
        **Exit Signal:** Every earlier entry in `## Stage Claims` is `[x]` and the Primary Success Signal is met.
        **Checklist:**
        - [ ] All earlier entries in `## Stage Claims` are `[x]`
        - [ ] Cached suggestions still return correct results for the canonical queries

        ## Verification
        - Run the relevant tests for search suggestions.

        ## Decision Points
        - When the available context does not show who owns invalidation.

        ## Decision Log
        - Decision: Keep cache ownership in the API layer
          Why: It is shared across multiple consumers.

        ## Debug Log Standard

        > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
        >
        > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

        ## Stage Claims

        > **Runtime coordination ledger** — composer seeds one `- [ ]` entry per DAG node (stages `s*`, checkpoints `ck*`, handoff `h`). Executors update in place:
        >
        > - `- [ ] <id>: <label>` — unclaimed
        > - `- [~] <id>: <label> — <agent-id> @ <MMDDHHMM>` — claimed, in progress
        > - `- [x] <id>: <label> — <agent-id> @ <MMDDHHMM>` — done
        >
        > See the Stage Claims section of `reference.md` for the full claim protocol.

        - [ ] s1: Add cache behavior
        - [ ] h: Handoff
        """
    )


# ---------------------------------------------------------------------------
# Positive / happy-path plan tests
# ---------------------------------------------------------------------------


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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Enter dual-read
            **Purpose:** Compare old and new reads.
            **Files:** `src/data/read_path.ts`
            **Exit Signal:** Parity is understood well enough for cutover review.
            **Checklist:**
            - [ ] Compare representative reads in staging
            - [ ] Stop if mismatch exceeds tolerance

            ### h: Handoff
            **Purpose:** Final sign-off — confirm cutover is ready.
            **Exit Signal:** Every earlier entry in `## Stage Claims` is `[x]`.
            **Checklist:**
            - [ ] All earlier entries in `## Stage Claims` are `[x]`

            ## Verification
            - Compare representative reads.

            ## Decision Points
            - When rollback is not available.

            ## Rollout / Rollback
            - Rollout: dual-read before cutover
            - Rollback: restore old path

            ## Compatibility / Migration
            - Keep the old path authoritative until parity passes.

            ## Decision Log
            - Decision: Use dual-read first
              Why: It reduces cutover risk.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Enter dual-read
            - [ ] h: Handoff
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Contract profile `migration` requires `## Risks & Mitigations`" in issue
                for issue in issues
            )
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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Improve test coverage
            **Purpose:** Add verification around cache invalidation.
            **Files:** `src/cache/cache.ts`, `tests/cache/test_cache.py`
            **Exit Signal:** Cache invalidation behavior is covered.
            **Checklist:**
            - [ ] Write tests for cache invalidation in `tests/cache/test_cache.py`
            - [ ] Run the new invalidation checks

            ### h: Handoff
            **Purpose:** Final sign-off — confirm all earlier work is complete.
            **Exit Signal:** Every earlier entry in `## Stage Claims` is `[x]`.
            **Checklist:**
            - [ ] All earlier entries in `## Stage Claims` are `[x]`

            ## Verification
            - Run cache invalidation tests.

            ## Decision Points
            - When the cache invalidation owner is unclear.

            ## Decision Log
            - Decision: Add a focused cache invalidation test
              Why: The change needs regression protection.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Improve test coverage
            - [ ] h: Handoff
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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Add suggestion behavior
            **Purpose:** Add suggestion behavior.
            **Checklist:**
            - [ ] Implement suggestion behavior
            - [ ] Run the relevant UI test

            ### h: Handoff
            **Purpose:** Final sign-off — confirm suggestions ship.
            **Exit Signal:** Every earlier entry in `## Stage Claims` is `[x]`.
            **Checklist:**
            - [ ] All earlier entries in `## Stage Claims` are `[x]`

            ## Verification
            - Run the relevant UI test.

            ## Decision Points
            - When ownership is unclear.

            ## Decision Log
            - Decision: Keep scope small
              Why: The feature is incremental.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Add suggestion behavior
            - [ ] h: Handoff
            """
        )
        _issues, warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "`### s1: Add suggestion behavior` is missing recommended field `**Files:**`"
                in w
                for w in warnings
            )
        )

    def test_handoff_stage_without_files_does_not_warn(self) -> None:
        # The handoff shape (`h`) does not recommend `Files`; ensure no warning
        # is emitted even when the handoff block omits it.
        _issues, warnings = VALIDATOR.validate(valid_feature_plan())
        self.assertFalse(
            any("`### h:" in w and "missing recommended field `**Files:**`" in w for w in warnings),
            f"Handoff should be exempt from the Files warning; got: {warnings}",
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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Run trial
            **Purpose:** Run the smallest useful trial.
            **Files:** `src/experiment.py`
            **Exit Signal:** Trial produces a bounded outcome.
            **Checklist:**
            - [ ] Run the trial
            - [ ] Confirm the trial can produce a bounded outcome

            ### h: Handoff
            **Purpose:** Sign off on the trial outcome.
            **Exit Signal:** Every earlier entry in `## Stage Claims` is `[x]`.
            **Checklist:**
            - [ ] All earlier entries in `## Stage Claims` are `[x]`

            ## Verification
            - Run the prototype trial.

            ## Decision Points
            - When scope expands.

            ## Decision Log
            - Decision: Keep scope narrow
              Why: This is an experiment, not implementation.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Run trial
            - [ ] h: Handoff
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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Run bounded prototype
            **Purpose:** Produce enough evidence to recommend proceed, defer, or reject.
            **Checklist:**
            - [ ] Record one quality comparison
            - [ ] Record one complexity observation

            ### h: Handoff
            **Purpose:** Final sign-off — confirm bounded recommendation exists.
            **Checklist:**
            - [ ] All earlier entries in `## Stage Claims` are `[x]`

            ## Verification
            - Execute the prototype and record the result.

            ## Decision Points
            - When the bounded recommendation cannot be produced.

            ## Decision Log
            - Decision: Use budget-limited mode
              Why: Fast feasibility matters more than completeness.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Run bounded prototype
            - [ ] h: Handoff
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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Do work
            **Purpose:** Do the work.
            **Checklist:**
            - [ ] Perform the work

            ### h: Handoff
            **Purpose:** Sign off on the work.
            **Checklist:**
            - [ ] All earlier entries are `[x]`

            ## Verification
            - Run the example check.

            ## Decision Points
            - When the context is unclear.

            ## Decision Log
            - Decision: Keep this broken on purpose
              Why: It is a test fixture.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Do work
            - [ ] h: Handoff
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Missing heading: `## Context Scope`" in issue for issue in issues)
        )

    def test_todo_produces_warning_not_issue(self) -> None:
        plan = valid_feature_plan().replace(
            "**Purpose:** Introduce cached suggestion behavior.",
            "**Purpose:** Introduce cached suggestion behavior. TODO: confirm exact spec with user.",
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertTrue(any("TODO" in w for w in warnings))

    def test_tbd_produces_warning_not_issue(self) -> None:
        plan = valid_feature_plan().replace(
            "- Use only the listed search files.",
            "- Use only the listed search files. Owner: TBD (pending user confirmation).",
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertTrue(any("TBD" in w for w in warnings))

    def test_todo_in_code_block_is_ignored(self) -> None:
        plan = valid_feature_plan().replace(
            "- [ ] Confirm the cache boundary is still valid",
            textwrap.dedent(
                """\
                - [ ] Confirm the cache boundary is still valid

                Sample snippet that must be preserved verbatim:

                ```python
                # TODO: replace with real implementation
                pass
                ```
                """
            ).rstrip(),
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertEqual([w for w in warnings if "TODO" in w], [])

    def test_lazy_list_items_still_produce_issue(self) -> None:
        plan = valid_feature_plan().replace(
            "## Verification\n- Run the relevant tests for search suggestions.",
            "## Verification\n- Run the relevant tests for search suggestions.\n- implement later",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("implement later" in i for i in issues),
            f"Expected hard placeholder issue, got: {issues}",
        )

    # ---- Mermaid surface form with color coding --------------------------

    def test_mermaid_dag_with_classdef_passes(self) -> None:
        plan = valid_feature_plan().replace(
            "## Dependency Graph\ns1 -> h",
            textwrap.dedent(
                """\
                ## Dependency Graph

                ```mermaid
                flowchart TD
                  s1[Cache]
                  h[Handoff]

                  s1 --> h

                  classDef stage   fill:#dbeafe,stroke:#1e40af
                  classDef handoff fill:#dcfce7,stroke:#166534

                  class s1 stage
                  class h handoff
                ```
                """
            ).rstrip(),
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])

    # ---- DAG structural negative tests -----------------------------------

    def test_dag_cycle_is_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "s1 -> h",
            "s1 -> s2\ns2 -> s3\ns3 -> s1\ns1 -> h\ns2 -> h\ns3 -> h",
        )
        # Add s2/s3 content blocks + claims so the error surfaces as a cycle
        # rather than alignment mismatches.
        plan = plan.replace(
            "### h: Handoff",
            textwrap.dedent(
                """\
                ### s2: Stage two
                **Purpose:** stub
                **Checklist:**
                - [ ] placeholder

                ### s3: Stage three
                **Purpose:** stub
                **Checklist:**
                - [ ] placeholder

                ### h: Handoff"""
            ),
        )
        plan = plan.replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "- [ ] s1: Add cache behavior\n- [ ] s2: Stage two\n- [ ] s3: Stage three\n- [ ] h: Handoff",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("contains a cycle" in i for i in issues),
            f"Expected cycle issue, got: {issues}",
        )

    def test_dag_multiple_sinks_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "s1 -> h",
            "s1 -> h\ns1 -> s2",
        )
        # Align s2 into Stages and Stage Claims so only the DAG multi-sink
        # issue remains, not alignment noise.
        plan = plan.replace(
            "### h: Handoff",
            textwrap.dedent(
                """\
                ### s2: Orphan sink
                **Purpose:** stub
                **Checklist:**
                - [ ] placeholder

                ### h: Handoff"""
            ),
        )
        plan = plan.replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "- [ ] s1: Add cache behavior\n- [ ] s2: Orphan sink\n- [ ] h: Handoff",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("multiple sinks" in i for i in issues),
            f"Expected multiple-sinks issue, got: {issues}",
        )

    def test_dag_sink_not_h_rejected(self) -> None:
        # Replace the `h` DAG node + content + claim with a fake non-`h` sink
        # to force the "single sink is not `h`" check.
        plan = valid_feature_plan()
        plan = plan.replace("s1 -> h", "s1 -> s2")
        plan = plan.replace("### h: Handoff", "### s2: Recommendation")
        plan = plan.replace("- [ ] h: Handoff", "- [ ] s2: Recommendation")
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "single sink is `s2`" in i and "id is not `h`" in i
                for i in issues
            ),
            f"Expected handoff-sink issue, got: {issues}",
        )

    def test_unknown_id_prefix_rejected(self) -> None:
        # `xy1` is not a recognized prefix; validator must reject both at the
        # DAG level and at the content-block level.
        plan = valid_feature_plan().replace("s1 -> h", "xy1 -> h")
        plan = plan.replace("### s1: Add cache behavior", "### xy1: Add cache behavior")
        plan = plan.replace("- [ ] s1: Add cache behavior", "- [ ] xy1: Add cache behavior")
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("unknown id prefix" in i for i in issues),
            f"Expected unknown-id-prefix issue, got: {issues}",
        )

    # ---- Alignment negative tests ----------------------------------------

    def test_content_block_id_not_in_dag_rejected(self) -> None:
        # Orphan content block `s7` whose id is absent from the DAG.
        plan = valid_feature_plan().replace(
            "### h: Handoff",
            textwrap.dedent(
                """\
                ### s7: Orphan block
                **Purpose:** stub
                **Checklist:**
                - [ ] placeholder

                ### h: Handoff"""
            ),
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "content blocks with ids not in `## Dependency Graph`" in i
                and "`s7`" in i
                for i in issues
            ),
            f"Expected orphan-content-block issue, got: {issues}",
        )

    def test_dag_node_without_content_block_rejected(self) -> None:
        # Add `s2` to DAG and claims, but not to Stages. Validator must report
        # the missing content block.
        plan = valid_feature_plan()
        plan = plan.replace("s1 -> h", "s1 -> s2\ns2 -> h")
        plan = plan.replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "- [ ] s1: Add cache behavior\n- [ ] s2: Missing block\n- [ ] h: Handoff",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "DAG nodes without a matching `## Stages` content block" in i
                and "`s2`" in i
                for i in issues
            ),
            f"Expected missing-content-block issue, got: {issues}",
        )

    def test_stage_claims_entry_not_in_dag_rejected(self) -> None:
        # Ledger has an `s9` entry that does not exist in the DAG.
        plan = valid_feature_plan().replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "- [ ] s1: Add cache behavior\n- [ ] s9: Ghost stage\n- [ ] h: Handoff",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "`## Stage Claims` entries with ids not in `## Dependency Graph`" in i
                and "`s9`" in i
                for i in issues
            ),
            f"Expected orphan-claim-entry issue, got: {issues}",
        )

    # ---- Checkpoint-shape negative tests ---------------------------------

    def _insert_checkpoint_into_valid_plan(self, ck_block: str) -> str:
        """Insert a `ck1` node between `s1` and `h` in `valid_feature_plan`."""
        plan = valid_feature_plan()
        plan = plan.replace("s1 -> h", "s1 -> ck1\nck1 -> h")
        plan = plan.replace("### h: Handoff", ck_block + "\n\n### h: Handoff")
        plan = plan.replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "- [ ] s1: Add cache behavior\n- [ ] ck1: Schema review\n- [ ] h: Handoff",
        )
        return plan

    def test_valid_checkpoint_block_passes(self) -> None:
        ck_block = textwrap.dedent(
            """\
            ### ck1: Schema review
            **Purpose:** verify schema boundary is clean
            **Mode:** auto_review
            **Exit Signal:** all pass criteria green
            **Checklist:**
            - [ ] migration runs idempotently
            - [ ] no cross-table cycles
            **On Fail:** revise_plan"""
        )
        plan = self._insert_checkpoint_into_valid_plan(ck_block)
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [], f"Expected clean validation, got: {issues}")
        # Warnings are tolerated (e.g., recommended On Fail) but we asserted it here.
        self.assertFalse(
            any("ck1:" in w for w in warnings),
            f"Expected no ck1 warnings, got: {warnings}",
        )

    def test_checkpoint_missing_mode_rejected(self) -> None:
        ck_block = textwrap.dedent(
            """\
            ### ck1: Schema review
            **Purpose:** verify schema boundary is clean
            **Exit Signal:** all pass criteria green
            **Checklist:**
            - [ ] migration runs idempotently
            **On Fail:** revise_plan"""
        )
        plan = self._insert_checkpoint_into_valid_plan(ck_block)
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "`### ck1: Schema review` is missing required field `**Mode:**`" in i
                for i in issues
            ),
            f"Expected missing-Mode issue, got: {issues}",
        )

    def test_checkpoint_invalid_mode_rejected(self) -> None:
        ck_block = textwrap.dedent(
            """\
            ### ck1: Schema review
            **Purpose:** verify schema boundary is clean
            **Mode:** careful_review
            **Exit Signal:** all pass criteria green
            **Checklist:**
            - [ ] migration runs idempotently
            **On Fail:** revise_plan"""
        )
        plan = self._insert_checkpoint_into_valid_plan(ck_block)
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "has unknown checkpoint `**Mode:**` `careful_review`" in i
                for i in issues
            ),
            f"Expected invalid-Mode issue, got: {issues}",
        )

    # ---- Handoff-shape negative tests -----------------------------------

    def test_multiple_handoff_blocks_rejected(self) -> None:
        # Second `### h:` block should trigger the "multiple handoff" error.
        plan = valid_feature_plan().replace(
            "### h: Handoff",
            textwrap.dedent(
                """\
                ### h: Handoff
                **Purpose:** Placeholder duplicate.
                **Checklist:**
                - [ ] placeholder

                ### h: Handoff"""
            ),
            1,
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Multiple handoff content blocks found" in i for i in issues),
            f"Expected multiple-handoff issue, got: {issues}",
        )

    def test_last_block_not_handoff_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "### h: Handoff",
            "### s2: Wrap up",
        ).replace(
            "- [ ] h: Handoff",
            "- [ ] s2: Wrap up",
        ).replace("s1 -> h", "s1 -> s2")
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Last content block under `## Stages` is not the handoff node" in i
                and "`### s2: Wrap up`" in i
                for i in issues
            ),
            f"Expected last-block-not-handoff issue, got: {issues}",
        )

    # ---- Stage Claims negative tests ------------------------------------

    def test_stage_claims_prefilled_marker_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "- [ ] s1: Add cache behavior",
            "- [x] s1: Add cache behavior — agent-a @ 04150900",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Stage Claims` contains pre-filled markers" in i for i in issues),
            f"Expected pre-filled-marker issue, got: {issues}",
        )

    def test_stage_claims_last_entry_must_be_h(self) -> None:
        # Isolate the "last entry must be `h`" check by *swapping*
        # the order of the existing ledger entries rather than
        # surgically rewriting them. The id set remains `{s1, h}`
        # so `validate_id_alignment` is untouched; only the ordering
        # trips the last-entry diagnostic. Earlier versions dropped
        # the `h` entry entirely and accepted that alignment also
        # complained — which left this test accidentally tolerant
        # of any other diagnostic as long as the target substring
        # also appeared. The strict `issues == [expected]` comparison
        # below catches that regression.
        plan = valid_feature_plan().replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff\n",
            "- [ ] h: Handoff\n- [ ] s1: Add cache behavior\n",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        matching = [
            i
            for i in issues
            if "Last `## Stage Claims` entry is not the `h` handoff" in i
        ]
        self.assertEqual(
            len(matching),
            1,
            f"Expected exactly one last-entry-not-h issue, got: {issues}",
        )
        self.assertEqual(
            issues,
            matching,
            f"Expected only the last-entry-not-h issue; other diagnostics "
            f"indicate the fixture broke more than one rule: {issues}",
        )

    def test_stage_claims_no_ledger_entries_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "Prose-only ledger placeholder, no list items.",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Stage Claims` has no ledger entries" in i for i in issues),
            f"Expected empty-Stage-Claims issue, got: {issues}",
        )

    def test_stage_claims_malformed_entry_rejected(self) -> None:
        # `Stage 1: foo` is the old pre-migration format; validator rejects
        # it as malformed because it does not parse into `<id>: <label>`.
        plan = valid_feature_plan().replace(
            "- [ ] s1: Add cache behavior",
            "- [ ] Stage 1: Add cache behavior",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Stage Claims` has malformed entries" in i for i in issues),
            f"Expected malformed-entry issue, got: {issues}",
        )

    def test_stage_claims_duplicate_ids_rejected(self) -> None:
        # Inject a duplicate `s1` claim. Without changing anything else the
        # alignment check would also fire, but the duplicate error surfaces
        # first with its own message.
        plan = valid_feature_plan().replace(
            "- [ ] s1: Add cache behavior\n- [ ] h: Handoff",
            "- [ ] s1: Add cache behavior\n- [ ] s1: Accidental duplicate\n- [ ] h: Handoff",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Stage Claims` has duplicate entry ids" in i and "`s1`" in i
                for i in issues
            ),
            f"Expected duplicate-ids issue, got: {issues}",
        )

    # ---- Checkpoint mode enumeration ------------------------------------

    def test_checkpoint_mode_human_review_passes(self) -> None:
        # `human_review` is a valid enum value per `ALLOWED_CHECKPOINT_MODES`;
        # regression coverage ensures the enum list is honored for all three
        # values, not just the default `auto_review`.
        ck_block = textwrap.dedent(
            """\
            ### ck1: Schema review
            **Purpose:** verify schema boundary is clean
            **Mode:** human_review
            **Exit Signal:** all pass criteria green
            **Checklist:**
            - [ ] migration runs idempotently
            **On Fail:** escalate"""
        )
        plan = self._insert_checkpoint_into_valid_plan(ck_block)
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [], f"Expected clean validation, got: {issues}")

    def test_checkpoint_mode_hybrid_passes(self) -> None:
        # `hybrid` is the third valid enum value — auto review with human
        # fallback. Same regression-coverage rationale as human_review.
        ck_block = textwrap.dedent(
            """\
            ### ck1: Integration review
            **Purpose:** verify integration seam holds
            **Mode:** hybrid
            **Exit Signal:** all pass criteria green
            **Checklist:**
            - [ ] API contract matches spec
            **On Fail:** escalate"""
        )
        plan = self._insert_checkpoint_into_valid_plan(ck_block)
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [], f"Expected clean validation, got: {issues}")

    # ---- Required-heading level + field-content strictness --------------

    def test_required_heading_at_wrong_level_rejected(self) -> None:
        # Previously `##+` matched any heading level — so a nested
        # `### Risks & Mitigations` would silently satisfy migration's
        # required-heading check. Tightening to `^##` rejects sub-section
        # placement; writers must lift required headings to top level.
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

            ## Output
            - Artifact produced by this plan.

            ## Dependency Graph
            s1 -> h

            ## Stages

            ### s1: Enter dual-read
            **Purpose:** Compare old and new reads.
            **Checklist:**
            - [ ] Compare representative reads

            ### h: Handoff
            **Purpose:** Final sign-off.
            **Checklist:**
            - [ ] All earlier entries are `[x]`

            ## Verification
            - Compare representative reads.

            ## Decision Points
            - When rollback is not available.

            ## Rollout / Rollback
            - Rollout: dual-read before cutover

            ## Compatibility / Migration
            - Keep the old path authoritative until parity passes.

            ## Notes
            ### Risks & Mitigations
            - Rollback may need manual steps.

            ## Decision Log
            - Decision: Use dual-read first
              Why: It reduces cutover risk.

            ## Debug Log Standard

            > **Standard — include verbatim**; points the executor to the debug log format this plan follows when the debug loop is entered.
            >
            > Format: `debug_log_template.md`. Trigger: debug loop. Filename: `debug.<contract-profile>.<task-type>.<MMDDHHMM>.md` (executor fills the placeholders at session start).

            ## Stage Claims

            - [ ] s1: Enter dual-read
            - [ ] h: Handoff
            """
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Contract profile `migration` requires `## Risks & Mitigations`" in i
                for i in issues
            ),
            f"Expected missing-Risks issue (level-3 heading should not satisfy "
            f"the required-heading check); got: {issues}",
        )

    def test_metadata_empty_value_rejected(self) -> None:
        # `**Goal:** ` with trailing whitespace but no content must count as
        # missing; the previous `.+$` accepted it silently.
        plan = valid_feature_plan().replace(
            "**Goal:** Add cached suggestions.",
            "**Goal:**   ",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Missing metadata line: `**Goal:**`" in i for i in issues),
            f"Expected missing-Goal issue, got: {issues}",
        )

    def test_content_block_field_empty_value_rejected(self) -> None:
        # Same regex tightening applies inside content blocks.
        plan = valid_feature_plan().replace(
            "**Purpose:** Introduce cached suggestion behavior.",
            "**Purpose:**   ",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "`### s1: Add cache behavior` is missing required field `**Purpose:**`"
                in i
                for i in issues
            ),
            f"Expected missing-Purpose issue, got: {issues}",
        )

    # ---- Hard placeholder variants --------------------------------------

    def test_checkbox_prefixed_lazy_list_rejected(self) -> None:
        # `- [ ] implement later` with an unchecked checkbox is still a lazy
        # placeholder; the patterns must tolerate the optional `[ ]` prefix.
        plan = valid_feature_plan().replace(
            "## Verification\n- Run the relevant tests for search suggestions.",
            "## Verification\n- Run the relevant tests for search suggestions.\n- [ ] implement later",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("implement later" in i for i in issues),
            f"Expected hard-placeholder issue for `- [ ] implement later`, got: {issues}",
        )

    # ---- Duplicate content block detection ------------------------------

    def test_duplicate_content_block_ids_rejected(self) -> None:
        # Two `### s1:` content blocks would otherwise collapse into one id in
        # the block_ids set and silently pass alignment; the explicit duplicate
        # check surfaces the real problem.
        plan = valid_feature_plan().replace(
            "### h: Handoff",
            textwrap.dedent(
                """\
                ### s1: Duplicate cache behavior
                **Purpose:** Accidental second s1 block.
                **Checklist:**
                - [ ] placeholder

                ### h: Handoff"""
            ),
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Duplicate content block ids under `## Stages`" in i and "`s1`" in i
                for i in issues
            ),
            f"Expected duplicate-content-block issue, got: {issues}",
        )

    # ---- Checklist label vs bullets diagnostics -------------------------

    def test_checklist_label_missing_reported_separately(self) -> None:
        # Bullets alone (without the `**Checklist:**` label) are
        # structurally ambiguous — they could be confused with any other
        # `- [ ]` style list. The diagnostic must pinpoint the missing
        # label so the composer knows what to add.
        plan = valid_feature_plan().replace(
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "is missing the `**Checklist:**` label line" in i
                and "`### s1: Add cache behavior`" in i
                for i in issues
            ),
            f"Expected missing-label diagnostic, got: {issues}",
        )

    def test_checklist_label_present_but_no_bullets_reported(self) -> None:
        # The inverse case: the label line exists but no `- [ ]` bullets
        # follow it. A separate diagnostic lets the composer see which
        # half of the checklist is missing instead of a single blunt
        # "items missing" error that also fires when the label is gone.
        plan = valid_feature_plan().replace(
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
            "**Checklist:**",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "has a `**Checklist:**` label but no `- [ ] ...` bullets" in i
                and "`### s1: Add cache behavior`" in i
                for i in issues
            ),
            f"Expected missing-bullets diagnostic, got: {issues}",
        )

    # ---- Dependency Graph fence-guard -----------------------------------

    def test_prose_arrows_outside_mermaid_fence_ignored(self) -> None:
        # When a Mermaid fence is present, stray prose arrows above it (e.g.
        # preamble or comments) must NOT inject extra edges into the DAG.
        plan = valid_feature_plan().replace(
            "## Dependency Graph\ns1 -> h",
            textwrap.dedent(
                """\
                ## Dependency Graph

                Preamble that happens to mention s1 -> ghost and ghost -> h in prose.

                ```mermaid
                flowchart TD
                  s1[Cache]
                  h[Handoff]
                  s1 --> h
                ```
                """
            ).rstrip(),
        )
        issues, warnings = VALIDATOR.validate(plan)
        # The `ghost` prose token must not leak into the DAG; otherwise the
        # validator would complain about unknown prefixes or an orphan node.
        self.assertEqual(
            issues, [], f"Prose outside the fence leaked into DAG: {issues}"
        )
        self.assertEqual(warnings, [])

    # ---- Orphan top-level heading rejection -----------------------------

    def test_stray_top_level_heading_inside_content_block_rejected(self) -> None:
        # A bare `## Something` inside a content block would be
        # reinterpreted as a new top-level plan section by
        # `extract_stages_section`, silently truncating every later stage
        # and surfacing as confusing "missing node" errors. The validator
        # should name the offending heading so the composer sees the real
        # cause at first glance.
        plan = valid_feature_plan().replace(
            "**Purpose:** Introduce cached suggestion behavior.",
            "**Purpose:** Introduce cached suggestion behavior.\n"
            "## Oops this is not supposed to be a heading",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Unknown top-level heading" in i
                and "## Oops this is not supposed to be a heading" in i
                for i in issues
            ),
            f"Expected unknown-top-level-heading issue, got: {issues}",
        )

    def test_unknown_top_level_heading_at_plan_root_rejected(self) -> None:
        # Even a stray `## Random Section` at the plan root (not inside a
        # content block) is a drift from the contract; it indicates the
        # composer added a custom section outside the allowed set.
        plan = valid_feature_plan().replace(
            "## Verification",
            "## Aside\n- side commentary\n\n## Verification",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Unknown top-level heading `## Aside`" in i
                for i in issues
            ),
            f"Expected unknown-top-level-heading issue for `## Aside`, got: {issues}",
        )

    def test_hash_hash_inside_code_fence_ignored(self) -> None:
        # Control case: composer may legitimately illustrate markdown in a
        # fenced code sample. `##` inside a code fence should be treated as
        # content, not as a structural heading.
        plan = valid_feature_plan().replace(
            "**Purpose:** Introduce cached suggestion behavior.",
            textwrap.dedent(
                """\
                **Purpose:** Introduce cached suggestion behavior.

                ```markdown
                ## Example heading shown inside a code block
                ```
                """
            ).rstrip(),
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(
            issues, [], f"Code-fenced `##` should be ignored, got: {issues}"
        )
        self.assertEqual(warnings, [])

    # ---- Nested code-fence handling (stack-based) -----------------------

    def test_hard_placeholder_inside_nested_4backtick_fence_ignored(self) -> None:
        # A 4-backtick wrapper fence containing a 3-backtick inner fence
        # (a common shape in examples.md-style docs) must keep every line
        # between the outer 4 backticks invisible to the placeholder
        # scanner. A toggle-style tracker would treat the inner 3-backtick
        # opener as the 4-backtick's closer and falsely expose the lazy
        # bullet to `find_hard_placeholders`.
        nested_fence = textwrap.dedent(
            """\


            ````markdown
            Example of a lazy checklist to avoid:

            ```
            - [ ] implement later
            ```

            Note: the line above is illustrative content, not real work.
            ````"""
        )
        plan = valid_feature_plan().replace(
            "- [ ] Confirm the cache boundary is still valid",
            "- [ ] Confirm the cache boundary is still valid" + nested_fence,
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(
            issues,
            [],
            f"Nested 4-backtick fence failed to hide placeholder: {issues}",
        )
        self.assertEqual(warnings, [])

    def test_mismatched_fence_token_inside_open_fence_treated_as_literal(
        self,
    ) -> None:
        # Per CommonMark §4.5 a fence marker inside an open fence that
        # uses a *different* fence character is literal content, not a
        # nested opener. The earlier revision of this test embedded the
        # mismatched token as an inline fragment ("stuff ``` stays
        # literal"), which the `^ {0,3}` anchor in
        # `_FENCE_TOKEN_PATTERN` does not even match — so the tracker's
        # mismatch branch was never exercised and the test would pass
        # on almost any implementation, including a naïve toggle.
        #
        # Here the mismatched backtick fence is placed at column 0 —
        # the exact position that a naïve tracker would mis-identify
        # as a nested opener (or, worse, a closer). Two distinct
        # placeholder phrases let us assert both halves independently:
        #
        #   - `- [ ] add tests` lives *inside* the outer ``~~~`` fence.
        #     A correct stack-based tracker keeps the stack at
        #     ``["~~~"]`` across the inner ``` ``` ``` edges and hides
        #     the bullet. A naïve toggle would flip out of "in fence"
        #     state on the inner ``` and surface the bullet as a
        #     spurious hard-placeholder issue.
        #   - `- [ ] fill in later` lives *outside* the fence. Both
        #     trackers expose it; the assertion confirms the real
        #     closer still pops cleanly and does not leak fence depth
        #     onto later prose.
        #
        # The two phrases deliberately differ so placeholder
        # deduplication (keyed on the full `pattern + line` string)
        # cannot collapse one half into the other, which would mask
        # the naïve-tracker bug.
        leaky_block = (
            "\n"
            "~~~\n"
            "```\n"
            "- [ ] add tests\n"
            "```\n"
            "~~~\n"
            "\n"
            "- [ ] fill in later\n"
        )
        plan = valid_feature_plan().replace(
            "## Verification",
            leaky_block + "## Verification",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("fill in later" in i for i in issues),
            (
                "Placeholder outside the closed `~~~` fence was "
                "hidden; the stack-based tracker should pop `~~~` "
                "cleanly on the real closer and let the outer "
                f"bullet surface. Got issues: {issues}"
            ),
        )
        self.assertFalse(
            any("add tests" in i for i in issues),
            (
                "Bullet inside the `~~~` fence was exposed; a "
                "mismatched inner ``` at column 0 must be treated "
                "as literal content, not as an opener or a closer. "
                f"Got issues: {issues}"
            ),
        )

    # ---- Metrics / KPI + optional headings acceptance -------------------

    def test_metrics_kpi_optional_heading_accepted(self) -> None:
        # `Metrics / KPI` is listed as a Conditional section in reference.md.
        # It must be accepted as a known top-level heading; otherwise the
        # L4 orphan-heading detector would reject every plan that adds
        # observable success metrics.
        plan = valid_feature_plan().replace(
            "## Decision Points",
            textwrap.dedent(
                """\
                ## Metrics / KPI
                - Cache hit rate > 70% for the canonical query set.
                - Suggestion latency p95 drops below 150 ms.

                ## Decision Points"""
            ),
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(
            issues, [], f"`## Metrics / KPI` incorrectly rejected: {issues}"
        )
        self.assertEqual(warnings, [])

    def test_all_optional_headings_accepted_together(self) -> None:
        # Positive acceptance sweep: each name listed in the Required vs
        # Conditional matrix (KNOWN_OPTIONAL_HEADINGS) must pass alongside
        # the required set. Guards against accidental drift between the
        # allow-set and the documented matrix.
        optional_block = textwrap.dedent(
            """\
            ## Non-Goals
            - Not re-architecting the search stack.

            ## Risks & Mitigations
            - Stale cache risk — mitigated by TTL + invalidation hooks.

            ## Rollout / Rollback
            - Phased behind feature flag; rollback disables the flag.

            ## Compatibility / Migration
            - No API or data-format change; cache is additive.

            ## Sources / Rationale
            - Inspired by prior suggestion-cache benchmarks.

            ## Proposed Deliverables
            - Cached suggestion path in `searchApi.ts`.

            ## Committed Deliverables
            - Cached suggestion path in `searchApi.ts`.

            ## Checkpoint Notes
            - None; first iteration runs without a ck* gate.

            ## Metrics / KPI
            - Cache hit rate > 70%.

            ## Decision Points"""
        )
        plan = valid_feature_plan().replace("## Decision Points", optional_block)
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(
            issues,
            [],
            (
                "All KNOWN_OPTIONAL_HEADINGS should be accepted together; "
                f"got: {issues}"
            ),
        )
        self.assertEqual(warnings, [])

    # ---- Heading misplaced inside Stages body ---------------------------

    def test_known_heading_before_handoff_block_rejected(self) -> None:
        # A `##` inside the Stages body ends Stages at that line. That is
        # legal only when Stages has been walked to completion — i.e. the
        # `### h: ...` handoff block has already been seen. A `##`
        # appearing *before* the handoff block (even one with a legal
        # section name like `## Non-Goals`) misplaces the section and
        # truncates Stages prematurely. The composer needs a diagnostic
        # that names the offending heading and points at the fix (move
        # below handoff or demote to `###`).
        plan = valid_feature_plan().replace(
            "### h: Handoff",
            "## Non-Goals\n- Not re-architecting search.\n\n### h: Handoff",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Top-level heading `## Non-Goals`" in i
                and "inside the `## Stages` body" in i
                and "before the handoff block" in i
                for i in issues
            ),
            f"Expected pre-handoff misplacement diagnostic, got: {issues}",
        )

    def test_known_heading_after_handoff_block_accepted(self) -> None:
        # Control case: the same `## Non-Goals` placed *after* the
        # handoff block is just the normal end-of-Stages boundary and
        # must not be flagged. The validator must distinguish "first `##`
        # before handoff" (misplaced) from "first `##` after handoff"
        # (legal next section). Without this, `## Verification` —
        # itself a required post-Stages heading — would be flagged on
        # every valid plan.
        plan = valid_feature_plan().replace(
            "## Verification",
            "## Non-Goals\n- Not re-architecting search.\n\n## Verification",
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(
            issues,
            [],
            f"Post-handoff `## Non-Goals` wrongly flagged: {issues}",
        )
        self.assertEqual(warnings, [])

    def test_empty_stages_body_does_not_trigger_misplaced_heading(
        self,
    ) -> None:
        # When the Stages body has no `### <id>: <label>` content blocks
        # at all (e.g. the empty shape in `plan_template.md`), the first
        # `##` after `## Stages` is simply the next plan-level section
        # beginning. Other validators ("Stages contains no content
        # blocks", "Dependency Graph has no nodes") already flag the
        # real issue with clearer wording; the misplacement branch must
        # stay silent to avoid duplicating noise. Strip the content
        # blocks from the canonical plan and confirm the misplacement
        # diagnostic is absent.
        plan = valid_feature_plan()
        # Collapse Stages body to an empty shell so Verification is the
        # first `##` after Stages, with no `### ` blocks in between.
        plan = re.sub(
            r"## Stages\n[\s\S]*?(?=## Verification)",
            "## Stages\n\n",
            plan,
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertFalse(
            any(
                "inside the `## Stages` body" in i and "before the handoff block" in i
                for i in issues
            ),
            (
                "Empty Stages body should not trigger the misplacement "
                "branch; other validators already cover the empty-shape "
                f"case. Got: {issues}"
            ),
        )

    # ---- Checklist anchor + inline form diagnostics ---------------------

    def test_inline_checklist_form_rejected_with_specific_diagnostic(
        self,
    ) -> None:
        # `**Checklist:** some text` on a single line collapses the
        # two-line label + bullets form into a single-line scalar.
        # The composer treated Checklist as a regular field, which is
        # the one thing the core contract explicitly forbids. The
        # diagnostic must pinpoint the inline form so the fix
        # ("split into label + bullets") is obvious — not the generic
        # missing-label message.
        plan = valid_feature_plan().replace(
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
            "**Checklist:** will fill in details later.",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "uses the inline form" in i
                and "`**Checklist:** <value>`" in i
                and "`### s1: Add cache behavior`" in i
                for i in issues
            ),
            f"Expected inline-Checklist diagnostic, got: {issues}",
        )

    def test_checklist_bullets_before_label_without_bullets_after_rejected(
        self,
    ) -> None:
        # Anchor test: bullets earlier in the block (e.g. a stray
        # `- [ ]`-shaped line before the Checklist label) must NOT
        # satisfy the Checklist-bullets check when no bullets follow
        # the actual label. Without anchoring, an empty Checklist
        # section would pass whenever *any* `- [ ]` bullet existed
        # upstream in the same block.
        plan = valid_feature_plan().replace(
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
            "- [ ] Earlier stray bullet not part of Checklist\n"
            "**Checklist:**",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "has a `**Checklist:**` label but no `- [ ] ...` bullets" in i
                and "`### s1: Add cache behavior`" in i
                for i in issues
            ),
            (
                "Bullets before the label should not satisfy the anchored "
                "bullets-after-label check. Got: "
                f"{issues}"
            ),
        )

    def test_inline_checklist_without_space_also_rejected(self) -> None:
        # `**Checklist:**foo` (no whitespace before the value) is the
        # same mistake as `**Checklist:** foo` — both collapse the
        # label-and-bullets two-line form into a single scalar line.
        # The earlier `[ \t]+` pattern required at least one space
        # between the label and the value, so the no-space variant
        # silently fell through to the weaker "missing label"
        # diagnostic. The inline-specific message is more actionable,
        # so both shapes must trigger it.
        plan = valid_feature_plan().replace(
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
            "**Checklist:**will fill in details later.",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "uses the inline form" in i
                and "`### s1: Add cache behavior`" in i
                for i in issues
            ),
            (
                "Expected inline-Checklist diagnostic for the no-space "
                f"form, got: {issues}"
            ),
        )

    def test_whitespace_only_checklist_bullet_does_not_satisfy_bullets_check(
        self,
    ) -> None:
        # `- [ ]    ` — marker present, content empty. The earlier
        # `\s+.+$` pattern let a single trailing space backtrack into
        # `.+`, so this "empty" bullet was mis-classified as a valid
        # checklist item. Anchoring to `\S` rejects it, and the
        # "label without bullets" diagnostic fires instead.
        plan = valid_feature_plan().replace(
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid",
            "**Checklist:**\n"
            "- [ ]    ",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "has a `**Checklist:**` label but no `- [ ] ...` bullets" in i
                and "`### s1: Add cache behavior`" in i
                for i in issues
            ),
            (
                "Whitespace-only bullet should not satisfy the "
                f"bullets check. Got: {issues}"
            ),
        )

    def test_crlf_line_endings_accepted(self) -> None:
        # Plans authored on Windows editors arrive with CRLF line
        # endings. Every regex / line-scan assumes LF, so the
        # `validate()` entry point now normalizes CRLF and bare CR to
        # LF up front. Without that, each `\r` would count as
        # non-whitespace content before `$` (breaking anchored field
        # checks) and as a non-whitespace suffix on closing fences
        # (breaking the `_update_fence_stack` closer rule).
        plan_lf = valid_feature_plan()
        plan_crlf = plan_lf.replace("\n", "\r\n")
        issues, warnings = VALIDATOR.validate(plan_crlf)
        self.assertEqual(
            issues, [], f"CRLF input leaked into validation: {issues}"
        )
        self.assertEqual(
            warnings, [], f"CRLF input produced spurious warnings: {warnings}"
        )

    def test_misplaced_heading_when_stages_empty_but_content_follows_below(
        self,
    ) -> None:
        # The composer placed a legal-looking `##` immediately after
        # the `## Stages` header, which silently truncates Stages and
        # pushes the real `### <id>: ...` blocks into the next
        # section. Earlier revisions only fired the misplaced-heading
        # diagnostic when at least one content block had been seen
        # *before* the offending `##`; this missed the equally
        # broken case where the heading sits at the very top of
        # Stages with all content sitting below it. The scanner now
        # looks ahead and fires whenever any `### <id>: ...` appears
        # later in the document, so the composer gets a named
        # diagnostic instead of a cascade of "missing node" errors.
        plan = valid_feature_plan().replace(
            "## Stages\n\n### s1:",
            "## Stages\n\n## Sources / Rationale\n- side note\n\n### s1:",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "Top-level heading `## Sources / Rationale`" in i
                and "inside the `## Stages` body" in i
                for i in issues
            ),
            (
                "Empty-Stages-but-content-below case should still fire "
                f"the misplacement diagnostic. Got: {issues}"
            ),
        )

    def test_misplaced_heading_diagnostic_mentions_missing_handoff(
        self,
    ) -> None:
        # DF-a: when the candidate `##` truncates Stages and no
        # `### h: <label>` exists anywhere later in the document, the
        # "move the heading below the handoff" advice is misleading —
        # the handoff itself is what's missing. Swap the fix in the
        # diagnostic to name the real root cause so the composer adds
        # the handoff before rearranging the heading.
        plan = (
            valid_feature_plan()
            .replace(
                "### h: Handoff",
                "## Intrusive Heading\n- side note\n\n### s2: No handoff",
            )
            .replace(
                "- [ ] h: Handoff",
                "- [ ] s2: No handoff",
            )
            .replace("s1 -> h", "s1 -> s2")
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any(
                "`## Intrusive Heading`" in i
                and "no `### h: <label>` handoff block exists later" in i
                for i in issues
            ),
            (
                "Expected handoff-missing variant of the misplacement "
                f"diagnostic, got: {issues}"
            ),
        )


# ---------------------------------------------------------------------------
# `_update_fence_stack` helper — direct CommonMark §4.5 edge cases.
# ---------------------------------------------------------------------------


class UpdateFenceStackTests(unittest.TestCase):
    """Focused coverage for `_update_fence_stack`.

    The plan-level tests above exercise the helper transitively through
    `find_hard_placeholders` and `extract_stages_section`, but they
    conflate tracker behaviour with the rest of the pipeline. The tests
    here call the helper directly so a regression in any single
    CommonMark rule (length, fence character, trailing prose, backtick
    info string) surfaces with a crisp failure message.
    """

    def test_opener_pushes_on_empty_stack(self) -> None:
        stack: list[str] = []
        self.assertTrue(VALIDATOR._update_fence_stack("```", stack))
        self.assertEqual(stack, ["```"])

    def test_matching_closer_pops(self) -> None:
        stack = ["```"]
        self.assertTrue(VALIDATOR._update_fence_stack("```", stack))
        self.assertEqual(stack, [])

    def test_same_char_longer_token_also_closes(self) -> None:
        # Per CommonMark §4.5 a closer may be longer than its opener.
        stack = ["```"]
        self.assertTrue(VALIDATOR._update_fence_stack("````", stack))
        self.assertEqual(stack, [])

    def test_same_char_shorter_token_is_literal_inside_longer_fence(
        self,
    ) -> None:
        # A 3-backtick token inside a 4-backtick opener is literal
        # content, not a closer.
        stack = ["````"]
        self.assertFalse(VALIDATOR._update_fence_stack("```", stack))
        self.assertEqual(stack, ["````"])

    def test_mismatched_char_token_is_literal(self) -> None:
        # Inside a `~~~` fence, a line starting with ``` is literal.
        stack = ["~~~"]
        self.assertFalse(VALIDATOR._update_fence_stack("```", stack))
        self.assertEqual(stack, ["~~~"])

    def test_closer_with_trailing_prose_not_closer(self) -> None:
        # Any non-whitespace after the fence token disqualifies the
        # line as a closer; the stack stays as-is.
        stack = ["```"]
        self.assertFalse(
            VALIDATOR._update_fence_stack("``` trailing", stack)
        )
        self.assertEqual(stack, ["```"])

    def test_closer_with_only_trailing_whitespace_still_closes(self) -> None:
        stack = ["```"]
        self.assertTrue(VALIDATOR._update_fence_stack("```   \t", stack))
        self.assertEqual(stack, [])

    def test_backtick_opener_with_backtick_in_info_string_not_opener(
        self,
    ) -> None:
        # CommonMark §4.5: a backtick fence's info string may not
        # contain any backtick. The line falls through as literal
        # text instead of opening a fence.
        stack: list[str] = []
        self.assertFalse(
            VALIDATOR._update_fence_stack("``` python `code`", stack)
        )
        self.assertEqual(stack, [])

    def test_tilde_opener_tolerates_backtick_in_info_string(self) -> None:
        # The info-string backtick restriction applies to backtick
        # fences only; tilde fences accept any info string.
        stack: list[str] = []
        self.assertTrue(
            VALIDATOR._update_fence_stack("~~~ lang `with backticks`", stack)
        )
        self.assertEqual(stack, ["~~~"])

    def test_fence_indented_up_to_3_spaces_still_fence(self) -> None:
        stack: list[str] = []
        self.assertTrue(VALIDATOR._update_fence_stack("   ```", stack))
        self.assertEqual(stack, ["```"])

    def test_fence_indented_4_or_more_spaces_not_fence(self) -> None:
        # 4 spaces of indent would make the line an indented code
        # block under CommonMark, not a fence.
        stack: list[str] = []
        self.assertFalse(VALIDATOR._update_fence_stack("    ```", stack))
        self.assertEqual(stack, [])

    def test_plain_prose_not_a_fence_edge(self) -> None:
        stack = ["```"]
        self.assertFalse(
            VALIDATOR._update_fence_stack("some content", stack)
        )
        self.assertEqual(stack, ["```"])


# ---------------------------------------------------------------------------
# Filename validator — unchanged contract, kept as-is with light cleanup.
# ---------------------------------------------------------------------------


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

    def test_unknown_profile_in_filename_rejected(self) -> None:
        # Shape-only matches like `plan.foo.sample-task.md` must fail because
        # `foo` is not one of `{delivery, refactor, migration, exploration}`.
        issues = VALIDATOR.validate_filename(Path("plan.foo.sample-task.md"))
        self.assertEqual(len(issues), 1)
        self.assertIn(
            "is not a recognized contract profile",
            issues[0],
        )


# ---------------------------------------------------------------------------
# `_extract_section` — shared fence-aware section extractor.
# ---------------------------------------------------------------------------


class ExtractSectionTests(unittest.TestCase):
    """Direct coverage for `_extract_section`.

    The plan-level tests exercise this helper transitively through
    `extract_stages_section` / `extract_dependency_graph_section` /
    `extract_stage_claims_section`, but they conflate section-slicing
    behaviour with downstream validators. Testing the helper directly
    gives a single failure site for the "start at `## <heading>`,
    stop at the next `## <word>`, honour fence state" contract.
    """

    def test_basic_section_body_is_extracted(self) -> None:
        text = (
            "# Title\n"
            "\n"
            "## Stages\n"
            "s1 body line\n"
            "s2 body line\n"
            "\n"
            "## Verification\n"
            "- verify\n"
        )
        body = VALIDATOR._extract_section(text, "Stages")
        self.assertIsNotNone(body)
        self.assertIn("s1 body line", body)
        self.assertIn("s2 body line", body)
        self.assertNotIn("## Verification", body)
        self.assertNotIn("- verify", body)

    def test_missing_heading_returns_none(self) -> None:
        text = "# Title\n\n## Other\nbody\n"
        self.assertIsNone(VALIDATOR._extract_section(text, "Stages"))

    def test_heading_inside_fence_does_not_open_section(self) -> None:
        # A `## Stages` that only appears inside a fenced example must
        # not be picked up as the real section header; the extractor
        # should return None in that case.
        text = (
            "# Title\n"
            "\n"
            "## Sources / Rationale\n"
            "```markdown\n"
            "## Stages\n"
            "fake body inside fence\n"
            "```\n"
            "\n"
            "## Verification\n"
            "- verify\n"
        )
        self.assertIsNone(VALIDATOR._extract_section(text, "Stages"))

    def test_h2_inside_fence_does_not_close_section(self) -> None:
        # A `## Something` inside a fenced block inside Stages must NOT
        # truncate the Stages body; the body should include the fenced
        # lines verbatim.
        text = (
            "## Stages\n"
            "real line before fence\n"
            "```markdown\n"
            "## FakeHeading\n"
            "still inside fence\n"
            "```\n"
            "real line after fence\n"
            "\n"
            "## Verification\n"
            "- verify\n"
        )
        body = VALIDATOR._extract_section(text, "Stages")
        self.assertIsNotNone(body)
        self.assertIn("real line before fence", body)
        self.assertIn("## FakeHeading", body)
        self.assertIn("still inside fence", body)
        self.assertIn("real line after fence", body)
        self.assertNotIn("- verify", body)

    def test_nested_4backtick_fence_preserves_inner_3backtick_heading(
        self,
    ) -> None:
        # A 4-backtick wrapper holding a 3-backtick inner block: the
        # inner `## Heading` is inside the 4-backtick fence, so it
        # must not close the outer Stages section.
        text = (
            "## Stages\n"
            "````markdown\n"
            "```python\n"
            "## Not a real section\n"
            "```\n"
            "````\n"
            "\n"
            "## Verification\n"
            "- verify\n"
        )
        body = VALIDATOR._extract_section(text, "Stages")
        self.assertIsNotNone(body)
        self.assertIn("## Not a real section", body)
        self.assertNotIn("- verify", body)


# ---------------------------------------------------------------------------
# Fence-aware metadata / heading / content-block / ledger regressions.
# ---------------------------------------------------------------------------


class FenceAwareRegressionTests(unittest.TestCase):
    """Regression coverage for Round 3 CF-1 fence-awareness fixes.

    Each test appends a fenced example to the baseline `valid_feature_plan`
    and verifies that the fenced example does NOT satisfy the presence
    check (metadata, heading, content block field, ledger entry) for the
    real plan body. Before the CF-1 fixes these would silently pass
    because the validator was using raw `re.search` over the full text.
    """

    def test_has_metadata_ignores_field_inside_fence(self) -> None:
        plan = valid_feature_plan()
        plan_no_field = plan.replace(
            "**Primary Success Signal:** Suggestions are cached and still correct.\n",
            "",
        )
        decoy = (
            "## Sources / Rationale\n"
            "```markdown\n"
            "**Primary Success Signal:** Not the real signal.\n"
            "```\n"
            "\n"
        )
        plan_with_decoy = plan_no_field.replace(
            "## Inputs / Context Sources",
            decoy + "## Inputs / Context Sources",
        )
        self.assertFalse(
            VALIDATOR.has_metadata(plan_with_decoy, "Primary Success Signal")
        )
        issues, _warnings = VALIDATOR.validate(plan_with_decoy)
        self.assertTrue(
            any("Primary Success Signal" in i for i in issues),
            f"Expected missing-metadata diagnostic, got: {issues}",
        )

    def test_has_heading_ignores_heading_inside_fence(self) -> None:
        plan = valid_feature_plan()
        plan_no_heading = plan.replace("## Verification\n", "")
        decoy = (
            "## Sources / Rationale\n"
            "```markdown\n"
            "## Verification\n"
            "```\n"
            "\n"
        )
        plan_with_decoy = plan_no_heading.replace(
            "## Decision Points", decoy + "## Decision Points"
        )
        self.assertFalse(VALIDATOR.has_heading(plan_with_decoy, "Verification"))

    def test_extract_metadata_value_skips_fenced_example(self) -> None:
        # The decoy **must** sit *before* the real `**Contract Profile:**`
        # line — otherwise a non-fence-aware implementation (naive
        # `re.search` with MULTILINE) would still pick up the real
        # value first and the test would pass regardless of
        # fence-awareness. Placing the decoy ahead of the real line
        # gives the test genuine discriminating power: a regression
        # would flip the value from `delivery` to `migration`.
        plan = valid_feature_plan()
        decoy = (
            "## Sources / Rationale\n"
            "```markdown\n"
            "**Contract Profile:** `migration`\n"
            "```\n"
            "\n"
        )
        plan_with_decoy = decoy + plan
        # Sanity check: a naive non-fence-aware scan matches the
        # decoy's fenced line first. This cements the "why" for the
        # test — without fence awareness the validator returns the
        # wrong value.
        naive_pattern = re.compile(
            r"^\*\*Contract Profile:\*\*[ \t]*(\S.*?)\s*$",
            flags=re.MULTILINE,
        )
        naive_match = naive_pattern.search(plan_with_decoy)
        self.assertIsNotNone(naive_match)
        self.assertEqual(
            naive_match.group(1).strip().strip("`"),  # type: ignore[union-attr]
            "migration",
        )
        # The real fence-aware implementation must see `delivery`
        # (the value outside the fence), not the decoy's `migration`.
        value = VALIDATOR.extract_metadata_value(
            plan_with_decoy, "Contract Profile"
        )
        self.assertEqual(value, "delivery")

    def test_split_content_blocks_ignores_fenced_subheader(self) -> None:
        # A fenced example inside a stage body that contains
        # `### s99: example` must NOT split the real block in two.
        plan = valid_feature_plan()
        decoy = (
            "**Exit Signal:** Cache behavior is ready for validation.\n"
            "````markdown\n"
            "```markdown\n"
            "### s99: Example nested stage\n"
            "**Purpose:** Fake.\n"
            "```\n"
            "````\n"
        )
        plan_with_decoy = plan.replace(
            "**Exit Signal:** Cache behavior is ready for validation.\n",
            decoy,
        )
        issues, _warnings = VALIDATOR.validate(plan_with_decoy)
        self.assertEqual(
            issues,
            [],
            f"Unexpected issues from fenced `### s99` decoy: {issues}",
        )

    def test_field_present_ignores_label_inside_fenced_example(self) -> None:
        # Remove the real `**Files:**` from s1, then add a fenced
        # example that quotes `**Files:**`. The recommended-field
        # warning must still fire.
        plan = valid_feature_plan()
        plan_no_files = plan.replace(
            "**Files:** `src/search/SearchBox.tsx`, `src/search/__tests__/SearchBox.test.tsx`\n",
            "",
        )
        decoy = (
            "**Purpose:** Introduce cached suggestion behavior.\n"
            "````markdown\n"
            "```markdown\n"
            "**Files:** `src/fake.ts`\n"
            "```\n"
            "````\n"
        )
        plan_with_decoy = plan_no_files.replace(
            "**Purpose:** Introduce cached suggestion behavior.\n",
            decoy,
        )
        _issues, warnings = VALIDATOR.validate(plan_with_decoy)
        self.assertTrue(
            any("missing recommended field `**Files:**`" in w for w in warnings),
            f"Expected recommended-field warning, got: {warnings}",
        )

    def test_checklist_label_inside_fence_does_not_satisfy_requirement(
        self,
    ) -> None:
        plan = valid_feature_plan()
        decoy_block = (
            "### s1: Add cache behavior\n"
            "**Purpose:** Introduce cached suggestion behavior.\n"
            "**Files:** `src/search/SearchBox.tsx`\n"
            "**Exit Signal:** Cache behavior is ready for validation.\n"
            "````markdown\n"
            "```markdown\n"
            "**Checklist:**\n"
            "- [ ] fake item\n"
            "```\n"
            "````\n"
        )
        original_block = (
            "### s1: Add cache behavior\n"
            "**Purpose:** Introduce cached suggestion behavior.\n"
            "**Files:** `src/search/SearchBox.tsx`, `src/search/__tests__/SearchBox.test.tsx`\n"
            "**Exit Signal:** Cache behavior is ready for validation.\n"
            "**Checklist:**\n"
            "- [ ] Add cache-aware fetch behavior\n"
            "- [ ] Confirm the cache boundary is still valid\n"
        )
        plan_with_decoy = plan.replace(original_block, decoy_block)
        issues, _warnings = VALIDATOR.validate(plan_with_decoy)
        self.assertTrue(
            any(
                "missing the `**Checklist:**` label line" in i for i in issues
            ),
            f"Expected missing-Checklist-label diagnostic, got: {issues}",
        )

    def test_stage_claims_ledger_skips_fenced_entries(self) -> None:
        plan = valid_feature_plan()
        real_ledger = (
            "- [ ] s1: Add cache behavior\n"
            "- [ ] h: Handoff\n"
        )
        decoy_ledger = (
            "```markdown\n"
            "- [ ] s42: fake ledger entry from a doc example\n"
            "```\n"
            "\n"
            "- [ ] s1: Add cache behavior\n"
            "- [ ] h: Handoff\n"
        )
        plan_with_decoy = plan.replace(real_ledger, decoy_ledger)
        issues, _warnings = VALIDATOR.validate(plan_with_decoy)
        self.assertFalse(
            any("s42" in i for i in issues),
            f"Fenced ledger entry leaked into validation: {issues}",
        )


# ---------------------------------------------------------------------------
# `_find_misplaced_heading_in_stages` — direct coverage for both branches.
# ---------------------------------------------------------------------------


class FindMisplacedHeadingInStagesTests(unittest.TestCase):
    """Direct unit coverage for `_find_misplaced_heading_in_stages`.

    The plan-level tests earlier in this module verify the user-facing
    diagnostic wording. These tests call the helper directly so each
    branch of the return tuple (`handoff_after` True / False / None)
    has a focused assertion.
    """

    def test_returns_none_when_stages_is_empty_and_nothing_follows(
        self,
    ) -> None:
        text = "## Stages\n\n## Verification\n- verify\n"
        self.assertIsNone(
            VALIDATOR._find_misplaced_heading_in_stages(text)
        )

    def test_handoff_after_true_when_handoff_exists_later(self) -> None:
        text = (
            "## Stages\n"
            "\n"
            "### s1: Real stage\n"
            "**Purpose:** work.\n"
            "\n"
            "## Oops\n"
            "body\n"
            "\n"
            "### h: Handoff\n"
            "**Purpose:** done.\n"
        )
        result = VALIDATOR._find_misplaced_heading_in_stages(text)
        self.assertIsNotNone(result)
        line_no, heading, handoff_after = result
        self.assertEqual(heading, "Oops")
        self.assertTrue(handoff_after)
        self.assertGreater(line_no, 0)

    def test_handoff_after_false_when_no_handoff_in_document(self) -> None:
        text = (
            "## Stages\n"
            "\n"
            "### s1: Real stage\n"
            "**Purpose:** work.\n"
            "\n"
            "## Oops\n"
            "body\n"
        )
        result = VALIDATOR._find_misplaced_heading_in_stages(text)
        self.assertIsNotNone(result)
        _line_no, heading, handoff_after = result
        self.assertEqual(heading, "Oops")
        self.assertFalse(handoff_after)


# ---------------------------------------------------------------------------
# Duplicate required heading diagnostic.
# ---------------------------------------------------------------------------


class DuplicateRequiredHeadingTests(unittest.TestCase):
    def test_duplicate_verification_heading_rejected(self) -> None:
        plan = valid_feature_plan()
        plan_with_dup = plan.replace(
            "## Verification\n", "## Verification\n", 1
        )
        # Inject a second `## Verification` right before `## Decision Points`.
        plan_with_dup = plan_with_dup.replace(
            "## Decision Points",
            "## Verification\n- duplicate body.\n\n## Decision Points",
        )
        issues, _warnings = VALIDATOR.validate(plan_with_dup)
        self.assertTrue(
            any(
                "`## Verification` appears 2 times" in i for i in issues
            ),
            f"Expected duplicate-heading diagnostic, got: {issues}",
        )

    def test_duplicate_stages_heading_rejected(self) -> None:
        # The more dangerous duplicate: two `## Stages` sections silently
        # truncate the first and hide its content from the validator.
        plan = valid_feature_plan()
        plan_with_dup = plan.replace(
            "## Decision Points",
            "## Stages\n- another body.\n\n## Decision Points",
        )
        issues, _warnings = VALIDATOR.validate(plan_with_dup)
        self.assertTrue(
            any("`## Stages` appears 2 times" in i for i in issues),
            f"Expected duplicate-heading diagnostic, got: {issues}",
        )


# ---------------------------------------------------------------------------
# `+` bullet hard-placeholder coverage.
# ---------------------------------------------------------------------------


class PlusBulletPlaceholderTests(unittest.TestCase):
    def test_plus_bullet_implement_later_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "- [ ] Add cache-aware fetch behavior",
            "+ implement later",
            1,
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("implement later" in i for i in issues),
            f"Expected hard-placeholder diagnostic for `+` bullet, got: {issues}",
        )

    def test_plus_bullet_with_checkbox_implement_later_rejected(self) -> None:
        plan = valid_feature_plan().replace(
            "- [ ] Add cache-aware fetch behavior",
            "+ [ ] implement later",
            1,
        )
        issues, _warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("implement later" in i for i in issues),
            f"Expected hard-placeholder diagnostic for `+ [ ]` bullet, got: {issues}",
        )


# ---------------------------------------------------------------------------
# Unclosed code fence warning.
# ---------------------------------------------------------------------------


class UnclosedFenceWarningTests(unittest.TestCase):
    def test_plain_plan_has_no_unclosed_fence_warning(self) -> None:
        _issues, warnings = VALIDATOR.validate(valid_feature_plan())
        self.assertFalse(
            any("Unclosed code fence" in w for w in warnings),
            f"Unexpected unclosed-fence warning on valid plan: {warnings}",
        )

    def test_unclosed_backtick_fence_warns(self) -> None:
        plan = (
            valid_feature_plan()
            + "\n```python\nstill open at EOF\n"
        )
        _issues, warnings = VALIDATOR.validate(plan)
        self.assertTrue(
            any("Unclosed code fence" in w for w in warnings),
            f"Expected unclosed-fence warning, got: {warnings}",
        )

    def test_nested_closed_fence_does_not_warn(self) -> None:
        plan = valid_feature_plan().replace(
            "## Decision Points",
            (
                "## Sources / Rationale\n"
                "````markdown\n"
                "```python\n"
                "inner\n"
                "```\n"
                "````\n"
                "\n"
                "## Decision Points"
            ),
        )
        _issues, warnings = VALIDATOR.validate(plan)
        self.assertFalse(
            any("Unclosed code fence" in w for w in warnings),
            f"Expected no unclosed-fence warning for nested closed fences: {warnings}",
        )


# ---------------------------------------------------------------------------
# Line-ending normalisation — CR-only edge case.
# ---------------------------------------------------------------------------


class CRLineEndingsTests(unittest.TestCase):
    def test_bare_cr_line_endings_accepted(self) -> None:
        # Classic-Mac style (bare `\r`) files still exist in some export
        # pipelines; `validate()` normalises them to `\n` at entry so
        # downstream regex and fence tracking see LF-only input.
        plan = valid_feature_plan().replace("\n", "\r")
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [])
        self.assertEqual(warnings, [])


# ---------------------------------------------------------------------------
# `UpdateFenceStackTests` gaps — longer fences, tilde closers, non-h2 lines.
# ---------------------------------------------------------------------------


class UpdateFenceStackAdditionalTests(unittest.TestCase):
    """Extra edge cases for `_update_fence_stack`.

    The main `UpdateFenceStackTests` class above covers the CommonMark
    §4.5 baseline (match, shorter, longer, trailing prose, backtick
    info string). This complement targets gaps called out in Round 3:
    five- and six-backtick openers, bare-tilde open/close, and the
    "line is not a fence" path which the main suite only exercises
    with trivially-shaped prose.
    """

    def test_5_backtick_opener_and_5_backtick_closer_match(self) -> None:
        stack: list[str] = []
        self.assertTrue(
            VALIDATOR._update_fence_stack("`````", stack)
        )
        self.assertEqual(stack, ["`````"])
        self.assertTrue(
            VALIDATOR._update_fence_stack("`````", stack)
        )
        self.assertEqual(stack, [])

    def test_6_backtick_closer_closes_5_backtick_opener(self) -> None:
        # Longer-than-opener closer is allowed per CommonMark §4.5.
        stack = ["`````"]
        self.assertTrue(
            VALIDATOR._update_fence_stack("``````", stack)
        )
        self.assertEqual(stack, [])

    def test_5_backtick_closer_does_not_close_6_backtick_opener(self) -> None:
        # Shorter closer stays literal inside the longer fence.
        stack = ["``````"]
        self.assertFalse(
            VALIDATOR._update_fence_stack("`````", stack)
        )
        self.assertEqual(stack, ["``````"])

    def test_bare_tilde_opener_pushes(self) -> None:
        stack: list[str] = []
        self.assertTrue(VALIDATOR._update_fence_stack("~~~", stack))
        self.assertEqual(stack, ["~~~"])

    def test_bare_tilde_closer_pops_matching_opener(self) -> None:
        stack = ["~~~"]
        self.assertTrue(VALIDATOR._update_fence_stack("~~~", stack))
        self.assertEqual(stack, [])

    def test_backtick_closer_does_not_close_tilde_opener(self) -> None:
        stack = ["~~~"]
        self.assertFalse(VALIDATOR._update_fence_stack("```", stack))
        self.assertEqual(stack, ["~~~"])

    def test_non_fence_line_leaves_stack_unchanged_outside_fence(self) -> None:
        stack: list[str] = []
        self.assertFalse(VALIDATOR._update_fence_stack("## A heading", stack))
        self.assertEqual(stack, [])
        self.assertFalse(VALIDATOR._update_fence_stack("plain prose", stack))
        self.assertEqual(stack, [])

    def test_crlf_remnant_after_closer_is_tolerated(self) -> None:
        # `validate()` normalises CRLF/CR to LF at entry, so
        # `_update_fence_stack` should never see a CR in practice.
        # Still, document the intrinsic behaviour: Python's
        # `str.strip()` (used inside the helper) treats `\r` as
        # whitespace, so a stray CRLF remnant after the token does
        # NOT disqualify the line as a closer. This is the graceful
        # direction — any mismatch would leak a partially-open fence
        # into every downstream scan, which is worse than the benign
        # "close a fence with a CR-contaminated line" that
        # normalisation prevents anyway.
        stack = ["```"]
        self.assertTrue(VALIDATOR._update_fence_stack("```\r", stack))
        self.assertEqual(stack, [])

    def test_tilde_indented_3_spaces_still_fence(self) -> None:
        stack: list[str] = []
        self.assertTrue(VALIDATOR._update_fence_stack("   ~~~", stack))
        self.assertEqual(stack, ["~~~"])

    def test_tilde_indented_4_spaces_not_fence(self) -> None:
        stack: list[str] = []
        self.assertFalse(VALIDATOR._update_fence_stack("    ~~~", stack))
        self.assertEqual(stack, [])


# ---------------------------------------------------------------------------
# Round 4 regressions — `parse_dag` fence-priority rule + inline-label stripping
# ---------------------------------------------------------------------------


class ParseDagFencePriorityTests(unittest.TestCase):
    """Round 4 Major fix (CF-1): ONLY mermaid-info-string fences are authoritative.

    Earlier versions set `fence_present` for *any* fenced block in
    the Dependency Graph section, which silently suppressed
    plain-arrow prose whenever the composer happened to include a
    ```text``` / ```bash``` illustration alongside the real DAG.
    These tests pin the corrected behaviour so it cannot silently
    regress.
    """

    def test_non_mermaid_fence_does_not_suppress_prose(self) -> None:
        # `text` fence sits alongside plain-arrow prose. The prose
        # edges must still be parsed; the fence body is ignored.
        section = (
            "```text\n"
            "Example illustration only — not a real DAG.\n"
            "x -> y\n"
            "```\n"
            "\n"
            "s1 -> s2\n"
            "s2 -> h\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertIn(("s1", "s2"), edges)
        self.assertIn(("s2", "h"), edges)
        # The illustration inside ```text``` must NOT leak edges.
        self.assertNotIn(("x", "y"), edges)
        self.assertNotIn("x", nodes)
        self.assertNotIn("y", nodes)

    def test_mermaid_fence_is_authoritative_over_prose(self) -> None:
        # Prose outside a mermaid fence is ignored — the fence body
        # is the single source of truth. This preserves the original
        # protection against preamble sentences like
        # "point s1 -> s2 into the fence" that would otherwise emit
        # phantom edges.
        section = (
            "```mermaid\n"
            "flowchart TD\n"
            "  s1[Setup] --> s2[Work]\n"
            "  s2 --> h[Handoff]\n"
            "```\n"
            "\n"
            "Also note: z -> w in some earlier draft.\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertIn(("s1", "s2"), edges)
        self.assertIn(("s2", "h"), edges)
        # Prose outside the mermaid fence must NOT leak edges.
        self.assertNotIn(("z", "w"), edges)
        self.assertNotIn("z", nodes)
        self.assertNotIn("w", nodes)

    def test_mermaid_and_non_mermaid_fence_still_mermaid_authoritative(
        self,
    ) -> None:
        # When BOTH a mermaid fence and an illustration fence live in
        # the same section, the mermaid body remains authoritative:
        # prose outside every fence is suppressed, and the
        # illustration body is skipped as a plain code block.
        section = (
            "```text\n"
            "pseudo: a -> b\n"
            "```\n"
            "\n"
            "```mermaid\n"
            "  s1 --> s2\n"
            "  s2 --> h\n"
            "```\n"
            "\n"
            "Also: q -> r elsewhere.\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertNotIn(("a", "b"), edges)
        self.assertNotIn(("q", "r"), edges)

    def test_no_fence_falls_back_to_plain_arrow_prose(self) -> None:
        section = "s1 -> s2\ns2 -> h\n"
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertIn(("s1", "s2"), edges)
        self.assertIn(("s2", "h"), edges)

    def test_full_plan_with_text_fence_and_prose_dag_validates(self) -> None:
        # End-to-end: a plan whose `## Dependency Graph` section mixes
        # a `text` illustration fence + plain-arrow prose must pass
        # validation. Pre-fix, the text fence would suppress prose
        # and the DAG would be reported as empty.
        plan = valid_feature_plan().replace(
            "## Dependency Graph\ns1 -> h\n",
            (
                "## Dependency Graph\n"
                "```text\n"
                "illustration: box -> box\n"
                "```\n"
                "\n"
                "s1 -> h\n"
            ),
        )
        issues, warnings = VALIDATOR.validate(plan)
        self.assertEqual(issues, [], f"Expected no issues; got: {issues}")
        self.assertEqual(warnings, [], f"Expected no warnings; got: {warnings}")


class ParseDagInlineLabelTests(unittest.TestCase):
    """Round 4 Minor fix (DF-2): strip mermaid `-- text -->` inline labels.

    Mermaid supports edge labels in two forms: pipe form (`-->|text|`)
    and inline form (`-- text -->`). The pipe form was already
    stripped; the inline form produced a phantom `text` node plus a
    spurious edge, breaking strict DAG id validation on otherwise-
    valid plans.
    """

    def test_inline_label_does_not_emit_phantom_node(self) -> None:
        section = (
            "```mermaid\n"
            "  s1 -- build widget --> s2\n"
            "  s2 --> h\n"
            "```\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertIn(("s1", "s2"), edges)
        self.assertIn(("s2", "h"), edges)
        # No phantom nodes from the label words.
        self.assertNotIn("build", nodes)
        self.assertNotIn("widget", nodes)

    def test_inline_label_single_word_stripped(self) -> None:
        section = (
            "```mermaid\n"
            "  s1 -- go --> s2\n"
            "  s2 --> h\n"
            "```\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertNotIn("go", nodes)

    def test_chain_with_two_inline_labels_parses_cleanly(self) -> None:
        section = (
            "```mermaid\n"
            "  s1 -- step one --> s2 -- step two --> h\n"
            "```\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertIn(("s1", "s2"), edges)
        self.assertIn(("s2", "h"), edges)
        self.assertNotIn("step", nodes)
        self.assertNotIn("one", nodes)
        self.assertNotIn("two", nodes)

    def test_plain_arrow_without_label_still_parses(self) -> None:
        # Make sure the inline-label stripping regex doesn't also eat
        # bare `-->` edges. Pre-regex guard via `(?!>)` prevents that.
        section = (
            "```mermaid\n"
            "  s1 --> s2\n"
            "  s2 --> h\n"
            "```\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        self.assertEqual(edges.count(("s1", "s2")), 1)

    def test_pipe_and_inline_labels_both_stripped(self) -> None:
        section = (
            "```mermaid\n"
            "  s1 -->|trigger| s2\n"
            "  s2 -- release candidate --> h\n"
            "```\n"
        )
        nodes, edges = VALIDATOR.parse_dag(section)
        self.assertEqual(set(nodes.keys()), {"s1", "s2", "h"})
        for phantom in ("trigger", "release", "candidate"):
            self.assertNotIn(phantom, nodes)


# ---------------------------------------------------------------------------
# Round 4 regressions — `_find_misplaced_heading_in_stages` content-block scope
# ---------------------------------------------------------------------------


class MisplacedHeadingContentBlockScopeTests(unittest.TestCase):
    """Round 4 Minor fix (CF-2): tighten `seen_content_block` trigger.

    The scan used to accept any `^###\\s+\\S` line as a content
    block. A transient sub-heading like `### Smoke Tests` under
    Stages would flip the flag on and suppress the misplaced-`##`
    diagnostic, even though Stages had not yet grown any real
    `### <id>: <label>` block. The regression cases below pin the
    corrected behaviour: only headers that match the canonical
    `### <id>: <label>` shape arm the diagnostic's content-after
    branch.
    """

    def test_non_content_block_sub_heading_does_not_count_as_content(
        self,
    ) -> None:
        # `## Stages` is followed immediately by a `### Smoke Tests`
        # sub-heading (not a content block), then a misplaced `## Oops`
        # heading, then the real content blocks. Pre-fix, the sub-
        # heading incorrectly set `seen_content_block = True`, which
        # *fired* the misplaced-heading diagnostic describing
        # content before Oops. Post-fix, `seen_content_block` stays
        # False — but the lookahead still sees the real `### s1:`
        # and `### h:` blocks later, so the diagnostic fires via the
        # "content-after" branch instead. Either way the diagnostic
        # must appear; the test confirms the validator still catches
        # the misplacement without being misled by the sub-heading.
        plan = valid_feature_plan().replace(
            "## Stages\n\n### s1: Add cache behavior",
            "## Stages\n\n### Smoke Tests\n\n## Oops\n\n### s1: Add cache behavior",
        )
        issues, _warnings = VALIDATOR.validate(plan)
        # The diagnostic wording is "Top-level heading `## Oops`
        # appears inside the `## Stages` body ... silently truncates
        # Stages". Match on the distinctive substring that is unique
        # to this check (so the test doesn't accidentally pass on an
        # unrelated "unknown heading" message).
        self.assertTrue(
            any(
                "appears inside the `## Stages` body" in i
                and "silently truncates Stages" in i
                for i in issues
            ),
            f"Expected a misplaced-heading diagnostic pointing at "
            f"`## Oops` truncating Stages, got: {issues}",
        )

    def test_find_misplaced_helper_ignores_non_content_sub_heading(
        self,
    ) -> None:
        # Direct unit on `_find_misplaced_heading_in_stages`: a
        # Stages section that contains ONLY a `### Smoke Tests`
        # sub-heading (no `### <id>: <label>` blocks) followed by
        # `## Later` must be treated as "no content yet" — so the
        # helper falls into the lookahead branch, which finds no
        # `### <id>: <label>` afterwards either, and returns None
        # (silent). Pre-fix the sub-heading would have armed the
        # content-before branch, firing a spurious diagnostic.
        plan = textwrap.dedent(
            """\
            ## Stages

            ### Smoke Tests
            Just a note.

            ## Later

            ### Other

            Prose afterwards.
            """
        )
        self.assertIsNone(
            VALIDATOR._find_misplaced_heading_in_stages(plan),
            "Non-canonical `### Smoke Tests` should not count as a "
            "content block for misplaced-heading detection.",
        )

    def test_find_misplaced_helper_uses_canonical_content_header(
        self,
    ) -> None:
        # Positive: a real `### s1: Setup` *does* arm the diagnostic.
        plan = textwrap.dedent(
            """\
            ## Stages

            ### s1: Setup
            Body.

            ## Early Graveyard

            ### h: Handoff
            Body.
            """
        )
        result = VALIDATOR._find_misplaced_heading_in_stages(plan)
        self.assertIsNotNone(result)
        assert result is not None  # type narrowing for mypy
        _line, heading, _handoff_after = result
        self.assertEqual(heading, "Early Graveyard")


if __name__ == "__main__":
    unittest.main()
