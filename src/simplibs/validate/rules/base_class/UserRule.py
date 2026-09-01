from typing import Any, Callable
# Outers
from ...exceptions import ValidateError
from ..base_class import Rule
# Inners
from ._helpers import as_predicate, describe_rule
from ._init_validators import raise_rule_param_not_callable


class UserRule(Rule):

    __slots__ = ("rule",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, rule: Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_rule_param_not_callable("Not", rule)


        # 2. Parameter assignment
        self.rule = rule

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Evaluate whether the value fails the wrapped rule
        try:
            return self.rule(value)
        except Exception:
            # Možná zde vyvolat výjimku
            return False

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        try:
            self.rule(value)
        except Exception:
            return False

        # 1. Prepare data
        rule_name = getattr(self.rule, "__name__", str(self.rule))

        # 2. Build the exception
        return ValidateError(
            error_name="VALIDATION_ERROR",
            label=value_name,
            expected=f"value satisfying callable condition '{rule_name}'",
            value=value,
            problem=f"Value failed validation check executed by callable '{rule_name}'.",
            context=context,
            how_to_fix=(
                f"Provide a value that evaluates to True when passed to '{rule_name}'.",
            ),
            exception=ValueError,
        )