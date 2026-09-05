from typing import Any
# Outers
from .._builders.ORIGIN_TABLE import ORIGIN_TABLE


def get_supported_origins() -> frozenset[Any]:
    """Return an immutable set of all supported typing origin constructs.

    This includes standard generic origins (list, set, dict, tuple),
    special typing constructs (Union, Optional, Literal, Callable, Type, Annotated),
    and typing equivalents from the typing module.

    Returns:
        A frozenset containing all supported typing origin keys.
    """
    return frozenset(ORIGIN_TABLE.keys())