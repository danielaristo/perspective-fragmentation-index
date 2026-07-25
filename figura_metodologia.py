"""Diagrama de metodología: pipeline completo del Índice de Fragmentación de Perspectivas.

Uso:
    python3 figura_metodologia.py figuras/diagrama_metodologia.png
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"

ETAPAS = [
    ("1", "Web of Science\nsearch",
     "Title field (TI)\n< 2000 articles", PALETA[0]),
    ("2", "Co-citation\nnetwork",
     "CR extraction\n+ DOI normalization", PALETA[2]),
    ("3", "Pruning to\ntarget size",
     "~2500 nodes\n(automatic min. weight)", PALETA[3]),
    ("4", "Community\ndetection",
     "Louvain + PageRank\n(fixed node order)", PALETA[6]),
    ("5", "Automated\nlabeling",
     "LLM (Claude) on\ntitles via OpenAlex", PALETA[4]),
    ("6", "Fragmentation\nIndex (IFP)",
     "Q + inter-cluster prop.\n+ nº perspectives", PALETA[7]),
]


def graficar_metodologia(salida):
    n = len(ETAPAS)
    fig, ax = plt.subplots(figsize=(15, 3.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    box_w, box_h = 1.85, 1.7
    gap = 0.55
    y0 = 0

    for i, (num, titulo, detalle, color) in enumerate(ETAPAS):
        x0 = i * (box_w + gap)

        box = FancyBboxPatch(
            (x0, y0), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=0, facecolor=color, alpha=0.15, zorder=1,
        )
        ax.add_patch(box)
        border = FancyBboxPatch(
            (x0, y0), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.4, edgecolor=color, facecolor="none", zorder=2,
        )
        ax.add_patch(border)

        # Número de etapa
        ax.text(x0 + 0.18, y0 + box_h - 0.32, num, fontsize=15,
                fontweight="bold", color=color, va="top", ha="left", zorder=3)

        # Título
        ax.text(x0 + box_w / 2, y0 + box_h - 0.62, titulo, fontsize=10.5,
                fontweight="bold", color=INK_PRIMARY, va="top", ha="center",
                linespacing=1.3, zorder=3)

        # Detalle
        ax.text(x0 + box_w / 2, y0 + 0.68, detalle, fontsize=8.3,
                color=INK_SECONDARY, va="top", ha="center",
                linespacing=1.4, zorder=3)

        # Flecha al siguiente
        if i < n - 1:
            arrow = FancyArrowPatch(
                (x0 + box_w + 0.06, y0 + box_h / 2),
                (x0 + box_w + gap - 0.06, y0 + box_h / 2),
                arrowstyle="-|>", mutation_scale=14,
                linewidth=1.4, color=INK_MUTED, zorder=2,
            )
            ax.add_patch(arrow)

    total_w = n * box_w + (n - 1) * gap
    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(-0.3, box_h + 0.3)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.suptitle("Methodological pipeline: from bibliographic corpus to the Index of Perspective Fragmentation",
                 fontsize=12.5, color=INK_PRIMARY, x=0.01, ha="left", y=1.04)

    fig.savefig(salida, dpi=220, bbox_inches="tight", facecolor=SURFACE)
    print(f"Guardada: {salida}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    args = ap.parse_args()
    graficar_metodologia(args.salida)


if __name__ == "__main__":
    main()
