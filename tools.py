"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────
_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "under", "over", "in", "of"
}

def _keywords(text: str) -> set[str]:
    # Lowercase words worth matching on, stopwords removed.
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any (tokens.startswith("ONE SIZE") for tokens in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted = _keywords(description)
    if not wanted:
        return []

    scored = []
    for listing in load_listings():
        # Price ceiling is inclusive: a $30 item passes max_price=30.
        if max_price is not None and listing["price"] > max_price:
            continue
        if not _size_matches(size, listing["size"]):
            continue

        # A title hit counts double — the title is what the seller led with.
        title_words = _keywords(listing["title"])
        other_words = _keywords(" ".join([
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
            " ".join(listing["colors"]),
            listing["brand"] or "",   # brand is None for most listings
        ]))
        score = 2 * len(wanted & title_words) + len(wanted & other_words)

        if score > 0:
            scored.append((score, listing))

    # sorted() is stable, so equal scores keep their order in the data.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    item_text = _describe_item(new_item)
    items = (wardrobe or {}).get("items") or []

    if not items:
        prompt = (
            f"Someone is thinking about buying this thrifted item:\n{item_text}\n\n"
            "They haven't told us what's in their wardrobe. Give general styling "
            "advice for this item: two outfit ideas built around it, naming the "
            "kinds of pieces, colors, and occasions it works with."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {w['name']} ({w['category']}; colors: {', '.join(w['colors'])})"
            for w in items
        )
        prompt = (
            f"Someone is thinking about buying this thrifted item:\n{item_text}\n\n"
            f"Here is what they already own:\n{wardrobe_lines}\n\n"
            "Suggest one or two outfits that pair the new item with specific "
            "pieces from their wardrobe. Name each wardrobe piece exactly as it "
            "is written above, and say briefly why the combination works."
        )

    system = (
        "You are a friendly thrift stylist. Keep it practical and concise — "
        "a short paragraph or a few bullet points per outfit. Only name "
        "wardrobe pieces that were listed; never invent ones the user owns."
    )
    response = generate(prompt, system=system).strip()
    # The spec promises a non-empty string, even if the model sends nothing.
    return response or (
        f"Couldn't generate an outfit right now — try pairing the "
        f"{new_item.get('title', 'item')} with simple basics in neutral colors."
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # Guard first: no outfit means nothing to caption, so don't spend a model call.
    if not outfit or not outfit.strip():
        return (
            f"No outfit was provided for the {new_item.get('title', 'item')}, "
            "so a fit card couldn't be written."
        )

    prompt = (
        f"Write a caption for a social media post about this thrifted find:\n"
        f"{_describe_item(new_item)}\n\n"
        f"How it's being styled:\n{outfit}\n\n"
        f"Mention the item, the price (${new_item['price']:.0f}), and the "
        f"platform ({new_item['platform']}) once each."
    )
    system = (
        "You write captions people actually post about their thrift finds. "
        "Two to four sentences, casual and first-person, specific about the "
        "vibe of the outfit. Not a product description, no hashtag walls. "
        "Return only the caption."
    )
    return generate(prompt, system=system).strip() or (
        f"Thrifted the {new_item['title']} for ${new_item['price']:.0f} "
        f"on {new_item['platform']}."
    )


def _describe_item(item: dict) -> str:
    # One readable block of the listing fields the model needs.
    lines = [
        f"Title: {item.get('title')}",
        f"Category: {item.get('category')}",
        f"Colors: {', '.join(item.get('colors') or [])}",
        f"Style: {', '.join(item.get('style_tags') or [])}",
        f"Condition: {item.get('condition')}",
        f"Price: ${item.get('price')}",
        f"Platform: {item.get('platform')}",
    ]
    if item.get("brand"):
        lines.append(f"Brand: {item['brand']}")
    return "\n".join(lines)
