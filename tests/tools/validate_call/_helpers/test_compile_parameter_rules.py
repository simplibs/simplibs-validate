import inspect
import pytest

# Tested helper and exceptions
from simplibs.validate.exceptions import ParamError
from simplibs.validate.rules import greater_than, is_integer
from simplibs.validate.rules.base_class import Rule
from simplibs.validate.rules.containers import AllOf
from simplibs.validate.rules.predicates.logic import UserRule
from simplibs.validate.tools.validate_call._helpers.compile_parameter_rules import (
    compile_parameter_rules,
)


def sample_func(a: int, b: str, c=10, *, validate: bool = True):
    pass


def unannotated_func(a, b):
    pass


def test_compile_parameter_rules_annotated_parameters() -> None:
    """Verify rules are compiled for annotated parameters and bypass parameter is skipped."""
    sig = inspect.signature(sample_func)
    compiled = compile_parameter_rules(sample_func, sig, check=None, overrides={})

    assert "a" in compiled
    assert "b" in compiled
    assert "c" not in compiled  # Unannotated parameter is skipped
    assert "validate" not in compiled  # Reserved bypass switch is not compiled
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