"""route_unmapped.py REQ: holes for a course OpenStreetMap does not map (.github/workflows/course_page_one.yml).

platform/package.py stops with "no holes built" when OSM has no golf=hole ways and too few greens / tees. This runs the
fast path's imagery router on the course (platform/fastpath/fast.py: NAIP + 3DEP + canopy scene, joint routing against
the web scorecard, two detectors, route_conf's pick and per-hole P(right)) and leaves in the page's output folder

    routed_holes.geojson   golf=hole lines + the detected greens / tee boxes / fairways / bunkers / water (an
                           osm_supplement: course_page.py pkgreq adds it to the package request)
    routed_card.json       the web card the routing fits best, when the router switched cards
    routing.json           status, per-hole P(right), the holes marked approximate, warnings

Exit 0 when routed_holes.geojson was written (the workflow then runs platform/package.py again), 1 otherwise.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(CD, "platform", "fastpath"), os.path.join(CD, "platform"), HERE]
FILES = ("routed_holes.geojson", "routed_card.json", "routing.json")


def row_for(q):
    """the fast path's index row: the page package's own resolve when it got that far, else the national index"""
    import fast
    p = os.path.join(CD, "packages", q["slug"], "raw", "course.json")
    if os.path.exists(p):
        c = json.load(open(p))
        if c.get("status", "ok") == "ok" and c.get("center") and (c.get("osm") or {}).get("id"):
            return dict(name=q["name"], state=q["state"], city=q.get("city") or "", lat=c["center"][1], lon=c["center"][0],
                        osm="%s/%s" % (c["osm"]["type"], c["osm"]["id"]), holes=c.get("holes") or 18)
    row = fast.lookup(", ".join(x for x in (q["name"], q.get("city"), q["state"]) if x))
    if row is None and q.get("near"):
        # not in OpenStreetMap as a golf course at all: the request's own point (course_page "near": "lat,lon")
        lat, lon = (float(x) for x in str(q["near"]).split(",")[:2])
        row = dict(name=q["name"], state=q["state"], city=q.get("city") or "", lat=lat, lon=lon, osm=None, holes=18,
                   radius_m=q.get("near_radius_m"))
    return row


def main(req):
    import course_page as cp
    import fast
    q = cp.request(req)
    out = cp.out_dir(q)
    for f in FILES:
        if os.path.exists(os.path.join(out, f)):
            os.remove(os.path.join(out, f))
    row = row_for(q)
    if row is None:
        print("route_unmapped: the course is not in the national index")
        return 1
    logs = []
    OK = ("shown", "ok", "confirm")

    def routed(r):
        return r.get("status") in OK and bool(r.get("p_holes") or (r.get("timing") or {}).get("perception"))

    def build(slug, extra=None):
        say = lambda *a: logs.append(" ".join(str(x) for x in a))    # noqa: E731
        r = fast.build(None, slug=slug, row=row, extra=extra, log=say)
        if (r.get("timing") or {}).get("card_late") or r.get("status") not in OK:
            # the web-card search runs beside the imagery fetch and the first build does not wait for it: let it
            # finish (it lands in the cache) and build once more with the card
            logs.append("card search still running after the first build: waiting for it, then building again")
            try:
                fast.wait_card(240)
            except Exception:                                        # noqa: BLE001
                pass
            r = fast.build(None, slug=slug, row=row, extra=extra, log=say)
        return r
    slug = "routed_" + q["slug"]
    r = build(slug)
    dropped = False
    if r.get("status") not in OK:
        # a partly mapped course whose few OSM hole lines do not fit the routing (renumbered or rebuilt course:
        # Jayhawk Club, 10 of 18 mapped, routed holes sharing greens with them): route every hole from the photos
        logs.append(f"first routing {r.get('status')}: {(r.get('why') or '')[:200]}; routing again without the OSM hole lines")
        r2 = build(slug + "_all", dict(ignore_osm_holes=True))
        if r2.get("status") in OK:
            r, slug, dropped = r2, slug + "_all", True
    d = r.get("dir") or os.path.join(fast.pc.PACKAGES, slug)
    # the routed holes: the supplement the routed build's own request ended with (the perception scene's holes, or
    # the joint solver's when OSM has the greens and tees but not the lines)
    sup = os.path.join(d, "raw", "scene_holes.geojson")
    try:
        sup = json.load(open(os.path.join(d, "package_request.json"))).get("osm_supplement") or sup
    except (OSError, ValueError):
        pass
    info = dict(schema="routing/1", status=r.get("status"), why=r.get("why"), holes=r.get("holes"),
                p_holes=r.get("p_holes"), approximate=r.get("approximate"), timing=r.get("timing"), log_tail=logs[-12:])
    rs = os.path.join(d, "route_scene.json")
    if os.path.exists(rs):
        x = json.load(open(rs))
        e = x.get("ensemble") or {}
        info.update(router=x.get("version"), ensemble={k: v for k, v in e.items() if k != "p"}, gate=(x.get("gate") or {}).get("reasons"),
                    card_select={k: v for k, v in (x.get("card_select") or {}).items() if k != "card"})
    pj = os.path.join(d, "package.json")
    if os.path.exists(pj):
        P = json.load(open(pj))
        rc = P.get("routing_confidence") or {}
        info.update(p_holes=rc.get("p_holes") or info["p_holes"], approximate=rc.get("approximate") or info["approximate"],
                    approx_below=rc.get("approx_below"), source=rc.get("source"), warnings=rc.get("warnings"),
                    imagery_year=(P.get("imagery") or {}).get("year"))
    info["ignore_osm_holes"] = dropped
    info["no_osm_course"] = not row.get("osm")
    ok = os.path.exists(sup) and r.get("status") in ("shown", "ok", "confirm") and bool(info.get("p_holes"))
    os.makedirs(out, exist_ok=True)
    if ok:
        shutil.copy(sup, os.path.join(out, "routed_holes.geojson"))
        card = routed_card(d)
        if card:
            json.dump(card, open(os.path.join(out, "routed_card.json"), "w"), indent=1)
            info["card"] = card.get("source")
    json.dump(info, open(os.path.join(out, "routing.json"), "w"), indent=1)
    print("route_unmapped:", r.get("status"), "|", (r.get("why") or "")[:300], "| supplement", "written" if ok else "none")
    return 0 if ok else 1


def routed_card(d):
    """The scorecard the routed build used, as a card file for the page's package. The page's own card search runs
    after the routed lines exist and checks each web card against their lengths; routed lines often start at a
    forward tee, so it would reject the very card the routing was fitted to and build the page without yardages."""
    p = os.path.join(d, "raw", "scene_card.json")              # the router switched cards / a 9-hole repeating card
    if os.path.exists(p):
        return json.load(open(p))
    pj, web = os.path.join(d, "package.json"), os.path.join(d, "raw", "scorecard_web.json")
    if not (os.path.exists(pj) and os.path.exists(web)):
        return None
    sc = json.load(open(pj)).get("scorecard") or {}
    for c in json.load(open(web)).get("cards") or []:
        if c.get("card") and c.get("source") == sc.get("source") and (not sc.get("url") or c.get("url") == sc.get("url")):
            card = dict(c["card"])
            if c.get("url") and not isinstance(card.get("source"), str):
                card["source"] = c["url"]
            return card
    return None


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
