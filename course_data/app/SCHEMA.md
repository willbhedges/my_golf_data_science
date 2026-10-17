# `golf_app/1`: the app's course data

One JSON format feeds the app: a golfer picks course X and tees Y, and every hole shows where to aim and which club,
re-solved on the phone for the wind and temperature when they reach the hole. Today
`course_data/app/build_app.py` writes it into the page (`const D = ...` in `out/index.html`). A backend
would serve the same documents per request: one **course document** per course (`build_app.py --json DIR`
writes them), plus a small **catalogue**.

Everything heavy (strategy simulation, wind grid, shot patterns, imagery) is precomputed. The client only:
interpolates the wind grid, applies elevation and temperature, and draws the result on the image.

## Bundle (what the page embeds)

```jsonc
{
  "schema": "golf_app/1",
  "built": "2026-10-17T04:15Z",
  "wind_axes": {"speeds": [0,5,10,15,20,25], "dirs": [0,30,...,330],
                "cells": ["0_0","5_0","5_30",...,"25_330"]},   // 61 cells; every per-cell array follows this order
  "player": {"clubs": {"Driver": {"carry":275,"total":300}, ...},
             "temp_carry_pct_per_f": 0.10, "temp_ref_f": 70},   // carry changes 0.1 % per deg F from 70 F
  "catalog": {"n_courses": 709, "n_with_holes": 366, "states": [{"state":"IA","n_courses":397,...}],
              "upcoming": [["Coldwater Golf Links","Ames","IA",18], ...]},  // searchable, not built yet
  "courses": [Course, ...]
}
```

A wind cell `"<mph>_<deg>"` is the wind speed and the direction it blows **from**, relative to the tee
line (0 = straight into the golfer, 90 = from the right, i.e. blowing right-to-left).

## Course

| field | meaning |
|---|---|
| `id`, `name`, `short`, `town`, `state`, `lat`, `lon` | identity |
| `confidence` | `{level: "verified"\|"auto", summary, red, amber, check_holes, map_score?}`. **verified** = a hand-checked map; **auto** = auto-mapped (OSM + NAIP + lidar). |
| `default_tee` | the tee set with the primary plan |
| `tee_sets[]` | `{name, colour, yards[18], total, rating, slope, computed, note}`. `computed`: `exact` (planned from that tee), `offset` (the main map, tee moved along the line, re-solved on a 20-yd grid), `missing` (not planned: the app greys it out) |
| `forecast` | `{fetched, source, lat, lon, days:[{key,label}], hourly:[{date,hour,mph,gust,dir,temp,pop}]}` (`dir` = degrees true the wind blows from), or `null` |
| `pace_min_per_hole` | minutes per hole: hole *n* is reached at tee time + (n-1) x pace |
| `checks[]` | pre-round check cards (below) |
| `images` | `{id: "data:image/jpeg;base64,..."}`: each hole image once (a backend would send URLs) |
| `holes[]` | Hole, in playing order |
| `imagery`, `attribution[]`, `model` | text for the footer |

## Hole

```jsonc
{"no": 7, "ref": "7", "par": 5, "hcp": 3,
 "confidence": {"level": "verified"|"auto"|"check", "lines": ["why"], "items": ["7-tee", ...], "map_score": 0.85},
 "tees":     {"Blue": {"variant": "Blue", "yards": 590, "back": 0}, ...},   // tee set -> where it is played from
 "variants": {"Blue": Variant, ...}}
```

`tees[set].variant` picks the variant; `back` is how many yards the set's tee sits **behind** the
variant's tee along its line (negative = in front). The golfer's own "move this tee" adds to `back`, and the
client snaps to the nearest computed offset. A course with one plan per tee set has one variant per set
(Veenker). A course with one map and offset grids has a single variant with `back` per set (Spirit Hollow).
Spirit Hollow's holes 2 and 9 have two variants, one per screenshot (Gold box `B`, Black box `F`).

## Variant: common fields

| field | meaning |
|---|---|
| `kind` | `"tee"` (par 4/5 tee shot) or `"par3"` |
| `image`, `w`, `h` | image id in `course.images` and its pixel size |
| `axes` | `{o, f, r}`: yard frame -> image px. A point `along` yds up this variant's tee line and `lat` yds right of it is drawn at `o + along*f + lat*r`. Several variants can share one image with different axes. |
| `bearing` | degrees true of this variant's tee line (rotates the wind into the grid's relative direction) |
| `up` | degrees true of "up" on the image (draws the wind arrow) |
| `length`, `tee_label`, `note`, `aim_at` | text |

