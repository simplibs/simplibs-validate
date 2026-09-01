"""Tests for the assert_rule_raise_invalid function."""

from typing import Any
import pytest
from _pytest.outcomes import Failed

from simplibs.validate.exceptions import ValidateError
from simplibs.validate.rules.base_class import Rule
from simplibs.validate.testing.asserts.assert_rule_raise_invalid import (
    assert_rule_raise_invalid,
)


# --- Mock Rules for Testing ---

class DummyValidRule(Rule):
    """Correct rule requiring evaluation."""
    def is_valid(self, value: Any) -> bool:
        return value == "valid"

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidateError:
        return ValidateError(
            problem="Value is invalid",
            expected="Value must be valid",
            how_to_fix="Fix value",
            label=value_name,
            value=value,
            context=context,
        )


class DummyTypeMismatchRule(Rule):
    """Rule returning a different exception type on the second build_exception call."""
    def __init__(self):
        self._call_count = 0

    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> Exception:
        self._call_count += 1
        # First call in assertor returns TypeError (as expected_exc)
        if self._call_count == 1:
            return TypeError("Expected type")
        # Second call inside raise_invalid returns ValueError (creating a mismatch!)
        return ValueError("Raised type")


# --- Tests ---

def test_assert_rule_raise_invalid_success(subtests):
    """Verify that a correct rule reliably passes the raise_invalid check."""
    rule = DummyValidRule()
    assert_rule_raise_invalid(
        subtests,
        rule=rule,
        invalid_values=["invalid_1", 123, None],
    )


def test_assert_rule_raise_invalid_fails_on_type_mismatch(subtests):
    """Verify failure when raise_invalid raises a different exception type than build_exception."""
    rule = DummyTypeMismatchRule()
    with pytest.raises((AssertionError, Failed)):
        assert_rule_raise_invalid(
            subtests,
            rule=rule,
            invalid_values=["invalid"],
            verbose=False,
        )


def test_assert_rule_raise_invalid_fails_when_no_exception_raised(subtests, monkeypatch):
    """Verify failure when raise_invalid fails to raise any exception."""
    rule = DummyValidRule()

    # Simulate situation where raise_invalid does not raise an exception
    import simplibs.validate.testing.asserts.assert_rule_raise_invalid as target_module
    monkeypatch.setattr(target_module, "raise_invalid", lambda val, r: None)

    with pytest.raises((AssertionError, Failed)):
        assert_rule_raise_invalid(
            subtests,
            rule=rule,
            invalid_values=["invalid"],
            verbose=False,
        )