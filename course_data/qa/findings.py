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

Common to every tee hole: **no `recovery` or `native` polygon anywhere** (no vision gap-fill merged), so every miss
into woods or prairie plays as rough - the R6 failure (unmapped hazard = rough), and why the auto club pick drifts
to Driver (see the golden table).

## 4. Bug reports by area

### data platform (`course_data/platform/`)
* **P1 (contract mismatch, blocker):** `platform/package.py` documents `course_package/1` with zones as
  `[[lie, [[x, y], ...]]]` in the **yard frame**, written to `course_data/packages/<slug>/`. ARCHITECTURE 9.2 says
  `package/1`, zones `{lie, poly: [[lon, lat], ...], src, p}` in **WGS84**, at `courses/<state>/<slug>/`. QA's reader
  accepts both, but vision_any (`gapfill`) and product must agree on one. Fix: emit package/1 as specified.
* **P2:** no platform-built package on disk yet; only `product/standin/spirit_hollow/package.json` (product's
  stand-in made from pipeline.py). Second/third-course end-to-end is blocked on this.

### hazard vision (`course_data/vision_any/`)
* **V1 (blocker for the club pick):** no gap-fill merged into any package: landing-zone IoU for trees and long grass
  is 0.00 on every Spirit Hollow hole. Concrete misses in section 3 (holes 1, 6, 9, 11, 13, 18).
* **V2:** creek corridors are 3-yd centre-line buffers (mean water IoU 0.37); on 10, 11, 14, 16, 18 the channel +
  banks are 10-20 yds wide in NAIP.

### product (`course_data/product/`)
* **R1:** the stand-in package lacks `exposure`, `yards{set}`, `course.state/boundary` and per-set `bearing_deg`,
  so the wind page can't be fed from it per 9.2 (`test_package_header`, `test_package_hole_fields`, `test_every_tee_set`).
* **R2:** aim search clipped at +/-60 yds; holes 11 and 18 sit on the bound because the tee line (first hole-line
  node) points away from the landing area. Take the aim line at the ~250-yd point on the line of play (architect's
  suggested geometry fix) or centre the search on the fairway.

### architect (`ARCHITECTURE.md`, `pipeline.py`, `acceptance.py`)
* **A1:** `tee_strategy.expected_strokes` raises `KeyError` for `green` and `ob_boundary`, which 9.1-4 allows in
  packages ("treated as fairway by the model"). Either the model maps them or the contract says every consumer maps
  `green -> fairway`, `ob_boundary -> ob` (QA's reader does).
* **A2:** two package schemas/locations in flight (P1); the contract needs one decision.
'''
