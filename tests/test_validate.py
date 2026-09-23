"""Tests for the main validate() orchestrator function."""

import pytest
from simplibs.exception import ValidationError
from simplibs.rules.base_class import Rule
from simplibs.validate.validate import validate


class DummyPassRule(Rule):
    """Dummy rule that always passes."""

    def is_valid(self, value: object) -> bool:
        return True

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        return ValueError("Should not be raised")


class DummyFailRule(Rule):
    """Dummy rule that always fails."""

    def is_valid(self, value: object) -> bool:
        return False

    def build_exception(
        self,
        value: object,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:
        label = value_name or "value"
        ctx = f" [{context}]" if context else ""
        return ValueError(f"Custom Rule Exception for {label}{ctx} with {value!r}")


# ==============================================================================
# 1. EVALUATION FOR RULE INSTANCES (Delegation to Rule.validate)
# ==============================================================================

def test_validate_rule_success(subtests) -> None:
    """Verify successful validation when passing a Rule instance."""
    rule = DummyPassRule()

    with subtests.test("default_return_true"):
        assert validate(100, rule) is True

    with subtests.test("return_value_true"):
        assert validate(100, rule, return_value=True) == 100


def test_validate_rule_failure_returns_bool() -> None:
    """Verify that the orchestrator returns False for a failed Rule when return_bool=True."""
    rule = DummyFailRule()
    assert validate(100, rule, return_bool=True) is False


def test_validate_rule_failure_raises_custom_exception() -> None:
    """Verify that the orchestrator fully delegates exception creation to rule.build_exception."""
    rule = DummyFailRule()
    with pytest.raises(ValueError, match="Custom Rule Exception for param_x \\[test_ctx\\] with 'invalid'"):
        validate("invalid", rule, value_name="param_x", context="test_ctx")


# ==============================================================================
# 2. EVALUATION FOR PLAIN CALLABLES AND LAMBDAS
# ==============================================================================

def test_validate_callable_success(subtests) -> None:
    """Verify correct evaluation for a plain function / lambda on success."""
    is_even = lambda x: x % 2 == 0

    with subtests.test("default_return_true"):
        assert validate(4, is_even) is True

    with subtests.test("return_value_true"):
        assert validate(4, is_even, return_value=True) == 4


def test_validate_callable_failure_returns_bool() -> None:
    """Verify that a callable failure returns False when return_bool=True."""
    is_even = lambda x: x % 2 == 0
    assert validate(5, is_even, return_bool=True) is False


def test_validate_callable_failure_raises_validate_error() -> None:
    """Verify that callable failure constructs a structured ValidationError via build_validation_error."""
    is_even = lambda x: x % 2 == 0

    with pytest.raises(ValidationError) as exc_info:
        validate(5, is_even, value_name="number", context="unit_test")

    err = exc_info.value
    assert err.label == "number"
    assert err.context == "unit_test"
    assert err.value == 5


def test_validate_callable_passthrough_exception() -> None:
    """Verify that if a user callable raises an exception internally, the orchestrator propagates it."""
    def buggy_callable(x):
        raise AttributeError("Custom internal function error")

    with pytest.raises(AttributeError, match="Custom internal function error"):
        validate("test", buggy_callable)