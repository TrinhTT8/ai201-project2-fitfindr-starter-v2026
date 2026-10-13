# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

In this repo, the user will be able to search for a thirfted product within the provided listings and receive outfit recommendations as well as a generated caption post for their social media. The user will need to tell the model what they are looking for, such as "vintage graphic tee under $20, size M", and the application will search for the matching listings and feed the best one to the model. The model will provide two outfit recommendations to the user and a unique caption related to the style of the outfits.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** This tool searches the catalog of 40 listings and returns the items that best match the user's keywords, filtered by size and price when given.
- **Inputs:** `description` (str, required): keywords for the item; `size` (str or None, optional): matched case-insensitively against whole size tokens, so "M" matches "S/M" but "S" does not match "US 9", and "One Size" listings always match; `max_price` (float or None, optional): price ceiling in US dollars, inclusive
- **Returns:** A list of up to 10 listing dicts, best match first, each with `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand` (often None) and `platform`
- **When it has nothing:** Returns an empty list `[]` (not None, not an exception). The agent then puts a message in the session telling the user to change their inputs.

### `suggest_outfit`

- **What it does:** Asks the model to suggest one or two outfits built around a single thrifted item, combining it with specific pieces the user already owns in their wardrobe.
- **Inputs:** `new_item` (dict): one listing dict, the item the user is considering, with fields like `title`, `category`, `colors`, `style_tags` and `price`; `wardrobe` (dict): a dict with an `items` key holding a list of the user's clothing items (this list may be empty).
- **Returns:** A non-empty string (str) containing one or two outfit suggestions, each naming the new item plus specific pieces from `wardrobe['items']` and how to wear them together.
- **When it has nothing:** If `wardrobe['items']` is empty, it doesn't raise or return `""`. It returns a non-empty string of general styling advice for the item instead (what kinds of pieces, colors and occasions it pairs well with).

### `create_fit_card`

- **What it does:** Asks the model to write a short, casual social-media caption about the thrifted find and how it's styled. It should read like a real post, not a product description, and come out differently on each run.
- **Inputs:** `outfit` (str): the outfit suggestion string returned by `suggest_outfit()`; `new_item` (dict): the listing dict for the item, with fields like `title`, `price`, `platform`, `colors` and `style_tags`.
- **Returns:** A non-empty string (str): a two-to-four sentence caption that mentions the item, its price and its platform once each, and is specific about the vibe of the outfit.
- **When it has nothing:** If `outfit` is empty or whitespace-only, it doesn't raise or call the model. It returns a non-empty descriptive message saying no outfit was provided, so a caption couldn't be written.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings return an empty list, put a message in the session suggesting the user change their max price, try another size, or use different keywords and stop the run without calling suggest_outfit or create_fit_card. Otherwise, store the first best result in session["selected_item"] and pass it to suggest_outfit, then create_fit_card.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The query is parsed using regex. <!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** The query is parsed into session["parsed"] (description, size, max_price), which search_listings uses; its results go into session["search_results"]. The loop picks the first result as session["selected_item"]. suggest_outfit takes selected_item and session["wardrobe"] and stores its outfit string in session["outfit_suggestion"]. create_fit_card takes outfit_suggestion and selected_item and stores the caption in session["fit_card"]. If the search comes back empty, session["error"] is set and the later fields stay None. <!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $130, size XL'

```

Found: Oversized Crewneck Sweatshirt — Vintage Navy — $20.0 on thredUp

Outfit: Here are two great ways to style your new vintage navy crewneck:

- **Casual Denim-on-Denim:** Pair the vintage navy crewneck with your baggy straight-leg jeans, dark wash, and chunky white sneakers, accented by the brown leather belt and black crossbody bag. This creates a classic, effortless monochrome blue look where the white sneakers add a crisp, fresh pop of contrast.
- **Smart-Casual Contrast:** Style the oversized crewneck sweatshirt — vintage navy over your wide-leg khaki trousers, finished with black combat boots and the black crossbody bag. The deep navy pairs naturally with warm khaki for a preppy, grounded vibe, while the combat boots add a cool edge to the tailored trousers.

Fit card: Scored this vintage navy crewneck on thredUp for just $20 and it's already my new entire personality. I'm living in it with baggy jeans and chunky sneakers for lazy coffee runs, but it looks surprisingly sick dressed up with wide-leg trousers and boots. Truly nothing beats a heavy, broken-in sweatshirt that looks like it actually has a history.

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
```

