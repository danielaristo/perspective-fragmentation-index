"""Genera las figuras del paper: mapa de red de un campo, y comparativo de IFP.

Uso:
    python3 visualizar.py red redes/rvrp_p2.gpickle figuras/red_rvrp.png
    python3 visualizar.py comparativo resultados_ifp.csv figuras/comparativo_ifp.png
"""
import argparse
import csv
import json
import math
import os
import pickle
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from clustering import detectar_perspectivas, top_referencias_por_cluster

# Paleta categórica validada (colorblind-safe), modo claro — dataviz skill
PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"


def cargar_nombres_llm(etiquetas_json, clusters_sig):
    """Lee etiquetas/<campo>.json (salida de etiquetado_llm.py) y arma
    {cluster: nombre_corto}. Si no existe el archivo o falta un cluster,
    cae de vuelta a 'Perspectiva N'."""
    nombres = {c: f"Perspectiva {c}" for c in clusters_sig}
    if etiquetas_json and os.path.exists(etiquetas_json):
        with open(etiquetas_json, encoding="utf-8") as f:
            datos = json.load(f)
        for entrada in datos:
            c = entrada["cluster"]
            if c in nombres:
                nombres[c] = entrada["nombre"]
    return nombres


def _layout_por_comunidad(H, particion, clusters_sig, radio_global=16.0,
                            radio_local=3.0, seed=42):
    """Layout consciente de comunidades: cada cluster se ancla a un punto
    distinto en un círculo grande, y dentro de cada cluster se hace un
    spring_layout local alrededor de ese ancla. Esto separa visualmente los
    clusters en vez de dejar que las aristas inter-cluster los junten al
    centro (que es lo que pasa con spring_layout global en redes muy
    fragmentadas)."""
    random.seed(seed)
    np.random.seed(seed)

    clusters_ordenados = sorted(clusters_sig)
    n = len(clusters_ordenados)
    anclas = {
        c: np.array([radio_global * math.cos(2 * math.pi * i / n),
                     radio_global * math.sin(2 * math.pi * i / n)])
        for i, c in enumerate(clusters_ordenados)
    }

    pos = {}
    for c in clusters_ordenados:
        nodos_c = [nd for nd in H.nodes if particion[nd] == c]
        subG = H.subgraph(nodos_c)
        if subG.number_of_nodes() == 1:
            pos[nodos_c[0]] = anclas[c]
            continue
        pos_local = nx.spring_layout(subG, k=0.4, iterations=50, weight="weight")
        for nd, p in pos_local.items():
            pos[nd] = anclas[c] + p * radio_local
    return pos, anclas


