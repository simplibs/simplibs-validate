Pojďme to nejdřív zmapovat jako přehled (kolik skupin, co by do nich patřilo), a pak ti ukážu dva rozpracované příklady (`string`, `integer`), jak jsi chtěl.

## Nejdřív jeden gap, na který jsem narazil při mapování

Chybí nám obecné **`IsBool`** pravidlo (`isinstance(value, bool)`). Máme jen `IsTrue`/`IsFalse` (identitu ke konkrétní hodnotě), ne "je to vůbec bool". Pro vrstvu 3 `boolean(...)` by se to hodilo. Zmiňuju to hned na začátku, ať víš, že to bude potřeba doplnit do vrstvy 1, než půjde `boolean(...)` postavit pořádně.

---

## Přehled skupin (kolik jich reálně je)

| Skupina | Základní typová kontrola | Kandidáti na volitelné parametry |
|---|---|---|
| `string` | `IsString` | `min_length`, `max_length`, `length`, `starts_with`, `ends_with`, `contains`, `pattern` (Regex), `blank` (povolit/zakázat), `equals`, `not_equals`, `is_in`, `not_in` |
| `integer` | `IsInteger` | `greater_than`, `greater_or_equal`, `less_than`, `less_or_equal`, `in_range` (min,max), `divisible_by`, `has_remainder` (divisor, remainder), `equals`, `not_equals`, `is_in`, `not_in`, `positive`, `negative` (pohodlné zkratky) |
| `float` | `IsFloat` | totéž co `integer` (kromě `divisible_by`/`has_remainder`) + `close_to` (target, tolerance), `finite` (zakáže NaN/Infinity) |
| `number` | `IsNumber`/`IsPrimitiveNumber` | jako `float`, obecněji přes `int`/`float`/`Decimal` |
| `boolean` | *(chybí — viz výše)* | `equals` (True/False) |
| `none` | `IsNone` | — *(triviální, asi zbytečná vrstva 3, viz níže)* |
| `container` / `collection` | `IsContainer` (nebo `IsIterable`) | `min_length`, `max_length`, `length`, `all_unique`, `is_subset_of`, `is_superset_of`, `for_each` (pravidlo na každý prvek — mocné, skládá vrstvu 3 s vrstvou 1/2) |
| `mapping` / `dict_` | `IsInstance(dict)` | `has_key`, `has_keys`, `min_length`/`max_length` — key/value validace je pokročilejší (viz poznámka níže) |
| `callable` | `IsCallable` | — *(triviální)* |
| `type_` / `class_` | `IsType` | `is_subclass_of` (*types) |
| `hashable` | `IsHashable` | — *(triviální)* |
| `dataclass` | `IsDataclass` | `has_attribute` |
| `comparable` | *(žádná typová kontrola)* | `greater_than`, `less_than`, `in_range`, `equals`, `is_in`... — obecný "skladač" bez vynucení typu, pro Decimal/datetime/vlastní třídy |

**Triviální skupiny** (`none`, `callable`, `hashable`) — u těch je otázka, jestli vůbec stojí za samostatnou funkci vrstvy 3, když nemají žádné parametry navíc a jsou to jen aliasy na vrstvu 2. Klidně je vynech a nech uživatele použít přímo `is_none`/`is_callable`.

**`mapping`** je složitější — validace klíčů/hodnot by chtěla `ForEach` aplikované na `dict.keys()`/`dict.values()` přes `Compose`, což je legitimní, ale je to už kombinace dvou kontejnerů najednou. Bych to nechal jako "později", ne v první vlně.

---

## Rozpracovaný příklad 1: `string`

