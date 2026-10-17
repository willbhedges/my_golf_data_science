"""Second-shot plan for every Spirit Hollow par 4 and par 5 -> output/approach.json + REPORT.md.

  python3 spirit_hollow/approach/build.py                      # all holes, full settings (slow: Actions)
  APPROACH_FAST=1 python3 spirit_hollow/approach/build.py      # quick local run (fewer samples)
  APPROACH_HOLES=2F,4 APPROACH_OUT=parts/x.json ...            # some holes -> a part file (Actions matrix)
  python3 spirit_hollow/approach/build.py --merge DIR          # part files -> approach.json + REPORT.md

Per hole:
  * tee shot = the calm-day pick and aim of output/final_decision.json, simulated by tee_strategy under the
    wind page's prior-mean settings -> where the ball finishes (ground yards, lie from the merged map);
  * approach distance / lie distribution and the DECADE target box on the real (OSM) green, from fairway
    and from rough, for each DECADE wind modifier (-1..+3), with a strokes-gained check of the box centre
    against every aim on the green (pin-averaged);
  * par 5s: go-for-it vs lay-up for every tee-ball position, the lay-up target (distance left, offset),
    a go/lay-up distance rule by lie, and sensitivities (5-hcp baselines; a partial-wedge penalty).
Polygons are given in the wind page's pixel frame (spirit_hollow/build_wind_page.py tee_hole: the 920 x 2000
frame of the screenshot the page draws on), in the page's (along, lat) yards from the tee, and in WGS84.
"""
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "..", "mozingo"), os.path.join(HERE, "..")]

import geom                                     # noqa: E402
import plan as P                                # noqa: E402
import shots as S                               # noqa: E402
import course                                   # noqa: E402
import yardage_book as yb                       # noqa: E402

OUT_DIR = os.path.join(HERE, "output")
FAST = bool(os.environ.get("APPROACH_FAST"))
CFG = dict(n_tee=1500 if FAST else 4000, n_sg=60 if FAST else 250, m_sg=40 if FAST else 80,
           n_p5=120 if FAST else 600, m_p5=60 if FAST else 120, grid=10.0 if FAST else 5.0,
           m_grid=80 if FAST else 200, n_sens=80 if FAST else 300)
LABEL = {"2B": "2 (Gold tee)", "2F": "2", "9B": "9 (Gold tee)", "9F": "9"}
BLACK = {"2B": False, "9B": False}


def key_of(k):
    return int(k) if str(k).isdigit() else str(k)


def r1(x):
    return [[round(float(a), 1), round(float(b), 1)] for a, b in np.atleast_2d(x)]


class PageFrame:
    """The wind page's tee frame for a hole: display screenshot px and (along, lat) yds from the tee."""

    def __init__(self, hole):
        hd = yb.display_hole(course.HOLES[hole.key])
        tee, d = np.array(hd["tee"], float), np.array(hd["dot270"], float)
        self.ppy = float(np.linalg.norm(d - tee) / 270)
        self.f = (d - tee) / np.linalg.norm(d - tee)
        self.r = np.array([-self.f[1], self.f[0]])
        self.tee = tee
        self.h = hole

    def px(self, xy):
        return self.h.xy_to_px(np.atleast_2d(xy))

    def yd(self, xy):
        rel = self.px(xy) - self.tee
        return np.c_[rel @ self.f, rel @ self.r] / self.ppy

    def geometry(self, xy):
        xy = np.atleast_2d(xy)
        return dict(px=r1(self.px(xy)), yd=r1(self.yd(xy)),
                    ll=[[round(float(a), 7), round(float(b), 7)] for a, b in self.h.xy_to_ll(xy)])


def describe_aim(b):
    lat, dep = b["aim_ld"]
    side = "centre" if abs(lat) < 1.5 else f"{abs(lat):.0f} {'right' if lat > 0 else 'left'}"
    depth = "middle" if abs(dep) < 1.5 else f"{abs(dep):.0f} {'long' if dep > 0 else 'short'}"
    return f"{side}, {depth}"


