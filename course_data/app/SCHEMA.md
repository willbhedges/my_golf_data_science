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

`player` also carries each plan club's `width95` (the pattern every precomputed pick assumes: Driver 70) and
`profile_defaults`: the "Your game" panel's starting bag (`clubs: {name: {carry, total, width95, plan}}`, `plan` = the
precomputed club it stands for, `null` = not planned yet) and the v2 prior sds (`course_data/personal/bayes.Prior.v2`).
The page fits a `golf_player/1`-style summary in the browser (closed form: log width and carry = shared part + club
part, shrunk toward the typed bag; launch-monitor CSVs (Garmin R10 etc.) and the generic tee-shot CSV are parsed by a
JS port of `parsers.py`) and keeps it in localStorage only. Each plan club then gets carry/total shifted by
(profile − default) and its drawn pattern scaled by profile width / default width.

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
| `mapping` | `"hand"` (hand-checked map: no confirm step) or `"auto"` (a course package) |
| `confirm` | the golfer-confirm data (below), or `null` |
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

#### `width_rule` (optional, on tee variants): the pick across the golfer's driver pattern

Spirit Hollow only, from `spirit_hollow/v2/output/v2_decisions.json`:
`{base: 70, pick, aim, sweep: [[width, pick], ...55-90], flips: [{width, frm, to}], aims: {club: [[width, aim], ...]}, source}`.
Client (tee at `back` 0): `a = sweep pick at W` (player_profile._pick_at); the calm-day pick is `a` if it differs
from the sweep pick at `base`, else `pick`; its aim is interpolated in `aims[club]` (60 / 70 / 82 yd sens runs).
It replaces `calm` (final_decision.json) on those holes; the wind rule above then applies as before.

#### `approach` (optional, on tee variants): the second shot