```python
from simplibs.sentinels import UNSET, UnsetType
from ..rules.base_class import Rule
from ..rules.containers import AllOf
from ..rules import (
    is_string, has_length, starts_with, ends_with,
    contains, regex, not_blank, equals, not_equals,
    is_in, not_in,
)


def string_rule(
    *,
    min_length: int | UnsetType = UNSET,
    max_length: int | UnsetType = UNSET,
    length: int | UnsetType = UNSET,
    starts_with_: str | UnsetType = UNSET,
    ends_with_: str | UnsetType = UNSET,
    contains_: str | UnsetType = UNSET,
    pattern: str | UnsetType = UNSET,
    blank: bool = True,  # False => vyžaduje not_blank
    equals_: str | UnsetType = UNSET,
    not_equals_: str | UnsetType = UNSET,
    is_in_: tuple | UnsetType = UNSET,
    not_in_: tuple | UnsetType = UNSET,
) -> Rule:
    """Compose a Rule validating a string against the given optional constraints."""
    parts: list[Rule] = [is_string]

    if length is not UNSET:
        parts.append(has_length(length=length))
    else:
        if min_length is not UNSET or max_length is not UNSET:
            kwargs = {}
            if min_length is not UNSET:
                kwargs["min_length"] = min_length
            if max_length is not UNSET:
                kwargs["max_length"] = max_length
            parts.append(has_length(**kwargs))

    if starts_with_ is not UNSET:
        parts.append(starts_with(starts_with_))
    if ends_with_ is not UNSET:
        parts.append(ends_with(ends_with_))
    if contains_ is not UNSET:
        parts.append(contains(contains_))
    if pattern is not UNSET:
        parts.append(regex(pattern))
    if not blank:
        parts.append(not_blank)
    if equals_ is not UNSET:
        parts.append(equals(equals_))
    if not_equals_ is not UNSET:
        parts.append(not_equals(not_equals_))
    if is_in_ is not UNSET:
        parts.append(is_in(is_in_))
    if not_in_ is not UNSET:
        parts.append(not_in(not_in_))

    return AllOf(*parts) if len(parts) > 1 else parts[0]


def validate_string(value, **kwargs):
    from ..validate import validate
    return_bool = kwargs.pop("return_bool", False)
    return_value = kwargs.pop("return_value", False)
    return validate(
        value, string_rule(**kwargs),
        return_bool=return_bool, return_value=return_value,
    )
```

**Poznámka k pojmenování parametrů:** `starts_with_`, `not_equals_` atd. mají koncové podtržítko, protože stejnojmenné funkce (`starts_with`, `not_equals`...) importuješ z vrstvy 2 do stejného modulu — kolize jmen. Buď to řešit podtržítky, nebo importovat vrstvu 2 s prefixem (`from ..rules import starts_with as _starts_with`). Řekni, který styl preferuješ, než to sjednotím napříč všemi skupinami.

---

## Rozpracovaný příklad 2: `integer`

```python
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
```

Všimni si, že `positive=True` + `greater_or_equal=5` zároveň by dalo `AllOf(IsInteger(), GreaterThan(0), GreaterOrEqual(5))` — logicky nekolidující (druhé je striktnější), takže bych to nechal projít bez chyby. Kdyby ale zadal `positive=True, negative=True` zároveň, to už je čistý logický nesmysl (nic nemůže projít) — tady by možná stálo za to udělat explicitní guard a vyhodit `ParamError`, podobně jako u `HasLength`.

---

## Co bych chtěl, abys mi potvrdil, než navrhnu zbytek

1. **Konvence pojmenování parametrů** kolidujících se jmény z vrstvy 2 (`starts_with_` vs. import s aliasem) — jak výše.
2. **Sjednocený vzor pro "flags místo hodnot"** (jako `positive`/`negative`, `blank=False`) — chceš tenhle styl pohodlných zkratek všude, kde to dává smysl, nebo raději jen čisté 1:1 mapování na parametry pravidel bez extra zkratek?
3. **Kam přesně tenhle kód umístit** — navrhoval jsem dřív `composed/` nebo `typed/`, potvrď/uprav název balíčku.
4. Mám **doplnit `IsBool`** do vrstvy 1 (a s ním `boolean(...)` do vrstvy 3), nebo to zatím necháme stranou?

Až tohle ujasníme, napíšu zbytek skupin (`float`/`number`, `container`, `type_`...) ve stejném stylu.