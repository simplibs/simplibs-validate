import inspect
from typing import Annotated, Literal, Optional

import pytest

# Tested helper and exceptions
from simplibs.exception import ParamError
from simplibs.validate.decorators.validate_call._helpers.resolve_signature import (
    resolve_signature,
)


class Defined:
    """Module-level class the string annotations below refer to."""


def real_annotations(a: int, b: list[int], c=1) -> None: ...
def string_annotations(a: "int", b: "str" = "x") -> "int": ...
def return_only(a: int) -> "str": ...
def nested_reference(a: list["Defined"]): ...
def optional_reference(a: Optional["Defined"] = None): ...
def string_union(a: "int | None" = None): ...
def annotated_reference(a: Annotated["int", "meta"]): ...
def variadic_strings(*args: "int", **kwargs: "str"): ...
def literal_and_annotated(mode: Literal["a", "b"], x: Annotated[int, "text"]): ...
def mixed(a: int, b: "int") -> None: ...
def missing_name(a: "NoSuchNameAnywhere"): ...
def broken_syntax(a: "list[int"): ...
def unannotated(a, b=2): ...


# ============================================================================
# Nothing to resolve
# ============================================================================

def test_resolve_signature_real_annotations_are_unchanged() -> None:
    """Verify a signature without strings comes back equal to inspect.signature."""
    assert resolve_signature(real_annotations) == inspect.signature(real_annotations)


def test_resolve_signature_unannotated_function_is_unchanged() -> None:
    """Verify unannotated parameters are not touched."""
    assert resolve_signature(unannotated) == inspect.signature(unannotated)


def test_resolve_signature_literal_and_annotated_strings_are_not_evaluated() -> None:
    """Verify Literal values and Annotated metadata strings never trigger resolution."""
    original = inspect.signature(literal_and_annotated)
    resolved = resolve_signature(literal_and_annotated)

    assert resolved == original
    assert resolved.parameters["mode"].annotation is original.parameters["mode"].annotation


# ============================================================================
# Resolving
# ============================================================================

def test_resolve_signature_resolves_string_parameters_and_return() -> None:
    """Verify string annotations become real objects."""
    resolved = resolve_signature(string_annotations)

    assert resolved.parameters["a"].annotation is int
    assert resolved.parameters["b"].annotation is str
    assert resolved.return_annotation is int


def test_resolve_signature_keeps_defaults_and_kinds() -> None:
    """Verify only annotations change — defaults, names and kinds are kept."""
    resolved = resolve_signature(string_annotations)

    assert resolved.parameters["b"].default == "x"
    assert list(resolved.parameters) == ["a", "b"]


def test_resolve_signature_return_only() -> None:
    """Verify a string return annotation alone is resolved."""
    resolved = resolve_signature(return_only)

    assert resolved.parameters["a"].annotation is int
    assert resolved.return_annotation is str


def test_resolve_signature_nested_reference() -> None:
    """Verify a reference nested inside a generic is resolved."""
    assert resolve_signature(nested_reference).parameters["a"].annotation == list[Defined]


def test_resolve_signature_optional_reference() -> None:
    """Verify Optional["Defined"] is resolved."""
    assert resolve_signature(optional_reference).parameters["a"].annotation == Optional[Defined]


def test_resolve_signature_string_union() -> None:
    """Verify a union written inside a string is resolved."""
    assert resolve_signature(string_union).parameters["a"].annotation == (int | None)


def test_resolve_signature_annotated_keeps_metadata() -> None:
    """Verify Annotated keeps its metadata after the type is resolved."""
    assert resolve_signature(annotated_reference).parameters["a"].annotation == Annotated[int, "meta"]


def test_resolve_signature_variadic_parameters() -> None:
    """Verify string annotations of *args and **kwargs are resolved."""
    resolved = resolve_signature(variadic_strings)

    assert resolved.parameters["args"].annotation is int
    assert resolved.parameters["kwargs"].annotation is str


def test_resolve_signature_touches_only_what_needed_resolving() -> None:
    """Verify real annotations stay as they are (for instance `-> None` is not NoneType)."""
    original = inspect.signature(mixed)
    resolved = resolve_signature(mixed)

    assert resolved.parameters["a"].annotation is original.parameters["a"].annotation
    assert resolved.parameters["b"].annotation is int
    assert resolved.return_annotation is None


# ============================================================================
# Failures
# ============================================================================

def test_resolve_signature_missing_name_not_strict_returns_none() -> None:
    """Verify a name that does not exist yet gives None, so the caller can retry later."""
    assert resolve_signature(missing_name) is None


def test_resolve_signature_missing_name_strict_raises() -> None:
    """Verify strict mode reports the missing name as ParamError."""
    with pytest.raises(ParamError) as exc_info:
        resolve_signature(missing_name, strict=True)

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"


def test_resolve_signature_invalid_syntax_raises_even_when_not_strict() -> None:
    """Verify an annotation that can never be evaluated is reported immediately."""
    with pytest.raises(ParamError) as exc_info:
        resolve_signature(broken_syntax)

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"


def test_resolve_signature_name_defined_later_is_found() -> None:
    """Verify the same function resolves once the name exists."""
    def late(a: "_LateDefinedName"): ...

    assert resolve_signature(late) is None

    globals()["_LateDefinedName"] = int
    try:
        assert resolve_signature(late).parameters["a"].annotation is int
    finally:
        del globals()["_LateDefinedName"]
