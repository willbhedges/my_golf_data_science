"""render.py <which> <set> [day] : each par 5's second shot over the 2023 photo with the map zones."""
import sys, os, json, numpy as np
ROOT='/home/user/my_golf_data_science/'
sys.path.insert(0, ROOT+'course_data/courses/gateway_national/opt'); sys.path.insert(0, ROOT+'course_data/courses')
import par5_second as P5
import rasterio, pyproj
from scipy.ndimage import map_coordinates
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
which, setn = sys.argv[1], sys.argv[2]; day = sys.argv[3] if len(sys.argv) > 3 else 'sat'
out = sys.argv[4] if len(sys.argv) > 4 else os.path.dirname(os.path.abspath(__file__))
Wd = P5.World(which); M = Wd.M
sys.path.insert(0, ROOT+'course_data/imagery'); import render as RD
res = json.load(open(ROOT+'course_data/courses/gateway_national/opt/results/par5_second_%s.json' % setn.replace(' ','_')))
src = rasterio.open(ROOT+'course_data/packages/gateway_national/imagery/naip_rgb.tif'); img = src.read(); T = pyproj.Transformer.from_crs(4326, src.crs, always_xy=True)
COL = {'water':'#3af','native':'orange','sand':'yellow','recovery':'#0a0','ob':'r','fairway':'lime','first_cut':'#9f9'}
for h in P5.PAR5:
    r = res['%d|%s' % (h, day)]
    hd, back = Wd.hole(h, setn)
    fr = RD.Frame.from_json(Wd.course.FRAMES[h])
    tee, fwd, right, ppy = M.frame(hd)
    g = np.array(r['green'])
    a0, a1 = 200.0, g[0] + 45
    xs_all = [g[1]] + [v['start'][1] for v in r['second'].values()]
    x0, x1 = min(xs_all) - 75, max(xs_all) + 75
    st = 0.4
    xs = np.arange(x0, x1, st); als = np.arange(a0, a1, st); XX, AA = np.meshgrid(xs, als)
    px = tee + (AA.ravel()[:, None] * fwd + XX.ravel()[:, None] * right) * ppy
    ll = np.asarray(fr.px_to_ll(px)); E, N = T.transform(ll[:, 0], ll[:, 1])
    rr, cc = rasterio.transform.rowcol(src.transform, E, N, op=float)
    rgb = np.stack([map_coordinates(b.astype(float), [np.array(rr), np.array(cc)], order=1).reshape(XX.shape) for b in img[:3]], -1)
    lo, hi = np.percentile(rgb, [1, 99]); rgb = np.clip((rgb - lo) / (hi - lo), 0, 1)
    w = 7.0; hh = (a1 - a0) / (x1 - x0)
    fig, axs = plt.subplots(1, 2, figsize=(2 * w, w * hh + 0.5))
    for i, ax in enumerate(axs):
        ax.imshow(rgb, extent=[x0, x1, a0, a1], origin='lower')
        if i == 1:
            for name, poly in hd['zones']:
                if len(poly) < 3: continue
                p = (np.asarray(poly, float) - tee) / ppy; q = np.c_[p @ right, p @ fwd]; q = np.r_[q, q[:1]]
                ax.plot(q[:, 0], q[:, 1], color=COL.get(name, 'w'), lw=0.8)
            gp = np.array(r['green_poly']); gp = np.r_[gp, gp[:1]]; ax.plot(gp[:, 1], gp[:, 0], color='cyan', lw=1)
        for key, mk in (('Driver|fairway', 'o'), ('2-wood|fairway', 's')):
            v = r['second'][key]; s = v['start']
            ax.plot(s[1], s[0], mk, color='w', mfc='none', ms=9, mew=1.5); ax.annotate(key.split('|')[0], (s[1] + 3, s[0]), color='w', fontsize=8)
            for kind, col in (('go', 'r'), ('lay', 'cyan')):
                o = v.get(kind)
                if not o: continue
                t = o['target']
                ax.plot([s[1], t[1]], [s[0], t[0]], color=col, lw=0.8, ls='-' if key.startswith('Driver') else ':')
                ax.plot(t[1], t[0], 's' if kind == 'lay' else '*', color=col, mfc='none', ms=10, mew=1.5)
                ax.annotate('%s %s lv %d' % (kind, o['club'], o['leave']), (t[1] + 3, t[0] + (3 if key.startswith('Driver') else -6)), color=col, fontsize=7)
            if key.startswith('Driver'):
                for row in v['by_club']:
                    t = row['target']; ax.plot(t[1], t[0], '+', color='m', ms=7); ax.annotate(row['club'][:2], (t[1] - 9, t[0]), color='m', fontsize=6)
        ax.axvline(0, color='m', lw=0.3)
        ax.set_xlim(x0, x1); ax.set_ylim(a0, a1); ax.set_yticks(np.arange(np.ceil(a0 / 10) * 10, a1, 10)); ax.set_xticks(np.arange(np.ceil(x0 / 10) * 10, x1, 10))
        ax.grid(color='w', lw=0.2, alpha=.5); ax.tick_params(labelsize=6)
    fig.suptitle('Hole %d %s %s: second shot (white = tee-shot centres, cyan square = lay-up target, red star = go target, magenta + = each club best)' % (h, setn, day), fontsize=9)
    fig.tight_layout(); fn = '%s/second_h%02d_%s_%s.jpg' % (out, h, setn.replace(' ', '_'), day); fig.savefig(fn, dpi=75); print(fn)
