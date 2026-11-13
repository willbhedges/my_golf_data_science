/* fastsolve kernel: the v2 tee-shot engine's per-sample loops in C (OpenMP).
 *
 * Every function reproduces spirit_hollow/v2/model.py (and course_data/courses/v2_course.py's lidar flight check)
 * operation for operation in IEEE double precision: same index rounding (rint, round-half-even, then clip), same
 * order of the floating-point operations, no fused multiply-add (-ffp-contract=off), no fast-math. The sums over the
 * swings run in swing order per aim, as numpy's mean(axis=0) of a (swings, aims) array does, so an EV curve is equal
 * to the engine's to the last bit (see README.md, "Equivalence").
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif

enum { ROUGH = 0, FAIRWAY = 1, FIRST_CUT = 2, SAND = 3, RECOVERY = 4, NATIVE = 5, WATER = 6, OB = 7, UNVERIFIED = 8 };
static const int HAZ[9] = {0, 0, 0, 1, 1, 1, 1, 1, 1};     /* model.HAZ: the ball stops where it lands */
static const int OPEN_[9] = {1, 1, 1, 1, 0, 0, 0, 0, 0};   /* model.OPEN */

static inline int cell(double v, double v0, double inv, int n)
{
    /* np.clip(np.rint((v - v0) / res).astype(np.int32), 0, n - 1); inv = 1 / res with res a power of two */
    double r = rint((v - v0) * inv);
    if (!(r > 0.0)) return 0;
    if (r >= (double)(n - 1)) return n - 1;
    return (int)r;
}

typedef struct {
    int nf;                 /* flight steps */
    const double *F;        /* fraction of the carry at each step mid-point */
    const double *y;        /* flight height there (yds) */
    const double *seg;      /* sqrt(1 + slope^2) of the flight in that step */
    double stepf;           /* step length as a fraction of the carry */
    double min_along;
    const float *top, *base;
    int nga, ngl;
    double ga0, gl0, inv_c; /* canopy grid origin, 1 / CANOPY_STEP */
    double tmax;
    int has_drop;
    const double *dg;
    int nda, ndl;
    double da0, dl0, inv_d; /* drop grid origin, 1 / DROP_STEP */
    double dmin;
    const float *need;      /* per swing: yds of crown the ball survives */
} lidar_t;

static inline double drop_at(const lidar_t *L, double pa, double pl)
{
    return L->dg[(size_t)cell(pa, L->da0, L->inv_d, L->nda) * L->ndl + cell(pl, L->dl0, L->inv_d, L->ndl)];
}

/* One tee shot: landing (c, lat0), roll r -> finish (a, l, lie). model.finish, one sample. */
static inline void roll_out(const int8_t *lie_g, int na, int nl, double a0, double l0, double inv,
                            double c, double lat0, double r, double rough_roll, int v1_roll,
                            double *fa, double *fl, int *flie)
{
    double a = c, l = lat0;
    int lie = lie_g[(size_t)cell(a, a0, inv, na) * nl + cell(l, l0, inv, nl)];
    double left = r;
    if (lie == ROUGH) left = left * rough_roll;
    if (HAZ[lie]) left = 0.0;
    if (left > 1e-9) {
        double norm = hypot(a, l);
        double den = norm > 1e-9 ? norm : 1e-9;
        double ua = a / den, ul = l / den;
        while (left > 1e-9) {
            double st = left < 2.0 ? left : 2.0;
            a = a + ua * st;
            l = l + ul * st;
            left = left - st;
            int nw = lie_g[(size_t)cell(a, a0, inv, na) * nl + cell(l, l0, inv, nl)];
            int was_fw = v1_roll ? (lie == FAIRWAY) : (lie == FAIRWAY || lie == FIRST_CUT);
            if (nw == ROUGH && was_fw) left = left * rough_roll;
            if (HAZ[nw]) left = 0.0;
            lie = nw;
        }
    }
    *fa = a; *fl = l; *flie = lie;
}

/* EV curve of one club: n swings x m aims. Per aim j, in swing order (numpy's mean(axis=0) order):
 *   sum_all[j] = sum of S over the swings                     (model.ev_curve: 1 + mean)
 *   v_all[j]   = sum of (1.0 + S); vA[j] over swings [0, ksplit), vB[j] over [ksplit, n)
 *                (decide.bayes: v = 1.0 + sv; v.mean(0), v[:k].mean(0), v[k:].mean(0))
 * oa/ol/olie/os (n x m, C order) are filled when not NULL. */
