# fastsolve: the tee-strategy solver in C

Built ALONGSIDE the engine: nothing outside this folder is edited, nothing is wired in. Two things live here:

1. **The exact kernel** (`kernel.c` + `fast.py`): the engine's per-ball loops in C. Same numbers as the engine,
   bit for bit on this box, and equal to the Actions rev 7 solve of Gateway to the last float bit or two.
2. **The adaptive Sobol solver** (`adaptive.py`, `run.py --adaptive 1 --swings sobol`): fewer, better-placed
   swings and a stopping rule. Different numbers from the engine by design (less Monte Carlo noise).

| Full Gateway solve (Back book + 10 offset grids, Middle book + card grid), 4 CPUs | wall time |
|---|---|
| Actions (engine, ~20 runners) | ~1 h 45 min |
| exact kernel, `run.py` | 873 s (Back 600 s, Middle 273 s) |
| adaptive Sobol, `run.py --adaptive 1 --swings sobol ...` | **183 s** (Back 113 s, Middle 70 s) |

| same, lower precision (64 prior draws, caps 2,048 / 512), Back and Middle run side by side | **83 s** |

The 1-minute target was not reached. Outputs in the engine's file format: the 183 s run in
`solved/gateway_national/{truth,truth_middle}/v2/`, the 83 s run in `solved_83s/gateway_national/...`.

What the 83 s run gave up (against Actions rev 7): book still the same club on all 26 holes, aims within 1.0 yd,
margins within 0.005 (0.002 in the 183 s run); Back wind cells flagged tie 4,674 (2,460); Middle card-grid aims
more than 1 yd off in 11 % of cells (4 %). No clear club disagreement in either. Its settings:
`--draws 64 --central 1024 --adaptive-cap 2048 --adaptive-cap-other 512 --adaptive-n0-other 256`.
CPU split of the 83 s run: books 142 s, card grids 47 s, offset grids 100 s (290 CPU-s; 73 s is the 4-core floor).

Prior-draw saturation (Sobol 512 swings per draw; holes 8, 9, 10, 11, 16; 32 / 64 / 128 / 256 draws): the pick
never changes from 32 draws up; the aim is within 0.5 yd from 64; the margin at 128 is within 0.0005 of the
256-draw margin on every hole, at 64 within 0.003 (inside its own SE of 0.003-0.016). 128 is the point where
nothing moves; 64 is inside the noise.

## Defaults (runner, from the saturation results)

`run.py solve` now defaults to: Sobol swings, 64 prior draws, 512 swings per draw, 2,048 for central worlds, adaptive
wind grids capped at 8,192 swings at the card tee (the 99 % aim saturation N) and 2,048 at the other offsets.
`--exact` restores the engine's numbers (identical to Actions). Full Gateway (Back + Middle, run concurrently with
`FASTSOLVE_SLOTS=<dir>:4`): 124 s; outputs in `solved_default/`. Against the 256-draw 183 s run: same club on all 26
holes, calm aims within 1.0 yd, wind-cell club differences 116 + 4, all in tie cells.

## Speed steps after the 124 s solve (`book.py`; each tested on Back 8, 10, 16 only)

Before these, one hole of the book cost 6.7 CPU-s: the prior-draw loop 4.1 s (per draw 27 ms map repaint, 17 ms
value raster, 13 ms ball work), ladder + sensitivities + width sweep 1.9 s, start-up and shares 0.7 s.

- **(2) 1-yd raster for the prior-draw maps and value rasters** (`--book-res 1.0`, now the default; 0 = 0.5 yd): kept.
  Prior-draw loop 4.1 -> 1.8 s a hole, book 6.7 -> 3.9 s a hole. Picks identical, pick aims identical (other clubs'
  aims within 0.5 yd), margins within 0.0007 on 8 / 10 / 16.

