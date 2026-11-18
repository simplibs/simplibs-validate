import inspect
from typing import Any, Callable
from simplibs.exception import ValidationError
from simplibs.exception.testing import maybe_subtest
from simplibs.rules import Rule

# The standard control parameters of every validate_* function (the ones of Rule.validate)
_CONTROL_PARAMS = ("value_name", "context", "return_bool", "return_value")


def assert_validate_wrapper(
    subtests: Any,
    *,
    validate_func: Callable[..., Any],
    rule_factory: Callable[..., Rule],
    valid_value: Any,
    invalid_value: Any,
    sample_params: dict[str, Any] | None = None,
    expected_exception_type: type[Exception] = ValidationError,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that a validate_* entrypoint correctly wraps its rule factory and Rule.validate.

    Validates:
    1. Signature compatibility between rule_factory and validate_func, in both directions.
    2. Presence of standard Rule.validate control parameters.
    3. Proper delegation of return_bool and return_value logic.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        validate_func: The high-level wrapper function (e.g. validate_str).
        rule_factory: The underlying rule composition factory (e.g. string_rule).
        valid_value: A value expected to pass validation under sample_params.
        invalid_value: A value expected to fail validation under sample_params.
        sample_params: Optional dict of rule-specific constraints to pass during tests.
        expected_exception_type: The exception that an invalid value must raise.
            Defaults to ValidationError.
        verbose: Enables isolated pytest subtest tracking for each check phase.
        intro: Optional prefix string placed before the generated `[validate_func name] ` prefix.
    """
    sample_params = sample_params or {}
    name = getattr(validate_func, "__name__", type(validate_func).__name__)
    factory_name = getattr(rule_factory, "__name__", type(rule_factory).__name__)
    prefix = f"{intro}[{name}] "

    # 1. Signature alignment checks
    rule_sig = inspect.signature(rule_factory)
    val_sig = inspect.signature(validate_func)

    with maybe_subtest(subtests, name=f"{prefix}signature_rule_params", verbose=verbose):
        for param_name in rule_sig.parameters:
            assert param_name in val_sig.parameters, (
                f"Param '{param_name}' from {factory_name} is missing in {name}."
            )

    with maybe_subtest(subtests, name=f"{prefix}signature_control_params", verbose=verbose):
        for ctrl_param in _CONTROL_PARAMS:
            assert ctrl_param in val_sig.parameters, (
                f"Control param '{ctrl_param}' is missing in {name}."
            )

    with maybe_subtest(subtests, name=f"{prefix}signature_no_extra_params", verbose=verbose):
        # The wrapper is the factory plus the control parameters plus the value it validates
        # (its first parameter); anything else was added to the wrapper and forgotten on the factory.
        value_param = next(iter(val_sig.parameters), None)
        allowed = set(rule_sig.parameters) | set(_CONTROL_PARAMS) | {value_param}
        extra = [
            param_name
            for param_name, param in val_sig.parameters.items()
            if param_name not in allowed
            and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        assert not extra, (
            f"Params {extra} of {name} are not parameters of {factory_name}."
        )

    # 2. Valid value execution checks
    with maybe_subtest(subtests, name=f"{prefix}valid_default_returns_true", verbose=verbose):
        assert validate_func(valid_value, **sample_params) is True, (
            f"Expected {name}({valid_value!r}) to return True by default."
        )

    with maybe_subtest(subtests, name=f"{prefix}valid_returns_value", verbose=verbose):
        assert validate_func(valid_value, return_value=True, **sample_params) == valid_value, (
            f"Expected {name}({valid_value!r}, return_value=True) to return the original value."
        )

    # 3. Invalid value execution checks
    with maybe_subtest(subtests, name=f"{prefix}invalid_returns_bool_false", verbose=verbose):
        assert validate_func(invalid_value, return_bool=True, **sample_params) is False, (
            f"Expected {name}({invalid_value!r}, return_bool=True) to return False."
        )

    with maybe_subtest(subtests, name=f"{prefix}invalid_raises_exception", verbose=verbose):
        caught: Exception | None = None
        # noinspection PyBroadException
        try:
            validate_func(invalid_value, return_bool=False, **sample_params)
        except Exception as error:
            caught = error
        assert caught is not None, (
            f"Expected {name}({invalid_value!r}) to raise an exception when return_bool=False."
        )
        assert isinstance(caught, expected_exception_type), (
            f"Expected {name}({invalid_value!r}) to raise {expected_exception_type.__name__}, "
            f"got {type(caught).__name__}."
        )


_DESIGN_NOTES = """
# assert_validate_wrapper (Wrapper ↔ Factory Consistency Audit)

## Purpose
Verifies that a high-level `validate_*` function stays in step with the `*_rule` factory it wraps
(`validate_string` / `string_rule`), without re-testing which values pass: that is the job of
`assert_rule_contract` on the composed rule.

---

## 1. Drift Detection in Both Directions
The wrapper is the factory plus the four control parameters plus the value it validates.
* `signature_rule_params` — every parameter of the factory is also on the wrapper.
* `signature_control_params` — the four control parameters are on the wrapper.
* `signature_no_extra_params` — the wrapper has nothing else: a parameter added to the wrapper and
  forgotten on the factory is drift too. The first parameter of the wrapper (the value) and
  `*args` / `**kwargs` are not counted.

## 2. Delegation
A valid value gives `True` by default and itself with `return_value=True`. An invalid value gives
`False` with `return_bool=True` and raises otherwise. The exception must be an instance of
`expected_exception_type` (`ValidationError` by default), not just any exception, so a wrapper
that fails with a native `TypeError` is caught.

## 3. One Value Pair
Exactly one valid and one invalid value: the tool asks how a value is routed, not which values pass.
`sample_params` are keyword arguments for the factory, chosen so that `valid_value` passes with them.

## 4. Reporting
Every check runs through `maybe_subtest` with the prefix `{intro}[validate_func name] `. The names
of the older subtests (`signature_rule_params`, ...) are kept.
"""
