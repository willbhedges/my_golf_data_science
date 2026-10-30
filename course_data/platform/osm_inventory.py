"""Inventory of cached OSM snapshots, and library / package builds made from a thinner fetch than a snapshot.

  python course_data/platform/osm_inventory.py            -> course_data/platform/osm_inventory.json + a table

Snapshots: every OSM cache in osm_guard.SNAPSHOT_GLOBS (structure/data, zero_tap, generalize/courses, ob, packages,
library raw). Builds: library/<slug>/raw/summary.json (+ library/gate) and packages/<slug>/raw/summary.json
(golf_tag_counts of the fetch the build used), and each library build's earlier committed summary.json versions.
A build is "thin" when osm_guard.thin_reasons flags its counts against a snapshot of the same OSM course (matched
by OSM type/id, or by directory name when the cache has no course.json) or against an earlier build of itself;
with nothing to compare, "suspect" when it has 0 hole ways but many greens and tees.
Builds whose request dropped the OSM holes on purpose (ignore_osm_holes) are listed but not flagged for holes.
Offline: reads the repo only.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import osm_guard as og  # noqa: E402
import platform_common as pc  # noqa: E402

OUT = os.path.join(HERE, "osm_inventory.json")


def _key(cj):
    o = (cj or {}).get("osm") or {}
    return f"{o.get('type')}/{o.get('id')}" if o.get("id") else None


def snapshots():
    rows = []
    for kind, g in og.SNAPSHOT_GLOBS:
        for p in sorted(glob.glob(os.path.join(pc.COURSE_DATA, g))):
            key, name, sp, _ = og._snapshot_key(p)
            fc = og._read_fc(p)
            if not fc:
                continue
            rows.append(dict(slug=name, kind=kind, osm=f"{key[0]}/{key[1]}" if key else None,
                             path=os.path.relpath(p, pc.ROOT), date=og._date_of(p, pc.read_json(sp) if sp else None),
                             counts=og.golf_counts(fc), features=len(fc.get("features", []))))
    return rows


def history(sp):
    """Earlier committed versions of a build's summary.json -> [(commit date, fetched_utc, counts)]."""
    import subprocess
    try:
        log = subprocess.run(["git", "-C", pc.ROOT, "log", "--format=%H %cI", "--", os.path.relpath(sp, pc.ROOT)],
                             capture_output=True, text=True, timeout=60).stdout.split("\n")
    except Exception:                                           # noqa: BLE001
        return []
    out, seen = [], set()
    for line in log[1:]:                                        # [0] is the current version
        if not line.strip():
            continue
        h, d = line.split()
        try:
            js = json.loads(subprocess.run(["git", "-C", pc.ROOT, "show", f"{h}:{os.path.relpath(sp, pc.ROOT)}"],
                                           capture_output=True, text=True, timeout=60).stdout)
        except ValueError:
            continue
        if js.get("fetched_utc") in seen:
            continue
        seen.add(js.get("fetched_utc"))
        gc = js.get("golf_tag_counts") or {}
        out.append(dict(commit=h[:10], date=d, fetched=js.get("fetched_utc"), counts={k: gc.get(k, 0) for k in og.KINDS}))
    return out


def builds():
    rows = []
    for kind, g in (("library", "library/*/raw/summary.json"), ("library", "library/gate/*/raw/summary.json"),
                    ("package", "packages/*/raw/summary.json")):
        for sp in sorted(glob.glob(os.path.join(pc.COURSE_DATA, g))):
            d = os.path.dirname(sp)
            slug = os.path.basename(os.path.dirname(d))
            summ = pc.read_json(sp) or {}
            gc = summ.get("golf_tag_counts") or {}
            req = pc.read_json(os.path.join(os.path.dirname(d), "package_request.json")) or \
                pc.read_json(os.path.join(pc.REQUESTS, f"package_{slug}.json")) or {}
            rows.append(dict(slug=slug, kind=kind, osm=_key(pc.read_json(os.path.join(d, "course.json"))),
                             fetched=summ.get("fetched_utc"), counts={k: gc.get(k, 0) for k in og.KINDS},
                             source=(summ.get("osm_source") or {}).get("source"),
                             ignore_osm_holes=bool(req.get("ignore_osm_holes")),
                             osm_supplement=req.get("osm_supplement"),
                             path=os.path.relpath(sp, pc.ROOT), history=history(sp) if kind == "library" else []))
    return rows


def compare(snaps, blds):
    by = {}
    for s in snaps:
        by.setdefault(s["osm"], []).append(s)
    out = []
    for b in blds:
        mine = os.path.dirname(b["path"])
        bare = b["slug"].replace("gate_", "")
        refs = [s for s in (by.get(b["osm"], []) if b["osm"] else []) + by.get(None, [])
                if not s["path"].startswith(mine) and (s["osm"] or s["slug"] in (b["slug"], bare))]
        why = []
        for s in refs:
            w = og.thin_reasons(b["counts"], s["counts"], f"{s['kind']} snapshot {s['path']} ({(s['date'] or '?')[:10]})")
            if b["ignore_osm_holes"]:
                w = [x for x in w if not x.startswith(("0 golf=hole", "hole:", "pin:"))]
            why += w
        for hst in b["history"]:
            if hst["fetched"] == b["fetched"]:
                continue
            w = og.thin_reasons(b["counts"], hst["counts"], f"earlier build fetched {(hst['fetched'] or '?')[:10]}")
            if b["ignore_osm_holes"]:
                w = [x for x in w if not x.startswith(("0 golf=hole", "hole:", "pin:"))]
            if w:
                why += w
                refs = refs + [dict(kind="history", path=f"{b['path']}@{hst['commit']}", date=hst["fetched"],
                                    counts=hst["counts"])]
        if not refs and not b["ignore_osm_holes"]:
            why += og.thin_reasons(b["counts"], None)
        out.append(dict(b, snapshots=[dict(path=s["path"], date=s["date"], counts=s["counts"]) for s in refs],
                        thin=why, rebuild=bool(why and refs)))
    return out


def main():
    snaps, blds = snapshots(), builds()
    cmp_ = compare(snaps, blds)
    res = dict(schema="osm_inventory/1", note=__doc__.strip().splitlines()[0], snapshots=snaps, builds=cmp_,
               rebuild=[b["slug"] for b in cmp_ if b["rebuild"] and b["kind"] == "library"],
               rebuild_packages=[b["slug"] for b in cmp_ if b["rebuild"] and b["kind"] == "package"],
               suspect_no_snapshot=[f"{b['kind']}/{b['slug']}" for b in cmp_ if b["thin"] and not b["snapshots"]])
    pc.write_json(OUT, res)
    with_snap = [b for b in cmp_ if b["snapshots"]]
    print(f"{len(snaps)} snapshots, {len(blds)} builds, {len(with_snap)} builds with a snapshot of the same course")
    for b in with_snap:
        s = b["snapshots"][0]["counts"]
        print(f"  {b['kind']:8s} {b['slug']:24s} build h/g/t/p {b['counts']['hole']}/{b['counts']['green']}/"
              f"{b['counts']['tee']}/{b['counts']['pin']}  snapshot {s['hole']}/{s['green']}/{s['tee']}/{s['pin']}"
              f"  {'THIN: ' + '; '.join(b['thin']) if b['thin'] else 'ok'}")
    print("rebuild (library):", res["rebuild"])
    print("rebuild (packages):", res["rebuild_packages"])
    print("suspect, no snapshot to compare:", res["suspect_no_snapshot"])
    return res


if __name__ == "__main__":
    main()