void fs_ev(const int8_t *lie_g, const double *S, int na, int nl, double a0, double l0, double inv,
           const double *car, const double *dev, const double *roll, int n,
           const double *aims, int m, double rough_roll, int v1_roll, int ksplit,
           const lidar_t *L,
           double *sum_all, double *vA, double *vB, double *v_all,
           double *oa, double *ol, int8_t *olie, double *os, int nthreads)
{
    if (nthreads < 1) nthreads = 1;
    #pragma omp parallel for schedule(dynamic, 2) num_threads(nthreads) if (nthreads > 1 && m > 1)
    for (int j = 0; j < m; j++) {
        double aim = aims[j];
        double sa = 0.0, sb = 0.0, st_all = 0.0, v_tot = 0.0;
        for (int i = 0; i < n; i++) {
            double c = car[i];
            double lat0 = dev[i] + aim;
            double a, l, s;
            int lie;
            int stopped = 0;
            if (L) {
                double d_land = L->has_drop ? drop_at(L, c, lat0) : 0.0;
                float acc = 0.0f;
                float need = L->need[i];
                for (int k = 0; k < L->nf; k++) {
                    double f = L->F[k], yf = L->y[k];
                    double pa = c * f;
                    if (!((yf - f * d_land + L->dmin < L->tmax) && (pa >= L->min_along))) continue;
                    double pl = lat0 * f;
                    double clear = yf - f * d_land + (L->has_drop ? drop_at(L, pa, pl) : 0.0);
                    size_t ci = (size_t)cell(pa, L->ga0, L->inv_c, L->nga) * L->ngl + cell(pl, L->gl0, L->inv_c, L->ngl);
                    if (!((clear < (double)L->top[ci]) && (clear > (double)L->base[ci]))) continue;
                    acc += (float)(c * L->stepf * L->seg[k]);   /* (car * stepf) * sqrt, as the engine */
                    if (acc >= need) { stopped = 1; a = pa; l = pl; break; }
                }
            }
            if (stopped) {
                lie = lie_g[(size_t)cell(a, a0, inv, na) * nl + cell(l, l0, inv, nl)];
            } else {
                roll_out(lie_g, na, nl, a0, l0, inv, c, lat0, roll[i], rough_roll, v1_roll, &a, &l, &lie);
            }
            s = S[(size_t)cell(a, a0, inv, na) * nl + cell(l, l0, inv, nl)];
            st_all += s;
            double v = 1.0 + s;
            v_tot += v;
            if (i < ksplit) sa += v; else sb += v;
            if (oa) {
                size_t o = (size_t)i * m + j;
                oa[o] = a; ol[o] = l; olie[o] = (int8_t)lie; os[o] = s;
            }
        }
        sum_all[j] = st_all; vA[j] = sa; vB[j] = sb; v_all[j] = v_tot;
    }
}

/* Path(poly).contains_points(pts) -> lie[inside] = code. matplotlib's point_in_path_impl (even-odd, crossings of the
 * +X ray, its exact inequality), only evaluated where the point's y lies inside the polygon's y range (outside it no
 * edge straddles the ray, so the result is "outside" there by the same arithmetic). */
void fs_fill(const double *pts, long npts, const double *poly, int nv, double dx, double dy, int8_t code,
             int8_t *lie, int nthreads)
{
    if (nv < 2) return;
    double *vx = (double *)malloc(sizeof(double) * nv), *vy = (double *)malloc(sizeof(double) * nv);
    double ymin = INFINITY, ymax = -INFINITY, xmin = INFINITY, xmax = -INFINITY;
    for (int k = 0; k < nv; k++) {
        vx[k] = poly[2 * k] + dx; vy[k] = poly[2 * k + 1] + dy;
        if (vy[k] < ymin) ymin = vy[k];
        if (vy[k] > ymax) ymax = vy[k];
        if (vx[k] < xmin) xmin = vx[k];
        if (vx[k] > xmax) xmax = vx[k];
    }
    /* edges bucketed by y so a point only meets the edges that can straddle its ray */
    int nb = 512;
    double h = (ymax - ymin) / nb;
    if (!(h > 0)) { free(vx); free(vy); return; }
    int *cnt = (int *)calloc(nb + 1, sizeof(int));
    for (int pass = 0; pass < 1; pass++) {
        for (int k = 0; k < nv; k++) {
            int k0 = k == 0 ? nv - 1 : k - 1;
            double lo = vy[k0] < vy[k] ? vy[k0] : vy[k], hi = vy[k0] < vy[k] ? vy[k] : vy[k0];
            int b0 = (int)floor((lo - ymin) / h) - 1, b1 = (int)floor((hi - ymin) / h) + 1;
            if (b0 < 0) b0 = 0;
            if (b1 > nb - 1) b1 = nb - 1;
            for (int b = b0; b <= b1; b++) cnt[b + 1]++;
        }
    }
    for (int b = 0; b < nb; b++) cnt[b + 1] += cnt[b];
    int *edges = (int *)malloc(sizeof(int) * (cnt[nb] > 0 ? cnt[nb] : 1));
    int *pos = (int *)malloc(sizeof(int) * nb);
    memcpy(pos, cnt, sizeof(int) * nb);
    for (int k = 0; k < nv; k++) {
        int k0 = k == 0 ? nv - 1 : k - 1;
        double lo = vy[k0] < vy[k] ? vy[k0] : vy[k], hi = vy[k0] < vy[k] ? vy[k] : vy[k0];
        int b0 = (int)floor((lo - ymin) / h) - 1, b1 = (int)floor((hi - ymin) / h) + 1;
        if (b0 < 0) b0 = 0;
        if (b1 > nb - 1) b1 = nb - 1;
        for (int b = b0; b <= b1; b++) edges[pos[b]++] = k;
    }
    if (nthreads < 1) nthreads = 1;
    #pragma omp parallel for schedule(static) num_threads(nthreads) if (nthreads > 1)
    for (long i = 0; i < npts; i++) {
        double tx = pts[2 * i], ty = pts[2 * i + 1];
        if (!(ty > ymin && ty <= ymax)) continue;
        if (tx > xmax + 1.0 || tx < xmin - 1.0) continue;
        int b = (int)floor((ty - ymin) / h);
        if (b < 0) b = 0;
        if (b > nb - 1) b = nb - 1;
        int in = 0;
        for (int e = cnt[b]; e < cnt[b + 1]; e++) {
            int k = edges[e];
            int k0 = k == 0 ? nv - 1 : k - 1;
            double vtx0 = vx[k0], vty0 = vy[k0], vtx1 = vx[k], vty1 = vy[k];
            int yflag0 = (vty0 >= ty), yflag1 = (vty1 >= ty);
            if (yflag0 != yflag1) {
                if ((((vty1 - ty) * (vtx0 - vtx1)) >= ((vtx1 - tx) * (vty0 - vty1))) == yflag1) in ^= 1;
            }
        }
        if (in) lie[i] = code;
    }
    free(vx); free(vy); free(cnt); free(edges); free(pos);
}