def box_record(hole, pf, b, start):
    dist = float(np.linalg.norm(hole.green_c - start))
    return dict(dist=round(dist, 1), lie=b["lie"], wind=b["wind"], base=b["base"],
                haz=b["haz"], haz_share=b["haz_share"], cushion={k: round(v, 1) for k, v in b["off"].items()},
                lat=[round(v, 1) for v in b["lat"]], dep=[round(v, 1) for v in b["dep"]],
                how_lat=b["how_lat"], how_dep=b["how_dep"], aim_ld=[round(v, 1) for v in b["aim_ld"]],
                aim_text=describe_aim(b), play=round(dist + b["aim_ld"][1], 1),
                lo=round(dist + b["dep"][0], 1), hi=round(dist + b["dep"][1], 1),
                club=S.club_for(dist + b["aim_ld"][1]),
                box=pf.geometry(b["box_xy"]), shape=pf.geometry(b["shape_xy"]), aim=pf.geometry(b["aim_xy"]))


def boxes_from(hole, R, pf, start, lies=("fairway", "rough")):
    out = {}
    for lie in lies:
        out[lie] = {str(w): box_record(hole, pf, P.decade_box(hole, R, start, lie, wind=w), start)
                    for w in P.WIND_MODS}
    return out


def ellipse(center, fwd, sl, sd, n=24):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = geom.right_of(fwd)
    return center + (2 * sd * np.cos(a))[:, None] * fwd + (2 * sl * np.sin(a))[:, None] * r


