from typing import Any
from simplibs.rules import build_typing_rule
from simplibs.rules.testing import assert_rule_contract

# Internal import within simplibs-validate testing package
from .assert_type_validate_call_integration import (
    assert_type_validate_call_integration,
)


def assert_type_contract(
    subtests: Any,
    type_: Any,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    expected_error_name: str | None = None,
    expected_exception_type: type[Exception] | None = None,
    sample_label: str = "target_var",
    sample_context: str = "test_execution_context",
    check_value: bool = True,
    check_validate_call: bool = True,
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None:
    """Master orchestrator for testing a validated_type()-built type against the
    same contract every Rule must satisfy, plus its actual wiring into @validate_call.

    Decomposes `type_` (an Annotated[type_, *rules] construct, whether built by
    validated_type() or by hand) into the Rule tree it represents, and delegates the
    entire deterministic battery — is_valid()/__call__, the validate() mode matrix,
    and build_exception()'s diagnostic card contract — straight to simplibs-rules'
    own assert_rule_contract. On top of that, it optionally verifies the type
    actually works when used as a real function annotation under @validate_call,
    which is the one thing rule-level contract testing alone cannot catch: a type
    whose decomposed Rule is perfectly correct in isolation can still be wired
    incorrectly into the annotation-driven call path.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        type_: The validated type under test — an Annotated[type_, *rules] construct.
        valid_values: Values that must satisfy the type.
        invalid_values: Values that must fail the type and produce a diagnostic
            exception.
        expected_error_name: If provided, asserted against every raised
            exception's error_name.
        expected_exception_type: If provided, asserted against every raised
            exception's wrapped `exception` attribute.
        sample_label: The value_name used when probing build_exception().
        sample_context: The context used when probing build_exception().
        check_value: If True, asserts that exc.value strictly matches the raw
            invalid value. Set to False for types whose rules transform values
            before failure.
        check_validate_call: If True, additionally builds a throwaway function
            annotated with `type_`, decorates it with @validate_call, and verifies
            every valid value is accepted and every invalid value raises
            ValidationError through that real call path — not just through the
            decomposed Rule directly. Delegated to
            assert_type_validate_call_integration.
        verbose: If True, registers individual checks as isolated pytest subtests.
        intro: Optional prefix string added to the generated subtest identity name.
        deep_check: If True, triggers exhaustive diagnostic field inspection in the
            build_exception check.
    """
    # 1. Decompose the Annotated construct into the Rule tree it represents,
    #    then reuse simplibs-rules' own contract battery wholesale — this function
    #    adds nothing new at the Rule level, only at the annotation-wiring level below.
    rule = build_typing_rule(type_)

    assert_rule_contract(
        subtests,
        rule,
        valid_values,
        invalid_values,
        expected_error_name=expected_error_name,
        expected_exception_type=expected_exception_type,
        sample_label=sample_label,
        sample_context=sample_context,
        check_value=check_value,
        verbose=verbose,
        intro=intro,
        deep_check=deep_check,
    )

    # 2. Optional: verify the type actually works wired into @validate_call —
    #    the one integration path decomposition testing alone can't exercise.
    if check_validate_call:
        assert_type_validate_call_integration(
            subtests,
            type_,
            valid_values,
            invalid_values,
            verbose=verbose,
            intro=intro,
        )


_DESIGN_NOTES = """
# assert_type_contract (Validated-Type Contract Orchestrator)

## Purpose
The single entry point for testing any type alias constructed with
`validated_type()` (or used within preset libraries like `simplibs-types`).
Deliberately thin: it decomposes the Annotated construct into a Rule via
`build_typing_rule` and hands the entire deterministic battery straight to
`simplibs-rules`' own `assert_rule_contract` — nothing about
is_valid/validate/build_exception is reimplemented here. The one thing this
adds is delegating to a second blade, `assert_type_validate_call_integration`,
which exercises the type through a real `@validate_call`-decorated function.

---

## 1. Why This Is Worth Having

With many custom or preset types across applications, writing a full contract
test by hand for each one — decomposing the annotation, wiring subtests,
checking both the Rule and the `@validate_call` path — is repetitive,
error-prone boilerplate. A single `assert_type_contract(...)` call replaces
that, ensuring complete compliance with one function call.

## 2. Why the `@validate_call` Check Is Not Redundant

`build_typing_rule(type_)` and `@validate_call`'s own internal compiler both
decompose `Annotated[type_, *rules]`, but they are two separate code paths. A
bug in how `validate_call` extracts and applies a parameter's annotation
(as opposed to a bug in the Rule itself) would pass every Rule-level check and
still break in real execution. `check_validate_call=True` (the default) catches
exactly that class of bug.

## 3. Reused vs. New

* **Reused wholesale**: `is_valid`/`__call__`, `validate()` mode matrix,
  `build_exception()` diagnostics, optional constructor `ParamError` sweep —
  all via `assert_rule_contract`, once `type_` is decomposed into its `Rule`.
* **New here**: only wiring in the `@validate_call` integration blade,
  delegated entirely to `assert_type_validate_call_integration` rather than
  inlined.
"""