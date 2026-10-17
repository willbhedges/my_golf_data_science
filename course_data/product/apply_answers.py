"""Apply the golfer's review answers (the review page's "Copy answers" JSON) to the course package, then re-plan
only the holes whose geometry changed.

  python3 course_data/product/apply_answers.py answers.json            # or '-' for stdin, or the JSON itself
      [--review course_data/packages/<slug>/out/review/review.json]    # default: from the answers' slug
      [--package-out <path>]  (default: the package in place)  [--no-replan]  [--plan-out <dir>]

What each answer does (items and frames come from review.json, so the page never needs geometry):
  tee     confirm  tees[set].verified = "golfer", confidence 1.0
          moved    tees[set].tee_ll moved dx yds right / dy yds forward in the review's frame for that hole
                   (aim_ll re-derived by platform/tee_line.py), method "golfer", confidence 1.0; hole-level tee_ll
                   too when it is the package's tee set
  hazard  confirm  the group's zones_ll get verified = "golfer", p = 1.0 (verify.py stops asking)
          absent   the group's zones_ll are deleted
          moved    the group is translated `shift` yds toward the fairway (sideways, or along the line for a
                   hazard across it), then verified
  gap     present  a "recovery" polygon over the tested strip is added (src golfer:gap)
          confirm  hole.verification.open_<side> = true (verify.py stops asking)
  check   playable / not_playable is recorded in hole.verification (the plan's guard still prints the CHECK)
Every answer is also recorded under hole["verification"][item id] and package["verification"]. Zone indices
are checked against review.json's fingerprints (first vertex); a mismatch (package rebuilt since the review)
skips that item with a warning.

Re-plan: decide.quick_hole (the quick plan, N = 8000, same seeds) for the changed holes only; their entries in
<plan out>/decision.json and plan.json picks are replaced and <plan out>/replan.json lists before -> after.
The book PDFs and the wind page are not rebuilt here (commit a plan request for that).
"""
import argparse
import copy
import datetime as dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import package as PK                                # noqa: E402
import render as R                                  # noqa: E402

GEOM = ("moved", "absent", "present")


def _read_answers(arg):
    if arg == "-":
        return json.load(sys.stdin)
    if os.path.exists(arg):
        return json.load(open(arg))
    return json.loads(arg)


def _to_yd(fr, poly):
    q = fr.ll_to_yds(np.array(poly, float)[:, :2])
    return np.c_[q[:, 0], -q[:, 1]]


def _to_ll(fr, xa):
    xa = np.asarray(xa, float)
    return fr.yds_to_ll(np.c_[xa[:, 0], -xa[:, 1]]).tolist()


def _fp_ok(z, fp):
    p = z.get("poly") or []
    return bool(p) and abs(float(p[0][0]) - fp[0]) < 1e-6 and abs(float(p[0][1]) - fp[1]) < 1e-6