def hole_plan(key, log=print):
    t0 = time.time()
    H = geom.Hole(key)
    R = geom.Raster(H)
    pf = PageFrame(H)
    ap = P.Approach(H, R)
    xy, club, aim = P.tee_finishes(H, n=CFG["n_tee"])
    lies = np.array([geom.LIES[i] for i in R.lie_id(xy)], dtype=object)
    dist = np.hypot(*(xy - H.green_c).T)
    playable = np.isin(lies, S.TARGETABLE)
    share = {l: round(float((lies == l).mean()), 3) for l in geom.LIES if (lies == l).any()}
    start = np.median(xy[playable], axis=0) if playable.any() else np.median(xy, axis=0)
    rec = dict(key=str(key), label=LABEL.get(str(key), str(key)), par=H.par, black=BLACK.get(str(key), True),
               tee=dict(club=club, aim=aim, tie=P.tee_pick(key)[2]),
               approach=dict(median=round(float(np.median(dist)), 1),
                             p10=round(float(np.percentile(dist, 10)), 1),
                             p90=round(float(np.percentile(dist, 90)), 1),
                             median_playable=round(float(np.median(dist[playable])), 1) if playable.any() else None,
                             lie_share=share, club=S.club_for(float(np.median(dist)))),
               green=dict(osm=pf.geometry(H.green), centre=pf.geometry(H.green_c),
                          trilat_offset_yd=round(float(np.linalg.norm(H.green_trilat - H.green_c)), 1),
                          depth_yd=None),
               finishes_sample=pf.geometry(xy[:: max(len(xy) // 150, 1)])["px"])
    fwd = P.frame(H, start)[0]
    gl = P.to_ld(H, H.green, fwd, geom.right_of(fwd))
    rec["green"]["depth_yd"] = round(float(np.ptp(gl[:, 1])), 1)
    rec["green"]["width_yd"] = round(float(np.ptp(gl[:, 0])), 1)
    page_in = pf.yd(H.green_c)[0]
    rec["green"]["in_page_crop"] = bool(-14 <= page_in[0] <= 400 and abs(page_in[1]) <= 75)

    if H.par == 4:
        rec["boxes"] = boxes_from(H, R, pf, start)
        rec["box_from"] = pf.geometry(start)
        idx = np.random.default_rng(1).choice(len(xy), min(CFG["n_sg"], len(xy)), replace=False)
        sg = P.sg_aim_check(ap, xy[idx], lies[idx], m=CFG["m_sg"])
        if sg:
            b0 = P.decade_box(H, R, start, "fairway")
            best_ld = P.to_ld(H, sg["best_xy"], b0["fwd"], b0["right"])[0]
            inside = (b0["lat"][0] - 1 <= best_ld[0] <= b0["lat"][1] + 1) and (b0["dep"][0] - 1 <= best_ld[1] <= b0["dep"][1] + 1)
            rec["sg_check"] = dict(e_decade=round(sg["e_decade"], 3), e_centre=round(sg["e_centre"], 3),
                                   e_best=round(sg["e_best"], 3), best_ld=[round(float(v), 1) for v in best_ld],
                                   best=pf.geometry(sg["best_xy"]), best_in_box=bool(inside),
                                   decade_cost=round(sg["e_decade"] - sg["e_best"], 3), n=sg["n_starts"])
        e_all = [ap.value(s, l) for s, l in zip(xy[idx], lies[idx])]
        rec["approach"]["expected_strokes"] = round(float(np.mean(e_all)), 3)
    else:
        rec.update(par5(H, R, pf, ap, xy, lies))
    rec["seconds"] = round(time.time() - t0, 1)
    log(f"{key}: {rec['seconds']} s")
    return rec


def par5(H, R, pf, ap, xy, lies):
    ap.build_grid(spacing=CFG["grid"])
    idx = np.random.default_rng(2).choice(len(xy), min(CFG["n_p5"], len(xy)), replace=False)
    res = P.par5_second(ap, xy[idx], lies[idx], m=CFG["m_p5"])
    s = P.summarize_par5(res)
    out = dict(par5=dict(p_go=round(s["p_go"], 3), p_layup=round(s["p_lay"], 3), p_forced=round(s["p_fixed"], 3),
                         ev_policy=round(s["ev_policy"], 3), go_threshold=s["go_threshold"],
                         ev_go_when_possible=None if s["ev_go_when_possible"] is None else round(s["ev_go_when_possible"], 3),
                         ev_lay_when_possible=None if s["ev_lay_when_possible"] is None else round(s["ev_lay_when_possible"], 3)))
    # go: by-lie go rate and the box from the median playable tee ball
    play = np.isin(lies, S.TARGETABLE)
    start = np.median(xy[play], axis=0)
    out["par5"]["go_rate_by_lie"] = {l: round(float(s["go_better"][res["lies"] == l].mean()), 2)
                                     for l in ("fairway", "first_cut", "rough", "sand") if (res["lies"] == l).sum() >= 5}
    out["go_boxes"] = boxes_from(H, R, pf, start)
    out["go_from"] = pf.geometry(start)
    fx = s["fixed"]
    if fx:
        L, off = fx["L"], fx["off"]
        p, fwd = H.along_line_from_green(L)
        tgt = p + off * geom.right_of(fwd)
        d_shot = float(np.linalg.norm(tgt - start))
        sl, sd = S.sigma(d_shot, "fairway")
        shot_dir = (tgt - start) / max(d_shot, 1e-9)
        out["layup"] = dict(L=L, off=off, ev=round(fx["ev"], 3), target=pf.geometry(tgt), shot=round(d_shot, 1),
                            club=S.club_for(d_shot), zone=pf.geometry(ellipse(tgt, shot_dir, sl, sd)),
                            ev_by_L={str(k): [round(v[0], 3), v[1]] for k, v in fx["ev_by_L"].items()},
                            lie_share=_layup_lies(H, R, start, tgt))
        third = tgt
        out["boxes"] = boxes_from(H, R, pf, third)
        out["box_from"] = pf.geometry(third)
        full = {int(k): v for k, v in fx["ev_by_L"].items()}
        fw = min((k for k in full if 100 <= k <= 120), key=lambda k: full[k][0], default=None)
        if fw is not None:
            out["layup"]["full_wedge_cost"] = round(full[fw][0] - fx["ev"], 3)
            out["layup"]["full_wedge_L"] = fw
    out["go_sweep"] = P.go_sweep(ap, m=CFG["m_p5"])
    out["sensitivity"] = sensitivity(H, R, xy, lies)
    return out


def _layup_lies(H, R, start, tgt, m=400):
    fin, _ = S.shot(start, tgt, "fairway", S.z_draws(m, 4))
    ids = R.lie_id(fin)
    return {geom.LIES[i]: round(float((ids == i).mean()), 3) for i in np.unique(ids)}


def sensitivity(H, R, xy, lies):
    out = {}
    idx = np.random.default_rng(3).choice(len(xy), min(CFG["n_sens"], len(xy)), replace=False)
    import tee_strategy as t
    for name, setup in (("hcp_baselines", lambda on: (setattr(S, "HCP", on), setattr(t, "HCP_BASELINE", on))),
                        ("partial_wedge_0.05", lambda on: setattr(S, "PARTIAL_WEDGE", 0.05 if on else 0.0))):
        setup(True)
        try:
            ap = P.Approach(H, R)
            ap.build_grid(spacing=max(CFG["grid"], 10.0), )
            res = P.par5_second(ap, xy[idx], lies[idx], m=max(CFG["m_p5"] // 2, 40))
            s = P.summarize_par5(res)
            fx = s["fixed"] or {}
            out[name] = dict(p_go=round(s["p_go"], 3), go_threshold=s["go_threshold"],
                             layup_L=fx.get("L"), layup_off=fx.get("off"))
        finally:
            setup(False)
    return out


# ------------------------------------------------------------------ report
def write_outputs(recs):
    os.makedirs(OUT_DIR, exist_ok=True)
    order = [str(k) for k in course.ORDER if str(k) in recs]
    data = dict(doc=__doc__.strip().splitlines()[0], cfg=CFG, settings=settings(),
                holes={k: recs[k] for k in order})
    with open(os.path.join(OUT_DIR, "approach.json"), "w") as f:
        json.dump(data, f, separators=(",", ":"), default=_js)
    with open(os.path.join(HERE, "REPORT.md"), "w") as f:
        f.write(report(data))


def _js(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


def settings():
    return dict(reach=S.REACH, sigma_lat_by_dist=dict(zip(map(int, S.SIG_D), S.SIG_LAT.tolist())),
                depth_ratio=S.DEPTH_RATIO, lie_mult=S.LIE_MULT, mishit=[S.MISHIT_FROM, S.MISHIT_RATE, list(S.MISHIT_RANGE)],
                decade_card=yb.TARGET, decade_add=yb.ADD, wind_mods=list(P.WIND_MODS), band=[P.BAND, P.BAND_PENAL],
                baselines="PGA Tour (Broadie) putting / short game / tee_strategy.BASELINE")


def _ft(x):
    return "-" if x is None else f"{x:.0f}"


def report(data):
    import report_md
    return report_md.render(data)


def main():
    args = sys.argv[1:]
    if args[:1] == ["--merge"]:
        recs = {}
        for path in sorted(glob.glob(os.path.join(args[1], "**", "*.json"), recursive=True)):
            part = json.load(open(path))
            CFG.update(part.get("cfg", {}))
            recs.update(part["holes"])
        write_outputs(recs)
        print("merged", len(recs), "holes")
        return
    only = [x.strip() for x in os.environ.get("APPROACH_HOLES", "").split(",") if x.strip()]
    keys = [k for k in course.ORDER if k in course.HOLES and (not only or str(k) in only)]
    recs = {str(k): hole_plan(k) for k in keys}
    part = os.environ.get("APPROACH_OUT")
    if part:
        os.makedirs(os.path.dirname(part) or ".", exist_ok=True)
        with open(part, "w") as f:
            json.dump(dict(cfg=CFG, holes=recs), f, default=_js)
        return
    write_outputs(recs)


if __name__ == "__main__":
    main()
