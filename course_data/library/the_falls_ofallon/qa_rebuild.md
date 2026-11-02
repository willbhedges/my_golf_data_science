# The Falls Golf Club (O'Fallon MO): rebuild QA, second pass (2026-11-02)

**Verdict: PUBLISH.** The per-set yardages are now on the right sets. Blue reads 379 / 341 / 449 / 360 on 2 / 3 / 9 /
10 from the Blue boxes. White is unchanged and clean.

Page checked: `course_data/library/the_falls_ofallon/page.html`, built 2026-11-02T06:12Z (GitHub Actions run
41392580512). Both solved sets (Blue, White, par 71) were run through `qa_page.js`: 18 holes each, phone and desktop,
0 page problems. I looked at every phone hole picture. Card: `card_review.json` (golfify), no build warnings.

## First-pass fix

| fix | applied? |
|---|---|
| Gold fixes keyed per set (`"yards": {"Gold": ...}`), 18 Blue + Gold 482 | **yes.** Blue 2 / 3 / 9 / 10 measure 380 / 341 / 445 / 365 (card 379 / 341 / 449 / 360), on OSM boxes 7-31 yds in front of the Gold fix points. |

Blue total **5,994** = card 6,011 less the reviewed 18 (482 vs 499). The first pass expected 6,011 because it did not
allow for the deliberate 18 change, so 5,994 is right.

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1-10, 12, 14, 17 | OK | OK | OSM boxes, yardage = card ±5 |
| 11, 13, 15, 16 | OK | OK | Blue shares the Gold fix box; Blue card = Gold yardage there (365 / 345 / 510 / 330), so it is the same box |
| 18 | OK (review tee, 482) | OK | |
| 16 | OK (uncertain, as reviewed) | OK | Blue Driver left of the line, fairway 30%; not blocking |
| 9 | OK (marginal) | OK | Driver next to the right-hand trees (trees 13-14%), pond short-left out of reach |

## Remaining (optional)

None blocking.