[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand':None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
```

Here are a couple of ways to style those vintage Levi's:

- **Streetwear Casual:** Pair the medium wash jeans with the white ribbed tank top, layered under the oversized grey crewneck sweatshirt. Finish the look with chunky white sneakers and the black crossbody bag for an effortless, everyday vibe that plays on classic streetwear proportions.
- **Edgy Denim on Denim:** Contrast the blue wash by pairing the jeans with the black cropped zip hoodie and the vintage black denim jacket. Ground the outfit with black combat boots and cinch it together using the brown leather belt for a cool, textured monochrome contrast.

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
```

Nothing beats finding the holy grail pair of vintage Levi's 501s while randomly scrolling on Depop. Snagged these for $38 and they fit like an absolute dream with just my beat-up white sneakers and ababy tee. The wash is pure casual perfection and I'm never taking them off.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- _What I asked for:_ I asked Claude to analyze my criterias and evaluate whether they are measurables and will provide a good guidelines to the model.
- _What came back:_ It gave me a thorough analysis of my crtierias and explained which one has poor wordings that would make my criterias impossible to test.
- _What I changed:_ Based on Claude's feedback, I revised my criterias accordingly by providing more details and adjusting the testing logic.

**Moment 2**

- _What I asked for:_ I asked Claude to assist me with writing the tools' functions and had it created a template for me to fill out the variables/logics.
- _What came back:_ It wrote the templates and inserted them at the corresponding spots. The templates have placeholder sections for me to go through and fill out.
- _What I changed:_ I finished the functions by filling out all the placeholder sections while reading through Claude's explanations.

**Moment 3 (unit 4)**

- _What I asked for:_ I asked Claude to check if my `mcp_server.py` did what the file asked for.
- _What came back:_ It said the tool was registered and worked, but my description said it returns a message when nothing matches when it actually returns `[]`, and my Tool Inventory listed `title` as an input instead of `size` and `max_price`.
- _What I changed:_ I had Claude fix the description and the Tool Inventory, then I swapped the agent's direct call for the MCP call myself.

**Moment 4 (unit 4)**

- _What I asked for:_ I asked Claude to score my before run and fill in the run log.
- _What came back:_ It marked criterion 2 as MISSED (4/5). I had marked it 5/5 because I only looked at one impossible query. It also found that most fit cards open with "Scored", which my criterion 4 didn't catch.
- _What I changed:_ I kept the MISSED verdict, added a revision to criterion 4, and picked the price-in-words bug as my one fix.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion                                              | Target                                         | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict             |
| ------------------------------------------------------ | ---------------------------------------------- | ----- | ----- | ----- | ----- | ----- | ------------------- |
| 1. Matching query completes all three tools            | 4 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |
| 2. Impossible query stops before `suggest_outfit`      | 5 of 5                                         | PASS  | PASS  | PASS  | FAIL  | PASS  | MISSED (4/5)        |
| 3. Selected item `id` matches across session and trace | 5 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |
| 4. Fit cards on the same item don't repeat sentences   | At most 1 of 10 caption pairs share a sentence | PASS  | PASS  | PASS  | PASS  | PASS  | MET (0 of 10 pairs) |
| 5. Search results stay within `max_price`              | 5 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |

Source: `results/run_2026-10-12_1509_before.md`, produced by `run_eval.py::main` (5 tries per scenario, caching off, temperature 0.9).

How the tries map to scenarios in `scenarios.py`:

- **Criterion 1:** the 5 tries of `vintage graphic tee under $30`.
- **Criterion 2:** try 1 of each of 5 different impossible queries, in the order `criteria.md` lists them: price (`black leather jacket under $10`), size (`velvet blazer size XS`), keywords (`sequin ballgown with feathers`), price in words (`graphic tee under five dollars`), combined (`designer ballgown size XXS under $5`). The search has no randomness, so all 5 tries of each scenario came out the same.
- **Criterion 3:** try 1 of each of 5 different matching queries (`lst_005`, `lst_018`, `lst_019`, `lst_014`, `lst_040`). All 25 tries passed.
- **Criterion 4:** the 5 captions from `y2k butterfly baby tee under $20` (`lst_002`). Each try is PASS because its caption shares no sentence with any of the other four.
- **Criterion 5:** try 1 of each of 5 price ceilings: exact listing price ($24), below cheapest ($10), with cents ($29.99), and two ordinary budgets ($20, $40).

**Real output from one try**, pasted as text, naming the file and function
that produced it:

**Criterion 1:** `agent.py::run_agent`, query `vintage graphic tee under $30`, try 1. The trace shows all three tools ran, and `tools.py::create_fit_card` returned:

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Vintage Graphic Hoodie — Faded Black … +7 more
      →    branch: found, selected_item = lst_006 (Graphic Tee — 2003 Tour Bootleg Style)
[3] suggest_outfit
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), wardrobe=10 items
      out: Here are two cool, grungy ways to style your new graphic tee:  *   **Outfit 1:** Pair the Graphic Tee — 2003 T…
