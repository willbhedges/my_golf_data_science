"""Guarded Overpass fetch: never build a course from a partial / stale OSM response.

Why: Creekmoor MO's page was built (2026-10-30) from a fetch with 0 golf=hole ways and 0 pins while the
2026-10-17 snapshot (structure/data/creekmoor_mo) had all 18 holes matching the card, so the router guessed every
hole. Overpass answers 200 with a partial body when a query times out or runs out of memory (the `remark` field),
and a lagging mirror answers with old data (osm3s.timestamp_osm_base); both used to be accepted silently.

fetch_guarded(snwe, course, raw):
  1. ask each mirror in MIRRORS in turn (one try each, bounded by a total deadline instead of 5 x 3 retries);
  2. judge each response: an Overpass runtime remark, a mirror base older than the cached snapshot, or golf counts
     far below the snapshot / the course's own shape (0 hole ways but many greens + tees, < half the snapshot's
     holes / greens / tees) mark it "thin"; a good response stops the loop;
  3. no good response: take the richest one and merge in every feature of the newest cached snapshot for this
     course that it lacks (structure/data/<slug>/osm.geojson.gz, the package's previous raw/osm.geojson, the
     library's raw/osm.geojson), or, when nothing answered at all, use the snapshot alone;
  4. record what was used and why: raw/osm_source.json, plus summary.json["osm_source"] (fetch_package).
A thin fetch with no snapshot to fall back on is still used (it may be the truth: many courses map greens but no
hole ways) but is recorded as thin, so the package says so instead of looking like a normal build.
"Newer" is not always "better" either (Shoal Creek: a neighbour's holes were added in the bbox): a fresh fetch with
MORE holes than the snapshot is accepted, and the difference is recorded.
"""
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import platform_common as pc  # noqa: E402

