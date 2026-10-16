# PROJECT.md: Tee-shot strategy system (DECADE style)

Player: ~5 handicap. Driver 275 carry / 300 total / 65-yd width, 2-wood 265/280/60, 4-wood 255/270/50.
Courses: Mozingo Lake GC (`mozingo/`, 14 tee holes + 4 par 3s) and Spirit Hollow GC (`spirit_hollow/`,
16 tee shots on 14 holes, two of them with back and forward tees (2B/2F, 9B/9F), plus 3 par 3s; **hole 3 is missing**).
Written by the PM/tech-lead review, 2026-10-16. Test run at review time: `pytest` gives 322 passed in 4.9 s.

---

## 1. System overview

```
 INPUTS                      MAP                        SIMULATION                  DECISION                    BOOK
 GPS-app screenshots   -->  course.py / tee_strategy  -->  tee_strategy.simulate  -->  tee_strategy.best_aim   -->  yardage_book.build
 (920x2000 frame,           .HOLES: tee, dot270,          2-D normal carry + mishit      (point estimate, book)      Strategy PDF + Aim Sheets
  red 300/270/240 dots,     polygons (fairway, recovery,  roll-out in 2-yd steps,      stats.py (100 what-if        cover: picks + "locks /
  app Center numbers)       sand, native, water, ob),      lie_at() point-in-polygon,   worlds -> confidence %)      coin flips" from
 Club table (CLUBS)         green (trilaterated from       Broadie tour baseline        decision.py (Bayesian,       stats_report.md regex
 research.md priors         APP numbers), PAR3 greens      (opt. HCP_BASELINE)          EVPI, width break-evens)     par-3 DECADE edge rule
                                    ^                                                   analysis.py (break-evens,
 QA side-loop:  vision.py (GBT pixel classifier, LOHO) / deep/ (DINOv2 features, SAM masks) / review.py (landing-zone sheet)
                -> flags disagreements -> human re-traces course.py
```

Data flow: screenshots -> hand-traced pixel polygons -> `hole_frame()` (yards per pixel from the tee->270-dot vector)
-> 20k Monte Carlo swings per club/aim -> expected strokes -> argmin over clubs and aims -> PDF pages.
All modules talk through **mutable module globals in `tee_strategy`** (`HOLES`, `CLUBS`, `Z`, `TREE_SEVERITY`, ...).

| File | Owns | Owner |
|---|---|---|
| `mozingo/tee_strategy.py` | Shot model, baselines, `simulate`, `best_aim`, Mozingo `HOLES` | Integrator |
| `mozingo/yardage_book.py` | PDF book, par-3 DECADE rule (`par3_plan`), Mozingo PAR3/NOTES/AIM_AT, `use_course()` | Integrator |
| `mozingo/stats.py` | SG:OTT tables, paired CIs, 100-world robustness -> `stats_report.md` (feeds book confidence) | Integrator / stats review |
| `mozingo/scenarios.py` | Ad-hoc what-ifs (runs on import, prints only) | Nobody (legacy) |
| `spirit_hollow/course.py` | Spirit Hollow HOLES, APP numbers, GREEN_SIDE, PAR3, NOTES, AIM_AT, ORDER | Integrator (map audit proposes) |
| `spirit_hollow/decision.py` | Bayesian pick (Sobol prior, EVPI, driver-width break-evens) -> `decision.json/.md` | Integrator |
| `spirit_hollow/analysis.py` | Model-form checks, break-evens, 120 worlds, attribution -> `analysis_report.md` (**never written**) | Unowned; overlaps decision.py |
| `spirit_hollow/build.py` | Wires course.py into yardage_book; `--stats` re-runs stats.py | Integrator |
| `spirit_hollow/review.py` | Landing-zone review PNG (script, no `main`) | Map audit |
| `spirit_hollow/vision.py` | Hand-feature GBT classifier, leave-one-hole-out QA -> `vision_report.md` | Vision |
| `spirit_hollow/deep/*.py` + workflows | DINOv2 features (done, committed), SAM masks (workflow, no output yet) | Vision / CI |
| `spirit_hollow/research.md` | Amateur baselines, dispersion, DECADE rules (search-extract sourced) | Stats review |
| `tests/` | 67 test functions / 322 parametrised cases: model, course geometry, par-3 rule | Integrator |

