/* The segment U-Net's convolutions in float32 without im2col (unet_fast.py): the fallback where AMX is missing
 * (AMD, older Intel, ARM). Portable C with GCC vector extensions, compiled with -march=native, so a vector is a zmm
 * (AVX-512), a ymm (AVX2) or a NEON / SSE register.
 *
 * Activations are NHWC float32 buffers with a 1-pixel zero border (the stem's input: 3). A convolution is an implicit
 * GEMM with a register-blocked micro-kernel: P output pixels of one row x NV vectors of output channels in
 * accumulators; per (tap, input channel) one weight load per vector and one broadcast per pixel. Bias, residual and
 * ReLU are applied before the accumulators are stored. Weights are packed [O / (NV VL)][tap][C][NV VL].
 *
 * The sums run over (tap, c) instead of im2col's (c, tap) order and use FMA: equal to unet.py's pass within float32
 * rounding (test_fastperc.py). */
#include <stdint.h>
#include <string.h>

#if defined(__AVX512F__)          /* 32 registers: 12 x 2 accumulators */
#define VL 16
#define PMAX 12
#define PMID 8
#elif defined(__AVX__)            /* 16 registers: 6 x 2 */
#define VL 8
#define PMAX 6
#define PMID 4
#else
#define VL 4
#define PMAX 4
#define PMID 2
#endif

typedef float vf __attribute__((vector_size(VL * 4)));
typedef int32_t vi __attribute__((vector_size(VL * 4)));
typedef float vfu __attribute__((vector_size(VL * 4), aligned(4)));

int fc_vl(void) { return VL; }

static inline vf vload(const float *p) { return *(const vfu *)p; }
static inline void vstore(float *p, vf v) { *(vfu *)p = v; }
static inline vf vbcast(float a) { return (vf){0} + a; }

/* P pixels (xo .. xo+P-1 of row yo) x NV vectors */
#define KERNEL(P, NV)                                                                                                  \
static inline void kern_##P##_##NV(const float *x, long Wb, long C, int k, int s, int off, const float *wb,           \
                                   long yo, long xo, float *acc) {                                                    \
    vf a[P][NV];                                                                                                       \
    for (int p = 0; p < P; p++) for (int v = 0; v < NV; v++) a[p][v] = vbcast(0.f);                                   \
    for (int ky = 0; ky < k; ky++)                                                                                     \
        for (int kx = 0; kx < k; kx++) {                                                                               \
            const float *xr = x + ((yo * s + ky + off) * Wb + xo * s + kx + off) * C;                                  \
            const float *wt = wb + (long)(ky * k + kx) * C * NV * VL;                                                  \
            for (long c = 0; c < C; c++) {                                                                             \
                vf w[NV];                                                                                              \
                for (int v = 0; v < NV; v++) w[v] = vload(wt + c * NV * VL + v * VL);                                  \
                for (int p = 0; p < P; p++) {                                                                          \
                    float b = xr[p * s * C + c];                                                                       \
                    for (int v = 0; v < NV; v++) a[p][v] += b * w[v];                                                  \
                }                                                                                                      \
            }                                                                                                          \
        }                                                                                                              \
    for (int p = 0; p < P; p++) for (int v = 0; v < NV; v++) vstore(acc + (p * NV + v) * VL, a[p][v]);               \
}
KERNEL(PMAX, 1)
KERNEL(PMAX, 2)
KERNEL(PMID, 1)
KERNEL(PMID, 2)
KERNEL(4, 1)
KERNEL(4, 2)
KERNEL(1, 1)
KERNEL(1, 2)

/* x buffer (Hb, Wb, C); output pixel (yo, xo), tap (ky, kx) reads x[yo*s + ky + off][xo*s + kx + off]. w packed
 * [Op / (nv VL)][k*k][C][nv VL], bias [Op]. out: (Ho + 2Po, Wo + 2Po, Op) (border zeroed when Po); res: out's shape
 * or NULL. Op % VL == 0; nv = 2 when Op % (2 VL) == 0, else 1. */
