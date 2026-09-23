# 📄 `tools` — Helpers for Everyday Use

The `tools` package is where `simplibs-validate`'s lower-level building blocks
(`Rule`, `IsTyping`, `build_typing_rule`) turn into small helpers for building the inputs
used by the validation decorators. Unlike the `rules/` documentation, this page describes
*what each tool does and why*, not their internal code — these are composition and
convenience layers, not new validation mechanisms of their own.

## 🧭 Table of Contents

* [`validated_type`](#validated_type)
* [`override_rules`](#override_rules)

[⬅️ Back to main README](../../README.md#-tools)

### `validated_type`

A small helper for defining a reusable "type + validation rule" once, under a name,
instead of repeating `Annotated[int, greater_than(0)]` everywhere that constraint is
needed:

```python
PositiveInt = validated_type(int, greater_than(0))

def register(age: PositiveInt) -> None: ...
```

**What it actually does.** Builds and returns `Annotated[type_, *rules]` — nothing
more. It performs no validation itself; the resulting annotation is only ever
decomposed later, whenever something that understands `Annotated` metadata
(`IsTyping`, `validate_call`, `validate_dataclass`) actually processes it. This keeps
`validated_type` a pure naming convenience, not a second validation mechanism running
alongside the real one.

**Multiple rules, two equivalent styles.** You can pass several rules as separate
positional arguments (`validated_type(int, is_integer, greater_than(0))`), or
pre-compose them with `&`/`|`/`~` into a single rule
(`validated_type(int, is_integer & greater_than(0))`) — both produce the same result
once decomposed, since every recognized `Rule`/callable item is combined via `AllOf`
regardless of whether it arrived as one composed rule or several separate ones. Pick
whichever reads more naturally for a given case; they can also be freely mixed in one
call.

**Validated eagerly, at the point you call it.** At least one rule is required —
calling `validated_type(int)` with none is treated as a likely mistake (you'd
otherwise just write `int` directly) and raised immediately. Every given rule is also
checked at that point: it must be either a `Rule` instance or a plain callable, or the
call fails right there, naming exactly which positional rule was invalid — not left to
silently do nothing the first time validation is eventually attempted.

[▲ Back to top](#-table-of-contents)

---

### `override_rules`

A small helper for building the `overrides=` mapping `validate_call`/
`validate_dataclass` expect, when several parameters need extra rules at once:

```python
my_overrides = override_rules(
    param1=is_integer & greater_than(0),
    param2=is_string,
    param3=lambda value: value != "forbidden",
)

@validate_call(overrides=my_overrides)
def some_func(param1: int, param2: str, param3: Any): ...
```

**Keyword arguments as the mapping itself.** Each keyword argument name becomes the
parameter name the rule applies to, and its value is the rule — there's no separate
positional/tuple syntax to learn, since Python's own `**kwargs` mechanism already
provides exactly this shape. A plain callable value is automatically wrapped so it
behaves like a proper rule; a `Rule` instance is used exactly as given. Every value is
checked at the point `override_rules(...)` is called — it must be a `Rule` instance or
callable, or the call fails immediately, naming which parameter's value was invalid.

**No `type` argument, on purpose.** `overrides=` is always combined with whatever a
parameter's own annotation already establishes — an override never replaces or
introduces a type on its own. If you want to pair a fresh type with a rule under one
name, that's what `validated_type` is for; `override_rules` exists purely to *add*
constraints to parameters that already have (or intentionally don't have) their own
annotation.

[▲ Back to top](#-table-of-contents)

---
