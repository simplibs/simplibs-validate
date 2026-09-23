import inspect
from typing import Any, Callable
from simplibs.exception.testing import maybe_subtest
from simplibs.rules import Rule


def assert_validate_wrapper(
    subtests: Any,
    *,
    validate_func: Callable[..., Any],
    rule_factory: Callable[..., Rule],
    valid_value: Any,
    invalid_value: Any,
    sample_params: dict[str, Any] | None = None,
    verbose: bool = True,
) -> None:
    """Verify that a validate_* entrypoint correctly wraps its rule factory and Rule.validate.

    Validates:
    1. Signature compatibility between rule_factory and validate_func.
    2. Presence of standard Rule.validate control parameters.
    3. Proper delegation of return_bool and return_value logic.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        validate_func: The high-level wrapper function (e.g. validate_str).
        rule_factory: The underlying rule composition factory (e.g. string_rule).
        valid_value: A value expected to pass validation under sample_params.
        invalid_value: A value expected to fail validation under sample_params.
        sample_params: Optional dict of rule-specific constraints to pass during tests.
        verbose: Enables isolated pytest subtest tracking for each check phase.
    """
    sample_params = sample_params or {}
    intro = f"[{validate_func.__name__}] "

    # 1. Signature alignment checks
    rule_sig = inspect.signature(rule_factory)
    val_sig = inspect.signature(validate_func)

    with maybe_subtest(subtests, name=f"{intro}signature_rule_params", verbose=verbose):
        for param_name in rule_sig.parameters:
            assert param_name in val_sig.parameters, (
                f"Param '{param_name}' from {rule_factory.__name__} is missing in {validate_func.__name__}."
            )

    with maybe_subtest(subtests, name=f"{intro}signature_control_params", verbose=verbose):
        control_params = {"value_name", "context", "return_bool", "return_value"}
        for ctrl_param in control_params:
            assert ctrl_param in val_sig.parameters, (
                f"Control param '{ctrl_param}' is missing in {validate_func.__name__}."
            )

    # 2. Valid value execution checks
    with maybe_subtest(subtests, name=f"{intro}valid_default_returns_true", verbose=verbose):
        assert validate_func(valid_value, **sample_params) is True, (
            f"Expected {validate_func.__name__}({valid_value!r}) to return True by default."
        )

    with maybe_subtest(subtests, name=f"{intro}valid_returns_value", verbose=verbose):
        assert validate_func(valid_value, return_value=True, **sample_params) == valid_value, (
            f"Expected {validate_func.__name__}({valid_value!r}, return_value=True) to return the original value."
        )

    # 3. Invalid value execution checks
    with maybe_subtest(subtests, name=f"{intro}invalid_returns_bool_false", verbose=verbose):
        assert validate_func(invalid_value, return_bool=True, **sample_params) is False, (
            f"Expected {validate_func.__name__}({invalid_value!r}, return_bool=True) to return False."
        )

    with maybe_subtest(subtests, name=f"{intro}invalid_raises_exception", verbose=verbose):
        raised = False
        # noinspection PyBroadException
        try:
            validate_func(invalid_value, return_bool=False, **sample_params)
        except Exception:
            raised = True

        assert raised, (
            f"Expected {validate_func.__name__}({invalid_value!r}) to raise an exception when return_bool=False."
        )