int fc_conv(const float *x, long Hb, long Wb, long C, int k, int s, int off, const float *w, const float *bias,
            long Op, long Ho, long Wo, float *out, int Po, const float *res, int relu) {
    (void)Hb;
    if (Op % VL) return -1;
    int nv = Op % (2 * VL) == 0 ? 2 : 1;
    long nob = Op / (nv * VL), bstride = (long)k * k * C * nv * VL, Wob = Wo + 2 * Po;
    if (Po) {
        memset(out, 0, sizeof(float) * Wob * Op);
        memset(out + (Ho + 1) * Wob * Op, 0, sizeof(float) * Wob * Op);
        for (long y = 1; y <= Ho; y++) {
            memset(out + (y * Wob) * Op, 0, sizeof(float) * Op);
            memset(out + (y * Wob + Wo + 1) * Op, 0, sizeof(float) * Op);
        }
    }
    #pragma omp parallel for collapse(2) schedule(static)
    for (long ob = 0; ob < nob; ob++)
        for (long yo = 0; yo < Ho; yo++) {
            float acc[PMAX * 2 * VL] __attribute__((aligned(64)));
            const float *wb = w + ob * bstride;
            for (long xo = 0; xo < Wo;) {
                long left = Wo - xo;
                int P = left >= PMAX ? PMAX : left >= PMID ? PMID : left >= 4 ? 4 : 1;
#define CALL(Q) do { if (nv == 2) kern_##Q##_2(x, Wb, C, k, s, off, wb, yo, xo, acc); \
                     else kern_##Q##_1(x, Wb, C, k, s, off, wb, yo, xo, acc); } while (0)
                if (P == PMAX) CALL(PMAX); else if (P == PMID) CALL(PMID); else if (P == 4) CALL(4); else CALL(1);
#undef CALL
                for (int p = 0; p < P; p++) {
                    long pix = (yo + Po) * Wob + xo + p + Po;
                    for (int v = 0; v < nv; v++) {
                        long o0 = (ob * nv + v) * VL;
                        vf a = vload(acc + (p * nv + v) * VL) + vload(bias + o0);
                        if (res) a += vload(res + pix * Op + o0);
                        if (relu) a = (vf)((vi)a & (a > 0.f));
                        vstore(out + pix * Op + o0, a);
                    }
                }
                xo += P;
            }
        }
    return 0;
}

/* x (C, H, W) -> (H + 2p, W + 2p, C), zero border p */
int fc_hwc_pad(const float *x, long C, long H, long W, int p, float *out) {
    long Wb = W + 2 * p;
    memset(out, 0, sizeof(float) * (H + 2 * p) * Wb * C);
    #pragma omp parallel for schedule(static)
    for (long y = 0; y < H; y++)
        for (long j = 0; j < W; j++)
            for (long c = 0; c < C; c++) out[((y + p) * Wb + j + p) * C + c] = x[(c * H + y) * W + j];
    return 0;
}

/* 3 x 3 / stride 2 / pad 1 max pool, padded (H + 2, W + 2, C) -> (Ho + 2, Wo + 2, C); the input is post-ReLU (>= 0),
 * so the zero border acts as -inf */
int fc_maxpool(const float *x, long H, long W, long C, float *out) {
    long Ho = (H - 1) / 2 + 1, Wo = (W - 1) / 2 + 1, Wb = W + 2, Wob = Wo + 2;
    memset(out, 0, sizeof(float) * (Ho + 2) * Wob * C);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < Ho; i++)
        for (long j = 0; j < Wo; j++) {
            float *o = out + ((i + 1) * Wob + j + 1) * C;
            for (long c = 0; c < C; c++) {
                float m = 0.f;
                for (int dy = 0; dy < 3; dy++)
                    for (int dx = 0; dx < 3; dx++) {
                        float v = x[((2 * i + dy) * Wb + 2 * j + dx) * C + c];
                        m = v > m ? v : m;
                    }
                o[c] = m;
            }
        }
    return 0;
}

/* nearest x2 up-sampling of x (h + 2, w + 2, Cx) + channel concatenation with skip (2h + 2, 2w + 2, Cs) (or none) */
int fc_upcat(const float *x, long h, long w, long Cx, const float *skip, long Cs, float *out) {
    long H = 2 * h, W = 2 * w, Co = Cx + Cs;
    memset(out, 0, sizeof(float) * (W + 2) * Co);
    memset(out + (H + 1) * (W + 2) * Co, 0, sizeof(float) * (W + 2) * Co);
    #pragma omp parallel for schedule(static)
    for (long i = 0; i < H; i++) {
        float *row = out + (i + 1) * (W + 2) * Co;
        memset(row, 0, sizeof(float) * Co);
        memset(row + (W + 1) * Co, 0, sizeof(float) * Co);
        for (long j = 0; j < W; j++) {
            float *o = row + (j + 1) * Co;
            memcpy(o, x + ((i / 2 + 1) * (w + 2) + j / 2 + 1) * Cx, sizeof(float) * Cx);
            if (Cs) memcpy(o + Cx, skip + ((i + 1) * (W + 2) + j + 1) * Cs, sizeof(float) * Cs);
        }
    }
    return 0;
}
