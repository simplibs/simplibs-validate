from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_not_a_dataclass_error(
    cls: Any
) -> NoReturn:
    """Raise a ParamError when validate_dataclass is applied to a non-dataclass.

    Args:
        cls: The class validate_dataclass was applied to.

    Raises:
        ParamError: Always.
    """
    # noinspection PyUnresolvedReferences
    cls_name = getattr(cls, "__qualname__", getattr(cls, "__name__", str(cls)))

    raise ParamError(
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
    )


_DESIGN_NOTES = """
# raise_not_a_dataclass_error — validate_dataclass Diagnostic Helper

## Purpose
Guards against the one ordering mistake this decorator cannot recover
from: being applied to a class that isn't (yet) a dataclass. Since
decorators apply bottom-up, `@validate_dataclass` above `@dataclass` is
correct; the reverse order leaves no dataclass-generated __init__ to wrap
and would otherwise fail with a confusing, unrelated error deeper inside
compile_parameter_rules instead of a clear, actionable one here.
"""