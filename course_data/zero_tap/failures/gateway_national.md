# Gateway National Golf Links (Madison, IL): blind automatic pipeline vs hand truth

NCCGA Regional 3 (Nov 14-15 2026). Blind request = name + town + state + "Blue" (`course_data/requests/package_gateway_national.json`).
"Blue" is not on this card (The Tips / Champions / Back / Middle / Forward); the pipeline substituted the longest
set name match rule -> **Back** (6623), which is the length the NCCGA played here in 2024: right by luck.
Truth: `course_data/truth/gateway_national/` (holes_truth.json; trace.py / hand_zones_ll.json, 13 par 4/5 corridors
from the Back tee). Scores: `course_data/courses/gateway_national/score_*.md`.

## Before / after

| | v0: first package build | blind auto (+ vision_any / OB evidence, rebuilt) |
|---|---|---|
| routing / par / green within 10 yds | 18/18, 18/18, 18/18 | same |
| par 3s planned (with outline) | 5/5 (5/5) | 5/5 (5/5) |
| tees within 10 yds (5 sets) | 89/90 | 89/90 |
| trees IoU | 0.0 | 0.33 |
| long grass IoU | 0.0 (every hole) | 0.0 (every hole) |
| tee-shot club same / same-or-tie | 11/13, 11/13 | 11/13, 11/13 |
| total regret | 0.126 strokes | 0.126 strokes |

No change kept (the experiment below did not pass). "after" = "blind auto".

## Failures

| # | holes | category | what went wrong | root cause | proposed fix | owner |
|---|---|---|---|---|---|---|
| G1 | all 13 tee shots (picks wrong on 9, 11) | perception: long grass | no long grass anywhere; a links / prairie course whose main hazard is fescue / prairie framing every hole (truth: native on 13/13 corridors). The planner plays it as rough: Driver +22 on 11 (truth 4-wood +8), 2-wood on 9 (truth 4-wood) | `vision_any/model_v2/model.json` ships `native_thr: null` (long grass OFF): the decision-level calibration (`v2_decision_calibration.md`) chose "off" on Spirit Hollow + Mozingo, two parkland courses where long grass is minor | the long-grass switch must be calibrated on a course mix that includes links / prairie courses (Gateway, Coldwater, Pine Dunes): add these hand maps to `v2_calibrate.py`; or gate it per course by the share of unmown, no-height vegetation inside the outline | A (formation / perception) |
| G2 | experiment | - | a simple rule (no lidar height + NIR local std >= T + >= D yds from OSM mown polygons) | - | Gateway native IoU 0.25 (precision 0.63, recall 0.30) at best, and 23-28k false-positive cells on Eagle Knoll's corridors: not adopted; texture alone does not separate fescue from dry mown rough in August NAIP | A |
| G3 | tee set | request | "Blue" not on the card -> longest-set substitute | the card names sets by name not colour (Back = black / "Blue" on the NCCGA sheet) | map a requested colour to the set whose total is closest to the tournament length when known; flag the substitution in the plan (it is, in the package warning) | C |
| G4 | 7, 12 (Middle) | tees | Middle set put on the Back / the pad ahead, 10-15 yds off the card | shared complex, no separate Middle box in OSM | as Eagle Knoll F5 | C |
| G5 | Actions | tooling | `nccga_v2.yml` compute jobs failed at `prepare` (`No module named 'cv2'`: product/imagery.render_all needs OpenCV) | missing pip dependency | fixed: opencv-python-headless added to both pip lines | - |

## Uncertain in the truth

* Fescue edges +/-5 yds (dry mown rough vs fescue in the Aug 2023 photo; checked on CIR and NAIP 2022).
* Middle tees on 7 / 12 estimated from the card.
