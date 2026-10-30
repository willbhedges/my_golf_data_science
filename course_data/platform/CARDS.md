# Scorecards: discovery and consensus

Reviewers traced most bad auto-built pages to the scorecard. The causes were a missing card (osm_back guesses that mix tee sets), a stale card (Finkbine, Harvester), a scrambled card (Eagle Bend golfify), swapped set names (WeaverRidge), and a card typed in metres (TPC Deere Run `card_review.json`, see below). This note covers two fixes: how cards are found without a search engine, and how disagreeing cards are settled on the OSM ground.

Code:
* `scorecard.py`: `derived_card_urls`, `golfify_urls`, `allsquare_urls`, `parse_allsquare`, `fetch_allsquare`, `page_matches`, `name_similarity` and `metres_to_yards`.
* `card_consensus.py`: settles disagreeing cards on the OSM ground.
* Tests: `test_card_consensus.py`, run on 14 reviewed courses (`fixtures/cards_consensus.json`, rebuilt by `fixtures/build_cards_consensus.py`).

## 1. Discovery without a search engine

DuckDuckGo bot-challenges the runner after about 2 queries. GolfPass returns 403, BlueGolf 405 and GolfLink refuses. Two sources do work, and both put the course page at a URL built from the name:

| site | URL | card data | match check |
|---|---|---|---|
| golfify | `golfify.io/courses/<name-slug>[-<town>]` | `__NEXT_DATA__` pageProps.tees[].holeInformation (yards) | facility state, clubName, lat/lon |
| AllSquare | `allsquaregolf.com/golf-courses/<state-name>/<name-slug>` | `__NEXT_DATA__` apolloState `Teebox.distances` (**yards**), `Scorecard.grid` (par, hcp, Men/Women groups), `lastEdit` | Club zipcode (`"IA 52242"` gives the state), name, lat/lon |

Slug variants are tried in this order:
1. The name as written.
2. Without "the-".
3. With "the-" (`the-harvester-golf-club`).
4. Without "Jr." (`a-l-gustin-golf-course`).
5. With initials merged.
6. "The Golf Club at X" as `x-golf-club`.
7. The core name with `-golf-course`, `-golf-club` and `-country-club`.
8. golfify only: the town forms `-<town>` (`st-andrews-golf-club-overland-park`).

`page_matches` checks each page against the course:
* **State.** It must match. This rejects both "Sycamore Ridge" pages, which are a 9-hole course in Goodview, VA.
* **Name.** The fuzzy token similarity must be at least 0.5.
* **Location.** When the page has coordinates, it must be within 8 km. Otherwise the town must match unless the names are identical.

**AllSquare units.** The rendered table shows **metres**, because the Meters toggle is active on first render: Finkbine Black reads 6417 there. The JSON holds yards (7017), and the parser reads the JSON. Without the JSON, `_allsquare_table` converts the table with `metres_to_yards`.

`fetch_package.fetch_scorecards` now tries the sources in this order: golfify (derived URLs first), AllSquare (derived), club site, OpenGolfAPI, then the search-based directories.

### Hit rate on the 18 reviewed courses

The courses are adams_pointe, buffalo_ridge, colbert_hills, creekmoor, dubs_dread, eagle_bend, falcon_ridge, finkbine, gustin, harvester, la_nickell, lake_shawnee, old_kinderhook, painted_hills, st_andrews_op, sycamore_ridge, tpc_deere_run and weaver_ridge.

A "correct card" is one for this course that the review accepts.

| source | before (library builds) | after (derived URLs, evidence already fetched) |
|---|---|---|
| golfify | 11/18 | 13/18 (+ weaver_ridge, dubs_dread: their pages exist at derived slugs; the builds missed them) |
| AllSquare | 0/18 (the search never ran or was challenged; the old `/<state>/<town>/<slug>/scorecard` pattern returns 404) | at least 6/18 (finkbine, harvester, gustin, la_nickell, adams_pointe, tpc_deere_run) |
| any card from golfify or AllSquare | 11/18 | **15/18** (+ adams_pointe, tpc_deere_run, weaver_ridge, dubs_dread) |
| wrong course accepted | 0 | 0 (sycamore_ridge rejected on both sites by state) |

Still missing:
* **old_kinderhook:** no page on either site. OpenGolfAPI plus the club site cover it.
* **colbert_hills:** golfify and AllSquare both return 404 for the derived slugs.
* **sycamore_ridge:** neither site lists the Kansas course. Its card is at the club site's /About#scorecard.

AllSquare pages for creekmoor, buffalo_ridge and dubs_dread returned 404 on the first slugs. The page may carry an `-<id>` suffix, which cannot be derived and still needs search.

