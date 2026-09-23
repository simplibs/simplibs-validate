import inspect
import pytest

# Tested function and constant
from simplibs.validate.decorators.validate_call._helpers.is_bypass_parameter import (
    BYPASS_PARAM_NAME,
)
from simplibs.validate.decorators.validate_call._helpers.should_validate import (
    should_validate,
)


def _make_bound_args(**kwargs) -> inspect.BoundArguments:
    """Helper to create inspect.BoundArguments from given keyword arguments."""
    sig = inspect.Signature(
        [
            inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY)
            for name in kwargs
        ]
    )
    return sig.bind(**kwargs)


def test_should_validate_no_bypass_parameter() -> None:
    """Verify that should_validate returns True when function has no bypass parameter regardless of bound arguments."""
    bound = _make_bound_args(x=10, y="test")

    assert should_validate(bound, has_bypass=False) is True


@pytest.mark.parametrize(
    "bypass_value, expected",
    [
        (True, True),
        (1, True),
        ("yes", True),
        (False, False),
        (0, False),
        (None, False),
    ],
)
def test_should_validate_with_bypass_parameter(
    bypass_value: object,
    expected: bool,
) -> None:
    """Verify that should_validate evaluates the truthiness of the bypass parameter when has_bypass is True."""
    bound = _make_bound_args(**{BYPASS_PARAM_NAME: bypass_value, "x": 10})

    assert should_validate(bound, has_bypass=True) is expected


def test_should_validate_with_bypass_parameter_missing_key_fallback() -> None:
    """Verify that should_validate falls back to True if bypass parameter key is missing from bound arguments."""
    bound = _make_bound_args(x=10)

    assert should_validate(bound, has_bypass=True) is True