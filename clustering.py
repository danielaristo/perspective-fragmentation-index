"""Detección de comunidades (perspectivas) + PageRank + Índice de Fragmentación.

Uso:
    python3 clustering.py redes/rvrp.gpickle --min-tamano-cluster 0.03
"""
import argparse
import pickle
from collections import defaultdict

import community as community_louvain
import networkx as nx


def detectar_perspectivas(G, min_tamano_cluster=0.03, seed=42):
    """Louvain + PageRank. Devuelve (particion, pagerank, clusters_significativos)."""
    particion = community_louvain.best_partition(G, weight="weight", random_state=seed)
    pagerank = nx.pagerank(G, weight="weight")

    tamanos = defaultdict(int)
    for nodo, cluster in particion.items():
        tamanos[cluster] += 1

    n_total = G.number_of_nodes()
    umbral = max(3, int(n_total * min_tamano_cluster))
    clusters_significativos = {c for c, tam in tamanos.items() if tam >= umbral}

    return particion, pagerank, clusters_significativos, tamanos


def top_referencias_por_cluster(particion, pagerank, clusters_significativos, top_n=8):
    por_cluster = defaultdict(list)
    for nodo, cluster in particion.items():
        if cluster in clusters_significativos:
            por_cluster[cluster].append((nodo, pagerank.get(nodo, 0)))
    for cluster in por_cluster:
        por_cluster[cluster].sort(key=lambda x: x[1], reverse=True)
        por_cluster[cluster] = por_cluster[cluster][:top_n]
    return por_cluster


def indice_fragmentacion(G, particion, clusters_significativos):
    """IFP = combinación de modularidad Q, nº de perspectivas significativas,
    y proporción de peso de citación que cruza entre clusters (vs. intra-cluster).
    Cada componente normalizado a [0,1]; el índice final es su promedio.
    """
    modularidad_q = community_louvain.modularity(particion, G, weight="weight")

    peso_intra = 0.0
    peso_inter = 0.0
    for u, v, d in G.edges(data=True):
        w = d.get("weight", 1)
        if particion[u] == particion[v]:
            peso_intra += w
        else:
            peso_inter += w
    peso_total = peso_intra + peso_inter
    proporcion_inter = peso_inter / peso_total if peso_total > 0 else 0.0

    n_perspectivas = len(clusters_significativos)
    # Normalización simple: 1 perspectiva = 0 fragmentación; 8+ perspectivas ~ tope 1.0
    n_perspectivas_norm = min(n_perspectivas / 8, 1.0)

    ifp = (modularidad_q + proporcion_inter + n_perspectivas_norm) / 3
    return {
        "IFP": round(ifp, 4),
        "modularidad_Q": round(modularidad_q, 4),
        "proporcion_citas_inter_cluster": round(proporcion_inter, 4),
        "n_perspectivas_significativas": n_perspectivas,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("red", help="Archivo .gpickle de la red de co-citación")
    ap.add_argument("--min-tamano-cluster", type=float, default=0.03,
                     help="Fracción mínima del total de nodos para contar un cluster (default 3%%)")
    ap.add_argument("--top-n", type=int, default=8, help="Top referencias por cluster a mostrar")
    args = ap.parse_args()

    with open(args.red, "rb") as f:
        G = pickle.load(f)

    particion, pagerank, clusters_sig, tamanos = detectar_perspectivas(
        G, min_tamano_cluster=args.min_tamano_cluster
    )
    top_refs = top_referencias_por_cluster(particion, pagerank, clusters_sig, top_n=args.top_n)
    metricas = indice_fragmentacion(G, particion, clusters_sig)

    print(f"Nodos: {G.number_of_nodes()}  Aristas: {G.number_of_edges()}")
    print(f"Clusters totales detectados: {len(tamanos)}  (significativos: {len(clusters_sig)})")
    print(metricas)
    print()
    for cluster in sorted(clusters_sig):
        print(f"--- Perspectiva {cluster} ({tamanos[cluster]} referencias) ---")
        for nodo, pr in top_refs[cluster]:
            print(f"   [{pr:.4f}] {nodo}")


if __name__ == "__main__":
    main()
