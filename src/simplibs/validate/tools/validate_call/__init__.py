from .validate_call import validate_call


_DESIGN_NOTES = """
# Validate Call Tool Sub-Package

## Purpose
Provides the `@validate_call` decorator for annotation-driven runtime argument
and return value validation for both synchronous and asynchronous functions.

## Internal Components Registry

| Component       | Type      | Description                                                                     |
| :-------------- | :-------- | :------------------------------------------------------------------------------ |
| `validate_call` | Decorator | Decorates functions to validate inputs and outputs against type annotations.    |
"""