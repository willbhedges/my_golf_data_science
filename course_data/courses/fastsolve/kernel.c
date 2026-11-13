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

/* ------------------------------------------------------------------------------------------------ AVX-512 path
 * The same per-ball arithmetic on 8 balls per register and NB registers per group (so the roll steps of 32 balls
 * overlap in the pipeline). Every operation is the IEEE operation of the scalar code (add, mul, sub, div, sqrt,
 * round-half-even, min / max), per lane, so the lanes hold exactly the scalar results. hypot is glibc's
 * (sysdeps/ieee754/dbl-64/e_hypot.c, the non-FMA kernel) written out; fs_selfcheck() compares it with the libm in
 * use and the path falls back to calling libm per ball when they ever differ. */
#if defined(__AVX512F__) && defined(__AVX512VL__) && defined(__AVX512DQ__) && !defined(FS_NO_SIMD)
#include <immintrin.h>
#define FS_SIMD 1
#define NB 4
static int g_hypot_inline = 0;          /* set by fs_selfcheck() */

static inline double hypot_kernel(double ax, double ay)
{
    double t1, t2, h = sqrt(ax * ax + ay * ay);
    if (h <= 2.0 * ay) {
        double delta = h - ay;
        t1 = ax * (2.0 * delta - ax);
        t2 = (delta - 2.0 * (ax - ay)) * delta;
    } else {
        double delta = h - ax;
        t1 = 2.0 * delta * (ax - 2.0 * ay);
        t2 = (4.0 * delta - ay) * ay + delta * delta;
    }
    h -= (t1 + t2) / (2.0 * h);
    return h;
}

static inline __m512d hypot_v(__m512d x, __m512d y)
{
    const __m512d two = _mm512_set1_pd(2.0), four = _mm512_set1_pd(4.0);
    __m512d fx = _mm512_abs_pd(x), fy = _mm512_abs_pd(y);
    __m512d ax = _mm512_max_pd(fx, fy), ay = _mm512_min_pd(fx, fy);
    __m512d h = _mm512_sqrt_pd(_mm512_add_pd(_mm512_mul_pd(ax, ax), _mm512_mul_pd(ay, ay)));
    __mmask8 m = _mm512_cmp_pd_mask(h, _mm512_mul_pd(two, ay), _CMP_LE_OQ);
    __m512d d1 = _mm512_sub_pd(h, ay);
    __m512d t1a = _mm512_mul_pd(ax, _mm512_sub_pd(_mm512_mul_pd(two, d1), ax));
    __m512d t2a = _mm512_mul_pd(_mm512_sub_pd(d1, _mm512_mul_pd(two, _mm512_sub_pd(ax, ay))), d1);
    __m512d d2 = _mm512_sub_pd(h, ax);
    __m512d t1b = _mm512_mul_pd(_mm512_mul_pd(two, d2), _mm512_sub_pd(ax, _mm512_mul_pd(two, ay)));
    __m512d t2b = _mm512_add_pd(_mm512_mul_pd(_mm512_sub_pd(_mm512_mul_pd(four, d2), ay), ay), _mm512_mul_pd(d2, d2));
    __m512d t1 = _mm512_mask_blend_pd(m, t1b, t1a), t2 = _mm512_mask_blend_pd(m, t2b, t2a);
    __m512d r = _mm512_sub_pd(h, _mm512_div_pd(_mm512_add_pd(t1, t2), _mm512_mul_pd(two, h)));
    /* lanes glibc does not send through the kernel (ay tiny against ax, zero, huge): libm */
    __mmask8 odd = _mm512_cmp_pd_mask(ay, _mm512_mul_pd(ax, _mm512_set1_pd(0x1p-40)), _CMP_NGT_UQ)
                 | _mm512_cmp_pd_mask(ay, _mm512_set1_pd(1e-100), _CMP_NGT_UQ)
                 | _mm512_cmp_pd_mask(ax, _mm512_set1_pd(1e100), _CMP_NLT_UQ);
    if (odd || !g_hypot_inline) {
        double bx[8], by[8], br[8];
        _mm512_storeu_pd(bx, x); _mm512_storeu_pd(by, y); _mm512_storeu_pd(br, r);
        for (int k = 0; k < 8; k++)
            if (!g_hypot_inline || ((odd >> k) & 1)) br[k] = hypot(bx[k], by[k]);
        r = _mm512_loadu_pd(br);
    }
    return r;
}

typedef struct { __m512d a0, l0, inv, amax, lmax, nl; } grid_v;

