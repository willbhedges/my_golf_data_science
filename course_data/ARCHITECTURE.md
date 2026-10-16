# Auto course: architecture

The goal is that the golfer says **"Spirit Hollow, white tees"** (any US course) and the system builds, with
no screenshots, everything `mozingo/tee_strategy.py` and `mozingo/yardage_book.py` need for every hole:
the tee point for the chosen tee set, the green centre, par, yardage, hazard polygons (`fairway`,
`recovery` = trees, `native` = long grass, `water`, `sand`, `ob`) in the model's frame, and a clean
overhead image for the book.

Owner of this file, `pipeline.py` and `acceptance.py`: architect. Stage owners are listed in section 1.
The status section (section 8) is kept current; read it first.

---

## 1. Stages

```
 "Spirit Hollow", "white"
        |
 S0 RESOLVE ------------- course.json         (OSM id, name, centre, bbox, slug)                 spike: fetch_course.find_course
        |
 S1 FETCH (Actions) ----- osm.geojson         (every golf/landcover feature, WGS84)              spike: fetch_course.py
        |                 scorecard.json      (tee sets x holes: par, yards, hcp)                tees/   (fetch_scorecards.py ...)
        |                 imagery/naip.tif    (NAIP RGB(+NIR) GeoTIFF, date, CRS)                imagery/
        |
 S2 TEES ---------------- tees.json           (per hole: tee point for the chosen set + how)    tees/
        |
 S3 BUILD HOLES --------- holes_osm.json      (per hole in the yard frame, OSM zones only)       geometry/
        |
 S4 GAP-FILL ------------ zones_vision.json   (classifier zones where OSM has nothing)           imagery/  (+ spirit_hollow/vision*.py)
        |
 S5 RENDER -------------- images/holeNN.png   (920x2000 overhead in the virtual pixel frame)     imagery/
        |
 S6 MERGE + QA ---------- holes.json         (the course model, with provenance + confidence)    architect: pipeline.py
        |                 course_auto.py      (generated module, same API as spirit_hollow/course.py)
        |                 qa.md               (per-hole flags; holes below the bar are listed)
        |
 S7 BOOK ---------------- <slug>/output/*_Strategy.pdf via yardage_book.use_course(...)          existing book code
```

| Stage | Runs where | Owner | Module (expected entry point) |
|---|---|---|---|
| S0 resolve | Actions (Nominatim + Overpass) | spike | `fetch_course.find_course(name, near, radius_m)` |
| S1 OSM fetch | Actions | spike | `fetch_course.py --name --near --out` -> `osm.geojson`, `summary.json` |
| S1 scorecard | Actions (web) | tee scientist | `tees/fetch_scorecards.py` -> `tees/raw/`; parsed to `scorecard.json` |
| S1 imagery | Actions (Planetary Computer STAC) | imagery | `imagery/*` -> `imagery/naip.tif` + `imagery/meta.json` |
| S2 tees | local, offline | tee scientist | `tees.<mod>.place_tees(fc, scorecard, tee_set) -> tees.json` |
| S3 holes | local, offline | geometry | `geometry.<mod>.build_holes(fc, tees) -> {ref: hole}` (fallback: spike `osm_to_model.convert`) |
| S4 gap-fill | local or Actions | imagery | `imagery.<mod>.gapfill(course_dir, holes) -> {ref: [zone,...]}` |
| S5 render | local (needs the GeoTIFF) | imagery | `imagery.<mod>.render_hole(course_dir, hole, out_png, frame)` |
| S6 merge, QA | local | architect | `pipeline.py` |
| S7 book | local | existing | `yardage_book.use_course(...)`, `yardage_book.build()` |

The network rule: this sandbox cannot reach Overpass, Nominatim, Planetary Computer or scorecard
sites. Everything with a URL in it runs in a GitHub Actions workflow that commits its outputs to the
branch (pattern: `.github/workflows/course_fetch.yml`, `deep_features.yml`). Everything after S1 is
offline and deterministic given the S1 files, so it runs in the sandbox, in CI or on the golfer's laptop.
`pipeline.py` never fetches; when an S1 file is missing it prints the `gh workflow run` command to get it.

## 2. Coordinate systems

Four frames, each with one job. Every conversion goes through the hole's **tee line**.

