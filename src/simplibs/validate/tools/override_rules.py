from typing import Any, Callable
from simplibs.rules import Rule, UserRule
# Inners
from ._validations import raise_override_rules_invalid_error


def override_rules(**rules: Rule | Callable[[Any], bool]) -> dict[str, Rule]:
    """Batch-build a parameter-name -> Rule mapping, for use as
    validate_call's/validate_dataclass's `overrides` argument.

        my_overrides = override_rules(
            param1=is_integer & greater_than(0),
            param2=is_string,
            param3=lambda value: value != "forbidden",
        )

        @validate_call(overrides=my_overrides)
        def some_func(param1: int, param2: str, param3: Any): ...

    Each override is combined (via AllOf) with whatever the parameter's
    own annotation already produces — this function only builds the
    override half; it never carries a type of its own (see design notes).

    Args:
        **rules: One Rule instance or callable predicate per parameter
            name, given as keyword arguments.

    Returns:
        A dict mapping each parameter name to its Rule — a plain
        callable value is wrapped in UserRule; a Rule instance is used
        as-is. Directly usable as `overrides=`.

    Raises:
        ParamError: If any value is neither a Rule instance nor callable.
    """
    compiled: dict[str, Rule] = {}

    for name, rule in rules.items():
        if not (isinstance(rule, Rule) or callable(rule)):
            raise_override_rules_invalid_error(name, rule)

        compiled[name] = rule if isinstance(rule, Rule) else UserRule(rule)

    return compiled


_DESIGN_NOTES = """
# override_rules — Batch overrides Builder

## Purpose
Lets many parameters' override rules be declared together in one place,
producing exactly what validate_call's/validate_dataclass's `overrides`
argument already accepts.

---

## 1. `**rules`, Not `*entries` of (name, type, rule) Tuples

An earlier design (kwargs_annotated) took `*entries` of `(name, type,
rule)` 3-tuples, requiring its own structural validation (is this
actually a 3-tuple?) and its own diagnostic for getting that shape wrong.
`**rules` uses Python's own keyword-argument mechanism instead — the
mapping from name to value is guaranteed correct by the language itself,
so there is nothing structural left to validate; only each value's
usability as a rule needs checking (see raise_override_rules_invalid_error).

---

## 2. No `type` Parameter — Deliberately

`overrides=` is always combined with whatever the parameter's own
annotation already establishes (`AllOf(annotation_rule, override_rule)`
— see compile_parameter_rules). A `type` argument here would therefore
either duplicate a type already given in the function's own signature,
or — worse — silently do nothing, since override_rules has no way to
inject a type into the function's actual annotation after the fact.
Type constraints belong on the parameter's own annotation (or on
validated_type, when a type+rule pairing is worth naming together);
override_rules exists purely to add rules where they're missing, not to
re-declare types.

---

## 3. No Multi-Rule-Per-Parameter Syntax (e.g. a Tuple of Rules)

`is_integer & greater_than(0)` already expresses "combine several rules"
without any new syntax. A tuple-per-parameter form
(`override_rules(param1=(is_integer, greater_than(0)))`) was considered
and rejected: unlike validated_type's `*rules` (where position
unambiguously separates "the type" from "the rules"), a tuple value
under one keyword here would require guessing whether that tuple *is* a
rule (an unusual but not impossible case for a custom callable) or a
*sequence of* rules — implicit, guessable behavior this library avoids
in favor of the explicit `&` composition that already exists.
"""