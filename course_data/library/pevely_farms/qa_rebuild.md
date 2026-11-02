# Pevely Farms: rebuild QA (2026-11-02)

**Verdict: PUBLISH.** The must-fix is done: holes 1, 9, 10 and 18 are now Pevely's own holes, not Crescent Farms'. The
pipeline's new neighbour-course filter dropped Crescent Farms' ways (`ignored 5 golf=hole way(s) of a neighbouring
course: OSM 881746238, 884242539, 884242547, 884242548, 884242556`). Hole 16's pick is still on the +40 aim bound, as
the reviewer reported. It is a model issue, not a geometry one.

Page checked: `course_data/library/pevely_farms/page.html`, built 2026-11-01T21:04Z. Both solved sets (Black 7,032,
Blue 6,704, par 72) were run through `qa_page.js`: 18 holes each, phone and desktop, 0 page problems. I looked at every
phone hole picture. The page yardage equals the golfify card on all 36 hole-sets, and the measured length is within 8
of it on every hole-set.

## Review fixes

| fix in review.md | applied? |
|---|---|
| Re-route 1, 9, 10, 18 to the Pevely ways inside the boundary (1 = OSM way 848080943) | **yes.** OSM handicaps now match the Pevely card: 1 hcp 16, 9 hcp 4, 10 hcp 13, 18 hcp 3. Every one has an OSM green, a full photo and a fairway landing: 1 Black 446 Driver (fairway 43%), 9 527 Driver, 10 403 Driver/4-wood tie, 18 468 Driver (fairway 63%). |
| 16: pick unreliable (+40 at the bound into the corner rough) | **unchanged.** Black 2-wood / Blue 2-wood (calm) aim **40.0 right**, fairway 2-3%, landing in the rough right of the fairway at the dogleg. 4-wood is 0.006-0.016 behind. No geometry fix exists; see the next fix. |

## Holes

| hole | Black | Blue | note |
|---|---|---|---|
| **1, 9, 10, 18** | **fixed** | **fixed** | re-routed, see above. 18 Black is a walk-back at 468 |
| 2, 4-8, 12-15, 17 | OK | OK | OSM boxes, card yardage |
| 3 | OK | OK | 277/250-yd par 4, 4-wood |
| 11 | OK | OK | Black walk-back (unmapped tips), Driver/4-wood tie |
| 16 | pick on the bound | pick on the bound | see above |

## Next fix

None blocking. Solver: 16 is one of several picks clamped at the ±40 aim bound (also La Nickell 16, Gustin 16,
Colbert 13). The hole's fairway is not mapped in OSM, so the landing quality comes from vision only.
