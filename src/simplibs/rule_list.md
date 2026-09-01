# Přehled pravidel a jejich konstruktorových parametrů

## `containers/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `AllOf`           | `*rules`                      |
| `AnyOf`           | `*rules`                      |
| `Compose`         | `transformer`, `validator`    |
| `ForEach`         | `rule`                        |
| `Regex`           | `pattern`                     |

## `containers/negations/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `Not`             | `rule`                        |
| `NoneOf`          | `*rules`                      |

## `base_logic/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `Is`              | `expected`                    |
| `IsIn`            | `options`                     |

## `base_logic/negations/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `IsNot`           | `forbidden`                   |
| `NotIn`           | `options`                     |

## `inspectors/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `HasAttribute`    | `attr_name`                   |
| `IsInstance`      | `*types`                      |
| `IsSubclass`      | `*types`                      |

## `inspectors/negations/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `NotHasAttribute` | `attr_name`                   |
| `NotInstance`     | `*types`                      |
| `NotSubclass`     | `*types`                      |

## `math_logic/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `Equals`          | `expected`                    |
| `GreaterOrEqual`  | `threshold`                   |
| `GreaterThan`     | `threshold`                   |
| `InRange`         | `min_val_`, `max_val`         |
| `LessOrEqual`     | `threshold`                   |
| `LessThan`        | `threshold`                   |

## `math_logic/arithmetic/`
| ----- Třída ----- | --------- Parametry ---------  |
|-------------------|--------------------------------|
| `CloseTo`         | `target`, `rel_tol`, `abs_tol` |
| `DivisibleBy`     | `divisor`                      |
| `HasRemainder`    | `divisor`, `remainder`         |

## `math_logic/negations/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `NotEquals`       | `forbidden`                   |

## `string_rules/`
| ---- Třída ----- | --------- Parametry --------- |
|------------------|-------------------------------|
| `Contains`       | `substring`                   |
| `EndsWith`       | `suffix`                      |
| `IsBlank`        | —                             |
| `NotBlank`       | —                             |
| `StartsWith`     | `prefix`                      |

## `collection_rules/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `AllUnique`       | —                             |
| `HasKey`          | `key`                         |
| `HasKeys`         | `*keys`                       |
| `IsSubsetOf`      | `reference`                   |
| `IsSupersetOf`    | `reference`                   |

## `specific_rules/checkers/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `IsEmpty`         | —                             |
| `IsFalse`         | —                             |
| `IsNone`          | —                             |
| `IsTrue`          | —                             |

## `specific_rules/checkers/negations/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `NotEmpty`        | —                             |

## `specific_rules/inspectors/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `HasLength`       | `exact`, `min_`, `max_`       |
| `IsCallable`      | —                             |
| `IsDataclass`     | —                             |
| `IsHashable`      | —                             |
| `IsIterable`      | —                             |
| `IsType`          | —                             |

## `specific_rules/numericals/`
| ----- Třída ----- | --------- Parametry --------- |
|-------------------|-------------------------------|
| `IsDecimal`       | —                             |
| `IsFloat`         | —                             |
| `IsInfinity`      | —                             |
| `IsInteger`       | —                             |
| `IsNan`           | —                             |
| `IsNumber`        | —                             |
| `IsPi`            | `decimal_places`              |
| `IsZero`          | —                             |
| `NotNan`          | —                             |
| `NotNumber`       | —                             |
| `NotZero`         | —                             |

