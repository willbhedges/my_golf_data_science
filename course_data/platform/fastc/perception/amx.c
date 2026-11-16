/* The segment U-Net's convolutions on Intel AMX (bf16 tiles, float32 accumulation): unet_amx.py.
 *
 * Activations are NHWC bfloat16 in buffers with a 1-pixel zero border, channels padded to a multiple of 16 (< 32)
 * or 32. A convolution is an implicit GEMM: an A tile is 16 output pixels of one row x kc input channels of one
 * kernel tap, read straight from the activation buffer with a row stride of (conv stride x channels), so there is
 * no im2col. B tiles are the weights, pre-packed in the VNNI layout [O/16][tap][C/kc][kc/2][16 x 2]. The epilogue
 * (bias, residual, ReLU, rounding to bf16) runs on the float32 accumulators before they leave the core.
 *
 * Built separately from kernel.c (gcc -O3 -march=native -mamx-tile -mamx-bf16 -mavx512bf16 -fopenmp) and used only
 * when the CPU has AMX and the kernel grants the tile state (fa_init). */
#include <immintrin.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>

#define ARCH_REQ_XCOMP_PERM 0x1023
#define XFEATURE_XTILEDATA 18

typedef struct {
    uint8_t palette, start;
    uint8_t rsv[14];
    uint16_t colsb[16];
    uint8_t rows[16];
} tilecfg_t;

int fa_init(void) {
    if (syscall(SYS_arch_prctl, ARCH_REQ_XCOMP_PERM, XFEATURE_XTILEDATA)) return -1;
    /* one tiny product as a self-check: 32 ones . 32 ones */
    tilecfg_t c;
    memset(&c, 0, sizeof c);
    c.palette = 1;
    for (int i = 0; i < 8; i++) { c.rows[i] = 16; c.colsb[i] = 64; }
    _tile_loadconfig(&c);
    static uint16_t A[16 * 32], B[16 * 32];
    static float C[16 * 16];
    for (int i = 0; i < 16 * 32; i++) { A[i] = 0x3f80; B[i] = 0x3f80; }
    _tile_zero(0);
    _tile_loadd(1, A, 64);
    _tile_loadd(2, B, 64);
    _tile_dpbf16ps(0, 1, 2);
    _tile_stored(0, C, 64);
    _tile_release();
    return C[0] == 32.f && C[255] == 32.f ? 0 : -2;
}

static inline __m512 bf16_to_f32(__m256i v) { return _mm512_castsi512_ps(_mm512_slli_epi32(_mm512_cvtepu16_epi32(v), 16)); }
static inline __m256i f32_to_bf16(__m512 v) { return (__m256i)_mm512_cvtneps_pbh(v); }

static void zero_border(uint16_t *o, long H, long W, long C) {      /* buffer (H + 2, W + 2, C) */
    long Wb = W + 2;
    memset(o, 0, sizeof(uint16_t) * Wb * C);
    memset(o + (H + 1) * Wb * C, 0, sizeof(uint16_t) * Wb * C);
    for (long y = 1; y <= H; y++) {
        memset(o + (y * Wb) * C, 0, sizeof(uint16_t) * C);
        memset(o + (y * Wb + W + 1) * C, 0, sizeof(uint16_t) * C);
    }
}

/* conv: x buffer (Hb, Wb, Cp) bf16; output pixel (yo, xo), tap (ky, kx) reads x[yo*s + ky + off][xo*s + kx + off].
 * w packed bf16 [Op/16][k*k][Cp/kc][kc/2][32]; bias float32 [Op]. out: bf16 (Ho + 2Po, Wo + 2Po, Op) (border zeroed
 * when Po) or, with out_f32, float32 (Ho, Wo, Op). res: bf16 with out's shape or NULL. Wo % 16 == 0, Op % 16 == 0,
 * Cp % kc == 0, kc 16 or 32. */
