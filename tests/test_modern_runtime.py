"""Compatibility and precision regressions exercised by Redstone Squid."""

from decimal import Decimal

import pytest

from fluent_compiler.bundle import FluentBundle


@pytest.mark.parametrize("value", [1, 1.0, Decimal("1"), Decimal("1.0")])
def test_fraction_precision_affects_plural_category(value: object) -> None:
    bundle = FluentBundle.from_string(
        "en",
        """
label = { NUMBER($value, minimumFractionDigits: 1) ->
    [one] one
   *[other] other
}
    .display = { NUMBER($value, minimumFractionDigits: 1) }
""",
        use_isolating=False,
    )
    assert bundle.format("label", {"value": value}) == ("other", [])
    assert bundle.format("label.display", {"value": value}) == ("1.0", [])


def test_rounding_affects_plural_category_but_exact_variants_use_original_number() -> None:
    bundle = FluentBundle.from_string(
        "en",
        """
rounded = { NUMBER($value, maximumFractionDigits: 0) ->
    [one] one
   *[other] other
}
exact = { NUMBER($value, maximumFractionDigits: 0) ->
    [1.2] exact
    [one] one
   *[other] other
}
""",
        use_isolating=False,
    )
    assert bundle.format("rounded", {"value": Decimal("1.2")}) == ("one", [])
    assert bundle.format("exact", {"value": Decimal("1.2")}) == ("exact", [])


def test_generated_ast_handles_references_attributes_and_missing_arguments() -> None:
    bundle = FluentBundle.from_string(
        "en",
        """
-project = Squid
message = Hello { $name } from { -project }
    .label = Label
""",
        use_isolating=False,
    )
    assert bundle.format("message", {"name": "Alex"}) == ("Hello Alex from Squid", [])
    assert bundle.format("message.label") == ("Label", [])
    assert bundle.format("message")[1]
