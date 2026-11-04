"""plan.py gets product/package.py even when platform/package.py already owns the module name 'package'.

pytest runs platform/ and product/ tests in one process; platform's tests import their package.py as `package`
first (alphabetical), and a bare `import package` in plan.py then got the platform builder (the test_parity
failure fixed in 6797539a9). Each case runs in a fresh interpreter so sys.modules starts clean."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)

CHECK = r"""
import importlib.util, os, sys
here, cd, platform_first = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
if platform_first:
    sys.path.insert(0, os.path.join(cd, "platform"))
    import package
    assert os.path.dirname(os.path.abspath(package.__file__)) == os.path.join(cd, "platform"), package.__file__
    sys.path.pop(0)
spec = importlib.util.spec_from_file_location("plan", os.path.join(here, "plan.py"))
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)
print(os.path.abspath(plan.PK.__file__))
for attr in ("load", "write_module", "import_module", "key_of", "ELEV_CLAMPED", "_tee_line_mod"):
    assert hasattr(plan.PK, attr), attr
"""


def _plan_pk_file(platform_first):
    r = subprocess.run([sys.executable, "-c", CHECK, HERE, CD, "1" if platform_first else "0"],
                       capture_output=True, text=True, cwd=CD, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout.strip().splitlines()[-1]


def test_plan_uses_product_package_after_platform_package():
    assert _plan_pk_file(platform_first=True) == os.path.join(HERE, "package.py")


def test_plan_uses_product_package_alone():
    assert _plan_pk_file(platform_first=False) == os.path.join(HERE, "package.py")
