# fastsolve: the tee-strategy solver's hot loops in C

Status: work in progress (checkpoint 1: profile + first bit-identical holes). Built ALONGSIDE the engine: nothing
outside this folder is edited, nothing is wired in.

## 1. Profile of the existing engine (this 4-CPU box, one process, 2026-11-13)

Engine = `spirit_hollow/v2/model.py` + `decide.py` + `wind_grid_v2.py` through `course_data/courses/v2_course.py`
(`activate`, `refined_solver`), Gateway National `truth` (Back), hole 8, 7 clubs.

The brief said the slow part is a polygon test per simulated ball. It is not: the engine already paints each hole's
lies into a 0.5-yd raster (`model.Raster`, 881 x 601 cells) and looks balls up. What is slow is what it does with
the raster, in numpy, per (swing, aim) sample:

| piece | time | share |
|---|---|---|
| **one refined wind cell** (`refined_solver`: 7 clubs x (381 aims x 2,500 swings + 41 aims x 16,000 swings) = 11.3 M balls) | **3.06 s** | |
| `model.finish` (roll every ball out in 2-yd steps, a raster lookup per step) | 2.84 s | 93 % |
| - of which `Raster.lie_at` / `idx` (rint, astype, clip, fancy index on (swings x aims) arrays) | 1.18 s | 39 % |
| - `a + ua * st`, `np.where`, masks: full-array temporaries per roll step | 1.4 s | 46 % |
| `robust_aim` (smoothing, spline, Brent), 14 calls | 0.02 s | 0.6 % |
| **decide.bayes, per prior draw** (7 clubs x 321 aims x 3,000 swings = 6.7 M balls) | **3.35 s** | |
| `model.ev_curve` -> `finish` | 2.19 s | 65 % |
| `model.Raster(hd, map_seed)`: the map re-painted for the draw's jitter | 1.03 s | 31 % |
| - of which `matplotlib.Path.contains_points` (530 k cells x ~40 zone polygons) | 0.82 s | 25 % |
| - `_water_entry`, `_blocked`, distance transform | 0.17 s | 5 % |
| `Raster.strokes` (value raster of the draw) | 0.10 s | 3 % |

Line level, `model.finish` (one refined cell, ms): `new = R.lie_at(a, l)` 1065 (35 %), `a, l = a + ua * st, l + ul * st`
476 (15 %), `np.where(HAZ[new], 0, left)` 298 (10 %), `np.where(into_rough, ...)` 204, first `lie_at` 179,
`np.hypot` 128, `left - st` 144, `np.minimum(left, 2) * mv` 140.

Eagle Knoll (`engine.flight_trees.mode = lidar`: every ball's descent is traced through the lidar crowns in 3-yd
steps): one refined wind cell of hole 14 takes **28.6 s**; 26 s of it is `v2_course.lidar_flight_ev_curve`'s trace
(`clear = ... + drop(pa, pl)` 8.2 s, the crown test 5.0 s, the candidate filter 3.3 s), `finish` 2.8 s.

So the polygon test is 25 % of the calm-day book (it runs once per prior draw, not per ball) and 0 % of the wind
grids; the rest is numpy making and scanning large temporaries around a per-ball loop that wants to be a loop.

## 2. First result

`kernel.c` (gcc -O3 -march=native -ffp-contract=off -fopenmp, ctypes) reproduces the per-ball loop operation for
operation in double precision, so the EV curves are **bit-identical** to the engine's (not "within 0.003"):

| | engine | fastsolve (4 threads) | |
|---|---|---|---|
| EV curve, one club, 381 aims x 2,500 swings, Gateway 8 | 0.11-0.64 s | 0.005-0.013 s | x20-49 |
| same, Eagle Knoll 14 / 9 (lidar crowns) | 1.0-3.1 s | 0.04-0.11 s | x21-30 |
| lie raster of a prior draw | 0.72-1.14 s | 0.02-0.09 s | x12-38 |

Every finish position, lie and stroke value of every ball, and every raster attribute (lie, entry_dist, blocked,
native_depth) compared equal (`==`) on Gateway 8 and Eagle Knoll 9 / 14, calm and 10 mph.

More to come: full equivalence table, benchmarks, the runner.
