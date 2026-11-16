/* Fast-path imagery kernels (fetch stage). ctypes front end and numpy references: fastimg.py; tests: test_fastimg.py.
 *
 *   fi_paste_u8     mosaic paste of one item's window into the course grid: mode 0 = rasterio.merge 'first'
 *                   (an element is set where it is still 0 and the source is not), mode 1 = 'last valid'
 *                   (naip_years.read_year: np.where(src > 0, src, dst)). Band-sequential uint8 arrays.
 *   fi_metrics      naip_years.metrics (the NAIP year-scoring statistics) on one year's RGBN array: NDVI, excess
 *                   green, bare share, cloud share, haze (2nd percentile of blue), turf RGB, per-green NDVI medians.
 *                   Same float32 arithmetic and the same median / percentile definitions as numpy, so the numbers
 *                   are equal, not close (test_fastimg.py).
 *   fi_chm_merge    canopy.fetch's per-quadkey merge (first finite value wins) and its uint8 quantisation.
 *
 * Nothing here reads a file or a byte from the network: decoding (zlib, libjpeg) and HTTP stay in GDAL / Python.
 * Build: gcc -O3 -march=native -ffp-contract=off -fopenmp -shared -fPIC (no -ffast-math: the float32 results must
 * be the ones numpy computes).
 */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ---------------------------------------------------------------------------------------------- mosaic paste */
/* dst (nb, DH, DW) contiguous; src (nb, SH, SW) contiguous; src pixel (r, c) goes to dst (r0 + r, c0 + c).
 * The caller guarantees the rectangle lies inside dst (fastimg.paste checks it). */
void fi_paste_u8(uint8_t *dst, long DH, long DW, const uint8_t *src, long SH, long SW, int nb, long r0, long c0,
                 int mode)
{
    long rows = (long)nb * SH;
#pragma omp parallel for schedule(static) if (rows * SW > (1L << 20))
    for (long k = 0; k < rows; k++) {
        long b = k / SH, r = k % SH;
        uint8_t *d = dst + ((size_t)b * DH + (size_t)(r0 + r)) * DW + c0;
        const uint8_t *s = src + ((size_t)b * SH + (size_t)r) * SW;
        if (mode == 0) {
            for (long c = 0; c < SW; c++)
                if (d[c] == 0 && s[c] != 0) d[c] = s[c];
        } else {
            for (long c = 0; c < SW; c++)
                if (s[c] > 0) d[c] = s[c];
        }
    }
}

/* ---------------------------------------------------------------------------------------------- selection */
static void swapf(float *a, float *b) { float t = *a; *a = *b; *b = t; }

/* k-th smallest of v[0..n) (v is reordered: Hoare quickselect, median-of-three pivot) */
static float select_k(float *v, long n, long k)
{
    long lo = 0, hi = n - 1;
    while (hi > lo) {
        long mid = lo + (hi - lo) / 2;
        if (v[mid] < v[lo]) swapf(&v[mid], &v[lo]);
        if (v[hi] < v[lo]) swapf(&v[hi], &v[lo]);
        if (v[hi] < v[mid]) swapf(&v[hi], &v[mid]);
        float p = v[mid];
        long i = lo, j = hi;
        while (i <= j) {
            while (v[i] < p) i++;
            while (v[j] > p) j--;
            if (i <= j) { swapf(&v[i], &v[j]); i++; j--; }
        }
        if (k <= j) hi = j;
        else if (k >= i) lo = i;
        else return v[k];
    }
    return v[k];
}

/* np.median of a float32 array: the middle element, or the float32 mean of the two middle ones */
static float median_f(float *v, long n)
{
    long k = n / 2;
    float hi = select_k(v, n, k);
    if (n % 2) return hi;
    float lo = v[0];                                   /* after select_k, v[0..k) <= v[k]: the max of them */
    for (long i = 1; i < k; i++) if (v[i] > lo) lo = v[i];
    return (lo + hi) / 2.0f;
}

/* order statistic k (0-based) of a uint8 histogram */
static int hist_k(const long *h, long k)
{
    long c = 0;
    for (int v = 0; v < 256; v++) { c += h[v]; if (c > k) return v; }
    return 255;
}

/* np.median of uint8 values cast to float32, from their histogram */
static float hist_median(const long *h, long n)
{
    long k = n / 2;
    float hi = (float)hist_k(h, k);
    if (n % 2) return hi;
    float lo = (float)hist_k(h, k - 1);
    return (lo + hi) / 2.0f;
}

