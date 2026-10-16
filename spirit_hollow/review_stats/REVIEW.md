# Statistical review: `spirit_hollow/decision.py` + `mozingo/tee_strategy.py`

Referee report. No existing file was modified. Everything below can be reproduced from this
folder:

| File | What it is |
|---|---|
| `experiment.py` → `experiment_results.json`, `experiment.log` | Holes 1, 16, 5. Four independent randomised-QMC batches (S=32, N=3000 each), a high-N "truth" (N=15,000 on 24 draws), width sweeps, and a calibration check (~10 min) |
| `structural.py` → `structural_results.json`, `structural.log` | All 16 holes at the prior-mean world under five structural variants (~2 min) |
| `corridor.py` | What the DECADE corridor rule means in this model's terms (analytic) |
| `decision_stats.py` (+ `test_decision_stats.py`) | **Patch 1**: honest Monte Carlo error, winner's-curse check, EVPI bracket, corrected P(best), common-scale width sweep |
| `baseline_patch.py` (+ `test_baseline_patch.py`) | **Patch 2**: lost ball priced as stroke-and-distance; HCP penalty-stroke consistency |
| `prior_patch.py` (+ `test_prior_patch.py`) | **Patch 3**: re-centred and widened prior (width ratios, common carry factor, depth, rough roll, scoring table) |

Tests: `python3 -m pytest -q spirit_hollow/review_stats/` (18 pass).

The 96-draw production run that was going on alongside this review had finished the per-hole table when this was written (its stdout log; `output/decision*.{json,md}` was still the earlier 4-draw run). It is quoted as "run-96".

---

## Executive summary

1. **The Monte Carlo is fine. The model is not.** At S=96 and N=3000 the margin SE is 0.001-0.006 strokes. The winner's-curse optimism is ≤0.002 strokes. Swing noise is only 1-5% of the variance of each draw's club difference. But structural choices that sit *outside* the prior move margins by 0.02-0.05 strokes and flip 5-7 of the 16 picks (section 4, table S). The reported EVPI (~0.09 strokes/round in total) covers only the parameters that are in the prior, so it greatly overstates how robust the picks are.
2. **The lost-ball cost is wrong by about 1 stroke.** `native` charges a lost ball "1 + rough at the same distance". That is a penalty-area drop. A ball lost outside a penalty area is stroke-and-distance, which the code already prices as `ob` = 2 + rough. This one-line fix alone flips holes 1, 4, 6, 16 and 18 to the 4-wood at the prior-mean world. Hole 18 is a pick that run-96 calls Driver by 0.047 with P(best) 76%.
3. **The prior's width centre contradicts `research.md`.** The median is 70 yd (90% interval ~61-80). The research's best estimate for a 5 handicap is a window of 80-85 yd (σ≈21). That puts the research value at the prior's ~97th percentile. The driver-width break-evens for 1, 4, 5, 6, 9B and 16 all fall at 70-80 yd, so the prior centre, not the data, is setting those picks.
4. **The width *ratios* between clubs are fixed exactly (65:60:50).** Yet they are the main thing a driver-vs-fairway-wood decision depends on. The published amateur data (3-wood only ~1.5% more fairways than driver) suggests the 4-wood is not 23% narrower.
5. **The calibration check fails.** At the prior-mean world, with the driver aimed on the line, the model gives about 75% fairways (published 5-hcp figure: 49%). Penalties run about 5% of drives, excluding hole 11 (published: 1-3%). The fairway polygons look generous, possibly including the first cut, and/or the native polygons or loss share run high.
6. **The decision rule is right for risk-neutral stroke play.** P(best) and EVPI are close to unbiased at N=3000, because CRN works and swing noise is small. They need clearer labels, and P(best) is not what decides the pick.

---

## 1. Decision rule

* **argmin over (c, a) of E_θ[ES(c, a | θ)] is the Bayes act for stroke play under additive, risk-neutral utility.** Total score is a sum over holes, and θ is shared across holes. The round's expected score is therefore the sum of per-hole expectations, and picking hole by hole is optimal for any fixed (non-adaptive) policy. Confirmed.
* **When it is not the right objective:**
  * **Match play.** Maximise P(win hole) − P(lose hole), conditional on the opponent's ball. This is risk-seeking when behind and risk-averse when ahead.
  * **Stableford / net-double-bogey posting cap.** The loss is truncated, so blow-ups are cheaper and aggressive play is favoured.
  * **"Break 80" or a cut line.** This is a nonlinear utility on the round total. Optimise P(total < k), which needs the whole score distribution, not just EV.
  * **Adaptive play.** If the player learns θ during the round (e.g. "driver is spraying today"), a conditional policy beats the fixed one. EVPI caps that value, and the width sweep is the natural "bad-day card".
