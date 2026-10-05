"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    trace.start_trace()  # fresh numbering for every run
    session = new_session(query, wardrobe)
    session["parsed"] = parse_query(query)
    parsed = session["parsed"]
    trace.step(
        "parse_query",
        inputs=query,
        returned=f"description={parsed['description']!r}, "
                 f"size={parsed['size']!r}, max_price={parsed['max_price']!r}",
    )

    # Each pass runs one tool, then looks at what it returned to pick the next.
    next_step = "search"
    count = 0
    while next_step != "done":
        count += 1
        trace.check_iterations(count)

        if next_step == "search":
            session["search_results"] = search_listings(
                parsed["description"], parsed["size"], parsed["max_price"]
            )

            # THE BRANCH: nothing found → explain what to change and stop here.
            if not session["search_results"]:
                session["error"] = _no_results_message(parsed)
                next_step = "done"
                note = "branch: empty, stopping before suggest_outfit"
            else:
                session["selected_item"] = session["search_results"][0]
                next_step = "suggest"
                note = f"branch: found, selected_item = {_item_label(session['selected_item'])}"

            trace.step(
                "search_listings",
                inputs=f"description={parsed['description']!r}, "
                       f"size={parsed['size']!r}, max_price={parsed['max_price']!r}",
                returned=session["search_results"],
                note=note,
            )

        elif next_step == "suggest":
            # The id logged here is read from the session — the same value the
            # tool receives — so the trace can be checked against selected_item.
            item = session["selected_item"]
            session["outfit_suggestion"] = suggest_outfit(item, session["wardrobe"])
            trace.step(
                "suggest_outfit",
                inputs=f"item={_item_label(item)}, "
                       f"wardrobe={len(session['wardrobe'].get('items') or [])} items",
                returned=session["outfit_suggestion"],
            )
            next_step = "fit_card"

        elif next_step == "fit_card":
            item = session["selected_item"]
            session["fit_card"] = create_fit_card(session["outfit_suggestion"], item)
            trace.step(
                "create_fit_card",
                inputs=f"item={_item_label(item)}, outfit=session['outfit_suggestion']",
                returned=session["fit_card"],
            )
            next_step = "done"

    return session


def _item_label(item: dict) -> str:
    # The id is what criterion 3 compares; the title is for a human reading along.
    return f"{item['id']} ({item['title']})"


# ── query parsing ─────────────────────────────────────────────────────────────

# "under $30", "below 30", "less than $30", "max $30", "up to 30", or a bare "$30"
_PRICE_RE = re.compile(
    r"(?:(?:under|below|less than|max|up to|<)\s*\$?|\$)\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
# "size M", "size: XXS", "size US 9", "size W30 L30", "size one size"
_SIZE_RE = re.compile(
    r"\bsize:?\s+(one size|us\s*\d+(?:\.\d+)?|w\d+(?:\s*l\d+)?|[a-z]{1,4})\b",
    re.IGNORECASE,
)
# Conversational words that would otherwise become search keywords.
_FILLER_RE = re.compile(
    r"\b(?:i'm|im|i am|i|a|an|the|looking|look|for|want|wanna|need|find|me|some|something|"
    r"please|can|you|show|get)\b",
    re.IGNORECASE,
)


def parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of a plain-language query,
    with regex — no model call. Missing size or price come back as None.

        "vintage graphic tee under $30, size M"
            → {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}
    """
    text = query or ""

    price_match = _PRICE_RE.search(text)
    max_price = float(price_match.group(1)) if price_match else None
    if price_match:
        text = text.replace(price_match.group(0), " ")

    size_match = _SIZE_RE.search(text)
    size = size_match.group(1).upper() if size_match else None
    if size_match:
        text = text.replace(size_match.group(0), " ")

    text = _FILLER_RE.sub(" ", text)
    description = " ".join(re.sub(r"[^\w\s'-]", " ", text).split())

    return {"description": description, "size": size, "max_price": max_price}


def _no_results_message(parsed: dict) -> str:
    # Name what the user can actually change, based on what they asked for.
    tips = []
    if parsed["max_price"] is not None:
        tips.append(f"raise your max price above ${parsed['max_price']:.0f}")
    if parsed["size"]:
        tips.append(f"try a size other than {parsed['size']}")
    if parsed["description"]:
        tips.append(f"use different or fewer keywords than \"{parsed['description']}\"")
    else:
        tips.append("describe the item you want, like \"vintage graphic tee\"")
    return "No listings matched. You could " + ", or ".join(tips) + "."


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
