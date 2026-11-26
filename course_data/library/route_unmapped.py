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
    return fast.lookup(", ".join(x for x in (q["name"], q.get("city"), q["state"]) if x))


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
    slug = "routed_" + q["slug"]
    r = fast.build(None, slug=slug, row=row, log=lambda *a: logs.append(" ".join(str(x) for x in a)))
    if (r.get("timing") or {}).get("card_late") or r.get("status") not in ("shown", "ok", "confirm"):
        # the web-card search runs beside the imagery fetch and the first build does not wait for it: let it finish
        # (it lands in the cache) and build once more with the card
        logs.append("card search still running after the first build: waiting for it, then building again")
        try:
            fast.wait_card(240)
        except Exception:                                            # noqa: BLE001
            pass
        r = fast.build(None, slug=slug, row=row, log=lambda *a: logs.append(" ".join(str(x) for x in a)))
    d = r.get("dir") or os.path.join(fast.pc.PACKAGES, slug)
    sup = os.path.join(d, "raw", "scene_holes.geojson")
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
    ok = os.path.exists(sup) and r.get("status") in ("shown", "ok", "confirm") and bool(info.get("p_holes"))
    os.makedirs(out, exist_ok=True)
    if ok:
        shutil.copy(sup, os.path.join(out, "routed_holes.geojson"))
        card = os.path.join(d, "raw", "scene_card.json")
        if os.path.exists(card):
            shutil.copy(card, os.path.join(out, "routed_card.json"))
    json.dump(info, open(os.path.join(out, "routing.json"), "w"), indent=1)
    print("route_unmapped:", r.get("status"), "|", (r.get("why") or "")[:300], "| supplement", "written" if ok else "none")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
