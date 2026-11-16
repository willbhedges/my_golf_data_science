/* Fast-path perception kernels (course_data/platform/fastpath/fastscene.py), loaded with ctypes by fastperc.py.
 *
 *   fp_features   the 38-feature stack of fastscene.features_py (NAIP / canopy / DEM -> float32 planes)
 *   fp_gbm        LightGBM multiclass tree ensemble -> softmax probabilities (numerical splits only)
 *   fp_label      8-connected component labelling of a uint8 mask (two-pass, union-find), sizes
 *
 * Separable filters follow scipy.ndimage: gaussian_filter(mode="nearest", truncate=3.0) = correlate1d with
 * weights exp(-x^2 / 2 s^2) / sum over |x| <= int(3 s + 0.5), one axis after the other (axis 0, then 1), each
 * pass accumulated in double and stored as float32 like scipy does for a float32 array; uniform_filter(k,
 * "nearest") = the mean of k samples centred on the pixel ((k - 1) / 2 each side for odd k). np.gradient:
 * central differences inside, one-sided at the edges.
 * Build: gcc -O3 -march=native -ffp-contract=off -fopenmp -shared -fPIC (fastperc.py, once per source hash).
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static inline long clampi(long i, long n) { return i < 0 ? 0 : (i >= n ? n - 1 : i); }

/* correlate along axis 0 (rows) or 1 (cols) with weights w[0..2r], nearest-edge mode; src and dst may not alias */
static void corr1d(const float *src, float *dst, long H, long W, const double *w, int r, int axis) {
    if (axis == 0) {
        #pragma omp parallel
        {
            double *acc = (double *)malloc(sizeof(double) * W);
            #pragma omp for schedule(static)
            for (long i = 0; i < H; i++) {
                for (long j = 0; j < W; j++) acc[j] = 0.0;
                for (int k = -r; k <= r; k++) {
                    const float *row = src + clampi(i + k, H) * W;
                    double wk = w[k + r];
                    for (long j = 0; j < W; j++) acc[j] += (double)row[j] * wk;
                }
                float *o = dst + i * W;
                for (long j = 0; j < W; j++) o[j] = (float)acc[j];
            }
            free(acc);
        }
    } else {
        #pragma omp parallel
        {
            double *buf = (double *)malloc(sizeof(double) * (W + 2 * r));
            #pragma omp for schedule(static)
            for (long i = 0; i < H; i++) {
                const float *row = src + i * W;
                for (long j = -r; j < W + r; j++) buf[j + r] = row[clampi(j, W)];
                float *o = dst + i * W;
                for (long j = 0; j < W; j++) {
                    double a = 0.0;
                    const double *b = buf + j;
                    for (int k = 0; k <= 2 * r; k++) a += b[k] * w[k];
                    o[j] = (float)a;
                }
            }
            free(buf);
        }
    }
}

static void gauss(const float *src, float *dst, float *tmp, long H, long W, double s) {
    int r = (int)(3.0 * s + 0.5);
    double *w = (double *)malloc(sizeof(double) * (2 * r + 1));
    double sum = 0.0;
    for (int k = -r; k <= r; k++) { w[k + r] = exp(-0.5 / (s * s) * (double)k * k); sum += w[k + r]; }
    for (int k = 0; k <= 2 * r; k++) w[k] /= sum;
    corr1d(src, tmp, H, W, w, r, 0);
    corr1d(tmp, dst, H, W, w, r, 1);
    free(w);
}

static void uniform(const float *src, float *dst, float *tmp, long H, long W, int k) {
    int r = k / 2;
    double *w = (double *)malloc(sizeof(double) * k);
    for (int i = 0; i < k; i++) w[i] = 1.0 / k;
    corr1d(src, tmp, H, W, w, r, 0);
    corr1d(tmp, dst, H, W, w, r, 1);
    free(w);
}

/* local standard deviation, k x k: sqrt(max(E[x^2] - E[x]^2, 0)) */
static void lstd(const float *a, float *dst, float *t1, float *t2, float *t3, long H, long W, int k) {
    long n = H * W;
    uniform(a, t1, t3, H, W, k);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) t2[i] = a[i] * a[i];
    uniform(t2, dst, t3, H, W, k);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) { float v = dst[i] - t1[i] * t1[i]; dst[i] = sqrtf(v > 0.f ? v : 0.f); }
}

