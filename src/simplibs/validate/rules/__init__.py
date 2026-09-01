from types import SimpleNamespace

# Base class
from .base_class import Rule

# Containers
from .containers import (
    AllOf,
    AnyOf,
    Compose,
    ForEach,
    NoneOf,
    Not,
)

# Predicates — arithmetic
from .predicates.arithmetic import (
    CloseTo,
    DivisibleBy,
    HasRemainder,
)

# Predicates — checkers
from .predicates.checkers import (
    IsEmpty,
    IsFalse,
    IsNone,
    IsTrue,
    NotEmpty,
)

# Predicates — collections
from .predicates.collections import (
    AllUnique,
    HasKey,
    HasKeys,
    IsContainer,
    IsSubsetOf,
    IsSupersetOf,
)

# Predicates — comparisons
from .predicates.comparisons import (
    Equals,
    GreaterOrEqual,
    GreaterThan,
    InRange,
    LessOrEqual,
    LessThan,
    NotEquals,
)

# Predicates — introspection
from .predicates.introspection import (
    HasAttribute,
    HasLength,
    IsCallable,
    IsDataclass,
    IsHashable,
    IsInstance,
    IsIterable,
    IsSubclass,
    IsType,
)

# Predicates — logic
from .predicates.logic import (
    Is,
    IsIn,
    IsNot,
    NotIn,
)

# Predicates — numeric
from .predicates.numeric import (
    IsBool,
    IsDecimal,
    IsFloat,
    IsInfinity,
    IsInteger,
    IsNan,
    IsNumber,
    IsPi,
    IsPrimitiveNumber,
    IsZero,
)

# Predicates — strings
from .predicates.strings import (
    Contains,
    EndsWith,
    IsBlank,
    IsString,
    NotBlank,
    Regex,
    StartsWith,
)


# ============================================================================
# Rule shortcuts
# ============================================================================

# Parameterized rules are exposed as classes.
# Zero-parameter rules are exposed as pre-instantiated objects.
#
# This allows:
#
#     validate(value, is_integer & greater_than(0))
#
# instead of:
#
#     validate(value, IsInteger() & GreaterThan(0))


# ---- containers ------------------------------------------------------------

all_of              = AllOf             # *rules
any_of              = AnyOf             # *rules
compose             = Compose           # transformer, validator
for_each            = ForEach           # rule
none_of             = NoneOf            # *rules
negate              = Not               # rule


# ---- predicates/arithmetic -------------------------------------------------

close_to            = CloseTo           # target, *, rel_tol=1e-9, abs_tol=0.0
divisible_by        = DivisibleBy       # divisor
has_remainder       = HasRemainder      # divisor, remainder


# ---- predicates/checkers ---------------------------------------------------

is_empty            = IsEmpty()
is_false            = IsFalse()
is_none             = IsNone()
is_true             = IsTrue()
not_empty           = NotEmpty()


# ---- predicates/collections ------------------------------------------------

all_unique          = AllUnique()
has_key             = HasKey            # key
has_keys            = HasKeys           # *keys
is_container        = IsContainer()
is_subset_of        = IsSubsetOf        # reference
is_superset_of      = IsSupersetOf      # reference


# ---- predicates/comparisons ------------------------------------------------

equals              = Equals            # expected_value
greater_or_equal    = GreaterOrEqual    # threshold
greater_than        = GreaterThan       # threshold
in_range            = InRange           # min_val, max_val, include_min=True,
                                        # include_max=True
less_or_equal       = LessOrEqual       # threshold
less_than           = LessThan          # threshold
not_equals          = NotEquals         # forbidden


# ---- predicates/introspection ----------------------------------------------

has_attribute       = HasAttribute      # attr_name
has_length          = HasLength         # length=None, *, min_length=None,
                                        # min_length=None, max_length=None
is_callable         = IsCallable()
is_dataclass        = IsDataclass()
is_hashable         = IsHashable()
is_instance         = IsInstance        # *types
is_iterable         = IsIterable()
is_subclass         = IsSubclass        # *types
is_type             = IsType()


