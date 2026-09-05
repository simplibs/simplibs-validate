from .validate_dataclass import validate_dataclass


_DESIGN_NOTES = """
# Validate Dataclass Tool Package

## Purpose
Provides the `@validate_dataclass` class decorator, which validates every field 
of a dataclass against its type annotations during instance construction.

## Exported Components Registry

| Component            | Type      | Description                                                                   |
| :------------------- | :-------- | :---------------------------------------------------------------------------- |
| `validate_dataclass` | Decorator | Decorates a dataclass to validate constructor arguments on instantiation.    |
"""