[4] create_fit_card
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), outfit=session['outfit_suggestion']
      out: Scored this 2003 tour bootleg tee on depop for just $24 and I'm obsessed. It has that perfectly worn-in grunge…

Fit card: Scored this 2003 tour bootleg tee on depop for just $24 and I'm obsessed. It has that perfectly worn-in grunge vibe that looks so good layered under a black hoodie with baggy denim. Total streetwear steal.
```

**Criterion 2:** `agent.py::run_agent`, the miss: query `graphic tee under five dollars`, try 1. The price was never parsed, so the agent didn't stop:

```
[1] parse_query
      in:  graphic tee under five dollars
      out: description='graphic tee under five dollars', size=None, max_price=None
[2] search_listings (via MCP)
      in:  description='graphic tee under five dollars', size=None, max_price=None
      out: 6 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey … +3 more
      →    branch: found, selected_item = lst_006 (Graphic Tee — 2003 Tour Bootleg Style)
[3] suggest_outfit
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), wardrobe=10 items
      out: Here are a couple of ways to style your new graphic tee!  * **Outfit 1:** Pair the Graphic Tee with your baggy…
[4] create_fit_card
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), outfit=session['outfit_suggestion']
      out: Scored this sick 2003 tour bootleg graphic tee on depop for just $24 and I'm obsessed. Threw it on with some b…
```

**Criterion 3:** `agent.py::run_agent`, query `corduroy wide leg pants under $40`, try 1. `lst_005` is the first search result, the `selected_item`, and the item going into both `suggest_outfit` and `create_fit_card`:

```
[2] search_listings (via MCP)
      in:  description='corduroy wide leg pants', size=None, max_price=40.0
      out: 5 items: Corduroy Wide-Leg Pants — Rust, Wide-Leg Linen Trousers — Natural, Low-Rise Cargo Pants — Khaki … +2 more
      →    branch: found, selected_item = lst_005 (Corduroy Wide-Leg Pants — Rust)
[3] suggest_outfit
      in:  item=lst_005 (Corduroy Wide-Leg Pants — Rust), wardrobe=10 items
[4] create_fit_card
      in:  item=lst_005 (Corduroy Wide-Leg Pants — Rust), outfit=session['outfit_suggestion']
