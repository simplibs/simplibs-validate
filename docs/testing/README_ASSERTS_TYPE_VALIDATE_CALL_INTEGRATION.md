# 🧪 `assert_type_validate_call_integration`

**Runtime Type Annotation ↔ `@validate_call` Execution Probe**

`assert_type_validate_call_integration` tests that a custom type annotation (`Annotated[type_, *rules]` or a `validated_type()` alias) works correctly when used as a parameter annotation on a function decorated with `@validate_call`.

## 💡 Table of Contents
> * [⚙️ Architectural Principles](#-architectural-principles)
> * [🧭 Pipeline Execution Flow](#-pipeline-execution-flow)
> * [🔍 Quick Usage Examples](#-quick-usage-examples)
> * [🛠️ Configuration & Parameters](#-configuration--parameters)
> * [🔄 Audit Pipeline (2 Phases)](#-audit-pipeline-2-phases)
>   * [Phase 1: Valid Inputs Execution](#phase-1-valid-inputs-execution)
>   * [Phase 2: Invalid Inputs Execution](#phase-2-invalid-inputs-execution)
> * [📖 Real-World Example](#-real-world-example)

[⬅️ Back to main README](../../README.md#-testing-utilities)

---

## ⚙️ Architectural Principles

* **Targeted Integration Probe:** Focuses specifically on parameter decoration and runtime interception under `@validate_call`, isolating annotation wiring logic from pure rule evaluation.
* **Dynamically Isolated Throwaway Functions:** Dynamically constructs a lightweight decorated function (`def _probe(param: type_) -> Any: return param`) for each test run to prevent cross-test contamination or lingering signature metadata.
* **Full Input Range Coverage:** Iterates through every valid and invalid value provided, ensuring valid values pass through untransformed and invalid values consistently trigger a `ValidationError`.

[▲ Back to Top](#-assert_type_validate_call_integration)

---

## 🧭 Pipeline Execution Flow

1. **Function Synthesis** — Dynamically constructs a throwaway single-argument function decorated with `@validate_call`, using `type_` as the argument's type annotation.
2. **Valid Value Probe** — Passes every value in `valid_values` to the function and asserts that it executes without error and returns the exact value.
3. **Invalid Value Probe** — Passes every value in `invalid_values` to the function and asserts that `@validate_call` intercepts the call and raises a `ValidationError`.

[▲ Back to top](#-table-of-contents)

---

## 🔍 Quick Usage Examples

```python
from simplibs.rules.predicates import IsString
from simplibs.validate.testing import assert_type_validate_call_integration
from simplibs.validate.tools import validated_type

NonEmptyString = validated_type(str, ~IsString(""))

# Verify type behavior under @validate_call
assert_type_validate_call_integration(
    subtests,
    type_=NonEmptyString,
    valid_values=["hello", "world"],
    invalid_values=["", 123, None],
)

```

[▲ Back to Top](#-assert_type_validate_call_integration)

---

## 🛠️ Configuration & Parameters

### Mandatory Parameters

* **`subtests`** (`Any`): The native pytest subtests fixture manager instance.
* **`type_`** (`Any`): The target type annotation under test.
* **`valid_values`** (`list[Any]`): List of sample values expected to pass function execution.
* **`invalid_values`** (`list[Any]`): List of sample values expected to be intercepted by `@validate_call`.

### Optional Parameters

* **`verbose`** (`bool`): Default `True`. Controls whether each test iteration is registered as an isolated pytest subtest frame.
* **`intro`** (`str`): Default `""`. Prefix string added to pytest subtest identity names.

```python
# Function signature:
def assert_type_validate_call_integration(
    subtests: Any,
    type_: Any,
    valid_values: list[Any],
    invalid_values: list[Any],
    *,
    verbose: bool = True,
    intro: str = "",
) -> None:

```

[▲ Back to Top](#-assert_type_validate_call_integration)

---

## 🔄 Audit Pipeline (2 Phases)

### Phase 1: Valid Inputs Execution

Constructs the probe function and invokes it with each value in `valid_values`.

```python
# Executed under the hood:
@validate_call
def _probe(val: type_) -> Any:
    return val

for val in valid_values:
    assert _probe(val) == val

```

### Phase 2: Invalid Inputs Execution

Invokes the probe function with each value in `invalid_values` and verifies that a `ValidationError` is raised.

```python
# Executed under the hood:
for val in invalid_values:
    raised = False
    try:
        _probe(val)
    except ValidationError:
        raised = True
    assert raised

```

[▲ Back to Top](#-assert_type_validate_call_integration)

---

## 📖 Real-World Example

```python
"""Tests for @validate_call integration with custom validated types."""

from simplibs.rules.predicates import GreaterThan
from simplibs.validate.testing import assert_type_validate_call_integration
from simplibs.validate.tools import validated_type

PositiveInt = validated_type(int, GreaterThan(0))

def test_positive_int_validate_call_integration(subtests):
    """Verify that @validate_call correctly enforces PositiveInt."""
    assert_type_validate_call_integration(
        subtests,
        type_=PositiveInt,
        valid_values=[1, 50, 999],
        invalid_values=[-10, 0, "invalid_string"],
        verbose=False,
    )

```

[▲ Back to Top](#-assert_type_validate_call_integration)

---

[⬅️ Back to main README](../../README.md#-testing-utilities)