* **Choosing the aim under the posterior, not per draw, is correct.** You must commit to one aim with θ unknown. Choosing per draw is the clairvoyant policy and belongs only inside EVPI and P(best), which is where the code uses it. Note that P(best) therefore compares clubs *each at its own clairvoyant aim*. It is not "the probability that the posterior play is best". Hole 1 in the 4-draw file shows the effect: the Bayes pick (4-wood) has P(best) 25% while Driver has 50%. That is consistent but confusing. P(best) has no role in the Bayes decision. Report expected regret, or P(pick at its aim beats runner at its aim), which `decision_stats.p_pick_beats` provides.
* **Terminology.** No likelihood is ever applied, so every "posterior" here is the *prior* (a preposterior analysis). Either rename it, or condition on the player's own shot data (Arccos/Shot Scope fairway%, miss L/R, carry) to get a real posterior.
* **Winner's curse (measured).** For each of 4 independent batches, pick (club, aim) on one batch and re-score it on the other three pooled (96 draws):

| Hole | Pooled pick (128 draws) | Pooled margin | Batch picks | Mean in-sample margin | Mean out-of-sample margin | EV optimism | Margin shrink |
|---|---|---|---|---|---|---|---|
| 1 | 4-wood +2.5 vs Driver | 0.0005 | D, 4w, 4w, 4w | 0.0010 | 0.0000 | +0.0005 | 0.0009 |
| 16 | 4-wood −2.5 vs Driver | 0.0018 | D, 4w, 4w, 4w | 0.0026 | 0.0004 | +0.0011 | 0.0021 |
| 5 | Driver −5.0 vs 2-wood | 0.0104 | D ×4 | 0.0104 | 0.0104 | 0.0000 | 0.0000 |

  The optimiser's curse is small in absolute terms (≤0.002 strokes), because CRN makes the EV-vs-aim curves smooth and there are only three clubs. On ties, however, the curse is *the same size as the margin*. On holes 1 and 16, essentially the whole in-sample margin is selection, and one batch in four picks the other club. Regret from a wrong pick was ≤0.003 strokes. **Fix:** report an indifference band, for example "|margin| < 0.01 or < 2·SE → tie". Then break ties with a stated secondary rule: lower P(blow-up), the DECADE default (driver), or whichever club the player trusts. Run-96's ties are 1 (0.001 ± 0.002), 9F (0.000 ± 0.001) and 16 (0.002 ± 0.003). Holes 5, 6 and 9B (0.007-0.010) are practically ties as well.

## 2. Monte Carlo error

Error budget, per batch (S=32, N=3000; `decision_stats.error_budget`). Each draw's paired margin d_s is split into a prior part and a swing-noise part. The swing-noise part is estimated from the two half-samples as ((d_A − d_B)/2)²:

| Hole | sd_θ of d_s | swing share of Var(d_s) | iid SE (S=32) | RQMC replicate SD (S=32) | S for iid-SE < 0.005 |
|---|---|---|---|---|---|
| 1 | ~0.016 | 3-5% | 0.0029 | 0.0010 | 10-14 |
| 16 | ~0.025 | 1-2% | 0.0045 | 0.0024 | 24-30 |
| 5 | ~0.017 | 2-4% | 0.0030 | 0.0009 | 10-14 |

