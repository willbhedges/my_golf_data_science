"""Per course / year: median NDVI (Jun, Jul-Sep min, March) of fairway, rough band (rf), off-course open land, and
truth native / rough cells. python3 drought_diag.py slug..."""
import sys, numpy as np, warnings
warnings.simplefilter("ignore")
import s2lib as S2, common
for slug in sys.argv[1:]:
    st = S2.load_stack(slug); g = S2.load_g10(slug)
    months = [str(m) for m in st["months"]]
    I = st["idx"].astype(np.float32); I[I == -128] = np.nan; I /= 100
    k = [str(n) for n in st["inames"]].index("ndvi")
    fw = np.nan_to_num(g["fairway"]) >= 0.7
    rf = (np.nan_to_num(g["mown"]) == 0) & (np.nan_to_num(g["canopy"]) < 0.05) & (g["dfw_mean"] >= 5) & (g["dfw_mean"] <= 25) & (np.nan_to_num(g["water"]) == 0)
    off = (np.nan_to_num(g["course"]) < 0.05) & (np.nan_to_num(g["canopy"]) < 0.05) & (np.nan_to_num(g["water"]) == 0)
    d = common.load(slug); cell = S2.map_1m(d["idx"], g)
    nat = np.zeros(int(g["H"]) * int(g["W"]), bool); rou = nat.copy()
    for m, c in ((nat, [4]), (rou, [0, 1])):
        u, n = np.unique(cell[np.isin(d["cls"], c)], return_counts=True); m[u[n >= 50]] = True
    nat = nat.reshape(fw.shape); rou = rou.reshape(fw.shape) & ~nat
    print(f"== {slug}: fw {fw.sum()} rf {rf.sum()} off {off.sum()} nat10 {nat.sum()} rough10 {rou.sum()}")
    for y in sorted({m[:4] for m in months}):
        def mo(ms, f):
            j = [months.index(f"{y}-{m:02d}") for m in ms if f"{y}-{m:02d}" in months]
            return f(I[j, k], axis=0) if j else np.full(fw.shape, np.nan)
        jun = mo([5, 6], np.nanmax); smin = mo([7, 8, 9], np.nanmin); mar = mo([3], np.nanmax)
        row = []
        for nm, m in (("fw", fw), ("rf", rf), ("off", off), ("nat", nat), ("rgh", rou)):
            row.append(f"{nm} {np.nanmedian(jun[m]):.2f}/{np.nanmedian(smin[m]):.2f}/{np.nanmedian(mar[m]):.2f}" if m.sum() else f"{nm} -")
        print("  ", y, " | ".join(row))
