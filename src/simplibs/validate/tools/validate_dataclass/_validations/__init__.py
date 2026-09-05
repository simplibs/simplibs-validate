from .raise_not_a_dataclass_error import raise_not_a_dataclass_error


_DESIGN_NOTES = """
# Validate Dataclass Internal Validations Sub-Package

## Purpose
Internal validation helpers used by `@validate_dataclass` at decoration time to 
enforce decorator ordering rules and raise clear diagnostic exceptions.

## Internal Components Registry

| Component                     | Type     | Description                                                                     |
| :---------------------------- | :------- | :------------------------------------------------------------------------------ |
| `raise_not_a_dataclass_error` | Function | Raises a ParamError when `@validate_dataclass` is applied to a non-dataclass.   |
"""