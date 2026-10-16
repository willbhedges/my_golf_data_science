"""Hand-written QA findings (visual review + bug reports), included verbatim at the end of REPORT.md by
golden_spirit_hollow.write_report(). Edit TEXT, then re-run golden_spirit_hollow.py (or run_qa.py)."""

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

### Spirit Hollow with vision (`qa/work/sh_v` = `vision_any/gapfill.py` on `packages/spirit_hollow`, precomputed lidar/NAIP layers; `review/spirit_hollow_vision/`)

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

## 4. End-to-end runs (`e2e.py`, `e2e.json`)

| course | package | result |
|---|---|---|
| Spirit Hollow, Black | `product/standin/spirit_hollow` (pipeline stand-in) -> `product/plan.py --quick` | **runs**: 19-page book (8.6 MB), aim sheets, self-contained 1.7 MB wind page covering all 14 tee shots, decision for every par 4/5. 26 min wall for "quick" (shared CPU). Card picks Driver on 9 of 14 tee shots. |
| Spirit Hollow, Black | `qa/work/spirit_hollow` = **platform `package.py` built offline** (seed_from_dir from course_data/spirit_hollow) | builds in seconds: 18 holes, all 4 card tee sets, zones + zones_ll consistent (reframe OK), elevation from the DEM. Contract failures below. |
| Mozingo Lake, White | `qa/work/mozingo_lake` = platform `package.py` offline from course_data/mozingo | builds 18 holes, but **no scorecard, no imagery, no DEM**: tee = OSM box nearest the line start (back tee), every length "measured", stage `imagery: missing` -> no book images, no vision. Not plannable as a product yet. |
| Spirit Hollow / Mozingo / **Veenker** (3rd) | **platform packages from Actions** `packages/{spirit_hollow,mozingo_lake,veenker}` | all three build (18 holes, imagery + DEM; Veenker card from golfify, 5 sets). **Vision failed in all three** (`stages.vision`: `IndexError` on Mozingo/Veenker, `ModuleNotFoundError: sklearn` on Spirit Hollow). plan.py e2e on these not run yet: the coordinator paused heavy local compute. |

Book review (Spirit Hollow stand-in, page 1 + hole pages): the card prints **"Driver 38 yds left" (1), "50 yds left" (14),
"98 yds right of the tee line" (18)**. These offsets are relative to the auto tee line (tee -> first hole-line node),
not to anything the golfer can see; on 18 the aim is on another part of the hole. The Confidence column is empty in
quick mode. The v1 hand-reviewed decision for 1 is 4-wood 5 yds right.

## 5. Bug reports by area

### data platform (`course_data/platform/`)
* **P1 (geometry, high):** `course.boundary` keeps only the largest ring of the course MultiPolygon (Spirit Hollow
  relation 13353211 has 3 outer rings: 101, 20, 12 x1e-6 deg2). Greens/tees of holes 5, 6, 7, 8, 9 fall 100-550 yds
  "outside the course" (`test_green_inside_course`, `test_tee_inside_course`). Anything that infers boundary OB from it
  will put 5 holes in OB. Fix: store the full MultiPolygon (GeoJSON) or a list of rings.
* **P2:** `course.state` is null when seeded from an existing fetch (`seed_from_dir`), and `town` too for Spirit Hollow;
  the request's `state`/`town` should be copied in.
* **P3:** Rust (forward) tees on par 3s 3, 12, 15 play 21-38% longer than the card along the hole line (e.g. 138 vs
  card 100): the forward box sits behind where the card says (`test_every_tee_set[...-Rust]`).
* **P4:** self-intersecting zone polygons survive into the package (water on 7/11/13/16, sand on 11):
  `geometry._holefree` output should be `make_valid`'d before export.
* **P6 (Veenker):** tee sets are duplicated as `Gold (Gold)` and `Red (Red)` next to `Gold`/`Red` (golfify parse);
  Red tees on 3, 6, 8, 11 fail the length check. Requested `White` silently fell back to `Blue` (warning only) - the
  golfer should be asked.
