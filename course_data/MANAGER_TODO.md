# Manager to-do (read and update at every check-in)

Pending actions the coordinator owes; remove an item when done, with the commit or run that closed it.

- [x] Overpass recovered; all 7 truth packages committed (runs 41349576884 / 41350092898); truth agent resumed on them 2026-11-02 00:30Z.
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
- [ ] National index full run 41355553763 (1-degree cells, 6 jobs): when it lands, read us_readiness.json
      partial_states; if any, push course_data/requests/national_index_us_cells2.json with
      {"states": [], "reuse_run": 41355553763, "oga_run": <that run id>, "rev": n} until empty. Check Spirit Hollow KS,
      Blue Hills MO, Eagle Knoll MO come out tier A/B. Then fill ROADMAP "national OSM coverage".
- [ ] Error budget follow-ups running: long-grass threshold fix agent, tee box + tree edge agent. When both land,
      re-run course_data/platform/error_budget.py and update ROADMAP "Where we are".
- [ ] QA checker agent writes course_data/library/<slug>/qa_rebuild.md per rebuilt reviewed course; publish the PUBLISH ones (hole-by-hole check of screenshots first) and tell the user. Gustin landed first.
- [ ] Native-grass classifier agent running (long grass stays off until it beats 'none' in LOCO error budget).
