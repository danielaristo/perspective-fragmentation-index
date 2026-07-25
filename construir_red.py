"""Construye la red de co-citación de un campo a partir de una exportación WoS.

Uso:
    python3 construir_red.py campos/rvrp.txt --salida redes/rvrp.gpickle
"""
import argparse
import itertools
import pickle
from collections import Counter

import networkx as nx

from wos_parser import parse_wos_file, cited_references, normalizar_referencia


def construir_red_cocitacion(records, min_peso=1):
    G = nx.Graph()
    conteo_citas = Counter()

    for rec in records:
        refs = [normalizar_referencia(r) for r in cited_references(rec)]
        refs = sorted(set(refs))  # sin duplicados dentro del mismo artículo
        for ref in refs:
            conteo_citas[ref] += 1
        for a, b in itertools.combinations(refs, 2):
            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
            else:
                G.add_edge(a, b, weight=1)

    for nodo in list(G.nodes):
        G.nodes[nodo]["veces_citado"] = conteo_citas[nodo]

    if min_peso > 1:
        aristas_debiles = [(u, v) for u, v, d in G.edges(data=True) if d["weight"] < min_peso]
        G.remove_edges_from(aristas_debiles)
        G.remove_nodes_from(list(nx.isolates(G)))

    return G


def _podar_por_eliminacion(G, min_peso):
    """Copia G y ELIMINA aristas/nodos débiles in-place (no reconstruye el
    grafo desde un generador). Louvain es sensible al orden de inserción de
    nodos, así que hay que preservar el orden original del grafo completo
    para que el resultado sea reproducible entre corridas."""
    H = G.copy()
    aristas_debiles = [(u, v) for u, v, d in H.edges(data=True) if d["weight"] < min_peso]
    H.remove_edges_from(aristas_debiles)
    H.remove_nodes_from(list(nx.isolates(H)))
    return H


def podar_a_nodos_objetivo(G, objetivo=2500, min_peso_max=50):
    """Encuentra el min_peso entero que deja la red más cerca de `objetivo`
    nodos, para que todos los campos queden en un rango de tamaño comparable
    (evita que el IFP se sesgue por el tamaño del corpus, no por la
    estructura real del campo)."""
    mejor_peso, mejor_G, mejor_dist = 1, G, abs(G.number_of_nodes() - objetivo)

    for min_peso in range(2, min_peso_max + 1):
        H = _podar_por_eliminacion(G, min_peso)
        dist = abs(H.number_of_nodes() - objetivo)
        if dist < mejor_dist:
            mejor_peso, mejor_G, mejor_dist = min_peso, H, dist
        if H.number_of_nodes() < objetivo:
            # ya pasamos el objetivo por abajo; pesos mayores solo lo alejan más
            break

    return mejor_peso, mejor_G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="Archivo de exportación WoS (plain text)")
    ap.add_argument("--salida", required=True, help="Ruta de salida .gpickle")
    ap.add_argument("--min-peso", type=int, default=None,
                     help="Peso mínimo de arista a conservar (fijo). Si se omite, "
                          "se autoajusta contra --nodos-objetivo.")
    ap.add_argument("--nodos-objetivo", type=int, default=2500,
                     help="Tamaño de red objetivo (nº de nodos) para autoajustar "
                          "el umbral de poda y hacer los campos comparables entre sí")
    args = ap.parse_args()

    records = parse_wos_file(args.entrada)
    print(f"Artículos leídos: {len(records)}")

    G_crudo = construir_red_cocitacion(records, min_peso=1)
    print(f"Red cruda (sin podar): {G_crudo.number_of_nodes()} nodos, {G_crudo.number_of_edges()} aristas")

    if args.min_peso is not None:
        G = construir_red_cocitacion(records, min_peso=args.min_peso)
        peso_usado = args.min_peso
    else:
        peso_usado, G = podar_a_nodos_objetivo(G_crudo, objetivo=args.nodos_objetivo)

    print(f"Umbral usado: min_peso={peso_usado} (objetivo {args.nodos_objetivo} nodos)")
    print(f"Red de co-citación podada: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

    with open(args.salida, "wb") as f:
        pickle.dump(G, f)
    print(f"Guardada en {args.salida}")


if __name__ == "__main__":
    main()
