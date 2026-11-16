/* fastc/routing: the joint router's beam search (zero_tap/joint/solve2.py beam2) in C.

   Same arithmetic in the same order as the numpy reference, same deterministic selection (the k smallest ranks,
   ties by flat index; then sorted by (rank, index); first occurrence of each state key kept; first B states), so
   the result is identical. Compiled by fastroute.py (gcc -O3 -march=native -ffp-contract=off). */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define BIG 1e6

typedef struct { double v; int64_t i; } VI;
typedef struct { double v; int64_t i; double t; } VIT;

static int cmp_vit(const void *a, const void *b) {
    const VIT *x = (const VIT *)a, *y = (const VIT *)b;
    if (x->v < y->v) return -1;
    if (x->v > y->v) return 1;
    return (x->i > y->i) - (x->i < y->i);
}

static int cmp_vi(const void *a, const void *b) {
    const VI *x = (const VI *)a, *y = (const VI *)b;
    if (x->v < y->v) return -1;
    if (x->v > y->v) return 1;
    return (x->i > y->i) - (x->i < y->i);
}

/* k-th smallest (0-based) of a[0..n) by quickselect on a copy */
static double kth(double *w, int64_t n, int64_t k) {
    int64_t lo = 0, hi = n - 1;
    while (lo < hi) {
        double p = w[lo + (hi - lo) / 2];
        int64_t i = lo, j = hi;
        while (i <= j) {
            while (w[i] < p) i++;
            while (w[j] > p) j--;
            if (i <= j) { double t = w[i]; w[i] = w[j]; w[j] = t; i++; j--; }
        }
        if (k <= j) hi = j;
        else if (k >= i) lo = i;
        else return w[k];
    }
    return w[k];
}

/* open-addressing set of 64-bit keys */
typedef struct { uint64_t *k; uint8_t *u; int64_t cap; } KSet;
static int kset_add(KSet *s, uint64_t key) {           /* 1 if newly added */
    uint64_t h = key * 0x9E3779B97F4A7C15ULL;
    int64_t m = s->cap - 1, p = (int64_t)(h >> 17) & m;
    while (s->u[p]) {
        if (s->k[p] == key) return 0;
        p = (p + 1) & m;
    }
    s->u[p] = 1; s->k[p] = key;
    return 1;
}

/* step [N*C] (base + card + mask), Tm [N*E*C] (row i: transitions into position i; row 0 unused), st [N*C] loop
   start costs (rows i % loop == 0), en [N*E] loop end costs (rows i % loop == loop - 1 and N - 1), gbit / tbit [C],
   endi [C], X [C*C], pz [C] or NULL, reuse < 0: no tee reuse. Out: seqs [keep*N], costs [keep]; returns the number
   of routings written (0: no feasible state). */
