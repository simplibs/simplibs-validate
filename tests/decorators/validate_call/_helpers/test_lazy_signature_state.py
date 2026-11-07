import pytest

# Tested helper and exceptions
from simplibs.exception import ParamError
from simplibs.validate.decorators.validate_call._helpers.lazy_signature_state import (
    lazy_signature_state,
)


def plain(a: int, b: "str"): ...
def late(a: "_LazyLateName"): ...
def never(a: "_NeverDefinedName"): ...


class _Recorder:
    """Counts build calls and remembers the signatures it received."""

    def __init__(self) -> None:
        self.calls = 0
        self.signatures = []

    def __call__(self, signature):
        self.calls += 1
        self.signatures.append(signature)
        return {"state": self.calls}


# ============================================================================
# Resolvable right away
# ============================================================================

def test_lazy_signature_state_builds_immediately_when_resolvable() -> None:
    """Verify state is built at creation time when every annotation resolves."""
    build = _Recorder()
    lazy_signature_state(plain, build)

    assert build.calls == 1


def test_lazy_signature_state_passes_the_resolved_signature() -> None:
    """Verify build receives annotations that are already real objects."""
    build = _Recorder()
    lazy_signature_state(plain, build)

    assert build.signatures[0].parameters["b"].annotation is str


def test_lazy_signature_state_getter_returns_cached_object() -> None:
    """Verify every getter call returns the same state without building again."""
    build = _Recorder()
    get = lazy_signature_state(plain, build)

    assert get() is get()
    assert build.calls == 1


def test_lazy_signature_state_build_error_propagates_at_creation() -> None:
    """Verify an error from build surfaces immediately when the signature is resolvable."""
    def failing(signature):
        raise ParamError(error_name="BUILD_FAILED")

    with pytest.raises(ParamError) as exc_info:
        lazy_signature_state(plain, failing)

    assert exc_info.value.error_name == "BUILD_FAILED"


# ============================================================================
# Postponed until the first call
# ============================================================================

def test_lazy_signature_state_postpones_when_name_is_missing() -> None:
    """Verify nothing is built while a referenced name does not exist."""
    build = _Recorder()
    lazy_signature_state(late, build)

    assert build.calls == 0


def test_lazy_signature_state_builds_on_first_call_once_name_exists() -> None:
    """Verify the state is built on first use and then cached."""
    build = _Recorder()
    get = lazy_signature_state(late, build)

    globals()["_LazyLateName"] = int
    try:
        first = get()
        second = get()
    finally:
        del globals()["_LazyLateName"]

    assert first is second
    assert build.calls == 1
    assert build.signatures[0].parameters["a"].annotation is int


def test_lazy_signature_state_still_missing_on_first_call_raises() -> None:
    """Verify a name that never appears is reported as ParamError at the first use."""
    get = lazy_signature_state(never, _Recorder())

    with pytest.raises(ParamError) as exc_info:
        get()

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"


def test_lazy_signature_state_recovers_after_a_failed_first_call() -> None:
    """Verify a failed first call is not cached: the name may appear later."""
    build = _Recorder()
    get = lazy_signature_state(late, build)

    with pytest.raises(ParamError):
        get()

    globals()["_LazyLateName"] = int
    try:
        assert get() == {"state": 1}
    finally:
        del globals()["_LazyLateName"]


def test_lazy_signature_state_build_error_is_raised_on_first_call_when_postponed() -> None:
    """Verify configuration errors of a postponed function appear on first use."""
    def failing(signature):
        raise ParamError(error_name="BUILD_FAILED")

    get = lazy_signature_state(late, failing)  # postponed, so nothing raised yet

    globals()["_LazyLateName"] = int
    try:
        with pytest.raises(ParamError) as exc_info:
            get()
    finally:
        del globals()["_LazyLateName"]

    assert exc_info.value.error_name == "BUILD_FAILED"