int fa_conv(const uint16_t *x, long Hb, long Wb, long Cp, int k, int s, int off, const uint16_t *w, const float *bias,
            long Op, long Ho, long Wo, void *out, int Po, int out_f32, const uint16_t *res, int relu) {
    (void)Hb;
    if (Wo % 16 || Op % 16) return -1;
    int kc = Cp >= 32 ? 32 : 16;
    if (Cp % kc) return -1;
    /* the output is cut into units of 16 pixels of one row; a work item is two units (two A tiles: the next 16
     * pixels, or the next row's when a row is one unit) x two 16-output blocks (two B tiles) = four accumulators */
    long nxu = Wo / 16, nunit = Ho * nxu, nup = (nunit + 1) / 2;
    int nb = Op % 32 == 0 ? 2 : 1;
    long nchunk = Cp / kc, ntap = (long)k * k, nobp = Op / (16 * nb);
    long bstride = ntap * nchunk * (kc / 2) * 32;          /* elements per 16-output weight block */
    long Wob = Wo + 2 * Po;
    long astride = (long)s * Cp * 2;                        /* bytes between A tile rows */
    if (Po && !out_f32) zero_border((uint16_t *)out, Ho, Wo, Op);
    #pragma omp parallel
    {
        tilecfg_t cfg;
        memset(&cfg, 0, sizeof cfg);
        cfg.palette = 1;
        for (int i = 0; i < 4; i++) { cfg.rows[i] = 16; cfg.colsb[i] = 64; }
        for (int i = 4; i < 6; i++) { cfg.rows[i] = 16; cfg.colsb[i] = kc * 2; }
        for (int i = 6; i < 8; i++) { cfg.rows[i] = kc / 2; cfg.colsb[i] = 64; }
        _tile_loadconfig(&cfg);
        float acc[4][16 * 16] __attribute__((aligned(64)));
        #pragma omp for collapse(2) schedule(static)
        for (long ob = 0; ob < nobp; ob++)
            for (long up = 0; up < nup; up++) {
                const uint16_t *w0 = w + (ob * nb) * bstride, *w1 = w0 + bstride;
                long u0 = 2 * up, y0 = u0 / nxu, x0 = (u0 % nxu) * 16;
                int na = u0 + 1 < nunit ? 2 : 1;
                long y1 = (u0 + 1) / nxu, x1 = ((u0 + 1) % nxu) * 16;
                _tile_zero(0); _tile_zero(1); _tile_zero(2); _tile_zero(3);
                for (long t = 0; t < ntap; t++) {
                    int ky = t / k, kx = t % k;
                    const uint16_t *a0 = x + ((y0 * s + ky + off) * Wb + x0 * s + kx + off) * Cp;
                    const uint16_t *a1 = x + ((y1 * s + ky + off) * Wb + x1 * s + kx + off) * Cp;
                    const uint16_t *b0 = w0 + t * nchunk * (kc / 2) * 32, *b1 = w1 + t * nchunk * (kc / 2) * 32;
                    for (long c = 0; c < nchunk; c++) {
                        _tile_loadd(4, a0 + c * kc, astride);
                        _tile_loadd(6, b0 + c * (kc / 2) * 32, 64);
                        _tile_dpbf16ps(0, 4, 6);
                        if (nb == 2) { _tile_loadd(7, b1 + c * (kc / 2) * 32, 64); _tile_dpbf16ps(1, 4, 7); }
                        if (na == 2) {
                            _tile_loadd(5, a1 + c * kc, astride);
                            _tile_dpbf16ps(2, 5, 6);
                            if (nb == 2) _tile_dpbf16ps(3, 5, 7);
                        }
                    }
                }
                _tile_stored(0, acc[0], 64);
                if (nb == 2) _tile_stored(1, acc[1], 64);
                if (na == 2) { _tile_stored(2, acc[2], 64); if (nb == 2) _tile_stored(3, acc[3], 64); }
                for (int ia = 0; ia < na; ia++)
                    for (int ib = 0; ib < nb; ib++) {
                        const float *A = acc[ia * 2 + ib];
                        long o0 = (ob * nb + ib) * 16, yo = ia ? y1 : y0, xo = ia ? x1 : x0;
                        __m512 bv = _mm512_loadu_ps(bias + o0);
                        for (int r = 0; r < 16; r++) {
                            long xx = xo + r;
                            long pix = (yo + Po) * Wob + xx + Po;
                            __m512 v = _mm512_add_ps(_mm512_load_ps(A + r * 16), bv);
                            if (res) v = _mm512_add_ps(v, bf16_to_f32(_mm256_loadu_si256((const __m256i *)(res + pix * Op + o0))));
                            if (relu) v = _mm512_max_ps(v, _mm512_setzero_ps());
                            if (out_f32) _mm512_storeu_ps((float *)out + (yo * Wo + xx) * Op + o0, v);
                            else _mm256_storeu_si256((__m256i *)((uint16_t *)out + pix * Op + o0), f32_to_bf16(v));
                        }
                    }
            }
        _tile_release();
    }
    return 0;
}