def apply(pkg, review, answers, log=print):
    """-> (new package dict, {hole ref: [item ids that changed geometry]}, warnings)."""
    pkg = copy.deepcopy(pkg)
    tee_set = review["tee_set"]
    items = {it["id"]: it for it in review["items"]}
    changed, warn = {}, []
    removals = {}
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    for a in answers.get("answers", []):
        it = items.get(a.get("id"))
        if it is None:
            warn.append(f"{a.get('id')}: not in this review")
            continue
        ref = it["hole"]
        h = pkg["holes"].get(ref)
        hv = review["holes"].get(ref) or {}
        if h is None:
            warn.append(f"{a['id']}: hole {ref} not in the package")
            continue
        ans = a.get("answer")
        rec = dict(a, at=answers.get("answered") or now, review_built=review.get("built"))
        h.setdefault("verification", {})[it["id"]] = rec
        fr = R.Frame.from_json(hv["frame"]) if hv.get("frame") else None
        if it["type"] == "tee":
            ent = _tee(h, tee_set)
            if ent is None:
                warn.append(f"{a['id']}: no {tee_set} tee entry")
                continue
            if ans == "moved" and fr is not None and (abs(a.get("dx", 0)) > 0.5 or abs(a.get("dy", 0)) > 0.5):
                new = fr.yds_to_ll([[float(a.get("dx", 0)), -float(a.get("dy", 0))]])[0].tolist()
                aim, _ = PK._tee_line_mod().aim_point(new, h.get("hole_line_ll"), PK._ll(h.get("green_ll")),
                                                      float(ent.get("card_yards") or h.get("length") or 0) or None,
                                                      int(h.get("par") or 4))
                ent.update(tee_ll=new, aim_ll=aim, method="golfer", confidence=1.0, verified="golfer",
                           moved_yds=[a.get("dx", 0), a.get("dy", 0)])
                if ent.get("measured_yards") is not None:
                    ent["measured_yards"] = round(float(ent["measured_yards"]) - float(a.get("dy", 0)), 1)
                if str(pkg.get("tee_set", "")).lower() == tee_set.lower():
                    h["tee_ll"], h["aim_ll"] = new, aim
                changed.setdefault(ref, []).append(it["id"])
            else:
                ent.update(confidence=1.0, verified="golfer")
        elif it["type"] == "hazard":
            zl = h.get("zones_ll") or []
            idx = it.get("zone_idx", [])
            fps = it.get("zone_fp", [])
            if any(i >= len(zl) or not _fp_ok(zl[i], fp) for i, fp in zip(idx, fps)):
                warn.append(f"{a['id']}: zones changed since the review (package rebuilt?): skipped")
                continue
            if ans == "absent":
                removals.setdefault(ref, set()).update(idx)
                changed.setdefault(ref, []).append(it["id"])
            elif ans == "moved" and abs(float(a.get("shift", 0))) >= 0.5 and fr is not None:
                vec = np.array(it["toward"], float) * float(a["shift"])
                for i in idx:
                    zl[i]["poly"] = _to_ll(fr, _to_yd(fr, zl[i]["poly"]) + vec)
                    zl[i].update(verified="golfer", p=1.0, moved_yds=float(a["shift"]))
                changed.setdefault(ref, []).append(it["id"])
            else:
                for i in idx:
                    zl[i].update(verified="golfer", p=1.0)
        elif it["type"] == "gap":
            if ans == "present" and fr is not None:
                h.setdefault("zones_ll", []).append(dict(lie="recovery", poly=_to_ll(fr, it["strip_xa"]),
                                                         src="golfer:gap", p=1.0, verified="golfer"))
                changed.setdefault(ref, []).append(it["id"])
            else:
                h["verification"][f"open_{it['side']}"] = True
        # check: recorded only
    for ref, idx in removals.items():
        zl = pkg["holes"][ref]["zones_ll"]
        pkg["holes"][ref]["zones_ll"] = [z for i, z in enumerate(zl) if i not in idx]
    pkg.setdefault("verification", {}).setdefault("rounds", []).append(
        dict(review_built=review.get("built"), applied=now, answers=len(answers.get("answers", [])),
             changed_holes=sorted(changed)))
    _reframe(pkg, warn)
    return pkg, changed, warn


def _tee(h, tee_set):
    for k, v in (h.get("tees") or {}).items():
        if k.lower() == tee_set.lower():
            return v
    return None


