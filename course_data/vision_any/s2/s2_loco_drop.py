import sys, numpy as np, s2lib as S2
DROP = [d for d in sys.argv[3].split(",") if d]
_cg = S2.course_grid
def cg(slug, fs):
    names, G, g = _cg(slug, fs)
    k = [i for i, n in enumerate(names) if not any(d in n for d in DROP)]
    return [names[i] for i in k], G[:, k], g
S2.course_grid = cg
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2]]
exec(open("s2_loco.py").read())
