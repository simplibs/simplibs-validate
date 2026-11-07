import typing
from collections.abc import Callable, Iterable
from typing import Annotated, ForwardRef, Literal, Optional, Union

import pytest

# Tested helper
from simplibs.rules import greater_than
from simplibs.validate.decorators.validate_call._helpers.needs_annotation_resolution import (
    needs_annotation_resolution,
)


# ============================================================================
# Needs resolution
# ============================================================================

@pytest.mark.parametrize(
    "annotation",
    [
        "int",                                  # plain string
        "list[int]",                            # string holding a generic
        ForwardRef("Node"),                     # explicit ForwardRef
        list["Node"],                           # string nested in a generic
        dict[str, "Node"],                      # ... in a later argument
        Optional["Node"],                       # typing.Optional of a forward ref
        Union["A", int],                        # typing.Union with a forward ref
        Iterable["Node"],                       # collections.abc generic
        Callable[["A"], int],                   # in the argument list of Callable
        Callable[[int], "B"],                   # in the return of Callable
        Annotated["Node", "meta"],              # the type part of Annotated
        list[list["Node"]],                     # deeply nested
        tuple["Node", ...],                     # tuple with Ellipsis
    ],
)
def test_needs_annotation_resolution_true(annotation) -> None:
    """Verify strings and forward references are detected, also when nested."""
    assert needs_annotation_resolution(annotation) is True


# ============================================================================
# Does not need resolution
# ============================================================================

@pytest.mark.parametrize(
    "annotation",
    [
        int,
        str,
        None,
        list[int],
        dict[str, int],
        tuple[int, ...],
        int | None,
        Optional[int],
        Iterable[int],
        Callable[[int], str],
        Callable[..., int],
        type,
        typing.Any,
    ],
)
def test_needs_annotation_resolution_false_for_real_objects(annotation) -> None:
    """Verify annotations that are already objects are left alone."""
    assert needs_annotation_resolution(annotation) is False


def test_needs_annotation_resolution_literal_values_are_not_references() -> None:
    """Verify the strings inside Literal[...] are values, not names."""
    assert needs_annotation_resolution(Literal["a", "b"]) is False
    assert needs_annotation_resolution(Literal["a"] | None) is False
    assert needs_annotation_resolution(list[Literal["x"]]) is False


def test_needs_annotation_resolution_annotated_metadata_is_not_a_reference() -> None:
    """Verify free-form Annotated metadata (including strings) is ignored."""
    assert needs_annotation_resolution(Annotated[int, "some text"]) is False
    assert needs_annotation_resolution(Annotated[int, "a", "b"]) is False


def test_needs_annotation_resolution_rule_instance_is_not_a_reference() -> None:
    """Verify a Rule used directly as an annotation is not mistaken for a string."""
    assert needs_annotation_resolution(greater_than(0)) is False
    assert needs_annotation_resolution(Annotated[int, greater_than(0)]) is False


def test_needs_annotation_resolution_literal_beside_forward_reference() -> None:
    """Verify a real reference next to a Literal is still found."""
    assert needs_annotation_resolution(Union[Literal["a"], "Node"]) is True