## 2. Status by workstream

| Workstream | Status | Quality assessment |
|---|---|---|
| Shot model (`tee_strategy`) | Done | Simple and well tested. Tour baseline by default. OB = 2 + rough at the landing distance (approximation, l.127). No wind, elevation or slope roll except a hand `extra_roll` (Mozingo 18). |
| Mozingo map + book | Done (v1) | 14 tee holes + 4 par 3s; PDFs built. README is stale ("8, 14-18 still to come"). Hole 4 imagery is cloud-shadowed. No OB anywhere on the Mozingo map. |
| Spirit Hollow map | Done, under audit | 16 tee shots + 3 par 3s; hole 3 missing. Errors found and fixed: 4 (fairway over tan grass), 18 (fairway under woods), 9 (creek missed), 7 (approach traced as the green), 1 (tan band left, found by vision QA), 2F (creek to the rough edge, found by vision QA). `vision_report.md` still lists 33 confident disagreements whose outcomes aren't recorded anywhere in the repo. |
| Independent map audit | In progress (agent) | No output in the repo yet. |
| Vision v1 (`vision.py`) | Done | Weak. Leave-one-hole-out pixel accuracy is **52.4%** (whole hole) and **59.4%** (landing zones). Penal vs playable: 72.5% / 79.2%. Landing-zone penal precision **55%**, rough recall 31-33%, native recall 36-37%. Good enough to point at places to re-check, not to build the map. |
| DINOv2 features (`deep/extract_features.py`) | Done | 19 `.npz` files, 64 PCA channels covering 88% of the variance. Whether they help hasn't been measured (`VISION_FEATS=deep` has no report). |
| SAM masks (`deep/sam_masks.py`, `sam_masks.yml`) | In progress | Workflow exists. There is no `spirit_hollow/deep/sam/` output yet. |
| SAM+DINOv2 classifier (`vision2.py`) | In progress (agent) | The file has appeared in the repo but has no report yet. Acceptance bar: beats 59.4% in the landing zones and 55% penal precision, leave-one-hole-out. |
| Stats report (`stats.py`) | Done | CIs are tight (±0.002-0.005). They cover Monte Carlo noise only, given the model. Robustness: 100 worlds x 2,000 shots on a 5-yd aim grid. |
| Bayesian decision (`decision.py`) | Done in code, **report invalid** | `decision_report.md` was produced with **S=4 draws** (P(best) moves in 25% steps; hole 11 margin 0.008 ± 0.119). It must be re-run at S>=64. |
| `analysis.py` | Not run to completion | No `analysis_report.md` / `analysis.json` in `output/`. |
| Adversarial stats review (`review_stats/`) | In progress (agent) | Not in the repo yet. |
| DECADE corridor benchmark (`benchmark/`) | In progress (agent) | Not in the repo yet. research.md section 5: 65-70-yd dead-zone rule; for this player the equivalent is about 80-85 yd. |
| OSM/NAIP auto course data (`course_data/`) | Spike in progress (agent) | Not in the repo yet. |
| Tests / CI | Partial | 322 tests cover the model, course geometry, the par-3 rule and `use_course`. **Zero tests** for decision.py, analysis.py, stats.py, vision.py, review.py and deep/. **No pytest workflow**: CI only runs the GPU-free feature and mask jobs. |

**The engines disagree.** The book's pick comes from `yardage_book.tee_plan` (point estimate, 65-yd width, tour baseline). Its confidence % comes from stats.py. decision.py is a third answer, and the book never reads it. They currently disagree on:
- Spirit Hollow 1: book and stats say Driver (64%); decision says 4-wood (P 25%).
- Spirit Hollow 16: Driver (34%) vs 4-wood.

## 3. Risk register (top risks to recommendation correctness)

L = likelihood, I = impact (H/M/L). Ranked by L x I.