# ---- predicates/logic ------------------------------------------------------

same_as             = Is                # expected
is_in               = IsIn              # options
is_not              = IsNot             # forbidden
not_in              = NotIn             # options


# ---- predicates/numeric ----------------------------------------------------

is_bool             = IsBool()
is_decimal          = IsDecimal()
is_float            = IsFloat()
is_infinity         = IsInfinity()
is_integer          = IsInteger()
is_nan              = IsNan()
is_number           = IsNumber()
is_pi               = IsPi              # decimal_places
is_primitive_number = IsPrimitiveNumber()
is_zero             = IsZero()


# ---- predicates/strings ----------------------------------------------------

contains            = Contains          # substring
ends_with           = EndsWith          # suffix
is_blank            = IsBlank()
is_string           = IsString()
not_blank           = NotBlank()
regex               = Regex             # pattern
starts_with         = StartsWith        # prefix


# ============================================================================
# Grouped namespaces
# ============================================================================

# All concrete Rule classes.
#
# Useful when the class itself is required, for example for subclassing,
# isinstance checks, introspection, or programmatic rule construction.

rule_class = SimpleNamespace(
    # containers
    AllOf=AllOf,
    AnyOf=AnyOf,
    Compose=Compose,
    ForEach=ForEach,
    NoneOf=NoneOf,
    Not=Not,

    # arithmetic
    CloseTo=CloseTo,
    DivisibleBy=DivisibleBy,
    HasRemainder=HasRemainder,

    # checkers
    IsEmpty=IsEmpty,
    IsFalse=IsFalse,
    IsNone=IsNone,
    IsTrue=IsTrue,
    NotEmpty=NotEmpty,

    # collections
    AllUnique=AllUnique,
    HasKey=HasKey,
    HasKeys=HasKeys,
    IsContainer=IsContainer,
    IsSubsetOf=IsSubsetOf,
    IsSupersetOf=IsSupersetOf,

    # comparisons
    Equals=Equals,
    GreaterOrEqual=GreaterOrEqual,
    GreaterThan=GreaterThan,
    InRange=InRange,
    LessOrEqual=LessOrEqual,
    LessThan=LessThan,
    NotEquals=NotEquals,

    # introspection
    HasAttribute=HasAttribute,
    HasLength=HasLength,
    IsCallable=IsCallable,
    IsDataclass=IsDataclass,
    IsHashable=IsHashable,
    IsInstance=IsInstance,
    IsIterable=IsIterable,
    IsSubclass=IsSubclass,
    IsType=IsType,

    # logic
    Is=Is,
    IsIn=IsIn,
    IsNot=IsNot,
    NotIn=NotIn,

    # numeric
    IsBool=IsBool,
    IsDecimal=IsDecimal,
    IsFloat=IsFloat,
    IsInfinity=IsInfinity,
    IsInteger=IsInteger,
    IsNan=IsNan,
    IsNumber=IsNumber,
    IsPi=IsPi,
    IsPrimitiveNumber=IsPrimitiveNumber,
    IsZero=IsZero,

    # strings
    Contains=Contains,
    EndsWith=EndsWith,
    IsBlank=IsBlank,
    IsString=IsString,
    NotBlank=NotBlank,
    Regex=Regex,
    StartsWith=StartsWith,
)


# All public snake_case rule shortcuts.
#
# Every attribute points to the same object as its corresponding module-level
# shortcut. Zero-parameter rules are shared instances; parameterized rules
# refer to their classes.

