from .rules import (
    boolean_rule,
    container_rule,
    float_rule,
    integer_rule,
    mapping_rule,
    number_rule,
    string_rule,
    type_rule,
)
from .validate_bool import validate_bool
from .validate_container import validate_container
from .validate_float import validate_float
from .validate_int import validate_int
from .validate_mapping import validate_mapping
from .validate_number import validate_number
from .validate_string import validate_string
from .validate_type import validate_type

__all__ = [
    "boolean_rule",
    "container_rule",
    "float_rule",
    "integer_rule",
    "mapping_rule",
    "number_rule",
    "string_rule",
    "type_rule",
    "validate_bool",
    "validate_container",
    "validate_float",
    "validate_int",
    "validate_mapping",
    "validate_number",
    "validate_string",
    "validate_type",
]


_DESIGN_NOTES = """
# High-Level Validators Sub-Package

## Purpose
Convenience validation functions and rule factory compositions providing high-level,
type-specific validation entry points for common data types.

## Exported Components Registry

| Component            | Type     | Description                                                              |
| :------------------- | :------- | :----------------------------------------------------------------------- |
| `boolean_rule`       | Function | Rule factory for boolean validation.                                     |
| `container_rule`     | Function | Rule factory for container validation.                                   |
| `float_rule`         | Function | Rule factory for float validation.                                       |
| `integer_rule`       | Function | Rule factory for integer validation.                                     |
| `mapping_rule`       | Function | Rule factory for dict/mapping validation.                                |
| `number_rule`        | Function | Rule factory for general numeric validation.                             |
| `string_rule`        | Function | Rule factory for string validation.                                      |
| `type_rule`          | Function | Rule factory for class/type validation.                                  |
| `validate_bool`      | Function | Directly validates a value as a boolean against constraints.             |
| `validate_container` | Function | Directly validates a value as a container against constraints.           |
| `validate_float`     | Function | Directly validates a value as a float against constraints.               |
| `validate_int`       | Function | Directly validates a value as an integer against constraints.            |
| `validate_mapping`   | Function | Directly validates a value as a dict against constraints.                |
| `validate_number`    | Function | Directly validates a value as a number against constraints.              |
| `validate_string`    | Function | Directly validates a value as a string against constraints.              |
| `validate_type`      | Function | Directly validates a value as a class/type object against constraints.   |
"""