/* np.gradient of a float32 array (unit spacing): gy along rows, gx along cols, in float32 */
static void gradient(const float *z, float *gy, float *gx, long H, long W) {
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < H; i++) {
        for (long j = 0; j < W; j++) {
            long p = i * W + j;
            if (H == 1) gy[p] = 0.f;
            else if (i == 0) gy[p] = z[p + W] - z[p];
            else if (i == H - 1) gy[p] = z[p] - z[p - W];
            else gy[p] = (z[p + W] - z[p - W]) / 2.0f;
            if (W == 1) gx[p] = 0.f;
            else if (j == 0) gx[p] = z[p + 1] - z[p];
            else if (j == W - 1) gx[p] = z[p] - z[p - 1];
            else gx[p] = (z[p + 1] - z[p - 1]) / 2.0f;
        }
    }
}

enum { F_r, F_g, F_b, F_nir, F_ndvi, F_exg, F_bright, F_ndvi_d, F_bright_d, F_nir_d, F_exg_d, F_sd_g3, F_sd_g5,
       F_sd_n3, F_sd_n5, F_grad, F_sd_g5_c4, F_sd_g5_c10, F_ndvi_c4, F_ndvi_c10, F_ndvi_c25, F_bright_c4,
       F_bright_c10, F_bright_c25, F_ndvi_ring, F_bright_ring, F_sd_ring, F_sand_c6, F_sand_c15, F_hag, F_tree_c3,
       F_tree_c8, F_tree_c20, F_slope, F_rough, F_relief6, F_relief15, F_relief40, NF };

int fp_nfeatures(void) { return NF; }

/* naip (4, H, W) uint8; hag (H, W) uint8 (0.25 m, 255 none); dtm (H, W) uint16 (cm, 65535 none, already filled
 * with `zfill` where missing); ref[8] = turf medians / IQRs (ndvi, bright, nir, exg). out: (NF, H, W) float32. */
int fp_features(const uint8_t *naip, const uint8_t *hag, const uint16_t *dtm, long H, long W, float zfill,
                const double *ref, float *out) {
    long n = H * W;
    float *t1 = (float *)malloc(sizeof(float) * n), *t2 = (float *)malloc(sizeof(float) * n);
    float *t3 = (float *)malloc(sizeof(float) * n), *t4 = (float *)malloc(sizeof(float) * n);
    if (!t1 || !t2 || !t3 || !t4) { free(t1); free(t2); free(t3); free(t4); return -1; }
#define P(k) (out + (long)(k) * n)
    const float rn = (float)ref[0], rb = (float)ref[2], rnir = (float)ref[4], rexg = (float)ref[6];
    const double iqr_b = ref[3], iqr_n = ref[1];
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) {
        float r = naip[i], g = naip[n + i], b = naip[2 * n + i], nir = naip[3 * n + i];
        P(F_r)[i] = r; P(F_g)[i] = g; P(F_b)[i] = b; P(F_nir)[i] = nir;
        float bright = (r + g + b) / 3.0f;
        float den = nir + r; if (den < 1.0f) den = 1.0f;
        float ndvi = (nir - r) / den;
        float exg = 2 * g - r - b;
        P(F_bright)[i] = bright; P(F_ndvi)[i] = ndvi; P(F_exg)[i] = exg;
        P(F_ndvi_d)[i] = ndvi - rn; P(F_bright_d)[i] = bright - rb; P(F_nir_d)[i] = nir - rnir; P(F_exg_d)[i] = exg - rexg;
        /* sand: ((bright - mb) / iqr_b - (ndvi - mn) / iqr_n) > 2.5, evaluated as numpy does (float32 arrays,
           float64 scalars -> float32 result) */
        float sa = (float)((double)(bright - (float)ref[2]) / iqr_b) ;
        float sb = (float)((double)(ndvi - (float)ref[0]) / iqr_n);
        t4[i] = (sa - sb) > 2.5f ? 1.0f : 0.0f;
        float h = hag[i] == 255 ? 0.0f : (float)hag[i] * 0.25f;
        P(F_hag)[i] = h;
        t3[i] = h > 2.5f ? 1.0f : 0.0f;
    }
    gauss(t4, P(F_sand_c6), t1, H, W, 6.0);
    gauss(t4, P(F_sand_c15), t1, H, W, 15.0);
    gauss(t3, P(F_tree_c3), t1, H, W, 3.0);
    gauss(t3, P(F_tree_c8), t1, H, W, 8.0);
    gauss(t3, P(F_tree_c20), t1, H, W, 20.0);
    lstd(P(F_g), P(F_sd_g3), t1, t2, t3, H, W, 3);
    lstd(P(F_g), P(F_sd_g5), t1, t2, t3, H, W, 5);
    lstd(P(F_nir), P(F_sd_n3), t1, t2, t3, H, W, 3);
    lstd(P(F_nir), P(F_sd_n5), t1, t2, t3, H, W, 5);
    gauss(P(F_bright), t4, t1, H, W, 1.0);
    gradient(t4, t2, t3, H, W);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) t4[i] = hypotf(t3[i], t2[i]);
    gauss(t4, P(F_grad), t1, H, W, 1.0);
    gauss(P(F_sd_g5), P(F_sd_g5_c4), t1, H, W, 4.0);
    gauss(P(F_sd_g5), P(F_sd_g5_c10), t1, H, W, 10.0);
    gauss(P(F_ndvi), P(F_ndvi_c4), t1, H, W, 4.0);
    gauss(P(F_bright), P(F_bright_c4), t1, H, W, 4.0);
    gauss(P(F_ndvi), P(F_ndvi_c10), t1, H, W, 10.0);
    gauss(P(F_bright), P(F_bright_c10), t1, H, W, 10.0);
    gauss(P(F_ndvi), P(F_ndvi_c25), t1, H, W, 25.0);
    gauss(P(F_bright), P(F_bright_c25), t1, H, W, 25.0);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) {
        P(F_ndvi_ring)[i] = P(F_ndvi_c4)[i] - P(F_ndvi_c10)[i];
        P(F_bright_ring)[i] = P(F_bright_c4)[i] - P(F_bright_c10)[i];
        P(F_sd_ring)[i] = P(F_sd_g5_c4)[i] - P(F_sd_g5_c10)[i];
        t4[i] = dtm[i] == 65535 ? zfill : (float)dtm[i] / 100.0f;
    }
    /* DEM: zs = g(z, 1); slope = g(|grad zs|, 1); rough = g(|zs - g(zs, 3)|, 2); relief_s = zs - g(zs, s) */
    float *zs = P(F_relief6);                       /* scratch until relief6 is written last */
    gauss(t4, zs, t1, H, W, 1.0);
    gradient(zs, t2, t3, H, W);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) t4[i] = hypotf(t3[i], t2[i]);
    gauss(t4, P(F_slope), t1, H, W, 1.0);
    gauss(zs, t2, t1, H, W, 3.0);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) t2[i] = fabsf(zs[i] - t2[i]);
    gauss(t2, P(F_rough), t1, H, W, 2.0);
    gauss(zs, t2, t1, H, W, 15.0);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) P(F_relief15)[i] = zs[i] - t2[i];
    gauss(zs, t2, t1, H, W, 40.0);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) P(F_relief40)[i] = zs[i] - t2[i];
    gauss(zs, t2, t1, H, W, 6.0);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < n; i++) P(F_relief6)[i] = zs[i] - t2[i];
