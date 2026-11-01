# Manager to-do (read and update at every check-in)

Pending actions the coordinator owes; remove an item when done, with the commit or run that closed it.

- [ ] Overpass was down/timing out on 2026-11-01 ~22:00Z. When it answers again (check a small web_fetch or
      a course-package run): re-push course_data/requests/package_{la_nickell,buffalo_ridge,rivercut,gustin}.json
      (run 41349576884 timed out) and, if run 41350092898 failed, package_{amana_colonies,osage_national,annbriar}.json.
      Then for each: tourn_truth request with "ob", and the 5 steps in course_data/truth_sets_v2/README.md
      (hand truth, workstream 3). adams_pointe needs its AllSquare card typed into the request first.
- [ ] Course-page retry runs 41346643978 (12 supplement courses), 41346747941 (16 commit-failed courses),
      41347851530 (17 national failures): when each finishes, read results, fix, re-queue; if they failed only on
      Overpass, re-queue after Overpass recovers. Then hole-by-hole check of reviewed courses and publish passes.
- [ ] Error-budget agent (workstream 1) and national-index agent (workstream 5) running; unmapped workstream 4: agent done (honest
      set 74 test courses, ~80 % paired); sticky re-solve agent (workstream 6) running.
- [ ] Aim Caddie: republish after the rebuilt library lands (fix review-label looseness first: St Andrews,
      Tiffany Greens shown as "OK").
- [ ] Tiffany Greens: club scorecard to settle tee names (course_data/research/web/rv_ph_tg/).
- [ ] Jayhawk Club: hand trace once its package is committed.
- [ ] Perception leakage-free re-train: runs 41353156906 (pass 1, train) then 41357754039 (pass 2, re-perceive
      212 courses). When pass 2 lands: rebuild zero_tap/bench_set.py, re-run formation hole_pairs on the new scenes
      (zt_formation), re-run the UNMAPPED.md commands; then launch: tee-candidate re-scorer (cut false tees),
      fairway-between-tee-and-green pairing term, threshold calibration that holds 98 % on new states.
