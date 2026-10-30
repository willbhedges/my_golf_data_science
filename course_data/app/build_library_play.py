"""Compact play records for the library courses (golf_lib_play/1, SCHEMA.md "Library play records").

Each built library page (course_data/library/<slug>/page.html, a v2 wind page with gzip+base64 data) becomes one
small JSON file, out/lib/<slug>.json, that the app fetches by relative URL when a golfer opens the course:

  holes, tees per solved set, greens (par 3 outline + target boxes), the calm-day pick and aim per solved set,
  a per-hole wind table (pick, aim, landing distance and drift at 0 / 10 / 20 mph from 8 directions relative to
  the tee line, from the page's own grids at the middle grid temperature, with the page's calm-pick rule), the
  qa.json PASS / CHECK result per hole, the tee / green coordinates (for the shared confirm), and small hole
  images (JPEG, 300 px wide, quality 45).

  python3 course_data/app/build_library_play.py [--out course_data/app/out/lib] [--only slug,...]
Returns (from build()) {slug: {"file": "lib/<slug>.json", "bytes": n, "check_holes": [...], "holes": n}}.
"""
import argparse
import base64
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
LIBDIR = os.path.join(CD, "library")
OUT = os.path.join(HERE, "out", "lib")
IMG_W, IMG_Q, IMG_HMAX = 300, 42, 760
SPEEDS = [0, 10, 20]
DIRS8 = list(range(0, 360, 45))
HYPO = re.compile(r"not in bag", re.I)


def load_page(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'<script id="pg-data"[^>]*>(.*?)</script>', s, re.S)
    if m:
        return json.loads(gzip.decompress(base64.b64decode(m.group(1).strip())))
    m = re.search(r"const D = (\{.*?\});\n", s, re.S)
    return json.loads(m.group(1)) if m else None


