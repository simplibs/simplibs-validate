# Reserved parameter name for per-call validation bypass
BYPASS_PARAM_NAME = "_validate_call"


_DESIGN_NOTES = """
# BYPASS_PARAM_NAME — Reserved Per-Call Bypass Parameter Name

## Purpose
Defines the canonical constant string used to identify and evaluate `@validate_call`'s
reserved per-call bypass parameter across internal compilation and execution helpers.

---

## 1. Single Source of Truth

By extracting `BYPASS_PARAM_NAME` into its own dedicated module, all dependent
internal helpers (`is_bypass_parameter`, `should_validate`, `validate_call`)
reference a single source of truth. This prevents circular imports and eliminates
magic string repetition across decoration-time signature analysis and call-time
bypass checks.
"""