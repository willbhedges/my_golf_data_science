# Tees and scorecard

What this folder is for: when the golfer says "Spirit Hollow, Black", the app needs each hole's
par and yardage, and where that tee box actually sits on the ground.

| File | What it is |
|---|---|
| `scorecard.json` | Spirit Hollow card: par, men's and women's handicap, the four tee sets (Gold, Black, White, Rust) with per-hole yardage and rating/slope, the Black/White combo, older cards still on aggregator sites, source URLs, confidence, and the app cross-check |
| `place_tee.py` | Tee placement: puts the tee for a yardage on a hole's OSM line and tee polygons (`place_tee`, `place_tee_sets`, `assign_tees_to_holes`); **joint ordered assignment of every set on a hole** (`assign_tee_sets`, `place_course_sets`), the green-centroid measuring point (`green_for_line`) |
| `lidar_pads.py` | Tee-pad candidates from the 3DEP 1 m DEM (flat, levelled, banked, slightly raised), used where a set has no OSM box; `python3 course_data/tees/lidar_pads.py` validates against the OSM boxes → `lidar_pads_validation.json` |
| `localize.py` | **Tee-set localizer v2** (optional S2 in `platform/package.py`: request `"tee_localizer": "v2"` or env `TEE_LOCALIZER=v2`, falls back to `place_course_sets`): OSM boxes + lidar pads + DEM/NAIP texture pads + segment-model / perception tee detections merged into one pad list, joint chain assignment of every set, per-set `sigma_yd` / `p_assign` / alternatives |
| `eval_localize.py` | Before/after of v2: Spirit Hollow hand-map truth, Mozingo lengths, and OSM-tees-hidden on the package courses + generalize train (test split report-only) → `eval_localize.md` / `.json` (`cache/` holds the lidar / texture pads) |
| `picks_localize.py` | Product picks (quick decision) on the committed packages re-teed per variant → `picks_localize.md` / `.json` |
| `screenshot_sets.py` | Which card set each 18Birdies screenshot of the hand map shows → `spirit_hollow/screenshot_tee_sets.json` (the acceptance truth for tees) |
| `eval_tees.py` | Before/after of the tee stage on all three courses, offline in seconds → `eval_tees.md` / `.json` |
| `place_course.py` | Runs the placement for every hole and tee set → `tee_positions.json`, and prints the check table |
| `tee_positions.json` | Lat/lon per hole and tee set, with the method used, the OSM tee way, and a confidence |
| `test_place_tee.py` | Synthetic-geometry unit tests (`python -m pytest -q course_data/tees`) |
| `fetch_scorecards.py`, `.github/workflows/tees_fetch.yml` | Fetch the scorecard pages from GitHub Actions (the dev sandbox has no web access) into `raw/` as text |

## Spirit Hollow card (Burlington, Iowa)

The course is confirmed as Spirit Hollow Golf Course, 5592 Clubhouse Dr, Burlington, IA 52601 (OSM
relation 13353211). It opened in 2000 and was designed by Rick Jacobson. Par is 72.

