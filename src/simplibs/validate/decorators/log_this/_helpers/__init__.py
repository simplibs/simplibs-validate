from .format_bound_arguments import format_bound_arguments
from .get_context_info import get_context_info
from .log_exception import log_exception
from .log_start import log_start
from .log_success import log_success
from .unwrap_log_this import unwrap_log_this


_DESIGN_NOTES = """
# Log This Internal Helpers Sub-Package

## Purpose
Shared execution and logging helpers used internally by `@log_this` to format 
arguments, safely extract metadata, emit entry/exit/exception log records, and
selectively unwrap previous `@log_this` layers.

## Internal Components Registry

| Component                | Type     | Description                                                                     |
| :----------------------- | :------- | :------------------------------------------------------------------------------ |
| `format_bound_arguments` | Function | Formats bound arguments into a masked, readable signature string.              |
| `get_context_info`       | Function | Safely extracts function name and module metadata for logger initialization.   |
| `log_exception`          | Function | Emits ERROR level records when wrapped functions raise exceptions.              |
| `log_start`              | Function | Emits initial call entry records before target function execution.              |
| `log_success`            | Function | Emits completion records with elapsed execution time and return values.         |
| `unwrap_log_this`        | Function | Recursively strips existing `@log_this` wrapper layers from a target function.  |
"""