| # | Risk | L | I | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | **Dispersion too narrow.** The model uses width/4, so driver sigma = 16.25 yd. research.md fits sigma of about 21 (an 80-85-yd window) to the published 5-hcp data (49% fairways, 7% more than 40 yd offline). decision.py break-evens flip Driver->wood at 70-79 yd on holes 1, 4, 5, 6, 9B, 14, 16 and 18, which is *inside* that plausible range. | H | H | Get the golfer's real dispersion (launch monitor or 30+ tracked drives). Until then, rebuild the book at width 80 and mark every hole whose pick flips between 65 and 85 as "depends on your driving day". | Integrator + golfer |
| R2 | **Three decision engines with no single source of truth.** The book (point estimate), stats.py (robustness %) and decision.py (Bayes) give different picks. The book confidence is regex-scraped from markdown (`yardage_book.py:123-132`). | H | H | Pick one engine (recommended: decision.py at S>=64, prior width centred about 75-80). Have the book read `decision.json`. Retire analysis.py or merge it in. Fail the build if the engines disagree without a note. | Integrator |
| R3 | **Map tracing errors.** Six errors were found after the fact. Edges are traced by eye to ±5 yd. 33 confident vision disagreements have no recorded outcome. | H | H | Finish the independent audit. Record each flag's verdict in a file under source control. Run `review.py` on every hole after every map change. Vision2 is QA only. | Map audit |
| R4 | **Baseline choice.** The tour baseline is the default (`HCP_BASELINE=False`). research.md says amateur rough costs about 0.7x tour and sand about 1.1x, so the tour table over-penalises missed fairways and biases toward short clubs. | M | H | Run the book under both baselines. Adopt the HCP baseline if the stats review accepts it. List picks that flip. | Stats review -> integrator |
| R5 | **Single-screenshot geometry.** Scale comes from one tee->270-dot vector per hole. Spirit Hollow 1 has its tee **extrapolated 9 dot-spacings off-screen** (`course.py:22`, y=2622); 10 and 18 are also off-screen. Photo tilt makes trees lean. A 1-2% scale error = 3-6 yd at 300. | M | H | Cross-check the 300/240 dots and the APP numbers (a test exists for the green). Add a per-hole scale residual test on all three dots. Confirm against OSM/NAIP (course_data spike). | Map audit / course_data |
| R6 | **Untraced OB.** Anything untraced is scored as rough. OB is drawn only where houses are visible (Spirit Hollow 2F, 4, 5, 8, 9B); Mozingo has none. Stakes and white lines can't be seen in imagery. | M | H | Golfer confirms OB on the scorecard or local rules. Add an `ob` check to the definition of done. The OSM `golf=*`/landuse spike may help. | Golfer + map audit |
| R7 | **Green placement.** Par-4/5 greens are trilaterated from the app's rounded Center numbers plus a hand-set `GREEN_SIDE` (`course.py:259-289`). Spirit Hollow par-3 12's green is a **synthetic 60-px circle** (`course.py:319-320`). Hole `length` is redefined as 270 + Center. | M | M | Trace the real 12 green. Test the trilateration residual on all three dots. Sanity-check `length` against the scorecard. | Map audit |
| R8 | **Monte Carlo noise and grid artefacts.** Robustness uses 2,000 shots on a 5-yd aim grid. decision.py clips aims to ±25 while course.py sets ±40 (Spirit Hollow 11 driver pinned at +40). The current Bayes report has S=4. Many margins are under 0.01, i.e. coin flips. | H | M | Use S>=64 and N>=5,000. Report "tie" when the margin is under 2 SE or under 0.01. Use one aim grid everywhere. | Integrator |
| R9 | **Global-state coupling in `tee_strategy`.** Every caller monkeypatches module globals (`t.HOLES = course.HOLES` at import in analysis.py:34, vision.py:39, review.py:12; `t.Z`/`N_SHOTS` overwritten in analysis.py:37). A missed `reset()` silently contaminates the next hole. `tee_plan` is lru-cached on globals. | M | M | Introduce a `Model`/`Params` object passed explicitly (see section 6). Until then, keep the `conftest` global snapshot and add a test that `build()` is idempotent. | Integrator |
| R10 | **Unmodelled physics.** Wind, elevation and firmness aren't modelled. A downhill hand roll exists only on Mozingo 18 (`extra_roll`). Prose NOTES hard-code margins ("Driver by 0.08") that go stale on re-run. | M | M | Generate the numbers in NOTES from results. Add a per-hole elevation/roll field once the golfer confirms it. | Integrator |

## 4. Definition of done: final strategy book

