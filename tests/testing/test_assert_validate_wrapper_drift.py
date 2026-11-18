"""Tests for assert_validate_wrapper — drift in both directions, exception type and subtest names."""
from contextlib import contextmanager
from typing import Any

import pytest

from simplibs.exception import ParamError, ValidationError
from simplibs.validate.testing import assert_validate_wrapper


def _factory(*, min_value: int | None = None):
    """Stands in for a *_rule factory with one rule parameter."""


def _wrapper(value: Any, *, min_value=None, value_name=None, context=None, return_bool=False, return_value=False):
    """A wrapper that follows its factory; invalid values (not int) raise ParamError."""
    if isinstance(value, int):
        return value if return_value else True
    if return_bool:
        return False
    raise ParamError("not an int")


class RecordingSubtests:
    """Records the names of the subtests; a failing check is recorded and the test goes on."""

    def __init__(self) -> None:
        self.names: list[str] = []

    @contextmanager
    def test(self, name: str):
        self.names.append(name)
        yield


def _assert_wrapper(wrapper, **overrides):
    kwargs = dict(
        validate_func=wrapper,
        rule_factory=_factory,
        valid_value=1,
        invalid_value="x",
        expected_exception_type=ParamError,
        verbose=False,
    )
    kwargs.update(overrides)
    assert_validate_wrapper(RecordingSubtests(), **kwargs)


def test_compliant_wrapper_passes():
    _assert_wrapper(_wrapper)


def test_extra_parameter_on_the_wrapper_is_drift():
    """Verify that a parameter added to the wrapper and forgotten on the factory is reported."""

    def drifted(value: Any, *, min_value=None, extra=None, value_name=None, context=None,
                return_bool=False, return_value=False):
        return _wrapper(value, min_value=min_value, return_bool=return_bool, return_value=return_value)

    with pytest.raises(AssertionError, match=r"\['extra'\]"):
        _assert_wrapper(drifted)


def test_var_args_and_kwargs_on_the_wrapper_are_not_drift():
    """Verify that *args / **kwargs are not counted as extra parameters."""

    def flexible(value: Any, *args, min_value=None, value_name=None, context=None,
                 return_bool=False, return_value=False, **kwargs):
        return _wrapper(value, return_bool=return_bool, return_value=return_value)

    _assert_wrapper(flexible)


def test_a_differently_named_value_parameter_is_not_drift():
    """Verify that the first parameter (the validated value) is allowed whatever it is called."""

    def renamed(candidate: Any, *, min_value=None, value_name=None, context=None,
                return_bool=False, return_value=False):
        return _wrapper(candidate, return_bool=return_bool, return_value=return_value)

    _assert_wrapper(renamed)


def test_wrong_exception_type_is_reported_with_both_names():
    """Verify that a wrapper failing with a native exception instead of the expected one is caught."""

    def raises_native(value: Any, *, min_value=None, value_name=None, context=None,
                      return_bool=False, return_value=False):
        if isinstance(value, int):
            return value if return_value else True
        if return_bool:
            return False
        raise TypeError("native error")

    with pytest.raises(AssertionError, match=r"to raise ValidationError, got TypeError"):
        _assert_wrapper(raises_native, expected_exception_type=ValidationError)


def test_a_subclass_of_the_expected_exception_is_accepted():
    """Verify the isinstance check: ParamError is a ValidationError, so the default expectation accepts it."""
    _assert_wrapper(_wrapper, expected_exception_type=ValidationError)


def test_intro_is_placed_before_the_wrapper_name():
    """Verify the subtest names: `{intro}[wrapper name] check`."""
    subtests = RecordingSubtests()

    assert_validate_wrapper(
        subtests,
        validate_func=_wrapper,
        rule_factory=_factory,
        valid_value=1,
        invalid_value="x",
        expected_exception_type=ParamError,
        intro="case 1: ",
    )

    assert subtests.names[0] == "case 1: [_wrapper] signature_rule_params"
    assert "case 1: [_wrapper] signature_no_extra_params" in subtests.names
