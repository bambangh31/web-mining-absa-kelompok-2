"""Gambar alur penelitian untuk laporan (results/figures/alur_penelitian.png).

  python src/flow_diagram.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch  # noqa: E402

COLORS = {  # isi, garis
    "data": ("#e8eef7", "#4a6a9a"),
    "manusia": ("#e5f3ea", "#2f8a55"),
    "llm": ("#fbeee0", "#c2701f"),
    "model": ("#efe9f7", "#6a4fa8"),
    "hasil": ("#fdf6d8", "#a08a1c"),
}
GREEN = COLORS["manusia"][1]


def box(ax, x, top, w, h, title, sub, kind):
    """Kotak dengan sisi atas di `top`; judul di atas, keterangan di bawahnya."""
    fill, edge = COLORS[kind]
    ax.add_patch(FancyBboxPatch((x - w / 2, top - h), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                facecolor=fill, edgecolor=edge, linewidth=1.3))
    ax.text(x, top - 0.24, title, ha="center", va="center", fontsize=9, fontweight="bold", color="#222222")
    if sub:
        ax.text(x, top - 0.43, sub, ha="center", va="top", fontsize=7.8, color="#444444", linespacing=1.3)
    return top - h  # sisi bawah


def arrow(ax, x1, y1, x2, y2, dashed=False, color="#555555", rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, linewidth=1.1,
                                 color=color, linestyle=(0, (4, 3)) if dashed else "-",
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=1))


def main(out=Path("results/figures/alur_penelitian.png")):
    fig, ax = plt.subplots(figsize=(8.2, 10.6), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13.6)
    ax.axis("off")
    W = 2.3
    xs = [1.25, 3.75, 6.25, 8.75]

    # 1-3: data
    b1 = box(ax, 5, 13.4, 6.0, 0.95, "1. Scraping ulasan Google Play",
             "39.995 ulasan SATUSEHAT Mobile (1 Mar 2023 - 3 Nov 2026)\nsrc/scrape_reviews.py", "data")
    b2 = box(ax, 5, b1 - 0.35, 6.0, 0.95, "2. Preprocessing",
             "32.843 ulasan bersih, pool unik 32.035\nsrc/preprocess.py", "data")
    b3 = box(ax, 5, b2 - 0.35, 6.0, 0.95, "3. Pembagian data (seed 42, strata rating)",
             "data/annotations/split.csv", "data")
    arrow(ax, 5, b1, 5, b1 - 0.35)
    arrow(ax, 5, b2, 5, b2 - 0.35)

    # Empat kelompok
    top_g = b3 - 0.55
    groups = [("Kalibrasi", "50 ulasan"), ("Latih + validasi", "400 + 100 ulasan"),
              ("Uji (gold_test)", "300; dipakai 150"), ("Silver", "31.185 ulasan")]
    for x, (t, s) in zip(xs, groups):
        bg = box(ax, x, top_g, W, 0.8, t, s, "data")
        arrow(ax, 5, b3, x, top_g)

    # 4-6: pelabelan
    top_l = bg - 0.4
    b4 = box(ax, xs[0], top_l, W, 1.15, "4. Label manual", "oleh Jap, 8 aspek\nlatihan pedoman", "manusia")
    b5a = box(ax, xs[1], top_l, W, 0.85, "5a. Label Gemini", "gemini-3.5-flash-lite", "llm")
    b5b = box(ax, xs[1], b5a - 0.35, W, 1.15, "5b. Verifikasi Jap",
              "125 diperiksa,\n2,5% sel dikoreksi\n→ verified.csv", "manusia")
    b6 = box(ax, xs[2], top_l, W, 1.85, "6. Label uji manual",
             "oleh Jap, tanpa melihat\nlabel Gemini\n= kunci jawaban\n→ final_v1/gold.csv", "manusia")
    for x in xs[:3]:
        arrow(ax, x, bg, x, top_l)
    arrow(ax, xs[1], b5a, xs[1], b5a - 0.35)
    # pedoman dari kalibrasi ke verifikasi dan label uji
    ax.text(xs[0], b4 - 0.25, "pedoman dipakai\nuntuk langkah 5b dan 6", fontsize=7, color=GREEN,
            ha="center", va="top", style="italic")

    # 7: model, B3, 9: analisis versi
    top_m = b5b - 0.5
    bb3 = box(ax, xs[0], top_m, W, 1.2, "B3-Gemini", "dipakai langsung,\ntanpa pelatihan", "llm")
    b7 = box(ax, xs[1], top_m, W, 1.2, "7. Latih model B1",
             "LR / SVM / NB (TF-IDF)\nsetelan dipilih\ndi validasi", "model")
    b9 = box(ax, xs[3], top_m, W, 1.2, "9. Analisis versi",
             "B1-LR melabeli semua\nulasan bersih", "model")
    arrow(ax, xs[1] - W / 2 + 0.25, b5a + 0.1, xs[0] + 0.3, top_m, dashed=True, color=COLORS["llm"][1])
    ax.text(xs[0] - 0.05, top_m + 0.55, "jawaban Gemini\nuntuk ulasan uji", fontsize=7,
            color=COLORS["llm"][1], ha="center", style="italic")
    arrow(ax, xs[1], b5b, xs[1], top_m)
    arrow(ax, xs[3], bg, xs[3], top_m)

    # 8: evaluasi
    top_e = b7 - 0.55
    b8 = box(ax, 3.75, top_e, 6.9, 1.15, "8. Evaluasi pada 150 ulasan uji (src/evaluate.py)",
             "prediksi B1 dan B3 dibandingkan dengan kunci jawaban gold.csv\nF1 pasangan, per aspek, kappa, paired bootstrap",
             "model")
    arrow(ax, xs[0], bb3, xs[0], top_e)
    arrow(ax, xs[1], b7, xs[1], top_e)
    arrow(ax, xs[2], b6, xs[2], top_e, color=GREEN)
    ax.text(xs[2] + 0.12, (b6 + top_e) / 2, "kunci\njawaban", fontsize=7, color=GREEN, ha="left",
            va="center", style="italic")

    # RQ
    top_r = b8 - 0.55
    box(ax, 3.75, top_r, 6.9, 0.95, "RQ1 dan RQ2 (bagian 10.7-10.10)",
        "kesepakatan label Gemini dan manusia, tingkat koreksi; model terbaik", "hasil")
    box(ax, xs[3], top_r, W, 0.95, "RQ3 (10.11)", "keluhan per aspek\ndan per versi", "hasil")
    arrow(ax, 3.75, b8, 3.75, top_r)
    arrow(ax, xs[3], b9, xs[3], top_r)

    ax.legend(handles=[Patch(facecolor=COLORS[k][0], edgecolor=COLORS[k][1], label=lab) for k, lab in
                       [("data", "Data"), ("manusia", "Label manusia"), ("llm", "LLM (Gemini)"),
                        ("model", "Model dan evaluasi"), ("hasil", "Jawaban RQ")]],
              loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=5, frameon=False, fontsize=8)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(out)


if __name__ == "__main__":
    main()
