import inspect
import pytest
from simplibs.validate.exceptions import ParamError
from simplibs.validate.rules.base_class import Rule
from simplibs.validate.rules import IsInstance
from simplibs.validate.tools.validate_call._helpers import compile_parameter_rules


def sample_func(a: int, b: str, c=10):
    pass


def unannotated_func(a, b):
    pass


def test_compile_parameter_rules_all_annotated() -> None:
    """Verify rules are compiled for all annotated parameters by default."""
    sig = inspect.signature(sample_func)
    compiled = compile_parameter_rules(sample_func, sig, check=None, overrides={})

    assert "a" in compiled
    assert "b" in compiled
    assert "c" not in compiled  # unannotated parameter skipped
    assert isinstance(compiled["a"], Rule)


def test_compile_parameter_rules_with_check_filter() -> None:
    """Verify check filter restricts compilation to explicitly specified parameters."""
    sig = inspect.signature(sample_func)
    compiled = compile_parameter_rules(sample_func, sig, check=("a",), overrides={})

    assert "a" in compiled
    assert "b" not in compiled


def test_compile_parameter_rules_with_overrides() -> None:
    """Verify overrides combine with annotations or create new parameter rules."""
    sig = inspect.signature(sample_func)
    override_rule = IsInstance(int)
    compiled = compile_parameter_rules(
        sample_func,
        sig,
        check=None,
        overrides={"a": override_rule, "c": lambda x: x > 0},
    )

    assert "a" in compiled
    assert "c" in compiled  # 'c' now has a rule via override


def test_compile_parameter_rules_raises_on_checked_param_without_rule() -> None:
    """Verify ParamError is raised when check names a parameter with no annotation or override."""
    sig = inspect.signature(unannotated_func)
    with pytest.raises(ParamError) as exc_info:
        compile_parameter_rules(unannotated_func, sig, check=("a",), overrides={})

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_RULE_FOR_PARAM_ERROR"