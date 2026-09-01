from .raise_has_length_param_conflict_error import raise_has_length_param_conflict_error
from .raise_regex_param_invalid_pattern_error import raise_regex_param_invalid_pattern_error


_DESIGN_NOTES = """
# Rule-Specific Constructor Error Guards Sub-Package

## Purpose
Guard functions that raise tailored `ParamError` diagnostics for
constructor problems specific to a single predicate rule, as opposed to
generic, reusable guards shared across many rules.

## Internal Components Registry

| Component                                  | Type     | Description                                                              |
| :-------------------------------------------| :------- | :--------------------------------------------------------------------------|
| `raise_has_length_param_conflict_error`      | Function | Raises when `HasLength` receives both `length` and `min_length`/`max_length`. |
| `raise_regex_param_invalid_pattern_error`    | Function | Raises when `Regex` receives a syntactically invalid pattern string.     |
"""