| Frame | Units, axes | Used for |
|---|---|---|
| **WGS84** | `[lon, lat]` (GeoJSON order, always) | Storage of everything fetched: OSM, tees, greens, imagery bounds |
| **Local ENU** | metres east, north of a course origin (equirectangular: `e = (lon-lon0)*cos(lat0)*111320`, `n = (lat-lat0)*111320`) | Distances, buffering, imagery warping. Error < 0.1% within 3 km. |
| **Yard frame** (proposed native model frame) | yards; `x` = right of the tee line, `y` = **minus** yards along it (screen y grows down). Tee = `(0, 0)`, `dot270 = (0, -270)`. | `holes.json`. The model runs on it directly: `hole_frame` gives `ppy = 1`, `fwd = (0,-1)`, `right = (1,0)`. |
| **Virtual pixel frame** | 920 x 2000 px, `ppy = 3.4`, tee at `(460, 1900)`: `px = 460 + 3.4*x`, `py = 1900 + 3.4*y` | Generated `course_auto.py` and the rendered images, so `yardage_book.draw_tee` (`extent=(0,920,2000,0)`, view `y 540..2000` = 0-429 yds, `x` = +/-135 yds) works unchanged. |
| **Fitted pixel frame** (what geometry emits by default, `frame="fit"`) | 920 x 2000 px, tee at `(tx, 1920)`, `ppy = px_per_yd` fitted per hole (<= 4.5) so the tee, the 240-330 landing box and the green are on screen | `holes.json` today. Same contract as the virtual frame (tee line straight up, `dot270` exactly 270 yds up it), so the model and the book can't tell the difference; the renderer reproduces it exactly from `tee_ll`, `aim_ll`, `px_per_yd`, `tee` (planar projection: UTM yards, not ENU; the two differ by grid convergence, ~1.2 deg here). |

**The tee line.** Tee point -> *aim point*, where the aim point is the first OSM `golf=hole` node at least
60 yds past the tee (the hole's first dog-leg node; the green for a par 3). This plays the role of the
app's dashed line in the screenshots. Aim offsets in the book ("5 yds left of the line") are relative to
it. It differs from the app's line by a few degrees on dog-legs, which is why `acceptance.py` registers
frames before comparing positions.

Conversions (implemented in `osm_to_model.Frame`; the geometry module must give the same numbers):

```
en      = ENU(lon, lat) about the tee            (metres -> yards: / 0.9144)
fwd     = unit(ENU(aim) - ENU(tee));  right = (fwd.n, -fwd.e)
x, y    = en . right,  -(en . fwd)               (yard frame)
px, py  = 460 + 3.4 x,  1900 + 3.4 y            (virtual pixel frame)
```

The inverse (pixel -> WGS84) is what the image renderer needs: `x = (px-460)/3.4`, `y = (py-1900)/3.4`,
`en = x*right - y*fwd` (yards -> metres), then ENU -> lon/lat. `holes.json` stores `tee_ll`, `aim_ll` per
hole, so any consumer can rebuild the frame without the geometry code.

**Why a yard-native frame.** The traced maps carry a scale error from one tee->270-dot vector per
screenshot (PROJECT.md R5: 1-2% = 3-6 yds at 300). Real coordinates have no scale to estimate; the
frame is yards by construction. The model already accepts it (it only uses ratios through `hole_frame`).
The pixel frame exists only for the book's image extent; it can be retired when `draw_image` takes
`extent` from the hole dict (one-line change in `yardage_book.py`, integrator's call).

## 3. Data contracts

All JSON is UTF-8, keys are strings, hole refs are strings (`"1"`, `"2"`, ... `"9"`; multi-tee keys are
added in S6 as `"2B"`, `"2F"` when the golfer asks for two sets). Coordinates in WGS84 are `[lon, lat]`.

### 3.1 `course.json` (S0)
```json
{"schema": "course/1", "name": "Spirit Hollow Golf Course", "slug": "spirit_hollow",
 "osm": {"type": "relation", "id": 13353211}, "center": [-91.1442, 40.7605],
 "bbox": [-91.1522, 40.7531, -91.1362, 40.7679], "address": "Burlington, IA",
 "candidates": [{"name": "...", "osm": {...}, "dist_km": 3.1}]}
```
Today `summary.json["course"]` carries this; `pipeline.py` reads either.

### 3.2 `osm.geojson` (S1)
A GeoJSON FeatureCollection, WGS84. Each feature's `properties` = the raw OSM tags plus `osm_id`,
`osm_type`, `inside_course` (bool). Holes are `golf=hole` LineStrings from tee end to green end with
`ref`, `par`, maybe `dist`/`handicap`. Produced by `fetch_course.py` (exists, works for Spirit Hollow:
18 holes, 103 tee boxes, 26 greens, 20 fairways, 50 bunkers, 11 lateral water hazards; **no tee colours,
no woods/scrub polygons, no tall-grass tagging** on this course).

### 3.3 `scorecard.json` (S1, tee scientist)
```json
{"schema": "scorecard/1", "source": "https://...", "fetched": "2026-10-16",
 "tee_sets": {
   "white": {"rating": 70.1, "slope": 125, "total": 6100,
             "holes": {"1": {"par": 4, "yards": 401, "hcp": 7}, "...": {}}},
   "blue":  {"...": {}}},
 "aliases": {"middle": "white", "men": "white"}}
```
Pars are tee-independent in most cards but are stored per set (some courses differ for forward tees).
**As built** (`course_data/tees/scorecard.json`): `tee_sets.<Name> = {colour, aliases: [...], yards: [18],
total, ratings}` with `par: [18]` at the top level. `pipeline._norm_card` reads both shapes.
Tee set names are matched case-insensitively, then through each set's `aliases` ("blue" -> Black,
"red" -> Rust). Spirit Hollow's White card is 6040 yds; the hand-traced holes are NOT white tees
(1 = 413 vs White 376): they mix Black/Gold-ish boxes, so acceptance uses "oracle tees" (section 7).

### 3.4 `tees.json` (S2, tee scientist)
```json
{"schema": "tees/1", "tee_set": "white",
 "holes": {"1": {"tee_ll": [-91.14, 40.76], "box_osm_id": 923958000,
                 "how": "tagged|length_match|interpolated|hole_line_start",
                 "scorecard_yards": 401, "measured_yards": 404, "confidence": 0.9}}}
```
**As built** (`course_data/tees/tee_positions.json`): `holes.<ref>.tees.<Set> = {lat, lon, method
(tee_centroid | tee_axis | walkback), tee_id, confidence, error_yd, dist_yd, d_front, d_back, shared_with}`.
Geometry's `build(..., tees=<that file>, tee_tag=<set>)` uses the point as the tee (provenance
`tee stage: White tee_axis`); `pipeline.py` passes it automatically.
`measured_yards` = tee -> hole-line nodes -> green centre, along the line (how scorecards measure).
`how` order of trust: `tagged` (OSM tee box tagged with the colour) > `length_match` (the box whose
measured yards are within 8 yds of the card) > `interpolated` (box between two matched sets, or a
point on the hole line at the card yardage when no box fits) > `hole_line_start`.

