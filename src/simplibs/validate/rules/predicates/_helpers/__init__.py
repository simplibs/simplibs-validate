from .format_container import format_container


_DESIGN_NOTES = """
# Predicate Rules Internal Helpers Sub-Package

## Purpose
Shared runtime helpers used internally by predicate validation rules
(`IsSubsetOf`, `IsSupersetOf`, `IsIn`, `NotIn`, etc.) to provide consistent,
deterministic formatting of collection representations in diagnostic exception
messages.

## Internal Components Registry

| Component          | Type     | Description                                                                     |
| :----------------- | :------- | :------------------------------------------------------------------------------ |
| `format_container` | Function | Formats containers deterministically (sorting sets/frozensets when possible).   |
"""