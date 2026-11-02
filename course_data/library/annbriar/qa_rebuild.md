# Annbriar Golf Course (Waterloo IL): rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The build now completes, and the hole 9 Black tee fix is in. All 36 hole-sets are on OSM boxes
within 5 yds of the card, with no CHECKs (status auto-OK).

Page checked: `course_data/library/annbriar/page.html`, GitHub Actions run 41479479995 (committed 19:29Z). Both solved
sets (Hickory 6,841, Black 6,517, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture.

## Review fixes

| fix (review.md rv03) | applied? |
|---|---|
| 9 Black off the lidar pad in the trees, onto the box 14 yds in front of Hickory (475, supplement) | **yes.** On an OSM box, 475 / 475. Driver +32.5 (was 2-wood +40 along the trees), fairway 33% |
| 13 Hickory (uncertain, kept) | unchanged: 379 / 383, 1 yd from a box |

## Checks

| check | result |
|---|---|
| Card | golfify; page = card on all 36 hole-sets; measured within 5 yds |
| Mapper / native cards | not used; `native.json` empty, as expected |
| Water filter | ran (full filter); no vision water. Water in the stats is the ponds on 5, 6, 11 (at most 11% on 11, calm) |
| Aims past ±40 | none (largest: Hickory 14 -36.5, Hickory / Black 9 +32.5, 11 -31.5) |

## Holes

| hole | Hickory | Black | note |
|---|---|---|---|
| 1-8, 10, 12, 13, 15-17 | OK | OK | |
| 9 | OK (marginal) | **fixed** | +32.5 to the dog-leg corner, fairway 24-33%. Model choice, as reviewed |
| 11 | OK | OK | 4-wood -31.5 around the dog-leg, water 2-11% from the pond left |
| 14 | OK (marginal) | OK | Driver / 2-wood -32 to -36 toward the left trees, trees 5-15%. Model choice, as reviewed |
| 18 | OK | OK (marginal) | Black calm Driver in rough (fairway 29%). Model choice |

## Next fix

None.