static inline __m256i cell_v(const grid_v *g, __m512d a, __m512d l)
{
    const __m512d zero = _mm512_setzero_pd();
    __m512d ra = _mm512_roundscale_pd(_mm512_mul_pd(_mm512_sub_pd(a, g->a0), g->inv), _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
    __m512d rl = _mm512_roundscale_pd(_mm512_mul_pd(_mm512_sub_pd(l, g->l0), g->inv), _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
    ra = _mm512_min_pd(_mm512_max_pd(ra, zero), g->amax);       /* max(NaN, 0) = 0, as cell() */
    rl = _mm512_min_pd(_mm512_max_pd(rl, zero), g->lmax);
    return _mm512_cvttpd_epi32(_mm512_add_pd(_mm512_mul_pd(ra, g->nl), rl));    /* exact integers */
}

static inline __m256i lie_v(const int8_t *lie_pad, __m256i idx)
{
    return _mm256_and_si256(_mm256_i32gather_epi32((const int *)lie_pad, idx, 1), _mm256_set1_epi32(0xFF));
}

typedef struct { __m512d s[NB]; } group_out;

/* One swing at 8 * NB consecutive aims (lanes = aims: neighbouring raster cells, the same roll length, and the per-aim
 * sums become vector adds in swing order). Returns the strokes after the tee shot per aim. */
static inline __attribute__((always_inline)) void group(const int8_t *lie_pad, const double *S, const grid_v *g, const lidar_t *L,
                         double c, double dv, double rl, float need, const __m512d *aimv,
                         double rough_roll, int v1_roll, group_out *out, const int nb)
{
    const __m512d zero = _mm512_setzero_pd(), two = _mm512_set1_pd(2.0), eps = _mm512_set1_pd(1e-9);
    const __m512d rr = _mm512_set1_pd(rough_roll), dev = _mm512_set1_pd(dv);
    const __m256i c_rough = _mm256_set1_epi32(ROUGH), c_fw = _mm256_set1_epi32(FAIRWAY);
    const __m256i c_fc = _mm256_set1_epi32(FIRST_CUT), c_sand = _mm256_set1_epi32(SAND);
    __m512d a[NB], l[NB], left[NB], ua[NB], ul[NB];
    __m256i lie[NB];
    __mmask8 stop[NB];
    __mmask8 any = 0;
    for (int b = 0; b < nb; b++) {
        a[b] = _mm512_set1_pd(c);
        l[b] = _mm512_add_pd(dev, aimv[b]);
        stop[b] = 0;
    }
    if (L) {
        /* v2_course.lidar_flight_ev_curve: the descent through the crowns, step by step (the steps are the same for
         * every aim of a swing; the lateral position, the ground drop and the crowns are per aim) */
        const __m512d dmin = _mm512_set1_pd(L->dmin), tmax = _mm512_set1_pd(L->tmax);
        const __m512d gl0 = _mm512_set1_pd(L->gl0), inv_c = _mm512_set1_pd(L->inv_c), glmax = _mm512_set1_pd((double)(L->ngl - 1));
        const __m512d dl0 = _mm512_set1_pd(L->dl0), inv_d = _mm512_set1_pd(L->inv_d), dlmax = _mm512_set1_pd((double)(L->ndl - 1));
        const __m256 needv = _mm256_set1_ps(need);
        __m512d d_land[NB], ha[NB], hl[NB];
        __m256 acc[NB];
        __mmask8 live = 0;
        for (int b = 0; b < nb; b++) {
            if (L->has_drop) {
                __m512d r = _mm512_roundscale_pd(_mm512_mul_pd(_mm512_sub_pd(l[b], dl0), inv_d), _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
                r = _mm512_min_pd(_mm512_max_pd(r, zero), dlmax);
                __m256i ix = _mm256_add_epi32(_mm512_cvttpd_epi32(r), _mm256_set1_epi32(cell(c, L->da0, L->inv_d, L->nda) * L->ndl));
                d_land[b] = _mm512_i32gather_pd(ix, L->dg, 8);
            } else {
                d_land[b] = zero;
            }
            acc[b] = _mm256_setzero_ps();
            ha[b] = hl[b] = zero;
        }
        for (int k = 0; k < L->nf; k++) {
            double f = L->F[k], pa = c * f;
            if (!(pa >= L->min_along)) continue;
            const __m512d fv = _mm512_set1_pd(f), yf = _mm512_set1_pd(L->y[k]);
            const __m256 seg = _mm256_set1_ps((float)(c * L->stepf * L->seg[k]));
            const int ca = cell(pa, L->ga0, L->inv_c, L->nga) * L->ngl;
            const int da = L->has_drop ? cell(pa, L->da0, L->inv_d, L->nda) * L->ndl : 0;
            live = 0;
            for (int b = 0; b < nb; b++) {
                __m512d t = _mm512_sub_pd(yf, _mm512_mul_pd(fv, d_land[b]));
                __mmask8 m1 = _mm512_cmp_pd_mask(_mm512_add_pd(t, dmin), tmax, _CMP_LT_OQ) & (__mmask8)~stop[b];
                live |= (__mmask8)~stop[b];
                if (!m1) continue;
                __m512d pl = _mm512_mul_pd(l[b], fv);
                __m512d clear = t;
                if (L->has_drop) {
                    __m512d r = _mm512_roundscale_pd(_mm512_mul_pd(_mm512_sub_pd(pl, dl0), inv_d), _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
                    r = _mm512_min_pd(_mm512_max_pd(r, zero), dlmax);
                    clear = _mm512_add_pd(t, _mm512_i32gather_pd(_mm256_add_epi32(_mm512_cvttpd_epi32(r), _mm256_set1_epi32(da)), L->dg, 8));
                } else {
                    clear = _mm512_add_pd(t, zero);
                }
                __m512d r = _mm512_roundscale_pd(_mm512_mul_pd(_mm512_sub_pd(pl, gl0), inv_c), _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
                r = _mm512_min_pd(_mm512_max_pd(r, zero), glmax);
                __m256i ci = _mm256_add_epi32(_mm512_cvttpd_epi32(r), _mm256_set1_epi32(ca));
                __m512d top = _mm512_cvtps_pd(_mm256_i32gather_ps(L->top, ci, 4));
                __m512d base = _mm512_cvtps_pd(_mm256_i32gather_ps(L->base, ci, 4));
                __mmask8 ins = m1 & _mm512_cmp_pd_mask(clear, top, _CMP_LT_OQ) & _mm512_cmp_pd_mask(clear, base, _CMP_GT_OQ);
                if (!ins) continue;
                acc[b] = _mm256_mask_add_ps(acc[b], ins, acc[b], seg);
                __mmask8 st = ins & _mm256_cmp_ps_mask(acc[b], needv, _CMP_GE_OQ);
                ha[b] = _mm512_mask_mov_pd(ha[b], st, _mm512_set1_pd(pa));
                hl[b] = _mm512_mask_mov_pd(hl[b], st, pl);
                stop[b] |= st;
            }
            if (!live) break;
        }
        for (int b = 0; b < nb; b++) {
            a[b] = _mm512_mask_mov_pd(a[b], stop[b], ha[b]);
            l[b] = _mm512_mask_mov_pd(l[b], stop[b], hl[b]);
        }
    }
    for (int b = 0; b < nb; b++) {
        lie[b] = lie_v(lie_pad, cell_v(g, a[b], l[b]));
        left[b] = _mm512_set1_pd(rl);
        left[b] = _mm512_mask_mul_pd(left[b], _mm256_cmpeq_epi32_mask(lie[b], c_rough), left[b], rr);
        left[b] = _mm512_mask_mov_pd(left[b], _mm256_cmpge_epi32_mask(lie[b], c_sand) | stop[b], zero);  /* HAZ: codes >= 3 */
        any |= _mm512_cmp_pd_mask(left[b], eps, _CMP_GT_OQ);
    }
    if (any) {
        for (int b = 0; b < nb; b++) {
            __m512d den = _mm512_max_pd(hypot_v(a[b], l[b]), eps);
            ua[b] = _mm512_div_pd(a[b], den);
            ul[b] = _mm512_div_pd(l[b], den);
        }
        for (;;) {
            __mmask8 mv[NB];
            any = 0;
            for (int b = 0; b < nb; b++) { mv[b] = _mm512_cmp_pd_mask(left[b], eps, _CMP_GT_OQ); any |= mv[b]; }
            if (!any) break;
            for (int b = 0; b < nb; b++) {
                if (!mv[b]) continue;
                __m512d st = _mm512_min_pd(left[b], two);
                a[b] = _mm512_mask_add_pd(a[b], mv[b], a[b], _mm512_mul_pd(ua[b], st));
                l[b] = _mm512_mask_add_pd(l[b], mv[b], l[b], _mm512_mul_pd(ul[b], st));
                left[b] = _mm512_mask_sub_pd(left[b], mv[b], left[b], st);
                __m256i nw = lie_v(lie_pad, cell_v(g, a[b], l[b]));
                __mmask8 was_fw = _mm256_cmpeq_epi32_mask(lie[b], c_fw);
                if (!v1_roll) was_fw |= _mm256_cmpeq_epi32_mask(lie[b], c_fc);
                __mmask8 into = mv[b] & was_fw & _mm256_cmpeq_epi32_mask(nw, c_rough);
                left[b] = _mm512_mask_mul_pd(left[b], into, left[b], rr);
                left[b] = _mm512_mask_mov_pd(left[b], mv[b] & _mm256_cmpge_epi32_mask(nw, c_sand), zero);
                lie[b] = _mm256_mask_mov_epi32(lie[b], mv[b], nw);
            }
        }
    }
    for (int b = 0; b < nb; b++)
        out->s[b] = _mm512_i32gather_pd(cell_v(g, a[b], l[b]), S, 8);
}

static void ev_simd(const int8_t *lie_pad, const double *S, int na, int nl, double a0, double l0, double inv,
                    const double *car, const double *dev, const double *roll, int n,
                    const double *aims, int m, double rough_roll, int v1_roll, int ksplit, const lidar_t *L,
                    double *sum_all, double *vA, double *vB, double *v_all, int nthreads, int bs, double *blk)
{
    int nblk = (bs > 0 && blk) ? (n + bs - 1) / bs : 0;
    grid_v g;
    g.a0 = _mm512_set1_pd(a0); g.l0 = _mm512_set1_pd(l0); g.inv = _mm512_set1_pd(inv);
    g.amax = _mm512_set1_pd((double)(na - 1)); g.lmax = _mm512_set1_pd((double)(nl - 1)); g.nl = _mm512_set1_pd((double)nl);
    const int W = 8 * NB;
    int nch = (m + W - 1) / W;
    #pragma omp parallel for schedule(dynamic, 1) num_threads(nthreads) if (nthreads > 1 && nch > 1)
    for (int ch = 0; ch < nch; ch++) {
        double ab[8 * NB];
        for (int k = 0; k < W; k++) ab[k] = aims[ch * W + k < m ? ch * W + k : m - 1];     /* pad with the last aim */
        __m512d aimv[NB], sS[NB], sV[NB], sA[NB], sB[NB];
        const __m512d one = _mm512_set1_pd(1.0);
        for (int b = 0; b < NB; b++) {
            aimv[b] = _mm512_loadu_pd(ab + 8 * b);
            sS[b] = sV[b] = sA[b] = sB[b] = _mm512_setzero_pd();
        }
        __m512d sK[NB];
        for (int b = 0; b < NB; b++) sK[b] = _mm512_setzero_pd();
        group_out o;
        for (int i = 0; i < n; i++) {
            group(lie_pad, S, &g, L, car[i], dev[i], roll[i], L ? L->need[i] : 0.0f, aimv, rough_roll, v1_roll, &o, NB);
            if (nblk) {                           /* per-block sums (blocks of bs swings) for the adaptive solver */
                for (int b = 0; b < NB; b++) sK[b] = _mm512_add_pd(sK[b], o.s[b]);
                if ((i + 1) % bs == 0 || i == n - 1) {
                    double kb[8 * NB];
                    for (int b = 0; b < NB; b++) { _mm512_storeu_pd(kb + 8 * b, sK[b]); sK[b] = _mm512_setzero_pd(); }
                    for (int k = 0; k < W && ch * W + k < m; k++) blk[(size_t)(ch * W + k) * nblk + i / bs] = kb[k];
                }
            }
            for (int b = 0; b < NB; b++) {
                __m512d v = _mm512_add_pd(one, o.s[b]);
                sS[b] = _mm512_add_pd(sS[b], o.s[b]);
                sV[b] = _mm512_add_pd(sV[b], v);
                if (i < ksplit) sA[b] = _mm512_add_pd(sA[b], v); else sB[b] = _mm512_add_pd(sB[b], v);
            }
        }
        double buf[4][8 * NB];
        for (int b = 0; b < NB; b++) {
            _mm512_storeu_pd(buf[0] + 8 * b, sS[b]); _mm512_storeu_pd(buf[1] + 8 * b, sA[b]);
            _mm512_storeu_pd(buf[2] + 8 * b, sB[b]); _mm512_storeu_pd(buf[3] + 8 * b, sV[b]);
        }
        for (int k = 0; k < W && ch * W + k < m; k++) {
            sum_all[ch * W + k] = buf[0][k]; vA[ch * W + k] = buf[1][k];
            vB[ch * W + k] = buf[2][k]; v_all[ch * W + k] = buf[3][k];
        }
    }
}

/* 1 when the written-out hypot equals libm's on a sample of the engine's range (then it is used) */
int fs_selfcheck(void)
{
    uint64_t s = 88172645463325252ULL;
    int ok = 1;
    for (long i = 0; i < 400000 && ok; i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        double x = (double)(s >> 11) / 9007199254740992.0 * 520.0 - 20.0;
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        double y = ((double)(s >> 11) / 9007199254740992.0 - 0.5) * 500.0;
        double ax = fabs(x), ay = fabs(y);
        if (ax < ay) { double t = ax; ax = ay; ay = t; }
        if (ay <= ax * 0x1p-40 || ay <= 1e-100) continue;
        if (hypot(x, y) != hypot_kernel(ax, ay)) ok = 0;
    }
    g_hypot_inline = ok;
    return ok;
}
int fs_simd(void) { return 1; }
#else
int fs_selfcheck(void) { return 0; }
int fs_simd(void) { return 0; }
#endif

/* EV curve of one club: n swings x m aims. Per aim j, in swing order (numpy's mean(axis=0) order):
 *   sum_all[j] = sum of S over the swings                     (model.ev_curve: 1 + mean)
 *   v_all[j]   = sum of (1.0 + S); vA[j] over swings [0, ksplit), vB[j] over [ksplit, n)
 *                (decide.bayes: v = 1.0 + sv; v.mean(0), v[:k].mean(0), v[k:].mean(0))
 * oa/ol/olie/os (n x m, C order) are filled when not NULL. lie_pad: the lie raster again with 3 readable bytes
 * after it (32-bit gathers), or NULL (scalar path). */
void fs_ev(const int8_t *lie_g, const double *S, int na, int nl, double a0, double l0, double inv,
           const double *car, const double *dev, const double *roll, int n,
           const double *aims, int m, double rough_roll, int v1_roll, int ksplit,
           const lidar_t *L,
           double *sum_all, double *vA, double *vB, double *v_all,
           double *oa, double *ol, int8_t *olie, double *os, int nthreads, const int8_t *lie_pad, int bs, double *blk)
{
    if (nthreads < 1) nthreads = 1;
    int nblk = (bs > 0 && blk) ? (n + bs - 1) / bs : 0;
#ifdef FS_SIMD
    if (lie_pad != NULL && !oa && m >= 8) {
        ev_simd(lie_pad, S, na, nl, a0, l0, inv, car, dev, roll, n, aims, m, rough_roll, v1_roll, ksplit, L,
                sum_all, vA, vB, v_all, nthreads, bs, blk);
        return;
    }
#else
    (void)lie_pad;
#endif
    #pragma omp parallel for schedule(dynamic, 2) num_threads(nthreads) if (nthreads > 1 && m > 1)
    for (int j = 0; j < m; j++) {
        double aim = aims[j];
        double sa = 0.0, sb = 0.0, st_all = 0.0, v_tot = 0.0, sk = 0.0;
        int i = 0;
        for (; i < n; i++) {
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
            if (nblk) {
                sk += s;
                if ((i + 1) % bs == 0 || i == n - 1) { blk[(size_t)j * nblk + i / bs] = sk; sk = 0.0; }
            }
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
typedef struct { double *vx, *vy; int *cnt, *edges; int nv, nb; double ymin, ymax, xmin, xmax, h; } poly_t;

static int poly_build(poly_t *p, const double *poly, int nv, double dx, double dy)
{
    p->nv = nv; p->nb = 512;
    p->vx = (double *)malloc(sizeof(double) * nv); p->vy = (double *)malloc(sizeof(double) * nv);
    p->ymin = INFINITY; p->ymax = -INFINITY; p->xmin = INFINITY; p->xmax = -INFINITY;
    for (int k = 0; k < nv; k++) {
        p->vx[k] = poly[2 * k] + dx; p->vy[k] = poly[2 * k + 1] + dy;
        if (p->vy[k] < p->ymin) p->ymin = p->vy[k];
        if (p->vy[k] > p->ymax) p->ymax = p->vy[k];
        if (p->vx[k] < p->xmin) p->xmin = p->vx[k];
        if (p->vx[k] > p->xmax) p->xmax = p->vx[k];
    }
    /* edges bucketed by y so a point only meets the edges that can straddle its ray */
    int nb = p->nb;
    p->h = (p->ymax - p->ymin) / nb;
    p->cnt = (int *)calloc(nb + 1, sizeof(int));
    p->edges = NULL;
    if (!(p->h > 0)) return 0;
    for (int pass = 0; pass < 2; pass++) {
        int *pos = NULL;
        if (pass == 1) {
            for (int b = 0; b < nb; b++) p->cnt[b + 1] += p->cnt[b];
            p->edges = (int *)malloc(sizeof(int) * (p->cnt[nb] > 0 ? p->cnt[nb] : 1));
            pos = (int *)malloc(sizeof(int) * nb);
            memcpy(pos, p->cnt, sizeof(int) * nb);
        }
        for (int k = 0; k < nv; k++) {
            int k0 = k == 0 ? nv - 1 : k - 1;
            double lo = p->vy[k0] < p->vy[k] ? p->vy[k0] : p->vy[k], hi = p->vy[k0] < p->vy[k] ? p->vy[k] : p->vy[k0];
            int b0 = (int)floor((lo - p->ymin) / p->h) - 1, b1 = (int)floor((hi - p->ymin) / p->h) + 1;
            if (b0 < 0) b0 = 0;
            if (b1 > nb - 1) b1 = nb - 1;
            for (int b = b0; b <= b1; b++) { if (pass == 0) p->cnt[b + 1]++; else p->edges[pos[b]++] = k; }
        }
        free(pos);
    }
    return 1;
}

static void poly_free(poly_t *p) { free(p->vx); free(p->vy); free(p->cnt); free(p->edges); }

/* matplotlib's point_in_path_impl for one point */
static inline int pip(const poly_t *p, double tx, double ty)
{
    if (!(ty > p->ymin && ty <= p->ymax)) return 0;
    if (tx > p->xmax + 1.0 || tx < p->xmin - 1.0) return 0;
    int b = (int)floor((ty - p->ymin) / p->h);
    if (b < 0) b = 0;
    if (b > p->nb - 1) b = p->nb - 1;
    int in = 0;
    for (int e = p->cnt[b]; e < p->cnt[b + 1]; e++) {
        int k = p->edges[e];
        int k0 = k == 0 ? p->nv - 1 : k - 1;
        double vtx0 = p->vx[k0], vty0 = p->vy[k0], vtx1 = p->vx[k], vty1 = p->vy[k];
        int yflag0 = (vty0 >= ty), yflag1 = (vty1 >= ty);
        if (yflag0 != yflag1) {
            if ((((vty1 - ty) * (vtx0 - vtx1)) >= ((vtx1 - tx) * (vty0 - vty1))) == yflag1) in ^= 1;
        }
    }
    return in;
}

static void fill_impl(const double *pts, long npts, const double *poly, int nv, double dx, double dy, int8_t code,
                      int8_t *lie, int nthreads, int nl, int ia0, int ia1, int il0, int il1);

void fs_fill(const double *pts, long npts, const double *poly, int nv, double dx, double dy, int8_t code,
             int8_t *lie, int nthreads)
{
    fill_impl(pts, npts, poly, nv, dx, dy, code, lie, nthreads, 0, 0, 0, 0, 0);
}

/* The same fill, only visiting the grid rows / columns [ia0, ia1] x [il0, il1] (the caller's index rectangle that
 * contains the polygon's bounding box with a margin: outside the bounding box a point is outside the polygon). */
void fs_fill_rect(const double *pts, int na, int nl, const double *poly, int nv, double dx, double dy, int8_t code,
                  int8_t *lie, int ia0, int ia1, int il0, int il1)
{
    if (ia1 < ia0 || il1 < il0) return;
    fill_impl(pts, (long)na * nl, poly, nv, dx, dy, code, lie, 1, nl, ia0, ia1, il0, il1);
}

static void fill_impl(const double *pts, long npts, const double *poly, int nv, double dx, double dy, int8_t code,
                      int8_t *lie, int nthreads, int nl, int ia0, int ia1, int il0, int il1)
{
    if (nv < 2) return;
    poly_t p;
    if (!poly_build(&p, poly, nv, dx, dy)) { poly_free(&p); return; }
    if (nthreads < 1) nthreads = 1;
    long ntot = nl ? (long)(ia1 - ia0 + 1) * (il1 - il0 + 1) : npts;
    int wl = nl ? il1 - il0 + 1 : 1;
    #pragma omp parallel for schedule(static) num_threads(nthreads) if (nthreads > 1)
    for (long q = 0; q < ntot; q++) {
        long i = nl ? (long)(ia0 + q / wl) * nl + il0 + q % wl : q;
        if (pip(&p, pts[2 * i], pts[2 * i + 1])) lie[i] = code;
    }
    poly_free(&p);
}

/* Prior-draw maps: each draw shifts a zone polygon by a few px. Once per hole, for the UNSHIFTED polygon and every
 * cell of its index rectangle: inside or not (base) and the distance from the cell centre to the polygon's outline
 * (dist, px). In a draw a cell further from the outline than the shift (+ a margin) is on the same side of the
 * shifted polygon as of the unshifted one, so only the band along the outline is tested again (fs_fill_band). */
void fs_fill_prep(const double *pts, int nl, const double *poly, int nv, int ia0, int ia1, int il0, int il1,
                  float *dist, uint8_t *base)
{
    poly_t p;
    int ok = nv >= 2 && poly_build(&p, poly, nv, 0.0, 0.0);
    int wl = il1 - il0 + 1;
    for (int ia = ia0; ia <= ia1; ia++)
        for (int il = il0; il <= il1; il++) {
            size_t o = (size_t)(ia - ia0) * wl + (il - il0);
            double tx = pts[2 * ((size_t)ia * nl + il)], ty = pts[2 * ((size_t)ia * nl + il) + 1];
            base[o] = ok ? (uint8_t)pip(&p, tx, ty) : 0;
            double best = INFINITY;
            for (int k = 0; k < nv; k++) {
                int k0 = k == 0 ? nv - 1 : k - 1;
                double ex = poly[2 * k] - poly[2 * k0], ey = poly[2 * k + 1] - poly[2 * k0 + 1];
                double px = tx - poly[2 * k0], py = ty - poly[2 * k0 + 1];
                double l2 = ex * ex + ey * ey, t = l2 > 0 ? (px * ex + py * ey) / l2 : 0.0;
                t = t < 0 ? 0 : (t > 1 ? 1 : t);
                double qx = px - t * ex, qy = py - t * ey, d2 = qx * qx + qy * qy;
                if (d2 < best) best = d2;
            }
            dist[o] = (float)(sqrt(best) * 0.999);       /* rounded down */
        }
    if (nv >= 2) poly_free(&p);
}

void fs_fill_band(const double *pts, int nl, const double *poly, int nv, double dx, double dy, int8_t code, int8_t *lie,
                  int ia0, int ia1, int il0, int il1, const float *dist, const uint8_t *base, double thr)
{
    if (nv < 2) return;
    poly_t p;
    if (!poly_build(&p, poly, nv, dx, dy)) { poly_free(&p); return; }
    int wl = il1 - il0 + 1;
    float th = (float)thr;
    for (int ia = ia0; ia <= ia1; ia++) {
        const float *dr = dist + (size_t)(ia - ia0) * wl;
        const uint8_t *br = base + (size_t)(ia - ia0) * wl;
        int8_t *lr = lie + (size_t)ia * nl + il0;
        const double *pr = pts + 2 * ((size_t)ia * nl + il0);
        for (int k = 0; k < wl; k++) {
            int in = dr[k] > th ? br[k] : pip(&p, pr[2 * k], pr[2 * k + 1]);
            if (in) lr[k] = code;
        }
    }
    poly_free(&p);
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

/* ------------------------------------------------------------------------------------------------ strokes raster
 * model.Raster.strokes (+ v2_course.install_green_putting's wrapper), cell by cell, the same expressions in the same
 * order. interp() is numpy's np.interp (compiled_base.c arr_interp): slope = (fp[j+1] - fp[j]) / (xp[j+1] - xp[j]),
 * value = slope * (x - xp[j]) + fp[j], fp[j] when x == xp[j], end values outside. */
typedef struct {
    int nd;
    const double *DIST, *T_fw, *T_ro, *T_sa, *T_rec;
    double long_slope;
    int am, broadie, v1;
    double am_off, am_slope, m_rough, m_sand;
    double first_cut, trees, one_m_trees, tree_restricted, punch_adv, punch_fail;
    double lost_edge, lost_deep, lost_ramp, block_sev, sd, unverified;
    int green_putting, nputt;
    const double *PUTT_FT, *PUTT_TOUR;
    double SY[3], SF[3], SR[3], SS[3];
    double gap_r, gap_s, mult_r, mult_s, mult_fc, putt_off;
} strokes_t;

static inline double interp(double x, const double *xp, const double *fp, const double *sl, int n)
{
    if (x != x) return x;
    if (x > xp[n - 1]) return fp[n - 1];
    if (x < xp[0]) return fp[0];
    int lo = 0, hi = n - 1;                 /* xp[lo] <= x <= xp[hi] */
    while (hi - lo > 1) {
        int mid = (lo + hi) >> 1;
        if (x >= xp[mid]) lo = mid; else hi = mid;
    }
    if (x >= xp[hi]) lo = hi;               /* x == xp[n - 1] */
    if (lo == n - 1) return fp[lo];
    if (xp[lo] == x) return fp[lo];
    return sl[lo] * (x - xp[lo]) + fp[lo];
}

static inline double clip(double x, double lo, double hi)
{
    double r = x > lo ? x : lo;             /* np.clip = minimum(maximum(x, lo), hi) */
    return r < hi ? r : hi;
}

typedef struct { const strokes_t *p; const double *s_fw, *s_ro, *s_sa, *s_rec; } sctx;

static inline double tour(const sctx *c, const double *T, const double *sl, double d)
{
    const strokes_t *p = c->p;
    double b = d - p->DIST[p->nd - 1];
    double beyond = (b > 0.0 ? b : 0.0) * p->long_slope;
    return interp(clip(d, p->DIST[0], p->DIST[p->nd - 1]), p->DIST, T, sl, p->nd) + beyond;
}

/* table("fairway" / "rough" / "sand", d, P) for one d */
static inline void tables(const sctx *c, double d, int want_sand, double *fw_t, double *ro_t, double *sa_t, double *fw_tour)
{
    const strokes_t *p = c->p;
    double fw = tour(c, p->T_fw, c->s_fw, d);
    double tro = tour(c, p->T_ro, c->s_ro, d);
    double tsa = want_sand ? tour(c, p->T_sa, c->s_sa, d) : 0.0;
    *fw_tour = fw;
    if (!p->am) { *fw_t = fw; *ro_t = tro; *sa_t = tsa; return; }
    double off = p->am_off + p->am_slope * (clip(d, 20.0, 450.0) - 150.0);
    *fw_t = fw + off;
    *ro_t = fw + off + p->m_rough * (tro - fw);
    *sa_t = want_sand ? fw + off + p->m_sand * (tsa - fw) : 0.0;
}

void fs_strokes(const strokes_t *p, const int8_t *lie, const double *dist, const double *native_depth,
                const double *entry, const uint8_t *blocked, const uint8_t *green, long ncell, double *S, int nthreads)
{
    int nd = p->nd;
    double *sl = (double *)malloc(sizeof(double) * 4 * nd);
    double *slp = (double *)malloc(sizeof(double) * (p->nputt > 0 ? p->nputt : 1));
    const double *Ts[4] = {p->T_fw, p->T_ro, p->T_sa, p->T_rec};
    for (int t = 0; t < 4; t++)
        for (int i = 0; i + 1 < nd; i++) sl[t * nd + i] = (Ts[t][i + 1] - Ts[t][i]) / (p->DIST[i + 1] - p->DIST[i]);
    for (int i = 0; i + 1 < p->nputt; i++) slp[i] = (p->PUTT_TOUR[i + 1] - p->PUTT_TOUR[i]) / (p->PUTT_FT[i + 1] - p->PUTT_FT[i]);
    double sF[2], sR[2], sS[2];
    for (int i = 0; i < 2; i++) {
        sF[i] = (p->SF[i + 1] - p->SF[i]) / (p->SY[i + 1] - p->SY[i]);
        sR[i] = (p->SR[i + 1] - p->SR[i]) / (p->SY[i + 1] - p->SY[i]);
        sS[i] = (p->SS[i + 1] - p->SS[i]) / (p->SY[i + 1] - p->SY[i]);
    }
    sctx c = {p, sl, sl + nd, sl + 2 * nd, sl + 3 * nd};
    if (nthreads < 1) nthreads = 1;
    #pragma omp parallel for schedule(static) num_threads(nthreads) if (nthreads > 1)
    for (long i = 0; i < ncell; i++) {
        double d = dist[i];
        int li = lie[i];
        double fw, ro, sa, fwt;
        tables(&c, d, li == SAND, &fw, &ro, &sa, &fwt);
        double rec = 0.0;
        int need_rec = (li == RECOVERY || li == NATIVE || li == UNVERIFIED || (p->block_sev > 0 && blocked[i]));
        if (need_rec) {
            if (p->broadie) {
                rec = tour(&c, p->T_rec, c.s_rec, d);
                if (p->am) rec = fw + 1.3 * (rec - fwt);
            } else {
                double d2 = d - p->punch_adv;
                d2 = d2 > 20.0 ? d2 : 20.0;
                double f2, r2, s2, t2;
                tables(&c, d2, 0, &f2, &r2, &s2, &t2);
                rec = 1.0 + 0.5 * (f2 + r2) + p->punch_fail;
            }
        }
        double sd_cost = p->v1 ? 2.0 + ro : p->sd;
        double s;
        switch (li) {
        case FAIRWAY: s = fw; break;
        case FIRST_CUT: s = fw + p->first_cut * (ro - fw); break;
        case SAND: s = sa; break;
        case RECOVERY:
            s = p->v1 ? p->trees * rec + p->one_m_trees * ro : p->trees * rec + p->one_m_trees * (ro + p->tree_restricted);
            break;
        case NATIVE: {
            double pl = p->v1 ? p->lost_deep
                              : p->lost_edge + (p->lost_deep - p->lost_edge) * clip(native_depth[i] / p->lost_ramp, 0.0, 1.0);
            s = pl * sd_cost + (1 - pl) * rec;
            break;
        }
        case WATER: {
            double f2, r2, s2, t2;
            tables(&c, p->v1 ? d : entry[i], 0, &f2, &r2, &s2, &t2);
            s = 1.0 + r2;
            break;
        }
        case OB: s = sd_cost; break;
        case UNVERIFIED:
            s = (1 - p->unverified) * ro + p->unverified * (p->trees * rec + p->one_m_trees * (ro + p->tree_restricted));
            break;
        default: s = ro;
        }
        if (p->block_sev > 0 && blocked[i]) {
            double m = rec - s;
            s = s + p->block_sev * (m > 0.0 ? m : 0.0);
        }
        if (p->green_putting) {
            if (d < p->SY[2] && (li == FAIRWAY || li == FIRST_CUT || li == ROUGH || li == SAND)) {
                double iF = interp(d, p->SY, p->SF, sF, 3);
                double delta = iF - p->SF[2];
                if (li == SAND) delta = delta + p->mult_s * (interp(d, p->SY, p->SS, sS, 3) - iF - p->gap_s);
                else if (li == ROUGH) delta = delta + p->mult_r * (interp(d, p->SY, p->SR, sR, 3) - iF - p->gap_r);
                else if (li == FIRST_CUT) delta = delta + p->mult_fc * (interp(d, p->SY, p->SR, sR, 3) - iF - p->gap_r);
                s = s + delta;
            }
            if (green && green[i] && (li == FAIRWAY || li == FIRST_CUT || li == ROUGH))
                s = interp(d * 3.0, p->PUTT_FT, p->PUTT_TOUR, slp, p->nputt) + p->putt_off;
        }
        S[i] = s;
    }
    free(sl); free(slp);
}

/* ------------------------------------------------------------------------------------------------ adaptive grid
 * One call per (hole, tee offset, temperature): every wind cell and club, no Python in between.
 * Per cell: (1) every club's EV on a coarse aim grid from n_coarse swings finds its basin(s); (2) the 0.5-yd aims of
 * that window are evaluated on n0 swings, kept as sums per block of `bs` swings; (3) racing: the paired block
 * differences (common swings) against the leader give each club's gap and its standard error; a club worse than the
 * leader by more than tq x SE is dropped; (4) the cell stops when the runner-up is separated at 99 % and the
 * leader's aim (block jackknife) is within aim_tol yds at 99 %, else the swings of the clubs still alive are doubled,
 * up to cap. Swings: whatever z holds (scrambled Sobol from Python), the same for every club and cell.
 * The per-ball arithmetic is the kernel above (group / roll_out); the aim is the minimum of the 1-yd Gaussian-smoothed
 * curve (parabola through the three lowest points, reported to 0.5 yd), the zone its 0.005-stroke window. */
typedef struct {
    double rho, kappa, skew, mis_slight, ms_lo, ms_hi, ms_lat, mis_heavy, mh_lo, mh_hi, mh_lat, bias, roll_noise;
    double rough_roll;
    int v1_roll;
} shot_t;

typedef struct {
    int n_coarse, n0, cap, bs, cstep, half;
    double window, aim_tol, delta, drop_t;
    int min_all;            /* every club gets at least this many swings on its window */
} adapt_t;

typedef struct {
    const int8_t *lie_g, *lie_pad; const double *S; int na, nl; double a0, l0, inv;
    double rough_roll; int v1_roll;
#ifdef FS_SIMD
    grid_v g;
#endif
} gctx;

/* strokes after the tee shot for one swing at `cnt` aims (cnt <= 32) */
static inline void vals(const gctx *x, double c, double dv, double rl, const double *aims, int cnt, double *out)
{
#ifdef FS_SIMD
    if (x->lie_pad) {
        double ab[32];
        int nb = (cnt + 7) / 8;
        for (int k = 0; k < 8 * nb; k++) ab[k] = aims[k < cnt ? k : cnt - 1];
        __m512d aimv[NB];
        for (int b = 0; b < nb; b++) aimv[b] = _mm512_loadu_pd(ab + 8 * b);
        group_out o;
        group(x->lie_pad, x->S, &x->g, NULL, c, dv, rl, 0.0f, aimv, x->rough_roll, x->v1_roll, &o, nb);
        double buf[32];
        for (int b = 0; b < nb; b++) _mm512_storeu_pd(buf + 8 * b, o.s[b]);
        for (int k = 0; k < cnt; k++) out[k] = buf[k];
        return;
    }
#endif
    for (int k = 0; k < cnt; k++) {
        double a, l; int lie;
        roll_out(x->lie_g, x->na, x->nl, x->a0, x->l0, x->inv, c, dv + aims[k], rl, x->rough_roll, x->v1_roll, &a, &l, &lie);
        out[k] = x->S[(size_t)cell(a, x->a0, x->inv, x->na) * x->nl + cell(l, x->l0, x->inv, x->nl)];
    }
}

static double tq995(int df)
{
    static const int d[] = {1, 2, 3, 4, 5, 6, 7, 9, 11, 15, 23, 31, 47, 63, 127, 255, 1000000};
    static const double t[] = {63.66, 9.925, 5.841, 4.604, 4.032, 3.707, 3.499, 3.250, 3.106, 2.947, 2.807, 2.744, 2.685, 2.656, 2.615, 2.595, 2.576};
    for (int i = 0; i < 17; i++) if (df <= d[i]) return t[i];
    return 2.576;
}

/* smoothed-curve minimum on a window: cur[0..w) at aims aim_w0 + k * step. Returns the grid index of the minimum
 * inside [klo, khi] and fills sm; *xmin = continuous aim (parabola), */
static int smooth_min(const double *cur, int w, int klo, int khi, const double *gw, double *sm, double *xfrac)
{
    int best = -1;
    for (int k = 0; k < w; k++) {
        double v = 0.0;
        for (int j = -8; j <= 8; j++) {
            int q = k + j;
            if (q < 0) q = 0;
            if (q > w - 1) q = w - 1;
            v += gw[j + 8] * cur[q];
        }
        sm[k] = v;
        if (k >= klo && k <= khi && (best < 0 || v < sm[best])) best = k;
    }
    *xfrac = 0.0;
    if (best > klo && best < khi && best > 0 && best < w - 1) {
        double y0 = sm[best - 1], y1 = sm[best], y2 = sm[best + 1], den = y0 - 2.0 * y1 + y2;
        if (den > 1e-15) {
            double f = 0.5 * (y0 - y2) / den;
            *xfrac = f < -0.5 ? -0.5 : (f > 0.5 ? 0.5 : f);
        }
    }
    return best;
}

void fs_grid(const int8_t *lie_g, const int8_t *lie_pad, const double *S, int na, int nl, double a0, double l0, double inv,
             const double *z, int zcap, int ncell, int nclub, const double *par, const double *lim, const int *hyp,
             const shot_t *sp, double aim0, double step, int naims, const adapt_t *op,
             double *out_club, double *out_cell, long long *balls_out, int nthreads)
{
    gctx x;
    x.lie_g = lie_g; x.lie_pad = lie_pad; x.S = S; x.na = na; x.nl = nl; x.a0 = a0; x.l0 = l0; x.inv = inv;
    x.rough_roll = sp->rough_roll; x.v1_roll = sp->v1_roll;
#ifdef FS_SIMD
    x.g.a0 = _mm512_set1_pd(a0); x.g.l0 = _mm512_set1_pd(l0); x.g.inv = _mm512_set1_pd(inv);
    x.g.amax = _mm512_set1_pd((double)(na - 1)); x.g.lmax = _mm512_set1_pd((double)(nl - 1)); x.g.nl = _mm512_set1_pd((double)nl);
#endif
    const int bs = op->bs, cap = op->cap < zcap ? op->cap : zcap, nbmax = cap / bs;
    double gw[17], gs = 0.0, sd = 1.0 / step;
    for (int j = -8; j <= 8; j++) { gw[j + 8] = exp(-0.5 * (j / sd) * (j / sd)); gs += gw[j + 8]; }
    for (int j = 0; j < 17; j++) gw[j] /= gs;
    const double *zl = z, *zc = z + zcap, *um = z + 2 * (size_t)zcap, *uf = z + 3 * (size_t)zcap, *ur = z + 4 * (size_t)zcap;
    const double rq = sqrt(1.0 - sp->rho * sp->rho), k0 = sqrt(2.0 / M_PI);
    long long balls = 0;
    if (nthreads < 1) nthreads = 1;
    #pragma omp parallel num_threads(nthreads) reduction(+:balls) if (nthreads > 1)
    {
        double *car = (double *)malloc(sizeof(double) * 3 * (size_t)cap * nclub);
        double *bsum = (double *)malloc(sizeof(double) * (size_t)nclub * nbmax * naims);
        double *aims = (double *)malloc(sizeof(double) * naims);
        double *cur = (double *)malloc(sizeof(double) * 4 * naims);
        int *w0 = (int *)malloc(sizeof(int) * 6 * nclub);
        double *caim = (double *)malloc(sizeof(double) * 6 * nclub);
        for (int k = 0; k < naims; k++) aims[k] = aim0 + k * step;
        #pragma omp for schedule(dynamic, 1)
        for (int ce = 0; ce < ncell; ce++) {
            int *w1 = w0 + nclub, *nsw = w0 + 2 * nclub, *alive = w0 + 3 * nclub, *kaim = w0 + 4 * nclub, *klo = w0 + 5 * nclub;
            double *cev = caim + nclub, *zlo = caim + 2 * nclub, *zhi = caim + 3 * nclub, *gap = caim + 4 * nclub, *gse = caim + 5 * nclub;
            int khi_[64];
            /* ---- shots of every club (model.shots, per swing) */
            for (int c = 0; c < nclub; c++) {
                const double *p = par + ((size_t)ce * nclub + c) * 5;
                double carry = p[0], roll = p[1], sl = p[2], sc = p[3], drift = p[4];
                double *cc = car + (size_t)c * 3 * cap, *dd = cc + cap, *rr = dd + cap;
                for (int i = 0; i < cap; i++) {
                    double dev = sl * zl[i];
                    double cv = carry + sc * (rq * zc[i] - sp->rho * zl[i]);
                    if (sp->kappa != 0.0) cv = cv - sp->kappa * sl * (fabs(zl[i]) - k0);
                    if (sp->skew != 0.0) {
                        double s_ = sp->skew;
                        int same = (zl[i] > 0) == (s_ > 0) && zl[i] != 0.0;
                        dev = same ? dev * (1 + fabs(s_)) : dev * (1 - fabs(s_) / 2);
                    }
                    int slight = um[i] < sp->mis_slight;
                    int heavy = um[i] >= sp->mis_slight && um[i] < sp->mis_slight + sp->mis_heavy;
                    if (slight) cv = carry * (sp->ms_lo + (sp->ms_hi - sp->ms_lo) * uf[i]);
                    if (heavy) cv = carry * (sp->mh_lo + (sp->mh_hi - sp->mh_lo) * uf[i]);
                    if (slight) dev = dev * sp->ms_lat;
                    if (heavy) dev = dev * sp->mh_lat;
                    dev = dev + sp->bias + drift;
                    double rl = roll * (1 + sp->roll_noise * (2 * ur[i] - 1));
                    cc[i] = cv; dd[i] = dev; rr[i] = rl > 0.0 ? rl : 0.0;
                }
            }
            #define EVAL(c_, i0_, i1_, n0_, n1_) do {                                                       \
                const double *cc_ = car + (size_t)(c_) * 3 * cap, *dd_ = cc_ + cap, *rr_ = dd_ + cap;        \
                double *bb_ = bsum + (size_t)(c_) * nbmax * naims;                                           \
                for (int q_ = (i0_); q_ <= (i1_); q_ += 32) {                                                \
                    int cnt_ = (i1_) - q_ + 1 < 32 ? (i1_) - q_ + 1 : 32;                                    \
                    double acc_[32], v_[32];                                                                 \
                    for (int k_ = 0; k_ < cnt_; k_++) acc_[k_] = 0.0;                                        \
                    for (int i_ = (n0_); i_ < (n1_); i_++) {                                                 \
                        vals(&x, cc_[i_], dd_[i_], rr_[i_], aims + q_, cnt_, v_);                            \
                        for (int k_ = 0; k_ < cnt_; k_++) acc_[k_] += v_[k_];                                \
                        if ((i_ + 1) % bs == 0) {                                                            \
                            for (int k_ = 0; k_ < cnt_; k_++) { bb_[(size_t)(i_ / bs) * naims + q_ + k_] = acc_[k_]; acc_[k_] = 0.0; } \
                        }                                                                                    \
                    }                                                                                        \
                    balls += (long long)cnt_ * ((n1_) - (n0_));                                              \
                }                                                                                            \
            } while (0)
            /* mean curve of club c on its window from the first nb blocks, optionally leaving block `skip` out */
            #define CURVE(c_, nb_, skip_, dst_) do {                                                         \
                const double *bb_ = bsum + (size_t)(c_) * nbmax * naims;                                     \
                int w_ = w1[c_] - w0[c_] + 1, used_ = 0;                                                     \
                for (int k_ = 0; k_ < w_; k_++) (dst_)[k_] = 0.0;                                            \
                for (int b_ = 0; b_ < (nb_); b_++) {                                                         \
                    if (b_ == (skip_)) continue;                                                             \
                    used_++;                                                                                 \
                    for (int k_ = 0; k_ < w_; k_++) (dst_)[k_] += bb_[(size_t)b_ * naims + w0[c_] + k_];     \
                }                                                                                            \
                for (int k_ = 0; k_ < w_; k_++) (dst_)[k_] = 1.0 + (dst_)[k_] / ((double)used_ * bs);        \
            } while (0)
            int n_now = op->n0;
            /* ---- stage 1: basin search on a coarse aim grid */
            for (int c = 0; c < nclub; c++) {
                const double *lm = lim + ((size_t)ce * nclub + c) * 2;
                int kl = (int)ceil((lm[0] - 1e-9 - aim0) / step), kh = (int)floor((lm[1] + 1e-9 - aim0) / step);
                if (kl < 0) kl = 0;
                if (kh > naims - 1) kh = naims - 1;
                klo[c] = kl; khi_[c] = kh;
                const double *cc = car + (size_t)c * 3 * cap, *dd = cc + cap, *rr = dd + cap;
                int nc = 0;
                double ca[512];
                int ci[512];
                for (int k = kl; k <= kh; k += op->cstep) { ci[nc] = k; ca[nc] = aims[k]; nc++; }
                if (ci[nc - 1] != kh) { ci[nc] = kh; ca[nc] = aims[kh]; nc++; }
                double *cs = cur;
                for (int k = 0; k < nc; k++) cs[k] = 0.0;
                for (int q = 0; q < nc; q += 32) {
                    int cnt = nc - q < 32 ? nc - q : 32;
                    double v[32];
                    for (int i = 0; i < op->n_coarse; i++) {
                        vals(&x, cc[i], dd[i], rr[i], ca + q, cnt, v);
                        for (int k = 0; k < cnt; k++) cs[q + k] += v[k];
                    }
                    balls += (long long)cnt * op->n_coarse;
                }
                int bi = 0;
                for (int k = 1; k < nc; k++) if (cs[k] < cs[bi]) bi = k;
                int lo_i = ci[bi], hi_i = ci[bi];
                for (int k = 0; k < nc; k++)            /* other basins that could hold the optimum */
                    if (cs[k] <= cs[bi] + op->delta * op->n_coarse) { if (ci[k] < lo_i) lo_i = ci[k]; if (ci[k] > hi_i) hi_i = ci[k]; }
                w0[c] = lo_i - op->half; w1[c] = hi_i + op->half;
                if (w0[c] < 0) w0[c] = 0;
                if (w1[c] > naims - 1) w1[c] = naims - 1;
                nsw[c] = 0; alive[c] = 1;
            }
            int leader = -1, runner = -1, sep = 0, aim_ok = 0;
            double se_run = 0.0, mar = 0.0;
            for (;;) {
                /* ---- stage 2: the windows of the clubs still alive, up to n_now swings; widen a window when the
                 * minimum or the 0.005 zone comes within the smoothing radius of its edge */
                for (int c = 0; c < nclub; c++) {
                    if (!alive[c]) continue;
                    if (nsw[c] < n_now) { EVAL(c, w0[c], w1[c], nsw[c], n_now); nsw[c] = n_now; }
                    for (int tries = 0; tries < 12; tries++) {
                        int w = w1[c] - w0[c] + 1, nb_ = nsw[c] / bs;
                        double *cu = cur, *sm = cur + naims, xf;
                        CURVE(c, nb_, -1, cu);
                        int kl = klo[c] - w0[c], kh = khi_[c] - w0[c];
                        if (kl < 0) kl = 0;
                        if (kh > w - 1) kh = w - 1;
                        int b = smooth_min(cu, w, kl, kh, gw, sm, &xf);
                        double aim = aims[w0[c] + b] + xf * step;
                        aim = floor(aim / 0.5 + 0.5) * 0.5;
                        if (aim < aims[w0[c] + kl]) aim = aims[w0[c] + kl];
                        if (aim > aims[w0[c] + kh]) aim = aims[w0[c] + kh];
                        int ka = (int)floor((aim - aims[w0[c]]) / step + 0.5);
                        double smb = sm[b] < sm[ka] ? sm[b] : sm[ka];
                        int za = ka, zb = ka;
                        while (za > kl && sm[za - 1] <= smb + op->window) za--;
                        while (zb < kh && sm[zb + 1] <= smb + op->window) zb++;
                        int grow_lo = (za < 9 || b < 9) && w0[c] > 0 && w0[c] > klo[c] - 9;
                        int grow_hi = (zb > w - 10 || b > w - 10) && w1[c] < naims - 1 && w1[c] < khi_[c] + 9;
                        if (!grow_lo && !grow_hi) {
                            kaim[c] = w0[c] + ka; caim[c] = aim; cev[c] = cu[ka];
                            zlo[c] = aims[w0[c] + za]; zhi[c] = aims[w0[c] + zb];
                            break;
                        }
                        if (grow_lo) { int n0_ = w0[c] - op->half < 0 ? 0 : w0[c] - op->half; EVAL(c, n0_, w0[c] - 1, 0, nsw[c]); w0[c] = n0_; }
                        if (grow_hi) { int n1_ = w1[c] + op->half > naims - 1 ? naims - 1 : w1[c] + op->half; EVAL(c, w1[c] + 1, n1_, 0, nsw[c]); w1[c] = n1_; }
                        if (tries == 11) { kaim[c] = w0[c] + ka; caim[c] = aim; cev[c] = cu[ka]; zlo[c] = aims[w0[c] + za]; zhi[c] = aims[w0[c] + zb]; }
                    }
                }
                /* ---- stage 3: racing on paired block differences against the leader */
                leader = -1;
                for (int c = 0; c < nclub; c++) if (!hyp[c] && (leader < 0 || cev[c] < cev[leader])) leader = c;
                runner = -1; sep = 1;
                int nbL = nsw[leader] / bs;
                const double *bL = bsum + (size_t)leader * nbmax * naims;
                for (int c = 0; c < nclub; c++) {
                    if (c == leader || hyp[c]) continue;
                    int nb_ = nsw[c] / bs < nbL ? nsw[c] / bs : nbL;       /* blocks both clubs have */
                    const double *bC = bsum + (size_t)c * nbmax * naims;
                    double m1 = 0.0, m2 = 0.0;
                    for (int b = 0; b < nb_; b++) {
                        double d = (bC[(size_t)b * naims + kaim[c]] - bL[(size_t)b * naims + kaim[leader]]) / bs;
                        m1 += d; m2 += d * d;
                    }
                    m1 /= nb_;
                    double var = (m2 / nb_ - m1 * m1) * nb_ / (nb_ - 1);
                    gap[c] = cev[c] - cev[leader];
                    gse[c] = sqrt((var > 0 ? var : 0.0) / nb_);
                    double t = tq995(nb_ - 1);
                    if (alive[c] && m1 > (t > op->drop_t ? t : op->drop_t) * gse[c] && nsw[c] >= op->min_all) alive[c] = 0;
                    if (runner < 0 || cev[c] < cev[runner]) runner = c;
                }
                mar = cev[runner] - cev[leader];
                se_run = gse[runner];
                {
                    int nb_ = nsw[runner] / bs < nbL ? nsw[runner] / bs : nbL;
                    sep = mar > tq995(nb_ - 1) * se_run;
                }
                /* ---- the leader's aim: block jackknife */
                {
                    int w = w1[leader] - w0[leader] + 1;
                    double *cu = cur + 2 * naims, *sm = cur + 3 * naims, xf, s1 = 0.0, s2 = 0.0;
                    int kl = klo[leader] - w0[leader], kh = khi_[leader] - w0[leader];
                    if (kl < 0) kl = 0;
                    if (kh > w - 1) kh = w - 1;
                    for (int b = 0; b < nbL; b++) {
                        CURVE(leader, nbL, b, cu);
                        int bi = smooth_min(cu, w, kl, kh, gw, sm, &xf);
                        double aj = aims[w0[leader] + bi] + xf * step;
                        s1 += aj; s2 += aj * aj;
                    }
                    double mean = s1 / nbL, v = s2 / nbL - mean * mean;
                    double se_aim = sqrt((v > 0 ? v : 0.0) * (nbL - 1));
                    gse[leader] = se_aim;
                    aim_ok = tq995(nbL - 1) * se_aim <= op->aim_tol;
                }
                if ((sep && aim_ok) || n_now >= cap) break;
                n_now *= 2;
                if (n_now > cap) n_now = cap;
                alive[leader] = 1;
                if (sep) { for (int c = 0; c < nclub; c++) if (c != leader && nsw[c] >= op->min_all) alive[c] = 0; }
                else { for (int c = 0; c < nclub; c++) if (hyp[c]) alive[c] = 0; }
            }
            #undef EVAL
            #undef CURVE
            for (int c = 0; c < nclub; c++) {
                double *o = out_club + ((size_t)ce * nclub + c) * 6;
                const double *lm = lim + ((size_t)ce * nclub + c) * 2;
                o[0] = caim[c]; o[1] = cev[c]; o[2] = zlo[c]; o[3] = zhi[c];
                o[4] = (caim[c] <= lm[0] + 1 || caim[c] >= lm[1] - 1) ? 1.0 : 0.0; o[5] = nsw[c];
            }
            double *oc = out_cell + (size_t)ce * 8;
            oc[0] = leader; oc[1] = runner; oc[2] = mar; oc[3] = se_run; oc[4] = nsw[leader];
            oc[5] = sep; oc[6] = aim_ok; oc[7] = gse[leader];
        }
        free(car); free(bsum); free(aims); free(cur); free(w0); free(caim);
    }
    *balls_out = balls;
}

int fs_max_threads(void)
{
#ifdef _OPENMP
    return omp_get_max_threads();
#else
    return 1;
#endif
}