/* x float32 (C, H, W) -> bf16 (H + 2p, W + 2p, C), zero border p (the stem's input) */
int fa_hwc_pad(const float *x, long C, long H, long W, int p, uint16_t *out) {
    long Wb = W + 2 * p;
    memset(out, 0, sizeof(uint16_t) * (H + 2 * p) * Wb * C);
    #pragma omp parallel for schedule(static)
    for (long y = 0; y < H; y++)
        for (long j = 0; j < W; j++) {
            uint16_t *o = out + ((y + p) * Wb + j + p) * C;
            for (long c = 0; c < C; c++) {
                float f = x[(c * H + y) * W + j];
                uint32_t u;
                memcpy(&u, &f, 4);
                o[c] = (uint16_t)((u + 0x7FFF + ((u >> 16) & 1)) >> 16);
            }
        }
    return 0;
}

/* the stem's 7 x 7 / stride 2 patches from xp = fa_hwc_pad(x, p=3): bf16 (Ho, Wo, Kp), K index (ky*7 + kx)*C + c,
 * zero beyond 49 C */
int fa_stem_patch(const uint16_t *xp, long C, long H, long W, long Kp, uint16_t *out) {
    long Ho = (H - 1) / 2 + 1, Wo = (W - 1) / 2 + 1, Wb = W + 6;
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < Ho; i++)
        for (long j = 0; j < Wo; j++) {
            uint16_t *o = out + (i * Wo + j) * Kp;
            for (int ky = 0; ky < 7; ky++)
                memcpy(o + ky * 7 * C, xp + ((2 * i + ky) * Wb + 2 * j) * C, sizeof(uint16_t) * 7 * C);
            memset(o + 49 * C, 0, sizeof(uint16_t) * (Kp - 49 * C));
        }
    return 0;
}

/* 3 x 3 / stride 2 / pad 1 max pool on padded bf16 buffers (H + 2, W + 2, C) -> (Ho + 2, Wo + 2, C). The input is
 * post-ReLU (>= 0), so the zero border acts as -inf and non-negative bf16 values order like their uint16 bits. */
int fa_maxpool(const uint16_t *x, long H, long W, long C, uint16_t *out) {
    long Ho = (H - 1) / 2 + 1, Wo = (W - 1) / 2 + 1, Wb = W + 2, Wob = Wo + 2;
    zero_border(out, Ho, Wo, C);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < Ho; i++)
        for (long j = 0; j < Wo; j++) {
            uint16_t *o = out + ((i + 1) * Wob + j + 1) * C;
            for (long c = 0; c < C; c += 32) {
                __m512i m = _mm512_setzero_si512();
                for (int dy = 0; dy < 3; dy++)
                    for (int dx = 0; dx < 3; dx++)
                        m = _mm512_max_epu16(m, _mm512_loadu_si512(x + ((2 * i + dy) * Wb + 2 * j + dx) * C + c));
                _mm512_storeu_si512(o + c, m);
            }
        }
    return 0;
}

/* nearest x2 up-sampling of x (h + 2, w + 2, Cx) and channel concatenation with skip (2h + 2, 2w + 2, Cs) (or none)
 * -> out (2h + 2, 2w + 2, Cx + Cs), all padded bf16 */
int fa_upcat(const uint16_t *x, long h, long w, long Cx, const uint16_t *skip, long Cs, uint16_t *out) {
    long H = 2 * h, W = 2 * w, Co = Cx + Cs;
    zero_border(out, H, W, Co);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < H; i++)
        for (long j = 0; j < W; j++) {
            uint16_t *o = out + ((i + 1) * (W + 2) + j + 1) * Co;
            const uint16_t *a = x + ((i / 2 + 1) * (w + 2) + j / 2 + 1) * Cx;
            for (long c = 0; c < Cx; c += 32) _mm512_storeu_si512(o + c, _mm512_loadu_si512(a + c));
            if (Cs) {
                const uint16_t *b = skip + ((i + 1) * (W + 2) + j + 1) * Cs;
                for (long c = 0; c < Cs; c += 32) _mm512_storeu_si512(o + Cx + c, _mm512_loadu_si512(b + c));
            }
        }
    return 0;
}