```

**Criterion 4:** `tools.py::create_fit_card`, query `y2k butterfly baby tee under $20`, tries 1 and 4. These are the closest pair: the openings are similar, but no sentence matches word for word. The other three captions are in the results file.

```
1. Scored this little butterfly tee on depop for just $18 and I’m so obsessed. The pastel pink and purple print gives major 2000s mallrat energy, especially paired with baggy denim and chunky sneakers. It’s tiny, nostalgic, and the exact kind of baby tee I've been hunting for.
4. Scored this little butterfly print Y2K baby tee on depop for just $18 and I’m obsessed. It gives major off-duty model energy when I style it with baggy dark wash jeans and chunky sneakers, but it's equally cute toughened up with combat boots and a denim jacket. Absolute steal for the closet.
```

**Criterion 5:** `tools.py::search_listings` (called over MCP), query `graphic tee under $24`, try 1. The $24 item is included, so the ceiling is inclusive:

```
[2] search_listings (via MCP)
      in:  description='graphic tee', size=None, max_price=24.0
      out: 4 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey … +1 more
      →    branch: found, selected_item = lst_006 (Graphic Tee — 2003 Tour Bootleg Style)

Returned prices: 24.0, 18.0, 19.0, 15.0 (ceiling 24.0)
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| #   | Criterion                                           | Target                                         | Verdict       | How I decided                                                                                                                                                                                                                                                                              |
| --- | --------------------------------------------------- | ---------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Matching query completes all three tools            | 4 of 5                                         | MET (5/5)     | All 5 traces show `parse_query`, `search_listings`, `suggest_outfit` and `create_fit_card`, and every try ended with a non-empty fit card.                                                                                                                                                 |
| 2   | Impossible query stops before `suggest_outfit`      | 5 of 5                                         | MISSED (4/5)  | Price, size, keywords and combined each stopped after `search_listings` with a message naming what to change. `graphic tee under five dollars` ran all four steps and wrote a fit card.                                                                                                    |
| 3   | Selected item `id` matches across session and trace | 5 of 5                                         | MET (5/5)     | For each query, the first title in the search output, the `selected_item` id, and the item id in the `suggest_outfit` and `create_fit_card` steps were the same (`lst_005`, `lst_018`, `lst_019`, `lst_014`, `lst_040`).                                                                   |
| 4   | Fit cards on the same item don't repeat sentences   | At most 1 of 10 caption pairs share a sentence | MET (0 of 10) | I split each caption on `.`, `!` and `?`, lowercased it and removed extra spaces, then compared all 10 pairs. None shared a sentence. The openings are similar ("Scored this little…") but no full sentence repeats. Against the revised criterion (see Diagnoses), it's MISSED (3 of 10). |
| 5   | Search results stay within `max_price`              | 5 of 5                                         | MET (5/5)     | No returned price was over the ceiling. The $24 item was included at a $24 ceiling, the $10 ceiling returned `[]`, and $29.99 returned only items at $27 or less.                                                                                                                          |

**Diagnoses**

**Criterion 2 missed on 1 of 5: the price written in words.** The miss happened in the **session**, before the search ran. `_PRICE_RE` in `agent.py` only matches digits, so for `graphic tee under five dollars`, `parse_query` set `session["parsed"]["max_price"]` to `None`. With no price ceiling, `search_listings` returned 6 graphic tees, and the branch correctly continued to `suggest_outfit`. The $5 budget was lost at parsing, which is the risk I predicted in `criteria.md`.

**Criterion 4: MET as written, but it measured the wrong thing** (revised in `criteria.md`). No two captions share a whole sentence, but they follow one template: 49 of 65 fit cards in the run open with "Scored". The cause is the **model's output**, steered by my prompt in `tools.py::create_fit_card`: asking for a casual first-person caption that mentions the price and platform pushes the model toward "Scored this [item] on [platform] for just $[price]". Against the revised criterion, tries 1, 4 and 5 all open "scored this little", so it's **MISSED (3 of 10 pairs, target at most 1)**.

