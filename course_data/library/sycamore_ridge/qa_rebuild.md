# Sycamore Ridge Golf Club (Spring Hill KS): rebuild QA, second pass (2026-11-02)

**Verdict: NEEDS FIX** (hole 1 tee, and hole 9 more mildly). The card, the renumbering and the par fix all worked. But on
card hole 1 the Black and Blue tees sit on OSM colour-tagged boxes 42 and 50 yds short of the card, and the page shows
the card yardage from there.

Page checked: `course_data/library/sycamore_ridge/page.html`, built 2026-11-02T06:05Z (GitHub Actions run 41392580512).
Both solved sets (Black, Blue) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I
looked at every phone hole picture.

## First-pass fixes

| fix | applied? |
|---|---|
| Card: golfify typed into `card_review.json` (Black 7,081 / Blue 6,465, par 72) | **yes.** Sets Black + Blue, totals 7,081 / 6,465. |
| Renumber the nines to the card (OSM 1-9 = card 10-18, OSM 10-18 = card 1-9) | **yes.** Pars 4 5 4 3 4 4 5 3 4 / 4 5 3 4 3 5 4 3 5 = 72, equal to the card on every hole. |
| Old hole 14 (OSM-tagged par 3 at 399) as a par 4 | **yes.** It is now card hole 5, a 413-yd par 4 (`par_overrides {"5": 4}`), with a Driver pick. Page hole 14 is card 14, the 176-yd par 3. |

## Tee vs card

The page yardage equals the card on all 36 hole-sets. The measured length is within 6 yds of the card on every hole
except these:

| card hole (OSM ref) | set | card / page | measured | tee | OSM boxes on the hole (yds) |
|---|---|---|---|---|---|
| **1** (OSM 10) | Black | 467 | **425** | OSM box 1042462315, colour-tagged black | 308 332 341 357 364 392 **447 463** |
| **1** (OSM 10) | Blue | 445 | **395** | OSM box 930492856, tagged blue | same |
| 9 (OSM 18) | Black | 466 | 452 | OSM box 930502257, tagged | 292 324 352 376 382 **416 462** |
| 9 (OSM 18) | Blue | 416 | 408 | OSM box 930502258, tagged | same |

On hole 1 the White, Green and Yellow tags fit the card to 1 yd (354 / 328 / 307), but the black and blue tags sit two
boxes forward. The 463 and 447 boxes match Black and Blue to 2-4 yds. The OSM hole line starts at the 463 box (465 yds
to the green centre). The page shows "467" and plays the hole from 425 (the note reads "about 111 yds in" for Blue
4-wood on a 445 hole). The tagged tee wins because the localizer takes a colour-tagged OSM box before it checks the
card yardage.

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| **1** | **wrong tee** (42 short) | **wrong tee** (50 short) | see above |
| 2-8, 10-18 | OK | OK | routing and greens as reviewed; yardage = card ±6 |
| 9 | minor (14 short) | minor (8 short) | tagged boxes; untagged 462 / 416 boxes fit the card |
| 13 | OK | OK (marginal) | 310-331 yd par 4 over the pond; Blue Driver aim 21 right into the greenside bunkers (sand 20%). Model choice |
| 18 | OK (marginal) | OK (marginal) | aim 40 right on the bound around the dogleg; fairway 51-70%. Model choice |

## Next fix

1. **Course** (`course_data/library/sycamore_ridge/review.json`; per-hole fixes there use the OSM numbers, which the
   renumber re-keys): OSM hole 10 `fix`: `"tee_ll": {"Black": [38.7582778, -94.8430081]}, "yards": {"Black": 467,
   "Blue": 445}`. Blue also needs a `tee_ll` on the 447 box (not in the repo's data: read it from the OSM tee ways at
   the top of the hole line, about 16 yds in front of the Black point). Optional, OSM hole 18: Black on the 462 box,
   Blue on the 416 box. Then rebuild.
2. **Pipeline** (tee localizer): a colour-tagged OSM box that is more than about 15 yds off the card should lose to an
   untagged box within 5 yds of the card. Hodge Park shows the same tag-first behaviour.

After that rebuild: PUBLISH, provided hole 1 measures about 465 / 447 from the back boxes.
