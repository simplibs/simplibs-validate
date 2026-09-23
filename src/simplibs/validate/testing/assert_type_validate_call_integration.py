from typing import Any
from simplibs.exception import ValidationError
from simplibs.exception.testing import (
    assert_function_raises,
    assert_function_valid_input,
)
from simplibs.validate import validate_call


def assert_type_validate_call_integration(
    subtests: Any,
    type_: Any,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that `type_`, used as a real @validate_call parameter annotation,
    accepts every valid value and rejects every invalid one with ValidationError.

    Kept as a separate, independently callable blade — rather than inlined into
    assert_type_contract — so a caller who only cares about the annotation-wiring
    behavior, without re-running the full Rule contract battery, can call it
    directly.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        type_: The validated type under test.
        valid_values: Values expected to pass through the decorated function.
        invalid_values: Values expected to raise ValidationError through it.
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.
    """

    @validate_call
    def _probe(value: type_) -> Any:
        return value

    for index, val in enumerate(valid_values):
        assert_function_valid_input(
            subtests,
            _probe,
            valid_params=(val,),
            verbose=verbose,
            intro=f"{intro}test_validate_call_pass_#index_{index}_",
        )

    for index, val in enumerate(invalid_values):
        assert_function_raises(
            subtests,
            _probe,
            invalid_params=(val,),
            exception_type=ValidationError,
            verbose=verbose,
            intro=f"{intro}test_validate_call_raises_#index_{index}_",
        )


_DESIGN_NOTES = """
# assert_type_validate_call_integration (Annotation-Wiring Contract Blade)

## Purpose
Verifies that a validated type is not just correct as a decomposed `Rule` in
isolation, but actually behaves correctly when used the way every real caller
will use it: as the annotation on a `@validate_call`-decorated function's
parameter.

---

## 1. Why This Exists Separately From assert_type_contract

`build_typing_rule(type_)` (used by `assert_type_contract` to obtain the
`Rule`) and `@validate_call`'s own internal annotation compiler are two
independent code paths that decompose the same `Annotated` construct. A bug
specific to the `@validate_call` wiring (argument binding, parameter-name
resolution, rule execution, ...) would never surface from Rule-level testing
alone. This blade closes that gap.

Splitting it into its own module keeps concerns separated: a caller who only
wants to sanity-check the annotation wiring can call this directly without
re-asserting the full `Rule` contract battery.

---

## 2. Design Choices

* **Throwaway Probe Function**: `_probe` exists purely to give `type_`
  somewhere to be a real annotation. Its body is a no-op passthrough — the
  only thing under test is whether `@validate_call` accepts/rejects the
  argument correctly.
* **Toolkit Reuse**: Delegates to `simplibs-exception`'s own
  `assert_function_valid_input`/`assert_function_raises`, exactly like every
  other assertion blade in this ecosystem.
* **No Diagnostic-Field Checking**: Unlike `assert_rule_build_exception`,
  this blade does not inspect the raised `ValidationError`'s fields — that
  content is already covered by `assert_rule_contract` at the `Rule` level.
"""