"""Automatic picture checks for one solved base of a course page (one process per base: the v2 engine binds one
course module per process).

  V2_COURSES_DIR=course_data/library python3 course_data/library/picture_checks.py --slug S --which auto --out x.json

Per hole, on the base set's tee (everything is read from what the page shows: the course module, the merged v2
calm-day decisions, the package it was built from):
  tee        the tee marker lies inside an OSM golf=tee polygon (TEE_TOL yds of slack for the polygon edge); a tee
             placed on a lidar pad, a texture pad or a walk-back from the card is a CHECK
  yardage    the measured tee -> green length along the hole line is within YARD_TOL yds of the card
  par        the hole's par is the card's par (and, course level, the pars sum to the card's total)
  aim        tee shots: the calm-day pick's landing point (club total along the tee line, at the pick's aim) is on
             fairway, on first cut, or rough within FIRST_CUT yds of a fairway cell
  oval       tee shots: the pick's landing pattern (an ellipse, the club's 95 % lateral width x carry window + roll
             spread, as the model uses) is not more than OVAL_MAX trees / water / OB (unverified ground beyond the
             mapped corridor counts half trees, as in the model)
  par3 box   par 3s: the calm target box (yardage_book.par3_plan, what the page draws) has its centre on the OSM
             green polygon and at least BOX_ON of its area on it; no OSM green outline is a CHECK
A hole is PASS when every check passes, else CHECK with the reasons.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "courses"))

TEE_TOL = 3.0
YARD_TOL = 10.0
FIRST_CUT = 6.0
OVAL_MAX = 0.40
BOX_ON = 0.6
ROLL_SPREAD = 6.0
YD = 0.9144


def _xy(ll, lat0):
    """lon/lat -> local yards (equirectangular; fine at hole scale)."""
    ll = np.asarray(ll, float)
    return np.c_[(ll[..., 0]) * 111320.0 * math.cos(math.radians(lat0)) / YD, ll[..., 1] * 110574.0 / YD]


def _inside(poly_xy, p):
    from matplotlib.path import Path
    return bool(Path(poly_xy).contains_point(p))


def _dist_to_poly(poly_xy, p):
    a, b = poly_xy, np.roll(poly_xy, -1, axis=0)
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-9), 0, 1)
    q = a + ab * t[:, None]
    return float(np.min(np.hypot(*(q - p).T)))


def osm_tees(osm_path):
    if not osm_path or not os.path.exists(osm_path):
        return []
    fc = json.load(open(osm_path))
    out = []
    for f in fc.get("features", []):
        if (f.get("properties") or {}).get("golf") != "tee":
            continue
        g = f.get("geometry") or {}
        if g.get("type") == "Polygon":
            out.append(g["coordinates"][0])
        elif g.get("type") == "MultiPolygon":
            out += [p[0] for p in g["coordinates"]]
    return out


def tee_check(tee_ll, tees_ll):
    if tee_ll is None:
        return False, "no tee for this set"
    if not tees_ll:
        return False, "OSM maps no tee boxes on this course"
    lat0 = tee_ll[1]
    p = _xy(tee_ll, lat0)[0]
    best = 1e9
    for t in tees_ll:
        q = _xy(t, lat0)
        if _inside(q, p):
            return True, "on an OSM tee box"
        best = min(best, _dist_to_poly(q, p))
    return best <= TEE_TOL, f"{best:.0f} yds from the nearest OSM tee box"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--which", required=True)
    ap.add_argument("--osm", help="raw/osm.geojson of the course (golf=tee polygons)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import v2_course as VC
    cfg = VC.config(a.slug)
    course, meta, M, D = VC.activate(a.slug, a.which)
    from matplotlib.path import Path
    from scipy import ndimage
    pkg = json.load(open(os.path.join(ROOT, cfg["package"])))
    holes = pkg["holes"]
    base = meta["tee_set"]
    card = (pkg.get("tee_sets") or {}).get(base) or {}
    tees_ll = osm_tees(a.osm)
    dp = VC.cdir(a.slug, a.which, "v2", "v2_decisions.json")
    dec = json.load(open(dp)) if os.path.exists(dp) else {}
    out = dict(slug=a.slug, which=a.which, set=base, holes={}, course={})
    refs = sorted(holes, key=lambda r: int(r) if str(r).isdigit() else 99)
    for ref in refs:
        h = holes[ref]
        k = int(ref) if str(ref).isdigit() else ref
        t = (h.get("tees") or {}).get(base) or {}
        rec = dict(par=h.get("par"), checks={})
        C = rec["checks"]
        ok, why = tee_check(t.get("tee_ll") or h.get("tee_ll"), tees_ll)
        C["tee"] = dict(ok=ok, why=why if ok else f"tee marker not on an OSM tee box ({t.get('method', '?')}; {why})")
        meas, cy = t.get("measured_yards"), t.get("card_yards") or (h.get("yards") or {}).get(base)
        if meas is None or cy is None:
            C["yardage"] = dict(ok=False, why=f"no {'card' if cy is None else 'measured'} yardage for {base}")
        else:
            d = float(meas) - float(cy)
            C["yardage"] = dict(ok=abs(d) <= YARD_TOL, why=f"measured {meas:.0f} vs card {cy:.0f} ({d:+.0f})")
        cp = None
        if card.get("par") and str(ref).isdigit() and int(ref) <= len(card["par"]):
            cp = card["par"][int(ref) - 1]
        C["par"] = dict(ok=cp is not None and cp == h.get("par"),
                        why=f"par {h.get('par')} vs card {cp}" if cp is not None else "no card par")
        if k in course.PAR3:
            p = course.PAR3[k]
            outline = bool(h.get("green_polygon_ll")) and str((h.get("provenance") or {}).get("green", "")).startswith("osm")
            if not outline:
                C["par3_box"] = dict(ok=False, why="no OSM green outline (the target box is drawn on an estimated green)")
            else:
                import yardage_book as yb
                yb.WIND_NOW = 0
                plan = yb.par3_plan(p)
                (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
                g = Path(np.asarray(p["green"], float))
                ll_, dd_ = np.meshgrid(np.linspace(l0, l1, 9), np.linspace(d0, d1, 9))
                share = float(g.contains_points(np.c_[ll_.ravel(), dd_.ravel()]).mean())
                cen = g.contains_point(((l0 + l1) / 2, (d0 + d1) / 2))
                C["par3_box"] = dict(ok=bool(cen and share >= BOX_ON),
                                     why=f"target box {100 * share:.0f}% on the green, centre {'on' if cen else 'OFF'} it")
                rec["box"] = dict(lat=[round(l0, 1), round(l1, 1)], dep=[round(d0, 1), round(d1, 1)])
        elif k in course.HOLES:
            r = dec.get(str(k))
            if not r or "pick" not in r:
                C["aim"] = dict(ok=False, why="no calm-day decision for this hole")
            else:
                hd = course.HOLES[k]
                pick, aim = r["pick"], float(r["aim"])
                carry, total, width, depth = M.CLUBS[pick]
                dc, rf = 0.0, 1.0
                e = (hd.get("elev") or {}).get(pick)
                if e:
                    dc, rf = float(e[0]), float(e[1])
                along = carry + dc + (total - carry) * rf
                R = M.Raster(hd)
                lie = M.LIES[int(R.lie_at(np.array([along]), np.array([aim]))[0])]
                fw = R.lie == M.CODE["fairway"]
                if fw.any():
                    dist = ndimage.distance_transform_edt(~fw) * M.RES
                    ia, il = R.idx(np.array([along]), np.array([aim]))
                    dfw = float(dist[ia[0], il[0]])
                else:
                    dfw = None
                ok = lie in ("fairway", "first_cut") or (lie == "rough" and dfw is not None and dfw <= FIRST_CUT)
                if dfw is None:
                    why = f"no fairway mapped on this hole; {pick} lands in {lie}"
                else:
                    why = f"{pick} {aim:+.0f} lands {along:.0f} yds out in {lie.replace('_', ' ')}" + \
                        ("" if lie == "fairway" else f" ({dfw:.0f} yds from fairway)")
                C["aim"] = dict(ok=bool(ok), why=why)
                sa, sl = depth / 2.0 + ROLL_SPREAD, width / 2.0
                m = ((R.AA - along) / sa) ** 2 + ((R.LL - aim) / sl) ** 2 <= 1.0
                L = R.lie[m]
                bad = np.isin(L, [M.CODE["recovery"], M.CODE["water"], M.CODE["ob"]]).sum() + 0.5 * (L == M.CODE["unverified"]).sum()
                frac = float(bad / max(m.sum(), 1))
                parts = {n: round(float((L == M.CODE[n]).mean()), 2) for n in ("recovery", "water", "ob", "unverified")
                         if (L == M.CODE[n]).any()}
                C["oval"] = dict(ok=frac <= OVAL_MAX, why=f"landing pattern {100 * frac:.0f}% trees / water / OB "
                                 f"({', '.join(f'{n} {v:.0%}' for n, v in parts.items()) or 'none'})")
                rec["pick"] = dict(club=pick, aim=round(aim, 1), along=round(along, 1), lie=lie, tie=bool(r.get("tie")))
        rec["status"] = "PASS" if all(c["ok"] for c in C.values()) else "CHECK"
        rec["reasons"] = [f"{n}: {c['why']}" for n, c in C.items() if not c["ok"]]
        out["holes"][str(ref)] = rec
    pars = [holes[r].get("par") or 0 for r in refs]
    cpar = sum(card.get("par") or []) if card.get("par") else None
    out["course"] = dict(par_total=sum(pars), card_par_total=cpar, pars_ok=cpar is not None and cpar == sum(pars),
                         holes=len(refs), card_holes=len(card.get("yards") or []))
    json.dump(out, open(a.out, "w"), indent=1)
    n = sum(1 for v in out["holes"].values() if v["status"] == "PASS")
    print(f"{a.slug}/{a.which} ({base}): {n}/{len(out['holes'])} holes PASS; pars {sum(pars)} vs card {cpar}")


if __name__ == "__main__":
    main()
