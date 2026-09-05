from .boolean_rule import boolean_rule
from .container_rule import container_rule
from .float_rule import float_rule
from .integer_rule import integer_rule
from .mapping_rule import mapping_rule
from .number_rule import number_rule
from .string_rule import string_rule
from .type_rule import type_rule


_DESIGN_NOTES = """
# Composed Validation Rules Sub-Package

## Purpose
Layer-3 composition factories that construct and return reusable `Rule` instances
(either a single base predicate or an `AllOf` composite rule) from optional constraint parameters.

## Internal Components Registry

| Component        | Type     | Description                                                              |
| :--------------- | :------- | :----------------------------------------------------------------------- |
| `boolean_rule`   | Function | Factory composing a `Rule` for boolean validation and equality.          |
| `container_rule` | Function | Factory composing a `Rule` for containers, length, uniqueness, and items.|
| `float_rule`     | Function | Factory composing a `Rule` for float bounds, finiteness, and tolerance.  |
| `integer_rule`   | Function | Factory composing a `Rule` for integer bounds, range, and divisibility.  |
| `mapping_rule`   | Function | Factory composing a `Rule` for dict values, entries length, and keys.    |
| `number_rule`    | Function | Factory composing a `Rule` for generic numeric values (int, float, etc.).|
| `string_rule`    | Function | Factory composing a `Rule` for string bounds, regex, and blankness.     |
| `type_rule`      | Function | Factory composing a `Rule` for class/type objects and inheritance.       |
"""