Today only Spirit Hollow has it (`spirit_hollow/approach/output/{approach.json, green_views.json}`, see that
folder's REPORT.md). The client shows it as the "Approach" view.

```jsonc
"approach": {
  "image": "gN", "w": 360, "h": 360, "ypp": 0.25,       // green close-up, turned so the shot plays up the image
  "up": 109.6,                                           // degrees true of "up" on that image
  "green": [[x,y],...], "green_size": [21.4, 33.9],      // outline (image px), width x depth (yds)
  "black": true,                                         // computed for the Black-tee plan (false: Gold box, 2B / 9B)
  "tee": {"club": "4-wood", "aim": 0.0},                 // the tee-shot plan it starts from
  "typical": {"median": 116.6, "p10": 101.3, "p90": 131.7, "club": "SW", "lies": {"fairway": 0.66, ...}},
  "shots": [Shot, ...],                                  // par 4: [approach]; par 5: [go, third] or [third]
  "par5": {"p_go": 0.93, "p_layup": 0.04, "p_forced": 0.04, "call": "go"|"layup",
           "go_up_to": {"fairway": 300, "first_cut": 300, "rough": 270},          // go when this close or closer
           "green_box_up_to": {...},                     // aim at the green box inside this; beyond it, the apron
           "go_aims": [["green", 0.72], ["20 short, +0", 0.15]],
           "margin": {"mean": -0.369, "se": 0.005},      // go minus lay-up, strokes, over balls that can go
           "layup": {"L": 60, "off": -10, "club": "PW", "shot": 141, "lies": {...},
                     "full_wedge_cost": 0.17, "full_wedge_L": 100, "target": [x,y] | null}}
}
Shot = {"id": "approach"|"go"|"third", "label": "...", "bearing": 224.1, "dist": 200.4,
        "plays_ratio": [61],                             // plays-like / calm yardage per wind cell (relative to `bearing`)
        "boxes": {"fairway"|"rough": {"-1".."3": {"shape": [[x,y],...], "aim": [x,y], "play", "lo", "hi",
                                                 "aim_text", "club", "haz": {"left": "bunker", ...}}}},
        "sg":    {"recommend": "decade"|"sg", "cost", "play", "best": [x,y], "box": [[x,y],...]},   // approach only
        "apron": {"L": 20, "off": 5, "club", "shot", "target": [x,y], "zone": [[x,y],...]}}        // go only, if in view
```

Client: box = `boxes[lie][windMod(mph)]` (the hole's forecast wind at that time); plays like =
`play x interp(plays_ratio) / (1 + k(T-70))`. When going for it from beyond `green_box_up_to`, the target is the apron.

### `kind: "par3"`

| field | meaning |
|---|---|
| `green` | green outline, image px |
| `sets[set]` | `{center, front, back, plays[61], boxes}`. `plays` = "plays like" yds per wind cell, including elevation. `boxes["-1".."3"]` = the DECADE target box for each wind modifier (`<5`, `5-10`, `10-20`, `20-30`, `30+` mph): `{poly (image px), play, lo, hi}` |
| `elev` | `{green_drop, dz, approx?}` or `null` |
| `short` | one-line hazard summary |

Auto-course holes also carry `geo: {tee_ll, green_ll, line}` (WGS84, from the package): where the plan's hole *n*
was computed. The confirm step compares the routed hole *n* with it (routing.score's rule: green within 20 yds, tee
within 40 yds of the line's first 60 %) and says so on the hole screen when they disagree.

## Hole map confirm (`course.confirm`): "I'm playing course X from tees Y" on a course nobody mapped by hand

```jsonc
"confirm": {
  "pool": Pool,                    // golf_confirm_pool/1 (course_data/app/confirm_pool.py), below
  "overview": {"img": "data:image/jpeg;base64,...", "w": 900, "h": 551, "ll0": [lon, lat],
               "ax": [a, b, c], "ay": [d, e, f],   // px = a (lon - lon0) + b (lat - lat0) + c, py likewise (affine fit to UTM)
               "m_per_px": 1.5, "fit_err_px": 0.01, "source": "USDA NAIP ...", "year": 2023},
  "card_known": true,              // false: no card online -> the page asks for a typed one first
  "card_note": "...",
  "typed_pools": [Pool, ...]       // pools re-solved with a card the page knows (the package request's card)
}
```

The routing never uses the package's OSM golf=hole ways: holes are placed by routing v2
(`course_data/platform/routing_v2.py`) from the OSM greens / tee boxes, the NAIP segment model and lidar tee
pads, with the course's card (or none). The ways are the hidden truth the tests answer from
(`fixtures/confirm_truth/<slug>.json`, never in the page).

**Pool** (`golf_confirm_pool/1`):

| field | meaning |
|---|---|
| `n`, `card`, `card_kind`, `holes[]` | holes on the card; `holes[h] = {par, yards[]}` the card the pool was routed with (empty without one) |
| `params` | `tau`, `p_check`, `p_stop` (routing_v2_weights.json), `doubt` 0.02, `snap_green` 15 / `snap_tee` 25 yds, `reject_r` 45 yds, `w_length`, `w_fingerprint`, `fp_cap`, `par_ranges` (typed-card re-score) |
| `greens[]`, `tees[]` | candidates `{ll, src}`; a tee's `cx` is its 40-yd tee complex (routing_v2._hole_key) |
| `pairs[h][i]` | hole h's (tee, green) answers used by some routing: `[t, g, back tee, straight yds, [lengths of the boxes on its line]]` |
| `routings[r]`, `costs[r]` | a whole round (`pairs` index per hole) and its exact routing_v2 cost |

How the pool is built (once per course, minutes, `confirm_pool.py`): the base solve (`keep_top 300`, leave-one-out
margins: exactly confirm.Session's starting posterior) plus, for every hole, its 10 most likely greens (best
hypothesis row per green, plus every answer of the base posterior) pinned one at a time (`solve(fixed=...)`, beam
500, top 40). Costs from different solves are comparable (path costs / local search's exact cost), so one
Boltzmann posterior covers the union (~4-6 k routings, 0.2-0.5 MB).

**Client algorithm** (`confirm_engine.js`, a port of `platform/confirm.py`):

1. Answers are constraints: "yes" pins hole n's key (green + tee complex); "no" drops that green with any box within
   45 yds of the shown tee (`routing_v2.reject`); a locate snaps the taps to a detected tee box / green within 25 / 15
   yds and pins that key (a spot with nothing detected is kept as the golfer's own point).
2. Re-solve after every answer: the routing is the cheapest pooled routing that meets every constraint; per hole the
   posterior is the Boltzmann share (`tau`) of each key over those routings; `p_hole` = the shown key's share. When no
   pooled routing meets them all, the routings with the fewest broken constraints stand in (a pin whose green the
   routing has under another tee complex counts half) and pinned holes are drawn where the golfer put them.
3. Next question: the most expected bits per tap (confirm: H(p) floored at a 2 % doubt, 1 tap; locate: entropy of
   the hole's answers, 2 taps, at least 1 bit after a "no"). Stop when every unconfirmed hole has `p_hole >= p_stop`.
   "This isn't hole n" stays on every hole screen (the stop rule leaves ~1.4 wrong holes per course on the test split):
   it is a confirm answered "no", then a locate of hole n.
4. Typed card (no card online): `typed_card.js` (port of `platform/typed_card.py`: same errors and warnings). A card
   that matches a `typed_pools` entry (pars equal, every yardage within 3 yds) switches to that pool, i.e. the
   routing re-solved with it (what a backend would return). Any other card re-scores the current pool's length and
   fingerprint terms (`routing.length_cost` / `fingerprint` per pair): approximate, and weak when the pool was routed
   without a card, since such a pool rarely holds a routing that fits a card on all 18 holes.
5. The answers (and the typed card) are kept in localStorage and replayed onto the pool on reload.

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
