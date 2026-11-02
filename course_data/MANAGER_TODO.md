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
- [ ] Gustin NEEDS FIX was the consensus set-order bug (fixed, card_consensus.py); re-queue gustin with the next batch of NEEDS FIX courses from the QA checker.
- [x] St Andrews published 2026-11-02: https://claude.ai/artifact/K4HKE8bS5usJqTPdYdarkz (QA PUBLISH + coordinator montage check).
- [ ] ~25 reviewed courses still queued in runs 41346643978 / 41346747941: when they land, launch a QA checker agent again (same brief as qa_rebuild.md) and publish PUBLISH verdicts.
- [ ] Aim grid ±40 yd edge: several calm picks sit exactly on the edge (Gustin 6 Gold, St Andrews 5, 15). Check whether the aim range caps picks in decide; widen or make it dogleg-aware if so (agent).
- [ ] National index pass 1 landed (run 41355553763): only AL FL GA HI LA MS TX reached half their cells (1,486 courses: 35 % tier A, 37.5 % complete OSM holes, 67 % any OSM golf). Pass 2 queued (national_index_us_cells2.json, reuse_run). Repeat until partial/missing states are empty; then fill ROADMAP coverage.
- [ ] Finish-error agent: Gamble Sands opaque finish failure + record real errors in status.json; re-queues gamble_sands + gustin.
- [ ] Long grass: Sentinel-2 seasonal model is the best so far (LOCO IoU 0.23–0.28, 0.54 precision) but beats 'none' by 1 hole on 7 courses, loses 1 on 11, fails Annbriar (green prairie) and Amana (drought-browned rough). NOT adopted (coordinator decision 2026-11-02). Next when capacity frees: course-level drought gate (compare to the course's own unirrigated areas / regional drought index), hole-window clipping, more prairie/links native truth (pick 3–4 links-style courses for truth set v2), then re-test; consider golfer extent tap as the product path.
- [ ] 04:25Z check-in: 20 reviewed courses rebuilt -> QA agent on 16 (verdicts in qa_rebuild.md); publish PUBLISH ones. Retry batch course_batch_retry_overpass.json (TCI, TPC Deere Run, Hodge Park, Kapalua, Queenstown, TPC Louisiana, Troon North, World Woods). Keller still not_found: fix its request (osm id) before retrying. National pass 2: 2,702 courses in 11 states (37 % complete holes, 69 % any OSM); pass 3 queued (national_index_us_cells3.json).
- [x] Published 2026-11-02 (QA PUBLISH + coordinator montage spot-check): buffalo_ridge TucBpmpP5LRf6yXt2rmRwQ, drumm_farm Wx6FuBvUaK3tkotjyLe5Zq, eagle_bend 3w3LTasgmEfkJRVNAXK2ar, falcon_ridge 4LZuNeLu9nV13SMAjAPSqz, la_nickell KR1WDRrJSpZV9HgKv2UPzp, old_kinderhook 8nMaobVLAd46Q1etxEQEWR, osage_national Bg613RyjLYYZYuGV8io7qA, pevely_farms Xb71X7fuwmyMjRvDF235S9, rivercut 2cM1de43UZXoAcAvsu9bQv (all https://claude.ai/artifact/<id>). Republish each when it is rebuilt with long grass / agent-mapper layers.
- [ ] QA-fix agent running (6 NEEDS FIX + Swope PDF); mapper-tooling agent running; native-grass agent (Will's 6 KS courses) running; vision-in-every-build agent running; tap-policy dev agent running.
- [ ] QA fixes landed in code; rebuild run 41392580512 (the_falls_ofallon, weaver_ridge, gustin, sycamore_ridge, creekmoor, colbert_hills, swope_memorial with 2026 card): when it lands, QA (qa_rebuild.md) and publish passes. Open pipeline item: capped walk-back ending in front of a shorter set's tee should fall back to that box (Weaver 5 pinned by hand).
- [ ] Blind mapper evaluation: 5 mapper agents running (gateway_national Back, coldwater Blue, blue_hills Black, pine_dunes Gold, ellis Blue). When all land: python3 course_data/mapper/eval_mapper.py --courses gateway_national,coldwater,blue_hills,pine_dunes,ellis; write course_data/mapper/EVAL_BLIND.md; decide whether the mapper goes into the product flow.
- [ ] 06:25Z: hodge_park + dubs_dread rebuilt -> include in next QA with the 7 from run 41392580512. National pass 3: 4,228 courses / 15 states (41 % complete holes, 71 % any OSM); pass 4 queued. Blind mapper eval done (pooled regret -21 %, Coldwater worse): brief-refinement agent running; then fresh blind round on 3-4 new truth courses + Coldwater redo.
- [ ] Vision layer in every build: shipped (shared build_layers.py + vision-layers action, loud gate). After the round-2 blind mappers land (annbriar/buffalo_ridge use the current packages), bump package requests to get vision_any/2 for tomahawk_hills, buffalo_ridge, gustin, amana_colonies, osage_national, annbriar (+ check la_nickell/rivercut re-request landed with vision_any/2). The 6 Kansas native courses + buffalo_dunes also need vision_any/2 (coordinate with the native-grass agent).
- [ ] Mapper adopted: run a mapper agent (BRIEF.md) for each library course before its next rebuild; add "agent_layers" to its course_page request; priority: native/prairie courses (eagle_bend, Will's 6 KS courses once their packages have vision_any/2), then the published 10. Next brief iteration: raise long-grass recall on thin bands without breaking parkland.
- [ ] 08:30Z: 6 courses failed again on Overpass timeouts (TCI, Kapalua, Queenstown, TPC Louisiana, Troon North, World Woods) — likely Overpass load from the national index passes; re-queue them only after the national index is complete. National pass 4: 5,020 courses (42 % complete holes, 72 % any OSM), 31 states missing; pass 5 queued.