### `kind: "tee"`

| field | meaning |
|---|---|
| `clubs[]` | clubs solved on this hole |
| `flight[club][cell]` | `[carry, total, width95, drift]` yds in that wind (no elevation and no temperature) |
| `offsets[back][club]` | `[aim[61], ev[61], zone_lo[61], zone_hi[61]]`: best aim (yds right of the line), expected strokes to hole out from the tee, and the aim range within 0.02 strokes of the best, per cell, for a tee `back` yds behind the variant's tee |
| `calm` | `{pick, aim, tie, margin, zone, flips[], source}`: the plan's calm-day decision (full Bayesian or quick). The client keeps it unless the wind changes the quick model's own pick, shifting its aim by the wind's aim change. |
| `cloud[club]` | `{dA, dL, A, B, u, w, width}`: simulated finishing pattern at the calm aim (centre offset from the drawn total/aim, 95 % half-axes, axis vectors in (along, lat)). The client scales it by width-in-wind / `width`. |
| `elev` | `{clubs: {club: {dc, rf, kick, drop}}}`: lidar carry change, roll factor, side kick (yds, + = right), landing drop (ft, + = below the tee), or `null` |
| `check[]` | the product's CHECK reasons (the best aim was rejected by the safety guard) |
| `mapped_along` | (verified) how far the hand-checked map reaches; landing past it shows a warning |
| `off_image_below` | image y (px) below which the tee falls off a screenshot |

### `kind: "par3"`

| field | meaning |
|---|---|
| `green` | green outline, image px |
| `sets[set]` | `{center, front, back, plays[61], boxes}`. `plays` = "plays like" yds per wind cell, including elevation. `boxes["-1".."3"]` = the DECADE target box for each wind modifier (`<5`, `5-10`, `10-20`, `20-30`, `30+` mph): `{poly (image px), play, lo, hi}` |
| `elev` | `{green_drop, dz, approx?}` or `null` |
| `short` | one-line hazard summary |

## Check card (`course.checks[]`)

From the product's 2-minute pre-round check (`out/review/review.json`, red and amber items):

```jsonc
{"id": "3-cut", "hole": 3, "severity": "red"|"amber", "type": "cut"|"tee"|"hazard"|"fairway"|"check"|"gap",
 "question": "...", "detail": "...", "p_wrong": 0.5, "worst_regret": 0.27, "tee_set": "Blue",
 "options": [{"answer": "present", "label": "Yes, a first cut", "text": "Hole 3: Driver -> 4-wood, aim 20 yds right.",
              "outcome": {"pick": "4-wood", "aim": 20.0, "club_changed": true, "d_ev": -0.025} | null}],
 "crop": {"img": "data:...", "w": 300, "h": 480, "overlay": {"polys": [...], "line": [...], "tee": [x,y], "target": [x,y], "ellipse": [rx,ry]}}}  // red only
```

When the golfer picks an answer whose `outcome` is set, and they play the check's `tee_set` from the card
spot, that hole's plan becomes the outcome (its aim shifted by the wind). "Moved" answers need a re-plan
on the backend (`course_data/product/apply_answers.py`).

## Client algorithm (what a native app would reimplement)

1. Wind for hole *n*: interpolate the hourly forecast as a vector at tee time + (n-1) x pace, or use the custom wind.
2. `rel = (wind_from - variant.bearing) mod 360`. Bilinear weights over (speed, rel) on the 4 nearest cells.
3. Tee shot: interpolate `flight` and `offsets[back]` per club. Add elevation (`carry += dc`,
   `total = carry + roll*rf`, aim finishes `kick` yds over) and temperature (`carry, total += carry*k*(T-70)`).
   Best club = lowest `ev`, with the calm-pick rule and check answers above. Draw the aim at
   (`total - back`, `aim`) and the pattern at the cloud offset plus drift and kick.
4. Par 3: `plays = interp(plays) / (1 + k*(T-70))`; box = `boxes[windMod(mph)]`; play-it-like = `box.play * plays / center`.

## Producing it for a new course

`plan.py` (course_data/product) already writes everything a course document needs into
`packages/<slug>/out*/`. `build_app.build_package()` is the adapter: a backend runs the plan per (course,
tee set) on request, then the adapter, and caches the document.
