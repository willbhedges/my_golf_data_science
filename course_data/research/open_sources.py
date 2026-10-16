"""Probe free, key-less course-data sources and compare them with our hand-checked cards.

Research prototype for course_data/research/auto_course_lookup.md (section 6). No API keys, no
sign-ups: every source here is anonymous and openly licensed.

    python course_data/research/open_sources.py fetch     # needs the web: GitHub Actions only
    python course_data/research/open_sources.py compare   # offline: reads raw/, writes probe.json/.md

Sources
  OpenGolfAPI REST (api.opengolfapi.org, ODbL 1.0, 1,000 anonymous calls/day/IP):
      /v1/courses/search?q=&state=   -> candidates (name, lat/lon, osm id)
      /api/v1/courses/{id}           -> detail with tees[] (name, colour, rating, slope, yardage)
                                        and holes_data[] (number, par, handicap, yardages{colour})
      /v1/courses/{id}/tees, /holes  -> the documented equivalents (fallback)
  OpenGolfAPI bulk dump (github.com/opengolfapi/data, ODbL): name/coords/osm_id/pars - resolver only.
  OSM taginfo (taginfo.openstreetmap.org, ODbL): how often golf=tee carries a tee colour (tee=*).
  Overpass (overpass-api.de, ODbL): tee-colour / dist tagging inside our three courses' bboxes.

The sandbox cannot reach any of these except raw.githubusercontent.com; `fetch` runs from
.github/workflows/research_fetch.yml and commits course_data/research/raw/.
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
ROOT = HERE.parent  # course_data/
UA = "my_golf_data_science research probe (github actions; contact via repo)"

COURSES = {
    "spirit_hollow": {"q": "Spirit Hollow", "state": "IA", "card": "tees/scorecard.json",
                      "package": "packages/spirit_hollow/package.json"},
    "veenker": {"q": "Veenker", "state": "IA", "card": None,
                "package": "packages/veenker/package.json"},
    "mozingo_lake": {"q": "Mozingo", "state": "MO", "card": None,
                     "package": "packages/mozingo_lake/package.json"},
}
DUMP_URL = "https://raw.githubusercontent.com/opengolfapi/data/main/opengolfapi-us.csv.gz"
API = "https://api.opengolfapi.org"


# ----------------------------------------------------------------------------- fetch (web)
def get(url: str, timeout: int = 40, data: bytes | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA,
                                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:  # keep the body: it explains 4xx
        return e.code, e.read().decode("utf-8", "replace")[:2000]
    except Exception as e:  # noqa: BLE001 - a probe records every failure
        return 0, f"{type(e).__name__}: {e}"


def jget(url: str) -> dict:
    status, body = get(url)
    try:
        js = json.loads(body)
    except ValueError:
        js = None
    time.sleep(1.0)  # be polite: well under the anonymous limit
    return {"url": url, "status": status, "json": js, "text": None if js is not None else body[:2000]}


def fetch() -> None:
    RAW.mkdir(exist_ok=True)
    log = {"fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "calls": []}
    for slug, c in COURSES.items():
        out = {"slug": slug, "search": jget(f"{API}/v1/courses/search?"
                                            + urllib.parse.urlencode({"q": c["q"], "state": c["state"],
                                                                      "limit": 20}))}
        cands = ((out["search"]["json"] or {}).get("courses") or [])
        out["details"] = []
        for cand in cands[:4]:
            cid = cand.get("id")
            if not cid:
                continue
            d = {"id": cid, "name": cand.get("course_name") or cand.get("name")}
            for k, path in (("api_v1", f"/api/v1/courses/{cid}"), ("tees", f"/v1/courses/{cid}/tees"),
                            ("holes", f"/v1/courses/{cid}/holes")):
                d[k] = jget(API + path)
            out["details"].append(d)
        (RAW / f"opengolfapi_{slug}.json").write_text(json.dumps(out, indent=1))
        log["calls"].append({"slug": slug, "status": out["search"]["status"], "n": len(cands)})

    # taginfo: share of golf=tee features that carry a tee colour key (global)
    ti = {}
    for k, url in {
        "golf_tee": "https://taginfo.openstreetmap.org/api/4/tag/stats?key=golf&value=tee",
        "golf_tee_combos": "https://taginfo.openstreetmap.org/api/4/tag/combinations?key=golf&value=tee"
                           "&sortname=together_count&sortorder=desc&rp=40&page=1",
        "tee_values": "https://taginfo.openstreetmap.org/api/4/key/values?key=tee&sortname=count"
                      "&sortorder=desc&rp=40&page=1",
        "golf_hole_combos": "https://taginfo.openstreetmap.org/api/4/tag/combinations?key=golf&value=hole"
                            "&sortname=together_count&sortorder=desc&rp=40&page=1",
    }.items():
        ti[k] = jget(url)
    (RAW / "taginfo_golf.json").write_text(json.dumps(ti, indent=1))

    # Overpass: tee tagging inside each course bbox + statewide counts for IA/MO
    ov = {}
    for slug, c in COURSES.items():
        try:
            bbox = json.loads((ROOT / c["package"]).read_text())["course"]["bbox"]
        except Exception:  # noqa: BLE001
            continue
        w, s, e, n = bbox
        q = (f'[out:json][timeout:60];(nwr["golf"="tee"]({s},{w},{n},{e}););out tags;')
        ov[slug] = jget("https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(q))
    for st in ("US-IA", "US-MO"):
        q = (f'[out:json][timeout:120];area["ISO3166-2"="{st}"]->.a;'
             f'(nwr["golf"="tee"](area.a););out count;'
             f'(nwr["golf"="tee"]["tee"](area.a););out count;'
             f'(nwr["golf"="hole"](area.a););out count;'
             f'(nwr["golf"="hole"][~"^dist"~"."](area.a););out count;'
             f'(nwr["leisure"="golf_course"](area.a););out count;')
        ov[st] = jget("https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(q))
    (RAW / "overpass_tees.json").write_text(json.dumps(ov, indent=1))
    (RAW / "fetch_log.json").write_text(json.dumps(log, indent=1))
    print(json.dumps(log, indent=1))
    compare()


# ----------------------------------------------------------------------------- compare (offline)
def _our_sets(slug: str) -> dict:
    """{set_name: {"yards": [18], "total": int, "rating": .., "slope": ..}} from our files."""
    c = COURSES[slug]
    out = {}
    if c["card"]:
        card = json.loads((ROOT / c["card"]).read_text())
        for name, t in card["tee_sets"].items():
            r = (t.get("ratings") or [{}])[0]
            out[name] = {"yards": t["yards"], "total": t.get("total"), "rating": r.get("rating"),
                         "slope": r.get("slope"), "src": "tees/scorecard.json"}
        out["_par"] = card.get("par")
        out["_hcp"] = (card.get("handicap") or {}).get("men")
        return out
    pkg = json.loads((ROOT / c["package"]).read_text())
    for name, t in pkg["tee_sets"].items():
        out[name] = {"yards": t["yards"], "total": t.get("total"), "rating": t.get("rating"),
                     "slope": t.get("slope"), "src": c["package"]}
    holes = pkg["holes"]
    hl = holes if isinstance(holes, list) else [holes[k] for k in sorted(holes, key=lambda x: int(x))]
    out["_par"] = [h.get("par") for h in hl]
    out["_hcp"] = [h.get("hcp") for h in hl]
    return out


def _their_sets(detail: dict) -> tuple[dict, list, list]:
    """Normalise OpenGolfAPI detail -> ({colour/name: {yards[18], total, rating, slope}}, par, hcp)."""
    js = (detail.get("api_v1") or {}).get("json") or {}
    tees = js.get("tees") or ((detail.get("tees") or {}).get("json") or {}).get("tees") or []
    holes = js.get("holes_data") or ((detail.get("holes") or {}).get("json") or {}).get("holes") or []
    holes = sorted(holes, key=lambda h: h.get("number") or h.get("hole_number") or 0)
    sets = {}
    for t in tees:
        key = (t.get("tee_color") or t.get("tee_name") or t.get("name") or t.get("tee_key") or "?")
        key = f"{key} ({t.get('gender')})" if t.get("gender") else key
        sets[key] = {"total": t.get("yardage") or t.get("total_yardage"), "rating": t.get("course_rating"),
                     "slope": t.get("slope") or t.get("slope_rating"), "yards": None,
                     "_colour": (t.get("tee_color") or t.get("tee_name") or "").lower()}
    per = {}
    for h in holes:
        for col, y in (h.get("yardages") or {}).items():
            per.setdefault(col.lower(), []).append(y)
    for col, ys in per.items():
        match = [k for k, v in sets.items() if v["_colour"] == col] or [col]
        for k in match:
            sets.setdefault(k, {"total": None, "rating": None, "slope": None, "_colour": col})
            sets[k]["yards"] = ys
    par = [h.get("par") for h in holes]
    hcp = [h.get("handicap_index") or h.get("handicap") for h in holes]
    return sets, par, hcp


def _best_match(ours: list, theirs: dict) -> tuple[str | None, float | None, int | None]:
    best = (None, None, None)
    for k, v in theirs.items():
        ys = v.get("yards")
        if not ys or len(ys) != len(ours) or any(y is None for y in ys):
            continue
        diffs = [abs(a - b) for a, b in zip(ours, ys)]
        mae = sum(diffs) / len(diffs)
        if best[1] is None or mae < best[1]:
            best = (k, round(mae, 1), sum(1 for d in diffs if d <= 3))
    return best


def compare() -> dict:
    res = {"courses": {}}
    for slug in COURSES:
        f = RAW / f"opengolfapi_{slug}.json"
        if not f.exists():
            res["courses"][slug] = {"status": "no raw fetch yet (run the workflow)"}
            continue
        raw = json.loads(f.read_text())
        ours = _our_sets(slug)
        row = {"search_status": raw["search"]["status"],
               "candidates": [d.get("name") for d in raw.get("details", [])], "sets": {}}
        if not raw.get("details"):
            row["note"] = (raw["search"].get("text") or "")[:300]
        for d in raw.get("details", []):
            theirs, par, hcp = _their_sets(d)
            if not theirs:
                continue
            row["matched_id"], row["matched_name"] = d["id"], d.get("name")
            row["their_sets"] = {k: {kk: v[kk] for kk in ("total", "rating", "slope")} for k, v in theirs.items()}
            if ours.get("_par") and par and len(par) == len(ours["_par"]):
                row["par_agree"] = sum(a == b for a, b in zip(par, ours["_par"]))
            if ours.get("_hcp") and hcp and len(hcp) == len(ours["_hcp"]):
                row["hcp_agree"] = sum(a == b for a, b in zip(hcp, ours["_hcp"]))
            for name, s in ours.items():
                if name.startswith("_"):
                    continue
                k, mae, within3 = _best_match(s["yards"], theirs)
                row["sets"][name] = {"our_total": s["total"], "their_set": k, "hole_mae_yd": mae,
                                     "holes_within_3yd": within3,
                                     "their_total": theirs.get(k, {}).get("total") if k else None}
            break
        res["courses"][slug] = row
    # tee-colour tagging in OSM
    ov = RAW / "overpass_tees.json"
    if ov.exists():
        o = json.loads(ov.read_text())
        tag = {}
        for k, v in o.items():
            js = v.get("json") or {}
            els = js.get("elements") or []
            if k.startswith("US-"):
                tag[k] = [int(e.get("tags", {}).get("total", 0)) for e in els]
            else:
                tag[k] = {"tees": len(els),
                          "with_tee_colour": sum(1 for e in els if "tee" in e.get("tags", {})),
                          "with_ref": sum(1 for e in els if "ref" in e.get("tags", {}))}
        res["osm_tee_tagging"] = tag
        res["osm_tee_tagging_legend"] = ("US-xx: [golf=tee, golf=tee with tee=*, golf=hole, "
                                         "golf=hole with dist*, leisure=golf_course]")
    ti = RAW / "taginfo_golf.json"
    if ti.exists():
        t = json.loads(ti.read_text())
        st = ((t.get("golf_tee") or {}).get("json") or {}).get("data") or []
        combos = ((t.get("golf_tee_combos") or {}).get("json") or {}).get("data") or []
        res["taginfo"] = {"golf_tee_all": next((x.get("count") for x in st if x.get("type") == "all"), None),
                          "golf_tee_with": {c.get("other_key"): c.get("together_count") for c in combos
                                            if c.get("other_key") in ("tee", "ref", "name", "colour", "par",
                                                                      "golf:par", "hole")},
                          "tee_values": [(v.get("value"), v.get("count")) for v in
                                         (((t.get("tee_values") or {}).get("json") or {}).get("data") or [])[:15]]}
    (HERE / "probe.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return res


def dump_resolve() -> dict:
    """Offline-capable resolver test on the ODbL bulk dump (raw.githubusercontent.com is reachable)."""
    status, _ = 200, None
    req = urllib.request.Request(DUMP_URL, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=60).read()
    rows = list(csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(data)), "utf-8")))
    full = sum(1 for r in rows if all(r[f"hole_{i}_par"] for i in range(1, 19)))
    out = {"rows": len(rows), "with_osm_id": sum(1 for r in rows if r["osm_id"]),
           "full_18_pars": full, "with_total_yardage": sum(1 for r in rows if r["total_yardage"]),
           "hits": {}}
    for slug, c in COURSES.items():
        hits = [r for r in rows if c["q"].lower() in r["name"].lower() and r["state"] == c["state"]]
        out["hits"][slug] = [{k: r[k] for k in ("id", "name", "latitude", "longitude", "osm_id",
                                                "holes", "par")} for r in hits]
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "compare"
    {"fetch": fetch, "compare": compare, "dump": dump_resolve}[cmd]()
