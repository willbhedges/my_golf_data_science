/* holesolve kernel: one Bellman backup  V(s) = cal(s) + min over (club, direction) of E[1 + value(finish)]
 * for a batch of states, on a lie raster in the tee frame (a = yds along the tee line, l = yds right of it).
 *
 * Built like fastsolve's kernel: gcc -O3 -march=native -fopenmp, loaded with ctypes (kernel.py).
 *
 * Raster arrays, row-major [na][nl], cell = round((a - A0) / res), round((l - L0) / res), clipped to the raster:
 *   rk     roll / rule kind of the cell: 0 fairway-like (ball rolls), 1 rough (roll x rough_roll), 2 dry, ball stops
 *          (sand, trees), 3 penalty area played as a drop (1 stroke + relief), 4 ball gone = stroke and distance
 *          (out of bounds; tall grass under the lost-ball rule)
 *   cellv  expected strokes to hole out for a ball at rest in the cell (kinds 0-2)
 *   dropv  expected strokes after a drop whose reference point is the cell (kinds 0-2): the better of the cell's own
 *          lie and back-on-the-line, prepared by the caller
 * Swings: car / dev / roll [nlc][nclub][ns] (carry along the shot line, yds right of it, roll), one set per lie class
 * of the START (fairway / rough / sand rules), common to every state, club and direction.
 * A swing: land at carry, roll on along the ball's own line in 2-yd steps (the engine's finish(): x rough_roll when
 * it lands in or rolls from short grass into rough, stops in kinds >= 2).
 *   kind 3: walk back along the ball's line in 1-yd steps to the first cell of kind <= 2: 1 + dropv there
 *           (back at the start: 1 + the start's own value = stroke and distance)
 *   kind 4: the same shot again from the same spot, closed form:
 *           E = (n + sum of found values + n_gone * (1 + cal)) / (n - n_gone)
 * Directions: th0[s] + ang[j]; coarse pass every `stride`-th direction, then the directions between the best coarse
 * one and its neighbours.
 */
#include <math.h>
#include <stdint.h>
#include <float.h>
#include <stddef.h>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef struct {
    const int8_t *rk; const float *cellv; const float *dropv;
    int na, nl; float A0, L0, ires, rr;
} Ras;

static inline int cell(const Ras *R, float a, float l) {
    int ia = (int)lrintf((a - R->A0) * R->ires), il = (int)lrintf((l - R->L0) * R->ires);
    if (ia < 0) ia = 0; else if (ia >= R->na) ia = R->na - 1;
    if (il < 0) il = 0; else if (il >= R->nl) il = R->nl - 1;
    return ia * R->nl + il;
}

/* value of one swing; returns 1 if the ball is gone (kind 4), else 0 and *v */
static inline int swing(const Ras *R, float a0, float l0, float ua, float ul, float car, float dev, float roll,
                        float vself, float *v, int *kind_out) {
    float a = a0 + car * ua - dev * ul, l = l0 + car * ul + dev * ua;
    float n = sqrtf((a - a0) * (a - a0) + (l - l0) * (l - l0));
    float fa = n > 1e-6f ? (a - a0) / n : ua, fl = n > 1e-6f ? (l - l0) / n : ul;
    int c = cell(R, a, l);
    int k = R->rk[c];
    float left = roll;
    if (k == 1) left *= R->rr; else if (k >= 2) left = 0.f;
    while (left > 1e-6f) {
        float st = left < 2.f ? left : 2.f;
        a += fa * st; l += fl * st; left -= st;
        c = cell(R, a, l);
        int nk = R->rk[c];
        if (nk == 1 && k == 0) left *= R->rr;
        if (nk >= 2) left = 0.f;
        k = nk;
    }
    *kind_out = k;
    if (k <= 2) { *v = R->cellv[c]; return 0; }
    if (k == 4) return 1;
    n = sqrtf((a - a0) * (a - a0) + (l - l0) * (l - l0));
    for (float t = n - 1.f; ; t -= 1.f) {
        if (t <= 0.f) { *v = 1.f + vself; return 0; }
        int q = cell(R, a0 + fa * t, l0 + fl * t);
        if (R->rk[q] <= 2) { *v = 1.f + R->dropv[q]; return 0; }
    }
}

