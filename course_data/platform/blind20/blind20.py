"""Blind loop: a fixed, seeded random draw of US courses (national tier mix), run one at a time through the automatic
course-page pipeline exactly as an app request, graded hole by hole. Protocol + scoreboard: platform/BLIND_LOOP.md.

  blind20.py sample            -> blind20.json (the fixed list and loop order; seed 20261109; do not re-run)
  blind20.py next [k]          -> writes the next k request files course_data/requests/course_page_b20_<slug>.json
                                  (commit + push one = one course-page run on Actions)
  blind20.py rerun slug.. | done -> bumps "rev" in those request files (commit + push = rebuild them)
  blind20.py status            -> the status.json rows of the courses built so far
  blind20.py timing RUN_ID..   -> timing.json (job and step minutes by stage, from the Actions API through `gh`)
  blind20.py sheets slug..     -> course_data/requests/blind_sheets.json (commit + push = grading renders on Actions:
                                  blind20_sheets.py on a fresh NAIP fetch -> blind20/sheets/<slug>/*.jpg)

Outputs: course_data/library/gate/gate_b20_<slug>/ (group "gate": same pipeline, never in index.json or the app).
"""
import collections
import glob
import gzip
import json
import math
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(CD)
SEED = 20261109
N = 20
REPO = "willbhedges/my_golf_data_science"
sys.path.insert(0, os.path.join(CD, "library"))


def rj(p, default=None):
    try:
        return json.load(open(p))
    except Exception:                                               # noqa: BLE001
        return default