# platform_common.OVERPASS (the three already used by every run) + one more independent world mirror
MIRRORS = list(pc.OVERPASS) + ["https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
KINDS = ("hole", "green", "tee", "pin", "bunker", "fairway")
REMARK_BAD = re.compile(r"runtime error|timed out|timeout|out of memory|maxsize|dispatcher|too busy|rate_limited",
                        re.I)
DEADLINE_S = 900          # the whole OSM step; Longview Lake once spent the job clock in pc.overpass retries
PASS_SLEEP_S = 30


# ----------------------------------------------------------------------------- judging a response
def golf_counts(fc):
    """FeatureCollection (or Overpass elements list) -> {golf kind: count} for KINDS."""
    feats = fc.get("features", []) if isinstance(fc, dict) else fc
    c = Counter()
    for f in feats:
        p = f.get("properties", f.get("tags")) or {}
        if p.get("golf") in KINDS:
            c[p["golf"]] += 1
    return {k: c.get(k, 0) for k in KINDS}


def remark_problem(data):
    """Overpass `remark` that means the body is partial (timeout, memory, maxsize), else None."""
    rm = str((data or {}).get("remark") or "")
    return rm[:240] if rm and REMARK_BAD.search(rm) else None


def osm_base(data):
    return ((data or {}).get("osm3s") or {}).get("timestamp_osm_base")


def thin_reasons(counts, ref=None, ref_label="snapshot"):
    """Why `counts` looks like a truncated / stale fetch (list of strings; empty = looks complete).
    ref: counts of a cached snapshot of the same course."""
    h, g, t = counts.get("hole", 0), counts.get("green", 0), counts.get("tee", 0)
    out = []
    if h == 0 and g >= 4 and t >= 4 and ref and ref.get("hole", 0) >= 4:
        out.append(f"0 golf=hole ways but {g} greens / {t} tees (the {ref_label} has {ref['hole']} holes)")
    elif h == 0 and g >= 9 and t >= 9 and ref is None:
        out.append(f"0 golf=hole ways but {g} greens / {t} tees (no snapshot to compare)")
    if ref:
        for k in ("hole", "green", "tee", "pin"):
            r = ref.get(k, 0)
            if r >= 4 and counts.get(k, 0) < r / 2.0 and not (k == "hole" and h == 0 and out):
                out.append(f"{k}: {counts.get(k, 0)} vs {r} in the {ref_label}")
    return out


def richness(counts):
    return 4 * counts.get("hole", 0) + 2 * counts.get("green", 0) + counts.get("tee", 0) + counts.get("pin", 0)


# ----------------------------------------------------------------------------- cached snapshots
def _read_fc(path):
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt") as fh:
                return json.load(fh)
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _git_date(path):
    try:
        r = subprocess.run(["git", "-C", os.path.dirname(path), "log", "-1", "--format=%cI", "--", path],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or None
    except Exception:                                           # noqa: BLE001
        return None


def _date_of(path, summary=None):
    """Best fetch date for a snapshot file: summary fetched_utc > git commit date > mtime (ISO, UTC)."""
    d = (summary or {}).get("fetched_utc") or _git_date(path)
    if not d:
        d = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(os.path.getmtime(path)))
    return _iso_utc(d)


def _iso_utc(d):
    """'2026-10-17T06:21:00+00:00' / '...Z' -> '2026-10-17T06:21:00Z' (sortable)."""
    m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", str(d or ""))
    if not m:
        return None
    s = m.group(1)
    tz = re.search(r"([+-])(\d\d):?(\d\d)$", str(d))
    if tz and tz.group(0) not in ("+00:00", "+0000"):
        import datetime as dt
        sign = 1 if tz.group(1) == "+" else -1
        off = dt.timedelta(hours=int(tz.group(2)), minutes=int(tz.group(3)))
        t = dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S") - sign * off
        s = t.strftime("%Y-%m-%dT%H:%M:%S")
    return s + "Z"


def _osm_key(course):
    o = (course or {}).get("osm") or {}
    return (o.get("type"), o.get("id")) if o.get("id") else None


# (kind, glob relative to course_data) of every OSM cache the repo keeps; course.json / summary.json sit beside the
# file (or in its raw/ dir) and give the OSM course id to match on; otherwise the directory name is the slug
SNAPSHOT_GLOBS = (("structure", "structure/data/*/osm.geojson.gz"),
                  ("zero_tap", "zero_tap/*/*/osm.geojson.gz"),
                  ("generalize", "generalize/courses/*/osm_golf.geojson"),
                  ("package", "packages/*/raw/osm.geojson"),
                  ("library", "library/*/raw/osm.geojson"),
                  ("library", "library/gate/*/raw/osm.geojson"))


def _snapshot_key(path):
    """-> (OSM key or None, slug-like dir name, summary path or None) for a cached snapshot file."""
    d = os.path.dirname(path)
    name = os.path.basename(os.path.dirname(d)) if os.path.basename(d) == "raw" else os.path.basename(d)
    cj = pc.read_json(os.path.join(d, "course.json"))
    sp = os.path.join(d, "summary.json")
    summ = pc.read_json(sp) if os.path.exists(sp) else None
    key = _osm_key(cj)
    if not key and summ and (summ.get("course") or {}).get("osm_id"):
        key = (summ["course"].get("osm_type"), summ["course"].get("osm_id"))
    return key, name, (sp if summ else None), (cj or {}).get("state")


def snapshot_paths(course=None, slug=None, roots=None):
    """Candidate cached snapshot files for a course: [(kind, geojson path, summary path or None)].
    roots: {kind: glob} to override SNAPSHOT_GLOBS (tests)."""
    key = _osm_key(course)
    globs = roots.items() if roots else [(k, os.path.join(pc.COURSE_DATA, g)) for k, g in SNAPSHOT_GLOBS]
    out = []
    for kind, g in globs:
        for p in sorted(glob.glob(g)):
            k, name, sp, st = _snapshot_key(p)
            names = {slug, f"{slug}_{st}".lower(), f"gate_{slug}"} if slug else set()
            if (key and k == key) or (not (key and k) and name in names):
                out.append((kind, p, sp))
    return out


def load_snapshots(course=None, slug=None, **kw):
    """-> [dict(kind, path, date, counts, fc)], newest first."""
    snaps = []
    for kind, p, sp in snapshot_paths(course, slug, **kw):
        fc = _read_fc(p)
        if not fc or not fc.get("features"):
            continue
        summ = pc.read_json(sp) if sp else None
        snaps.append(dict(kind=kind, path=os.path.relpath(p, pc.ROOT), date=_date_of(p, summ), counts=golf_counts(fc),
                          source=(summ or {}).get("osm_source", {}).get("source"), fc=fc))
    snaps.sort(key=lambda s: s["date"] or "", reverse=True)
    return snaps


def reference(snaps):
    """The snapshot to judge a fresh fetch against: the newest one that is itself not thin vs. the others
    (a snapshot written by a thin build must not lower the bar)."""
    for i, s in enumerate(snaps):
        older = [o for o in snaps[i + 1:] if not thin_reasons(s["counts"], o["counts"])]
        if len(older) == len(snaps[i + 1:]):
            return s
    return snaps[-1] if snaps else None


def merge(fc, snap_fc):
    """fc + every snapshot feature (by osm type/id) that fc lacks; -> (merged fc, n added)."""
    have = {(f["properties"].get("osm_type"), f["properties"].get("osm_id")) for f in fc["features"]}
    add = [json.loads(json.dumps(f)) for f in snap_fc["features"]
           if (f.get("properties", {}).get("osm_type"), f.get("properties", {}).get("osm_id")) not in have]
    for f in add:
        f["properties"]["src"] = "snapshot"
        f["properties"].pop("inside_course", None)
    return dict(fc, features=fc["features"] + add), len(add)


# ----------------------------------------------------------------------------- network
def answered_(attempts):
    return [a for a in attempts if a.get("ok")]


def _agree(answered):
    """Two or more mirrors answered, without a runtime remark, with identical golf counts."""
    clean = [a for a in answered if not any(w.startswith("Overpass remark") for w in a["thin"])]
    return len(clean) >= 2 and all(a["counts"] == clean[0]["counts"] for a in clean)


def _post(url, query, timeout):
    import requests
    r = requests.post(url, data={"data": query}, headers=pc.UA, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} {r.text[:160]}")
    return r.json()


def fetch_guarded(snwe, course=None, slug=None, query=None, post=None, snapshots=None, mirrors=None,
                  deadline_s=DEADLINE_S, timeout=200, sleep=time.sleep, now=time.time):
    """-> (overpass data or None, FeatureCollection, provenance dict). Raises only when no mirror answered and
    there is no snapshot."""
    import fetch_course as fcm
    query = query or fcm.features_query(snwe)
    post = post or _post
    mirrors = list(mirrors or MIRRORS)
    snaps = load_snapshots(course, slug) if snapshots is None else snapshots
    ref = reference(snaps)
    ref_label = f"{ref['kind']} snapshot of {(ref['date'] or '?')[:10]}" if ref else "snapshot"
    t0, attempts, good = now(), [], None
    for p in range(3):
        for url in mirrors:
            if now() - t0 > deadline_s:
                break
            a = dict(mirror=url, pass_=p + 1)
            try:
                data = post(url, query, timeout)
            except Exception as e:                              # noqa: BLE001
                a.update(ok=False, error=repr(e)[:240])
                attempts.append(a)
                pc.log("osm_guard:", url, a["error"])
                continue
            fc = fcm.to_geojson(data.get("elements", []))
            c = golf_counts(fc)
            why = thin_reasons(c, ref and ref["counts"], ref_label)
            rm = remark_problem(data)
            if rm:
                why.insert(0, f"Overpass remark: {rm}")
            base = osm_base(data)
            if base and ref and ref.get("date") and _iso_utc(base) and _iso_utc(base) < ref["date"] and \
                    richness(c) < richness(ref["counts"]):
                why.append(f"mirror data as of {base} is older than the {ref_label}")
            a.update(ok=True, counts=c, osm_base=base, thin=why, n_elements=len(data.get("elements", [])))
            a["_data"], a["_fc"] = data, fc
            attempts.append(a)
            pc.log("osm_guard:", url, c, "thin: " + "; ".join(why) if why else "ok")
            if not why:
                good = a
                break
            if ref is None and _agree(answered_(attempts)):
                break                     # no snapshot: two mirrors agreeing on the same thin counts is the map
        if good or now() - t0 > deadline_s or answered_(attempts):
            break                         # a thin answer from every mirror is an answer: don't loop again
        sleep(PASS_SLEEP_S * (p + 1))     # nothing answered: public servers are often at capacity
    answered = answered_(attempts)
    prov = dict(schema="osm_source/1", fetched_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                mirrors_tried=[a["mirror"] for a in attempts],
                attempts=[{k: v for k, v in a.items() if not k.startswith("_")} for a in attempts],
                reference=ref and {k: ref[k] for k in ("kind", "path", "date", "counts")},
                snapshots=[{k: s[k] for k in ("kind", "path", "date", "counts")} for s in snaps])
    if good:
        prov.update(source="overpass", mirror=good["mirror"], osm_base=good["osm_base"], counts=good["counts"],
                    reason="complete")
        if ref and good["counts"]["hole"] > ref["counts"]["hole"]:
            prov["note"] = (f"fresh fetch has more holes ({good['counts']['hole']}) than the {ref_label} "
                            f"({ref['counts']['hole']}): new OSM edits (maybe a neighbouring course) - check")
        return good["_data"], good["_fc"], prov
    best = max(answered, key=lambda a: richness(a["counts"])) if answered else None
    if ref:
        if best:
            fc, n = merge(best["_fc"], ref["fc"])
            prov.update(source="overpass+snapshot", mirror=best["mirror"], osm_base=best["osm_base"],
                        snapshot=ref["path"], snapshot_date=ref["date"], merged_features=n, counts=golf_counts(fc),
                        reason="thin fetch on every mirror: " + "; ".join(best["thin"]))
            return best["_data"], fc, prov
        fc = json.loads(json.dumps(ref["fc"]))
        for f in fc["features"]:
            f["properties"].pop("inside_course", None)
        prov.update(source="snapshot", snapshot=ref["path"], snapshot_date=ref["date"], counts=golf_counts(fc),
                    reason="no Overpass mirror answered: " + "; ".join(a.get("error", "") for a in attempts)[:600])
        return None, fc, prov
    if best:
        prov.update(source="overpass", mirror=best["mirror"], osm_base=best["osm_base"], counts=best["counts"],
                    thin=best["thin"], reason="thin fetch on every mirror and no cached snapshot: used as is")
        return best["_data"], best["_fc"], prov
    raise RuntimeError("all Overpass mirrors failed and no cached snapshot: " +
                       "; ".join(f"{a['mirror']}: {a.get('error')}" for a in attempts)[:800])
