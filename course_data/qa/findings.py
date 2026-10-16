"""Hand-written QA findings (visual review + bug reports), included verbatim at the end of REPORT.md by
golden_spirit_hollow.write_report(). Edit TEXT, then re-run golden_spirit_hollow.py (or run_qa.py)."""

SUMMARY = r'''
## 0. Summary

* **Contracts** (`test_contracts.py`, 7 packages, ~1,900 checks): the platform packages for all three courses load,
  have every hole, par, tees for every card set, bearing, zones + zones_ll, provenance, and `tee_strategy` runs on
  every hole. Failing: course boundary drops 2 of 3 rings (SH 5-9 "outside"), self-intersecting polygons on every
  course, forward-tee lengths, tee points inside vision `native`, zones/zones_ll drift after gap-fill.
* **Golden (Spirit Hollow)**: every bar fails. Best build (platform + vision): green within 10 yds 75%, same club as
  final_decision.json 50% (bar 80%), trees IoU 0.15 / long grass 0.09 (bar 0.6).
* **End to end**: plan.py produces a book, aim sheets and a wind page for Spirit Hollow, Mozingo Lake and Veenker.
  Mozingo picks match the hand-made Mozingo plan on 8/9 holes. Veenker (no vision) prints "Driver, 120 yds right"
  across a river on 15.
* **Usable for a new course today? No, not without a human check.** The pipeline runs, but the printed aims are
  relative to an arbitrary tee line, there is no guard on absurd picks, and courses without built vision layers play
  every wood as rough. With vision layers and a human look at the review images (`review/<slug>/`), the open
  Mozingo-type course is close.
'''