### 3.5 Hole in the yard frame (S3 output, S6 input) - `holes_osm.json`
```json
{"schema": "holes/1", "frame": "yard", "holes": {"1": {
  "ref": "1", "par": 4, "length": 401,
  "tee_ll": [lon, lat], "aim_ll": [lon, lat], "green_ll": [lon, lat],
  "tee": [0, 0], "dot270": [0, -270], "green": [-14.2, -398.0],
  "hole_line": [[0, 0], [0, -290], [-14, -398]],
  "green_polygon": [[x, y], ...],
  "zones": [["ob", [[x, y], ...]], ["fairway", [[x, y], ...]], ...],
  "zone_src": ["osm:way/123", "osm:boundary", ...],
  "provenance": {"tee": "length_match", "green": "osm_green", "par": "osm", "length": "scorecard"}}}}
```
Zone rules (the model's `lie_at` contract): later zones win where they overlap, so S3/S6 sort by
`ob < native < recovery < fairway < water < sand` (spike's `ZONE_ORDER`). Polygons are simple vertex
lists (no holes); holes are encoded as keyholes (`osm_to_model.keyhole`). Anything not covered is rough.
Window kept per hole: +/-150 yds lateral, 40 yds behind the tee to 40 yds past the green (min 330 along).

### 3.6 `zones_vision.json` (S4, imagery)
```json
{"schema": "zones_vision/1", "imagery": {"source": "naip", "date": "2023-08-14", "gsd_m": 0.6},
 "model": "vision2 / ndvi-texture v1",
 "holes": {"1": [{"lie": "recovery", "poly": [[x, y], ...], "p": 0.86, "area_yd2": 3120}]}}
```
Gap-fill only adds `recovery`, `native` and `water` where OSM has no polygon of a penal class; it never
removes or reshapes an OSM `fairway`, `water`, `sand` or `green`. Minimum polygon 150 yd2,
probability >= 0.7, simplified to 2 yds.

### 3.7 Images (S5)
`<slug>/screenshots/holeNN.png` (the folder `yardage_book.draw_image` reads; `holeNN_b.png` for second tee sets), 920 x 2000 RGB, north-unaware:
rendered in the **virtual pixel frame of that hole**, so the tee is at `(460, 1900)` and the tee line runs
straight up. Par 3s use the same frame with the flag on the line. A sidecar `images/index.json` records
for each image the imagery date, the frame (`tee_ll`, `aim_ll`, `ppy`, `tee_px`) and the fraction of
pixels with no imagery.

### 3.8 `holes.json` (S6, the course model - the one file the rest of the system reads)
```json
{"schema": "course_model/1", "course": {...course.json...}, "tee_set": "white",
 "built": "2026-10-16T18:30Z", "frame": "yard", "pixel_frame": {"size": [920, 2000], "tee_px": [460, 1900], "ppy": 3.4},
 "stages": {"osm": "ok", "scorecard": "missing", "tees": "fallback:osm_to_model.pick_tee", "geometry": "fallback:spike", "vision": "missing", "images": "missing"},
 "holes": {"1": {...hole in the yard frame (3.5)...,
                 "image": "hole01.png",
                 "confidence": {"score": 0.71, "osm": 0.62, "imagery": 0.0, "inferred": 0.38,
                                "flags": ["no tree polygons in the landing zone", "tee from length match"]}}},
 "par3": {"7": {"tee": [0, 0], "flag": [0, -159], "center": 159, "front": 150, "back": 170,
                "green": [[lat, depth], ...], "haz": {"left": "sand", "right": "rough", "short": "water", "long": "native"}}}}
```

### 3.9 Generated `course_auto.py` (S6) - compatibility with `spirit_hollow/course.py`
Exposes `HOLES`, `PAR3`, `NOTES`, `AIM_AT`, `ORDER`, `LABELS`, `APP` (empty), `GREEN_SIDE` (empty), in the
**virtual pixel frame**, so `build.py` swaps `import course` for `import course_auto as course`:

* `HOLES[k] = dict(par, image, length, tee=(460, 1900), dot270=(460, 1900 - 270*3.4), green=(px, py),
  zones=[(lie, [(px, py), ...]), ...], aim_min=-40, aim_max=40, auto=dict(confidence...))`
  The model reads `tee`/`dot270` only through `hole_frame`, so a synthesised `dot270` exactly 270 yds up the
  line reproduces the yard-frame results bit for bit (the scale is exact, not estimated).
* `length` = scorecard yards for the set when known (the convention the book prints), else the
  measured tee -> green distance along the hole line.
* Par 3s go to `PAR3` via the same fields `_par3` produces: `tee`, `flag` (green centroid), `center`,
  `front`/`back` (along the tee-flag line), `green` as `(yds right, yds past the flag)`, `haz` from the
  zones touching each side of the green, plus generated `note`/`short`.
* `NOTES`/`AIM_AT` get a generated provenance line ("OSM fairway + bunkers, trees from imagery,
  tee matched to the card at 401 yds"); the book's text fields stay human-editable.

## 4. Merge rules (S6)

1. Tee: `tees.json` if present; else spike `pick_tee` with the card yardage; else hole-line start.
2. Green: OSM `golf=green` polygon nearest the hole line's last node (within 40 yds); centre = polygon
   centroid. Else the last node (flag: `green from hole line`).
3. Par: card > OSM `par` tag > length rule (<= 250 -> 3, <= 470 -> 4, else 5).
4. Length: card yards > measured along the line. A measured-vs-card gap > 15 yds is a QA flag (wrong box).
5. Zones: OSM first, then vision gap-fill for penal classes, then the course boundary as OB (only if
   the course has OB evidence - see failure modes), sorted by `ZONE_ORDER`.

## 5. Failure modes and what the pipeline does

| Failure | Detection | Handling |
|---|---|---|
| Course name ambiguous / not in OSM | S0 returns 0 or several `leisure=golf_course` | Ask the golfer with the candidate list (name, town, distance). No guess. |
| Holes missing in OSM (no `golf=hole`, or fewer than 9/18) | count refs vs scorecard | Hole line = tee box -> green pairs by card yardage and sequence (nearest unused green at the card distance +/-10%). Flag `inferred hole line`, confidence <= 0.5. Course with no tees *and* no greens: stop, ask for screenshots (the old path). |
| Tees missing / untagged colours (Spirit Hollow: 103 boxes, 0 colours) | `how != tagged` | Length match to the card (S2). No card: the box nearest 85% of the longest box (a typical white/middle) and flag it. |
| Tee box shared by two holes or a practice tee | box within 30 yds of two hole lines | Choose by projected position and heading toward the hole's aim node (spike's window `-150 < s < L-100`). |
| Mis-tagged polygons (fairway mapped as rough, `natural=sand` on a beach, ponds as `landuse=basin`) | vision disagreement > 40% of a polygon; area sanity (fairway 25-70 yds wide) | Keep OSM, add a QA flag; imagery-only classes never override `fairway`/`water`/`sand`. |
| Under-mapped trees and long grass (the common case: Spirit Hollow has none) | penal-class area in the landing zone = 0 while imagery NDVI/texture says woods | S4 gap-fill. Without imagery: hole confidence capped at 0.5 and the book says "trees not mapped". |
| OB not mapped | no `golf=out_of_bounds`, only the course boundary | Course boundary -> OB only where it borders `building`/`landuse=residential`/roads within 40 yds; elsewhere boundary = `native`. Flag every hole with OB from inference; golfer confirms from local rules. |
| Imagery date / season | NAIP `datetime` in metadata | Prefer leaf-on (May-Sep) for trees, leaf-off is better for creeks under canopy; store both when available. Record date in `images/index.json`; flag course changes (OSM `start_date`, construction). |
| Imagery shadow / tilt | NAIP is orthorectified: no lean, unlike the app screenshots | Trees traced at the canopy edge from NAIP, i.e. *wider* than the hand maps (traced at trunks). Acceptance expects tree IoU to be the weakest class. |
| Water as a line only (`waterway=stream`) | LineString | Buffer 4 yds (stream/ditch) or 10 yds (river); banks are `native` only if imagery says so. |
| Card has a hole the course re-routed | card par/yards vs OSM differ > 25% | Trust OSM geometry, card par; flag. |

## 6. Confidence per hole

Each hole gets `confidence = {score, osm, imagery, inferred, flags}`:

* Evaluate the landing-zone grid (220-340 yds along, +/-45 yds lateral, 5-yd step, 425 cells) and the
  source of the lie each cell gets: `osm` (inside an OSM polygon), `imagery` (inside a gap-fill polygon),
  `inferred` (rough by default, boundary OB, buffered lines). `osm + imagery + inferred = 1`.
* Default-rough cells count as `inferred` unless imagery checked them (imagery says "grass, low"),
  because the dangerous error is an unmapped hazard scored as rough (PROJECT.md R6).
* Point items: tee (`tagged` 1.0, `length_match` 0.9, `interpolated` 0.6, `hole_line_start` 0.4),
  green (`osm_green` 1.0, `hole_line_end` 0.6), par/length (card 1.0, OSM 0.8, rule 0.5).
* `score = 0.35 * tee + 0.15 * green + 0.10 * par_length + 0.40 * (osm + 0.8 imagery + 0.3 inferred)`.
* Bands: >= 0.8 "auto", 0.6-0.8 "check the flags", < 0.6 "needs screenshots / human review". The book
  prints the band on each hole page; `qa.md` lists the flags.

## 7. Acceptance (`acceptance.py`)

Compares an auto build of Spirit Hollow with the hand-reviewed `spirit_hollow/course.py`.

* Frames: the traced holes are in screenshot pixels with no georeference, and their line is the app's,
  not OSM's. So each traced hole is first converted to yards (`hole_frame`) and then **registered** to the
  auto hole by a rigid transform (rotation +/-15 deg, shift +/-40 yds, scale 0.95-1.05) that maximises
  agreement of the hazard rasters (fairway, water, sand, which both sources map well) over the whole
  window. The tee and green are *not* used to fit, so their errors are honest. Scale is fixed at 1
  (a free scale shrinks the hand-traced fairways, which are ~2x OSM's, onto OSM's). The imagery team's
  NAIP registration of the screenshots (`imagery/traced_align.py` -> `traced_registration.json`, ECC on
  gradient images) is preferred when its ECC >= 0.3; the raster fit is then reported as a cross-check.
* The traced green is itself uncertain: it is trilaterated from three app numbers rounded to 1 yd, which is
  ill-conditioned laterally for far greens (hole 4: +/-32 yds, 17: +/-25, 5: +/-16). The green check passes
  within max(10 yds, that spread).
* Per hole: tee error and green error (yds, after registration), length error (|card or measured -
  traced `length`|, frame-free), landing-zone IoU per class (220-340 along, +/-45, in the traced frame),
  and the club pick: `t.best_aim` for Driver, 2-wood and 4-wood on both maps, same club or not.
* Bar (proposed): tee and green within 10 yds, length within 5 yds, landing-zone IoU > 0.6 for water,
  OB and trees (classes present on the hole in either map), same club on >= 80% of the 16 tee shots.
* **Circularity rules.** (a) `imagery/classify.py` trains on the hand-traced zones, so for acceptance the
  gap-fill on hole k must come from the leave-one-hole-out model that did not see hole k
  (`gapfill_loho/<k>.geojson` or a `holdout` property); the product build uses the all-holes model.
  (b) Since bdd4aa1, `spirit_hollow/course.py` narrows its fairways to OSM's mown width at 200-340 yds
  (`first_cut`), so fairway IoU against OSM is partly circular; read it as a sanity check only. Water,
  OB, trees and the club pick remain independent.
* Hole keys: traced `2B`/`2F`/`9B`/`9F` are matched to auto holes 2/9 built with the traced length as the
  card yardage (that picks the same box), so one auto build covers both tees.

Run: `python3 course_data/acceptance.py [--holes course_data/spirit_hollow/holes.json] [--fast]`.
Writes `course_data/spirit_hollow/acceptance.json` and `acceptance.md`.

## 8. Status

(updated by the architect; newest first)

### 2026-10-16 18:45 UTC

* v2 team onboarded (section 9): platform/, vision_any/, product/, qa/. Contracts: package/1 (9.2),
  `gapfill(package, imagery_dir) -> package` (9.3), request files (9.4). First request committed:
  `course_data/requests/package_ia_spirit_hollow.json` (Black tees). None of platform/, product/ exist yet;
  vision_any/ has a fetch commit (3DEP lidar HAG, Meta CHM, WorldCover, NAIP); qa/ has `packages.py`.
* The committed v1 build is now **Black tees** (the golfer's set): `pipeline.py --tees black` uses
  `tees/tee_positions.json` for every hole; card yardages 391/501/148/... match the measured lengths
  (no >15-yd flags); confidence 0.71-0.80 on tee holes, 0.93 on par 3s.
* S7 works: `pipeline.py --book` produced `spirit_hollow/output/Spirit_Hollow_Auto_Strategy.pdf` + aim
  sheets from NAIP renders (white-tee build, 2 min). Found: on dog-legs the auto aim line points at the
  first hole-line node, so the best aim hit the +/-40 search bound (hole 1: "40 yds left"). Auto holes now
  search +/-60; better fix for geometry: aim line = tee -> hole-line point at ~250 yds along the line of play.
* Acceptance re-run against the new hand map (first_cut + AUDIT_FIXES): unchanged headline (club 62%,
  tee/green within 10 yds on 8 of 11 NAIP-registered holes, trees/long grass IoU 0).

### 2026-10-16 18:35 UTC

`python3 course_data/pipeline.py --course "Spirit Hollow" --tees white` runs end to end offline in ~25 s
and writes `course_data/spirit_hollow/{holes.json, course_auto.py, qa.md, screenshots/hole01..18.png}`.

| Stage | State | Notes |
|---|---|---|
| S0 resolve | works (from the fetched `summary.json`) | Free-text resolve of a *new* course still needs an Actions run (`course_fetch.yml`). |
| S1 OSM | done | 18 holes, 103 tee boxes (no colours), 26 greens, 20 fairways, 50 bunkers. No woods, scrub, tall grass or OB tags. |
| S1 scorecard | done (tees/) | Club page, 4 sets (Gold/Black/White/Rust), pars, handicaps; aliases map blue->Black, red->Rust. |
| S1 imagery | done (imagery/) | NAIP 2023-09-01 0.3 m RGB + NIR, USGS 3DEP DEM. |
| S2 tees | done (tees/) | `tee_positions.json`: every set on every hole, method + confidence. Wired into geometry (`tees=`). |
| S3 holes | done (geometry/) | Fitted pixel frame + yard frame; par-3 entries; `tee_ll/aim_ll/green_ll` + provenance per hole. |
| S4 vision gap-fill | **missing** | No tree / tall-grass layer yet. This is the biggest gap (see acceptance). |
| S5 images | done (imagery/render.py) | Exact re-projection of NAIP into each hole's frame. |
| S6 merge + QA | done (pipeline.py) | Confidence per hole: 0.67-0.79 on tee holes ("check the flags"), 0.93-0.96 on par 3s. |
| S7 book | in test | `pipeline.py --book` -> `yardage_book.use_course(...)`. |

**Acceptance (oracle tees, `--fast`), see `spirit_hollow/acceptance.md`:**
* Club pick: same club on 62% of 16 tee shots (bar 80%) - **fails**. Mismatches 1, 8, 9B, 9F, 16, 17.
* Geometry where the same tee box is used (NAIP-registered holes): tee error 1.4-8.4 yds and green error
  1.6-8.3 yds on 8 of 11 holes - **meets the 10-yd bar**. Failures are explained: 2F, 9B, 17 picked a
  different box (no OSM box at the traced length; 17 is 20 yds short), 4 and 11 have traced greens that are
  themselves uncertain (4: +/-32 yds lateral from the app-number trilateration; 11 is put on the line by hand
  though its offset is ~34).
* Length within 5 yds on 62% of tee shots; misses are the same box-selection cases (2B -25: the 607 back tee
  is not mapped in OSM).
* Landing-zone IoU: fairway 0.56, water 0.37, sand 0.40, OB 0.18, **trees 0.00, long grass 0.00**.
  OSM water is the creek centre-line buffered 3 yds; the hand maps include the banks.

**Top blockers**
1. Trees / long grass: OSM has none on this course; S4 gap-fill must produce `recovery` and `native`
   polygons (NAIP NDVI + NIR texture + DEM-derived canopy height). Without it every landing zone scores
   unmapped hazards as rough, which biases toward driver.
2. Creek corridors: buffer `waterway=stream` by the visible channel + banks (imagery), not 3 yds.
3. Tee boxes missing from OSM (2 back 607, 15 back 215, 17): fall back to walkback but flag.
4. OB: only the course boundary is available; houses on 2F/4/5/8/9B come from `building` tags only
   where mapped.
5. Acceptance needs NAIP registration of all 16 traced holes (11 now) to retire the raster-fit fallback,
   whose rotation is poorly constrained on dog-legs (13: 84-yd green error).

---

## 9. Any-course product (v2): teams and contracts

The Spirit Hollow pipeline (sections 1-8) becomes a product for **any US course**: "Spirit Hollow, IA,
Black tees" -> a course **package** -> a PDF book + wind page. The package is the one hand-off between
data and product; every other team reads or augments it.

```
 request file ----> platform/ (course_package.yml) ----> package.json (WGS84, all tee sets)
 (course, state,       OSM + scorecard + tees + geometry          |
  tee set)                                                         v
                     vision_any/ gapfill(package, imagery_dir) -> package.json (+ vision zones)
                                                                   |
                     product/ plan.py (plan_course.yml) ---------> <slug>/output/*_Strategy.pdf, wind page
                                                                   |
                     qa/ contract tests, Spirit Hollow golden, visual review -> qa/REPORT.md
```

| Folder | Owner | Provides (interface) | Reads |
|---|---|---|---|
| `course_data/platform/` | data platform | `package.json` (9.2) via `course_package.yml`; Python: `build_package(name, state, tee_sets=None) -> dict` | OSM, scorecards (Actions), `geometry/`, `tees/` |
| `course_data/vision_any/` | hazard vision | `gapfill(package: dict, imagery_dir: str) -> dict` (9.3): the same package with vision zones added | package, NAIP, USGS 3DEP lidar (HAG) |
| `course_data/product/` | product | `plan.py --package <path> --tees Black [--wind auto]` -> book PDF + wind page; `plan_course.yml` | package, `mozingo/tee_strategy`, `yardage_book`, `spirit_hollow/wind.py` |
| `course_data/qa/` | QA | `packages.py` (lenient reader of package.json and holes.json), contract tests, Spirit Hollow golden comparison, visual review -> `qa/REPORT.md` | every package; `spirit_hollow/course.py` |
| `course_data/{geometry,tees,imagery}/` | v1 engineers | libraries the platform calls (`build_holes.build`, `place_tee.place_tee_sets`, `render.Frame/render_hole`, `classify.py`) | |
| `course_data/{ARCHITECTURE.md,pipeline.py,acceptance.py}` | architect | contracts; dev orchestrator; acceptance vs the hand map | |

### 9.1 Decisions

1. **The package is frame-free.** Everything in `package.json` is WGS84 `[lon, lat]`. The pixel/yard
   frame is chosen by the consumer per tee set (`render.Frame(tee_ll, aim_ll, ...)`), so one package
   serves every tee set and the book, wind page and QA can't disagree about geometry. (holes.json /
   course_model/1 stays as the v1 per-tee-set, pixel-frame artefact; `pipeline.py` keeps producing it.)
2. **Golfer's tee set: Black** at Spirit Hollow (`tees/scorecard.json`: 6589 yds). Product default
   comes from the request file; Spirit Hollow requests say `"tees": "Black"`.
3. **Triggering Actions.** `workflow_dispatch` from the sandbox returns 403. Every workflow that must be
   started from here is triggered by a committed **request file** (9.4) via `on: push: paths:`.
   Workflows commit their outputs back with the pull-rebase-retry loop from `course_fetch.yml`.
4. **Lie classes** (model contract, `tee_strategy.lie_at`; later zones win): order
   `ob_boundary < native < recovery < ob < first_cut < fairway < water < sand`. `first_cut` is the
   intermediate cut beside the mown fairway (scored via `tee_strategy.FIRST_CUT_COST`); OSM rarely maps
   it, so a package may omit it; the hand map synthesises it. `green` may appear in packages and is
   treated as `fairway` by the model.
5. **Vision never overrides OSM** `fairway`, `green`, `water`, `sand`; it adds `recovery`, `native`,
   and `water` only where OSM has no polygon of that class (section 3.6 thresholds: p >= 0.7, >= 150 yd2,
   simplified to 2 yds). Each vision zone carries `src` and `p`.
6. **Hand-map reference.** `spirit_hollow/course.py` (with `AUDIT_FIXES` and `first_cut`) is the golden
   map. QA's golden comparison and `acceptance.py` must use the same metric definitions (section 7);
   QA owns the reported numbers going forward, `acceptance.py` is the reference implementation.
7. **Wind** is a product concern: `spirit_hollow/wind.py` `adjust_clubs(clubs, speed_mph, rel_dir_deg,
   gust_mph, temp_f, exposure)` with `hole_relative(wind_from_true, hole_bearing_true)`. The package
   supplies each tee set's `bearing_deg` (tee -> aim, degrees true) and an `exposure` hint (share of the
   landing zone's edge that is trees, from vision) so the product needs no geometry of its own.

### 9.2 `package.json` (schema `package/1`)

Location: `course_data/courses/<state>/<slug>/package.json` (slug = `pipeline.slugify(name)`, state = 2-letter
lower case, e.g. `courses/ia/spirit_hollow/`). Supporting files sit next to it (`osm.geojson`, `scorecard.json`,
`imagery/` pointer, `qa.json`).

```json
{"schema": "package/1",
 "course": {"name": "Spirit Hollow Golf Course", "slug": "spirit_hollow", "state": "IA", "city": "Burlington",
            "osm": {"type": "relation", "id": 13353211}, "center": [-91.1442, 40.7605],
            "bbox": [-91.1522, 40.7531, -91.1362, 40.7679], "boundary": [[lon, lat], ...]},
 "built": "2026-10-16T19:00Z",
 "sources": {"osm": {"fetched": "...", "file": "osm.geojson"},
             "scorecard": {"url": "...", "confidence": "high"},
             "imagery": {"naip_date": "2023-09-01", "dir": "course_data/imagery/spirit_hollow"},
             "dem": {"source": "USGS 3DEP", "file": "..."}},
 "tee_set": "Black",
 "tee_sets": {"Black": {"aliases": ["black", "blue", "member", "middle"], "total": 6589, "rating": 71.4, "slope": 124}},
 "stages": {"osm": "ok", "scorecard": "ok", "tees": "ok", "geometry": "ok", "vision": "missing"},
 "holes": {
  "1": {"ref": "1", "par": 4, "hcp": 3,
        "yards": {"Gold": 426, "Black": 391, "White": 376, "Rust": 299},
        "hole_line_ll": [[lon, lat], ...],
        "green_ll": [lon, lat], "green_polygon": [[lon, lat], ...],
        "tees": {"Black": {"tee_ll": [lon, lat], "aim_ll": [lon, lat], "bearing_deg": 352.1,
                           "method": "tee_axis", "confidence": 0.9, "measured_yards": 388.6, "card_yards": 391}},
        "tee_ll": [lon, lat], "aim_ll": [lon, lat], "bearing_deg": 352.1, "length": 391,
        "zones": [{"lie": "water", "poly": [[lon, lat], ...], "src": "osm:way/123", "p": 1.0}],
        "exposure": 0.7,
        "provenance": {"tee": "tees:tee_axis", "green": "osm_green", "par": "card", "zones": {"recovery": "vision:lidar_hag"}},
        "confidence": {"score": 0.77, "band": "check the flags", "osm": 0.42, "imagery": 0.0, "inferred": 0.58, "flags": []}}}}
```

Rules: hole refs are strings; `tee_ll`/`aim_ll`/`bearing_deg`/`length` at the hole level repeat the
package's `tee_set` entry (QA's reader and simple consumers use them); `zones` cover the hole window
(+/-150 yds of the line, 40 yds behind the back tee to 40 past the green), polygons without holes (cut
them, as `geometry._holefree` does); `aim_ll` follows the geometry rule (first hole-line node >= 60 yds past
the tee). The aim point on dog-legs is often off the landing area, so consumers search aims over +/-60 yds
(`aim_min/aim_max`), not +/-40. Confidence follows section 6.

### 9.3 `vision_any.gapfill(package, imagery_dir) -> package`

* Input: a package/1 dict and a directory with NAIP (`naip_rgb.tif`, `naip_nir.tif`) and lidar/DEM
  (`dem.tif`, DSM or HAG raster).
* Output: a new dict (do not mutate the input) with zones appended per hole:
  `{"lie": "recovery"|"native"|"water", "poly": [[lon, lat], ...], "src": "vision:lidar_hag"|"vision:naip", "p": 0.0-1.0}`,
  `stages.vision = "ok: <model id>"`, `sources.vision = {model, trained_on, imagery_date, lidar_date}`,
  `holes[ref].exposure` set, and `confidence` recomputed (or left for `pipeline.confidence`).
* Trees = height-above-ground >= 4 m (lidar) inside the window; long grass = NAIP texture/NDVI where HAG < 1 m
  and not mown. Must work on courses with no hand map (no training on traced labels in the product path).
* For acceptance on Spirit Hollow: a `--holdout` mode, or a model that never saw the traced labels
  (decision 9.1-6, section 7 circularity rule).

### 9.4 Request files (Actions triggers)

`course_data/requests/<kind>_<state>_<slug>.json`, committed and pushed; the workflow's `on.push.paths`
matches its kind and it deletes nothing (the request stays as the record).

```json
{"schema": "request/1", "kind": "package", "course": "Spirit Hollow", "state": "IA", "near": "40.76,-91.14",
 "tees": "Black", "requested": "2026-10-16T19:00Z", "by": "architect"}
```

| kind | Workflow | Writes |
|---|---|---|
| `package` | `course_package.yml` (platform) | `courses/<state>/<slug>/package.json` (+ OSM, scorecard) |
| `imagery` | `imagery_fetch.yml` (imagery/vision_any) | NAIP + 3DEP for the package bbox |
| `plan` | `plan_course.yml` (product) | `courses/<state>/<slug>/output/*.pdf`, wind page |

### 9.5 What pipeline.py does in v2

`pipeline.py` stays the developer orchestrator and the reference implementation of S6 (merge, confidence,
qa.md, course module). When a `package.json` exists for the course it will build `holes.json` from it
(frame per tee set) instead of re-running geometry; until then it runs geometry/tees/imagery directly.
