"""Offline tests: osm_guard rejects partial / stale / thin Overpass answers and falls back to cached snapshots."""
import gzip
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import osm_guard as og  # noqa: E402

M = og.MIRRORS


def way(i, golf, lon=-94.47, lat=38.83, **tags):
    return dict(type="way", id=i, tags=dict(golf=golf, **tags),
                geometry=[dict(lat=lat, lon=lon), dict(lat=lat + 0.001, lon=lon + 0.001)])


def node(i, golf, lon=-94.47, lat=38.83):
    return dict(type="node", id=i, lat=lat, lon=lon, tags=dict(golf=golf))


def response(holes=18, greens=18, tees=40, pins=18, remark=None, base="2026-10-30T00:00:00Z"):
    els = [way(1000 + i, "hole", ref=str(i + 1)) for i in range(holes)]
    els += [way(2000 + i, "green") for i in range(greens)] + [way(3000 + i, "tee") for i in range(tees)]
    els += [node(4000 + i, "pin") for i in range(pins)]
    els += [way(9000, None, highway="service")]
    d = dict(version=0.6, osm3s=dict(timestamp_osm_base=base), elements=els)
    if remark:
        d["remark"] = remark
    return d


def fc_of(data):
    import fetch_course as fcm
    return fcm.to_geojson(data["elements"])


def snap(holes=18, date="2026-10-17T06:21:00Z", kind="structure"):
    fc = fc_of(response(holes=holes))
    return dict(kind=kind, path=f"course_data/structure/data/x/osm.geojson.gz", date=date,
                counts=og.golf_counts(fc), fc=fc)


class FakeOverpass:
    def __init__(self, answers):
        self.answers, self.calls = dict(answers), []

    def __call__(self, url, query, timeout):
        self.calls.append(url)
        a = self.answers.get(url, RuntimeError("HTTP 504 Gateway Timeout"))
        if isinstance(a, Exception):
            raise a
        return a


def run(fake, snaps):
    return og.fetch_guarded((0, 0, 1, 1), query="q", post=fake, snapshots=snaps, sleep=lambda s: None)


# ----------------------------------------------------------------------------- judging
def test_remark_problem():
    assert og.remark_problem({"remark": 'runtime error: Query timed out in "query" at line 3 after 181 seconds.'})
    assert og.remark_problem({"remark": "runtime error: Query run out of memory using about 2048 MB of RAM."})
    assert og.remark_problem({"remark": ""}) is None and og.remark_problem({}) is None


def test_thin_reasons():
    full = dict(hole=18, green=18, tee=40, pin=18)
    assert og.thin_reasons(full, full) == []
    creekmoor = dict(hole=0, green=19, tee=77, pin=0)                 # the 2026-10-30 fetch
    why = og.thin_reasons(creekmoor, dict(hole=18, green=19, tee=77, pin=18))
    assert any("0 golf=hole" in w for w in why) and any(w.startswith("pin") for w in why)
    assert og.thin_reasons(dict(hole=8, green=18, tee=40, pin=18), full)          # < half the snapshot's holes
    assert og.thin_reasons(dict(hole=10, green=18, tee=40, pin=18), full) == []    # not < half: accepted
    assert og.thin_reasons(dict(hole=0, green=19, tee=30), None)                   # no snapshot: suspicious
    assert og.thin_reasons(dict(hole=0, green=2, tee=3), None) == []               # barely mapped course
    assert og.thin_reasons(dict(hole=36, green=36, tee=80, pin=36), full) == []    # more is not thin


def test_reference_skips_thin_newer_snapshot():
    old, thin = snap(18, "2026-10-17T00:00:00Z"), snap(0, "2026-10-30T00:00:00Z", kind="package")
    assert og.reference([thin, old]) is old


# ----------------------------------------------------------------------------- fetch_guarded
def test_good_first_mirror():
    fake = FakeOverpass({M[0]: response()})
    data, fc, prov = run(fake, [snap()])
    assert prov["source"] == "overpass" and prov["mirror"] == M[0] and fake.calls == [M[0]]
    assert og.golf_counts(fc)["hole"] == 18


def test_timeout_remark_retries_next_mirror():
    fake = FakeOverpass({M[0]: response(holes=3, remark="runtime error: Query timed out in \"query\""),
                         M[1]: response()})
    data, fc, prov = run(fake, [])
    assert prov["source"] == "overpass" and prov["mirror"] == M[1]
    assert "Overpass remark" in prov["attempts"][0]["thin"][0]