def rows():
    d = json.load(gzip.open(os.path.join(CD, "library", "us_courses.json.gz")))
    return [dict(zip(d["fields"], r)) for r in d["rows"]]


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"['’]", "", s)
    s = re.sub(r"\b(golf|course|club|country|and|the|cc|gc|links|resort|at|of)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def known():
    """every course the project has already seen: OSM ids, centres [lat, lon] and slugs"""
    ids, pts, slugs = set(), [], set()

    def walk(o):
        if isinstance(o, dict):
            v = o.get("osm")
            if isinstance(v, str) and re.fullmatch(r"(way|relation|node)/\d+", v):
                ids.add(v)
            elif isinstance(v, dict) and v.get("type") and v.get("id"):
                ids.add(f"{v['type']}/{v['id']}")
            c = o.get("center") or o.get("centre")
            if isinstance(c, list) and len(c) == 2 and all(isinstance(x, (int, float)) for x in c):
                a, b = c
                pts.append((a, b) if 17 < a < 72 else (b, a))
            near = o.get("near")
            if isinstance(near, str) and re.fullmatch(r"-?[\d.]+,-?[\d.]+", near):
                pts.append(tuple(float(x) for x in near.split(",")))
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    pats = ["library/index.json", "library/*/status.json", "library/gate/*/status.json", "library/*/raw/course.json",
            "library/osm_check/*.json", "packages/*/raw/course.json", "packages/*/package.json", "requests/*.json",
            "zero_tap/selection.json", "zero_tap/benchmark.json", "zero_tap/surveys/*.json", "truth_sets_v2/index.json",
            "zero_tap/truth_sets/*.json", "structure/data/*/course.json", "structure/*.json", "generalize/*.json",
            "zero_tap/osm_check/*.json", "zero_tap/unmapped/eval/*.json", "truth/*/course.json", "tees/*.json"]
    for pat in pats:
        for f in glob.glob(os.path.join(CD, pat)):
            if "b20_" in f or "blind20" in f or os.path.getsize(f) > 30e6:
                continue
            walk(rj(f))
    for d in ("library", "library/gate", "courses", "packages", "truth", "truth_sets_v2", "structure/data",
              "zero_tap/data", "zero_tap/truth", "vision_any", "mapper", "ob", "vision_any/s2"):
        p = os.path.join(CD, d)
        if os.path.isdir(p):
            for n in os.listdir(p):
                n = re.sub(r"\.json$", "", n)
                if n.startswith("gate_b20_") or n.startswith("b20_"):
                    continue
                slugs.add(re.sub(r"^gate_", "", n))
    return ids, pts, slugs


def km(a, b):
    return math.hypot((a[0] - b[0]) * 111.32, (a[1] - b[1]) * 111.32 * math.cos(math.radians(a[0])))


def slug_of(name):
    import requests_to_batch
    return requests_to_batch.slug_of(name)


def sample():
    R = [r for r in rows() if not r["closed"]]
    R.sort(key=lambda r: (r["state"], r["name"], r["osm"]))
    n_all = len(R)
    mix = collections.Counter(r["tier"] for r in R)
    # largest-remainder allocation of 20 to the national tier mix
    quota = {t: N * mix[t] / n_all for t in "ABCD"}
    alloc = {t: int(quota[t]) for t in quota}
    for t in sorted(quota, key=lambda t: quota[t] - alloc[t], reverse=True)[:N - sum(alloc.values())]:
        alloc[t] += 1
    ids, pts, slugs = known()
    st_slugs = set()
    for s in slugs:
        st_slugs.add(s)
        st_slugs.add(re.sub(r"_[a-z]{2}$", "", s))

    def seen(r):
        if r["osm"] in ids:
            return "osm id"
        if any(km((r["lat"], r["lon"]), p) < 2.0 for p in pts):
            return "within 2 km of a known course"
        s = slug_of(r["name"])
        if s in st_slugs or norm(r["name"]) in st_slugs:
            return "slug"
        return None

    rng = random.Random(SEED)
    out, excluded = [], []
    for t in "ABCD":
        pool = [r for r in R if r["tier"] == t]
        rng.shuffle(pool)
        got = 0
        for r in pool:
            if got == alloc[t]:
                break
            why = seen(r)
            if why:
                excluded.append(dict(name=r["name"], state=r["state"], tier=t, why=why))
                continue
            got += 1
            out.append(dict(r, n=len(out) + 1, slug="b20_" + slug_of(r["name"])[:40]))
    # slugs unique
    used = collections.Counter(c["slug"] for c in out)
    for c in out:
        if used[c["slug"]] > 1:
            c["slug"] += "_" + c["state"].lower()
    doc = dict(schema="blind20/1", seed=SEED, frame=dict(n=n_all, tiers=dict(mix), source="course_data/library/us_courses.json.gz (closed rows dropped)"),
               alloc=alloc, known=dict(osm_ids=len(ids), centres=len(pts), slugs=len(slugs)),
               drawn_then_excluded=excluded, courses=out)
    # loop order: a seeded shuffle, so any window of the loop is near the national tier mix
    random.Random(SEED + 1).shuffle(out)
    for i, c in enumerate(out):
        c["order"] = i + 1
    json.dump(doc, open(os.path.join(HERE, "blind20.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(alloc=alloc, frame=mix, excluded=excluded), ensure_ascii=False))
    for c in out:
        print(c["order"], c["tier"], c["slug"], "|", c["name"], "|", c["city"], c["state"], c["osm"], "holes", c["holes"],
              "osm_holes", c["osm_holes"], "greens", c["greens"], "tees", c["tees"], "card", c["card"])


def the20():
    return rj(os.path.join(HERE, "blind20.json"))["courses"]


def request_path(c):
    return os.path.join(CD, "requests", f"course_page_{c['slug']}.json")


def nxt(k=1):
    """write the request file(s) of the next k courses of the loop: exactly what the app's "Request this course" +
    requests_to_batch.py write (name, city, state, osm, near), with group "gate" so the page stays out of the library
    index and the app. Pushing the file starts one course-page run."""
    made = []
    for c in the20():
        p = request_path(c)
        if os.path.exists(p):
            continue
        q = {"schema": "course_page/1", "name": c["name"], "state": c["state"], "slug": c["slug"], "group": "gate",
             "rev": 1, "source": "blind loop (course_data/platform/BLIND_LOOP.md): as an app request",
             "city": c["city"], "osm": c["osm"], "near": f"{c['lat']:.5f},{c['lon']:.5f}"}
        if not q["city"]:
            del q["city"]
        json.dump(q, open(p, "w"), indent=1, ensure_ascii=False)
        made.append(os.path.relpath(p, ROOT))
        print(c["order"], c["tier"], made[-1])
        if len(made) >= k:
            break
    return made


def rerun(slugs):
    """bump "rev" in the request files of the named courses ("done" = every course already requested): commit + push
    those files = one course-page run that rebuilds them"""
    out = []
    for c in the20():
        p = request_path(c)
        if not os.path.exists(p) or not (c["slug"] in slugs or c["slug"][4:] in slugs or "done" in slugs):
            continue
        q = rj(p)
        q["rev"] = int(q.get("rev") or 1) + 1
        json.dump(q, open(p, "w"), indent=1, ensure_ascii=False)
        out.append(os.path.relpath(p, ROOT))
    print("git add " + " ".join(out))


def out_dir(c):
    return os.path.join(CD, "library", "gate", "gate_" + c["slug"])


def status():
    for c in the20():
        s = rj(os.path.join(out_dir(c), "status.json")) or {}
        print(f"{c['order']:2d} {c['tier']} {c['slug'][4:]:32s} {str(s.get('status')):14s} holes {str(s.get('holes')):4s} "
              f"check {len(s.get('check_holes') or []):2d} | {'; '.join(s.get('reasons') or [])[:150]}")


def timing(run_ids):
    import datetime as D
    f = lambda x: D.datetime.fromisoformat(x.replace("Z", "+00:00"))
    by = {}
    runs = []
    for rid in run_ids:
        js, page = [], 1
        while True:
            o = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPO}/actions/runs/{rid}/jobs?per_page=100&page={page}"]))
            js += o["jobs"]
            if len(js) >= o["total_count"] or not o["jobs"]:
                break
            page += 1
        r = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPO}/actions/runs/{rid}"]))
        runs.append(dict(id=rid, created=r["created_at"], updated=r["updated_at"], conclusion=r["conclusion"]))
        for j in js:
            if not j.get("started_at") or not j.get("completed_at"):
                continue
            m = re.search(r"(b20_[a-z0-9_]+)", j["name"])
            slug = m.group(1) if m else "_run"
            stage = j["name"].split(" / ")[-1].split(" (")[0].strip()
            if stage == "compute":
                mm = re.search(r", (\d), (wind|decide)\)", j["name"]) or re.search(r", (\d), (\w+)", j["name"].split(" / ")[-1])
                stage = f"compute {mm.group(2)}{mm.group(1)}" if mm else "compute"
            mins = (f(j["completed_at"]) - f(j["started_at"])).total_seconds() / 60
            wait = (f(j["started_at"]) - f(j["created_at"])).total_seconds() / 60
            steps = {s["name"]: round((f(s["completed_at"]) - f(s["started_at"])).total_seconds() / 60, 2)
                     for s in j.get("steps") or [] if s.get("started_at") and s.get("completed_at")}
            by.setdefault(slug, {})[stage] = dict(min=round(mins, 1), queued=round(wait, 1), result=j["conclusion"], steps=steps, run=rid)
    p = os.path.join(HERE, "timing.json")
    old = rj(p) or {"runs": [], "courses": {}}
    old["runs"] = [r for r in old["runs"] if r["id"] not in run_ids] + runs
    old["courses"].update(by)
    json.dump(old, open(p, "w"), indent=1)
    for s, st in sorted(by.items()):
        print(s, {k: v["min"] for k, v in st.items()}, "total", round(sum(v["min"] for v in st.values()), 1))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sample":
        sample()
    elif cmd == "next":
        nxt(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    elif cmd == "rerun":
        rerun(sys.argv[2:])
    elif cmd == "status":
        status()
    elif cmd == "timing":
        timing(sys.argv[2:])
    elif cmd == "sheets":
        # request the grading sheets of the named courses (commit + push the file = one blind-sheets run)
        f = os.path.join(CD, "requests", "blind_sheets.json")
        d = rj(f) or {"rev": 0}
        d = dict(slugs=[s if s.startswith("b20_") else "b20_" + s for s in sys.argv[2:]], rev=d["rev"] + 1,
                 note="blind loop grading renders (.github/workflows/blind_sheets.yml)")
        json.dump(d, open(f, "w"), indent=1)
        print("git add", os.path.relpath(f, ROOT))
    else:
        print(__doc__)
