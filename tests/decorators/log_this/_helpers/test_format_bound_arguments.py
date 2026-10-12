import inspect
from simplibs.validate.decorators.log_this._helpers import build_repr_func, format_bound_arguments


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


def test_format_bound_arguments_uses_given_repr_func() -> None:
    """Verify every non-masked value goes through the supplied repr_func."""
    sig = inspect.signature(dummy_function)
    bound = sig.bind("chris", 30)
    bound.apply_defaults()

    result = format_bound_arguments(bound, exclude=(), repr_func=lambda value: f"<{value}>")
    assert result == "name=<chris>, age=<30>, password=<secret>"


def test_format_bound_arguments_masked_value_never_reaches_repr_func() -> None:
    """Verify a masked value is not even rendered, let alone logged."""
    rendered: list[object] = []

    def spy(value: object) -> str:
        rendered.append(value)
        return repr(value)

    sig = inspect.signature(dummy_function)
    bound = sig.bind("chris", 30, "secret")
    bound.apply_defaults()

    format_bound_arguments(bound, exclude=("password",), repr_func=spy)
    assert "secret" not in rendered
    assert rendered == ["chris", 30]


def test_format_bound_arguments_with_bounded_repr() -> None:
    """Verify a bounded repr keeps a huge argument short."""
    def collect(root: str, paths: list[int]) -> None:
        pass

    sig = inspect.signature(collect)
    bound = sig.bind("/p", list(range(1000)))
    bound.apply_defaults()

    result = format_bound_arguments(bound, exclude=(), repr_func=build_repr_func(2))
    assert result == "root='/p', paths=[0, 1, ...] (1000 items)"
