# 📄 `tools` — Decorators & Helpers for Everyday Use

The `tools` package is where `simplibs-validate`'s lower-level building blocks
(`Rule`, `IsTyping`, `build_typing_rule`) turn into things you actually reach for in
day-to-day code: decorators that validate a function's arguments automatically, a
decorator that gives any function structured logging, and two small helpers for
building the inputs those decorators expect. Unlike the `rules/` documentation, this
page describes *what each tool does and why*, not their internal code — these are
composition and convenience layers, not new validation mechanisms of their own.

---

## 🧭 Table of Contents

* [`validate_call`](#validate_call)
* [`validate_dataclass`](#validate_dataclass)
* [`validated_type`](#validated_type)
* [`override_rules`](#override_rules)
* [`log_this`](#log_this)

[⬅️ Back to main README](../../README.md#-tools)

---

### `validate_call`

A decorator that validates a function's arguments — and optionally its return value —
against the function's own type annotations, on every call. This is the main way
`simplibs-validate` attaches itself to ordinary functions: annotate the parameters
however you'd normally write type hints, and `@validate_call` enforces them at
runtime, using the exact same annotation-decomposition machinery `IsTyping` provides.

**What it accepts as an annotation.** Anything `build_typing_rule` understands: a
plain type (`int`, `str`), a typing generic (`list[int]`, `dict[str, int]`), a union
(`int | None`), a `Rule` instance used directly (`x: is_integer`), or an
`Annotated[...]` construct carrying `Rule`/callable metadata (typically built via
`validated_type`). Parameters with no annotation at all are simply skipped, unless
they're named in `overrides`.

**Two ways to apply it.** As a bare decorator (`@validate_call`), or called with
keyword arguments (`@validate_call(check=..., overrides=..., check_return=...)`) —
both forms produce a function whose full original signature (parameter names, types,
return type) remains visible to IDEs and type checkers, not a generic
`(*args, **kwargs)`.

**Selective validation with `check`.** By default every annotated parameter is
validated. Passing `check=("x", "y")` restricts validation to just those named
parameters — every other parameter, annotated or not, is left alone. If a name in
`check` has neither an annotation nor a matching entry in `overrides`, that's treated
as a mistake and raised immediately when the decorator is applied (not on first call)
— a parameter explicitly asked to be checked but with nothing to check it against
would otherwise silently validate nothing, which is worse than an upfront error.

**Adding extra rules with `overrides`.** `overrides` supplies additional `Rule`/
callable constraints per parameter name, combined with whatever the parameter's own
annotation already establishes — never replacing it. This is how you add a business
rule (e.g. "must be one of our known statuses") without cluttering the function
signature itself, or add a constraint to a parameter that has no type annotation at
all. `override_rules(...)` (see below) is the recommended way to build this mapping
when several parameters need overrides at once.

**Validating the return value with `check_return`.** Off by default — a return
annotation is often more aspirational than authoritative, so turning this on
unconditionally for every annotated function would be surprising. Setting
`check_return=True` validates the return value against the function's `->` annotation
after the function runs; if the function has no return annotation at all,
`check_return=True` is treated as a mistake and raised at decoration time, the same
way an unchecked `check` entry is.

**Skipping validation per call with a `validate` parameter.** If the decorated
function itself declares a parameter literally named `validate` (with no annotation,
or an explicit `bool` annotation), its value at call time acts as a bypass switch:
passing `validate=False` skips every check — both parameters and return value — for
that one call, while the function's own logic still runs normally. This exists for
functions that are sometimes called directly (where validation is wanted) and
sometimes called from code that has already validated the same data upstream (where
re-validating would just be wasted work). Functions that don't declare this parameter
always validate — the bypass is opt-in per function, never assumed, and the
`validate` parameter itself is passed through to the function body unchanged, so the
function can inspect or forward it if it wants to.

**Works on `async def` functions too**, with no change in how you write your
annotations. Parameters are still validated synchronously, before the function runs
— validation never needs to wait on anything. The return value, however, is only
validated *after* being awaited, so `check_return=True` checks the function's actual
resolved result, not an unstarted coroutine object.

---

### `validate_dataclass`

The `@dataclass`-specific counterpart to `validate_call`: validates every field of a
dataclass against its own field annotation, every time an instance is constructed.

```python
@validate_dataclass
@dataclass
class User:
    name: str
    age: Annotated[int, greater_than(0)]
```

**Why this needs to be a separate decorator.** `validate_call` already works
perfectly well on an ordinary, hand-written `__init__` — there's no gap there. The
gap is specifically `@dataclass`, which *generates* `__init__` itself; at the point
you write the class body, there's no `__init__` yet for `validate_call` to wrap.
`validate_dataclass` is applied *above* `@dataclass` in the decorator stack
(decorators apply bottom-up, so `@dataclass` must run first) and wraps the `__init__`
that `@dataclass` just generated. Applying it to something that isn't a dataclass yet
— wrong decorator order, or simply forgetting `@dataclass` — is caught immediately and
reported clearly, rather than failing confusingly somewhere inside rule compilation.

**Same field-rule logic as `validate_call`.** A dataclass-generated `__init__` has
exactly one parameter per field, each carrying that field's own annotation —
structurally identical, from this decorator's point of view, to any other function
signature. No separate rule-building logic exists for dataclasses; the same
per-parameter compiler `validate_call` uses is reused unchanged. `check` and
`overrides` work exactly as they do for `validate_call`, scoped to field names instead
of parameter names.

**Validates before any field is assigned.** The wrapped `__init__` checks every
constructor argument *before* calling the original `__init__` that actually assigns
values onto `self`. This matters most for frozen dataclasses: if validation fails, no
field is ever set — the instance never exists in a partially-valid state. It also
means any custom `__post_init__` you've written keeps working exactly as before,
since it's called from inside the original `__init__` this decorator wraps, not
replaced or bypassed.

**No return-value equivalent.** A dataclass's `__init__` always returns `None`, so
there's no `check_return` option here — it isn't a missing feature, just a fact about
what `__init__` is.

---

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

---

### `log_this`

A decorator that gives any function entry/exit/timing/exception logging, without
requiring the function to contain any logging code of its own, and without this
decorator ever deciding *where* those logs end up — that remains entirely up to your
own application's `logging` configuration. `log_this` is entirely independent of the
validation decorators above; it observes and records, it never checks or enforces
anything.

```python
@log_this()
def process_order(order_id: int) -> dict: ...
```

**What gets logged, and when.** Before the function runs, a record is emitted showing
the function's qualified name and its call arguments. After the function completes
successfully, a second record shows the elapsed time and (unless disabled) the return
value. If the function raises, that's logged too — at `ERROR` level, with a full
traceback — immediately before the same exception is re-raised completely unchanged;
`log_this` never swallows or replaces an exception, it only observes it on its way
past.

**Where the logs actually go.** Every record is emitted through
`logging.getLogger(<the decorated function's own module>)` — exactly as if the
function's own module had called `logging.getLogger(__name__)` itself. This is what
lets `log_this` blend into whatever logging setup your application already has,
without needing any `simplibs`-specific configuration step; if your application hasn't
configured logging at all, these records are simply discarded, the same as any other
unconfigured logger in Python.

**Nothing is logged at a surprising level by default.** The entry/success records
default to `DEBUG` — a successful call is a debugging detail worth having available,
not something that should show up unprompted in a typical production log
configuration (which commonly filters below `INFO`). Pass `level=logging.INFO` (or
any other level) explicitly if you want these visible by default.

**What you can adjust.** `exclude` masks named parameters (replacing their value with
`***` in the logged call signature) — the one setting genuinely worth knowing about
for anything touching secrets or credentials. `log_result=False` omits the return
value from the success record, useful when it's large or sensitive, without losing
the timing information. `log_exceptions=False` turns off the failure record entirely
(the exception itself is still always re-raised, regardless). `logger=` lets you
supply your own `Logger` instance instead of the automatically derived one, for the
rare case you want several decorated functions sharing one logger.

**Works on `async def` functions too.** The timing and logging wrap around the actual
`await`, not just the moment the coroutine object is created — so elapsed time and the
logged result reflect the function's real execution, not an instantaneous, empty
measurement.

---

[⬅️ Back to main README](../../README.md#-tools)