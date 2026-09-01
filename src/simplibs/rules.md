# >>> src/simplibs/validate/rules/containers/AllOf.py
all(rule(value) for rule in rules)

# >>> src/simplibs/validate/rules/containers/AnyOf.py
any(rule(value) for rule in rules)

# >>> src/simplibs/validate/rules/containers/Compose.py
rule(transformer(value))

# >>> src/simplibs/validate/rules/containers/ForEach.py
all(rule(item) for item in value)

# >>> src/simplibs/validate/rules/containers/NoneOf.py
not any(rule(value) for rule in rules)

# >>> src/simplibs/validate/rules/containers/Not.py
not rule(value)

# >>> src/simplibs/validate/rules/predicates/arithmetic/CloseTo.py
math.isclose(value, target, rel_tol, abs_tol)

# >>> src/simplibs/validate/rules/predicates/arithmetic/DivisibleBy.py
value % divisor == 0

# >>> src/simplibs/validate/rules/predicates/arithmetic/HasRemainder.py
value % divisor == remainder

# >>> src/simplibs/validate/rules/predicates/checkers/IsEmpty.py
len(value) == 0

# >>> src/simplibs/validate/rules/predicates/checkers/IsFalse.py
value is False

# >>> src/simplibs/validate/rules/predicates/checkers/IsNone.py
value is None

# >>> src/simplibs/validate/rules/predicates/checkers/IsTrue.py
value is True

# >>> src/simplibs/validate/rules/predicates/checkers/NotEmpty.py
len(value) > 0

# >>> src/simplibs/validate/rules/predicates/collections/AllUnique.py
len(set(value)) == len(value)

# >>> src/simplibs/validate/rules/predicates/collections/HasKey.py
key in value

# >>> src/simplibs/validate/rules/predicates/collections/HasKeys.py
all(key in value for key in keys)

# >>> src/simplibs/validate/rules/predicates/collections/IsContainer.py
isinstance(value, (list, tuple, set, frozenset, dict)) or isinstance(value, Container)

# >>> src/simplibs/validate/rules/predicates/collections/IsSubsetOf.py
set(value) <= reference

# >>> src/simplibs/validate/rules/predicates/collections/IsSupersetOf.py
set(value) >= reference

# >>> src/simplibs/validate/rules/predicates/comparisons/Equals.py
value == expected_value

# >>> src/simplibs/validate/rules/predicates/comparisons/GreaterOrEqual.py
value >= threshold

# >>> src/simplibs/validate/rules/predicates/comparisons/GreaterThan.py
value > threshold

# >>> src/simplibs/validate/rules/predicates/comparisons/InRange.py
min_val < value > max_val
min_val <= value >= max_val

# >>> src/simplibs/validate/rules/predicates/comparisons/LessOrEqual.py
value <= threshold

# >>> src/simplibs/validate/rules/predicates/comparisons/LessThan.py
value < threshold

# >>> src/simplibs/validate/rules/predicates/comparisons/NotEquals.py
value != forbidden

# >>> src/simplibs/validate/rules/predicates/introspection/HasAttribute.py
hasattr(value, attr_name)

# >>> src/simplibs/validate/rules/predicates/introspection/HasLength.py
value == length
value > min_length
value < max_length
min_length < value < max_length

# >>> src/simplibs/validate/rules/predicates/introspection/IsCallable.py
callable(value)

# >>> src/simplibs/validate/rules/predicates/introspection/IsDataclass.py
dataclasses.is_dataclass(value)

# >>> src/simplibs/validate/rules/predicates/introspection/IsHashable.py
hash(value)

# >>> src/simplibs/validate/rules/predicates/introspection/IsInstance.py
isinstance(value, types)

# >>> src/simplibs/validate/rules/predicates/introspection/IsIterable.py
iter(value)

# >>> src/simplibs/validate/rules/predicates/introspection/IsSubclass.py
issubclass(value, types)

# >>> src/simplibs/validate/rules/predicates/introspection/IsType.py
isinstance(value, type)

# >>> src/simplibs/validate/rules/predicates/logic/Is.py
value is expected

# >>> src/simplibs/validate/rules/predicates/logic/IsIn.py
value in options

# >>> src/simplibs/validate/rules/predicates/logic/IsNot.py
value is not forbidden

# >>> src/simplibs/validate/rules/predicates/logic/NotIn.py
value not in options

# >>> src/simplibs/validate/rules/predicates/numeric/IsDecimal.py
isinstance(value, Decimal)

# >>> src/simplibs/validate/rules/predicates/numeric/IsFloat.py
isinstance(value, float)

# >>> src/simplibs/validate/rules/predicates/numeric/IsInfinity.py
math.isinf(value)

# >>> src/simplibs/validate/rules/predicates/numeric/IsInteger.py
isinstance(value, int) and not isinstance(value, bool)

# >>> src/simplibs/validate/rules/predicates/numeric/IsNan.py
math.isnan(value)

# >>> src/simplibs/validate/rules/predicates/numeric/IsNumber.py
isinstance(value, (int, float, Decimal, complex)) and not isinstance(value, bool)

# >>> src/simplibs/validate/rules/predicates/numeric/IsPi.py
round(value, decimal_places) == round(math.pi, decimal_places)

# >>> src/simplibs/validate/rules/predicates/numeric/IsPrimitiveNumber.py
isinstance(value, (int, float)) and not isinstance(value, bool)

# >>> src/simplibs/validate/rules/predicates/numeric/IsZero.py
value == 0

# >>> src/simplibs/validate/rules/predicates/strings/Contains.py
substring in value

# >>> src/simplibs/validate/rules/predicates/strings/EndsWith.py
value.endswith(suffix)

# >>> src/simplibs/validate/rules/predicates/strings/IsBlank.py
value.strip() == ""

# >>> src/simplibs/validate/rules/predicates/strings/NotBlank.py
value.strip() != ""

# >>> src/simplibs/validate/rules/predicates/strings/Regex.py
re.compile(pattern).search(value) is not None

# >>> src/simplibs/validate/rules/predicates/strings/StartsWith.py
value.startswith(prefix)

