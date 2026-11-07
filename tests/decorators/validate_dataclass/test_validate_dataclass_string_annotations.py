from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import pytest

# Tested decorator and exceptions
from simplibs.exception import ParamError, ValidationError
from simplibs.rules import greater_than
from simplibs.validate.decorators.validate_dataclass.validate_dataclass import validate_dataclass

# This whole module uses `from __future__ import annotations`, so every
# field annotation below is a string until validate_dataclass resolves it.


# ============================================================================
# Dataclasses defined at module level
# ============================================================================

@validate_dataclass
@dataclass
class Point:
    x: int
    y: int


@validate_dataclass
@dataclass
class Person:
    name: str
    age: Annotated[int, greater_than(0)]


@validate_dataclass
@dataclass
class Node:
    """Refers to its own class — the name does not exist when the decorator runs."""

    value: int
    parent: Node | None = None


@validate_dataclass
@dataclass
class Holder:
    """Refers to a class defined further down the module."""

    item: LaterClass


class LaterClass:
    pass


@validate_dataclass
@dataclass(frozen=True)
class Frozen:
    value: int


# ============================================================================
# Plain string annotations
# ============================================================================

def test_validate_dataclass_string_annotations_valid() -> None:
    """Verify valid values pass with string field annotations."""
    point = Point(1, 2)

    assert (point.x, point.y) == (1, 2)


def test_validate_dataclass_string_annotations_invalid() -> None:
    """Verify an invalid value raises ValidationError."""
    with pytest.raises(ValidationError):
        Point(1, "2")


def test_validate_dataclass_string_annotations_annotated_rule() -> None:
    """Verify Annotated[...] with a rule survives resolution."""
    assert Person("Ann", 30).age == 30

    with pytest.raises(ValidationError):
        Person("Ann", -1)


def test_validate_dataclass_string_annotations_frozen_never_partially_built() -> None:
    """Verify a frozen dataclass is still validated before any field is set."""
    assert Frozen(1).value == 1

    with pytest.raises(ValidationError):
        Frozen("x")


def test_validate_dataclass_string_annotations_keyword_arguments() -> None:
    """Verify keyword construction is validated too."""
    assert Point(x=1, y=2).y == 2

    with pytest.raises(ValidationError):
        Point(x=1, y="2")


# ============================================================================
# Names that do not exist yet when the decorator runs
# ============================================================================

def test_validate_dataclass_field_of_its_own_class() -> None:
    """Verify a field annotated with the class itself works."""
    root = Node(1)
    child = Node(2, parent=root)

    assert child.parent is root
    assert root.parent is None


def test_validate_dataclass_field_of_its_own_class_is_validated() -> None:
    """Verify the self-referencing field is really checked."""
    with pytest.raises(ValidationError):
        Node(1, parent=5)

    with pytest.raises(ValidationError):
        Node("x")


def test_validate_dataclass_field_of_a_class_defined_later() -> None:
    """Verify a class defined below the dataclass is found on the first construction."""
    assert isinstance(Holder(LaterClass()).item, LaterClass)

    with pytest.raises(ValidationError):
        Holder(5)


def test_validate_dataclass_repeated_construction_after_first() -> None:
    """Verify rules built on the first construction keep working."""
    for _ in range(3):
        assert Node(1, Node(0)).value == 1


# ============================================================================
# check / overrides and failures
# ============================================================================

def test_validate_dataclass_string_annotations_check_filter() -> None:
    """Verify `check` restricts validation to the named fields."""

    @validate_dataclass(check=("x",))
    @dataclass
    class Partial:
        x: int
        y: int

    assert Partial(1, "anything").x == 1

    with pytest.raises(ValidationError):
        Partial("bad", 1)


def test_validate_dataclass_string_annotations_overrides() -> None:
    """Verify `overrides` combine with a string annotation."""

    @validate_dataclass(overrides={"count": greater_than(0)})
    @dataclass
    class Counter:
        count: int

    assert Counter(1).count == 1

    with pytest.raises(ValidationError):
        Counter(0)


def test_validate_dataclass_unresolvable_name_is_reported_on_first_construction() -> None:
    """Verify decoration succeeds and construction raises a clear ParamError."""

    @validate_dataclass
    @dataclass
    class Broken:
        value: DoesNotExistAnywhere  # noqa: F821

    with pytest.raises(ParamError) as exc_info:
        Broken(1)

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"