- **(3) crossed design** (`--book-maps 16`, now the default; 0 = a map per draw): 16 jittered maps painted once per
  hole, draw s uses map s mod 16: kept. Prior-draw loop 1.7 -> 1.3 s a hole, book 3.9 -> 3.6 s a hole. Against the
  per-draw repaint over 6 prior seeds on 8 / 10 / 16: same pick and runner in 18 of 18 (one runner swap between two
  clubs 0.001 apart), margin difference mean +0.0003 / +0.0002 / +0.0015, sd 0.0015-0.0021 (margin SE is 0.004-0.016,
  unchanged), pick aim within 0.5 yd in 16 of 18 and 1.5 yd apart twice on hole 8, whose aim moves by the same
  1.5 yds from prior seed to prior seed with a map per draw.

- **(4) racing in the book** (`--book-race 1`, now the default): from 16 draws on, every 8 draws, a club behind the
  leader by more than the tie threshold (0.01) + 3 paired SE is not simulated further; the leader, the runner-up and
  any club within 3 SE of the runner-up always run every draw: kept. Prior-draw loop 1.3 -> 0.9 s a hole (4 or 5 of
  the 7 clubs stop at 16 draws), book 3.6 -> 3.3 s a hole. Over 6 prior seeds on 8 / 10 / 16: pick, runner, pick aim,
  margin, margin SE and cross-fit margin identical to no racing in 18 of 18. A stopped club carries `draws: 16`; its
  EV is the pick's EV + its paired margin over those draws, its own aim is from 16 draws (up to 2.5 yds off).

- **(5) compiler.** PGO (`-fprofile-generate` on the book + two wind grids of hole 8, then `-fprofile-use`): dropped.
  Hole 10 book 3.2 -> 3.7 s, card grid 3.4 -> 3.7-3.9 s, offset grid 1.3 -> 1.3-1.4 s (two rounds, box shared).
  `-flto`: dropped, one source file, nothing to link across (4.3 -> 4.3 s on hole 8's card grid).
  `FASTSOLVE_SO=<file>` loads a prebuilt library for such experiments.
- **float32 lanes** (`--f32 1` or `FASTSOLVE_F32=1`; adaptive wind grids only; 16 aims per register, positions and
  value raster in single precision, sums in double): built, NOT the default. Card + one offset grid of 8 / 10 / 16:
  16.8 -> 10.9 task-s in the one quiet pair of runs (-35 %; -20 to -30 % in two pairs with the box shared). All
  1,098 cells keep their club, swing count and tie flag; the pick's aim moves by 0.5 yd in 2 cells (4 of 7,686 club
  aims), EVs by at most 0.0002. Off because the bar for it was "aims unchanged", not "within 1 yd".

### Full Gateway solve with (2) + (3) + (4) (float32 off), outputs in `solved_book16/`

One run, Back + Middle side by side: **140 s wall, on a box another job was using** (load 3.7 at the start, 5.8 at
the end), so the wall time is not comparable with the 124 s. The wind code is the same as in the 124 s run and its
task time went from 307 to 401 s, which is the other job. Books: 162 -> 129 task-s under that load; 6.2 -> 3.3 s a
hole (86 s for 26 holes) when measured alone on 8 / 10 / 16. Estimate on a quiet box: 86 + 307 = 393 CPU-s against
469, about 104 s. Not run again. The minute is not reached: the wind grids are 307 of the 393 CPU-s and none of
(2)-(4) touch them; `--f32 1` would take about 30 % off that part (about 80 s in all, not run in full).