def _reframe(pkg, warn):
    """Refresh the package's yard-frame zones (platform.package.reframe), if the platform module imports."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("cdp_platform_package", os.path.join(CD, "platform", "package.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.reframe(pkg)
    except Exception as e:                                   # noqa: BLE001
        warn.append(f"reframe skipped ({type(e).__name__}: {e}); zones_ll is authoritative")


def replan(pkg_path, tee_set, refs, workers=1, n=8000, log=print):
    """Quick plan (decide.quick_hole) for the given holes of the package at pkg_path -> {ref: result}."""
    import decide
    C = PK.load(pkg_path, tee_set)
    keys = [k for k in C.holes if str(k) in {str(r) for r in refs}]
    if not keys:
        return {}
    decide.bind(C.holes)
    res = {}
    if workers > 1 and len(keys) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(workers, len(keys))) as pool:
            for k, r in pool.imap_unordered(decide._work, [("quick", k, dict(n=n)) for k in keys]):
                res[str(k)] = r
    else:
        for k in keys:
            res[str(k)] = decide._work(("quick", k, dict(n=n)))[1]
    for k, r in res.items():
        log(f"  re-planned {k}: {r['pick']} aim {r['aim']:+.1f} margin {r['margin']:.3f}")
    return res


def write_plan(plan_out, results, tee_set):
    """Replace the re-planned holes in <plan_out>/decision.json and plan.json picks; write replan.json."""
    os.makedirs(plan_out, exist_ok=True)
    dp, pp = os.path.join(plan_out, "decision.json"), os.path.join(plan_out, "plan.json")
    dec = json.load(open(dp)) if os.path.exists(dp) else {}
    before = {k: (dict(pick=dec[k]["pick"], aim=dec[k]["aim"]) if k in dec else None) for k in results}
    for k, r in results.items():
        dec[k] = r
    with open(dp, "w") as fh:
        json.dump(dec, fh, indent=1, default=float)
    if os.path.exists(pp):
        plan = json.load(open(pp))
        for k, r in results.items():
            plan.setdefault("picks", {})[k] = dict(club=r["pick"], aim=r["aim"], zone=r["zone"], margin=round(r["margin"], 4),
                                                   tie=r["tie"], conf=r.get("conf"), check=r.get("check") or [],
                                                   status="CHECK" if r.get("check") else "PLAY", replanned="golfer answers")
        with open(pp, "w") as fh:
            json.dump(plan, fh, indent=1, default=float)
    rp = dict(tee_set=tee_set, at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
              holes={k: dict(before=before[k], after=dict(pick=r["pick"], aim=r["aim"], tie=r["tie"]))
                     for k, r in results.items()})
    with open(os.path.join(plan_out, "replan.json"), "w") as fh:
        json.dump(rp, fh, indent=1)
    return rp


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("answers", help="answers JSON file, '-' for stdin, or the JSON text")
    ap.add_argument("--review")
    ap.add_argument("--package-out")
    ap.add_argument("--plan-out")
    ap.add_argument("--no-replan", action="store_true")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    ans = _read_answers(a.answers)
    review_path = a.review or os.path.join(CD, "packages", ans["slug"], "out", "review", "review.json")
    review = json.load(open(review_path))
    if ans.get("review_built") and ans["review_built"] != review.get("built"):
        print(f"! answers are for the review built {ans['review_built']}, this review is {review.get('built')}")
    pkg_path = os.path.join(ROOT, review["package"])
    pkg = json.load(open(pkg_path))
    new, changed, warn = apply(pkg, review, ans)
    out_pkg = a.package_out or pkg_path
    with open(out_pkg, "w") as fh:
        json.dump(new, fh, separators=(",", ":"))
    print(f"applied {len(ans.get('answers', []))} answers -> {os.path.relpath(out_pkg, ROOT)}; "
          f"geometry changed on holes {sorted(changed) or 'none'}")
    for w in warn:
        print("  !", w)
    if changed and not a.no_replan:
        res = replan(out_pkg, review["tee_set"], list(changed), workers=a.workers)
        plan_out = a.plan_out or os.path.join(os.path.dirname(pkg_path), "out")
        rp = write_plan(plan_out, res, review["tee_set"])
        for k, v in rp["holes"].items():
            b = v["before"] or {}
            print(f"  hole {k}: {b.get('pick', '-')} {b.get('aim', 0):+.0f} -> {v['after']['pick']} {v['after']['aim']:+.0f}")
    return new, changed


if __name__ == "__main__":
    main()
