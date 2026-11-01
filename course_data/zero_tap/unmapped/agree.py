"""Unmapped tiers: per-hole confidence from two independent routers agreeing (taps to 98 % pair precision).

    python course_data/zero_tap/unmapped/agree.py              # dev: compare confidence rules (dev only)
    python course_data/zero_tap/unmapped/agree.py agree_mean   # + test once at the dev threshold, writes results

Holes, numbers and pars are sequence_v3's (unmapped_card); a hole's confidence is the mean of sequence_v3's and
pathroute_v2_unmapped's when pathroute has the same green (15 m) with a tee within 30 m of one of sequence_v3's
boxes, else 0 (always asked). Rule chosen on dev (agree_mean: fewest dev taps, simplest of the ties); the taps
threshold is fitted on dev and applied to test unchanged. Writes results/sequence_v3_agree/unmapped_card/.
"""
import json
import math
import os
import sys

import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ZT, 'pathroute_v2'), ZT]
import bench as B, detect_eval as DE, confidence as CF, run2 as R2
import honest_eval as HE
def ll2xy(a, b):
    k = math.cos(math.radians(b[1])); return math.hypot((a[0]-b[0])*111320*k, (a[1]-b[1])*110540)
seq = {x['slug']: x for x in B.load_results(os.path.join(ZT, 'results', 'sequence_v3/unmapped_card'))}
pr = {x['slug']: x for x in B.load_results(os.path.join(ZT, 'results', 'pathroute_v2_unmapped/unmapped_nocard'))}
def combine(s, p, mode):
    s = json.loads(json.dumps(s))
    for h in s.get('holes') or []:
        best = None
        for q in p.get('holes') or []:
            if h.get('green_ll') and q.get('green_ll') and ll2xy(h['green_ll'], q['green_ll']) < 15:
                best = q
        agree = False
        if best and h.get('tee_ll'):
            tp = [best.get('tee_ll')] + list(best.get('tee_boxes_ll') or [])
            th = [h.get('tee_ll')] + list(h.get('tee_boxes_ll') or [])
            agree = any(a and b and ll2xy(a, b) < 30 for a in tp for b in th)
        cs, cp = float(h.get('confidence') or 0), float((best or {}).get('confidence') or 0)
        if mode == 'seq': c = cs
        elif mode == 'agree_pr': c = cp if agree else 0.0
        elif mode == 'agree_mean': c = (cs + cp) / 2 if agree else 0.0
        elif mode == 'agree_max': c = max(cs, cp) if agree else 0.0
        elif mode == 'agree_bonus': c = min(1.0, (cs + cp) / 2 + 0.2) if agree else 0.5 * min(cs, cp)
        h['confidence'] = c
    return s
def rows(split, mode):
    out = []
    for r in B.courses(split, tier='unmapped_card'):
        x = combine(seq.get(r['slug']) or dict(slug=r['slug'], holes=[]), pr.get(r['slug']) or {}, mode)
        x['slug'] = r['slug']
        cr = R2.course_rows([x])[0]
        sc = DE.load_scene(r); r['_perc_models'] = sc['sources']['models']['perception']
        out.append((r, (np.r_[cr['c'], np.zeros(cr['miss'])], np.r_[cr['y'], np.zeros(cr['miss'], int)])))
    return out
modes = ['seq', 'agree_pr', 'agree_mean', 'agree_max', 'agree_bonus']
test_mode = sys.argv[1] if len(sys.argv) > 1 else None
for m in modes if not test_mode else [test_mode]:
    dv = rows('dev', m)
    tp = CF.taps_to_precision([c for _, c in dv], 0.98)
    line = f'{m:12s} dev thr {tp[0]:.3f} taps {tp[1]:.2f} prec {tp[2]:.4f}'
    if test_mode:
        te = rows('test', m)
        for sub in ('all', 'held_out'):
            sel = [c for r, c in te if sub == 'all' or DE.perc_split(r) == sub]
            line += f' | test {sub} ({len(sel)}): {HE.taps_at(sel, tp[0])}'
        for r in B.courses(None, tier='unmapped_card'):
            x = combine(seq.get(r['slug']) or dict(slug=r['slug'], holes=[]), pr.get(r['slug']) or {}, m)
            x.update(method='sequence_v3_agree', tier='unmapped_card', slug=r['slug'], taps_threshold_dev=round(tp[0], 4))
            B.write_result(x, os.path.join(ZT, 'results', 'sequence_v3_agree', 'unmapped_card'))
    print(line, flush=True)
