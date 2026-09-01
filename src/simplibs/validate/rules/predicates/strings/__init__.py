from .Regex import Regex
from .Contains import Contains
from .StartsWith import StartsWith
from .EndsWith import EndsWith
from .IsBlank import IsBlank
from .NotBlank import NotBlank
from .IsString import IsString


_DESIGN_NOTES = """
# String Predicate Rules Sub-Package

## Purpose
Predicate rules operating on `str` values — pattern matching, substring
and affix checks, and blank/non-blank content checks.

## Internal Components Registry

| Component      | Type  | Description                                                              |
| :-----------------| :---- | :---------------------------------------------------------------------------|
| `Regex`           | Class | String must match a given regular expression pattern.                   |
| `Contains`        | Class | String must contain a given substring.                                  |
| `StartsWith`      | Class | String must start with a given prefix.                                  |
| `EndsWith`        | Class | String must end with a given suffix.                                    |
| `IsBlank`         | Class | String must be empty or whitespace-only.                                |
| `NotBlank`        | Class | String must contain at least one non-whitespace character.              |
| `IsString`        | Class | Value must be strictly a `str`.              |
"""
