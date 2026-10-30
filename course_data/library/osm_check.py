"""OSM completeness count for candidate library courses (runs on GitHub Actions: the sandbox cannot reach Overpass).

  python course_data/library/osm_check.py course_data/requests/osm_check_<name>.json out.json

Input  {"candidates": [{"name": "Pebble Beach", "state": "CA", "pattern": "Pebble Beach Golf Links"}, ...]}
       `pattern` (optional) is the case-insensitive regex on leisure=golf_course name; default = `name`.
Output {"schema": "osm_check/1", "results": [{name, state, matches: [{osm, name, center, holes, refs, missing_refs,
       greens, tees, complete}]}]}
complete = every ref 1-18 on a golf=hole way inside the course area, at least 18 golf=green and 18 golf=tee.
"""
import json
import re
import sys
import time

sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),
                                              "..", "platform"))
import platform_common as pc  # noqa: E402

Q = """[out:json][timeout:120];
area["ISO3166-2"="US-{st}"]["admin_level"="4"]->.st;
nwr["leisure"="golf_course"]["name"~"{pat}",i](area.st)->.c;
foreach.c->.x(
  .x out tags center;
  .x map_to_area->.ca;
  way["golf"="hole"](area.ca)->.h;
  .h out tags;
  nwr["golf"="green"](area.ca)->.g;
  .g out count;
  nwr["golf"="tee"](area.ca)->.t;
  .t out count;
);"""


def check(c):
    pat = re.sub(r'["\\]', "", c.get("pattern") or c["name"])
    try:
        js = pc.overpass(Q.format(st=c["state"].upper(), pat=pat), tries=4, timeout=180)
    except Exception as e:                                       # noqa: BLE001
        return dict(c, error=str(e)[:200], matches=[])
    els, matches, cur = js.get("elements", []), [], None
    for e in els:
        tg = e.get("tags", {})
        if e["type"] in ("way", "relation", "node") and tg.get("leisure") == "golf_course":
            ce = e.get("center") or ({"lat": e.get("lat"), "lon": e.get("lon")} if "lat" in e else None)
            cur = dict(osm=f"{e['type']}/{e['id']}", name=tg.get("name"), center=[ce["lat"], ce["lon"]] if ce else None,
                       city=tg.get("addr:city"), access=tg.get("access"), holes=0, refs=[], counts=[])
            matches.append(cur)
        elif cur is not None and e["type"] == "count":
            cur["counts"].append(int(e["tags"].get("total", 0)))
        elif cur is not None and tg.get("golf") == "hole":
            cur["holes"] += 1
            cur["refs"].append(tg.get("ref"))
    for m in matches:
        cnt = m.pop("counts") + [0, 0]
        m["greens"], m["tees"] = cnt[0], cnt[1]
        refs = {str(r).strip() for r in m["refs"] if r}
        m["missing_refs"] = [i for i in range(1, 19) if str(i) not in refs]
        m["refs"] = sorted(refs, key=lambda r: (len(r), r))
        m["complete"] = (not m["missing_refs"] and m["greens"] >= 18 and m["tees"] >= 18)
    return dict(c, matches=matches)


def main(inp, out):
    cands = json.load(open(inp))["candidates"]
    res = []
    for i, c in enumerate(cands):
        r = check(c)
        res.append(r)
        ok = [m for m in r["matches"] if m["complete"]]
        print(f"{i + 1:3d} {c['state']} {c['name']:<36} matches={len(r['matches'])} complete={len(ok)} "
              + "; ".join(f"{m['osm']} {m['name']} h={m['holes']} g={m['greens']} t={m['tees']} miss={len(m['missing_refs'])}"
                          for m in r["matches"][:4]) + (f" ERR {r['error']}" if r.get("error") else ""), flush=True)
        json.dump(dict(schema="osm_check/1", source=inp, results=res), open(out, "w"), indent=1)
        time.sleep(1.5)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