rules = SimpleNamespace(
    # containers
    all_of=all_of,
    any_of=any_of,
    compose=compose,
    for_each=for_each,
    none_of=none_of,
    negate=negate,

    # arithmetic
    close_to=close_to,
    divisible_by=divisible_by,
    has_remainder=has_remainder,

    # checkers
    is_empty=is_empty,
    is_false=is_false,
    is_none=is_none,
    is_true=is_true,
    not_empty=not_empty,

    # collections
    all_unique=all_unique,
    has_key=has_key,
    has_keys=has_keys,
    is_container=is_container,
    is_subset_of=is_subset_of,
    is_superset_of=is_superset_of,

    # comparisons
    equals=equals,
    greater_or_equal=greater_or_equal,
    greater_than=greater_than,
    in_range=in_range,
    less_or_equal=less_or_equal,
    less_than=less_than,
    not_equals=not_equals,

    # introspection
    has_attribute=has_attribute,
    has_length=has_length,
    is_callable=is_callable,
    is_dataclass=is_dataclass,
    is_hashable=is_hashable,
    is_instance=is_instance,
    is_iterable=is_iterable,
    is_subclass=is_subclass,
    is_type=is_type,

    # logic
    same_as=same_as,
    is_in=is_in,
    is_not=is_not,
    not_in=not_in,

    # numeric
    is_bool=is_bool,
    is_decimal=is_decimal,
    is_float=is_float,
    is_infinity=is_infinity,
    is_integer=is_integer,
    is_nan=is_nan,
    is_number=is_number,
    is_pi=is_pi,
    is_primitive_number=is_primitive_number,
    is_zero=is_zero,

    # strings
    contains=contains,
    ends_with=ends_with,
    is_blank=is_blank,
    is_string=is_string,
    not_blank=not_blank,
    regex=regex,
    starts_with=starts_with,
)

# __all__ = [
#     "Rule",
#     "rule_class",
#     "rules",
# ]


# ============================================================================
# Public exports
# ============================================================================

__all__ = [
    "Rule",
    "rule_class",
    "rules",

    # containers
    "AllOf",
    "AnyOf",
    "Compose",
    "ForEach",
    "NoneOf",
    "Not",

    # arithmetic
    "CloseTo",
    "DivisibleBy",
    "HasRemainder",

    # checkers
    "IsEmpty",
    "IsFalse",
    "IsNone",
    "IsTrue",
    "NotEmpty",

    # collections
    "AllUnique",
    "HasKey",
    "HasKeys",
    "IsContainer",
    "IsSubsetOf",
    "IsSupersetOf",

    # comparisons
    "Equals",
    "GreaterOrEqual",
    "GreaterThan",
    "InRange",
    "LessOrEqual",
    "LessThan",
    "NotEquals",

    # introspection
    "HasAttribute",
    "HasLength",
    "IsCallable",
    "IsDataclass",
    "IsHashable",
    "IsInstance",
    "IsIterable",
    "IsSubclass",
    "IsType",

    # logic
    "Is",
    "IsIn",
    "IsNot",
    "NotIn",

    # numeric
    "IsBool",
    "IsDecimal",
    "IsFloat",
    "IsInfinity",
    "IsInteger",
    "IsNan",
    "IsNumber",
    "IsPi",
    "IsPrimitiveNumber",
    "IsZero",

    # strings
    "Contains",
    "EndsWith",
    "IsBlank",
    "IsString",
    "NotBlank",
    "Regex",
    "StartsWith",

    # shortcuts
    "all_of",
    "any_of",
    "compose",
    "for_each",
    "none_of",
    "negate",
    "close_to",
    "divisible_by",
    "has_remainder",
    "is_empty",
    "is_false",
    "is_none",
    "is_true",
    "not_empty",
    "all_unique",
    "has_key",
    "has_keys",
    "is_container",
    "is_subset_of",
    "is_superset_of",
    "equals",
    "greater_or_equal",
    "greater_than",
    "in_range",
    "less_or_equal",
    "less_than",
    "not_equals",
    "has_attribute",
    "has_length",
    "is_callable",
    "is_dataclass",
    "is_hashable",
    "is_instance",
    "is_iterable",
    "is_subclass",
    "is_type",
    "same_as",
    "is_in",
    "is_not",
    "not_in",
    "is_bool",
    "is_decimal",
    "is_float",
    "is_infinity",
    "is_integer",
    "is_nan",
    "is_number",
    "is_pi",
    "is_primitive_number",
    "is_zero",
    "contains",
    "ends_with",
    "is_blank",
    "is_string",
    "not_blank",
    "regex",
    "starts_with",
]