The **authoritative source is the club's own Hole-by-Hole page**
(<https://www.spirithollowgolfcourse.com/golf/hole-by-hole>). It gives each hole's par and four
yardages, back to front. It doesn't print colours or handicaps. Golfify's card
(<https://www.golfify.io/courses/spirit-hollow-golf-course>) matches it hole for hole and names the sets
Gold / Black / White / Rust. Golfify also gives the stroke index. Stymie's men's index matches it.

| Hole | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | Out | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | In | Tot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Par | 4 | 5 | 3 | 5 | 4 | 4 | 3 | 4 | 4 | 36 | 5 | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 5 | 36 | 72 |
| Gold | 426 | 607 | 183 | 607 | 468 | 445 | 165 | 431 | 410 | 3742 | 575 | 352 | 210 | 480 | 467 | 215 | 434 | 496 | 579 | 3808 | 7550 |
| Black | 391 | 507 | 148 | 532 | 384 | 408 | 154 | 383 | 365 | 3272 | 502 | 338 | 186 | 409 | 393 | 145 | 378 | 445 | 521 | 3317 | 6589 |
| White | 376 | 452 | 134 | 501 | 361 | 365 | 136 | 365 | 323 | 3013 | 457 | 305 | 163 | 389 | 370 | 132 | 331 | 397 | 483 | 3027 | 6040 |
| Rust | 299 | 390 | 100 | 439 | 273 | 303 | 108 | 332 | 266 | 2510 | 394 | 252 | 120 | 298 | 328 | 105 | 282 | 341 | 423 | 2543 | 5053 |
| Hcp (M) | 3 | 11 | 9 | 13 | 15 | 1 | 17 | 5 | 7 | | 8 | 12 | 14 | 2 | 4 | 18 | 16 | 10 | 6 | | |
| Hcp (W) | 6 | 14 | 16 | 10 | 12 | 2 | 18 | 4 | 8 | | 9 | 15 | 13 | 1 | 5 | 17 | 11 | 3 | 7 | | |

Rating and slope, from GolfNow/GolfPass/Golfify for the 7550 card:

| Tee | Men | Women |
|---|---|---|
| Gold | 74.8 / 134 | |
| Black | 71.4 / 124 | |
| White | 69.0 / 117 | 71.5 / 120 |
| Rust | | 70.3 / 116 |

Stymie shows newer-looking ratings, for example Gold 75.9 / 135 and Black 72.4 / 131, but against an
older per-hole card. The USGA NCRDB is the real authority, but it returns 403 to scripted requests, so
**ratings are medium confidence; yardages and par are high.**

### Older cards still on aggregator sites (don't use)

- GolfLink and ForeTee have a 7021-yard Gold card: 527 on 2, 566 on 4, 383 on 9, 165 on 15, and so on.
  They also have a 6580-yard Black card: 141 on 3, 136 on 7, 390 on 8, 418 on 13.
- Stymie has a 7301-yard Gold card, and OpenGolfAPI has a 7268-yard one.

The OSM hole lines were traced to back tees that match these older cards (line lengths: hole 2 is
528, hole 15 is 158). That's why the current 607 on 2 and 215 on 15 have no mapped box. All of these
cards are in `scorecard.json → historical_cards`.

### Sources, licences and reliability

| Source | What it gives | Reliability | Licence / access |
|---|---|---|---|
| Club website, Hole-by-Hole page | Par, 4 yardages per hole | Authoritative, current | Club copyright; we use the facts only |
| Golfify | Colours, stroke index, ratings, full card | High (matches the club) | Proprietary |
| GolfNow / GolfPass / TeeOff | Tee totals, rating/slope | Medium-high | Proprietary; GolfPass returns 403 to scripts |
| Stymie | 7 sets (M/W ratings, B/W combo) | Medium (stale holes) | Proprietary |
| GolfLink, OpenGolfAPI, ForeTee, 1golf | Older cards | Low (stale) | Proprietary; some return 403 |
| USGA NCRDB (ncrdb.usga.org) | Official rating/slope per tee, sometimes yardage | Authoritative | Not retrieved: 403 from Actions; USGA terms forbid bulk use |
| BlueGolf, mScorecard, Offcourse, SwingU, 18Birdies, GolfLogix | Per-hole cards | Unknown | Blocked to scripts (403/405/500) |
| GolfAPI.io | Per-hole tees, GPS | Usually good | Paid API key; not tried |
| OpenStreetMap | `golf=hole` lines (ref, par) and 103 `golf=tee` polygons | Good geometry, but no tee colour or ref tags | ODbL 1.0: attribution and share-alike |

## Which tee is the golfer playing? (app cross-check)

`spirit_hollow/course.py` sets each hole's length to `270 + APP[h][1]`. That's the GPS app's
yards-to-green from the 270 dot, measured from the tee the app was showing.

| Hole | 1 | 2B | 2F | 4 | 5 | 6 | 7 | 8 | 9B | 9F | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| App | 413 | 609 | 520 | 520 | 397 | 421 | 159 | 375 | 399 | 373 | 521 | 348 | 177 | 407 | 418 | 134 | 388 | 453 | 516 |
| Black | 391 | 507 | 507 | 532 | 384 | 408 | 154 | 383 | 365 | 365 | 502 | 338 | 186 | 409 | 393 | 145 | 378 | 445 | 521 |
| App − Black | +22 | +102 | **+13** | −12 | +13 | +13 | +5 | −8 | +34 | **+8** | +19 | +10 | −9 | −2 | +25 | −11 | +10 | +8 | −5 |
| App − Gold | −13 | **+2** | −87 | −87 | −71 | −24 | −6 | −56 | **−11** | −37 | −54 | −4 | −33 | −73 | −49 | −81 | −46 | −43 | −63 |

Across the 15 single-tee holes plus 2F and 9F, here's how the app's lengths compare with each tee set:

| Tee | Mean (app − card) | Mean absolute error |
|---|---|---|
| Black | +6 yd | 11 yd |
| White | +37 yd | 37 yd |
| Gold | −49 yd | 49 yd |

**So the golfer plays the Black tees.** On holes 2 and 9:

- **2B (back) = Gold** (609 vs 607), and **2F (forward) = Black** (520 vs 507).
- **9B (back) = Gold** (399 vs 410), and **9F (forward) = Black** (373 vs 365).

The app's number isn't a scorecard measurement. It runs from the app's tee point through the 270 dot
to the green centre, so it overstates doglegs. Its tee point is also whatever the app chose. A ±15-yard
scatter is expected, and the big outliers (1: +22, 10: +19, 14: +25) look like doglegs or tee boxes
behind the Black marker.

## Which set each screenshot shows (Q1, `screenshot_sets.py`)

18Birdies sets its tee icon by hand, by default on the farthest-back set, so a traced hole is not
automatically the Black tee. `course_data/spirit_hollow/screenshot_tee_sets.json` labels every traced
key with the card set nearest the screenshot's measured length, cross-checked by where the screenshot
tee sits on NAIP (`hand_zones_ll.json` `tee_ll`) against each set's placed tee:

| Set | Traced keys |
|---|---|
| Gold | 1 (413 vs Gold 426 / Black 391; 8 yds from the Gold box, 40 from Black), 2B, 9B, 11 (348 vs 352 / 338, one shared box) |
| White | 15 (par 3, length only: 134 vs White 132 / Black 145) |
| Black | 2F, 3, 4, 5, 6, 7, 8, 9F, 10, 12, 13, 14, 16, 17, 18 |

No label conflicts with the position evidence. The screenshot tee lies within 9 yds of an OSM box
centroid on all 16 traced tee shots, so the app shows box centres. On 7 of the 12 Black screenshots
that box is 9-30 yds *behind* the box that contains the card yardage (5, 6, 10, 14, 16, 17, 2F). Either
the app chose a box behind the Black markers, or the card is measured on a different line. A
card-driven placement cannot reproduce it, which caps "tee within 10 yds" at about half the holes.
`acceptance.py --holes <package>` and `qa/golden_spirit_hollow.py` now score each traced hole with the
tee of its screenshot's set (`--tee-set package` gives the old numbers).

## Joint assignment (Q2, `assign_tee_sets` / `place_course_sets`)

What the package (`platform/package.py`) and `place_course.py` now run:

1. **One solve per hole for all sets.** Sets are taken back to front by card yards. Each set picks a
   candidate box (sharing allowed) or a walk-back. The placed points must keep that order along the
   line of play (2-yd slack). A dynamic programme minimises:
   - the yards outside each box's extent,
   - plus 0.05 x |centroid − card|,
   - plus a source cost (borrowed box +4, lidar pad +6),
   - plus 0.1/yd for a box more than 45 yds off the first leg,
   - plus 0.25 x the gap mismatch between consecutive sets (capped at 10),
   - with walk-back at 30.
2. **Distances go to the OSM green-polygon centroid** (`green_for_line`, geometry's `find_green` rule)
   along the OSM hole line, through its turning points. Before this change they went to the line's last
   vertex, which disagreed with the measured length geometry reports.
3. **A hole where some set has no box within 10 yds is re-solved with a wider window.**
   - Boxes up to 130 yds off the first leg count, from any hole or none.
   - The lidar pads near that hole's first leg are added as candidates.
   - This finds SH 2's 607 Gold, which sits in hole 18's tee complex 126 yds left of the old line,
     and the 2F/9B boxes that are set off the line.
4. An OSM box tagged with the set's colour still wins (`tagged`).

The card itself is picked in `platform/scorecard.py`: request > card file > club site > golfify >
OpenGolfAPI, the first that passes the consistency check (per-hole sum = stated total, longer sets
longer on every hole). It is never picked by fit to the map. The other cards are a per-hole cross-check
(`sources.scorecard.cross_check`).

Results (`eval_tees.md`, same OSM and cards, every tee measured the same way):

| | before (independent) | after (joint + lidar) |
|---|---|---|
| SH vs screenshots, screenshot's set: tee within 10 yds | 7/16 | 7/16 (median error 17.6 → 12.4 yds; 2B 126 → 29, 2F 100 → 14, 9B 49 → 6) |
| SH vs screenshots: measured length within 5 yds | 3/16 | 3/16 (capped by app length vs card: see Q1) |
| Measured length within 5 yds of the card, every hole x set: SH / Veenker / Mozingo | 85% / 78% / 78% | 93% / 83% / 94% |
| Walk-backs: SH / Veenker | 4 / 3 | 1 / 1 |

## Lidar tee pads (Q3, `lidar_pads.py`)

Each pad is detected on the 1 m bare-earth DEM, smoothed with sigma 1 m. A pad is a connected
component of 30-2,000 m² with these properties:

- slope under 5 %;
- top-hat `z − opening(z, disk 15 m)` above 0.05 m: raised against a plane, even a steep one;
- mean top-hat of at least 0.10 m;
- at least 30 % of its 1-4 m outer ring is bank steeper than 10 %.

Components within 25 yds of a green are dropped. Validation against the OSM boxes near hole starts,
with centroids matched within 10 yds (`lidar_pads_validation.json`):

| Course | Pads | OSM boxes | Precision | Recall |
|---|---|---|---|---|
| Spirit Hollow (tuned) | 69 | 95 | 0.72 | 0.53 |
| Mozingo Lake (held out) | 41 | 56 | 0.66 | 0.48 |
| Veenker (held out) | 36 | 38 | 0.28 | 0.26 |

Precision counts real unmapped tees as false, so it is a lower bound. Recall loses flush tees and
complexes that merge into one pad. Veenker is a 1938 course whose tees are mostly flush with the
ground. Pads are used only where no OSM box fits, at +6 yds cost and medium confidence at best.

## Placement algorithm (`place_tee.py`)

Scorecard yardage follows the USGA measuring convention. It's horizontal, from the permanent marker
(normally the middle of the tee box) along the line of play to the centre of the green, through the
turning point on a dogleg. So for a point P on the tee:

```
dist(P) = |P − V_k| + (line length from V_k to the green),
V_k = the first line vertex in front of P (next turning point)
```

1. Project to a local flat frame in yards (equirectangular about the hole; error under 0.1 % over a
   hole).
2. `assign_tees_to_holes` gives each OSM tee box to one hole: the hole whose first leg it sits closest
   to, measured perpendicular. The box must be no more than 150 yd behind the line start and no further
   forward than half-way down the hole.
3. For each box near the first leg (offset 45 yd or less), compute `dist` at the centroid (the middle
   of the tee) and at its front-most and back-most points.
   - The error is 0 if the card yardage falls inside the box's front-to-back extent, otherwise the gap
     to the nearer end.
   - The best box has the smallest error, with ties broken by how close the centroid is to the
     yardage.
4. Return the centroid if it's within 3 yd of the card. Otherwise return the point on the box's axis
   (through the centroid, parallel to the first leg) at exactly the card yardage, clamped to the box.
   Confidence is high if the error is 5 yd or less, medium if 15 or less, else low.
5. If no box is within 25 yd, walk back from the green along the line by the yardage. Past the line
   start, the first leg is extended backwards. This gets method `walkback` and low confidence.
6. `place_course.py` adds one more step: if a hole's own boxes don't fit a tee set, it may borrow a
   neighbouring hole's box, but only on a match within 10 yd. Shared tee complexes are common.
   `place_tee_sets` reports when two tee sets share a box.

Tests (`test_place_tee.py`, 14 cases) use synthetic geometry. They cover:

- picking among three boxes, and placing on the box axis inside a long box
- clamping and the error it reports
- ignoring off-line boxes, and walking back along a straight hole and a dogleg
- measuring a dogleg through its turning point
- point tees and a green override
- giving the same answer when the hole is rotated
- tee sets sharing a box, and assigning boxes to holes exclusively

## Accuracy on Spirit Hollow (OSM tee boxes vs the card)

This section describes the per-set placement *before* the joint assignment. With the joint assignment,
Gold 2 lands on hole 18's complex box at 611 yds, Gold 7 on a lidar pad, Rust 6 and 18 on boxes, and
Gold 15 (215) is the only walk-back left. The current table is printed by `place_course.py`.

From `python course_data/tees/place_course.py`: 72 hole × tee placements.

- **Black (the golfer's tee): all 18 holes land on an OSM tee box.** 17 are within 2 yd of the box's
  extent. Hole 2 is 9 yd off (box at 488–498 yd vs 507), and the box picked is 38 yd right of the
  line; box 72943 at 519–536 is the other candidate.
- **Gold:**
  - No mapped box on 2 (607; the furthest-back box is 536) or 15 (215; the furthest back is 166). These
    are walk-backs, and are 71 and 49 yd behind the furthest-back mapped box.
  - Hole 18 is 22 yd past the furthest-back box.
  - Hole 16 borrows box 91717 from hole 14's complex.
- **White:** all on boxes. Hole 6 is 19 yd off.
- **Rust:** walk-backs on 6 (303) and 18 (423), where OSM has no forward box. Holes 3 and 4 are 12 and
  15 yd short of the forward-most box.

## Gaps

Some of these are closed by Q2/Q3 above: Gold 2, Rust 6 and Rust 18 now have boxes, and pads cover
holes where OSM has none. Still open: Gold 15, colour tags, and the NCRDB.

- No OSM tee polygon has a colour or `ref` tag. Tee identity comes only from distance, so on
  closely-spaced boxes (holes 1, 6 and 9) two sets may land on the same box or on a neighbour's box.
- No mapped box for Gold 2 (607), Gold 15 (215), Rust 6 or Rust 18. These come from walk-backs, which
  are only as good as the OSM line's first leg extended backwards. Adding these boxes to OSM from the
  NAIP imagery would fix it.
- Rating/slope aren't confirmed against the USGA NCRDB (403). GolfAPI.io (paid) hasn't been tried.
- I haven't checked the app's tee pixel positions against the placed lat/lon. That needs the
  screenshot-to-OSM georeferencing in `course_data/compare_traced.py`, which would confirm 2B = Gold
  and 9B = Gold on the ground.
