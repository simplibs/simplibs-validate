from .get_dataclass_context_string import get_dataclass_context_string


_DESIGN_NOTES = """
# Validate Dataclass Internal Helpers Sub-Package

## Purpose
Internal execution helpers used by `@validate_dataclass` at decoration time to 
extract metadata and build diagnostic context strings.

## Internal Components Registry

| Component                      | Type     | Description                                                                 |
| :----------------------------- | :------- | :-------------------------------------------------------------------------- |
| `get_dataclass_context_string` | Function | Safely extracts formatted diagnostic context strings from target dataclasses.|
"""