from .Is import Is
from .IsNot import IsNot
from .IsIn import IsIn
from .NotIn import NotIn


_DESIGN_NOTES = """
# Logic Predicate Rules Sub-Package

## Purpose
Predicate rules built on Python's identity (`is`) and membership (`in`)
operators — checking exact object identity or presence/absence within a
reference collection.

## Internal Components Registry

| Component   | Type  | Description                                                              |
| :-------------| :---- | :---------------------------------------------------------------------------|
| `Is`          | Class | Value must be identical (`is`) to a specific object.                    |
| `IsNot`       | Class | Value must NOT be identical (`is not`) to a specific object.            |
| `IsIn`        | Class | Value must be a member of a given collection.                           |
| `NotIn`       | Class | Value must NOT be a member of a given collection.                       |
"""