**Pattern:** Both findings come from a step passing along something narrower than I assumed, without any error. `parse_query` drops a price it can't read, and the fit card prompt gets the same opening back each time. In both cases the tool did exactly what it was told, and nothing crashed. The problem was in what went into it: the parsed query, or the prompt's wording.

**Were my other targets too easy?** Criteria 3 and 5 test plain Python with no model and no randomness, so 5 of 5 was the only honest target, and they held. Criterion 1 is the one I'd tighten. It met 5 of 5 against a 4 of 5 target, but all five tries used the same easy query (`vintage graphic tee under $30`). My reason for allowing one miss was that "some phrasings will miss", yet the scenario never varied the phrasing. A stronger version would use five differently worded matching queries and still expect 4 of 5.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Vintage Graphic Hoodie — Faded Black … +7 more
      →    branch: found, selected_item = lst_006 (Graphic Tee — 2003 Tour Bootleg Style)
[3] suggest_outfit
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), wardrobe=10 items
      out: **Outfit 1: 90s Grunge Streetwear** * **Top:** Graphic Tee — 2003 Tour Bootleg Style * **Bottoms:** Baggy stra…
[4] create_fit_card
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), outfit=session['outfit_suggestion']
      out: Scored this bootleg tour tee for just $24 on depop and honestly haven't taken it off since. It’s got that perf…
```

**Empty search**

```
$ python app.py ask 'vintage graphic tee under $1' --trace
[1] parse_query
      in:  vintage graphic tee under $1
      out: description='vintage graphic tee', size=None, max_price=1.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=1.0
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

  No listings matched. You could raise your max price above $1, or use different or fewer keywords than "vintage graphic tee".
```

The empty search stops after step 2, so it never reaches `suggest_outfit` or `create_fit_card`, and makes 0 model calls.

**On the MCP move:** I swapped the direct `search_listings(...)` call in `agent.py::run_agent` for `call_tool("search_listings", {...})`, so the search now goes through `mcp_server.py`. Nothing behaved differently after: the same queries returned the same results, and no match still returns `[]`, so the empty-search branch still works.

### Failure Modes

**1. Empty search.** Query: `'vintage graphic tee under $1'` (trace above).
The agent said: _"No listings matched. You could raise your max price above $1, or use different or fewer keywords than "vintage graphic tee"."_
No handler needed: the branch in `agent.py::run_agent` already stops before `suggest_outfit` and names what to change.

**2. Empty wardrobe.** Query: `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe --trace`

```
[3] suggest_outfit
      in:  item=lst_006 (Graphic Tee — 2003 Tour Bootleg Style), wardrobe=0 items
      out: That 2003 tour bootleg tee is a fantastic, versatile find for building effortless grunge and streetwear looks.…
```

The agent gave general styling advice instead of naming wardrobe pieces: _"The Off-Duty Streetwear Look: Pair the graphic tee with baggy denim jeans and chunky sneakers…"_ and _"The Edgy Night-Out Look: Tuck the tee into a leather skirt or sleek black trousers…"_. The fit card was still written.
No handler needed: `tools.py::suggest_outfit` checks for an empty `wardrobe["items"]` and asks the model for general advice instead.

**3. Model unavailable.** I changed one character of my key in `.env`, then ran a new query: `python app.py ask 'black shirt under $40' --trace`

```
[3] suggest_outfit
      in:  item=lst_003 (Oversized Flannel Shirt — Plaid Red/Black), wardrobe=10 items
      →    model unavailable, stopping before create_fit_card

  Found lst_003 (Oversized Flannel Shirt — Plaid Red/Black), but couldn't get outfit ideas because the model couldn't be reached. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. If your key is fine, the service may be busy — try again in a few minutes.
