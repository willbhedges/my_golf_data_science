"""Tee-frame landing patterns for an already built library page, offline (no imagery, no GitHub run).

  python3 course_data/library/landing_cache.py [--only slug,...] [--jobs 4] [--swings 3000]
      -> course_data/library/<slug>/landing.json

The app's library play records (course_data/app/build_library_play.py) draw each club's landing pattern from the
page's clouds. Pages built before 2026-11-03 carry build_page_v2's covariance-eigen cloud (a near circle, see
landing_pattern.py), and the play records had none (a fixed 60 x 28 yd oval for every club). Rebuilding every page
needs the imagery (a GitHub run per course); the pattern does not: it needs only the course module (written from
the package, as v2_course prepare does, minus the hole pictures), the v2 engine and the page's own calm grids (the
aim, carry, total and width the page draws at). So this re-runs exactly landing_pattern.page_cloud for every solved
set's tee shots, every club, at the page's calm temperature, and stores

  {"schema": "golf_landing/1", "page": <md5 of the page's data>, "swings": n,
   "sets": {set: {hole key: {club: [dA, dL, long, short, left, right, tilt]}}}}

dA / dL: the pattern's centre relative to the landing point the page computes (calm total incl. elevation; aim +
slope kick), as the page cloud's. build_library_play uses it only while "page" matches the page it reads (a rebuilt
page carries the shape in its own clouds). One process per (course, solved set): the v2 engine binds one course
module per process.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
VC_PY = os.path.join(CD, "courses", "v2_course.py")
SCHEMA = "golf_landing/1"
FIELDS = ("dA", "dL", "long", "short", "left", "right", "tilt")


def page_data(slug):
    s = open(os.path.join(HERE, slug, "page.html"), encoding="utf-8").read()
    m = re.search(r'<script id="pg-data"[^>]*>(.*?)</script>', s, re.S)
    if not m:
        return None, None
    raw = m.group(1).strip()
    return json.loads(gzip.decompress(base64.b64decode(raw))), hashlib.md5(raw.encode()).hexdigest()


def solved_sets(D, cfg):
    """[(set, which, holes)] for the page's base set and each alt base it shows."""
    out = [(D["base_set"], cfg.get("main_which", "auto"), D["holes"])]
    for s, w in (cfg.get("alt_bases") or {}).items():
        if s in (D.get("alt") or {}):
            out.append((s, w, D["alt"][s]))
    return out


def worker(slug, which, set_name, holes, swings):
    """Child process: module from the package, the v2 engine on it, page_cloud per tee hole -> {key: {club: row}}."""
    sys.path[:0] = [HERE, os.path.join(CD, "courses")]
    import landing_pattern as LP
    import v2_course as VC
    cfg = VC.config(slug)
    PK = VC.product_pk()
    C = PK.load(os.path.join(ROOT, cfg["package"]), set_name)
    out_dir = VC.cdir(slug, which)
    os.makedirs(out_dir, exist_ok=True)
    PK.write_module(C, os.path.join(out_dir, "course.py"))
    json.dump(dict(tee_set=C.tee_set, holes={}), open(os.path.join(out_dir, "meta.json"), "w"))
    course, meta, M, _ = VC.activate(slug, which)
    res = {}
    for h in holes:
        if h.get("kind") != "tee":
            continue
        k = int(h["key"]) if str(h["key"]).isdigit() else h["key"]
        if k not in M.HOLES:
            continue
        G = (h.get("grids") or {}).get("0") or {}
        if not G:
            continue
        temp = (h.get("calm") or {}).get("temp") or M.hole_temp(k)
        T = min(G, key=lambda x: abs(float(x) - float(temp)))
        clubs = {c: dict(aim=v[0], carry=v[4], total=v[5], width=v[6]) for c, v in G[T]["0_0"].items()}
        cl = LP.page_cloud(M, k, {"clubs": clubs}, float(T), n=swings)
        res[str(h["key"])] = {c: [x[f] for f in FIELDS] for c, x in cl.items()}
    return res


def run_set(slug, which, set_name, swings):
    """One (course, set) in a child process with a scratch courses dir (nothing written under the library)."""
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, slug))
        shutil.copy(os.path.join(HERE, slug, "config.json"), os.path.join(td, slug, "config.json"))
        env = dict(os.environ, V2_COURSES_DIR=td, OMP_NUM_THREADS="1")
        out = os.path.join(td, "out.json")
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", slug, which, set_name,
                            "--swings", str(swings), "--child-out", out], env=env, capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"{slug} {set_name}: {r.stderr.strip().splitlines()[-1:] or r.returncode}")
        return json.load(open(out))


def build_course(slug, swings, log=print):
    D, sig = page_data(slug)
    if not D:
        return None
    cfg = json.load(open(os.path.join(HERE, slug, "config.json")))
    sets = {}
    for s, w, _ in solved_sets(D, cfg):
        sets[s] = run_set(slug, w, s, swings)
    rec = dict(schema=SCHEMA, page=sig, swings=swings, fields=list(FIELDS), sets=sets)
    json.dump(rec, open(os.path.join(HERE, slug, "landing.json"), "w"), separators=(",", ":"))
    log(f"{slug}: {', '.join(f'{s} {len(v)} holes' for s, v in sets.items())}")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--swings", type=int, default=3000)
    ap.add_argument("--skip-current", action="store_true", help="skip courses whose landing.json matches the page")
    ap.add_argument("--child", nargs=3)
    ap.add_argument("--child-out")
    a = ap.parse_args()
    if a.child:
        slug, which, set_name = a.child
        D, _ = page_data(slug)
        cfg = json.load(open(os.path.join(HERE, slug, "config.json")))
        holes = next(h for s, w, h in solved_sets(D, cfg) if s == set_name)
        json.dump(worker(slug, which, set_name, holes, a.swings), open(a.child_out, "w"))
        return
    slugs = a.only.split(",") if a.only else sorted(
        d for d in os.listdir(HERE) if os.path.exists(os.path.join(HERE, d, "page.html")))
    if a.skip_current:
        def current(s):
            p = os.path.join(HERE, s, "landing.json")
            return os.path.exists(p) and json.load(open(p)).get("page") == page_data(s)[1]
        slugs = [s for s in slugs if not current(s)]

    def one(s):
        try:
            return build_course(s, a.swings)
        except Exception as e:                          # noqa: BLE001 (one course never stops the rest)
            print(f"{s}: FAILED {e}", file=sys.stderr)
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(one, slugs))


if __name__ == "__main__":
    main()