# ============================================================================
# Design notes
# ============================================================================

_DESIGN_NOTES = """
# rules — Central Rule Namespace

This module is the main public entry point for the validation rules provided
by `simplibs-validate`.

It exposes three complementary interfaces:

1. Concrete rule classes
2. Readable snake_case shortcuts
3. Grouped namespaces for programmatic access


## 1. Rule shortcuts

Parameterized rules are exposed as their classes:

    greater_than = GreaterThan
    regex = Regex
    is_instance = IsInstance

The caller supplies the required configuration:

    validate(value, greater_than(0))
    validate(value, regex(r"^[a-z]+$"))
    validate(value, is_instance(int))

Zero-parameter rules are exposed as pre-instantiated objects:

    is_integer = IsInteger()
    is_string = IsString()
    is_none = IsNone()

They can therefore be used directly:

    validate(value, is_integer)
    validate(value, is_string & not_empty)
    validate(value, is_none | is_string)


## 2. Composition

Because Rule implements the `&`, `|`, and `~` operators, shortcuts can be
combined directly into declarative validation expressions:

    is_integer & greater_or_equal(0) & less_than(100)

    is_string & not_empty & starts_with("user_")

    is_none | is_instance(dict)

    ~(is_string & is_blank)

The operators correspond to:

    &  -> logical AND
    |  -> logical OR
    ~  -> logical NOT


## 3. Grouped namespaces

### `rule_class`

Contains every concrete Rule subclass under its original class name:

    rule_class.IsInteger
    rule_class.GreaterThan
    rule_class.Regex

This namespace is intended for programmatic access when the actual class is
required, such as subclass checks, introspection, or dynamic construction.


### `rules`

Contains every public snake_case shortcut:

    rules.is_integer
    rules.greater_than
    rules.regex

It is functionally equivalent to importing the shortcuts directly:

    from simplibs.validate.rules import is_integer

    # or

    from simplibs.validate.rules import rules
    rules.is_integer

Both references point to the same underlying object for zero-parameter
rules, or to the same underlying class for parameterized rules.


## 4. Naming policy

Rule shortcuts use descriptive snake_case names derived from the semantics
of the rule.

Names are intentionally not abbreviated. The goal is to keep composed
validation expressions readable and self-describing:

    is_string & not_empty & has_length(min_length=3)

is preferred over an abbreviated form such as:

    is_str & nonempty & length(...)

The public API therefore favors clarity and discoverability over minimizing
individual identifier length.


## 5. Keyword-related names

Python keywords cannot be used as ordinary identifiers. Where necessary,
the public name uses a descriptive alternative:

    Is      -> same_as
    Not     -> negate

The `is_in` and `is_not` names remain valid Python identifiers because they
are compound names rather than the keywords themselves.


## 6. Rule reference tables

### `containers/`

| Shortcut   | Parameters               | Logic                              |
|------------|--------------------------|------------------------------------|
| `all_of`   | `*rules`                 | All rules must pass.               |
| `any_of`   | `*rules`                 | At least one rule must pass.       |
| `compose`  | `transformer, validator` | Validate the transformed value.    |
| `for_each` | `rule`                   | The rule must pass for every item. |
| `none_of`  | `*rules`                 | No rule may pass.                  |
| `negate`   | `rule`                   | The rule must fail.                |


### `predicates/arithmetic/`

| Shortcut        | Parameters                             | Logic                                   |
|-----------------|----------------------------------------|-----------------------------------------|
| `close_to`      | `target, *, rel_tol=1e-9, abs_tol=0.0` | Value is approximately equal to target. |
| `divisible_by`  | `divisor`                              | `value % divisor == 0`                  |
| `has_remainder` | `divisor, remainder`                   | `value % divisor == remainder`          |


### `predicates/checkers/`

| Shortcut    | Parameters | Logic             |
|-------------|------------|-------------------|
| `is_empty`  | —          | `len(value) == 0` |
| `is_false`  | —          | `value is False`  |
| `is_none`   | —          | `value is None`   |
| `is_true`   | —          | `value is True`   |
| `not_empty` | —          | `len(value) > 0`  |


### `predicates/collections/`

| Shortcut         | Parameters  | Logic                                 |
|------------------|-------------|---------------------------------------|
| `all_unique`     | —           | All values are unique.                |
| `has_key`        | `key`       | The key exists in the value.          |
| `has_keys`       | `*keys`     | All specified keys exist.             |
| `is_container`   | —           | Value is a supported container.       |
| `is_subset_of`   | `reference` | Value is a subset of the reference.   |
| `is_superset_of` | `reference` | Value is a superset of the reference. |


### `predicates/comparisons/`

| Shortcut           | Parameters                                             | Logic                                   |
|--------------------|--------------------------------------------------------|-----------------------------------------|
| `equals`           | `expected_value`                                       | `value == expected_value`               |
| `greater_or_equal` | `threshold`                                            | `value >= threshold`                    |
| `greater_than`     | `threshold`                                            | `value > threshold`                     |
| `in_range`         | `min_val, max_val, include_min=True, include_max=True` | Value lies within the configured range. |
| `less_or_equal`    | `threshold`                                            | `value <= threshold`                    |
| `less_than`        | `threshold`                                            | `value < threshold`                     |
| `not_equals`       | `forbidden`                                            | `value != forbidden`                    |


### `predicates/introspection/`

| Shortcut        | Parameters                                         | Logic                                       |
|-----------------|----------------------------------------------------|---------------------------------------------|
| `has_attribute` | `attr_name`                                        | Attribute exists on the value.              |
| `has_length`    | `length=None, *, min_length=None, max_length=None` | Value has the specified length or range.    |
| `is_callable`   | —                                                  | Value is callable.                          |
| `is_dataclass`  | —                                                  | Value is a dataclass instance or class.     |
| `is_hashable`   | —                                                  | Value is hashable.                          |
| `is_instance`   | `*types`                                           | `isinstance(value, types)`                  |
| `is_iterable`   | —                                                  | Value is iterable.                          |
| `is_subclass`   | `*types`                                           | Value is a subclass of the specified types. |
| `is_type`       | —                                                  | Value is a type object.                     |


### `predicates/logic/`

| Shortcut  | Parameters  | Logic                    |
|-----------|-------------|--------------------------|
| `same_as` | `expected`  | `value is expected`      |
| `is_in`   | `options`   | `value in options`       |
| `is_not`  | `forbidden` | `value is not forbidden` |
| `not_in`  | `options`   | `value not in options`   |


### `predicates/numeric/`

| Shortcut              | Parameters       | Logic                                                    |
|-----------------------|------------------|----------------------------------------------------------|
| `is_bool`             | —                | Value is a `bool`.                                       |
| `is_decimal`          | —                | Value is a `Decimal`.                                    |
| `is_float`            | —                | Value is a `float`.                                      |
| `is_infinity`         | —                | Value is infinite.                                       |
| `is_integer`          | —                | Value is an integer but not a boolean.                   |
| `is_nan`              | —                | Value is NaN.                                            |
| `is_number`           | —                | Value is a supported numeric type other than `bool`.     |
| `is_pi`               | `decimal_places` | Value equals π to the specified precision.               |
| `is_primitive_number` | —                | Value is a primitive integer or float, excluding `bool`. |
| `is_zero`             | —                | `value == 0`                                             |


### `predicates/strings/`

| Shortcut      | Parameters  | Logic                                        |
|---------------|-------------|----------------------------------------------|
| `contains`    | `substring` | Substring occurs in the value.               |
| `ends_with`   | `suffix`    | Value ends with the suffix.                  |
| `is_blank`    | —           | String contains only whitespace or is empty. |
| `is_string`   | —           | Value is a `str`.                            |
| `not_blank`   | —           | String contains non-whitespace characters.   |
| `regex`       | `pattern`   | Regex search finds a match in the string.    |
| `starts_with` | `prefix`    | Value starts with the prefix.                |
"""