import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.validate.exceptions import ParamError
from simplibs.validate.tools.validate_dataclass._validations import (
    raise_not_a_dataclass_error,
)


class RegularClass:
    """Mock non-dataclass."""


class AnotherRegularClass:
    """Mock non-dataclass."""


@pytest.mark.parametrize(
    "cls",
    [
        RegularClass,
        AnotherRegularClass,
    ],
)
def test_raise_not_a_dataclass_error_contract(subtests, cls) -> None:
    """Verify raise_not_a_dataclass_error produces a well-formed ParamError card."""

    def raising_wrapper(target_cls):
        raise_not_a_dataclass_error(target_cls)

    cls_name = getattr(cls, "__qualname__", getattr(cls, "__name__", str(cls)))

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(cls,),
        exception_type=ParamError,
        error_name="VALIDATE_DATACLASS_NOT_A_DATACLASS_ERROR",
        label="cls",
        expected="A class decorated with @dataclasses.dataclass.",
        value=cls,
        problem=(
            f"Class '{cls_name}' is not a dataclass.",
            "@validate_dataclass requires @dataclass to have already generated its __init__.",
        ),
        how_to_fix=(
            f"Add @dataclasses.dataclass above @validate_dataclass on {cls_name}.",
            "Ensure the decorators apply bottom-up so @dataclass runs first.",
        ),
        verbose=False,
    )