#undef P
    free(t1); free(t2); free(t3); free(t4);
    return 0;
}

/* LightGBM trees, flattened: tree t has nodes [node_off[t], node_off[t+1]) with feature, threshold, left, right
 * (child >= 0: node index within the tree, < 0: leaf ~child), leaves [leaf_off[t], ...). decision: x <= thr ->
 * left (numerical split, no missing values: the features are NaN-free; dleft[] only used when x is NaN).
 * Tree t adds to class t % K. X (n, nf) float32 row-major; out (n, K) float64 softmax. */
int fp_gbm(const float *X, long n, int nf, int ntree, int K, const int *node_off, const int *leaf_off,
           const int *feat, const double *thr, const int *left, const int *right, const int8_t *dleft,
           const double *leaf, double *out) {
    #pragma omp parallel for schedule(dynamic, 1024)
    for (long i = 0; i < n; i++) {
        const float *x = X + i * (long)nf;
        double s[64];
        for (int k = 0; k < K; k++) s[k] = 0.0;
        for (int t = 0; t < ntree; t++) {
            int no = node_off[t], lo = leaf_off[t];
            double v;
            if (node_off[t + 1] == no) v = leaf[lo];
            else {
                int nd = 0;
                for (;;) {
                    int q = no + nd;
                    double xv = (double)x[feat[q]];
                    int go_left = isnan(xv) ? dleft[q] : (xv <= thr[q]);
                    int c = go_left ? left[q] : right[q];
                    if (c < 0) { v = leaf[lo + ~c]; break; }
                    nd = c;
                }
            }
            s[t % K] += v;
        }
        double m = s[0];
        for (int k = 1; k < K; k++) if (s[k] > m) m = s[k];
        double z = 0.0;
        for (int k = 0; k < K; k++) { s[k] = exp(s[k] - m); z += s[k]; }
        for (int k = 0; k < K; k++) out[i * K + k] = s[k] / z;
    }
    return 0;
}