Against `solved_default/` (hole 10's map changed between the two runs: ab3797b50, the ditch beside the green):
- Book, 26 holes: same club on all 26. Aims within 1.0 yd on the 24 holes whose map did not change (Middle 8 is
  1.0 off, 12 holes are 0.5 off, 11 identical); margins within 0.004. Hole 10 moved 2.5 yds (Back -17.5 -> -20.0,
  Middle -16.0 -> -18.5): that is the map. On the new map with the old settings Back is the same 2-wood at -20.0
  (margin 0.0453 against 0.0450), Middle the same 4-wood at -19.0 against -18.5.
- Wind grids, 24,156 cells outside hole 10: identical, every number. Hole 10 (2,013 cells, new map): club differs
  in 43, of which 39 in ties and 4 outside (2 Back card tee, 2 Middle); not attributable to these steps.

## Flight-tree courses (lidar crowns: Eagle Knoll)

A course whose config has `engine.flight_trees.mode = "lidar"` traces every ball's descent through the measured
crowns (`v2_course.lidar_flight_ev_curve`): steps of 3 yds from 30 % of the carry, clearance against each 1-yd cell's
crown top and base (with the ground's drop below the tee), path length inside crowns summed in float32, and the ball
drops where that length passes its swing's exponential draw (`default_rng(n * 7919 + 17).random(n)`, one uniform per
swing shared by every aim and club, n = the swings of the call). It finishes at that spot on whatever lie is there.

What ran where before, and now:

| path | before | now |
|---|---|---|
| `--exact` (book and wind grids) | C (`fs_ev` has had the crown trace since the first version) | unchanged |
| default book (Sobol, `book.py`) | C | unchanged (outputs byte-identical) |
| default wind grids (`--adaptive 1`) | NOT adaptive: `adaptive.install` saw mode `lidar` and returned the exact kernel's plain solve on 2,500 Sobol swings (no refine, no stopping rule, no tie flags) | adaptive: `fs_grid` has the crown trace |
| legacy constant-height check (`V2_FLIGHT_MODE=legacy`; no course's config uses it) | the engine's Python | still the engine's Python (not ported) |

So no Eagle Knoll path ran on the Python engine; the gap was the adaptive grid. `fs_grid` now gets the hole's crown
and ground-drop grids and each swing's exponential draw (the engine's generator and seed for the swing count of the
Sobol set), and per (cell, club) the flight steps from that club's median carry over the set's swings in that wind,
all built by the code the exact path uses (`fast.Fast._lidar_base` / `_lidar_flight`). The per-ball code is the same
`group()` / `crown_stop()` as `fs_ev`. `--f32 1` is ignored on these courses (the float32 lanes have no crown trace).

Verified (Nov 13, this box, 4 CPUs; holes chosen by the share of 4,000 calm drives stopped in crowns at aim 0:
hole 1 30 %, 14 29 %, 15 22 %, 10 12 %):

| compared | result |
|---|---|
| engine (`--engine slow --exact`) vs exact kernel (`--exact`), holes 1, 10, 14, 15: book `bayes` on 3 prior draws x 3,000 swings (1,032 numbers a hole, curves included) and 5 refined wind cells (50 F; calm, 10 mph x 4 directions; 2,500 + 16,000 swings; 355 numbers a hole) | files byte-identical, max difference 0 on every hole |
| `fs_grid` vs the engine's Python `ev_curve` on the same Sobol swings (n0 = cap = 512, every club's EV at its reported aim, 4 cells x 7 clubs, holes 1, 14, 15; 8 % of those balls stopped in crowns) | max difference 1.8e-15 (summation order); this is `test_eagle_knoll_flight_trees_adaptive_grid_equals_engine_on_its_swings` |
| the same with the scalar branch (`FASTSOLVE_SIMD=0`), holes 9, 14 against the exact kernel | max 1e-14 |
| default solve (adaptive, cap 8,192, 64 draws) vs exact kernel (64 draws; 2,500 + 16,000 swings), holes 1, 10, 14, 15, 3 temperatures, 732 cells | book: same club on 4 of 4, aims equal on 3 and 0.5 yd apart on 14, margins within 0.005. Wind: club differs in 12 cells (0 / 2 / 8 / 2), every one flagged tie or with an exact gap <= 0.02; 88 cells flagged tie; aim of the pick within 1 yd in all same-pick cells of 10, 14, 15 and in 96 % of hole 1 (max 3 yds); EV of the pick: median difference 0.001-0.002, max 0.033 (hole 1, a cell stopped at 512 swings) |
| Gateway `--holes 10 / 11 / 16 --card-only` with the request file, before vs after | `v2_decisions.json` and `wind_grid.json` byte-identical |

