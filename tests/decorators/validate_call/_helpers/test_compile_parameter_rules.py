import inspect
from typing import Callable

import pytest

# Tested helper and exceptions
from simplibs.exception import ParamError
from simplibs.rules import HasLength, greater_than, is_integer
from simplibs.rules.base_class import Rule
from simplibs.rules.containers import AllOf
from simplibs.rules.predicates.logic import UserRule
from simplibs.validate.decorators.validate_call._helpers.compile_parameter_rules import (
    compile_parameter_rules,
)


def sample_func(a: int, b: str, c=10, *, _validate_call: bool = True):
    pass


def unannotated_func(a, b):
    pass


def variadic_func(a: int, *args: int, **kwargs: str):
    pass


def variadic_union_func(*sources: inspect.Parameter | Callable):
    pass


def unannotated_variadic_func(*args, **kwargs):
    pass


# ============================================================================
# Regular parameters
# ============================================================================

def test_compile_parameter_rules_annotated_parameters() -> None:
    """Verify rules are compiled for annotated parameters and bypass parameter is skipped."""
    sig = inspect.signature(sample_func)
    compiled = compile_parameter_rules(sample_func, sig, check=None, overrides={})

    assert "a" in compiled
    assert "b" in compiled
    assert "c" not in compiled  # Unannotated parameter is skipped
    assert "_validate_call" not in compiled  # Reserved bypass switch is not compiled
    assert isinstance(compiled["a"], Rule)


def test_compile_parameter_rules_with_check_filter() -> None:
    """Verify check filter restricts compilation to specified parameters only."""
    sig = inspect.signature(sample_func)
    compiled = compile_parameter_rules(sample_func, sig, check=("a",), overrides={})

    assert "a" in compiled
    assert "b" not in compiled


def test_compile_parameter_rules_with_overrides() -> None:
    """Verify overrides combine with existing annotations via AllOf and wrap plain callables."""
    sig = inspect.signature(sample_func)
    override_rule = greater_than(0)
    custom_pred = lambda x: x > 0

    compiled = compile_parameter_rules(
        sample_func,
        sig,
        check=None,
        overrides={"a": override_rule, "c": custom_pred},
    )

    # Parameter 'a' has both annotation (int) and override (greater_than) -> must be AllOf
    assert isinstance(compiled["a"], AllOf)

    # Parameter 'c' had no annotation, received callable override -> wrapped in UserRule
    assert "c" in compiled
    assert isinstance(compiled["c"], UserRule)


def test_compile_parameter_rules_raises_on_checked_param_without_rule() -> None:
    """Verify ParamError is raised when check filter names a parameter without annotation or override."""
    sig = inspect.signature(unannotated_func)

    with pytest.raises(ParamError) as exc_info:
        compile_parameter_rules(unannotated_func, sig, check=("a",), overrides={})

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_RULE_FOR_PARAM_ERROR"


def test_compile_parameter_rules_regular_parameter_rule_describes_the_value_itself() -> None:
    """Verify a regular parameter keeps its annotation as-is (no collection wrapping)."""
    sig = inspect.signature(variadic_func)
    compiled = compile_parameter_rules(variadic_func, sig, check=None, overrides={})

    assert compiled["a"].is_valid(5) is True
    assert compiled["a"].is_valid("5") is False
    assert compiled["a"].is_valid((5,)) is False  # a is a single int, not a tuple


# ============================================================================
# Variadic parameters (*args / **kwargs)
# ============================================================================

def test_compile_parameter_rules_var_positional_annotation_describes_each_item() -> None:
    """Verify `*args: int` compiles to a rule that accepts a tuple of ints."""
    sig = inspect.signature(variadic_func)
    compiled = compile_parameter_rules(variadic_func, sig, check=None, overrides={})

    assert "args" in compiled
    assert compiled["args"].is_valid((1, 2, 3)) is True
    assert compiled["args"].is_valid(()) is True  # No extra arguments is valid
    assert compiled["args"].is_valid((1, "x")) is False  # One bad item is enough


def test_compile_parameter_rules_var_positional_rejects_non_tuple() -> None:
    """Verify the compiled `*args` rule describes a tuple, not a bare item."""
    sig = inspect.signature(variadic_func)
    compiled = compile_parameter_rules(variadic_func, sig, check=None, overrides={})

    assert compiled["args"].is_valid(5) is False


def test_compile_parameter_rules_var_keyword_annotation_describes_each_value() -> None:
    """Verify `**kwargs: str` compiles to a rule that accepts a dict of strings."""
    sig = inspect.signature(variadic_func)
    compiled = compile_parameter_rules(variadic_func, sig, check=None, overrides={})

    assert "kwargs" in compiled
    assert compiled["kwargs"].is_valid({"x": "a", "y": "b"}) is True
    assert compiled["kwargs"].is_valid({}) is True
    assert compiled["kwargs"].is_valid({"x": 1}) is False


def test_compile_parameter_rules_var_positional_with_union_annotation() -> None:
    """Verify a union annotation is applied to every item of `*args`."""
    sig = inspect.signature(variadic_union_func)
    compiled = compile_parameter_rules(variadic_union_func, sig, check=None, overrides={})

    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_ONLY)
    assert compiled["sources"].is_valid((len, param)) is True
    assert compiled["sources"].is_valid((len, 5)) is False


def test_compile_parameter_rules_var_positional_override_applies_to_whole_tuple() -> None:
    """Verify an override on `*args` sees the whole tuple and combines via AllOf."""
    sig = inspect.signature(variadic_func)
    compiled = compile_parameter_rules(
        variadic_func,
        sig,
        check=None,
        overrides={"args": HasLength(min_length=1)},
    )

    assert isinstance(compiled["args"], AllOf)
    assert compiled["args"].is_valid((1,)) is True
    assert compiled["args"].is_valid(()) is False  # Collection-level rule fires
    assert compiled["args"].is_valid(("x",)) is False  # Item-level annotation still applies


def test_compile_parameter_rules_unannotated_variadic_parameters_are_skipped() -> None:
    """Verify unannotated `*args` / `**kwargs` get no rule."""
    sig = inspect.signature(unannotated_variadic_func)
    compiled = compile_parameter_rules(unannotated_variadic_func, sig, check=None, overrides={})

    assert "args" not in compiled
    assert "kwargs" not in compiled


def test_compile_parameter_rules_checked_unannotated_variadic_raises() -> None:
    """Verify naming an unannotated `*args` in check without an override raises ParamError."""
    sig = inspect.signature(unannotated_variadic_func)

    with pytest.raises(ParamError) as exc_info:
        compile_parameter_rules(unannotated_variadic_func, sig, check=("args",), overrides={})

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_RULE_FOR_PARAM_ERROR"
