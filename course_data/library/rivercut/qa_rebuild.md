# Rivercut Golf Course (Springfield MO): rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The one queued fix (16 Black) is applied, and every hole on both sets matches the card.

Page checked: `course_data/library/rivercut/page.html`, built 2026-11-01T21:06Z. Both solved sets (Black 7,066 with
16 at 316, Blue 6,536, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I
looked at every phone hole picture. The page yardage equals the card on all 36 hole-sets, and the measured length is
within 1-5 yds of it.

## Review fixes

| fix in review.md | applied? |
|---|---|
| 16 Black: 316 (AllSquare / OpenGolfAPI), tee on the hole line about 23 yds behind the Blue box, not the lidar pad in the hollow at 337 | **yes.** Tee snapped 6 yds to OSM tee 758217945; the page shows 316 (311 measured). Driver to just short of the green among the greenside bunkers on a drivable par 4. The Black total is now 7,066. |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| 1-3, 5-14, 17, 18 | OK | OK | OSM boxes, card yardage; par-3 boxes on the green |
| 4 | OK | OK (accepted CHECK) | Blue Driver/4-wood tie to the apron on the 323-yd dogleg, as reviewed |
| 15 | OK (accepted CHECK) | OK | Black on the shared long box at card length |
| 16 | **fixed** | OK | Blue 2-wood (calm Driver) at 295 |

## Next fix

None. Publish.