```

**Handler added.** Before, nothing in `run_agent` caught `ModelUnavailable`. The only reason there was no stack trace was the catch-all in `app.py::main`, which printed `ModelUnavailable: ...` and exited the whole program. I added a `try/except ModelUnavailable` around both model calls in `agent.py::run_agent` (`suggest_outfit` and `create_fit_card`). Each one sets `session["error"]` to a message naming what broke and what to do, logs the failure as a trace step, and ends the loop, so `run_agent` returns the session normally instead of crashing.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** `agent.py::parse_query` now reads prices written as words. A new `_WORD_PRICE_RE` finds a number word after "under", "below", "less than", "max" or "up to" (0–99, such as "five" or "twenty-five", plus "hundred"), with an optional "dollars" or "bucks". It rewrites the price as digits ("under five dollars" becomes "under $5") before the existing `_PRICE_RE` runs. Prices written with digits are parsed exactly as before. Nothing else changed.

**Which failure it was meant to fix:** Criterion 2's miss. `graphic tee under five dollars` lost its $5 budget at parsing (`max_price=None`), so the search returned 6 tees and the agent never stopped.

### Run Log — After

| Criterion                                              | Target                                         | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict             |
| ------------------------------------------------------ | ---------------------------------------------- | ----- | ----- | ----- | ----- | ----- | ------------------- |
| 1. Matching query completes all three tools            | 4 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |
| 2. Impossible query stops before `suggest_outfit`      | 5 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |
| 3. Selected item `id` matches across session and trace | 5 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |
| 4. Fit cards on the same item don't repeat sentences   | At most 1 of 10 caption pairs share a sentence | PASS  | PASS  | PASS  | PASS  | PASS  | MET (0 of 10 pairs) |
| 5. Search results stay within `max_price`              | 5 of 5                                         | PASS  | PASS  | PASS  | PASS  | PASS  | MET (5/5)           |

Source: `results/run_2026-10-12_2323_after.md`, produced by `run_eval.py::main` with the same scenarios, 5 tries each, caching off, temperature 0.9. Tries map to scenarios the same way as in the before run.

Criterion 2's fixed try (query `graphic tee under five dollars`, try 1), from `agent.py::run_agent`:

```
[1] parse_query
      in:  graphic tee under five dollars
      out: description='graphic tee', size=None, max_price=5.0
[2] search_listings (via MCP)
      in:  description='graphic tee', size=None, max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

No listings matched. You could raise your max price above $5, or use different or fewer keywords than "graphic tee".
```

**Did it help, and how do I know:** Yes. Criterion 2 went from MISSED (4/5) to MET (5/5), and nothing else changed. The price-in-words query now parses as `max_price=5.0` and stops after the search in all 5 tries. Criteria 1, 3 and 5 got the same results as before, and no try crashed. I also checked that the other 17 scenario queries parse exactly as they did before the change.

The revised criterion 4 also moved, from 3 of 10 pairs sharing an opening to 1 of 10, but that wasn't the fix: I didn't touch the fit card prompt. It's the model varying between runs. Across the whole after run, 48 of 60 fit cards still open with "Scored" (80%), compared with 49 of 65 (75%) before, so the template problem is still there.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

All five original criteria are met after the fix, but a few things are still not right:

- **Fit card template (criterion 4, revised).** Most fit cards still open with "Scored this… for just $…" (48 of 60 in the after run). It passed 1 of 10 in the after run only by chance. I would rewrite the `create_fit_card` prompt so it doesn't push the model into the same opening. I stopped there because this milestone allowed one change, and I used it on the price parsing.
- **Size parsing bug.** "one size bag" gets parsed as `size='BAG'` because `_SIZE_RE` grabs any short word after "size". I would make "one size" match first and only accept real sizes. I found it while testing the price fix and left it so I didn't change two things at once.
- **Criterion 1 is too easy.** All five tries used the same query. I would test it with five differently worded queries, but I didn't get to it in this unit.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