def graficar_red(red_path, salida, min_tamano_cluster=0.03, titulo=None,
                  etiquetas_json=None, top_n_por_cluster=45):
    with open(red_path, "rb") as f:
        G = pickle.load(f)

    particion, pagerank, clusters_sig, tamanos = detectar_perspectivas(
        G, min_tamano_cluster=min_tamano_cluster
    )
    nombres = cargar_nombres_llm(etiquetas_json, clusters_sig)

    # Solo los nodos más centrales (PageRank) de cada cluster: mostrar los
    # ~2.000 nodos completos es ilegible e innecesario para transmitir la
    # fragmentación — un paper de bibliometría muestra el "backbone".
    top_por_cluster = top_referencias_por_cluster(
        particion, pagerank, clusters_sig, top_n=top_n_por_cluster
    )
    nodos_incluidos = [nodo for c in clusters_sig for nodo, _ in top_por_cluster[c]]
    H = G.subgraph(nodos_incluidos)

    color_por_cluster = {c: PALETA[i % len(PALETA)]
                         for i, c in enumerate(sorted(clusters_sig))}
    colores_nodo = [color_por_cluster[particion[n]] for n in H.nodes]
    tamanos_nodo = [max(15, pagerank.get(n, 0) * 8000) for n in H.nodes]

    pos, anclas = _layout_por_comunidad(H, particion, clusters_sig)

    fig, ax = plt.subplots(figsize=(11, 9), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    # Solo aristas dentro del mismo cluster (las inter-cluster, ya escasas
    # tras filtrar al backbone, solo añaden ruido visual entre anclas lejanas)
    aristas_intra = [(u, v) for u, v in H.edges if particion[u] == particion[v]]
    nx.draw_networkx_edges(H, pos, ax=ax, edgelist=aristas_intra,
                            edge_color=GRID, width=0.6, alpha=0.6)
    nx.draw_networkx_nodes(H, pos, ax=ax, node_color=colores_nodo,
                            node_size=tamanos_nodo, linewidths=0.5,
                            edgecolors=SURFACE, alpha=0.95)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")

    # Etiqueta directa (nombre real) debajo de cada blob de cluster, envuelta
    # en varias líneas para que no se solape con el cluster vecino
    import textwrap
    radio_local = 3.0
    for c in sorted(clusters_sig):
        etiqueta = "\n".join(textwrap.wrap(nombres[c], width=18))
        pos_label = anclas[c] + np.array([0, -radio_local * 1.5])
        ax.annotate(etiqueta, pos_label, ha="center", va="top",
                    fontsize=8, color=INK_PRIMARY, fontweight="bold",
                    linespacing=1.3)

    handles = [plt.Line2D([0], [0], marker="o", color="none",
                           markerfacecolor=color_por_cluster[c], markersize=9,
                           label=f"{nombres[c]} ({tamanos[c]} refs)")
               for c in sorted(clusters_sig)]
    ax.legend(handles=handles, loc="upper left", frameon=False,
              fontsize=8.5, labelcolor=INK_SECONDARY,
              bbox_to_anchor=(1.01, 1.0))

    if titulo:
        ax.set_title(titulo, fontsize=13, color=INK_PRIMARY, loc="left", pad=12)

    os.makedirs(os.path.dirname(salida), exist_ok=True)
    fig.savefig(salida, dpi=220, bbox_inches="tight", facecolor=SURFACE)
    print(f"Guardada: {salida}")


def graficar_comparativo(csv_path, salida):
    filas = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            filas.append(row)

    filas.sort(key=lambda r: float(r["IFP"]))
    campos = [r["campo"] for r in filas]
    ifps = [float(r["IFP"]) for r in filas]

    fig, ax = plt.subplots(figsize=(9, max(3, 0.5 * len(filas) + 1)), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    y_pos = range(len(campos))
    barras = ax.barh(y_pos, ifps, color=PALETA[0], height=0.55)

    for i, v in enumerate(ifps):
        ax.text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=9, color=INK_PRIMARY)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(campos, fontsize=10, color=INK_SECONDARY)
    ax.set_xlabel("Index of Perspective Fragmentation (IFP)",
                  fontsize=10, color=INK_SECONDARY)
    ax.set_xlim(0, 1)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK_MUTED)
    ax.tick_params(axis="x", colors=INK_MUTED)
    ax.tick_params(axis="y", length=0)

    ax.set_title("Perspective fragmentation by research field",
                 fontsize=13, color=INK_PRIMARY, loc="left", pad=12)

    os.makedirs(os.path.dirname(salida), exist_ok=True)
    fig.savefig(salida, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    print(f"Guardada: {salida}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="modo", required=True)

    p1 = sub.add_parser("red")
    p1.add_argument("red_path")
    p1.add_argument("salida")
    p1.add_argument("--min-tamano-cluster", type=float, default=0.03)
    p1.add_argument("--titulo", default=None)
    p1.add_argument("--etiquetas-json", default=None,
                     help="JSON de etiquetado_llm.py con los nombres reales de cada cluster")
    p1.add_argument("--top-n-por-cluster", type=int, default=45,
                     help="Nº de nodos más centrales (PageRank) a graficar por cluster")

    p2 = sub.add_parser("comparativo")
    p2.add_argument("csv_path")
    p2.add_argument("salida")

    args = ap.parse_args()
    if args.modo == "red":
        graficar_red(args.red_path, args.salida, args.min_tamano_cluster, args.titulo,
                     args.etiquetas_json, args.top_n_por_cluster)
    else:
        graficar_comparativo(args.csv_path, args.salida)


if __name__ == "__main__":
    main()