int fr_beam(int N, int C, int E, int B, int loop, const double *step, const double *Tm, const double *st,
            const double *en, const uint64_t *gbit, const uint64_t *tbit, const int64_t *endi, const uint8_t *X,
            const double *pz, double reuse, double wx, int keep, int64_t *seqs, double *costs) {
    int64_t S = 1;
    int64_t cap = (int64_t)B;
    uint64_t *gm = calloc(cap, 8), *tm = calloc(cap, 8), *ngm = calloc(cap, 8), *ntm = calloc(cap, 8);
    int64_t *last = calloc(cap, 8), *nlast = calloc(cap, 8);
    double *rank = calloc(cap, 8), *tru = calloc(cap, 8), *nrank = calloc(cap, 8), *ntru = calloc(cap, 8);
    uint8_t *acc = calloc((size_t)cap * C, 1), *nacc = calloc((size_t)cap * C, 1);
    int64_t *bpar = calloc((size_t)N * cap, 8), *bc = calloc((size_t)N * cap, 8);
    int64_t *nS = calloc(N, 8);
    int64_t kmax = 4 * (int64_t)B;
    VI *sel = malloc((size_t)(kmax + 1) * sizeof(VI));
    double *selt = malloc((size_t)(kmax + 1) * 8);
    VIT *srt = malloc((size_t)(kmax + 1) * sizeof(VIT));
    int64_t hcap = 1; while (hcap < 2 * kmax + 2) hcap <<= 1;
    KSet ks = { malloc(hcap * 8), malloc(hcap), hcap };
    int ret = 0;
    gm[0] = 0; tm[0] = 0; last[0] = 0; rank[0] = 0; tru[0] = 0;
    for (int i = 0; i < N; i++) {
        const double *sp = step + (size_t)i * C;
        int lt = (i > 0 && i % loop == 0);
        /* the k smallest (rank, flat index) among feasible cells, by a bounded max-heap (same set as the
           reference's sort-free top-k + filter, since (rank, index) is a total order) */
        int64_t n = S * C, k = n < kmax ? n : kmax, m = 0;
        for (int64_t s = 0; s < S; s++) {
            const uint8_t *a = acc + (size_t)s * C;
            const double *trow = i > 0 ? Tm + ((size_t)i * E + last[s]) * C : st;
            double ens = lt ? en[(size_t)(i - 1) * E + last[s]] : 0.0;
            const double *strow = st + (size_t)i * C;
            for (int c = 0; c < C; c++) {
                double t = trow[c];
                if (lt) {
                    double alt = ens + strow[c];
                    if (alt < t) t = alt;
                }
                double ad = (sp[c] + t) + wx * (double)a[c];
                int tcl = (tm[s] & tbit[c]) != 0;
                int bad;
                if (reuse >= 0) { ad = ad + reuse * (double)tcl; bad = (gm[s] & gbit[c]) != 0; }
                else bad = ((gm[s] & gbit[c]) != 0) || tcl;
                if (bad) continue;                       /* rank BIG*10: never among the k smallest feasible */
                double tv = tru[s] + ad;
                if (!(tv < BIG)) continue;
                double v = (rank[s] + ad) + (pz ? pz[c] : 0.0);
                int64_t f = s * C + c;
                if (m < k) {                             /* sift up */
                    int64_t q = m++;
                    while (q > 0) {
                        int64_t pp = (q - 1) / 2;
                        if (sel[pp].v > v || (sel[pp].v == v && sel[pp].i > f)) break;
                        sel[q] = sel[pp]; selt[q] = selt[pp]; q = pp;
                    }
                    sel[q].v = v; sel[q].i = f; selt[q] = tv;
                } else if (v < sel[0].v || (v == sel[0].v && f < sel[0].i)) {   /* replace the max, sift down */
                    int64_t q = 0;
                    for (;;) {
                        int64_t l = 2 * q + 1, r = l + 1, bgt = q;
                        double bv = v; int64_t bi = f;
                        if (l < m && (sel[l].v > bv || (sel[l].v == bv && sel[l].i > bi))) { bgt = l; bv = sel[l].v; bi = sel[l].i; }
                        if (r < m && (sel[r].v > bv || (sel[r].v == bv && sel[r].i > bi))) { bgt = r; }
                        if (bgt == q) break;
                        sel[q] = sel[bgt]; selt[q] = selt[bgt]; q = bgt;
                    }
                    sel[q].v = v; sel[q].i = f; selt[q] = tv;
                }
            }
        }
        if (m == 0) { ret = 0; goto done; }
        for (int64_t q = 0; q < m; q++) { srt[q].v = sel[q].v; srt[q].i = sel[q].i; srt[q].t = selt[q]; }
        qsort(srt, m, sizeof(VIT), cmp_vit);
        memset(ks.u, 0, hcap);
        int64_t ns = 0;
        for (int64_t q = 0; q < m && ns < B; q++) {
            int64_t f = srt[q].i, s = f / C, c = f % C;
            uint64_t g2 = gm[s] | gbit[c], t2 = tm[s] | tbit[c];
            int64_t l2 = endi[c];
            uint64_t key = (g2 * 0x9E3779B97F4A7C15ULL) ^ (t2 * 0xC2B2AE3D27D4EB4FULL) ^ (uint64_t)l2;
            if (!kset_add(&ks, key)) continue;
            ngm[ns] = g2; ntm[ns] = t2; nlast[ns] = l2; nrank[ns] = srt[q].v; ntru[ns] = srt[q].t;
            const uint8_t *a = acc + (size_t)s * C, *x = X + (size_t)c * C;
            uint8_t *b = nacc + (size_t)ns * C;
            for (int j = 0; j < C; j++) b[j] = (uint8_t)(a[j] + x[j]);
            bpar[(size_t)i * cap + ns] = s; bc[(size_t)i * cap + ns] = c;
            ns++;
        }
        S = ns; nS[i] = ns;
        { uint64_t *t = gm; gm = ngm; ngm = t; } { uint64_t *t = tm; tm = ntm; ntm = t; }
        { int64_t *t = last; last = nlast; nlast = t; } { double *t = rank; rank = nrank; nrank = t; }
        { double *t = tru; tru = ntru; ntru = t; } { uint8_t *t = acc; acc = nacc; nacc = t; }
    }
    {
        VI *fin = malloc((size_t)S * sizeof(VI));
        for (int64_t s = 0; s < S; s++) { fin[s].v = tru[s] + en[(size_t)(N - 1) * E + last[s]]; fin[s].i = s; }
        qsort(fin, S, sizeof(VI), cmp_vi);           /* == np.argsort(kind="stable") */
        int kk = keep < S ? keep : (int)S;
        for (int q = 0; q < kk; q++) {
            int64_t s = fin[q].i;
            costs[q] = fin[q].v;
            for (int i = N - 1; i >= 0; i--) {
                seqs[(size_t)q * N + i] = bc[(size_t)i * cap + s];
                s = bpar[(size_t)i * cap + s];
            }
        }
        free(fin);
        ret = kk;
    }
done:
    free(gm); free(tm); free(ngm); free(ntm); free(last); free(nlast); free(rank); free(tru); free(nrank);
    free(ntru); free(acc); free(nacc); free(bpar); free(bc); free(nS); free(sel); free(selt); free(srt);
    free(ks.k); free(ks.u);
    return ret;
}