/* Raster._water_entry: entry_dist (pre-filled with dist) at the water cells. */
void fs_water_entry(const int8_t *lie, int na, int nl, double a0, double l0, double res, double g0, double g1,
                    double *entry, int nthreads)
{
    double inv = 1.0 / res;
    if (nthreads < 1) nthreads = 1;
    #pragma omp parallel for schedule(dynamic, 16) num_threads(nthreads) if (nthreads > 1)
    for (int ia = 0; ia < na; ia++) {
        for (int il = 0; il < nl; il++) {
            if (lie[(size_t)ia * nl + il] != WATER) continue;
            double a = a0 + ia * res, l = l0 + il * res;      /* == np.arange(A0, ..., RES)[ia] for these grids */
            double r = hypot(a, l);
            double ea = a, el = l;
            double den = r > 1e-9 ? r : 1e-9;
            for (int k = 1; k <= 120; k++) {
                double num = r - (double)k;
                if (num < 0.0) num = 0.0;
                double s = num / den;
                double pa = a * s, pl = l * s;
                if (lie[(size_t)cell(pa, a0, inv, na) * nl + cell(pl, l0, inv, nl)] != WATER) { ea = pa; el = pl; break; }
            }
            entry[(size_t)ia * nl + il] = hypot(ea - g0, el - g1);
        }
    }
}

/* Raster._blocked(near=10, far=60, step=5). */
void fs_blocked(const int8_t *lie, const double *dist, int na, int nl, double a0, double l0, double res,
                double a1, double l1, double g0, double g1, uint8_t *blk, int nthreads)
{
    double inv = 1.0 / res;
    if (nthreads < 1) nthreads = 1;
    #pragma omp parallel for schedule(dynamic, 16) num_threads(nthreads) if (nthreads > 1)
    for (int ia = 0; ia < na; ia++) {
        double a = a0 + ia * res;
        for (int il = 0; il < nl; il++) {
            size_t o = (size_t)ia * nl + il;
            blk[o] = 0;
            if (!(OPEN_[lie[o]] && a > 120.0)) continue;
            double l = l0 + il * res;
            double d = dist[o];
            double den = d > 1e-9 ? d : 1e-9;
            double ua = (g0 - a) / den, ul = (g1 - l) / den;
            for (int k = 0; k <= 10; k++) {
                double s = 10.0 + k * 5.0;
                if (!(s < d - 25.0)) continue;
                double pa = a + ua * s, pl = l + ul * s;
                if (!(pa >= a0 && pa <= a1 && pl >= l0 && pl <= l1)) continue;
                if (lie[(size_t)cell(pa, a0, inv, na) * nl + cell(pl, l0, inv, nl)] == RECOVERY) { blk[o] = 1; break; }
            }
        }
    }
}

int fs_max_threads(void)
{
#ifdef _OPENMP
    return omp_get_max_threads();
#else
    return 1;
#endif
}
