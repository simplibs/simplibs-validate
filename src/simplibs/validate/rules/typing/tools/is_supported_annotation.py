from typing import Any
# Outers
from ....exceptions import ParamError
from ..build_typing_rule import build_typing_rule


def is_supported_annotation(annotation: Any) -> bool:
    """Check whether a given type annotation is supported by the validation engine.

    This recursively inspects the annotation (including nested generic arguments)
    by attempting to compile it via `build_typing_rule`.

    Args:
        annotation: Any type annotation, class, or typing construct to inspect.

    Returns:
        True if the annotation can be successfully compiled into a Rule,
        False if it contains unsupported constructs (e.g. bare TypeVar,
        unparsed ForwardRef, or unknown objects).
    """
    try:
        build_typing_rule(annotation)
        return True
    except ParamError:
        return False