/* np.percentile(values, q) (method 'linear') of uint8 values cast to float32, from their histogram */
static double hist_percentile(const long *h, long n, double q)
{
    double vi = (q / 100.0) * (double)(n - 1);
    double pf = floor(vi);
    long p = (long)pf, nx = p + 1 < n ? p + 1 : n - 1;
    double t = vi - pf;
    float a = (float)hist_k(h, p), b = (float)hist_k(h, nx);
    float d = b - a;
    return t >= 0.5 ? (double)b - (double)d * (1.0 - t) : (double)a + (double)d * t;
}

/* NDVI of a (NIR, red) uint8 pair is one of 65536 float32 values: PAIR_ORDER lists the pairs by NDVI (built once
 * at load), so a median over any pixel set is a 65536-bin histogram walked in that order: exact, O(n) */
static float PAIR_NDVI[65536];
static uint16_t PAIR_ORDER[65536];

static float ndvi_of(int nir, int red)
{
    float r = (float)red, nn = (float)nir, den = nn + r;
    return (nn - r) / (den > 1.0f ? den : 1.0f);
}

static int cmp_pair(const void *a, const void *b)
{
    float x = PAIR_NDVI[*(const uint16_t *)a], y = PAIR_NDVI[*(const uint16_t *)b];
    return (x > y) - (x < y);
}

__attribute__((constructor)) static void init_pairs(void)
{
    for (int i = 0; i < 65536; i++) { PAIR_NDVI[i] = ndvi_of(i >> 8, i & 255); PAIR_ORDER[i] = (uint16_t)i; }
    qsort(PAIR_ORDER, 65536, sizeof(uint16_t), cmp_pair);
}

/* np.median of the NDVI values counted in h (h[nir * 256 + red]), n of them */
static float pair_median(const long *h, long n)
{
    long k = n / 2, c = 0;
    float lo = 0.0f, hi = 0.0f;
    int have_lo = 0;
    for (int j = 0; j < 65536; j++) {
        long q = h[PAIR_ORDER[j]];
        if (!q) continue;
        float v = PAIR_NDVI[PAIR_ORDER[j]];
        if (!have_lo && c + q > k - 1) { lo = v; have_lo = 1; }
        c += q;
        if (c > k) { hi = v; break; }
    }
    return n % 2 ? hi : (lo + hi) / 2.0f;
}

/* ---------------------------------------------------------------------------------------------- year metrics */
/* r, g, b, n: the bands (npx uint8 each); valid, turf: uint8 0/1; labels: int32 0..n_greens.
 * out (12 doubles, NaN = None): turf_ndvi, turf_exg, green_ndvi, bare_turf, cloud, haze, turf_r, turf_g, turf_b,
 *     turf_px, fallback (0/1), use_any (0/1).
 * green_meds (n_greens doubles): median NDVI of each green (NaN when it has fewer than min_px valid pixels).
 * Returns 0, or -1 when out of memory. */
