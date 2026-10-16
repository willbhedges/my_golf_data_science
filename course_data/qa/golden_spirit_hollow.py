"""Golden test: an auto-built Spirit Hollow package vs the hand-reviewed spirit_hollow/course.py.

  python3 course_data/qa/golden_spirit_hollow.py                      # oracle-tee pipeline build + every
                                                                      # Spirit Hollow package on disk
  python3 course_data/qa/golden_spirit_hollow.py --package course_data/platform/.../package.json
  python3 course_data/qa/golden_spirit_hollow.py --no-oracle --fast

Reuses course_data/acceptance.py (registration, tee/green error, landing-zone IoU, club pick) but writes
only into course_data/qa/: golden.json, golden.md, and REPORT.md (which also pulls in contracts.json
from run_qa.py and the hand-written findings.md).

Extra over acceptance.py: club-pick agreement with the published decision
(spirit_hollow/output/final_decision.json, the robust pick incl. ties) as well as with the model run on
the traced map; per-class IoU means; pass/fail per bar of ARCHITECTURE.md section 7.
"""
import argparse
import contextlib
import io
import json
import os
import sys
import time

import numpy as np

QA = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(QA)
ROOT = os.path.dirname(CD)
sys.path[:0] = [QA, CD, os.path.join(ROOT, "spirit_hollow"), os.path.join(ROOT, "mozingo")]
import acceptance as A                                   # noqa: E402
import packages as PK                                    # noqa: E402

FINAL = os.path.join(ROOT, "spirit_hollow", "output", "final_decision.json")


def package_auto(pkg):
    """{traced key: auto hole dict in acceptance's format} for a Spirit Hollow package."""
    out = {}
    for k in list(A.course.HOLES) + list(A.course.PAR3):
        q = pkg.holes.get(A.ref_of(k))
        if q is None or q.model is None:
            continue
        h = dict(q.raw) if pkg.kind == "holes.json" else dict(q.model)
        h.setdefault("length", q.length)
        h["length"] = int(round(float(h.get("length") or 0)))
        h.setdefault("par", q.par)
        if pkg.kind != "holes.json":
            h.update(q.model)
            h["length"] = int(round(float(q.length or 0)))
            h["zones"] = [(n, [list(p) for p in poly]) for n, poly in q.model["zones"]]
            h["tee"], h["dot270"], h["green"] = list(h["tee"]), list(h["dot270"]), list(h["green"])
        out[k] = h
    return out


