"""solve_c.simulate_c (C roll-out) == tee_strategy.simulate with the lie raster, array for array, on built courses.

  python3 -m pytest -q course_data/platform/fastpath/test_solve_c.py    (skips courses whose package is not built)
"""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
COURSES = ["b20_chevy_chase", "b20_crow_canyon"]


def _load(slug):
    p = os.path.join(HERE, "cache", "packages", slug, "package.json")
    if not os.path.exists(p):
        pytest.skip(f"{slug} not built")
    import importlib.util as _ilu                # fastpath/solve.py by path: `import solve` can be zero_tap's
    spec = _ilu.spec_from_file_location("fastpath_solve", os.path.join(HERE, "solve.py"))
    SV = sys.modules.get("fastpath_solve") or _ilu.module_from_spec(spec)
    sys.modules["fastpath_solve"] = SV           # solve_c finds the raster's module by name
    if not hasattr(SV, "EB"):
        spec.loader.exec_module(SV)
    EB = SV.EB
    pkg = json.load(open(p))
    C = EB.PK().load(p, pkg.get("tee_set"))
    import decide
    decide.bind(dict(C.holes))
    decide.set_prior_means()
    SV.use_raster()
    return C


@pytest.mark.parametrize("slug", COURSES)
def test_simulate_c_identical(slug):
    C = _load(slug)
    import solve_c
    import tee_strategy as t
    import decide
    assert solve_c.install() or os.environ.get("GOLF_FASTC") == "0"
    py = t._simulate_py
    z = decide._z(2000, 31)
    n = 0
    for k in C.holes:
        for club in decide.clubs_for(k):
            for aim in (-15.0, 0.0, 12.5):
                a = py(k, club, aim, z=z)
                b = solve_c.simulate_c(k, club, aim, z=z)
                assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]), (k, club, aim)
                assert np.array_equal(a[2], b[2]) and np.array_equal(a[3], b[3]), (k, club, aim)
                n += 1
    assert n > 20
