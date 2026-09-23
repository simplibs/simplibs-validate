import inspect
import pytest

# Tested function
from simplibs.validate.decorators.validate_call._helpers.is_bypass_parameter import (
    is_bypass_parameter,
)


def _make_param(name: str, annotation=inspect.Parameter.empty) -> inspect.Parameter:
    """Helper to create inspect.Parameter instances with specific name and annotation."""
    return inspect.Parameter(
        name=name,
        kind=inspect.Parameter.KEYWORD_ONLY,
        annotation=annotation,
    )


@pytest.mark.parametrize(
    "param, expected",
    [
        # Happy path - reserved bypass switch
        (_make_param("_validate_call", inspect.Parameter.empty), True),
        (_make_param("_validate_call", bool), True),
        # Escape hatches - named "_validate_call" but with non-bool annotation
        (_make_param("_validate_call", int), False),
        (_make_param("_validate_call", str), False),
        (_make_param("_validate_call", list[str]), False),
        # Ordinary parameters (including "validate" which is no longer reserved)
        (_make_param("validate", bool), False),
        (_make_param("x", inspect.Parameter.empty), False),
        (_make_param("x", bool), False),
        (_make_param("data", dict), False),
    ],
)
def test_is_bypass_parameter(param: inspect.Parameter, expected: bool) -> None:
    """Verify that is_bypass_parameter correctly identifies reserved bypass parameters."""
    assert is_bypass_parameter(param) is expected