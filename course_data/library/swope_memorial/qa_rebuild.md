# Swope Memorial Golf Course: rebuild QA, mapper wave 2c (2026-11-03)

**Verdict: NEEDS FIX (one tee).** The hole 1 **Green** tee sits on hole 6's tee box. Hole 1's line starts on the
Bronze box, about 87 yds north. Everything else is clean: Bronze is right on all 18 holes, and Green is right on
17. The fix is in `review.json` (hole 1 `fix.tee_ll` Green + `yards` Green 390). Rebuild with it, then publish.

Page checked: `course_data/library/swope_memorial/page.html`, GitHub Actions run 41554623184 (package built
2026-11-03T01:41Z). Mapper layers: `course_data/mapper/swope_memorial/` (19 zone edits on 6 holes, 0 tees moved, 72
checked). Both solved sets (Green 6,324, Bronze 6,079, par 71, the 2026 club card) were run through `qa_page.js`: 18
holes each, phone and desktop, 0 page problems, no console errors. I looked at every phone hole picture. I also
re-rendered the mapper tee panels for holes 1, 5, 6 and 9 (NAIP 2020/2022 plus the DEM).

## Holes 1 and 6: same Green tee point

| | hole 1 Green | hole 6 Green |
|---|---|---|
| tee point | -94.51655, 39.00066 (OSM tee 692649939, `tee_axis`) | -94.51651, 39.00065 (OSM tee 692649939, `tee_centroid`) |
| measured / card | 391 / 390 | 406 / 406 |
| distance to the hole's own line start | **88 yds** | 1 yd |

**Finding: a tee-assignment error, not a routing or numbering error.** Routing and numbering are right. Hole 1's OSM
line starts on the Bronze box (284464464). Hole 6's line starts on box 692649939. The two greens, the pars and the
Bronze/Silver boxes are each on their own hole. The localizer put 1 Green on hole 6's box with p = 0.50, against
0.35 for hole 1's own box. Its distance to the green happens to be 389, which matches the card, so no yardage CHECK
fired. Why I do not think it is a real shared back tee:
- On the other 17 holes the Green tee is 8-25 yds from the Bronze tee, and the card gap is 13-14 yds on every hole.
  On hole 1 the two tees are 87 yds apart, almost side by side, not one behind the other.
- The box is hole 6's own teeing ground. Holes 1 and 6 leave it heading east and southeast. A back tee for 1 there
  would play across the trees between the two holes. On the tee panel, hole 1's complex (Bronze and Silver boxes,
  OSM) is a separate strip by the clubhouse, north of the 9 green.

**Fix applied** (`review.json`, hole 1): Green `tee_ll` [39.001355, -94.516316], which is 14 yds behind the Bronze box
on hole 1's line, 388 straight to the green (card 390). Plus `yards` {Green: 390}. `review_fixes.library_request`
gives `tee_overrides {1: {Green}}` and `yardage_overrides {1: {Green: 390}}`.

Hole 6 Green is right as it stands: it is on its own line start, 406 = card.

Not verified: the imagery is NAIP 2020/2022, before the 2025-26 restoration. A new 2026 back tee for 1 cannot be ruled
out from the photos. The 13-14 yd card gap makes it unlikely.

## Mapper layers

| hole | mapper edit | on the page? |
|---|---|---|
| 2, 6, 8, 9, 11, 17 | crown groups added as recovery (77-278 sq yds each) | yes. The landing ovals show the extra trees (2: 12%, 8: 5%, 11: 12%). No crown is drawn on open fairway |
| 1, 3, 5, 10, 12, 14, 15, 18 | checked, no change; no long grass on either side | as before |

## Holes

| hole | Green | Bronze | note |
|---|---|---|---|
| 1 | **wrong tee** | OK | Green plays from hole 6's box (above). Driver -8.5, fairway 54%. The pick is plausible, but from the wrong spot |
| 2 | OK (CHECK) | OK | Driver +8 to 42 yds short of the 321-yd green, fairway 14%. The aim CHECK (rough, 11 yds off the fairway) is printed |
| 3, 4, 7, 10-13, 16, 17 | OK | OK | yardage = card ±6; par-3 boxes on the green. 12 Green is on a lidar pad (CHECK printed), 527 / 533 |
| 5 | OK (marginal) | OK | Driver on the line, trees 21-23% (pre-restoration tree line). Tee CHECK (11 yds from an OSM box) is printed |
| 6 | OK (tie) | OK (tie) | Driver ≈ long iron (tie badge), aim 8.5-12 right |
| 8 | OK | OK | 273 / 259 par 4: 2-wood / 4-wood toward the greenside bunkers (sand 25-27%) |
| 9 | OK (tie) | OK (tie) | Driver/4-wood tie, aim 19.5 / 23.5 right (inside ±40) |
| 14, 15, 18 | OK (marginal) | OK (marginal) | Aims 12-24 off the line; trees 11-18%. Model choice |

No aim is wider than ±40, so no wide-aim CHECK is needed. Page yardage = the 2026 card on all 36 hole-sets.

## Other

- 16 Black (not solved) sits on hole 14's box, 87 vs 78. It is not on the page; worth a look if Black is ever built.
- The imagery caveat from the 2026-11-02 pass still stands: the photos predate the restoration.

## Next fix

Rebuild with the updated `review.json` (hole 1 Green tee). After the rebuild, check that hole 1 Green measures about
390 from behind the Bronze box, and that hole 6 is unchanged.
