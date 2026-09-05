from .log_this import log_this


_DESIGN_NOTES = """
# Log This Tool Package

## Purpose
Provides the `@log_this` decorator, giving functions entry, exit, timing, and 
exception logging integrated directly into the target function's module logger.

## Exported Components Registry

| Component  | Type      | Description                                                                  |
| :--------- | :-------- | :--------------------------------------------------------------------------- |
| `log_this` | Decorator | Decorates functions to automatically log entry, execution time, and errors.  |
"""