- [ ] Every hole on the scorecard is present, including Spirit Hollow 3. Par and length match the scorecard within 5 yd.
- [ ] The independent map audit has signed off every hole. Every vision flag has a recorded verdict (fixed / not an error).
- [ ] `review.py` sheets regenerated for all holes after the last map change. No simulated ball sits on visibly wrong terrain.
- [ ] OB, penalty areas and lateral-vs-red/yellow confirmed against the local rules or scorecard for every hole.
- [ ] Every par-3 green is traced from imagery (no synthetic shapes). Front/back match the app within 2 yd.
- [ ] Per-hole scale check: the 300/270/240 dots and the Center numbers agree within 2 yd (an automated test).
- [ ] Dispersion is calibrated from the golfer's own data, or the book shows picks at both 65 and 80 yd.
- [ ] One decision engine. Book picks, confidence and margins come from one JSON run with S>=64 and recorded seeds.
- [ ] Margins under 2 SE (or under 0.01 strokes) are printed as "tie: choose by feel / conditions", never as a pick.
- [ ] The baseline choice (tour vs HCP) is documented. Holes that flip under the alternative are flagged on the page.
- [ ] NOTES text matches the current numbers (generated, or checked by a test).
- [ ] The stats review and corridor benchmark have no open blocker. Every disagreement with the DECADE rule is explained.
- [ ] `pytest` is green in CI (workflow added). decision/stats code has smoke tests.
- [ ] The golfer has read one page per hole and confirmed the aim landmarks make sense on the tee.

## 5. Prioritised backlog (next 10)

1. **Unify the decision engine.** decision.py writes `decision.json`. `yardage_book.tee_page/cover` read it (no regex). Delete or fold in the analysis.py duplicates. Re-run at S>=64. *(Integrator)*
2. **Dispersion calibration plus a dual-width book.** Collect the golfer's dispersion. Meanwhile, centre the prior near 78 yd (research sigma 21) and print the "pick flips at X yd" line on each page. *(Integrator + golfer)*
3. **Close the map audit.** Hole 3, a real green for 12, recorded verdicts for all 33 vision flags, OB confirmation, an automated 3-dot scale test. *(Map audit)*
4. **"Tell me the course and tees, no screenshots" (product direction).** `course_data/` loader: OSM `golf=fairway|green|bunker|water_hazard|tee|rough` + `natural=wood` polygons, projected to yards (UTM). Tees and greens from OSM `golf=tee/green`, or a hole centreline from `golf=hole` ways. NAIP 0.6 m imagery for vision2 to fill untagged trees and long grass. Output the same `HOLES` schema in yards (no pixel frame), so `simulate` works unchanged. *(course_data spike -> integrator)*
5. **Refactor out the global state.** `Params` dataclass (clubs, severities, baseline, z), and `simulate(hole, club, aim, params)`. Remove the `t.HOLES = ...` monkeypatching. Pure functions make the book reproducible. *(Integrator)*
6. **Baseline decision.** The stats review adjudicates the tour vs HCP baseline and the lie multipliers (rough 0.7x). Adopt the result and list the flips. *(Stats review)*
7. **DECADE corridor benchmark in the book.** Show the rule-based pick (dead zones within 80-85 yd -> club down) next to the model pick. Any disagreement gets a one-line explanation. *(Benchmark)*
8. **CI.** Add a `pytest` workflow. Add smoke tests for `decision.main` (S=2, N=200), `stats.sg_table`, and `vision.ui_mask`/`label_map` shapes. *(Integrator)*
9. **Vision2 acceptance.** Measure SAM+DINOv2 leave-one-hole-out against the v1 numbers. Adopt it as the QA flagger only if it beats 59.4% / 55% penal precision in the landing zones. *(Vision)*
10. **Conditions page.** Wind, firmness and elevation adjustments (carry ±, roll factor) as a small "today" table, using the existing break-evens. Generate NOTES from results. *(Integrator)*

## 6. Code-health findings

