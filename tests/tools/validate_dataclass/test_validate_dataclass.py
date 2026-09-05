from dataclasses import dataclass
import pytest
from simplibs.validate.exceptions import ParamError, ValidationError
from simplibs.validate.tools.validate_dataclass import validate_dataclass


# ============================================================================
# Basic & Bare Decorator Tests
# ============================================================================

def test_validate_dataclass_bare_success() -> None:
    """Verify bare @validate_dataclass validates instance construction arguments."""

    @validate_dataclass
    @dataclass
    class User:
        name: str
        age: int

    user = User("Alice", 30)
    assert user.name == "Alice"
    assert user.age == 30


def test_validate_dataclass_bare_failure() -> None:
    """Verify bare @validate_dataclass raises ValidationError on type mismatch."""

    @validate_dataclass
    @dataclass
    class User:
        name: str
        age: int

    with pytest.raises(ValidationError):
        User("Alice", "thirty")


def test_validate_dataclass_order_check_raises_param_error() -> None:
    """Verify ParamError is raised at decoration time if applied to a non-dataclass."""

    with pytest.raises(ParamError) as exc_info:

        @validate_dataclass
        class PlainClass:
            name: str

    assert exc_info.value.error_name == "VALIDATE_DATACLASS_NOT_A_DATACLASS_ERROR"


# ============================================================================
# Check & Overrides Parameter Tests
# ============================================================================

def test_validate_dataclass_with_check_filter() -> None:
    """Verify check restricts validation to specified fields only."""

    @validate_dataclass(check=("name",))
    @dataclass
    class Config:
        name: str
        port: int

    # 'name' is validated (str), 'port' is ignored even though it receives invalid type
    cfg = Config("production", "8080")
    assert cfg.name == "production"
    assert cfg.port == "8080"

    with pytest.raises(ValidationError):
        Config(12345, 8080)


def test_validate_dataclass_with_overrides() -> None:
    """Verify overrides add custom predicates to fields."""

    @validate_dataclass(overrides={"age": lambda x: x >= 18})
    @dataclass
    class Account:
        username: str
        age: int

    acc = Account("john_doe", 20)
    assert acc.username == "john_doe"

    with pytest.raises(ValidationError):
        Account("underage", 16)


# ============================================================================
# Frozen Dataclass Behavior Tests
# ============================================================================

def test_validate_dataclass_frozen_dataclass() -> None:
    """Verify validation applies before field assignment on frozen dataclasses."""

    @validate_dataclass
    @dataclass(frozen=True)
    class ImmutablePoint:
        x: int
        y: int

    pt = ImmutablePoint(10, 20)
    assert pt.x == 10
    assert pt.y == 20

    with pytest.raises(ValidationError):
        ImmutablePoint("invalid", 20)