Timings (Eagle Knoll, per hole unless said; task seconds on one core):

| | engine (Python) | exact kernel | default before | default now |
|---|---|---|---|---|
| 5 refined wind cells | 118-127 s | 3.5-3.8 s | | |
| book `bayes`, 3 draws | 42-47 s | 1.7-1.8 s | | |
| card-tee grid, 3 temperatures, 183 cells | ~75 min (24 s a cell, not run) | 127-129 s | 37.7 s (hole 14, 2,500 swings, no refine) | 8-12 s (10.6 s hole 14) |
| book, 64 draws, all parts | not run | 62-65 s | 10-12 s | 10-12 s |
| whole course `--card-only` (14 tee shots), wall on 4 CPUs | | not run | 188 s (682 task-s: grids 537) | **96 s** (349 task-s: books 149, grids 201) |

A crown-traced ball costs about 75 ns (41 M balls in 3.1 s for one temperature of hole 14) against 5-20 ns without.

## 1. Profile of the existing engine (one process, this box)

Engine = `spirit_hollow/v2/model.py` + `decide.py` + `wind_grid_v2.py` through `v2_course.py`. Gateway Back hole 8.

The brief said the slow part is a polygon test per simulated ball. It is not: the engine already paints the lies
into a 0.5-yd raster (`model.Raster`, 881 x 601 cells). What is slow is numpy around a per-ball loop:

| piece | time | share |
|---|---|---|
| **one refined wind cell** (7 clubs x (381 aims x 2,500 + 41 aims x 16,000 swings) = 11.3 M balls) | **3.06 s** | |
| `model.finish` (roll every ball out in 2-yd steps, a raster lookup per step) | 2.84 s | 93 % |
| of which `Raster.lie_at` / `idx` | 1.18 s | 39 % |
| of which full-array temporaries per roll step (`a + ua * st`, `np.where`, masks) | 1.4 s | 46 % |
| **decide.bayes, per prior draw** (6.7 M balls) | **3.35 s** | |
| `ev_curve` -> `finish` | 2.19 s | 65 % |
| `model.Raster(hd, map_seed)`: the map repainted for the draw's jitter | 1.03 s | 31 % |
| of which `matplotlib.Path.contains_points` (530 k cells x ~40 zones) | 0.82 s | 25 % |
| `Raster.strokes` | 0.10 s | 3 % |

Eagle Knoll (lidar flight-through-crowns): one refined cell of hole 14 takes 28.6 s, 26 s of it in
`v2_course.lidar_flight_ev_curve`.

## 2. The exact kernel

`kernel.c` (gcc -O3 -march=native -ffp-contract=off -fopenmp, loaded with ctypes; compiled on first use into
`_build/`). `fast.install(M, D)` points THIS PROCESS's `model.ev_curve` and `model.Raster` at it; every engine entry
point then runs unchanged on top, so the output formats are the engine's by construction.

- `fs_ev`: landing -> roll-out -> strokes lookup, summed per aim in swing order. AVX-512: 8 aims per register, 32
  aims of one swing per group. Includes the lidar crown trace (Eagle Knoll). Scalar path for other CPUs and for the
  per-ball outputs.
- `fs_fill` / `fs_fill_rect` / `fs_fill_band`: zone polygons into the lie raster with matplotlib's point-in-path
  arithmetic; per prior draw only the band along each shifted outline is re-tested.
