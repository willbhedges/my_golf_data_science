"""Evaluate gate v2 (gate_v2.py) against human labels, with leave-one-course-out threshold tuning.

  python3 course_data/library/gate/gate_v2_eval.py [--target 0.95] [--csv out.csv]  -> stdout tables (GATE_V2.md)

Labels (one row per hole x solved tee set):
  review    course_data/library/<slug>/review.json (course_review/1): verdict OK -> right, anything else (wrong tee
            position / yardage / par / routing, bad pick) -> wrong. Verdicts are per hole, so a hole's verdict is
            applied to every tee set of it (slightly pessimistic for set-specific faults). Holes the reviewer lists as
            'missing' have no page row; they make the course unsafe.
  truth     course_data/library/gate/gate_eval.json rows (hand-truth courses, the blind-built set only): wrong when the
            tee club is not the same-or-tie, or the hole is routed to the wrong green / par. Rows with nothing scored
            are skipped.
A course is 'safe' when no labelled hole is wrong and nothing is missing.
"""
import argparse
import glob
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gate_v2 as G  # noqa: E402


def rj(p):
    with open(p) as fh:
        return json.load(fh)


def load():
    courses = {}
    for rp in sorted(glob.glob(os.path.join(LIB, "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        qp = os.path.join(os.path.dirname(rp), "qa.json")
        if not os.path.exists(qp):
            continue
        r = rj(rp)
        r = r.get("course_review/1", r)
        lab, missing = {}, 0
        for h in r.get("holes") or []:
            v = str(h.get("verdict", "")).strip().lower()
            if v == "missing":
                missing += 1
            else:
                # a tee fix keyed by some (not all) of the page's sets says which sets are wrong
                tl = (h.get("fix") or {}).get("tee_ll")
                page_sets = {b.get("set") for b in rj(qp)["checks"].values()}
                only = set(tl) if isinstance(tl, dict) and set(tl) < page_sets and v != "bad pick" else None
                lab[str(h["n"])] = (v != "ok", v, only)
        courses[slug] = dict(src="review", qa=rj(qp), lab=lab, missing=missing)
    ge = os.path.join(HERE, "gate_eval.json")
    if os.path.exists(ge):
        for c in rj(ge)["courses"]:
            qp = os.path.join(HERE, "gate_" + c["slug"], "qa.json")
            if not c.get("rows") or not os.path.exists(qp) or c["slug"] in courses:
                continue
            qa = rj(qp)
            qa["checks"] = {"auto": qa["checks"]["auto"]}  # truth scores the blind 'auto' set only
            lab = {}
            for row in c["rows"]:
                bad = []
                if row.get("same_or_tie") is False:
                    bad.append("club")
                if row.get("routing") not in (None, "ok"):
                    bad.append("routing")
                if row.get("par_ok") is False:
                    bad.append("par")
                if row.get("same_or_tie") is None and row.get("routing") is None and row.get("par_ok") is None:
                    continue
                lab[str(row["hole"])] = (bool(bad), "/".join(bad) or "ok", None)
            courses["T:" + c["slug"]] = dict(src="truth", qa=qa, lab=lab, missing=0)
    return courses


def is_wrong(c, set_name, n):
    w, _, only = c["lab"][n]
    return bool(w) and (only is None or set_name in only)


def rows_of(courses):
    out = []
    for slug, c in courses.items():
        for w, blk in c["qa"]["checks"].items():
            for n, h in blk["holes"].items():
                if n not in c["lab"]:
                    continue
                f = G.hole_features(h)
                out.append(dict(course=slug, src=c["src"], set=blk.get("set"), hole=n,
                                wrong=is_wrong(c, blk.get("set"), n),
                                verdict=c["lab"][n][1], **f))
    return out


def course_safe(c):
    return c["missing"] == 0 and not any(w for w, _, _ in c["lab"].values())


def strict(c):
    """Today's gate: a hole is OK iff PASS; a course iff every hole PASS + card matched + par sum ok."""
    hd = {}
    for w, blk in c["qa"]["checks"].items():
        for n, h in blk["holes"].items():
            hd[(blk.get("set"), n)] = h["status"] == "PASS"
    ok_course = all(hd.values()) and all(
        (blk.get("course") or {}).get("pars_ok") and (blk.get("course") or {}).get("card_holes")
        for blk in c["qa"]["checks"].values())
    return hd, ok_course


def v2(c):
    g = G.gate(c["qa"])
    hd = {}
    for w, blk in c["qa"]["checks"].items():
        s = blk.get("set") or w
        for n in blk["holes"]:
            hd[(blk.get("set"), n)] = g["holes"][s][n][0] == "AUTO"
    return hd, g["course"] == "AUTO"


def score(courses, fn):
    """-> hole x set: auto n, auto wrong, total n, total wrong; courses: auto, auto&safe"""
    a = aw = n = nw = 0
    ca, cas, cs = [], [], 0
    for slug, c in courses.items():
        hd, cok = fn(c)
        for (w, hn), ok in hd.items():
            if hn not in c["lab"]:
                continue
            wrong = is_wrong(c, w, hn)
            n += 1
            nw += wrong
            if ok:
                a += 1
                aw += wrong
        cs += course_safe(c)
        if cok:
            ca.append(slug)
            if course_safe(c):
                cas.append(slug)
    return dict(n=n, wrong=nw, auto=a, auto_wrong=aw, courses=len(courses), safe=cs, c_auto=ca, c_auto_safe=cas)


GRID = dict(YARD_OK=[5, 10, 15, 25], AIM_ROUGH_OK=[0, 10, 15, 25, 50], MAX_COURSE_TEE_FITS=[2, 4, 6, 99],
            PAD_MODE=["never", "no_osm_tees", "always"])


def set_params(p):
    for k, v in p.items():
        setattr(G, k, v)


def tune(courses, target):
    """Max hole coverage s.t. hole precision (1 - wrong rate among AUTO) >= target; ties -> stricter params."""
    best = None
    for vals in itertools.product(*GRID.values()):
        p = dict(zip(GRID, vals))
        set_params(p)
        s = score(courses, v2)
        prec = 1 - s["auto_wrong"] / s["auto"] if s["auto"] else 1.0
        key = (prec >= target, s["auto"] if prec >= target else prec, -vals[0], -vals[1], -vals[2],
               ["always", "no_osm_tees", "never"].index(vals[3]))
        if best is None or key > best[0]:
            best = (key, p)
    return best[1]


def loco(courses, target):
    tot = dict(n=0, wrong=0, auto=0, auto_wrong=0, c_auto=[], c_auto_safe=[], safe=0, courses=0)
    chosen = {}
    for slug in courses:
        train = {k: v for k, v in courses.items() if k != slug}
        p = tune(train, target)
        chosen[slug] = p
        set_params(p)
        s = score({slug: courses[slug]}, v2)
        for k in tot:
            tot[k] += s[k]
    return tot, chosen


def fmt(s):
    pr = (1 - s["auto_wrong"] / s["auto"]) if s["auto"] else float("nan")
    return (f"hole x set: {s['auto']}/{s['n']} AUTO ({s['auto'] / s['n']:.0%} coverage), {s['auto_wrong']} wrong "
            f"-> precision {pr:.1%} (base wrong rate {s['wrong'] / s['n']:.1%}); courses AUTO {len(s['c_auto'])}"
            f"/{s['courses']} (safe among them {len(s['c_auto_safe'])}; safe overall {s['safe']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=float, default=0.92)
    ap.add_argument("--csv")
    a = ap.parse_args()
    courses = load()
    rows = rows_of(courses)
    print(f"courses {len(courses)} ({sum(c['src'] == 'review' for c in courses.values())} review, "
          f"{sum(c['src'] == 'truth' for c in courses.values())} truth); labelled hole x set rows {len(rows)}, "
          f"wrong {sum(r['wrong'] for r in rows)}")
    if a.csv:
        import csv
        with open(a.csv, "w", newline="") as fh:
            wtr = csv.DictWriter(fh, fieldnames=list(rows[0]))
            wtr.writeheader()
            for r in rows:
                wtr.writerow({k: (";".join(v) if isinstance(v, list) else v) for k, v in r.items()})
    print("\n# wrong rate by failed check (a row counts under each check it fails)")
    from collections import defaultdict
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        for k in (r["failed"] or ["(PASS)"]):
            key = k
            if k == "tee":
                ym = r["yard_delta"] is not None and abs(r["yard_delta"]) <= 10
                key = f"tee:{r['tee_kind']}{' +yds ok' if ym else (' no card' if r['no_card_yards'] else ' +yds off')}"
            if k == "aim":
                key = f"aim:{r['aim_lie']}" + (" nofw" if r["no_fairway"] else
                                               (" <=15" if (r["aim_from_fw"] or 0) <= 15 else " >15"))
            if k in ("par", "yardage"):
                key = k + (" (no card)" if r["no_card_par"] or r["no_card_yards"] else " (vs card)")
            agg[key][0] += 1
            agg[key][1] += r["wrong"]
        if len(r["failed"]) == 1:
            agg["only " + r["failed"][0]][0] += 1
            agg["only " + r["failed"][0]][1] += r["wrong"]
    for k, (n, w) in sorted(agg.items()):
        print(f"| {k} | {n} | {w} ({w / n:.0%}) |")
    print("\n# course flags")
    for slug, c in courses.items():
        hd, _ = v2(c)
        print(f"| {slug} | {', '.join(G.course_flags(c['qa'])) or '-'} | safe={course_safe(c)} | "
              f"wrong {sum(v[0] for v in c['lab'].values())}/{len(c['lab'])} missing {c['missing']} |")
    print("\n# in-sample")
    print("strict  :", fmt(score(courses, strict)))
    defaults = {k: getattr(G, k) for k in GRID}
    print("v2 dflt :", fmt(score(courses, v2)))
    for src in ("review", "truth"):
        sub = {k: v for k, v in courses.items() if v["src"] == src}
        print(f"  {src:6} strict:", fmt(score(sub, strict)))
        print(f"  {src:6} v2    :", fmt(score(sub, v2)))
    print(f"\n# leave-one-course-out (thresholds tuned on the other courses, target precision {a.target})")
    tot, chosen = loco(courses, a.target)
    print("v2 LOCO :", fmt(tot))
    from collections import Counter
    print("params chosen:", Counter(tuple(sorted(p.items())) for p in chosen.values()).most_common(4))
    set_params(defaults)
    print("\n# ablations (in-sample; each changes one thing from the defaults)")
    abl = [("defaults", {}), ("no course flags", "noflags"), ("pad tee never benign", dict(PAD_MODE="never")),
           ("pad tee always benign (OSM tees or not)", dict(PAD_MODE="always")),
           ("aim rough <=15 yds benign", dict(AIM_ROUGH_OK=15)), ("tee_fits flag off", dict(MAX_COURSE_TEE_FITS=99)),
           ("tee_fits > 4", dict(MAX_COURSE_TEE_FITS=4)), ("pad yardage within 5", dict(YARD_OK=5))]
    for name, p in abl:
        set_params(defaults)
        if p == "noflags":
            keep = G.course_flags
            G.course_flags = lambda qa: []
            print(f"| {name} | {fmt(score(courses, v2))} |")
            G.course_flags = keep
            continue
        set_params(p)
        print(f"| {name} | {fmt(score(courses, v2))} |")
    set_params(defaults)
    print("\n# course level: no red flag and at most K holes to confirm (the CONFIRM holes are the tap list);"
          " 'clean' = every wrong hole x set of the course is on the tap list (or none wrong) and nothing missing")
    for K in (0, 2, 4, 6, 18):
        for fn, nm in ((strict, "strict"), (v2, "v2")):
            ok, clean = [], []
            for slug, c in courses.items():
                hd, _ = fn(c)
                flags = (G.course_flags(c["qa"]) if nm == "v2" else
                         [1 for b in c["qa"]["checks"].values()
                          if not ((b.get("course") or {}).get("pars_ok") and (b.get("course") or {}).get("card_holes"))])
                taps = {n for (w, n), a in hd.items() if not a}
                if flags or len(taps) > K:
                    continue
                ok.append(slug)
                missed = [(w, n) for (w, n), a in hd.items() if a and n in c["lab"] and is_wrong(c, w, n)]
                if not missed and not c["missing"]:
                    clean.append(slug)
            print(f"| {K} | {nm} | {len(ok)} | {len(clean)} | {', '.join(ok)} |")
    print("\n# per course (default params)")
    for slug, c in courses.items():
        g = G.gate(c["qa"])
        print(f"| {slug} | {g['course']} | {', '.join(g['flags']) or '-'} | confirm {','.join(g['confirm'])} | "
              f"wrong {','.join(k for k, v in c['lab'].items() if v[0])} |")


if __name__ == "__main__":
    main()
