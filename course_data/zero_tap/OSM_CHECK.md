# How good is OSM as truth? (workstream D)

Three checks, in order of how much they catch. Code: `truth.py` (completeness), `osm_check.py` (sheets, card check,
verdicts). Sheets: `osm_check/sheets/<slug>_overview.jpg` (NAIP 2022-23, every OSM hole line numbered at its tee
`T` and green `G`, OSM greens yellow, tees cyan) and `<slug>_holes.jpg` (one tile per hole).

## 1. Course-level: is the hole set complete? (all 213 candidate courses, automatic)

| outcome | courses | share |
|---|---|---|
| refs exactly 1..N (or 9x3/4, 18x2, 18+9), lines 50-750 yds, >= 90 % of lines end on an OSM green -> **in the benchmark** | 161 | 76 % |
| refs duplicated (two ways for one hole: alternate tees, a neighbouring course, a 27/36-hole facility tagged inconsistently) | 21 | 10 % |
| refs missing (usually exactly one hole of 18 unmapped) | 18 | 8 % |
| refs both duplicated and missing | 8 | 4 % |
| greens not mapped (< 90 % of lines end on an OSM green) | 4 | 2 % |
| no hole ways | 1 | 0.5 % |

These are dropped, not repaired: a course counts only when its truth is complete.

## 2. Hole-level: hand check against NAIP (30 seeded courses, `osm_check.py pick`, seed 20261020)

30 courses drawn at random from the 161 benchmark courses (both splits; 27 x 18 holes, 2 x 9, 1 x 36), 540 holes.
For each hole I checked by eye on the overview sheet: the line runs from a tee area to a green of one hole, ends on
the mapped green, and the number fits the round (green *n* close to tee *n+1*, 1 and 10 / 18 near the clubhouse).

| verdict | holes | share |
|---|---|---|
| ok | 537 | 99.4 % |
| wrong green / wrong tee / wrong number | **0** | **0 %** (95 % upper bound 0.55 %) |
| unclear (westchester_ca 15-17: that part of the course looks unmaintained in the 2022 imagery) | 3 | 0.6 % |

No course in the sample had a pairing or numbering error. **Per-hole OSM error rate on complete courses: 0 / 537
judged holes.** What the sheet scale cannot show is *where on the tee complex* the line starts; the card check covers
that.

## 3. Hole-level: OSM vs the published scorecard (49 benchmark courses with a fitting web card, 864 holes)

| check | holes flagged | share |
|---|---|---|
| line length vs the card's longest tee: off by > 15 % and > 30 yds | 46 | 5.3 % |
| OSM `par` tag vs card par | 14 | 1.6 % |

Almost every length flag is a line that starts at a forward / member tee (40-120 yds short of the back tee); the
hole is right. Two courses look like card mismatches rather than OSM errors (upland_hills_ca, derryfield_nh: several
holes 150-300 yds off). Details: `osm_check/card_check.json`.

## What was fixed in the truth

* **Par**: when the course's web card fits (same hole count), the card's par is the truth (`par_src: "card"`, the
  OSM value kept as `par_osm`). The 14 OSM par disagreements no longer count against methods that use the card.
* **Tee position**: the scorer accepts a tee up to 30 yds off the first 60 % of the true line extended 90 yds behind
  its start, so a line that starts at a forward tee still credits the back tee.
* Hand-check verdicts are stored per hole in `truth/<slug>.json` (`hand_check`); a course judged bad would be dropped
  (none so far).
