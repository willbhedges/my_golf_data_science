# World Woods / Cabot Citrus Farms: rebuild QA, Geofabrik OSM (2026-11-03)

**Verdict: BLOCKED.** The page has 16 holes, not 18 (2 and 13 are missing), and its pars sum to 64 against the card's
72. OSM has no `golf=hole` ways here. All 16 holes were placed by routing inference ("v2+structure"), and 11 of them
are flagged ambiguous. On the photos, most hole lines run through the pines or parallel to the real fairway, not
along it. It cannot be fixed by tees or layers. The course needs hand-routed hole ways, or a decision about which
Cabot Citrus course this request means.

Page checked: `course_data/library/world_woods/page.html`, GitHub Actions run 41539188571 (built 2026-11-03T00:13Z).
Both solved sets (Black, Silver) were run through `qa_page.js`: 16 holes each, phone and desktop, 0 page problems. I
looked at every phone hole picture and drew the package lines, tees and zones on all 12 par 4s and par 5s.

## OSM source and resolve

* `raw/summary.json` → `osm_source`: `{"source": "geofabrik", "reason": "thin fetch on every mirror and no cached
  snapshot: used as is", "mirror": "geofabrik:FL"}`. Counts: **0 holes**, 39 greens, 162 tees, 144 bunkers, 40
  fairways. 39 greens means two or more courses' greens are inside the boundary. Geofabrik did return hole ways for
  IA and LA, so this looks like OSM itself has no hole ways here, not an extract bug. I could not compare it with
  Overpass (no snapshot; the sandbox cannot reach it).
* The request was "World Woods Pine Barrens" near 28.665, -82.460. It resolved to OSM way/410646892 "Cabot Citrus
  Farms" (centre 28.6856, -82.4786), about 2.9 km from the `near` point, with a resolve score of 0.38. The card is
  golfify "cabot-citrus-farms" (Black 7,562, par 72, flag "1 Yellow(W) 300 < Green(M) 334"). It is not clear which
  of the property's courses (Karoo, the former Pine Barrens, or Wild Rye) this card or this boundary is.

## Holes (Black; inferred = routing CHECK)

| hole | par / yds | routing | verdict |
|---|---|---|---|
| 1 | 4 / 475 | inferred (66%) | **wrong.** The line runs through rough and trees between two fairways |
| 2 | (5?) | not built | **missing** |
| 3 | 3 / 292 | inferred (78%) | **doubtful.** A 292-yd par 3 off a walk-back tee 54 yds from any box |
| 4 | 5 / 511 | inferred (78%) | **wrong.** The line is right of the fairway, and the walk-back tees are in the pines |
| 5 | 4 / 382 | inferred (78%) | **wrong.** The line runs through the pines between two fairways |
| 6 | 5 / 563 | inferred (80%) | **wrong.** It runs diagonally through tree clumps |
| 7 | 3 / 199 | OSM structure ok | OK (tee_axis CHECK) |
| 8 | 4 / 426 | ok | doubtful. It crosses waste sand and trees, with the fairway to the right |
| 9 | 4 / 421 | ok | plausible, along the right edge of a fairway |
| 10 | 3 / 242 | inferred (15%) | doubtful (walk-back tee 48 yds from a box) |
| 11 | 4 / 427 | inferred (47%) | **wrong.** It runs parallel to the fairway, 40+ yds right of it, in rough |
| 12 | 4 / 496 | ok | **wrong.** The tee and line are in the pines right of the fairway |
| 13 | (?) | not built | **missing** |
| 14 | 5 / 581 | inferred (77%) | **wrong.** It is offset right of the fairway |
| 15 | 4 / 388 | inferred (92%) | **wrong.** It runs through woods |
| 16 | 3 / 201 | ok | OK |
| 17 | 5 / 500 | inferred (78%) | **wrong.** It runs through dense woods |
| 18 | 4 / 489 | inferred (83%) | doubtful. It runs along the pond edge with the fairway to the left |

Silver plays the same lines. Its picks therefore inherit the same routing errors.

## Next fix

1. Decide what the request means. World Woods Pine Barrens is now Cabot Citrus Farms' Karoo course. Re-request it
   by that name, with a `near` point on that course and the Karoo card.
2. Hand-route the 18 holes (`osm_supplement.geojson` hole ways from each tee to its green, with card numbering)
   and rebuild with `ignore_osm_holes`. Until then, do not publish.
