def integer_rule(
    *,
    greater_than: int | UnsetType = UNSET,
    greater_or_equal: int | UnsetType = UNSET,
    less_than: int | UnsetType = UNSET,
    less_or_equal: int | UnsetType = UNSET,
    divisible_by_: int | UnsetType = UNSET,
    has_remainder_: tuple[int, int] | UnsetType = UNSET,  # (divisor, remainder)
    positive: bool = False,
    negative: bool = False,
    equals_: int | UnsetType = UNSET,
    not_equals_: int | UnsetType = UNSET,
    is_in_: tuple | UnsetType = UNSET,
    not_in_: tuple | UnsetType = UNSET,
) -> Rule:
    """Compose a Rule validating an integer against the given optional constraints."""
    parts: list[Rule] = [is_integer]

    if positive:
        parts.append(greater_than_rule(0))  # zkratka za GreaterThan(0)
    if negative:
        parts.append(less_than_rule(0))

    if greater_than is not UNSET:
        parts.append(greater_than_rule(greater_than))
    if greater_or_equal is not UNSET:
        parts.append(greater_or_equal_rule(greater_or_equal))
    if less_than is not UNSET:
        parts.append(less_than_rule(less_than))
    if less_or_equal is not UNSET:
        parts.append(less_or_equal_rule(less_or_equal))
    if divisible_by_ is not UNSET:
        parts.append(divisible_by(divisible_by_))
    if has_remainder_ is not UNSET:
        divisor, remainder = has_remainder_
        parts.append(has_remainder(divisor, remainder))
    if equals_ is not UNSET:
        parts.append(equals(equals_))
    if not_equals_ is not UNSET:
        parts.append(not_equals(not_equals_))
    if is_in_ is not UNSET:
        parts.append(is_in(is_in_))
    if not_in_ is not UNSET:
        parts.append(not_in(not_in_))

    return AllOf(*parts) if len(parts) > 1 else parts[0]