def small_jpeg(uri):
    raw = base64.b64decode(uri.split(",", 1)[1])
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    k = min(IMG_W / im.width, IMG_HMAX / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=IMG_Q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode(), [im.width, im.height], k


def r1(x):
    return round(x * 2) / 2 if x is not None else None


def cell_vals(g, sp, d):
    """{club: (aim, ev, total, carry, drift)} at speed sp, relative direction d (any degree: linear in 30-deg cells)."""
    if sp == 0:
        return {c: (a[0], a[1], a[5], a[4], a[7]) for c, a in g["0_0"].items()}
    d0 = (d // 30) * 30
    d1 = (d0 + 30) % 360
    w = (d - d0) / 30
    A, B = g[f"{sp}_{d0}"], g[f"{sp}_{d1}"]
    return {c: tuple((1 - w) * A[c][i] + w * B[c][i] for i in (0, 1, 5, 4, 7)) for c in A}


def tee_table(h, temps, clubs):
    G = h["grids"]["0"]
    T = str(int(temps[1])) if str(int(temps[1])) in G else str(temps[1]) if str(temps[1]) in G else list(G)[len(G) // 2]
    g = G[T]
    elev = (h.get("elev") or {}).get("clubs") or {}
    calm = h.get("calm") or {}
    q0 = cell_vals(g, 0, 0)
    quick0 = min((c for c in q0 if not HYPO.search(c)), key=lambda c: q0[c][1])

    def land(c, v):                                     # elevation: carry change, roll factor, side kick
        aim, ev, tot, car, dr = v
        e = elev.get(c)
        kick = 0.0
        if e:
            roll = tot - car
            car += e["dc"]
            tot = car + roll * e["rf"]
            kick = e.get("kick") or 0.0
        return tot, dr + kick

    def entry(sp, d):
        q = cell_vals(g, sp, d)
        quick = min((c for c in q if not HYPO.search(c)), key=lambda c: q[c][1])
        if calm.get("pick") in q and quick == quick0:
            c = calm["pick"]
            aim = calm["aim"] + (q[c][0] - q0[c][0])
        else:
            c, aim = quick, q[quick][0]
        tot, dr = land(c, q[c])
        return [clubs.index(c), r1(aim), round(tot), round(dr, 1)]
    out = [entry(0, 0)]
    for sp in SPEEDS[1:]:
        for d in DIRS8:
            out.append(entry(sp, d))
    return out


def par3_table(h, S):
    plays = S.get("plays") or h.get("plays")

    def at(sp, d):
        if sp == 0:
            return plays["0_0"]
        d0 = (d // 30) * 30
        d1 = (d0 + 30) % 360
        w = (d - d0) / 30
        return (1 - w) * plays[f"{sp}_{d0}"] + w * plays[f"{sp}_{d1}"]
    return [round(at(0, 0))] + [round(at(sp, d)) for sp in SPEEDS[1:] for d in DIRS8]


def qa_holes(slug, set_of_which):
    p = os.path.join(LIBDIR, slug, "qa.json")
    if not os.path.exists(p):
        return {}
    q = json.load(open(p))
    out = {}
    for which, c in (q.get("checks") or {}).items():
        s = c.get("set") or set_of_which.get(which) or which
        for ref, hh in (c.get("holes") or {}).items():
            why = [f"{k}: {v.get('why')}" for k, v in (hh.get("checks") or {}).items() if not v.get("ok")]
            out.setdefault(s, {})[str(ref)] = [hh.get("status") or ("PASS" if not why else "CHECK"), why[:4]]
    return out


def build_one(slug, idx_row, out_dir):
    page = os.path.join(LIBDIR, slug, "page.html")
    D = load_page(page)
    if not D:
        return None
    pkg = json.load(open(os.path.join(LIBDIR, slug, "package.json")))
    ph = pkg.get("holes") or {}
    if isinstance(ph, list):
        ph = {str(x.get("ref")): x for x in ph}
    by_set = {D["base_set"]: D["holes"]}
    by_set.update(D.get("alt") or {})
    sets = [s for s in D["sets"] if s in by_set]
    clubs = []
    for hs in by_set.values():
        for h in hs:
            for c in (h.get("calm") or {}, ):
                pass
            if h.get("kind") == "tee":
                for c in h["grids"]["0"][list(h["grids"]["0"])[0]]["0_0"]:
                    if c not in clubs:
                        clubs.append(c)
    images, img_ids = {}, {}
    holes = []
    keys = []
    for h in D["holes"]:
        if h["key"] not in keys:
            keys.append(h["key"])
    for s in sets:
        for h in by_set[s]:
            if h["key"] not in keys:
                keys.append(h["key"])
    cfg = {}
    try:
        cfg = json.load(open(os.path.join(LIBDIR, slug, "config.json")))
    except Exception:                                   # noqa: BLE001
        pass
    which_of = {"auto": D["base_set"]}
    for s, w in (cfg.get("alt_bases") or {}).items():
        which_of[w] = s
    qa = qa_holes(slug, which_of)
    for key in keys:
        rec = None
        for s in sets:
            h = next((x for x in by_set[s] if x["key"] == key), None)
            if not h:
                continue
            p = ph.get(str(key)) or {}
            if rec is None:
                no = int(re.sub(r"\D", "", str(key)) or 0) or len(holes) + 1
                rec = dict(no=no, ref=str(key), par=h["par"], sets={})
                if p.get("green_ll"):
                    rec["green_ll"] = [round(v, 7) for v in p["green_ll"]]
            hid = hashlib.md5(h["img"][:20000].encode() + h["img"][-2000:].encode()).hexdigest()[:10]
            if hid not in img_ids:
                uri, hh, k = small_jpeg(h["img"])
                img_ids[hid] = (f"i{len(img_ids)}", hh, k)
                images[f"i{len(img_ids) - 1}"] = uri
            iid, ih, k = img_ids[hid]
            sk = h["s"] * k
            V = dict(yds=round(h["length"]), img=iid, w=ih[0], h=ih[1], bearing=h["bearing"], kind=h["kind"],
                     note=h.get("note", "")[:600])
            tee_ll = ((p.get("tees") or {}).get(s) or {}).get("tee_ll")
            if not tee_ll:
                t0 = next(iter((p.get("tees") or {}).values()), {})
                tee_ll = t0.get("tee_ll")
            if tee_ll:
                V["tee_ll"] = [round(v, 7) for v in tee_ll]
            sc = lambda pt: [round((pt[0] - h["x0"]) * sk, 1), round((pt[1] - h["y0"]) * sk, 1)]   # noqa: E731
            if h["kind"] == "tee":
                V.update(tee=sc(h["tee"]), f=h["f"], r=h["r"], ppy=round(h["ppy"] * sk, 4),
                         offimg=bool(h.get("tee_offimage")))
                if h.get("green_al"):
                    V["green_al"] = [round(v, 1) for v in h["green_al"]]
                calm = h.get("calm") or {}
                V["calm"] = dict(pick=calm.get("pick"), aim=calm.get("aim"), win=calm.get("window"), tie=bool(calm.get("tie")))
                V["wind"] = tee_table(h, D["temps"], clubs)
            else:
                S3 = (h.get("by_set") or {}).get(s) or dict(center=h["length"], boxes=h["boxes"], plays=h["plays"],
                                                          front=h.get("front"), back=h.get("back"))
                V.update(green=[sc(pt) for pt in h["green"]], center=round(S3["center"]), front=S3.get("front"),
                         back=S3.get("back"), short=h.get("short", ""),
                         boxes={m: dict(poly=[sc(pt) for pt in b["poly"]], play=round(b["play"]), lo=round(b["lo"]), hi=round(b["hi"]))
                                for m, b in S3["boxes"].items()},
                         plays=par3_table(h, S3))
            q = (qa.get(s) or {}).get(str(key))
            if q:
                V["qa"] = q
            rec["sets"][s] = V
        if rec:
            holes.append(rec)
    holes.sort(key=lambda r: r["no"])
    fc = D.get("forecast") or []
    days = D.get("days") or []
    rec = dict(schema="golf_lib_play/1", id=slug, name=idx_row.get("name") or D.get("title"),
               town=idx_row.get("city"), state=idx_row.get("state"), status=idx_row.get("status"),
               check_holes=idx_row.get("check_holes") or [], reasons=idx_row.get("reasons") or [],
               built=idx_row.get("built"), weather=idx_row.get("weather"),
               placeholder=bool(D.get("placeholder")), fc_note=D.get("fc_note"),
               days=[dict(key=d, label=(D.get("day_labels") or days)[i]) for i, d in enumerate(days)],
               hourly=[[days.index(r["date"]) if r["date"] in days else 0, r["hour"], round(r["mph"], 1), r.get("dir") or 0,
                        round(r.get("temp") or 65)] for r in fc if r.get("date") in days],
               tee_hour=D.get("tee_hour") or 9, temps=D.get("temps"),
               sets=[dict(name=s, colour=(D.get("colors") or {}).get(s, "#888"), total=(D.get("set_totals") or {}).get(s)) for s in sets],
               card_sets=[[t.get("name"), t.get("yards"), t.get("on_page")] for t in (idx_row.get("tee_sets") or [])],
               clubs=clubs, speeds=SPEEDS, dirs=DIRS8, imagery=D.get("imagery"),
               foot=D.get("foot_extra", ""), images=images, holes=holes)
    os.makedirs(out_dir, exist_ok=True)
    fn = os.path.join(out_dir, f"{slug}.json")
    with open(fn, "w") as fh:
        json.dump(rec, fh, separators=(",", ":"))
    return dict(file=f"lib/{slug}.json", bytes=os.path.getsize(fn), holes=len(holes), check_holes=rec["check_holes"],
                sets=[s["name"] for s in rec["sets"]])


def build(out_dir=OUT, only=None, log=print):
    idx = json.load(open(os.path.join(LIBDIR, "index.json")))
    res = {}
    for r in idx["courses"]:
        slug, pg = r.get("slug"), r.get("page")
        if not slug or not pg or r.get("group") != "library" or (only and slug not in only):
            continue
        if not os.path.exists(os.path.join(ROOT, pg)):
            continue
        fn = os.path.join(out_dir, f"{slug}.json")
        src = os.path.join(ROOT, pg)
        if os.path.exists(fn) and os.path.getmtime(fn) > max(os.path.getmtime(src), os.path.getmtime(__file__)):
            d = json.load(open(fn))
            res[slug] = dict(file=f"lib/{slug}.json", bytes=os.path.getsize(fn), holes=len(d["holes"]),
                             check_holes=d["check_holes"], sets=[s["name"] for s in d["sets"]])
            continue
        try:
            x = build_one(slug, r, out_dir)
        except Exception as e:                          # noqa: BLE001
            log(f"  lib {slug}: FAILED {e!r}")
            continue
        if x:
            res[slug] = x
            log(f"  lib {slug:24s} {x['bytes'] / 1e3:6.0f} kB  {x['holes']} holes  sets {x['sets']}")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only")
    a = ap.parse_args()
    r = build(a.out, set(a.only.split(",")) if a.only else None)
    print(f"{len(r)} courses, {sum(x['bytes'] for x in r.values()) / 1e6:.2f} MB")
    sys.exit(0 if r else 1)
