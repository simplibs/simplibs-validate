# 🧪 `assert_validate_wrapper`

**`validate_*` Wrapper ↔ `*_rule` Factory Consistency Audit**

`assert_validate_wrapper` verifies that a high-level `validate_*` convenience function
(`validate_string`, `validate_int`, ...) stays faithfully in sync with the `*_rule`
composition factory it wraps (`string_rule`, `integer_rule`, ...) — confirming the two
halves of every such pair expose the same constraints and delegate correctly to
`Rule.validate()`, without re-testing either one's actual validation logic (that's
`assert_rule_contract`'s job, run against the composed rule itself).

## 💡 Table of Contents:
> * [⚙️ Architectural Principles](#-architectural-principles)
> * [🧭 Pipeline Execution Flow](#-pipeline-execution-flow)
> * [🔍 Quick Usage Examples](#-quick-usage-examples)
> * [🛠️ Configuration & Parameters](#-configuration--parameters)
> * [🔄 Audit Pipeline (3 Phases)](#-audit-pipeline-3-phases)
>   * [Phase 1: Signature Alignment](#phase-1-signature-alignment)
>   * [Phase 2: Successful Delegation](#phase-2-successful-delegation)
>   * [Phase 3: Failure Delegation](#phase-3-failure-delegation)
> * [📖 Real-World Example](#-real-world-example)

[⬅️ Back to main README](../../README.md#-testing-utilities)

---

## ⚙️ Architectural Principles

* **Pairing Contract, Not Validation Logic:** This function never asks "is `min_length`
  correctly enforced" — that's what `assert_rule_contract` against `string_rule(...)`
  already answers. It asks a narrower, equally important question: "does
  `validate_string` actually expose and forward every constraint `string_rule`
  supports, and does it correctly implement the standard `Rule.validate()` calling
  convention on top?"
* **Drift Detection:** The main bug class this catches is a new constraint parameter
  added to a `*_rule` factory and forgotten on its `validate_*` wrapper (or the
  reverse) — a silent, easy-to-miss mismatch that a hand-written test for one function
  in isolation would never surface.
* **Single Value Pair:** Unlike `assert_rule_contract`, which takes lists of many
  valid/invalid values, this function takes exactly one of each — it isn't testing
  *which* values pass or fail (the rule itself already covers that), only that passing
  and failing values are correctly routed through the wrapper.

[▲ Back to Top](#-assert_validate_wrapper)

---

## 🧭 Pipeline Execution Flow

1. **Signature Alignment** — every parameter `rule_factory` accepts must also exist on
   `validate_func`, and `validate_func` must additionally expose the four standard
   control parameters (`value_name`, `context`, `return_bool`, `return_value`).
2. **Successful Delegation** — a valid value passes normally, and correctly returns
   the original value when `return_value=True`.
3. **Failure Delegation** — an invalid value returns `False` under `return_bool=True`,
   and raises when it isn't.

[▲ Back to top](#-table-of-contents)

---

## 🔍 Quick Usage Examples

```python
# 1. Standard wrapper/factory pairing audit
assert_validate_wrapper(
    subtests,
    validate_func=validate_string,
    rule_factory=string_rule,
    valid_value="hello",
    invalid_value="",
    sample_params={"min_length": 1},
)

# 2. No rule-specific constraints needed for this pair
assert_validate_wrapper(
    subtests,
    validate_func=validate_bool,
    rule_factory=boolean_rule,
    valid_value=True,
    invalid_value="not_a_bool",
    sample_params={"equals": True},
)

# 3. Silent mode execution without allocating pytest subtest frames
assert_validate_wrapper(
    subtests,
    validate_func=validate_container,
    rule_factory=container_rule,
    valid_value=[1, 2, 3],
    invalid_value="not_a_container",
    verbose=False,
)
```

[▲ Back to Top](#-assert_validate_wrapper)

---

## 🛠️ Configuration & Parameters

### Mandatory Parameters

* **`subtests`** (`Any`): The native pytest subtests fixture manager instance.
* **`validate_func`** (`Callable[..., Any]`): The high-level wrapper under test (e.g.
  `validate_string`).
* **`rule_factory`** (`Callable[..., Rule]`): The underlying composition factory it
  should wrap (e.g. `string_rule`).
* **`valid_value`** (`Any`): A value expected to pass validation under `sample_params`.
* **`invalid_value`** (`Any`): A value expected to fail validation under
  `sample_params`.

### Optional Parameters

* **`sample_params`** (`dict[str, Any] | None`):
  Default: `None`.
  Rule-specific constraints applied during every check (e.g. `{"min_length": 3}`). An
  empty/`None` value tests the pair with no constraints beyond the base type check.
* **`verbose`** (`bool`):
  Default: `True`.
  Controls pytest subtest frame allocation for each individual check.

```python
# Function signature:
def assert_validate_wrapper(
    subtests: Any,
    *,
    validate_func: Callable[..., Any],
    rule_factory: Callable[..., Rule],
    valid_value: Any,
    invalid_value: Any,
    sample_params: dict[str, Any] | None = None,
    verbose: bool = True,
) -> None:
```

[▲ Back to Top](#-assert_validate_wrapper)

---

## 🔄 Audit Pipeline (3 Phases)

### Phase 1: Signature Alignment

Reflects both callables' signatures via `inspect.signature` and checks two things:
every parameter `rule_factory` accepts is also present on `validate_func`, and
`validate_func` additionally carries the four control parameters that have no reason
to exist on `rule_factory` itself.

```python
# Executed under the hood:
rule_sig = inspect.signature(rule_factory)
val_sig = inspect.signature(validate_func)

for param_name in rule_sig.parameters:
    assert param_name in val_sig.parameters

control_params = {"value_name", "context", "return_bool", "return_value"}
for ctrl_param in control_params:
    assert ctrl_param in val_sig.parameters
```

### Phase 2: Successful Delegation

Calls `validate_func` with `valid_value` in both its default mode and
`return_value=True` mode, confirming both return what `Rule.validate()` itself would.

```python
# Executed under the hood:
assert validate_func(valid_value, **sample_params) is True
assert validate_func(valid_value, return_value=True, **sample_params) == valid_value
```

### Phase 3: Failure Delegation

Calls `validate_func` with `invalid_value` in `return_bool=True` mode (must return
`False`, never raise) and in default mode (must raise).

```python
# Executed under the hood:
assert validate_func(invalid_value, return_bool=True, **sample_params) is False

raised = False
try:
    validate_func(invalid_value, return_bool=False, **sample_params)
except Exception:
    raised = True
assert raised
```

[▲ Back to Top](#-assert_validate_wrapper)

---

## 📖 Real-World Example

`simplibs-validate`'s own test suite uses `assert_validate_wrapper` for every
`validate_*`/`*_rule` pair. Here's the one covering `validate_bool`:

```python
"""Tests for the validate_bool high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_bool
from simplibs.validate.validators.rules import boolean_rule


def test_validate_bool_contract(subtests):
    """Verify validate_bool wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_bool,
        rule_factory=boolean_rule,
        valid_value=True,
        invalid_value="not_a_bool",
        sample_params={"equals": True},
        verbose=False,
    )
```

One call replaces what would otherwise be four separate hand-written assertions
(signature check, two success-path checks, two failure-path checks) — and the same
call, repeated for `validate_container`/`container_rule`,
`validate_string`/`string_rule`, and every other pair, is what keeps every
`validate_*` wrapper in this library provably synchronized with its underlying
composer as both evolve over time.

[▲ Back to Top](#-assert_validate_wrapper)

---

[⬅️ Back to main README](../../README.md#-testing-utilities)