def test_creekmoor_thin_on_every_mirror_merges_snapshot():
    thin = response(holes=0, pins=0, greens=19, tees=77)
    fake = FakeOverpass({u: thin for u in M})
    data, fc, prov = run(fake, [snap(18)])
    assert fake.calls == M                                      # every mirror tried once, no second pass
    assert prov["source"] == "overpass+snapshot" and "0 golf=hole" in prov["reason"]
    c = og.golf_counts(fc)
    assert c["hole"] == 18 and c["pin"] == 18 and c["green"] == 19   # snapshot holes + fresh greens (ids overlap)
    assert all(f["properties"].get("src") == "snapshot" for f in fc["features"]
               if f["properties"].get("golf") == "hole")


def test_stale_mirror_skipped():
    fake = FakeOverpass({M[0]: response(holes=0, pins=0, base="2026-10-01T00:00:00Z"), M[1]: response()})
    data, fc, prov = run(fake, [snap(18, "2026-10-17T06:21:00Z")])
    assert prov["mirror"] == M[1]
    assert any("older than" in w for w in prov["attempts"][0]["thin"])


def test_no_mirror_answers_uses_snapshot():
    fake = FakeOverpass({})
    data, fc, prov = run(fake, [snap(18)])
    assert data is None and prov["source"] == "snapshot" and og.golf_counts(fc)["hole"] == 18
    assert len(fake.calls) == 3 * len(M)                        # three passes, then the snapshot


def test_no_mirror_no_snapshot_raises():
    with pytest.raises(RuntimeError):
        run(FakeOverpass({}), [])


def test_thin_without_snapshot_used_but_recorded():
    thin = response(holes=0, pins=0, greens=18, tees=40)
    fake = FakeOverpass({u: thin for u in M})
    data, fc, prov = run(fake, [])
    assert len(fake.calls) == 2                                 # two mirrors agree: that is the map
    assert prov["source"] == "overpass" and prov["thin"] and "no cached snapshot" in prov["reason"]


def test_more_holes_than_snapshot_accepted_with_note():
    fake = FakeOverpass({M[0]: response(holes=27)})
    data, fc, prov = run(fake, [snap(18)])
    assert prov["source"] == "overpass" and "more holes" in prov["note"]


def test_deadline_bounds_the_step():
    t = [0.0]

    def slow(url, query, timeout):
        t[0] += 400
        raise RuntimeError("read timeout")
    prov = og.fetch_guarded((0, 0, 1, 1), query="q", post=slow, snapshots=[snap()], sleep=lambda s: None,
                            now=lambda: t[0], deadline_s=900)[2]
    assert prov["source"] == "snapshot" and len(prov["attempts"]) == 3


def test_snapshot_discovery(tmp_path):
    st = tmp_path / "structure" / "creekmoor_mo"
    st.mkdir(parents=True)
    (st / "course.json").write_text(json.dumps(dict(osm=dict(type="relation", id=4249741), state="MO")))
    with gzip.open(st / "osm.geojson.gz", "wt") as fh:
        json.dump(fc_of(response()), fh)
    os.utime(st / "osm.geojson.gz", (1792218060, 1792218060))            # 2026-10-17
    pk = tmp_path / "packages" / "creekmoor" / "raw"
    pk.mkdir(parents=True)
    (pk / "course.json").write_text(json.dumps(dict(osm=dict(type="relation", id=4249741))))
    (pk / "summary.json").write_text(json.dumps(dict(fetched_utc="2026-10-30T00:11:10Z")))
    (pk / "osm.geojson").write_text(json.dumps(fc_of(response(holes=0, pins=0))))
    snaps = og.load_snapshots(dict(osm=dict(type="relation", id=4249741)), "creekmoor",
                              packages=str(tmp_path / "packages"), library=str(tmp_path / "lib"),
                              structure=str(tmp_path / "structure"))
    assert [s["kind"] for s in snaps] == ["package", "structure"]        # newest first
    assert og.reference(snaps)["kind"] == "structure"                    # the thin package fetch is no reference


def test_merge_keeps_fresh_and_adds_missing():
    fresh = fc_of(response(holes=0))
    merged, n = og.merge(fresh, fc_of(response()))
    assert n == 18 and og.golf_counts(merged)["hole"] == 18 and len(merged["features"]) == len(fresh["features"]) + 18
