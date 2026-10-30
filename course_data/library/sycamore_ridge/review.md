# Sycamore Ridge Golf Club (Spring Hill, KS): course check (rv09)

**No scorecard found.** golfify's and AllSquare's "Sycamore Ridge" pages are a 9-hole course in Goodview, VA. OpenGolfAPI lists Sycamore Ridge (Spring Hill) as par 72 with no hole data. The club site keeps its card at /About#scorecard (a second fetch is queued: course_data/requests/webfetch_rv09_cards2.json). Every hole is a CHECK only because there is no card.

The page renders cleanly (qa_page.js: 18 holes, 0 problems). Every hole was inspected on the page photos with the OSM greens, hole lines and tees overlaid. All 18 OSM greens exist, each hole line runs from its tee to its own green, and the routing is coherent.

| hole | verdict | note |
|---|---|---|
| 1-13, 15-18 | OK (yardage unverified) | Routing and green match the photo. The tee is the OSM tee at the start of the hole line. |
| 14 | **wrong par** | OSM tags it par 3, but it measures 399 yds (404 along the OSM line). It is a par 4: two par 3s in a row at 13 and 14 would be unlikely, and with 14 as a par 4 the course totals 72, matching OpenGolfAPI. The page shows a par-3 green box at "play it like 393" and gives no tee-shot pick. |

Fix: hole 14 par 4 (review.json). This needs a typed card or a par override, not an OSM geometry supplement, because the hole, tee and green are mapped correctly. OSM `dist` tags on this course are shuffled between holes and should not be used as a card.

Verdict: **not safe to publish as-is.** Hole 14 is wrong, and no hole yardage can be checked against a card.
