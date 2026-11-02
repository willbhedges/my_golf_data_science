# Long grass vs the error budget (2026-11-02)

`native_thr: null` in `model_v2/model.json` is a decision, not a lost setting. It is now recorded as
`settings.native_off`, and `v2_model.check_native_settings` (test: `test_v2.py`) refuses a bare None, so packages
no longer print `P(native) >= None`.

The error budget (`platform/ERROR_BUDGET.md`) found that the true long-grass layer would cut regret 64 %. The
committed product P(native) at the training-course threshold (0.04) and at 0.3 / 0.5 was rebuilt into the packages
(`v2_longgrass_eb_build.py`) and re-scored (`platform/error_budget_variant.py`). On 7 held-out card courses
(96 tee shots), every threshold is worse than no long grass: match 71 -> 47 / 63 / 61, regret 1.36 -> 4.84 / 3.18 /
2.58 strokes. Corridor IoU where hand native exists is 0.41 / 0.25 / 0.18. The false long grass in corridors with
none is 247k / 101k / 59k sq yds, so pooled precision is 0.14-0.17. Details and caveats:
`platform/ERROR_BUDGET.md`, "Follow-up 2026-11-02".

Follow-up (v3, same day): `v3_longgrass_loco.md`. A LOCO classifier with a per-course mown-rough reference raises
pooled corridor precision to 0.50 at recall 0.10 (Pine Dunes 85 % -> 0.3 % marked). It is still worse than none in
this budget (match 71 -> 67-69, regret 1.36 -> 1.40-1.46), and so is a simulated per-hole yes/no tap. Not adopted.