/* the same ensemble, rows in blocks of GB_BLOCK, trees outer within a block (the tree's nodes stay in cache):
 * identical sums in the identical tree order -> bit-identical to fp_gbm */
#define GB_BLOCK 128
int fp_gbm_blocked(const float *X, long n, int nf, int ntree, int K, const int *node_off, const int *leaf_off,
                   const int *feat, const double *thr, const int *left, const int *right, const int8_t *dleft,
                   const double *leaf, double *out) {
    long nb = (n + GB_BLOCK - 1) / GB_BLOCK;
    #pragma omp parallel for schedule(dynamic, 4)
    for (long bi = 0; bi < nb; bi++) {
        long i0 = bi * GB_BLOCK, i1 = i0 + GB_BLOCK < n ? i0 + GB_BLOCK : n;
        int m = (int)(i1 - i0);
        double s[GB_BLOCK * 64];
        for (int j = 0; j < m * K; j++) s[j] = 0.0;
        for (int t = 0; t < ntree; t++) {
            int no = node_off[t], lo = leaf_off[t], k = t % K;
            if (node_off[t + 1] == no) { for (int j = 0; j < m; j++) s[j * K + k] += leaf[lo]; continue; }
            const int *ft = feat + no, *lt = left + no, *rt = right + no;
            const double *th = thr + no;
            const int8_t *dl = dleft + no;
            for (int j = 0; j < m; j++) {
                const float *x = X + (i0 + j) * (long)nf;
                int nd = 0, c;
                for (;;) {
                    double xv = (double)x[ft[nd]];
                    int go_left = isnan(xv) ? dl[nd] : (xv <= th[nd]);
                    c = go_left ? lt[nd] : rt[nd];
                    if (c < 0) break;
                    nd = c;
                }
                s[j * K + k] += leaf[lo + ~c];
            }
        }
        for (int j = 0; j < m; j++) {
            double *sj = s + j * K;
            double mx = sj[0];
            for (int k = 1; k < K; k++) if (sj[k] > mx) mx = sj[k];
            double z = 0.0, e[64];
            for (int k = 0; k < K; k++) { e[k] = exp(sj[k] - mx); z += e[k]; }
            for (int k = 0; k < K; k++) out[(i0 + j) * K + k] = e[k] / z;
        }
    }
    return 0;
}

/* gather rows: X[j, f] = F[f, idx[j]] for a (nf, n) plane stack -> (m, nf) row-major */
int fp_gather(const float *F, long n, int nf, const long *idx, long m, float *X) {
    #pragma omp parallel for schedule(static)
    for (long j = 0; j < m; j++) {
        long p = idx[j];
        for (int f = 0; f < nf; f++) X[j * nf + f] = F[(long)f * n + p];
    }
    return 0;
}

/* 8-connected labelling: union-find over the raster, then labels renumbered by first pixel in raster order
 * (scipy.ndimage.label's numbering). lab (H, W) int32 out; returns the number of components. */
static long uf_find(long *p, long i) { while (p[i] != i) { p[i] = p[p[i]]; i = p[i]; } return i; }
static void uf_union(long *p, long a, long b) { a = uf_find(p, a); b = uf_find(p, b); if (a < b) p[b] = a; else if (b < a) p[a] = b; }

long fp_label8(const uint8_t *m, long H, long W, int32_t *lab) {
    long n = H * W;
    long *par = (long *)malloc(sizeof(long) * n);
    if (!par) return -1;
    for (long i = 0; i < H; i++) {
        for (long j = 0; j < W; j++) {
            long p = i * W + j;
            par[p] = p;
            if (!m[p]) continue;
            if (j > 0 && m[p - 1]) uf_union(par, p, p - 1);
            if (i > 0) {
                long q = p - W;
                if (m[q]) uf_union(par, p, q);
                if (j > 0 && m[q - 1]) uf_union(par, p, q - 1);
                if (j < W - 1 && m[q + 1]) uf_union(par, p, q + 1);
            }
        }
    }
    long k = 0;
    int32_t *map = (int32_t *)calloc(n, sizeof(int32_t));
    for (long p = 0; p < n; p++) {
        if (!m[p]) { lab[p] = 0; continue; }
        long r = uf_find(par, p);
        if (!map[r]) map[r] = (int32_t)(++k);
        lab[p] = map[r];
    }
    free(map); free(par);
    return k;
}

