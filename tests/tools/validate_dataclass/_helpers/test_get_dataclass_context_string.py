import pytest
from simplibs.validate.tools.validate_dataclass._helpers import get_dataclass_context_string


class DummyDataClass:
    pass


def test_get_dataclass_context_string_standard_class() -> None:
    """Verify context string formatting for standard classes with module and qualname."""
    result = get_dataclass_context_string(DummyDataClass)
    assert result == f"Dataclass {DummyDataClass.__module__}.{DummyDataClass.__qualname__}"


def test_get_dataclass_context_string_without_module() -> None:
    """Verify context string formatting when __module__ is absent or None."""
    # Custom metaclass allows overriding __module__ on the class object itself
    class MetaWithoutModule(type):
        pass

    cls = MetaWithoutModule("NoModuleClass", (), {"__module__": None})

    result = get_dataclass_context_string(cls)
    assert result == f"Dataclass {cls.__qualname__}"


def test_get_dataclass_context_string_fallback_name_with_module() -> None:
    """Verify fallback name 'dataclass' when class name attributes are absent but module exists."""
    # Instance/object that has __module__ but lacks __qualname__ and __name__
    class DynamicObj:
        pass

    obj = DynamicObj()
    result = get_dataclass_context_string(obj)
    assert result == f"Dataclass {obj.__module__}.dataclass"


def test_get_dataclass_context_string_fallback_name_without_module() -> None:
    """Verify full fallback 'Dataclass dataclass' when both name attributes and __module__ are absent."""
    class DynamicObj:
        pass

    obj = DynamicObj()
    object.__setattr__(obj, "__module__", None)

    result = get_dataclass_context_string(obj)
    assert result == "Dataclass dataclass"