def evaluate(auto, label, fast=True, final=None):
    regs = json.load(open(A.REG)) if os.path.exists(A.REG) else {}
    regs = regs.get("holes", regs)
    n = 4000 if fast else A.t.N_SHOTS
    rng = np.random.default_rng(11)
    z = np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])
    rows, p3 = [], []
    for k, h in A.course.HOLES.items():
        if k not in auto:
            rows.append(dict(hole=str(k), missing=True, checks={}))
            continue
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                r = A.tee_hole(k, h, auto[k], regs, z)
        except Exception as e:                                     # noqa: BLE001
            rows.append(dict(hole=str(k), error=f"{type(e).__name__}: {e}", checks={}))
            continue
        r["checks"] = A.passes(r)
        fd = (final or {}).get(str(k))
        if fd:
            r["club_final"] = fd["pick"]
            r["final_tie"] = bool(fd.get("tie"))
            r["final_runner"] = fd.get("runner")
            r["same_as_final"] = r["club_auto"] == fd["pick"] or (fd.get("tie") and r["club_auto"] == fd.get("runner"))
        rows.append(r)
    for k, p in A.course.PAR3.items():
        if k in auto:
            r = A.par3_hole(k, p, auto[k])
            r["checks"] = dict(length=abs(r["length_err"]) <= A.BAR["length"])
            p3.append(r)
    ok = [r for r in rows if "club_auto" in r]

    def frac(v):
        v = [x for x in v if x is not None]
        return round(float(np.mean(v)), 3) if v else None
    S = dict(label=label, n=len(ok), missing=[r["hole"] for r in rows if r.get("missing")],
             errors={r["hole"]: r["error"] for r in rows if r.get("error")},
             tee_within=frac([r["checks"].get("tee") for r in ok]),
             green_within=frac([r["checks"].get("green") for r in ok]),
             length_within=frac([r["checks"].get("length") for r in ok]),
             median_tee_err=float(np.median([r["tee_err"] for r in ok if "tee_err" in r])) if ok else None,
             median_green_err=float(np.median([r["green_err"] for r in ok if "green_err" in r])) if ok else None,
             median_abs_len_err=float(np.median([abs(r["length_err"]) for r in ok])) if ok else None,
             same_club_traced_model=frac([r["same_club"] for r in ok]),
             same_club_final=frac([r.get("same_as_final") for r in ok]),
             iou_pass={c: frac([r["checks"].get(f"iou_{c}") for r in ok]) for c in A.BAR["iou_classes"]},
             mean_iou={c: frac([r["iou"].get(c) for r in ok]) for c in A.CLASSES},
             par3_len_within=frac([r["checks"]["length"] for r in p3]))
    bars = [("tee within 10 yds", S["tee_within"], 1.0, "of holes"),
            ("green within 10 yds (or traced spread)", S["green_within"], 1.0, "of holes"),
            ("length within 5 yds", S["length_within"], 1.0, "of holes"),
            ("landing IoU water > 0.6", S["iou_pass"]["water"], 1.0, "of holes with water"),
            ("landing IoU OB > 0.6", S["iou_pass"]["ob"], 1.0, "of holes with OB"),
            ("landing IoU trees > 0.6", S["iou_pass"]["recovery"], 1.0, "of holes with trees"),
            ("same club as model-on-traced >= 80%", S["same_club_traced_model"], 0.8, "of tee shots"),
            ("same club as final_decision.json >= 80%", S["same_club_final"], 0.8, "of tee shots (ties count both)")]
    S["bars"] = [dict(bar=b, value=v, need=need, unit=u, ok=(v is not None and v >= need - 1e-9)) for b, v, need, u in bars]
    return dict(summary=S, tee_shots=rows, par3=p3)


