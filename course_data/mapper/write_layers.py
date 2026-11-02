"""The mapper agent's edits.json (yard frame) -> agent_zones.geojson + agent_tees.json (WGS84), plus review renders.

  python3 course_data/mapper/write_layers.py <slug> [--no-render]

Reads course_data/mapper/<slug>/edits.json (schema mapper_edits/1, see BRIEF.md) and frames.json, validates every
edit, converts shapes to WGS84 polygons with the hole's corridor frame, and writes in the same folder:
  agent_zones.geojson   one feature per zone edit (op add / erase / grow), applied in file order by apply.py
  agent_tees.json       every tee the agent checked: keep, or move (to a point read off the tee sheet)
  review.md             per hole: AUTO -> AUTO+AGENT visible area per lie in the landing zone (180-330, +/-50),
                        tee moves (yds, measured length vs card)
  render/hNN_review.png [AUTO] [AUTO + AGENT] [the edits on the 2nd NAIP year: add = lie colour, erase = magenta,
                        grow region = cyan] (not committed)
Fails loudly on a bad edit (unknown lie / op / shape, a shape outside the window, a move without evidence).

Guards from the blind evaluation (course_data/mapper/BRIEF.md "Rules from the evaluation"), applied here so every
mapper gets them:
  * native keep-out: an `add native` that is not confidence "high" loses the part within NATIVE_KEEPOUT yds of the
    package fairway / first cut / green (mown rough is the default next to a fairway; a thin strip of "native"
    hugging the fairway was the main cause of wrong clubs). High-confidence native is kept but listed.
  * warnings (review.md "Checks", not fatal): sand drawn over tree canopy (sand wins over trees in the lie
    precedence), a large tree polygon over mostly open ground (scattered crowns drawn as a stand), native
    strips with w < NATIVE_KEEPOUT.
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as M  # noqa: E402


class EditError(ValueError):
    pass


NATIVE_KEEPOUT = 10.0       # yds from the package fairway: unsure native never comes closer
STAND_MIN_YD2 = 600.0       # a tree polygon this big ...
STAND_MIN_CANOPY = 0.35     # ... with less than this share on the auto (lidar) canopy: warn
SAND_ON_CANOPY = 0.3        # sand add with more than this share on the auto canopy: warn


def _mown(fj, h):
    from shapely.ops import unary_union
    fw = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h, ("fairway", "first_cut", "green"))]
    return unary_union(fw).buffer(0) if fw else None


def _canopy(fj, h):
    from shapely.ops import unary_union
    tr = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h, ("recovery",))]
    return unary_union(tr).buffer(0) if tr else None


def _geo(g, fj):
    """shapely (x, along) -> GeoJSON Polygon / MultiPolygon in WGS84."""
    ps = M.polys_of(g, 1.0)
    rings = []
    for p in ps:
        ext = M.xy_to_ll(fj, np.asarray(p.exterior.coords))
        holes = [M.xy_to_ll(fj, np.asarray(i.coords)) for i in p.interiors]
        rings.append([[[round(float(x), 7), round(float(y), 7)] for x, y in r] for r in [ext] + holes])
    if not rings:
        return None
    return dict(type="Polygon", coordinates=rings[0]) if len(rings) == 1 else dict(type="MultiPolygon", coordinates=rings)


def build(slug, ed, pkg, FJ, TF):
    feats, tees, problems = [], {}, []
    reviewed = {}
    win = M.window(pad=10.0)
    for ref, he in sorted((ed.get("holes") or {}).items(), key=lambda kv: M.hole_key(kv[0])):
        if ref not in FJ:
            problems.append(f"hole {ref}: not a corridor hole (par 3 or not framed): zone edits ignored")
            continue
        fj, h = FJ[ref], pkg["holes"][ref]
        bad = [x for x in he.get("reviewed") or [] if x not in M.LAYERS]
        if bad:
            raise EditError(f"hole {ref}: reviewed {bad} not in {M.LAYERS}")
        reviewed[ref] = dict(layers=he.get("reviewed") or [], confidence=he.get("confidence"), note=he.get("note"))
        for i, e in enumerate(he.get("edits") or []):
            where = f"hole {ref} edit {i}"
            op = e.get("op")
            if op not in M.OPS:
                raise EditError(f"{where}: op {op!r} not in {M.OPS}")
            lies = e.get("lies") or ([e["lie"]] if e.get("lie") else [])
            if not lies or any(lie not in M.LIES for lie in lies):
                raise EditError(f"{where}: lie(s) {lies} not in {M.LIES}")
            if op in ("add", "grow") and len(lies) != 1:
                raise EditError(f"{where}: {op} takes one lie")
            if e.get("confidence") and e["confidence"] not in M.CONF:
                raise EditError(f"{where}: confidence {e['confidence']!r} not in {M.CONF}")
            try:
                g = M.shape_geom(e.get("shape"), fj, h)
            except (ValueError, KeyError, TypeError) as x:
                raise EditError(f"{where}: {x}") from x
            if g.is_empty or g.area < 1:
                problems.append(f"{where}: empty shape, skipped")
                continue
            inside = g.intersection(win)
            if inside.area < 0.5 * g.area:
                raise EditError(f"{where}: shape mostly outside the window (x +/-{M.WIN['lat']:g}, along "
                                f"{M.WIN['a0']:g}-{M.WIN['a1']:g}); check x / along order ([x, along])")
            clipped = 0.0
            if op == "add" and lies[0] == "native":
                mown = _mown(fj, h)
                near = inside.intersection(mown.buffer(NATIVE_KEEPOUT)).area if mown is not None else 0.0
                if near >= 1 and e.get("confidence") != "high":
                    inside = inside.difference(mown.buffer(NATIVE_KEEPOUT))
                    clipped = near
                    problems.append(f"{where}: native within {NATIVE_KEEPOUT:g} yds of the fairway removed ({near:.0f} sq yds; "
                                    f"confidence is not high): keep it only with a crisp tall-grass edge in both years")
                    if inside.area < 1:
                        continue
                elif near >= 25:
                    problems.append(f"{where}: high-confidence native within {NATIVE_KEEPOUT:g} yds of the fairway "
                                    f"({near:.0f} sq yds): check the edge on both years (it changes clubs)")
                sh = (e.get("shape") or {}).get("beyond_fairway")
                if sh and not clipped and float(sh.get("w", 10.0)) < NATIVE_KEEPOUT:
                    problems.append(f"{where}: beyond_fairway w={sh.get('w')} (< {NATIVE_KEEPOUT:g}): mown rough is "
                                    f"usually wider; measure it")
            if op == "add" and lies[0] == "sand":
                can = _canopy(fj, h)
                if can is not None and inside.area > 0 and inside.intersection(can).area > SAND_ON_CANOPY * inside.area:
                    problems.append(f"{where}: {100 * inside.intersection(can).area / inside.area:.0f}% of the sand lies on "
                                    f"the tree canopy (sand wins over trees): draw only open sand, outside the crowns")
            if op == "add" and lies[0] == "recovery" and inside.area >= STAND_MIN_YD2:
                can = _canopy(fj, h)
                share = inside.intersection(can).area / inside.area if can is not None else 0.0
                if share < STAND_MIN_CANOPY:
                    problems.append(f"{where}: tree polygon of {inside.area:.0f} sq yds with only {100 * share:.0f}% on the "
                                    f"lidar canopy: if the crowns stand apart with grass between, draw each crown (ell)")
            if op == "grow" and not e.get("by"):
                raise EditError(f"{where}: grow needs 'by' (yds, negative shrinks)")
            geo = _geo(inside, fj)
            if geo is None:
                continue
            props = dict(hole=ref, op=op, lie=lies[0], edit=f"{ref}.{i}", area_yd2=round(inside.area))
            if clipped:
                props["keepout_clipped_yd2"] = round(clipped)
            if op == "erase":
                props["lies"] = lies
            if op == "grow":
                props["by"] = float(e["by"])
            for k in ("note", "confidence", "evidence"):
                if e.get(k):
                    props[k] = e[k]
            feats.append(dict(type="Feature", properties=props, geometry=geo))
    for ref, by_set in sorted((ed.get("tees") or {}).items(), key=lambda kv: M.hole_key(kv[0])):
        h = pkg["holes"].get(ref)
        if h is None:
            problems.append(f"tees hole {ref}: not in the package")
            continue
        for s, e in by_set.items():
            act = (e or {}).get("action") or ""
            if not act:
                continue
            if act not in ("keep", "move"):
                raise EditError(f"tees {ref} {s}: action {act!r} (keep | move)")
            t = (h.get("tees") or {}).get(s)
            if t is None:
                raise EditError(f"tees {ref} {s}: no such set on this hole ({list(h.get('tees') or {})})")
            rec = dict(action=act, auto_ll=t["tee_ll"], auto_method=t.get("method"), confidence=e.get("confidence"),
                       evidence=e.get("evidence"))
            if act == "move":
                if not e.get("evidence"):
                    raise EditError(f"tees {ref} {s}: a move needs evidence (what box is visible where)")
                if e.get("to_ll"):
                    ll = [float(e["to_ll"][0]), float(e["to_ll"][1])]
                elif e.get("to") is not None:
                    fj = TF.get(ref) or FJ.get(ref)
                    ll = M.xy_to_ll(fj, [e["to"]])[0].tolist()
                else:
                    raise EditError(f"tees {ref} {s}: move needs 'to': [x, along] (tee sheet frame) or 'to_ll'")
                rec["tee_ll"] = [round(ll[0], 7), round(ll[1], 7)]
                rec["moved_yd"] = round(M.yd_between(rec["tee_ll"], t["tee_ll"]), 1)
                if rec["moved_yd"] > 120:
                    raise EditError(f"tees {ref} {s}: moved {rec['moved_yd']:.0f} yds (> 120): wrong frame or hole?")
            tees.setdefault(ref, {})[s] = rec
    return feats, tees, reviewed, problems


def native_gaps(pkg, out, FJ, a0=180, a1=330, step=5, reach=45):
    """{ref: {"L": "min / median", "R": ...}}: lateral gap from the base fairway edge to the visible native
    (after precedence) on each side, sampled every `step` yds along."""
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    res = {}
    for ref, fj in FJ.items():
        h0, h1 = pkg["holes"][ref], out["holes"][ref]
        nat = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h1, ("native",))]
        if not nat:
            continue
        above = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h1, ("recovery", "ob", "first_cut", "fairway", "green",
                                                                    "water", "sand"))]
        g = unary_union(nat).buffer(0)
        if above:
            g = g.difference(unary_union(above).buffer(0))
        mown = _mown(fj, h0)
        row = {}
        for side, sgn in (("L", -1), ("R", 1)):
            d = []
            for a in range(a0, a1 + 1, step):
                ln = LineString([(0, a), (sgn * reach, a)])
                it = g.intersection(ln)
                if it.is_empty:
                    continue
                xs = [abs(c[0]) for p in getattr(it, "geoms", [it]) for c in p.coords]
                fw = mown.intersection(ln) if mown is not None else None
                fx = 0.0                     # outer edge of the fairway piece(s) that start near the line
                if fw is not None and not fw.is_empty:
                    for p in getattr(fw, "geoms", [fw]):
                        cx = [abs(c[0]) for c in p.coords]
                        if cx and min(cx) < 15:
                            fx = max(fx, max(cx))
                d.append(max(0.0, min(xs) - fx))
            row[side] = f"{min(d):.0f} / {float(np.median(d)):.0f}" if d else "-"
        if row["L"] != "-" or row["R"] != "-":
            res[ref] = row
    return res


def review_md(slug, pkg, out, FJ, rep, tees, problems):
    import render_inputs as RI
    L = [f"# Mapper review: {pkg['course']['name']}", "",
         f"Applied with apply.py: {out['stages']['agent_layers']}", "",
         "| hole | edits | landing zone AUTO (sq yds) | AUTO + AGENT |", "|---|---|---|---|"]
    for ref, fj in FJ.items():
        a = RI.landing_areas(fj, pkg["holes"][ref])
        b = RI.landing_areas(fj, out["holes"][ref])
        s = (rep["holes"].get(ref) or {}).get("summary", "")
        if a != b or s:
            L.append(f"| {ref} | {s} | {', '.join(f'{k} {v}' for k, v in sorted(a.items())) or '-'} | "
                     f"{', '.join(f'{k} {v}' for k, v in sorted(b.items())) or '-'} |")
    L += ["", "## Tees", "", "| hole | set | action | moved yds | card | measured after | evidence |", "|---|---|---|---|---|---|---|"]
    for ref, by in tees.items():
        for s, r in by.items():
            t = out["holes"][ref]["tees"][s]
            L.append(f"| {ref} | {s} | {r['action']} | {r.get('moved_yd', '')} | {t.get('card_yards')} | "
                     f"{t.get('measured_yards')} | {(r.get('evidence') or '')[:80]} |")
    gaps = native_gaps(pkg, out, FJ)
    if gaps:
        L += ["", "## Native gap to the fairway (180-330 yds along; min / median yds per side, '-' = none)", "",
              "| hole | left | right |", "|---|---|---|"]
        for ref, g in gaps.items():
            L.append(f"| {ref} | {g['L']} | {g['R']} |")
    if problems:
        L += ["", "## Checks and problems", ""] + [f"- {p}" for p in problems]
    open(M.mdir(slug, "review.md"), "w").write("\n".join(L) + "\n")


def render_review(slug, pkg, out, FJ, feats, holes=None):
    import corridor as C
    import cv2
    import render_inputs as RI
    S = C.sources(slug)
    a0, a1, lat = M.WIN["a0"], M.WIN["a1"], M.WIN["lat"]
    ys, py = RI.other_years(S)
    edited = sorted({f["properties"]["hole"] for f in feats}, key=M.hole_key)
    for ref in edited:
        if holes and ref not in holes:
            continue
        fj = FJ[ref]
        fr = RI.frame(fj, RI.PPY, a0, a1, lat)
        photo = C._u8(S["photo"].warp(fr))
        before = RI.zones_for_draw(fj, pkg["holes"][ref])
        after = RI.zones_for_draw(fj, out["holes"][ref])
        P = [C.title(RI.gridw(RI.draw(photo, fr, before, a1, lat), fr, a0, a1, lat), f"{slug} {ref}: AUTO", 0.4),
             C.title(RI.gridw(RI.draw(photo, fr, after, a1, lat), fr, a0, a1, lat), "AUTO + AGENT (as the planner sees it)", 0.4)]
        base = C._u8(S[ys[0]].warp(fr)[..., :3]) if ys else photo.copy()
        img = base.copy()
        for f in feats:
            p = f["properties"]
            if p["hole"] != ref:
                continue
            g = f["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            col = (255, 0, 255) if p["op"] == "erase" else (0, 255, 255) if p["op"] == "grow" else C.COL[p["lie"]]
            for poly in polys:
                xy = M.ll_to_xy(fj, poly[0])
                q = np.c_[(xy[:, 0] + lat) * fr.ppy, (a1 - xy[:, 1]) * fr.ppy]
                cv2.polylines(img, [np.round(q * 8).astype(np.int32)], True, (0, 0, 0), 4, shift=3)
                cv2.polylines(img, [np.round(q * 8).astype(np.int32)], True, col, 2, shift=3)
                m = q.mean(0).astype(int)
                cv2.putText(img, f"{p['edit']} {p['op']}", (int(m[0]), int(m[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 3)
                cv2.putText(img, f"{p['edit']} {p['op']}", (int(m[0]), int(m[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.4, col, 1)
        P.append(C.title(RI.gridw(img, fr, a0, a1, lat), "edits (add = lie colour, erase = magenta, grow = cyan)"
                         + (f" on {S[ys[0]].label}" if ys else ""), 0.4))
        C.save(M.mdir(slug, "render", f"h{int(ref):02d}_review.png"), C.stack(P, 3))
        M.log(f"  review render {ref}")


def run(slug, render=True, holes=None):
    import apply as AP
    ed = M.rj(M.mdir(slug, "edits.json"))
    if ed is None:
        raise SystemExit(f"no course_data/mapper/{slug}/edits.json (copy edits.template.json and fill it in)")
    fjson = M.rj(M.mdir(slug, "frames.json"))
    FJ, TF = fjson["holes"], fjson.get("tee_frames") or {}
    pkg = M.load_base(slug)
    if pkg.get("built") != fjson.get("base_built"):
        M.log(f"! the base package was rebuilt after the renders ({fjson.get('base_built')} -> {pkg.get('built')}): "
              f"edits are in the old frames (still exact on the ground; check tees)")
    feats, tees, reviewed, problems = build(slug, ed, pkg, FJ, TF)
    made = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    common = dict(slug=slug, mapper=ed.get("mapper"), made=made, corridor_set=fjson.get("set"),
                  base_package=fjson.get("base_package"), base_built=fjson.get("base_built"),
                  minutes=ed.get("minutes"), edits_sha=M.sha1_file(M.mdir(slug, "edits.json")))
    M.wj(M.mdir(slug, AP.ZONE_FILE), dict(type="FeatureCollection", properties=dict(
        common, schema="agent_zones/1", reviewed=reviewed, uncertain=ed.get("uncertain") or [],
        doc="Mapper agent zone edits (course_data/mapper/BRIEF.md), WGS84; applied in order by course_data/mapper/apply.py"),
        features=feats))
    M.wj(M.mdir(slug, AP.TEE_FILE), dict(common, schema="agent_tees/1", holes=tees))
    out, rep = AP.apply(pkg, M.mdir(slug))
    review_md(slug, pkg, out, FJ, rep, tees, problems)
    M.log(out["stages"]["agent_layers"])
    for p in problems:
        M.log("  ! " + p)
    if render:
        render_review(slug, pkg, out, FJ, feats, holes)
    M.log(f"-> {os.path.relpath(M.mdir(slug), M.ROOT)}/agent_zones.geojson ({len(feats)} edits), agent_tees.json "
          f"({sum(len(v) for v in tees.values())} tees), review.md")
    return out, rep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--holes")
    a = ap.parse_args()
    try:
        run(a.slug, not a.no_render, set(a.holes.split(",")) if a.holes else None)
    except EditError as e:
        raise SystemExit(f"edits.json: {e}")


if __name__ == "__main__":
    main()
