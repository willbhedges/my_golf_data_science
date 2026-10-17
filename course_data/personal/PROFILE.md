# `golf_player/1`: the player profile

One JSON document per golfer, written by `player_profile.py` from the posterior (`bayes.py`). The app reads
`app_player` (a drop-in for the bundle's `player` block in `course_data/app/SCHEMA.md`) and shows the
uncertainty; the planner reads `draws` (64 posterior draws) in place of its 64 generic prior draws.

```jsonc
{
  "schema": "golf_player/1",
  "player": "example",
  "updated": "2026-10-17T09:00Z",
  "home_course": "spirit_hollow" | null,          // course whose emulator priced the summary stats
  "reference_club": "Driver",                      // W (the width every ratio is relative to)
  "prior": "v2" | "generic",                       // v2 = the book golfer's prior, generic = a new user
  "conventions": {"units": "yards", "lateral": "+ = right of the intended line", "temp_ref_f": 70,
                  "width95": "central 95.45 % lateral interval of a good strike (= 4 sigma when normal), on course",
                  "depth95": "carry window of a good strike (= 4 sd)", "total": "carry + roll on the home fairways"},
  "sources": [{"kind": "launch_monitor"|"on_course"|"arccos"|"summary", "file": "...", "n": 40}],
  "data": {"launch_monitor": 40, "on_course": 30, "summary": 0},
  "fit": {"ess": 1800, "method": "laplace-is" | "metropolis (acc 0.25)", "logpost_map": -1111.0},

  "clubs": {
    "Driver": {
      "stated":  {"carry": 275, "total": 300},                         // what the golfer typed (the prior centre)
      "carry":   {"median": 274.1, "mean": 274.0, "sd": 2.21, "ci90": [270.5, 277.7]},
      "total":   {...},  "roll": {...},                                // roll = (stated total - carry) x roll_mult
      "width95": {"median": 76.0, "mean": 76.3, "sd": 4.1, "ci90": [69.5, 83.2], "sd_log": 0.054},
      "depth95": {...},
      "bias":    {...},                                                 // yds, + = right; common aim/shape + club part
      "ratio_to_ref": {...},                                            // width95 / the driver's
      "n_shots": {"launch_monitor": 20, "on_course": 30},
      "source":  "data" | "summary" | "prior"                           // prior = no shots with this club: ratio x W
    },
    "4-wood": {...}, ...
  },
  "shared": {
    "nu":            {...},           // Student-t tail of the lateral (30 = near normal; 4 = heavy tails)
    "mishit_slight": {...},           // share of swings, carry 92-95 % of normal, lateral x 1.15
    "mishit_heavy":  {...},           // share of swings, carry 65-85 %, lateral x 1.5
    "roll_mult": {...}, "depth_mult": {...},
    "range_to_course": {...},         // f: on-course width / launch-monitor width (prior 1.05, sd 8 %)
    "mishit_model": {"slight": {"carry_frac": [0.92, 0.95], "lateral_x": 1.15}, "heavy": {...}},
    "not_learned": {"rho": "U(-0.1, 0.3) (v2 prior)", "kappa": "U(0, 0.16) (v2 prior)"}
  },
  "draws": {                          // 64 equally weighted posterior draws (systematic resampling)
    "n": 64, "nu": [...], "mishit_slight": [...], "mishit_heavy": [...], "roll_mult": [...], "depth_mult": [...],
    "clubs": {"Driver": {"carry": [...], "width95": [...], "bias": [...], "roll": [...], "depth95": [...]}, ...}
  },
  "app_player": {                     // = SCHEMA.md bundle "player" + width95 (posterior medians)
    "clubs": {"Driver": {"carry": 274.1, "total": 298.9, "width95": 76.0}, ...},
    "temp_carry_pct_per_f": 0.10, "temp_ref_f": 70
  },
  "spirit_hollow_picks": {            // optional: picks across the width interval (player_profile.picks_at_interval)
    "width": {"median": 76.0, "ci90": [69.5, 83.2]}, "source": "spirit_hollow/v2/output/v2_decisions.json",
    "holes": [{"hole": "5", "pick_median": "Driver", "pick_lo": "Driver", "pick_hi": "4-wood",
               "break_evens": [{"width": 79.1, "frm": "Driver", "to": "4-wood"}], "inside_ci": [79.1],
               "near": true, "p_other_club": 0.31, "plan_pick": "Driver"}, ...]
  }
}
```

## How each consumer uses it

* **App (today's page):** replace `bundle.player` with `profile.app_player`. Carry/total feed the flight and
  temperature maths exactly as now. `width95` is informational until the plan is re-run (the precomputed
  `offsets` assume the plan's widths); the app should show `clubs.Driver.width95.ci90` and, when
  `spirit_hollow_picks.holes[].inside_ci` is non-empty, mark that hole's club as "depends on your pattern".
* **Planner (backend):** `player_profile.to_v2_params(profile, i)` turns draw *i* into overrides for
  `spirit_hollow/v2/model.central` (widths per club, carry offsets, bias, mishit rates, roll and depth
  multipliers). Running `decide.bayes` over the 64 draws instead of `decide.prior_draws` gives the golfer's own
  robust club + aim. nu is not in the v2 engine (normal lateral + mishit scale mixture); with nu < 10 use the
  emulator's `HoleSim` (t lateral) or widen the mishit tail.
* **Re-fitting:** the profile is a summary, not a sufficient statistic. Keep the raw normalised shots
  (`bayes.Data`) and re-fit when new data arrive; the fit takes ~5-10 s.

## Field rules

* All distances are yards; carries are at 70°F (the app's temperature model applies on top).
* `ci90` is the 5-95 % posterior interval; `sd` is the posterior sd (for `width95` also `sd_log`).
* A club with `source: "prior"` has a width = its prior ratio x the driver's posterior width: learning the
  driver moves every club (common factor), but the ratio itself is unlearned.
* `range_to_course` is an assumption until the golfer has both launch-monitor and on-course shots; with
  launch-monitor data only, the on-course width can't be known better than ~ ±13 % (90 %).
