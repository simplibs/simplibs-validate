import inspect
from typing import Any, Callable
from simplibs.rules import Rule, build_typing_rule
# Outers
from .._validations import raise_no_rule_for_return


def compile_return_rule(
    func: Callable[..., Any],
    signature: inspect.Signature,
    *,
    check_return: bool,
) -> Rule | None:
    """Build the return-value Rule, if check_return was requested.

    Args:
        func: The function being decorated — used only for diagnostics
            (raise_no_rule_for_return's error message).
        signature: The function's inspect.Signature.
        check_return: Whether the return value should be validated at all.

    Returns:
        None if check_return is False. Otherwise, the Rule built from the
        function's return annotation.

    Raises:
        ParamError: If check_return is True but the function has no
            return annotation.
    """
    # 1. Not requested — nothing to build
    if not check_return:
        return None

    # 2. Requested, but no rule source exists — an explicit request
    #    without a rule source behind it is always an error, mirroring
    #    compile_parameter_rules' handling of `check`
    if signature.return_annotation is inspect.Signature.empty:
        raise_no_rule_for_return(func)

    # 3. Build the rule from the return annotation
    return build_typing_rule(signature.return_annotation)


_DESIGN_NOTES = """
# compile_return_rule — validate_call's Return-Value Rule Compiler

## Purpose
The return-value counterpart to compile_parameter_rules: extracted from
validate_call itself so the "is this requested, does a rule source exist,
build it" decision can be tested directly against a signature/check_return
combination, without going through the decorator machinery to exercise it.
Kept as its own function rather than folded into compile_parameter_rules
because it validates a fundamentally different thing (one return
annotation, not a dict of per-parameter annotations) and has its own,
simpler return type (`Rule | None` instead of `dict[str, Rule]`).

---

## 1. Called Once, at Decoration Time — Same as Before

Moving this into its own function changes nothing about *when* it runs:
validate_call still calls it exactly once, when the decorator is applied,
never per-call. See validate_call's own design notes for the "build once"
rationale this preserves unchanged.

---

## 2. `func` Is Passed Through Only for Diagnostics

Same rationale as compile_parameter_rules: this function never calls
`func` — it only exists here so raise_no_rule_for_return can report a
fully qualified, readable error message (`func.__qualname__`).
"""