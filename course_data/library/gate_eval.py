"""How good is the confidence gate? Score each blind gate build (course_data/library/gate/gate_<slug>/) against the
hand-checked truth of that course, and compare with the page's status.

  python3 course_data/library/gate_eval.py [--n 8000] [--only blue_hills,ellis]
  -> course_data/library/gate/gate_eval.json + GATE.md

Truth, per course:
  holes_truth courses (Blue Hills, Eagle Knoll, Gateway, National KC, Pine Dunes, Hot Springs Arlington):
      courses/score_auto.py: routing, par, greens, tees per set, corridor IoU, and the product's quick decision on
      the blind package vs on the truth package (truth tees + greens + hand corridor zones), n swings
  scoreboard courses (Spirit Hollow, Mozingo Lake, Veenker, Coldwater, Ellis): qa/scoreboard.py score_course on the
      blind package (Spirit Hollow: final_decision.json; Mozingo: the hand map; Veenker / Coldwater / Ellis: the
      hand corridor maps in the blind package)
A course "matches truth" when every scored tee shot is the same club or a tie, and (where scored) every hole is
routed to the right green with the right par. Hole level: is a wrong pick more likely on a CHECK hole?
"""
import argparse
import copy
import datetime as dt
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
GATE = os.path.join(HERE, "gate")
sys.path[:0] = [os.path.join(CD, "courses"), os.path.join(CD, "qa"), os.path.join(CD, "product"),
                os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")]

SCORE_AUTO = {"blue_hills": "Black", "eagle_knoll": "Back", "gateway_national": "Back", "national_kc": "Black",
              "pine_dunes": "Gold", "hot_springs_arlington": "Gold"}
SCOREBOARD = ["spirit_hollow", "mozingo_lake", "veenker", "coldwater", "ellis"]


def rj(p, d=None):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return d


def ref_of(k):
    return str(k).rstrip("BF")


def score_one(slug, n):
    gd = os.path.join(GATE, "gate_" + slug)
    st = rj(os.path.join(gd, "status.json"))
    pkg = os.path.join(gd, "package.json")
    if not st:
        return dict(slug=slug, status="not built")
    if not os.path.exists(pkg):
        return dict(slug=slug, status=st.get("status"), reasons=st.get("reasons"), error="no package")
    out = dict(slug=slug, status=st["status"], check_holes=[str(h) for h in st.get("check_holes") or []],
               reasons=st.get("reasons"), solved=st.get("solved_sets"))
    qa = rj(os.path.join(gd, "qa.json")) or {}
    out["hole_status"] = {r: h["status"] for r, h in ((qa.get("checks") or {}).get("auto") or {}).get("holes", {}).items()}
    try:
        if slug in SCORE_AUTO:
            import score_auto as SA
            o = SA.score(slug, pkg, "gate", n=n, tees=SCORE_AUTO[slug], out_dir=gd)
            S = o["summary"]
            rows = [dict(hole=r["hole"], same=r.get("same"), same_or_tie=r.get("same_or_tie"), regret=r.get("regret"),
                         routing=r.get("routing"), par_ok=r.get("par_ok"), pick=r.get("pick_auto"), truth=r.get("pick_truth"))
                    for r in o["rows"]]
            out.update(tees=SCORE_AUTO[slug], truth="score_auto (holes_truth + hand corridors)",
                       routing_ok=S["routing_ok"], par_ok=S["par_ok"], holes=S["holes"], tee_shots=S["tee_shots"],
                       same=S["same_club"], same_or_tie=S["same_or_tie"], regret=S["regret"],
                       tees_within_10=f"{S['tees_within_10']}/{S['tees_scored']}", iou=S["iou_mean"])
        else:
            import scoreboard as SB
            import tee_strategy as t
            if SB.HAND_HOLES is None:
                SB.HAND_HOLES = copy.deepcopy(t.HOLES)
            cfg = dict(next(c for c in SB.COURSES if c["slug"] == slug))
            cfg["package"] = os.path.relpath(pkg, ROOT)
            pk = rj(pkg) or {}
            if cfg["tees"] not in (pk.get("tee_sets") or {}):
                out["tee_note"] = f"{cfg['tees']} not on the blind package's card; scored its own set {pk.get('tee_set')}"
                cfg["tees"] = pk.get("tee_set")
            a = types.SimpleNamespace(n=n, workers=None, from_out=False, holes=None, no_hand_quick=True, full=False,
                                      dry_run=False, full_S=64, full_N=3000)
            o = SB.score_course(cfg, a, {})
            S = o["summary"]
            rows = [dict(hole=ref_of(r["hole"]), key=r["hole"], same=r.get("same"), same_or_tie=r.get("same_or_tie"),
                         regret=r.get("regret"), pick=r.get("pick"), truth=r.get("truth")) for r in o["holes"] if "same" in r]
            out.update(tees=cfg["tees"], truth=o.get("truth"), tee_shots=S.get("n_truth"), same=S.get("same"),
                       same_or_tie=S.get("same_or_tie"),
                       regret=round(sum(r["regret"] or 0 for r in rows), 3) if rows else None,
                       tees_within_10=(f"{S['tee10']}/{S['n_geo']}" if "tee10" in S else None),
                       iou={k: v["mean"] for k, v in (S.get("iou") or {}).items()})
            json.dump(o, open(os.path.join(gd, "score_gate.json"), "w"), indent=1, default=float)
        out["rows"] = rows
        scored = [r for r in rows if r.get("same_or_tie") is not None]
        route_ok = all(r.get("routing", "ok") == "ok" and r.get("par_ok", True) is not False for r in rows)
        out["match"] = bool(scored) and all(r["same_or_tie"] for r in scored) and route_ok
    except (Exception, SystemExit) as e:                         # noqa: BLE001
        import traceback
        out["error"] = f"{type(e).__name__}: {e}"
        out["trace"] = traceback.format_exc()[-1500:]
    return out


def md(res):
    L = ["# Confidence gate vs the hand-checked courses", "",
         f"Built {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M}Z by `course_data/library/gate_eval.py`. Each course was "
         "built blind by the course-page workflow (`course_data/requests/course_page_gate_<slug>.json`: name, town, state, "
         "the hand-checked tee set; the same disambiguation the earlier blind requests used) and scored against its "
         "hand truth. **match** = every scored tee shot is the same club or a tie, and every hole routed to the right "
         "green with the right par where the truth scores routing.", "",
         "| course | gate status | CHECK holes | reasons | tees | same / same-or-tie | regret | routing / par | match |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        if r.get("status") in (None, "not built"):
            L.append(f"| {r['slug']} | not built | | | | | | | |")
            continue
        so = f"{r.get('same')}/{r.get('tee_shots')}, {r.get('same_or_tie')}/{r.get('tee_shots')}" if r.get("tee_shots") else "-"
        rp = f"{r.get('routing_ok')}/{r.get('holes')}, {r.get('par_ok')}/{r.get('holes')}" if r.get("holes") else "n/a"
        L.append(f"| {r['slug']} | {r['status']} | {', '.join(r.get('check_holes') or []) or '-'} | "
                 f"{'; '.join(r.get('reasons') or [])[:220]} | {r.get('tees', '')} | {so} | {r.get('regret')} | {rp} | "
                 f"{'yes' if r.get('match') else 'no' if 'match' in r else 'error: ' + str(r.get('error'))[:80]} |")
    ok = [r for r in res if r.get("status") == "auto-OK" and "match" in r]
    nc = [r for r in res if r.get("status") == "needs confirm" and "match" in r]
    L += ["", f"* auto-OK courses: {len(ok)}; of them match truth: {sum(r['match'] for r in ok)}",
          f"* needs-confirm courses: {len(nc)}; of them match truth anyway: {sum(r['match'] for r in nc)}"]
    # hole level
    hp = dict(pass_n=0, pass_wrong=0, check_n=0, check_wrong=0)
    for r in res:
        hs = r.get("hole_status") or {}
        for row in r.get("rows") or []:
            if row.get("same_or_tie") is None:
                continue
            s = hs.get(str(row["hole"]))
            if s is None:
                continue
            k = "pass" if s == "PASS" else "check"
            hp[k + "_n"] += 1
            hp[k + "_wrong"] += 0 if row["same_or_tie"] else 1
    L += [f"* tee shots on PASS holes: {hp['pass_n']}, wrong club (not same or tie) {hp['pass_wrong']}; "
          f"on CHECK holes: {hp['check_n']}, wrong {hp['check_wrong']}", ""]
    cc = {"PASS": [0, 0], "CHECK": [0, 0]}
    for r in res:
        if not r.get("rows") or "scorecard not matched" in " ".join(r.get("reasons") or []):
            continue
        hs = r.get("hole_status") or {}
        for x in r["rows"]:
            if x.get("same_or_tie") is None or str(x["hole"]) not in hs:
                continue
            k = hs[str(x["hole"])]
            cc[k][0] += 1
            cc[k][1] += 0 if x["same_or_tie"] else 1
    L += [f"* courses with a web card only: PASS holes {cc['PASS'][0]} tee shots, {cc['PASS'][1]} wrong club; CHECK holes "
          f"{cc['CHECK'][0]}, {cc['CHECK'][1]} wrong. Pine Dunes: no build (Overpass timed out in all three runs).", ""]
    # which check carries the signal (main solved base = the scored set), and looser course thresholds
    kind = {}
    rows_c = []
    for r in res:
        if not r.get("rows"):
            continue
        qa = rj(os.path.join(GATE, "gate_" + r["slug"], "qa.json")) or {}
        ch = (((qa.get("checks") or {}).get("auto")) or {}).get("holes", {})
        structural = [x for x in (r.get("reasons") or []) if "hole(s) with a CHECK" not in x]
        rows_c.append((r, structural, len(r.get("check_holes") or [])))
        for row in r["rows"]:
            h = ch.get(str(row["hole"]))
            if row.get("same_or_tie") is None or not h:
                continue
            for k in {x.split(":")[0] for x in h["reasons"]} or {"(none: PASS)"}:
                a = kind.setdefault(k, [0, 0])
                a[0] += 1
                a[1] += 0 if row["same_or_tie"] else 1
    L += ["Wrong tee-shot club (not the same club, not a tie) by failed check, on the scored set:", "",
          "| check failed | tee shots | wrong club |", "|---|---|---|"]
    L += [f"| {k} | {v[0]} | {v[1]} ({100 * v[1] / max(v[0], 1):.0f}%) |" for k, v in sorted(kind.items())]
    L += ["", "Looser course thresholds (sensitivity, same courses): OSM holes + card matched + page clean, and at most "
          "K holes with a CHECK (the CHECK holes are then the golfer's confirm list):", "",
          "| K | courses passing | of them match truth |", "|---|---|---|"]
    for K in (0, 2, 3, 5):
        ok_ = [r for r, st, n in rows_c if not st and n <= K]
        L.append(f"| {K} | {len(ok_)} ({', '.join(r['slug'] for r in ok_) or '-'}) | {sum(bool(r.get('match')) for r in ok_)} |")
    L.append("")
    return "\n".join(L) + "\n", dict(auto_ok=len(ok), auto_ok_match=sum(r["match"] for r in ok), needs_confirm=len(nc),
                                     needs_confirm_match=sum(r["match"] for r in nc), holes=hp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--only")
    a = ap.parse_args()
    want = a.only.split(",") if a.only else list(SCORE_AUTO) + SCOREBOARD
    prev = {r["slug"]: r for r in (rj(os.path.join(GATE, "gate_eval.json")) or {}).get("courses", [])}
    for s in want:
        print("==", s, flush=True)
        prev[s] = score_one(s, a.n)
        print(json.dumps({k: v for k, v in prev[s].items() if k not in ("rows", "trace", "hole_status")}, default=float))
    order = list(SCORE_AUTO) + SCOREBOARD
    res = [prev[s] for s in order if s in prev]
    text, summ = md(res)
    json.dump(dict(courses=res, summary=summ), open(os.path.join(GATE, "gate_eval.json"), "w"), indent=1, default=float)
    open(os.path.join(GATE, "GATE.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
