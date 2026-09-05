import inspect
from typing import Any, Callable
# Outers
from ....rules.base_class import Rule
from ....rules.containers import AllOf, Compose
from ....rules.typing import build_typing_rule
# Inners
from .._validations import raise_no_rule_for_checked_param


def compile_parameter_rules(
    func: Callable[..., Any],
    signature: inspect.Signature,
    *,
    check: tuple[str, ...] | None,
    overrides: dict[str, Rule | Callable[[Any], bool]],
) -> dict[str, Rule]:
    """Build the per-parameter Rule for every parameter that should be
    validated, given a function's signature, the `check` filter, and any
    `overrides`.

    A parameter's Rule combines (via AllOf) whatever build_typing_rule
    produces from its annotation with whatever override was given for it
    — either half may be absent, but not both (see
    raise_no_rule_for_checked_param).

    Args:
        func: The function being decorated — used only for diagnostics
            (raise_no_rule_for_checked_param's error message).
        signature: The function's inspect.Signature.
        check: If given, restricts compilation to only these parameter
            names; every other parameter is skipped entirely.
        overrides: Extra Rule/callable predicates per parameter name.

    Returns:
        A dict mapping parameter name to its compiled Rule — only for
        parameters that ended up with at least one rule source
        (an annotation, an override, or both). Parameters with neither
        are omitted (when check is None) or raise (when check names them).

    Raises:
        ParamError: If `check` names a parameter with neither an
            annotation nor an overrides entry.
    """

    # 1. Initialize rules dictionary
    compiled: dict[str, Rule] = {}

    # 2. Iterate through function signature parameters
    for name, param in signature.parameters.items():

        # 2.1 Skip parameters not listed in check filter
        if check is not None and name not in check:
            continue

        # 2.2 Inspect parameter sources
        has_annotation = param.annotation is not inspect.Parameter.empty
        override = overrides.get(name)

        # 2.3 Handle missing rule sources
        if not has_annotation and override is None:
            if check is not None:
                raise_no_rule_for_checked_param(func, name)
            continue

        # 2.4 Process type annotation rule
        parts: list[Rule] = []
        if has_annotation:
            parts.append(build_typing_rule(param.annotation))

        # 2.5 Process override additions
        if override is not None:
            parts.append(override if isinstance(override, Rule) else Compose(lambda value: value, override))

        # 2.6 Store compiled parameter rule
        compiled[name] = parts[0] if len(parts) == 1 else AllOf(*parts)

    # 3. Return compiled rules dictionary
    return compiled


_DESIGN_NOTES = """
# compile_parameter_rules — validate_call's Per-Parameter Rule Compiler

## Purpose
Extracted from validate_call itself: the one piece of real decision logic
in the whole decorator (what to combine with what, when to skip, when to
raise), isolated so it can be tested directly against a signature/check/
overrides combination without going through the decorator machinery
(the `@validate_call`/`@validate_call(...)` dispatch, `functools.wraps`,
the wrapper closure) just to exercise it.

---

## 1. Called Once, at Decoration Time — Same as Before

Moving this into its own function changes nothing about *when* it runs:
validate_call still calls it exactly once, when the decorator is applied,
never per-call. See validate_call's own design notes, section 2, for the
"build once" rationale this preserves unchanged.

---

## 2. `func` Is Passed Through Only for Diagnostics

This function never calls `func` — it only exists here so
raise_no_rule_for_checked_param can report a fully qualified, readable
error message (`func.__qualname__`) rather than a bare parameter name
with no indication of which function's decoration failed.
"""