TEXT = r'''
## 3. Visual review findings (hand-checked, `review/<slug>/<hole>.jpg`)

Images: left = whole hole (tee line up), right = landing zone 145-365 yds, +/-95 yds. Outlines: fairway green,
water cyan, sand white, OB magenta, trees orange, long grass yellow; dashed box = landing grid 220-340 +/-45;
star + dots = Driver best aim and 300 simulated balls coloured by the lie the package gives them.

### Spirit Hollow (v1 holes.json, Black tees; the product stand-in package has the same geometry)

| hole | what's wrong | where (yds along the tee line / lon, lat) |
|---|---|---|
| 11 | Driver best aim sits on the +60 search bound and lands in **thick woods right of the creek**, scored 89% rough. Real play is a lay-up short of the creek (crosses at ~275-290 yds). | 290-310 yds, 40-70 R; woods ~(-91.1430, 40.7650) |
| 9 | Fairway ends at ~280 yds into a **wood line**; Driver lands 98% "rough" in the trees. | 280-320 yds, 0-30 R |
| 18 | Aim on the +60 bound again: balls land across the creek in **unmapped tall native grass** by the cart path, scored as rough. | 270-310 yds, 45-75 R |
| 6 | **Native grass + tree clump left** of the fairway scored as rough; the OB polygon by the house on the right is a thin triangle, not the lot line. | 250-300 yds, 20-45 L; OB ~330 yds, 35-60 R |
| 1 | Trees left and the woods right of the cart path unmapped; the pond right is a half-disc of water clipped by an OB triangle. | 240-300 yds, 25-50 L |
| 13 | Woods left of the fairway unmapped; Driver goes into the fairway bunker at 290 (19% sand) with no tree cost weighed. | 150-330 yds, 30-90 L |
| 4, 5, 10, 12, 13 | Self-intersecting zone polygons (`test_zones_valid_simple`): OB on 4 and 5, creek water on 10/12/13 (buffers folding on themselves). `matplotlib.Path` tolerates them but even-odd fill leaves holes in the hazard. | see contracts.json messages |

### Spirit Hollow with vision (`qa/work/v_spirit_hollow` = `vision_any/gapfill.py` on `packages/spirit_hollow` (same as the 19:58 Actions package), precomputed lidar/NAIP layers; `review/spirit_hollow_vision/`)

Big improvement: woods right of the creek on 11 are now `recovery`, and Driver on 11 now finds the creek (78% water)
instead of "rough", so the model will lay up; trees appear in every landing zone (exposure 0.14-0.47).
Remaining errors:

| hole | what's wrong | where |
|---|---|---|
| all | Almost every `recovery` polygon has a `native` polygon hugging its outline 2-8 yds outside it (paired orange/yellow rings on 1, 9, 11): canopy shadow / crown edge classified as long grass. Inflates native (325 polygons added) and makes tree edges play as 50% lost ball. | e.g. hole 1 left woods ~(-91.1452, 40.7570) |
| 1 | Pond right of the 260-330 landing area is still a half-disc cut off by the OB line; tree clump left at 250-280 yds 20-45 L only partly covered (balls there score rough). | (-91.14515, 40.75696) is `rough` |
| 2 (Gold), 6 (Rust), 18 (Rust) | **Tee box inside a vision `native` polygon** (`test_every_tee_set`): gap-fill subtracts OSM tee polygons but not the package's tee points. | tees.<set>.tee_ll |
| 2, 9, 10 | `zones` (yard) no longer equal `zones_ll` after gap-fill: 2-4% of the 100-400 yd grid differs (e.g. recovery->ob on 2, recovery->water on 10): reframe re-sorts by ZONE_ORDER but the WGS84 list keeps append order, so overlap winners differ. | `test_zones_match_zones_ll` |
| 1, 9, 10, 11, 13, 15-18 | Self-intersecting vision polygons (recovery/native/water). | contracts.json |
| tree polygons | stair-stepped ~5-10 yd blocks (raster outline, little simplification) - fine for the model, ugly in the book. | - |

### Veenker Memorial (Ames IA, platform `packages/veenker`, Blue tees; requested White is not on the card)

| hole | what's wrong | where |
|---|---|---|
| 15 | Sharp dog-leg right across the river at ~230 yds; Driver goes straight through the corner into **trees/brush at 270-310 yds**, scored 98% rough. | 270-310 yds, 0-40 R |
| 5 | Mapped fairway ends at 245 yds; the line of play turns right. Driver lands in the **tree belt between two ponds**, 99% "rough"; fairway past the corner not mapped in OSM. | 260-320 yds, -40..+40 |
| 2 | Driver landing 96% rough: fairway not mapped in the landing zone (check OSM). | 220-340 yds |
| 3, 12, 14 | Best aim 42-50 yds off the tee line (dog-leg tee line again). | - |

### Mozingo Lake (Maryville MO, platform `packages/mozingo_lake`, `osm_back` tees)

NAIP 2022 here is visibly softer than Spirit Hollow's 2023 0.3 m. Fairways/bunkers line up with the photo on the
holes checked (12 sampled). No card, so `length` is the measured back-tee length (e.g. 12: "508"), and the book would
label it as the card yardage.

Common to every tee hole: **no `recovery` or `native` polygon anywhere** (no vision gap-fill merged), so every miss
into woods or prairie plays as rough - the R6 failure (unmapped hazard = rough), and why the auto club pick drifts
to Driver (see the golden table).

## 4. End-to-end runs (`e2e.py` -> `e2e.json`; plan.py --quick into a scratch dir)

| course | package | plan.py | deliverables | club picks |
|---|---|---|---|---|
| Spirit Hollow, Black | `product/standin/spirit_hollow` | OK, 1565 s | 19-page book 8.6 MB, aim sheets, 1.7 MB self-contained wind page (all 14 tee shots), decision for every par 4/5 | Driver on 9/14; golden on the **platform** package (with vision): same club as final_decision.json on 50% of 16 tee shots |
| Mozingo Lake (2nd) | `qa/work/v_mozingo_lake` (platform package + vision_any gapfill) | OK, 962 s | 19-page book, aim sheets, 0.9 MB wind page | **8 of 9** match the hand-mapped picks in `mozingo/README.md` (1 4w, 2 4w, 3 D, 4 D, 6 D, 7 4w, 9 D, 12 D; miss: 10 auto 4-wood vs D). Caveat: vision_any tuned its native threshold on Mozingo |
| Veenker (3rd) | `packages/veenker` (no vision layers) | OK, 364 s | book, aim sheets, 1.6 MB wind page | 15: "Driver, aim **120 yds right** of the tee line" across the river and trees next to another hole's green; 9: 2-wood +118 yds. Driver on 11 of 14. Not playable advice. |

Book review: every course's card prints aims relative to the auto tee line - Spirit Hollow "38 yds left" (1),
"50 left" (14), "98 right" (18); Mozingo 3 "58 yds right"; Veenker 15 "120 right", 9 "118 right". On the page the
yellow tee line runs into trees and the star sits on a fairway well off it. The Confidence column is empty in quick
mode.

## 5. Bug reports by area (state at 21:00 UTC; packages rebuilt on Actions 19:58)

### data platform (`course_data/platform/`)
* **P1 (geometry, high):** `course.boundary` keeps only the largest ring of the course MultiPolygon (Spirit Hollow
  relation 13353211 has 3 outer rings). Greens and tees of holes 5-9 fall 100-550 yds "outside the course"
  (`test_green_inside_course`, `test_tee_inside_course`), e.g. tee 6 (-91.15081, 40.76492) is 548 yds out. Anything
  that infers boundary OB from it puts 5 holes in OB. Fix: keep every ring (GeoJSON MultiPolygon).
* **P8 (high):** Veenker's package reports `stages.vision = "ok: vision_any/gapfill.py"` while gapfill found no
  layers (only 15 OSM `recovery` / 7 `native` polygons on a wooded course, `sources.vision` = null). Copy gapfill's own
  stage string.
* **P6 (Veenker):** duplicated tee sets `Gold (Gold)`, `Red (Red)` (golfify parse); Red tees on 3, 6, 8, 11 fail the
  15% length check. Requested `White` silently became `Blue` (warning only): ask the golfer.
* **P3 (Spirit Hollow):** Rust tees on par 3s 3, 12, 15 play 21-38% over the card (138 vs 100 on 3).
* **P4:** self-intersecting polygons exported (Spirit Hollow 10 holes, Mozingo 10, Veenker 5): `make_valid` before
  writing `zones_ll`.
* **P7 (Mozingo):** the tee set is `request` (yardages from the request file, `par: null`); requested `App` fell back
  silently. With no card, `length` is measured but printed as the card yardage.

### hazard vision (`course_data/vision_any/`)
* **V1 (high):** trees / long grass still far from the hand map on Spirit Hollow: landing-zone IoU trees 0.15,
  long grass 0.09 (bar 0.6); trees pass on 6% of holes.
* **V4:** a `native` ring hugs the outside of almost every `recovery` polygon (canopy shadow / crown edge as long
  grass; 325 native polygons) - tree edges then play as 50% lost ball. Tee points inside native: 2 Gold, 6 Rust,
  18 Rust. Self-intersecting recovery/native polygons on 1, 9, 10, 11, 13, 15-18.
* **V5b (21:05 update):** Veenker layers landed (e8096f0). QA's gapfill of `packages/veenker` adds 459 recovery /
  162 native; on 15 the woods left/right of the corner are now `recovery` and the Driver landing is 35% trees
  (`review/veenker_vision/15.jpg`); hole 5 landing 29% trees. The platform package itself still has the old
  (vision-less) zones until it is rebuilt. Contracts on the gap-filled Veenker: 266 passed, 27 failed.
* **V5 (Veenker):** no layers (`run_any`: `ValueError: window shape cannot be larger than input array shape`; a fix
  for the missing DTM landed at 20:4x, not rebuilt yet), so the 3rd course has no tree hazards and the model sends
  Driver through the woods (15, 9).
* **V2:** on-the-fly gapfill (no precomputed layers) is too heavy for the sandbox (one run OOM-killed at ~9 GB free).
  With the committed `vision_any.geojson` it takes seconds - keep that the only product path.
* **V3:** creek corridors narrow: water IoU 0.32 mean, passes on 20% of holes with water.

### product (`course_data/product/`)
* **R1 (high, golfer-facing, all three courses):** aims printed relative to the auto tee line ("98 yds right" SH 18,
  "58 right" Mozingo 3, "120 right" Veenker 15). Use decision 9.1-8 (aim line to the 250-yd point on the line of play)
  and say the aim against something visible.
* **R5 (high):** no guard on absurd aims: Veenker 15 Driver 120 yds right across the river and trees to another
  hole's green; such picks (|aim| > ~60 or landing outside the hole's own corridor) should be refused / flagged on
  the page, not printed as PLAY.
* **R2:** `--quick` is 6-26 min per course (wind grid dominates).
* **R3:** the Confidence column is empty in quick mode although `confidence.score` is in the package.
* **R4:** `plan_course.yml`/requests should point at `packages/<slug>/package.json`, not the stand-in.

### architect (`ARCHITECTURE.md`, `pipeline.py`, `acceptance.py`)
* **A1:** `tee_strategy.expected_strokes` raises `KeyError` for `green` and `ob_boundary` (allowed in packages by
  9.1-4); either map them in the model or state that consumers must.
* **A2:** the golden bar is unmet on every build. With the corrected hand map (19:5x) the platform package with vision
  picks the same club as final_decision.json on 50% of 16 tee shots, the OSM-only oracle on 50%. Tee/length errors on
  the as-built package are expected (Black boxes vs traced boxes); green within the bar 75%.
* **A3:** `pipeline.py` reads `imagery/<slug>/gapfill.geojson` (classifier trained on the hand map); any golden run on
  a v1 holes.json built that way is circular. QA's golden uses the oracle (vision disabled) and the platform package
  (vision_any, not hand-trained) only.
'''
