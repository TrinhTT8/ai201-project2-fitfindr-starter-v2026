"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    # ── Criterion 2: five different impossible queries ───────────────────────
    {
        # Fails on price: nothing in the data costs under $12.
        "name": "impossible: price",
        "query": "black leather jacket under $10",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Fails on size: no XS listings, and no "One Size" item is a velvet blazer.
        "name": "impossible: size",
        "query": "velvet blazer size XS",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Fails on keywords: no listing mentions sequins, ballgowns or feathers.
        "name": "impossible: keywords",
        "query": "sequin ballgown with feathers",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Price written in words, which _PRICE_RE doesn't recognize
        "name": "impossible: price in words",
        "query": "graphic tee under five dollars",
        "wardrobe": "example",
        "criterion": 2,
    },

    # ── Criterion 3: five different matching queries ────────────────────────
    {
        "name": "state: corduroy pants",       # top match lst_005
        "query": "corduroy wide leg pants under $40",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: linen blazer",         # top match lst_018
        "query": "cream linen blazer",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: platform sneakers",    # top match lst_019
        "query": "platform sneakers size US 8",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: leather belt",         # top match lst_014
        "query": "brown braided leather belt",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "state: tie-dye long sleeve",  # top match lst_040
        "query": "pastel tie dye long sleeve",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        "name": "fit card repetition",         # top match lst_002
        "query": "y2k butterfly baby tee under $20",
        "wardrobe": "example",
        "criterion": 4,
    },

    {
        # Equal to a listing's exact price: lst_006 costs $24 and must be included.
        "name": "price: exact listing price",
        "query": "graphic tee under $24",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Below the cheapest listing ($12), so the search should return [].
        "name": "price: below cheapest",
        "query": "leather belt under $10",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # A ceiling with cents.
        "name": "price: with cents",
        "query": "vintage tee under $29.99",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "price: ordinary budget, low",
        "query": "vintage shirt under $20",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "price: ordinary budget, high",
        "query": "denim under $40",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