* **P7:** with no card the package reports the measured length as `length` and the book prints it as the card
  yardage (Mozingo); mark it as measured.
* **P8:** Veenker's package says `stages.vision = "ok: vision_any/gapfill.py"` but gapfill returned *missing*
  (`vision_any/veenker/vision_any.geojson` does not exist; gapfill error "window shape cannot be larger than input
  array shape") - the package carries only 15 `recovery` / 7 `native` polygons (OSM) on a heavily wooded course.
  The stage must report gapfill's own `stages.vision` string, not "ok".
* **P5 (Mozingo):** no scorecard source found offline (request yardages / card file / golfify / club site all missing)
  -> every hole falls back to the back-most OSM tee; the request should carry yardages or the Actions scorecard fetch
  must run. No imagery/DEM for Mozingo in the package (imagery request missing).

### hazard vision (`course_data/vision_any/`)
* **V1 (blocker for the club pick):** no gap-fill merged into any package: landing-zone IoU for trees and long grass is
  0.00 on every Spirit Hollow hole. Concrete misses in section 3 (holes 1, 6, 9, 11, 13, 18).
* **V1b:** in the Actions builds `stages.vision` = `failed: IndexError: list index out of range` (Mozingo, Veenker)
  and `failed: ModuleNotFoundError: No module named 'sklearn'` (Spirit Hollow: add scikit-learn to the workflow).
* **V5 (Veenker):** no layers built: `run_any` fails with `ValueError: window shape cannot be larger than input array
  shape`, so the third course has no trees/long grass at all (see P8).
* **V2:** `gapfill.py` first failed with `ModuleNotFoundError: run_any` (module landed later); a second run on
  `--holes` was OOM-killed (exit 137, machine had ~9 GB free) on a 1876x2162 1-m stack; a third run on the platform
  package is paused by the coordinator. QA has not yet seen a gap-filled package.
* **V4:** native rings around every tree polygon; tee points inside native; zones/zones_ll order mismatch after
  gap-fill; self-intersecting output polygons (all detailed in section 3, "Spirit Hollow with vision").
* **V3:** creek corridors are 3-yd centre-line buffers (mean water IoU 0.37); on 10, 11, 14, 16, 18 the channel + banks
  are 10-20 yds wide in NAIP.

### product (`course_data/product/`)
* **R1 (high, golfer-facing):** aims are printed relative to the auto tee line; on dog-legs that line points off the
  landing area, so the card says "98 yds right of the tee line" (18), "50 yds left" (14), "38 yds left" (1). Express the
  aim against something visible (fairway centre / a landmark / distance from the left edge) or re-aim the frame at the
  ~250-yd point of the line of play.
* **R2:** `plan.py --quick` took 26 min wall for one course (shared CPU; wind grid dominates: 61 winds x 14 shots).
  Fine for Actions, too slow for "quick".
* **R3:** quick-mode book prints an empty Confidence column; the package's per-hole `confidence.score` exists and
  could be printed.
* **R4:** the stand-in package is not course_package/1 (`schema`, no `zones_ll`, `exposure`, `yards{set}`); retire it
  in favour of the platform package (which `plan.py` should be pointed at).

### architect (`ARCHITECTURE.md`, `pipeline.py`, `acceptance.py`)
* **A1:** `tee_strategy.expected_strokes` raises `KeyError` for `green` and `ob_boundary`, which 9.1-4 allows in
  packages. Either the model maps them or the contract says every consumer maps `green -> fairway`,
  `ob_boundary -> ob` (QA's reader does).
* **A2:** acceptance bars are unmet even with oracle tees (tee 50%, green 56%, length 62%, club 62%); the as-built Black
  package matches `final_decision.json` on 81% of tee shots (13/16), which is the only bar met - largely because the
  hand-reviewed picks lean Driver/4-wood on open holes where missing trees don't matter.
'''