* **N=3000 is more than enough.** Doubling or quadrupling N changes the required S by less than 1 draw. Precision is entirely about S. You could drop to N≈1500 and spend the CPU on draws.
* **decision.py's iid SE is conservative by about 2-3x**, because scrambled Sobol beats iid even with a pseudo-random map-jitter coordinate. That is safe. To get an honest QMC error bar, use R≈8 independent scrambles and the SD of their means.
* **For a margin SE below 0.005:** S ≈ 12-30 by the iid formula, so S=64 is already enough on these holes. Run-96's SEs (0.001-0.006) agree, with hole 11 at 0.006 (irons vs 4-wood depend heavily on carry and roll). For SE < 0.002 everywhere, use S=128 (a power of 2), or S=256 for hole 11. **Use a power of 2.** S=96 triggers scipy's "balance properties require n to be a power of 2" warning (seen in run-96's log).
* **Caveat.** The margin SE is computed at aims chosen on the same draws, so it ignores selection. Use `crossfit_margin` (choose on half the draws, score on the other half) for an honest number.
* **Is P(best) inflated by noise?** Theoretically yes. Per-draw argmin with noisy EVs pulls P toward uniform, and the per-draw min over ~60 noisy grid cells biases EVPI upward. Empirically it is small here, because CRN keeps swing noise at 1-5% of between-draw variance:
  * Deconvolved P(best) (`p_best_deconvolved`) equals the naive value to 2 decimals. The shrinkage factor is about 0.98-0.99.
  * Against the N=15,000 truth on the same 24 draws, naive P(best) at N=3000 is off by ≤0.08. The winner flips in 4%, 12% and 8% of draws (holes 1, 16, 5). Every flip is a within-draw tie of a few thousandths of a stroke.
  * EVPI naive vs truth: hole 1 0.0087 vs 0.0077, hole 16 0.0138 vs 0.0142, hole 5 0.0041 vs 0.0035 (+0 to +17%). The cross-fitted value is 0.0074 / 0.0125 / 0.0021.
  * **The binomial SE dominates.** At S=96 the SE of P(best) is about 0.05. Report P(best) to the nearest 5-10%, with that SE.
  * **Recommendation:** keep half-sample EVs (free) and report EVPI as a [cross-fit, naive] bracket and P(best) as cross-fitted or deconvolved. The patch does both. Re-check the noise share if N is ever lowered or CRN is broken.

## 3. Prior

Compared with `research.md`, here is what is mis-centred, missing or wrongly independent. They are ordered by how much they can move the pick.

1. **Width centre.** Median 70 yd vs the research's 80-85 yd (σ≈21). The prior is a deliberate compromise, but the break-evens sit right inside the gap:
   * Holes 1 and 16 flip at ~70.
   * 4, 5, 6 and 9B flip at ~72-73 in run-96's 4-draw predecessor.
   * 18 flips at ~77, 14 at ~78, 2B at ~79, 10 at ~82 and 2F at ~84.

   Either centre it on 82 (prior_patch's median 82, 90% 72-94), or better, fit it to the player's own fairway% and >40-yd miss rate. Under the patched baseline and W=84, holes 1, 4, 5, 6, 16 and 18 all go to the 4-wood (table S).
2. **Club-to-club width ratios have zero variance.** The common multiplier keeps driver:2-wood:4-wood at exactly 1 : 0.92 : 0.77. Yet `research.md` says amateurs hit 3-wood only ~1.5% more fairways, and only 28% of players are 20+ yd narrower with it. The ratio is the decision variable. Give it a prior; the patch uses LN(0.94, 0.04) for 2w/D and LN(0.85, 0.06) for 4w/D.
3. **Scoring table.** decision.py never sets `HCP_BASELINE`, so a 5 handicap is scored with PGA Tour expected strokes. `research.md` recommends the 5-hcp curve (rough gap 0.7x, trees 1.3x). This flips 9F and moves margins by up to 0.02. Put it in the prior as a mixture, or simply use HCP.
4. **Independent carry offsets.** Driver N(0,5) and the woods N(0,4) independently. In reality a common factor (swing speed, temperature, altitude, wind, firmness) moves all clubs together. Independence gives the driver-to-4-wood gap an SD of 6.4 yd, which is too much, and the common level an SD of only ~3 yd, which is too little. Use common N(0,6) plus club-specific N(0,3).
5. **Carry and roll should correlate.** Firm, dry and downwind days raise both carry and roll. Draw a common "conditions" factor driving both. Better still, see the next point.
6. **Wind and firmness are observable on the day. Do not integrate them out.** Condition the card on them: "into wind / firm: 4-wood on 1, 16, 18". The value of doing that is EVPPI on wind, which the current setup can't show.
7. **Depth dispersion is too tight.** The carry SD is depth/4 = 7 yd for the driver. Research suggests 15-20 yd total for amateurs, including the short-miss skew. The mishit model (10-20% of swings carrying 92-97%, with the same lateral) shortens mean carry by only ~0.8%. The published P-avg vs all-drives gap (~261 vs ~244) implies ~7%. Big mishits (tops, 20-40% short) are absent. Depth matters exactly on the holes decided by cross-hazards: 8 (bunker 270-290), 11 (creek 286-292) and 13 (pots 280-300). Add a depth multiplier and a small heavy-short component (e.g. 3-5% at 60-80% carry).
8. **Roll is deterministic and the rough-roll share is fixed.** Every swing of a club gets the same roll, times one factor per draw, and `ROUGH_ROLL`=0.3 is never varied. P(roll into the hole-11 creek) is then driven by carry alone. Add swing-level roll noise (SD ~5-8 yd) and a prior U(0.15, 0.5) on rough roll.
9. **Lateral bias and skew.** A known bias doesn't matter, since the aim absorbs it. An unknown symmetric bias, integrated out, behaves like extra width. Asymmetry (slice-heavy tails) does matter. research.md's 23/24% L/R split supports symmetry for an average 5 handicap, but use the player's own split if available. RHO (correlation between lateral miss and carry) is 0 in decision.py. Run a ±0.3 sensitivity as analysis.py does, or put a prior on it.
10. **Lost-ball share is U(0.35, 0.65), with no published support.** Fine as stated, but research.md suggests grading by depth into the native. This matters less than the *rule* used to price a lost ball (section 4).
11. **The map jitter moves every polygon independently by 2.5 yd RMS.** That opens gaps and overlaps between adjacent zones (fairway vs native). Moving the whole hole together plus a small per-edge jitter would be more realistic. It is second order.

## 4. Model structure

**Table S.** Pick (gap to next club, in strokes) at the prior-mean world, all holes, N=6000 fixed swings, no map jitter. Source: `structural.py`.

| Hole | as-is | lost ball = S&D | 5-hcp table | both | both + W=84 |
|---|---|---|---|---|---|
| 1 | Driver (0.005) | **4-wood** (0.008) | Driver (0.025) | Driver (0.019) | **4-wood** (0.001) |
| 2B | Driver (0.031) | Driver (0.017) | Driver (0.043) | Driver (0.034) | Driver (0.014) |
| 2F | Driver (0.072) | Driver (0.071) | Driver (0.090) | Driver (0.092) | Driver (0.072) |
| 4 | Driver (0.026) | **4-wood** (0.045) | Driver (0.012) | **4-wood** (0.028) | **4-wood** (0.042) |
| 5 | Driver (0.012) | Driver (0.007) | Driver (0.025) | Driver (0.023) | **4-wood** (0.002) |
| 6 | Driver (0.014) | **4-wood** (0.010) | Driver (0.025) | Driver (0.012) | **4-wood** (0.039) |
| 8 | 4-wood (0.081) | 4-wood (0.095) | 4-wood (0.087) | 4-wood (0.095) | 4-wood (0.112) |
| 9B | Driver (0.012) | Driver (0.013) | Driver (0.017) | Driver (0.017) | Driver (0.011) |
| 9F | 2-wood (0.001) | 2-wood (0.001) | **4-wood** (0.004) | **4-wood** (0.004) | **4-wood** (0.011) |
| 10 | Driver (0.058) | Driver (0.058) | Driver (0.074) | Driver (0.076) | Driver (0.050) |
| 11 | 4-wood (0.144) | 4-wood (0.150) | 4-wood (0.190) | 4-wood (0.179) | 4-wood (0.188) |
| 13 | 4-wood (0.028) | 4-wood (0.028) | 4-wood (0.023) | 4-wood (0.021) | 4-wood (0.039) |
| 14 | Driver (0.023) | Driver (0.022) | Driver (0.042) | Driver (0.041) | Driver (0.025) |
| 16 | Driver (0.000) | **4-wood** (0.014) | Driver (0.013) | Driver (0.004) | **4-wood** (0.025) |
| 17 | Driver (0.071) | Driver (0.070) | Driver (0.089) | Driver (0.089) | Driver (0.075) |
| 18 | Driver (0.046) | **4-wood** (0.005) | Driver (0.047) | Driver (0.016) | **4-wood** (0.006) |

Robust picks under every variant: 2B, 2F, 10, 14 and 17 (Driver), and 8, 11 and 13 (4-wood). Everything else depends on structural choices, not on Monte Carlo error.

* **Native = 50% lost + 50% recovery.** The *lost* half is mispriced. `_expected_strokes("native")` uses `1 + rough(d)`, which is a lateral-relief drop. A ball lost outside a penalty area is stroke-and-distance: re-tee hitting 3, ≈ 1 + E_tee(hole). Under Model Local Rule E-5 it is 2 strokes plus a fairway drop. Both are ≈ the code's own `ob` = 2 + rough(d). Example: lost at 150 yd in, on a 420-yd hole. The model gives SG ≈ −1.2; the correct value is ≈ −2.0, which is Broadie's figure as quoted in research.md section 4. Fix: `baseline_patch.py`. It prices lost balls as OB unless `NATIVE_IS_PENALTY_AREA` is set. **Check the course's staking**: if the native is red-staked, the original is right. This is a fact to look up, not a parameter to integrate over.
* **Water = rough + 1.** Correct for a lateral penalty-area drop near the entry point. For a creek *crossing* the fairway (11, 9B), back-on-the-line relief is about the same distance from the green, so it is fine.
* **OB = water + 1 (2 + rough).** Approximately E-5 / stroke-and-distance. Consistent with research.md.
* **Trees as recovery baseline, with a `TREE_SEVERITY` mixture.** Reasonable. Broadie's recovery baseline already includes the chip-out.
* **HCP_BASELINE inconsistencies (minor).**
  * The lie multiplier is applied to (lie − fairway). For native, that also scales the penalty stroke by 1.3.
  * Water and OB use the tour rough gap (×1.0) while a real rough lie gets ×0.7.
  * For partial `TREE_SEVERITY`, the rough part of a tree ball gets 1.3.

  `baseline_patch` keeps penalty strokes unscaled and applies each multiplier to its own playing lie.
* **The fairway offset is a uniform shift.** It doesn't change rankings except through the slope term (+0.001/yd), which adds ~0.03 per 30 yd of driver distance. That favours driver. Fine.
* **Straight-line distance to the green** ignores doglegs and trees between the ball and the green (e.g. corner holes). This is a known optimistic bias for the long club on doglegs.
* **Normal lateral, with the app's width as the 95% window (σ = W/4).** Defensible: research.md shows a normal with σ≈21 matches fairway%, >40-yd% and within-30% together, and argues against t(5). The problem is the *value* of W (70 vs 82-85), not the shape. Two refinements:
  * Lateral SD in yards should scale with carry (it is angular), so a carry offset should widen the pattern proportionally. This is small.
  * Mishits should widen the lateral spread (heel/toe curvature), not keep it.
* **Calibration check fails.** `experiment.py` part D: driver at aim 0, prior-mean world.

  | Driver width | Mean fairway % | Penalty-equivalent rate | Dead rate (water/OB/native/trees) |
  |---|---|---|---|
  | 70 | 71% (75% excluding 11) | 10% (≈5% excluding 11) | 17% |
  | 84 | 64% | 12% | 21% |

  Published 5-hcp figures: 49% fairways, 1-3% tee-shot penalties, ~12% penalty-or-recovery (Arccos). The fairway share is too high even at W=84, so the traced fairway polygons are probably too wide (likely including first cut, given the winter imagery note in course.py). The penalty and dead rates are high: the native polygons and/or a 50% loss rate are generous. Both biases distort the picks: wide fairways make dispersion cheap, and heavy native makes it expensive. Fix the map against the app or an on-course walk, and use this check as a gate before trusting any margin below ~0.03.
* **The 70-yd DECADE corridor rule in this model** (`corridor.py`, stylised: two-sided dead zones, centred aim):
  * At C=70 the driver goes dead on 3.1% / 4.6% / 9.6% of swings for W = 65 / 70 / 84.
  * Take the model's 4-wood as 0.77x as wide and 30 yd shorter. Price 30 yd at 0.08-0.12 strokes and a dead ball at 0.8-1.3 strokes. Then clubbing down pays only when the dead-zone corridor is narrower than about 35-65 yd (W=65-70), or 45-72 yd (W=84).
  * With the 2-wood (0.92x as wide) it *never* pays on corridor width alone.

  So the model reproduces DECADE's ~70-yd rule only for an amateur-width pattern and harsh dead-ball pricing. That is another reason the W centre and the lost-ball price matter. The model's 4-wood picks on 8, 11 and 13 are *depth* decisions (driver reaches the hazard), which the corridor rule doesn't cover. There, the too-tight depth SD (section 3, point 7) matters.

## 5. EVPI and break-evens

* **EVPI = E_θ[ES(d* | θ) − min_d ES(d | θ)].** The definition and computation are correct, and the noise bias is ≤0.001 at N=3000 (section 2). Run-96 totals about 0.086 strokes/round. The interpretation needs care:
  * It is the value of *perfect* information on the 9 prior parameters, including the exact map. Data you can actually collect is worth less.
  * The useful version is **EVPPI per parameter group**, for example "how much is knowing my true driver width worth?". It can be computed from the same draws by regressing per-draw ES differences on that parameter (Strong-Oakley non-parametric EVPPI). It is cheap and would tell the player whether a launch-monitor session or Arccos data is worth it.
  * It says nothing about **structural uncertainty** (lost-ball rule, scoring table, map calibration). Table S shows that uncertainty is ~10x larger. "Small EVPI = robust" is true only *within the model*.
* **Break-even driver width.** decision.py varies driver width alone, with the woods at centre width (70x their ratios), other inputs at their prior means, no map jitter, and fixed N=6000 swings.
  * **It is the wrong conditional for the question "how wide can I be?".** The prior moves all widths together, so the relevant sweep is the *common* multiplier. Driver-only is really a sweep on the driver/wood width ratio. They agree on holes 1 and 16 (70.3 vs 70.6, 70.6 vs 71.7) but not on hole 5: driver-only flips Driver→2-wood at 73.5, while common flips Driver→4-wood at 79.5. Report both (`decision_stats.width_sweep(h, mode="common")`), labelled as "my whole game is wider" vs "my driver is wider than my woods".
  * **It is a plug-in, not integrated.** It uses ES at E[θ] rather than E[ES | width]. With nonlinear carry/hazard interactions the two differ. Integrated version: bin the existing S draws by width, or regress d_s on width (free).
  * **Bug.** In the driver-only sweep, `apply(th)` also scales `t.IRONS` by the swept width (`apply` now scales irons), so on holes 11 and 13 the irons widen with the driver while the woods are held. Hold the irons at centre width (done in the patch).
* **The docstring promises an aim refinement step ("then refined") that is not in the code.** It doesn't matter: the EV curves are flat near the optimum. Either fix the docstring or set `REFINE`.

---

## Prioritised fixes

1. **Price a lost ball in native as stroke-and-distance (or confirm the native is a penalty area).** Location: `tee_strategy._expected_strokes`, the `native` branch. Patch: `baseline_patch.py`, tested; `install()` monkeypatches it. This flips 5 of 16 picks at the mean world.
2. **Re-centre and widen the prior.** Location: `decision.prior_draws` / `apply`. Patch: `prior_patch.py`, tested. Changes:
   * width median ~82, or fitted to the player's data
   * uncertain width ratios
   * common plus club-specific carry
   * depth multiplier and rough-roll share
   * 5-hcp scoring table (or a mixture)
   * S=128
3. **Report decisions honestly.** Location: `decision.main()` per-hole block. Patch: `decision_stats.py`, tested; `ev_grid_halves` + `summarize`. Changes:
   * an indifference band, so ties are called ties (1, 9F and 16 now; 5, 6 and 9B nearly)
   * the error budget and cross-fitted margin
   * the EVPI bracket
   * cross-fitted or deconvolved P(best), plus P(pick beats runner at the posterior aims)
   * a power-of-2 S
4. **Calibration gate.** Compare model fairway%, penalty and recovery rates per drive against research.md (49%, 1-3%, ~12%) or the player's data, and re-trace fairway and native edges where it misses. Use `experiment.py` part D as the template.
5. **Break-evens.** Add the common-scale sweep, an integrated (binned-draw) version and EVPPI for width. Fix the irons-width bug in the driver-only sweep (`decision.py` lines ~186-196).
6. **Depth and roll noise.** Add a short-miss tail, per-swing roll noise and swing-to-swing RHO uncertainty in `tee_strategy.simulate`. Re-check 8, 11 and 13.
7. **Condition on day-of observables** (wind, firmness) rather than integrating them out. Produce a small conditional card.
8. **Cosmetic.** Rename "posterior" to "prior-expected" until data is used. Make the docstring match the code (S, refinement). Add tests for decision.py (none exist in `tests/`).
