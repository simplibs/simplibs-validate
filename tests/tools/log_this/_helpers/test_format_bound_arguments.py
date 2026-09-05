import inspect
from simplibs.validate.tools.log_this._helpers import format_bound_arguments


def dummy_function(name: str, age: int, password: str = "secret") -> None:
    pass


def test_format_bound_arguments_basic() -> None:
    """Verify standard argument formatting using repr for non-masked values."""
    sig = inspect.signature(dummy_function)
    bound = sig.bind("chris", 30, "secret")
    bound.apply_defaults()

    result = format_bound_arguments(bound, exclude=())
    assert result == "name='chris', age=30, password='secret'"


def test_format_bound_arguments_with_masking() -> None:
    """Verify parameters listed in exclude are replaced with '***'."""
    sig = inspect.signature(dummy_function)
    bound = sig.bind("chris", 30, "secret")
    bound.apply_defaults()

    result = format_bound_arguments(bound, exclude=("password",))
    assert result == "name='chris', age=30, password=***"


def test_format_bound_arguments_args_kwargs() -> None:
    """Verify *args and **kwargs format correctly as tuples and dicts."""
    def variadic_function(*args: int, **kwargs: str) -> None:
        pass

    sig = inspect.signature(variadic_function)
    bound = sig.bind(1, 2, key="val")
    bound.apply_defaults()

    result = format_bound_arguments(bound, exclude=())
    assert result == "args=(1, 2), kwargs={'key': 'val'}"