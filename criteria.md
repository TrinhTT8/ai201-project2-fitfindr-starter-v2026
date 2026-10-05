# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. _"The agent handles errors"_ is an opinion.
_"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"_ is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; _"80% seemed reasonable"_ does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**

<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

Some phrasing will not contain fuzzy keywords, so 4 out of 5 is a reasonable metrics considering if the keyword is found in 4 other tries.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

Each try uses a different impossible query: one that fails on price, one on
size, one on keywords, one that states the price in a form `_PRICE_RE` doesn't
recognize (e.g. "under five dollars"), and one that combines constraints.

**Why this target:**

<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

Stopping is a plain if in run_agent that checks for an empty list from search_listings. No model makes that decision, so unlike criterion 1, there's no fuzzy matching to forgive and it should behave the same every time. If it ever fails, the likely cause is the parsing step dropping a constraint like the size or price, which loosens the search enough to return something. Since the same query would give the same answer all five times, each try uses a different query so each one can fail in its own way.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

Across 5 different matching queries, the listing `id` in `session["selected_item"]` is the `id` of `session["search_results"][0]`, and it is the same `id` the trace shows going into `suggest_outfit` and into `create_fit_card` — in 5 of 5 tries.

**Why this target:**

Passing state involves no model and no randomness. It's plain Python reading values back out of the session dict, so it should never vary between runs. Any mismatch at all means a real bug, such as a stale value from an earlier step or an overwritten variable, and it would show up looking like a bad outfit or caption rather than a state problem. So anything less than 5 of 5 isn't acceptable. The `id` has to be the first result, not just any result, because the agent's rule is to use the top match, and "one of the results" would still pass if the wrong one were picked. Each try uses a different query so the compared `id`s actually change between tries.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

Across 5 runs of create_fit_card on the same item, at most 1 of the 10 pairs of captions shares a sentence word-for-word. A sentence is text split on `.`, `!` or `?`; two sentences match if they are identical after lowercasing and removing emoji and extra spaces.

**Why this target:**

A caption is supposed to feel like a fresh post, so getting the same sentences back defeats the point of asking for one. The caption comes from the model, though, and short captions about the same item can land on a common phrase by chance (like "Thrifted this for $18!"), so one repeated pair is tolerable. I count pairs rather than captions because a shared sentence always involves two captions, so "4 of 5 captions" would really have meant 5 of 5. More than one repeated pair wouldn't be chance: since `run_eval.py` turns the cache off, it would mean `TEMPERATURE` is too low in `config.py` or my prompt is pushing the model toward a fixed template, which is exactly what this target is meant to catch.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

Given a `max_price`, every listing `search_listings` returns has a `price` at or below that `max_price` (inclusive), and when no listing is priced at or below it, `search_listings` returns an empty list — in 5 of 5 tries. Each try uses a different ceiling: one equal to an exact listing price, one below the cheapest listing, one with cents (e.g. `29.99`), and two ordinary budgets.

**Why this target:**

The price filter is a plain numeric comparison in my own code, with no model and no fuzzy matching involved, so it should give the same right answer every time. A user who sets a budget and sees an item over it would stop trusting the search, and a single over-budget result means the filter is broken. Returning an empty list rather than None matters too, because the planning loop branches on that empty list. The ceilings vary because the same one would pass identically five times; the exact-price and below-cheapest cases test the `<=` boundary and the empty-list path, which are where a bug would actually show.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