def md_section(res):
    S = res["summary"]
    L = [f"### {S['label']}", "",
         f"{S['n']} tee shots evaluated; missing {S['missing'] or 'none'}; errors {S['errors'] or 'none'}. "
         f"Median tee error {S['median_tee_err']} yds, green {S['median_green_err']} yds, |length| {S['median_abs_len_err']} yds.",
         "", "| acceptance bar | value | need | result |", "|---|---|---|---|"]
    for b in S["bars"]:
        v = "n/a" if b["value"] is None else f"{b['value']:.0%}"
        L.append(f"| {b['bar']} | {v} {b['unit']} | {b['need']:.0%} | {'PASS' if b['ok'] else '**FAIL**'} |")
    L += ["", "Mean landing-zone IoU: " + ", ".join(f"{c} {v:.2f}" for c, v in S["mean_iou"].items() if v is not None), "",
          "| hole | len err | tee err | green err | reg | club traced-model / final / auto | IoU water | ob | trees | native | fairway | failed |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["tee_shots"]:
        if "club_auto" not in r:
            L.append(f"| {r['hole']} | {'missing' if r.get('missing') else 'ERROR ' + r.get('error', '')} |||||||||||")
            continue
        i = r["iou"]
        fail = [k for k, v in r["checks"].items() if not v]
        fin = r.get("club_final", "-") + ("~" if r.get("final_tie") else "")
        L.append(f"| {r['hole']} | {r['length_err']:+d} | {r.get('tee_err', '-')} | {r.get('green_err', '-')} | "
                 f"{r['registration']['method'].replace('_registration', '').replace('lie_raster_fit', 'raster')} | "
                 f"{r['club_traced']} / {fin} / {r['club_auto']} | {i.get('water', '-')} | {i.get('ob', '-')} | "
                 f"{i.get('recovery', '-')} | {i.get('native', '-')} | {i.get('fairway', '-')} | {', '.join(fail)} |")
    if res["par3"]:
        L += ["", "| par 3 | traced | auto | err | hazards traced | hazards auto |", "|---|---|---|---|---|---|"]
        for r in res["par3"]:
            L.append(f"| {r['hole']} | {r['traced_center']} | {r['auto_center']} | {r['length_err']:+d} | "
                     f"{r.get('haz_traced', '-')} | {r.get('haz_auto', '-')} |")
    return "\n".join(L) + "\n"


def write_report(golden):
    """REPORT.md = header + contract summary (contracts.json) + golden sections + findings.md."""
    L = ["# QA report: any-course product", "",
         f"Generated by `course_data/qa/golden_spirit_hollow.py` / `run_qa.py` at {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}.",
         "Hand-written findings and bug reports are in `findings.md` (included at the end).", ""]
    cj = os.path.join(QA, "contracts.json")
    if os.path.exists(cj):
        c = json.load(open(cj))
        L += ["## 1. Contract tests (`test_contracts.py`)", "", "| package | holes | passed | failed | skipped | failing checks |",
              "|---|---|---|---|---|---|"]
        for pk, v in c.items():
            L.append(f"| {pk} | {v.get('holes', '-')} | {v['passed']} | {v['failed']} | {v['skipped']} | "
                     f"{'; '.join(v['fail_summary'][:8]) or '-'} |")
        L.append("")
    L += ["## 2. Golden: Spirit Hollow vs the hand-reviewed course.py", "",
          "Bars are ARCHITECTURE.md section 7. *traced-model* = tee_strategy run on spirit_hollow/course.py; "
          "*final* = spirit_hollow/output/final_decision.json (`~` = a tie there; the runner-up then also counts).", ""]
    for res in golden:
        L.append(md_section(res))
    f = os.path.join(QA, "findings.md")
    if os.path.exists(f):
        L += ["", open(f).read()]
    with open(os.path.join(QA, "REPORT.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", action="append", help="package.json / holes.json to evaluate (repeatable)")
    ap.add_argument("--no-oracle", action="store_true", help="skip the oracle-tee pipeline build")
    ap.add_argument("--fast", action="store_true", default=True)
    ap.add_argument("--full", action="store_true", help="20,000 swings per sim")
    a = ap.parse_args()
    final = json.load(open(FINAL)) if os.path.exists(FINAL) else {}
    jobs = []
    if a.package:
        for p in a.package:
            pk = [x for x in PK.find_packages() if os.path.abspath(x.path) == os.path.abspath(p)]
            if pk:
                jobs.append((f"package {os.path.relpath(p, ROOT)} ({pk[0].kind}, as built)", package_auto(pk[0])))
    else:
        for pk in PK.find_packages():
            if "spirit" in pk.slug:
                jobs.append((f"package {os.path.relpath(pk.path, ROOT)} ({pk.kind}, as built: card tees, not the traced ones)",
                             package_auto(pk)))
    if not a.no_oracle:
        with contextlib.redirect_stdout(io.StringIO()):
            auto = A.oracle_builds()
        jobs.insert(0, ("oracle tees: pipeline.build_course with the traced lengths as the card (apples to apples)", auto))
    golden = []
    for label, auto in jobs:
        t0 = time.time()
        res = evaluate(auto, label, fast=not a.full, final=final)
        res["summary"]["seconds"] = round(time.time() - t0)
        golden.append(res)
        S = res["summary"]
        print(label)
        for b in S["bars"]:
            v = "n/a" if b["value"] is None else f"{b['value']:.0%}"
            print(f"  {b['bar']:<45} {v:>5}  {'ok' if b['ok'] else 'FAIL'}", flush=True)
    with open(os.path.join(QA, "golden.json"), "w") as fh:
        json.dump(golden, fh, indent=1, default=float)
    write_report(golden)
    print("wrote course_data/qa/golden.json, REPORT.md")


if __name__ == "__main__":
    main()
