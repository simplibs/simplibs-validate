import inspect
import pytest
from simplibs.exception import ParamError
from simplibs.rules.base_class import Rule
from simplibs.validate.decorators.validate_call._helpers import compile_return_rule


def func_with_return() -> int:
    return 42


def func_without_return():
    pass


def test_compile_return_rule_disabled() -> None:
    """Verify None is returned when check_return is False."""
    sig = inspect.signature(func_with_return)
    rule = compile_return_rule(func_with_return, sig, check_return=False)
    assert rule is None


def test_compile_return_rule_success() -> None:
    """Verify a Rule is compiled when return annotation exists and check_return is True."""
    sig = inspect.signature(func_with_return)
    rule = compile_return_rule(func_with_return, sig, check_return=True)
    assert isinstance(rule, Rule)


def test_compile_return_rule_raises_on_missing_annotation() -> None:
    """Verify ParamError is raised when check_return is True but return annotation is missing."""
    sig = inspect.signature(func_without_return)
    with pytest.raises(ParamError) as exc_info:
        compile_return_rule(func_without_return, sig, check_return=True)

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_RULE_FOR_RETURN_ERROR"