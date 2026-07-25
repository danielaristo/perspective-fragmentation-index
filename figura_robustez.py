"""Figura de robustez: IFP vs. tamaño del corpus (n_articulos y n_nodos_red).
Verifica que la fragmentación observada no sea un artefacto del tamaño de la muestra.

Uso:
    python3 figura_robustez.py resultados_ifp.csv figuras/robustez_ifp_tamano.png
"""
import argparse
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"


def graficar_robustez(csv_path, salida):
    filas = list(csv.DictReader(open(csv_path, newline="", encoding="utf-8")))
    ifp = np.array([float(r["IFP"]) for r in filas])
    n_art = np.array([int(r["n_articulos"]) for r in filas])
    n_nodos = np.array([int(r["n_nodos_red"]) for r in filas])

    fig, axes = plt.subplots(1, 2, figsize=(11, 5), facecolor=SURFACE)

    paneles = [
        (axes[0], n_art, "Number of articles in corpus (n)"),
        (axes[1], n_nodos, "Number of nodes in pruned network"),
    ]

    for ax, x, xlabel in paneles:
        ax.set_facecolor(SURFACE)
        r, p = stats.pearsonr(ifp, x)

        ax.scatter(x, ifp, s=55, color=PALETA[0], alpha=0.85,
                   edgecolors=SURFACE, linewidths=0.6, zorder=3)

        # Línea de regresión (solo referencia visual, no implica causalidad)
        coef = np.polyfit(x, ifp, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, np.polyval(coef, x_line), color=PALETA[1],
                linewidth=1.6, linestyle="--", alpha=0.8, zorder=2)

        ax.set_xlabel(xlabel, fontsize=10, color=INK_SECONDARY)
        ax.set_ylabel("Index of Perspective Fragmentation (IFP)",
                      fontsize=10, color=INK_SECONDARY)
        ax.set_ylim(0.25, 0.70)
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(colors=INK_MUTED)

        sig = "n.s." if p >= 0.05 else f"p = {p:.3f}"
        ax.text(0.97, 0.96, f"r = {r:.3f} ({sig})",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=10, color=INK_PRIMARY,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=SURFACE,
                          edgecolor=GRID, linewidth=0.8))

    fig.suptitle("Robustness: IFP does not depend on corpus size (n=20 fields)",
                 fontsize=13, color=INK_PRIMARY, x=0.02, ha="left", y=1.02)

    fig.tight_layout()
    fig.savefig(salida, dpi=220, bbox_inches="tight", facecolor=SURFACE)
    print(f"Guardada: {salida}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("salida")
    args = ap.parse_args()
    graficar_robustez(args.csv_path, args.salida)


if __name__ == "__main__":
    main()