/* grey erosion (op 0, min) / dilation (op 1, max) with a disk footprint x^2 + y^2 <= r^2, scipy.ndimage's
 * 'reflect' boundary (d c b a | a b c d | d c b a). Per output row and disk row dy: a van Herk / Gil-Werman
 * running min / max of width 2 w(dy) + 1 over the padded source row. Exact (min / max only). */
static inline long refl(long i, long n) {
    if (n == 1) return 0;
    long p = 2 * n;
    i %= p; if (i < 0) i += p;
    return i < n ? i : p - 1 - i;
}

int fp_grey_disk(const double *in, double *out, long H, long W, int r, int op) {
    int *hw = (int *)malloc(sizeof(int) * (2 * r + 1));
    for (int dy = -r; dy <= r; dy++) { int w = 0; while ((long)(w + 1) * (w + 1) + (long)dy * dy <= (long)r * r) w++; hw[dy + r] = w; }
    long PW = W + 2 * r;
    #pragma omp parallel
    {
        double *row = (double *)malloc(sizeof(double) * PW), *g = (double *)malloc(sizeof(double) * PW);
        double *h = (double *)malloc(sizeof(double) * PW), *acc = (double *)malloc(sizeof(double) * W);
        #pragma omp for schedule(static)
        for (long y = 0; y < H; y++) {
            for (long x = 0; x < W; x++) acc[x] = op ? -INFINITY : INFINITY;
            for (int dy = -r; dy <= r; dy++) {
                const double *src = in + refl(y + dy, H) * W;
                for (long x = 0; x < PW; x++) row[x] = src[refl(x - r, W)];
                int w = hw[dy + r], k = 2 * w + 1;
                /* running extreme over windows [x - w, x + w] (padded index x + r) */
                for (long b0 = 0; b0 < PW; b0 += k) {
                    long b1 = b0 + k < PW ? b0 + k : PW;
                    g[b0] = row[b0];
                    for (long x = b0 + 1; x < b1; x++) g[x] = op ? fmax(g[x - 1], row[x]) : fmin(g[x - 1], row[x]);
                    h[b1 - 1] = row[b1 - 1];
                    for (long x = b1 - 2; x >= b0; x--) h[x] = op ? fmax(h[x + 1], row[x]) : fmin(h[x + 1], row[x]);
                }
                for (long x = 0; x < W; x++) {
                    long lo = x + r - w, hi = x + r + w;      /* padded indices, inside [0, PW) */
                    double v = op ? fmax(h[lo], g[hi]) : fmin(h[lo], g[hi]);
                    acc[x] = op ? fmax(acc[x], v) : fmin(acc[x], v);
                }
            }
            for (long x = 0; x < W; x++) out[y * W + x] = acc[x];
        }
        free(row); free(g); free(h); free(acc);
    }
    free(hw);
    return 0;
}

/* perception geo.comp_stats in one raster pass: per label 1..n the pixel count, the mean row / col, and for each
 * of the k float32 planes the sum and count of its finite values. Sums are accumulated in double in raster order,
 * as numpy's bincount (behind ndimage.sum) does, so the means are bit-identical. out_cnt (n+1), out_rs / out_cs
 * (n+1), out_s / out_m (k, n+1). */
int fp_comp_stats(const int32_t *lab, long npx, int n, const float *const *planes, int k,
                  double *cnt, double *rs, double *cs, double *s, double *m, long W) {
    for (long i = 0; i <= n; i++) { cnt[i] = 0; rs[i] = 0; cs[i] = 0; }
    for (long i = 0; i < (long)k * (n + 1); i++) { s[i] = 0; m[i] = 0; }
    long nz = 0;
    for (long p = 0; p < npx; p++) nz += lab[p] > 0 && lab[p] <= n;
    long *idx = (long *)malloc(sizeof(long) * (nz ? nz : 1));
    if (!idx) return -1;
    long q = 0;
    for (long p = 0; p < npx; p++) if (lab[p] > 0 && lab[p] <= n) idx[q++] = p;
    for (long t = 0; t < nz; t++) {
        long p = idx[t]; int l = lab[p];
        cnt[l] += 1.0; rs[l] += (double)(p / W); cs[l] += (double)(p % W);
    }
    #pragma omp parallel for schedule(dynamic, 1)
    for (int j = 0; j < k; j++) {               /* planes are independent: each keeps raster order */
        const float *a = planes[j];
        double *sj = s + (long)j * (n + 1), *mj = m + (long)j * (n + 1);
        for (long t = 0; t < nz; t++) {
            long p = idx[t];
            float v = a[p];
            if (isfinite(v)) { sj[lab[p]] += (double)v; mj[lab[p]] += 1.0; }
        }
    }
    free(idx);
    return 0;
}