- `fs_water_entry`, `fs_blocked`, `fs_strokes` (value raster incl. green putting; numpy's `interp` formula).
- `decide.bayes` runs unchanged: the three means it takes come from kernel sums through a lazy proxy.
- Coarse-to-fine aim sweep in the wind grids (`fast.c2f_aim`): same records, ~20 % less time.

Why it is exact: the same IEEE operations in the same order, no fused multiply-add, no fast-math; `hypot` is
glibc's algorithm written out and checked against the running libm at load (falls back to libm if they differ).

### Equivalence on this box (engine vs kernel, same process inputs)

| compared | result |
|---|---|
| Gateway Back, all 13 holes x 3 temps x {0, 5, 10 mph} x 4 directions, refined (351 cells) | JSON identical |
| Gateway Back hole 8 full decide (16 draws + ladder + sensitivities + sweep + shares) | JSON identical |
| Gateway Back holes 10, 16 `decide.bayes`, 32 prior draws | JSON identical |
| Eagle Knoll Back, all 14 holes x 50 F x {0, 10 mph x 4 directions}, refined (70 cells) | JSON identical |
| Eagle Knoll Back holes 9, 14, 15 `decide.bayes`, 8 draws | JSON identical |
| rasters (lie, entry_dist, blocked, native_depth), 13 holes x base + jittered maps | equal |
| strokes raster, 76 worlds (central, v1 ladder worlds, tour table, prior draws) | equal |

Not run: the engine at 256 draws on every hole (hours). The Actions comparison below covers that for Gateway.
One Eagle Knoll slice (temps 35 / 65 on 3 holes) failed to run because of my own bad arguments and was not redone.

### Acceptance against Actions

| Actions run | fastsolve vs committed outputs |
|---|---|
| rev 7, cee080946 (final map), Back: book + 11 grids, 23,790 cells | 0 differences above 1e-9; 4,775 numbers differ in the last float bit (max 3.6e-15) |
| rev 7, Middle: book + card grid, 2,379 cells | 0 differences above 1e-9; 754 last-bit differences |
| rev 6, 57dae0081 (map 222f7ece4) | 10 holes identical in all 13 files; 2 / 3 / 5 identical on a 0 / 10 mph sample |

The last-bit differences are numpy summation on the runner's CPU against this box (margin_se, crossfit, some cell
EVs); every pick, runner, aim, window and at_bound is identical. Note for rev 6: the `course.py` that Actions run
committed was re-prepared on the later map, so 2 / 3 / 5 only match with 222f7ece4's own `course.py`.

The engine's own seed noise (5 seeds, refined calm cell, all 13 holes): no pick flips; pick aim range median 1.0 yd,
max 2.0; EV sd median 0.0008, max 0.0026.

### Speed, exact kernel

| | engine | kernel | factor |
|---|---|---|---|
| refined wind cell, one core | 3.06 s | 0.15 s | ~20 |
| prior draw of the book, one core | 3.35 s | 0.17 s, later ~0.12 s | ~20-28 |
| full decide of hole 8 (16 draws) | 359 s | 12.7 s | 28 |
| Eagle Knoll, 14 holes x 5 refined cells (CPU-s) | 1,852 | 74 | 25 |
| per ball, one core | ~270 ns | 5-20 ns (fairway balls roll 13 steps) | |

A Back solve is about 200 billion balls (offset grids 143 G, card grid 27 G, book 32 G). At 8-20 ns a ball the
exact kernel cannot go under several minutes: the rest has to come from fewer balls.

## 3. The adaptive Sobol solver

Three changes, all behind flags:

- **Sobol swings** (`--swings sobol`, `fast.sobol_draws`): scrambled Sobol points in the 5 swing dimensions
  instead of independent draws.
- **Adaptive wind grids** (`--adaptive 1`, `adaptive.py` -> `fs_grid`): one C call per (hole, offset,
  temperature) does every cell and club. Per cell: coarse basin search (128 swings, 3-yd aims; every basin within
  0.04 strokes is kept), 0.5-yd window on 512 swings, racing on paired block differences (a club worse than the
  leader by more than max(3, t) SE is dropped), then doubling until the runner-up is separated at 99 % and the
  leader's aim (block jackknife) is within +/-1 yd at 99 %, or the cap. Cells that reach the cap unseparated
  carry `tie: true`.
