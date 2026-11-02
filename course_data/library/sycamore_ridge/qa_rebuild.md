# Sycamore Ridge Golf Club (Spring Hill KS): rebuild QA (2026-11-02)

**Verdict: NEEDS FIX.** The review's only fix (hole 14 par 4) was **not applied**: the page still shows hole 14 as a
"Par 3 · 364 yds" with a green box and "play it like 384". The page also still has no card: the set is named
"osm_back" and every hole reads "no card yardage / no card par". A matching card has since been fetched (see below).

Page checked: `course_data/library/sycamore_ridge/page.html`, built 2026-11-01T21:18Z. One solved set (`osm_back`).
This is a single-set page, so `qa_page.js` was run without the set argument (with it, the run times out on the hidden
picker). 18 holes, phone and desktop, 0 page problems. I looked at every phone hole picture. Routing and greens look as
reviewed.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 14: par 4, not par 3 (OSM-tagged par 3 at 399 yds) | **no.** The request carried `par_overrides {"14": 4}`, but `package.py apply_card_overrides()` returns at once when there is no card (`if not card or not (yo or po): return card`). So par overrides are dropped on card-less builds. The package keeps `par: 3`, provenance `par: osm`. |
| Get the club card (`webfetch_rv09_cards2.json`) | **fetched, not used.** See below. |

## The card now in the repo

`course_data/research/web/rv09_cards2/00.txt` is golfify `sycamore-ridge-golf-course`, Spring Hill KS (Jim Colbert /
Baxter Spann, 2000). Black 7,081 / Blue 6,465 / White 5,907 / Green 5,262 / Yellow 4,539, par 72. The club site
(`01.txt`) and OpenGolfAPI (`02.txt`) confirm 7,081, par 72, and OpenGolfAPI has the same tee ratings.

- Black: 467 544 351 226 413 390 600 195 466 / 457 566 230 331 176 548 381 215 525
- Par: 4 5 4 3 4 4 5 3 4 / 4 5 3 4 3 5 4 3 5; SI 4 6 14 12 10 16 2 18 8 / 9 5 15 7 17 1 11 13 3

The OSM hole order does **not** follow this card hole for hole. OSM 3 is a 228-yd par 3 (card 3 is a 351-yd par 4),
OSM 4 is 316 / par 4 (card 4 is a 226-yd par 3), and OSM 14 is about 399 (the card has no par 3 near 400). Holes 1, 2,
10 and 11 agree. The review already noted that the OSM `dist` tags are shuffled, so the OSM refs may be too. The card
cannot simply be attached by number. Someone has to match card holes to OSM ways (by length, par and SI) and renumber
them with `hole_renumber`.

## Holes

| hole | osm_back | note |
|---|---|---|
| 1-13, 15-18 | OK geometry, no card | routing and greens as reviewed; yardages measured, unverified |
| 14 | **wrong par** | par 3 box view on a 399-yd hole |

## Next fix

1. **Pipeline** (`course_data/platform/package.py` `apply_card_overrides`): apply `par_overrides` (and per-hole
   yardages) even when there is no card, for example by patching the OSM hole par/ref before geometry. Otherwise no
   card-less course can take a par fix.
2. **Course:** turn the golfify card above into `course_data/library/sycamore_ridge/card_review.json`, match it to
   the 18 OSM hole ways (length, par, SI), and add the renumbering to `review.json`. Then rebuild with
   `tees ["Black", "Blue"]`.
3. Rebuild and recheck. 14 must come out as a par 4 (or as whatever card hole that way turns out to be).
