# Painted Hills Golf Club (Kansas City KS): rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The build now completes, and the hole 17 fix is in: it is a 144 / 142 par 3, and the course par
is 70. The 17 CHECKs are tee-position CHECKs, because OSM maps no tee boxes here. The pads match the card.

Page checked: `course_data/library/painted_hills/page.html`, GitHub Actions run 41479479995 (committed 19:13Z). Both
solved sets (Blue 5,831, White 5,398, par 70) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page
problems. I looked at every phone hole picture.

## Review fixes

| fix (review.md rv08) | applied? |
|---|---|
| 17: supplement hole way (par 3) and back tee pad | **yes.** Par 3, Blue 144 card / 139 measured on the OSM box, White 142 / 139; box on the green. Course par 70 (was 84) |

## Checks

| check | result |
|---|---|
| Card | golfify; page yardage = card on all 36 hole-sets; measured within 5 yds |
| Tees | 17 of 18 holes on lidar / texture pads or walkbacks (OSM has no tee boxes; "CHECK: tee" on the page). All within 5 yds of the card. Blue 7 is now 322 / 327 (was 316) |
| Mapper / native cards | not used; `native.json` empty, as expected |
| Water filter | ran (full filter); no vision water |
| Aims past ±40 | **White 7 2-wood -48.5** (tie with 4-wood). Blue 7 and White 12 sit on -40 |

## Holes

| hole | Blue | White | note |
|---|---|---|---|
| 1-6, 8-11, 13-16, 18 | OK (CHECK, tee) | OK (CHECK, tee) | routing follows the OSM hole ways; pictures right |
| 7 | OK (CHECK) | **wide aim** (CHECK) | 327 / 303 dog-leg left (green 89 yds left). White 2-wood -48.5 cuts the corner (fairway, 4% trees, 8% unverified). The page has a CHECK on the hole (tee), but no wide-aim CHECK |
| 12 | OK (CHECK) | OK (marginal) | White Driver -40 on the bound around the dog-leg |
| 17 | **fixed** | **fixed** | see above |

## Next fix

None blocking; 7 is already a CHECK hole. The pipeline wide-aim CHECK (see gustin/qa_rebuild.md) would add the reason
"aim past 40" to White 7.