**Duplication**
- Map jitter (shift each polygon by N(0, k·ppy)) is implemented three times: `mozingo/stats.py:52-57`, `spirit_hollow/decision.py:89-97`, `spirit_hollow/analysis.py:147-151`.
- `reset()` and the `BASE` snapshot are written twice: `decision.py:62-63,100-104` and `analysis.py:40-52`. The test fixture `tests/conftest.py:29-47` is a third copy.
- Club/world perturbation is written three times: `stats.py:40-58`, `decision.py:82-97`, `analysis.py:135-146`.
- Flip-point interpolation is written twice: `decision.py:197-204` and `analysis.py:100-105`.
- `clubs_for` exists in `tee_strategy.py:352` and again in `decision.py:114` (BASE-based). The aim-bounds logic is in `tee_strategy.best_aim:417-421`, `decision.aims_for:107-111` (clipped to ±25) and `yardage_book.tee_plan:150-152` (default ±20). These are three different grids.
- The tee-frame maths is in `tee_strategy.hole_frame:342`, `course.py:281-284` (inline), `course._par3:296-300` and `yardage_book.frame:204`.
- The `share` dict is built twice inside `best_aim` (`tee_strategy.py:427-428, 436-437`).
- `spirit_hollow/analysis.py` and `decision.py` both answer "which club, how sure, what flips it". analysis.py has never produced output. **Recommend merging its variants/attribution into decision.py and deleting the rest.**

**Global state**
- `tee_strategy` has 14+ mutable globals (`HOLES, CLUBS, IRONS, Z, N_SHOTS, TAIL_NU, CHI, RHO, HCP_BASELINE, TREE_SEVERITY, NATIVE_LOST, MISHIT_RATE, ROUGH_ROLL, REFINE`). `set_tails` uses `global` (l.93-96).
- `yardage_book.use_course` rewrites 9 globals (l.58-64). `tee_plan` is `lru_cache`d over globals (l.146), so a stale cache is possible if `HOLES` is mutated in place.
- Import-time mutation: `analysis.py:34,37`, `vision.py:39`, `review.py:12` set `t.HOLES` (and `t.Z`) on import. `mozingo/scenarios.py` and `spirit_hollow/review.py` run their whole body at import (no `__main__` guard).
- Every script uses `sys.path` hacks (`build.py:12-13`, `decision.py:53`, `analysis.py:29`, `vision.py:34`) because the code isn't a package. Add `pyproject.toml` with a `golfsim` package.

**Ordering / latent bugs**
- `REFINE` is defined after `best_aim` (`tee_strategy.py:443` vs 416). `HCP_LIE_MULT` is defined after its use (l.119 vs 114). Both work only because they're module-level.
- `plot_hole` colours have no `"ob"` key (`tee_strategy.py:456-457`), so it raises KeyError on any Spirit Hollow hole with OB.
- `review.py:16` hard-codes `k = 1206/920` (assumes the native screenshot width). It breaks silently on other devices.
- `course.py:278-280` defaults every Spirit Hollow hole to `aim_min/max = ±40`, so `best_aim` ignores the caller's `aims` argument and always searches ±40 at 2.5-yd steps.
- decision.py doesn't perturb `IRONS` width or carry (`apply`, l.82-97), so irons look relatively better in wide-dispersion draws on 11 and 13.

**Naming inconsistencies**
- Lies are called `recovery` in the map but "trees" in reports and par-3 `haz`. The map's `sand` is "bunker" in `yardage_book.ADD/SEVERITY`. `native` appears as "long grass", "prairie", "tall grass" and "reeds" in comments.
- Hole keys mix `int` and `str` ("2B", "9F"). `length` means scorecard yards on Mozingo but 270 + app Center on Spirit Hollow (`course.py:289`).
- Club tuples are positional `(carry, total, width, depth)` everywhere. Use a NamedTuple.

**Missing or stale docs, dead code**
- `mozingo/README.md` says "8, 14-18 still to come", but those holes are done. `spirit_hollow/README.md` says "holes 1-3 weren't provided", but 1 and 2 are present. The `course.py` docstring lists 10 and 18 as off-screen tees but omits hole 1.
- `golf_data_science.py` and `golf_data.csv` (score vs days plot) are unrelated to the system. Move them to `misc/` or delete them.
- `mozingo/scenarios.py` hard-codes old polygons (l.36 `(200, 550)...`) and the old README numbers. Treat it as dead code or turn it into tests.
- `vision_report.md` points to "the strategy README" for flag outcomes, but there are none there.
- No module documents the global-mutation contract. There are no type hints. `__pycache__/` and `.pytest_cache/` are in the tree; `.pytest_cache` isn't ignored.