int fi_metrics(const uint8_t *R, const uint8_t *G, const uint8_t *B, const uint8_t *N, const uint8_t *valid,
               const uint8_t *turf, const int32_t *labels, long npx, int n_greens, int min_px, double *out,
               double *green_meds)
{
    const float BARE = 0.15f, BRIGHT_NDVI = 0.1f;      /* naip_years.BARE_NDVI and the cloud rule, as float32 */
    for (int i = 0; i < 12; i++) out[i] = NAN;
    for (int i = 0; i < n_greens; i++) green_meds[i] = NAN;
    long *hp = calloc(65536, sizeof(long)), *hpg = calloc(65536, sizeof(long)), *he = calloc(1021, sizeof(long));
    long *cnt = calloc((size_t)n_greens + 2, sizeof(long));
    if (!hp || !hpg || !he || !cnt) { free(hp); free(hpg); free(he); free(cnt); return -1; }
    long hr[256] = {0}, hg[256] = {0}, hb[256] = {0}, hbv[256] = {0};
    /* pass 1: the counts that decide the turf set (OSM turf, or the vegetated box when it has < 200 px), blue over
     * the valid box (haze), the green labels (green_ndvi, and the sizes of each green's slice) */
    long n_use = 0, n_valid = 0, ng = 0;
    for (long i = 0; i < npx; i++) {
        if (!valid[i]) continue;
        n_valid++;
        hbv[B[i]]++;
        n_use += turf[i] != 0;
        int l = labels[i];
        if (l > 0) {
            ng++;
            hpg[(int)N[i] << 8 | R[i]]++;
            if (l <= n_greens) cnt[l + 1]++;
        }
    }
    int fallback = n_use < 200;
    /* pass 2: the turf statistics */
    long m = 0, bare = 0, bright = 0;
    for (long i = 0; i < npx; i++) {
        if (!valid[i]) continue;
        int pr = (int)N[i] << 8 | R[i];
        float t = PAIR_NDVI[pr];
        if (fallback ? !(t > 0.0f) : !turf[i]) continue;
        m++;
        hp[pr]++;
        bare += t < BARE;
        bright += (R[i] > 200 && G[i] > 200 && B[i] > 200 && t < BRIGHT_NDVI);
        hr[R[i]]++; hg[G[i]]++; hb[B[i]]++;
        he[2 * (int)G[i] - (int)R[i] - (int)B[i] + 510]++;  /* excess green: an integer in [-510, 510] */
    }
    out[9] = (double)m;
    out[10] = fallback;
    out[11] = m > 0;
    if (m) {
        out[0] = pair_median(hp, m);
        out[3] = (double)bare / (double)m;
        out[4] = (double)bright / (double)m;
        out[6] = hist_median(hr, m);
        out[7] = hist_median(hg, m);
        out[8] = hist_median(hb, m);
        long k = m / 2, c = 0;
        int lo = -1, hi = -1;
        for (int v = 0; v < 1021; v++) {
            c += he[v];
            if (lo < 0 && c > k - 1 && m % 2 == 0) lo = v;
            if (c > k) { hi = v; break; }
        }
        float fh = (float)(hi - 510);
        out[1] = m % 2 ? fh : ((float)(lo - 510) + fh) / 2.0f;
    }
    if (n_valid) out[5] = hist_percentile(hbv, n_valid, 2.0);
    if (ng >= 30) out[2] = pair_median(hpg, ng);
    /* each green's own median: its NDVI values gathered by a counting sort on the label, then a quickselect */
    if (n_greens > 0) {
        for (int l = 1; l <= n_greens + 1; l++) cnt[l] += cnt[l - 1];   /* cnt[l] = start of label l */
        long tot = cnt[n_greens + 1];
        float *buf = malloc(sizeof(float) * (size_t)(tot ? tot : 1));
        long *pos = malloc(sizeof(long) * ((size_t)n_greens + 2));
        if (!buf || !pos) { free(buf); free(pos); free(hp); free(hpg); free(he); free(cnt); return -1; }
        memcpy(pos, cnt, sizeof(long) * ((size_t)n_greens + 2));
        for (long i = 0; i < npx; i++) {
            int l = labels[i];
            if (l > 0 && l <= n_greens && valid[i]) buf[pos[l]++] = PAIR_NDVI[(int)N[i] << 8 | R[i]];
        }
        for (int l = 1; l <= n_greens; l++) {
            long n = cnt[l + 1] - cnt[l];
            if (n >= min_px) green_meds[l - 1] = median_f(buf + cnt[l], n);
        }
        free(buf);
        free(pos);
    }
    free(hp); free(hpg); free(he); free(cnt);
    return 0;
}

/* ---------------------------------------------------------------------------------------------- canopy */
/* acc (float32, NaN = nothing yet) takes tmp's finite values where it has none (canopy.fetch, per quadkey) */
void fi_chm_merge(float *acc, const float *tmp, long npx)
{
#pragma omp parallel for schedule(static) if (npx > (1L << 21))
    for (long i = 0; i < npx; i++)
        if (isnan(acc[i]) && isfinite(tmp[i])) acc[i] = tmp[i];
}

/* q = 255 where acc is NaN, else clip(round-half-even(acc), 0, 254) (np.round, np.clip, astype(uint8)) */
void fi_chm_quantize(const float *acc, uint8_t *q, long npx)
{
#pragma omp parallel for schedule(static) if (npx > (1L << 21))
    for (long i = 0; i < npx; i++) {
        float v = acc[i];
        if (!isfinite(v)) { q[i] = 255; continue; }
        float r = nearbyintf(v);                        /* round half to even under the default rounding mode */
        q[i] = r < 0.0f ? 0 : (r > 254.0f ? 254 : (uint8_t)r);
    }
}
