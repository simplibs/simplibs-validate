"""Tests for assert_type_contract — pinning the description of the decomposed rule."""
from typing import Annotated, Any

import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ValidationError
from simplibs.rules import Rule
from simplibs.validate.testing import assert_type_contract


class PositiveIntRule(Rule):
    """Rule checking positive integer values, with a pinned description."""

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, int) and value > 0

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Value must be positive integer.",
            expected="Integer > 0.",
            how_to_fix="Provide positive integer.",
            label=value_name,
            value=value,
            context=context,
            error_name="NOT_POSITIVE_INT",
            exception=ValueError,
        )

    def describe(self) -> str:
        return "positive integer"


PositiveInt = Annotated[int, PositiveIntRule()]


def test_expected_description_matching_passes(subtests):
    assert_type_contract(
        subtests,
        type_=PositiveInt,
        valid_values=[1, 42],
        invalid_values=[0, -1],
        # `Annotated[int, rule]` is decomposed into the type check and the rule, joined by AllOf
        expected_description="int & positive integer",
        verbose=False,
    )


def test_expected_description_mismatch_fails(subtests):
    with pytest.raises((AssertionError, Failed), match="describe"):
        assert_type_contract(
            subtests,
            type_=PositiveInt,
            valid_values=[1],
            invalid_values=[0],
            expected_description="natural number",
            verbose=False,
        )


def test_description_is_not_checked_when_not_given(subtests):
    """Verify that omitting expected_description keeps the old behavior (generic contract only)."""
    assert_type_contract(
        subtests,
        type_=PositiveInt,
        valid_values=[1],
        invalid_values=[0],
        verbose=False,
    )