- **Fewer swings where Sobol makes them unnecessary**: 512 per prior draw, 2,048 for the central worlds.

### Convergence (30 replications, converged answer = 1 M Sobol swings; `converge.py`, `converge_gateway.json`)

Smallest N meeting each criterion at that N and every larger N tested:

| hole (converged pick, margin) | pick right >= 99 % | aim within 1 yd >= 99 % | margin SE < 0.002 |
|---|---|---|---|
| 8 (Driver, 0.045) | random 128, Sobol 128 | random 32,768, Sobol 8,192 | random 4,096, Sobol 1,024 |
| 10 (2-wood, 0.018) | random 2,048, Sobol 512 | random > 32,768, Sobol 4,096 | random > 32,768, Sobol 4,096 |
| 16 (4-wood, 0.102) | random 128, Sobol 128 | random 8,192, Sobol 2,048 | random 32,768, Sobol 1,024 |
| 13 (Driver, 0.129) | random 128, Sobol 128 | random 32,768, Sobol 4,096 | random 16,384, Sobol 2,048 |

With 30 replications ">= 99 %" means all 30. Today's 16,000 random swings give an aim sd of 0.4-0.8 yd; Sobol 4,096
gives 0.3-0.7. So Sobol 4,096 is at least today's refine precision, and the pick is settled by a few hundred
swings; it is the +/-1 yd aim rule that sends most cells to the cap.

Antithetic pairs were tried on hole 10
only and did not help the EV (sd 0.0071 against 0.0049 for plain random at 16k).

### Agreement of the 183 s solve with Actions rev 7

- Book: same club on all 26 holes (Back + Middle), aims within 0.5 yd, margins within 0.002.
- Back wind grids, 23,790 cells: club differs in 357 (1.5 %). All but one are flagged tie or have a reference
  margin <= 0.02. The one clear disagreement: offset -80, hole 16, 50 F, 15 mph from 300: fastsolve Driver by 0.025
  (1,024 Sobol swings), rev 7 2-wood by 0.023 (2,500 random swings). I did not adjudicate it with a long run.
- 2,460 Back cells are flagged tie.
- Middle card grid, 2,379 cells: 18 club differences, none clear; aim differs by more than 1 yd in 4 %, more than
  2 yd in 0.3 %.
- Back including the nine offset grids: aim differs by more than 1 yd in 27 % of cells, more than 2 yd in 8 %.
  Those nine reference grids are 2,500 random swings, whose own aim sd is 2-3.5 yd.

Where the 183 s goes: books 459 CPU-s (map repaint + value raster, ~70 ms a draw x 6,656 draws), wind 229 CPU-s
(11 G balls). The per-draw raster is the floor now.

### 3-hole timings (8, 10, 16; seconds per hole, one process per hole)

| | exact kernel | adaptive Sobol |
|---|---|---|
| book (256 draws + ladder + sensitivities + sweep) | 40.9 | ~23 before the band repaint (not re-timed after) |
| refined card grid (183 cells) | 25.6 | 2.3 (cap 4,096) |
| one offset grid (183 cells) | 7.7 | 2.0 at cap 4,096; cap 1,024 used in the full run |

## 4. On demand

`ondemand.py`: one temperature / wind speed / wind direction, all 13 Gateway tee shots, no grid interpolation.
Exact kernel (2,500 + 16,000 swings): 1.07 s. Sobol 512 + 4,096: 0.42 s. Start-up (imports, map, rasters) is 2 s
on top unless the process stays alive.

## 5. Evaluated and rejected (`experiments.py`)

- **Aim sweep as a convolution.** The roll-out runs along each ball's own line from the tee and changes with the
  lies it crosses, so a finish is not the aim-0 finish shifted sideways: doing that moves EVs by 0.08-0.18 strokes
  and aims by up to 12 yds (holes 8, 10). A landing-value raster (roll-out from the landing cell centre, roll
  rounded to 1 yd) is closer: max EV error 0.0007-0.0051, aim moved 0.5 yd on 2 of 6 curves. Not adopted.