**Pending.** The remaining derived URLs (58, in `course_data/requests/webfetch_cards_derived_v1.json`) were queued behind about 20 web-fetch runs. The results will land in `course_data/research/web/cards_derived_v1/`. Note that web_fetch.yml checks out the branch head rather than the triggering SHA, so a busy queue can make the run read another agent's request. If the directory never appears, re-push the request with "rev" bumped.

## 2. Consensus: `card_consensus.consensus(cards, ground)`

**Ground.** For each hole, the ground is the OSM hole-line length plus the OSM tee-box distances to the green:
* `ground_from_package` builds it from `package.json` (`tee_options`).
* `ground_from_summary` builds it at fetch time, from hole lines only. `fetch_scorecards` writes it, as advisory output, to `raw/scorecard_web.json["consensus"]`.

The steps:
1. **Units.** A card whose longest set runs at 0.84 to 0.95 times the ground, on most holes, is treated as metres and converted to yards, but only when that fits the ground better. The conversion is vetoed when another card's same-named sets agree with it as printed. This protects Painted Hills, where OpenGolfAPI lists only the White set.
2. **Swaps.** When two sets' rows sum to each other's stated totals, the rows are moved back under the right names and the card is flagged (WeaverRidge OpenGolfAPI: the "Gold" rows sum 6876 under Black 7000). When the OSM tee order says a "shorter" set is longer on at least 60% of the multi-tee holes, the card is flagged only.
3. **Base card.** Each card is scored by the share of hole/set values within 12 yd of a ground length, plus 0.05 for each other card that agrees with it. Among cards within 0.20 of the best score, the most reliable wins (typed card, then club site, golfify, AllSquare, OpenGolfAPI), then the most recent `card_date` (AllSquare `lastEdit`). A card that scores more than 0.25 below the best is flagged "stale or scrambled" and gives no per-hole values.
4. **Per hole.** A base value that misses the ground by more than 12 yd is replaced when another card's same set fits the ground by at least 8 yd better and is itself within 12 yd. "Same set" means the set totals are within 6%. When two cards agree on the base value, it is replaced only if it misses by at least 24 yd and the replacement is within 3 yd.

### Results on the reviewed cards

All 11 tests pass, as do the existing scorecard tests.

| course | consensus | review says |
|---|---|---|
| finkbine | golfify base. Black 1 = 375 (card 415), Black 10 = 410 (449), White 10 and 13 from OpenGolfAPI | Current club card: 1 = 375, 10 = 410. Match. Hole 9 (card 449) is still left at 449, because two cards agree and it misses by only 18 |
| harvester | Black 14 = 180 (card 230), Black 13 = 418 (390), Blue 14 = 155, Black 9 = 437 | 14: OSM box at 176 (OpenGolfAPI 180); 13: ground 409-414; 9: line start 437. Match |
| eagle_bend | golfify flagged scrambled (44% fit vs 89%); OpenGolfAPI base | golfify holes 2-9 are really 11-18. Match |
| weaver_ridge | OpenGolfAPI Gold/Black rows swapped back. Black now matches the review card on at least 14 of 18 holes | Labels swapped. Match |
| tpc_deere_run | `card_review.json` flagged as metres: 6646 m = 7267 yd, matching AllSquare's JSON 7268 | **The typed review card is in metres.** It needs retyping in yards; the review owner should fix it |
| painted_hills | No metres false positive; golfify base | golfify. Match |
| creekmoor, st_andrews_op, la_nickell, falcon_ridge, old_kinderhook, buffalo_ridge | At most 1 change | Cards accepted. Match |
| gustin | Gold 15 = 401 (golfify 350, misses by 46) from OpenGolfAPI | Not reviewed per hole |
| lake_shawnee | Nothing can be settled (OSM maps 4 holes) | Not applicable |

## Failure modes still open

* **AllSquare `-<id>` slugs** and **courses missing from both sites** (colbert_hills, old_kinderhook, sycamore_ridge) still need search or the club site.
* **golfify and AllSquare are often the same data.** At Finkbine both are stale, so their agreement is weak evidence, which is why the strong-replacement rule exists.
* **The ground is incomplete.** Unmapped back tees make a correct long value look wrong; tees are missing at Harvester 6 and 18 and Weaver 5. A mis-tagged OSM hole line can also make a wrong value look right. Consensus only replaces a value with a value another card actually printed. It never invents one.
* **OpenGolfAPI "Web" sets** duplicate golfify's longest set and trip the OSM-order swap flag (La Nickell). That flag is advisory only.
* **Recency** is known only for AllSquare (`lastEdit`). golfify and OpenGolfAPI carry no date, so reliability decides among near-equal cards.
* **Done:** `package.pick_scorecard` now uses `consensus(...)["card"]` for web cards, on build-time ground (`ground_from_fc`: OSM hole lines + tee boxes near each line start) when OSM maps at least 9 hole lines; otherwise it falls back to `choose_card`. A request / file / typed card still wins, and is only checked for metres (`check_units`). Consensus flags go to the package warnings.
