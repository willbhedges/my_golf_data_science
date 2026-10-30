"""App "Request this course" docs -> course_page request files + one course_batch file (README "Requests").

  python course_data/library/requests_to_batch.py requests.json [--name nov01] [--max 10] [--dry-run]

requests.json: the app's shared db collection "requests" as exported (ArtifactData list / query output, a list of
docs, {"docs": [...]} or {"documents": [{"id", "data"}]}). Each doc (golf_request/1):
  {slug, name, city, state, osm, lat, lon, holes, requested_at, user_id}

Courses are grouped by OSM id (else state + slug), ranked by how many golfers asked (then the earliest request), and
the top --max are written as course_data/requests/course_page_<slug>.json (schema course_page/1) plus
course_data/requests/course_batch_<name>.json listing them. Courses that already have a library folder, a request
file, or a hand-checked tournament folder are skipped (listed in the summary). Docs are untrusted: every field is
checked for shape and length before use.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REQ_DIR = os.path.join(ROOT, "course_data", "requests")
STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
          "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
          "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"}


def slug_of(name):
    """the app's slugOf (course_index.js): same rule, so a request's slug can be re-derived from its name"""
    s = (name or "").lower().replace("&", " and ")
    s = re.sub(r"['’]", "", s)
    s = re.sub(r"\b(golf|course|club|country|and|the|cc|gc)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return (s or "course")[:48]


def docs_of(js):
    """every request-shaped dict in an export, whatever the wrapper"""
    out = []
    if isinstance(js, dict):
        if "name" in js and "state" in js:
            return [js]
        for k in ("docs", "documents", "rows", "items", "results", "data"):
            if k in js:
                out += docs_of(js[k])
        if not out:
            for v in js.values():
                if isinstance(v, (dict, list)):
                    out += docs_of(v)
    elif isinstance(js, list):
        for x in js:
            out += docs_of(x)
    return out


def clean(d):
    name = d.get("name")
    st = str(d.get("state") or "").upper()
    if not isinstance(name, str) or not name.strip() or len(name) > 120 or st not in STATES:
        return None
    name = re.sub(r"[\x00-\x1f]", " ", name).strip()
    city = d.get("city") if isinstance(d.get("city"), str) and len(d.get("city")) <= 80 else ""
    osm = d.get("osm") if isinstance(d.get("osm"), str) and re.fullmatch(r"(way|relation|node)/\d{1,12}", d["osm"]) else None
    near = None
    try:
        lat, lon = float(d.get("lat")), float(d.get("lon"))
        if 18 <= lat <= 72 and -180 <= lon <= -60:
            near = f"{lat:.5f},{lon:.5f}"
    except (TypeError, ValueError):
        pass
    at = d.get("requested_at") if isinstance(d.get("requested_at"), str) and len(d["requested_at"]) <= 40 else ""
    uid = str(d.get("user_id") or "")[:128]
    return dict(name=name, city=re.sub(r"[\x00-\x1f]", " ", city).strip(), state=st, osm=osm, near=near,
                slug=slug_of(name), at=at, user=uid)


def taken_slugs():
    """slugs that already have a page or a request: library folders, request files, tournament folders, index.json"""
    t = set()
    lib = HERE
    for n in os.listdir(lib):
        if os.path.isdir(os.path.join(lib, n)):
            t.add(n)
    if os.path.isdir(REQ_DIR):
        for n in os.listdir(REQ_DIR):
            m = re.fullmatch(r"course_page_(.+)\.json", n)
            if m:
                t.add(m.group(1))
    cdir = os.path.join(ROOT, "course_data", "courses")
    if os.path.isdir(cdir):
        t |= set(os.listdir(cdir))
    try:
        t |= {c.get("slug") for c in json.load(open(os.path.join(HERE, "index.json")))["courses"]}
    except Exception:                                               # noqa: BLE001
        pass
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--name", default=dt.datetime.now(dt.timezone.utc).strftime("req%Y%m%d%H%M"))
    ap.add_argument("--max", type=int, default=10, help="courses per batch (push one batch at a time)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    raw = docs_of(json.load(open(a.export)))
    groups = {}
    for d in raw:
        c = clean(d)
        if not c:
            continue
        k = c["osm"] or (c["state"] + "|" + c["slug"])
        g = groups.setdefault(k, dict(c, users=set(), first=c["at"]))
        g["users"].add(c["user"] or f"anon{len(g['users'])}")
        if c["at"] and (not g["first"] or c["at"] < g["first"]):
            g["first"] = c["at"]
        for f in ("osm", "near", "city"):
            g[f] = g[f] or c[f]
    ranked = sorted(groups.values(), key=lambda g: (-len(g["users"]), g["first"] or "9"))
    taken = taken_slugs()
    picked, skipped, used = [], [], set()
    for g in ranked:
        slug = g["slug"]
        if slug in taken:
            skipped.append(f"{slug} ({g['name']}, {g['state']}): already has a library page or request")
            continue
        if slug in used:
            slug = f"{slug}_{g['state'].lower()}"
        if slug in used or slug in taken:
            skipped.append(f"{slug}: slug clash")
            continue
        if len(picked) >= a.max:
            skipped.append(f"{slug} ({g['name']}, {g['state']}, {len(g['users'])} asked): next batch")
            continue
        used.add(slug)
        q = {"schema": "course_page/1", "name": g["name"], "state": g["state"], "slug": slug, "group": "library",
             "rev": 1, "requested_by": len(g["users"]), "requested_first": g["first"] or None, "source": "app request"}
        if g["city"]:
            q["city"] = g["city"]
        if g["osm"]:
            q["osm"] = g["osm"]
        if g["near"]:
            q["near"] = g["near"]
        picked.append(q)
    paths = [f"course_data/requests/course_page_{q['slug']}.json" for q in picked]
    batch = f"course_data/requests/course_batch_{re.sub(r'[^a-z0-9_]', '', a.name.lower())}.json"
    if not a.dry_run and picked:
        os.makedirs(REQ_DIR, exist_ok=True)
        for q, p in zip(picked, paths):
            with open(os.path.join(ROOT, p), "w") as fh:
                json.dump(q, fh, indent=1)
        with open(os.path.join(ROOT, batch), "w") as fh:
            json.dump({"requests": paths, "rev": 1, "source": "app requests (requests_to_batch.py)"}, fh, indent=1)
    print(json.dumps(dict(docs=len(raw), courses=len(groups), batch=batch if picked else None, requests=paths,
                          skipped=skipped, dry_run=a.dry_run), indent=1))


if __name__ == "__main__":
    sys.exit(main())