- **fast-math / FMA** (`-Ofast -ffp-contract=fast`): no faster (x0.71 in one noisy run), curves differ by up to
  2.7e-15, no aim changes. Rejected: nothing gained.
- **float32**: not tried.
- **Mirrored wind directions sharing one sweep**: skipped on instruction.

## 6. How to run

```
# exact (the engine's numbers), outputs into a separate folder
python3 course_data/courses/fastsolve/run.py solve --slug gateway_national --which truth \
    --request course_data/requests/nccga_v2_gateway_national.json --out /tmp/fs_gateway
# adaptive Sobol (the 183 s configuration)
python3 course_data/courses/fastsolve/run.py solve --slug gateway_national --which truth \
    --request course_data/requests/nccga_v2_gateway_national.json --out DIR --swings sobol \
    --swings-decide 512 --central 2048 --adaptive 1 --adaptive-cap 4096 --adaptive-cap-other 1024
python3 course_data/courses/fastsolve/run.py compare --slug gateway_national --out DIR [--ref OTHER_DIR]
python3 course_data/courses/fastsolve/ondemand.py --temp 41 --wind 12 --from 200
python3 -m pytest -q course_data/courses/fastsolve/test_fastsolve.py        # 105 s: kernels vs engine
```

Iteration (seconds instead of minutes): `--holes 8,10` solves only those holes and merges them into whatever is
already in `--out` (the other holes' book entries and wind cells are kept); `--card-only` skips the offset grids
(book + card-tee grid). One hole `--holes 10 --card-only`: 8.6 s, Back `--card-only`: 37 s, both measured before the book steps (which take about 3 s a hole off). `--only
decide` / `--only wind` take one half. The book shortcuts are `--book-res 1.0 --book-maps 16 --book-race 1`
(defaults; 0 switches each off), `--f32 1` the float32 wind lanes, `--exact` the engine's own numbers.

`run.py` refuses to write inside a course folder. `--engine slow` runs the same tasks on the unpatched engine.
Other scripts: `bench.py`, `equiv.py seeds`, `noise.py`, `converge.py`, `experiments.py`.

## 7. Known differences and limits

- Exact path: identical to the engine on this box; against another CPU, last-bit differences in a few summed
  statistics.
- Adaptive path: wind cells carry extra fields (`n_swings`, `margin_se`, `tie`, `aim_se`, `aim_ok`, per-club `n`).
  The aim is the minimum of the smoothed curve by a parabola, not the engine's spline + Brent; the zone is clipped
  to the evaluated window. Clubs dropped early are reported from 512 swings.
- With Sobol swings `decide.bayes`'s `swing_noise_share` compares two halves of one Sobol set, not two independent
  halves.
- Lidar flight trees are covered by both paths (section "Flight-tree courses"); with them `--f32` is ignored.
- Times assume AVX-512. The scalar path is what the first measurements used (about 3x slower per ball; `fs_grid`'s
  scalar branch about 2x on Eagle Knoll).
- The legacy constant-height flight-tree check is not ported (falls back to the engine's function).
- Tests: the exact kernel against the engine, and the adaptive grid's per-ball code against the engine on the grid's
  own swings (Gateway 10 / 16, Eagle Knoll 1 / 14 / 15). The adaptive stopping rule itself has no test.

## 8. Before it replaces the Actions solve

- A test of the adaptive stopping rule (the per-ball code is tested; its scalar branch was run once by hand on
  Eagle Knoll 9 / 14 and Gateway 10 with `FASTSOLVE_SIMD=0`: same numbers as the AVX-512 branch).
- A draw-local repaint and value-raster update (not built) if the whole solve is to go under a minute at the
  183 s run's precision.
- A decision on the stopping rule: most cells hit the cap on the +/-1 yd aim rule.
- Page build and the par-3 target solve were not profiled.
