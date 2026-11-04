"""Offline checks of truth set v2: every registered course with holes_truth.json is complete and consistent."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import truth_sets as TS  # noqa: E402

SLUGS = sorted(TS.available())


def test_registry_has_courses():
    assert SLUGS, "no truth set v2 course with holes_truth.json"


@pytest.mark.parametrize("slug", SLUGS)
def test_course(slug):
    T, HZ = TS.load(slug)
    assert len(T["holes"]) == 18
    pars = [T["holes"][str(i)]["par"] for i in range(1, 19)]
    assert all(p in (3, 4, 5) for p in pars)
    meta = json.load(open(os.path.join(HERE, "index.json")))["courses"][slug]
    cs = meta["corridor_set"]
    for ref, h in T["holes"].items():
        assert h["green_ll"] and h["tees"], (slug, ref)
        assert cs in h["tees"], (slug, ref, cs)
        # corridor-set tee measured within 12 yds of the card unless CHECK.md explains it
        d = abs(h["measured"][cs] - h["card"][cs])
        if d > 12:
            assert f"| {ref} |" in open(os.path.join(HERE, slug, "CHECK.md")).read(), (slug, ref, d)
        for s, c in (h.get("tee_confidence") or {}).items():   # a re-check disputes this truth tee: say why
            assert s in h["tees"] and c == "low", (slug, ref, s, c)
            assert "LOW CONFIDENCE" in h["note"] and f"| {ref} |" in open(os.path.join(HERE, slug, "CHECK.md")).read()
    for ref, z in HZ.items():
        assert T["holes"][ref]["par"] >= 4
        assert z["footprint_ll"] and z["zones"]
        assert {q["lie"] for q in z["zones"]} <= {"fairway", "recovery", "water", "sand", "native", "ob", "rough",
                                                   "first_cut"}


@pytest.mark.parametrize("slug", SLUGS)
def test_truth_package_layers(slug):
    p = os.path.join(TS.CD, "packages", slug, "package.json")
    if not os.path.exists(p):
        pytest.skip("auto package not checked out")
    auto = json.load(open(p))
    T, HZ = TS.load(slug)
    only_tees = TS.truth_package(slug, auto, None, layers=("tees",))
    ref = next(iter(HZ)) if HZ else "1"
    assert only_tees["holes"][ref].get("zones_ll") == auto["holes"][ref].get("zones_ll")
    full = TS.truth_package(slug, auto, None)
    if HZ:
        assert any(z.get("src") == "hand" for z in full["holes"][ref]["zones_ll"])