static float action(const Ras *R, float a0, float l0, float th, const float *car, const float *dev,
                    const float *roll, int ns, float cal, float vself, float *pen_share) {
    float ua = cosf(th), ul = sinf(th);
    double sum = 0.0; int gone = 0, pen = 0;
    for (int i = 0; i < ns; i++) {
        float v; int k;
        if (swing(R, a0, l0, ua, ul, car[i], dev[i], roll[i], vself, &v, &k)) gone++;
        else { sum += v; if (k == 3) pen++; }
    }
    if (pen_share) *pen_share = (float)(pen + gone) / ns;
    if (gone >= ns) return FLT_MAX;
    return (float)((ns + sum + gone * (1.0 + cal)) / (ns - gone));
}

void hs_backup(const int8_t *rk, const float *cellv, const float *dropv, int na, int nl, float A0, float L0,
               float res, float rough_roll,
               int nclub, int ns, const float *car, const float *dev, const float *roll,
               int nang, const float *ang, int stride,
               int nst, const float *sa, const float *sl, const float *th0, const int32_t *slc,
               const uint32_t *mask, const float *cal, const float *vprev,
               float *vout, int32_t *bclub, float *bang, float *ev_club, float *ang_club) {
    Ras R = {rk, cellv, dropv, na, nl, A0, L0, 1.f / res, rough_roll};
    if (stride < 1) stride = 1;
    #pragma omp parallel for schedule(dynamic, 8)
    for (int s = 0; s < nst; s++) {
        float best = FLT_MAX; int bc = -1; float ba = 0.f;
        for (int c = 0; c < nclub; c++) {
            float e_best = FLT_MAX; int j_best = -1;
            if (mask[s] >> c & 1u) {
                const float *pc = car + ((size_t)slc[s] * nclub + c) * ns;
                const float *pd = dev + ((size_t)slc[s] * nclub + c) * ns;
                const float *pr = roll + ((size_t)slc[s] * nclub + c) * ns;
                for (int j = 0; j < nang; j += stride) {
                    float e = action(&R, sa[s], sl[s], th0[s] + ang[j], pc, pd, pr, ns, cal[s], vprev[s], 0);
                    if (e < e_best) { e_best = e; j_best = j; }
                }
                if (stride > 1 && j_best >= 0) {
                    int lo = j_best - stride + 1, hi = j_best + stride - 1, jc = j_best;
                    if (lo < 0) lo = 0;
                    if (hi > nang - 1) hi = nang - 1;
                    for (int j = lo; j <= hi; j++) {
                        if (j == jc) continue;
                        float e = action(&R, sa[s], sl[s], th0[s] + ang[j], pc, pd, pr, ns, cal[s], vprev[s], 0);
                        if (e < e_best) { e_best = e; j_best = j; }
                    }
                }
            }
            if (ev_club) { ev_club[(size_t)s * nclub + c] = e_best; ang_club[(size_t)s * nclub + c] = j_best >= 0 ? ang[j_best] : 0.f; }
            if (e_best < best) { best = e_best; bc = c; ba = ang[j_best]; }
        }
        vout[s] = best < FLT_MAX ? cal[s] + best : vprev[s];
        bclub[s] = bc; bang[s] = ba;
    }
}

/* every direction of one club from one state (reports and tests): ev[nang], pen[nang] */
void hs_curve(const int8_t *rk, const float *cellv, const float *dropv, int na, int nl, float A0, float L0,
              float res, float rough_roll, int ns, const float *car, const float *dev, const float *roll,
              int nang, const float *th, float a0, float l0, float cal, float vself, float *ev, float *pen) {
    Ras R = {rk, cellv, dropv, na, nl, A0, L0, 1.f / res, rough_roll};
    #pragma omp parallel for schedule(static)
    for (int j = 0; j < nang; j++)
        ev[j] = action(&R, a0, l0, th[j], car, dev, roll, ns, cal, vself, pen + j);
}
