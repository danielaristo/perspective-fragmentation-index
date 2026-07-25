"""Exporta cada red .gpickle como lista de aristas en CSV (source,target,weight),
formato portátil y seguro para publicar en el repositorio (evita distribuir
pickles de Python, que no deberían deserializarse desde fuentes no confiables).

Uso:
    python3 exportar_redes_csv.py
"""
import csv
import os
import pickle

ENTRADA = "redes"
SALIDA = "redes_csv"

os.makedirs(SALIDA, exist_ok=True)

for archivo in sorted(os.listdir(ENTRADA)):
    if not archivo.endswith(".gpickle"):
        continue
    ruta = os.path.join(ENTRADA, archivo)
    with open(ruta, "rb") as f:
        G = pickle.load(f)

    nombre_base = archivo.replace(".gpickle", "")
    ruta_csv = os.path.join(SALIDA, f"{nombre_base}_edges.csv")
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source", "target", "weight"])
        for u, v, d in G.edges(data=True):
            w.writerow([u, v, d.get("weight", 1)])

    print(f"{archivo}: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas -> {ruta_csv}")
