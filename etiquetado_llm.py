"""Etiqueta automáticamente cada perspectiva (cluster) usando un LLM.

1. Resuelve los DOIs/referencias top (por PageRank) de cada cluster a títulos
   reales vía OpenAlex.
2. Le pide a Claude un nombre corto + descripción de la perspectiva a partir
   de esos títulos.

Uso:
    python3 etiquetado_llm.py redes/rvrp_p2.gpickle --min-tamano-cluster 0.03
"""
import argparse
import json
import os
import pickle
import re
import time
import urllib.parse
import urllib.request

import anthropic

from clustering import detectar_perspectivas, top_referencias_por_cluster

SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(SCRATCH_DIR, ".llm_key")


def cargar_api_key():
    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            return f.read().strip()
    raise RuntimeError(
        f"No encontré API key. Defínela en ANTHROPIC_API_KEY o en {KEY_FILE}"
    )


def resolver_titulo_openalex(nodo, cache):
    """nodo es 'DOI:10.xxxx/...' o un string de referencia crudo."""
    if nodo in cache:
        return cache[nodo]

    titulo = None
    if nodo.startswith("DOI:"):
        doi = nodo[4:]
        url = (
            f"https://api.openalex.org/works/https://doi.org/{doi}"
            "?select=title,publication_year&mailto=danielaristo@yahoo.com"
        )
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
            anio = data.get("publication_year")
            t = data.get("title")
            if t:
                titulo = f"({anio}) {t}" if anio else t
        except Exception:
            titulo = None
    if titulo is None:
        titulo = nodo  # sin DOI: usamos el string crudo de la referencia
    cache[nodo] = titulo
    time.sleep(0.15)
    return titulo


def construir_prompt(titulos):
    lista = "\n".join(f"- {t}" for t in titulos)
    return (
        "Estos son los títulos de las referencias más centrales (mayor "
        "PageRank) de un cluster de co-citación dentro de un campo de "
        "investigación:\n\n"
        f"{lista}\n\n"
        "En una frase corta (máximo 8 palabras) nombra la perspectiva de "
        "investigación que representa este cluster. Luego, en una segunda "
        "línea, da una descripción de 1 frase (máximo 25 palabras).\n\n"
        "Responde SOLO en este formato exacto:\n"
        "NOMBRE: <nombre corto>\n"
        "DESCRIPCION: <descripción de 1 frase>"
    )


def etiquetar_cluster(client, titulos):
    prompt = construir_prompt(titulos)
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = next(b.text for b in resp.content if b.type == "text")
    nombre_match = re.search(r"NOMBRE:\s*(.+)", texto)
    desc_match = re.search(r"DESCRIPCION:\s*(.+)", texto)
    nombre = nombre_match.group(1).strip() if nombre_match else texto.strip()
    descripcion = desc_match.group(1).strip() if desc_match else ""
    return nombre, descripcion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("red", help="Archivo .gpickle de la red de co-citación")
    ap.add_argument("--min-tamano-cluster", type=float, default=0.03)
    ap.add_argument("--top-n", type=int, default=6,
                     help="Referencias top por cluster a resolver/enviar al LLM")
    ap.add_argument("--salida-json", default=None,
                     help="Ruta para guardar las etiquetas en JSON (ej. etiquetas/rvrp.json)")
    args = ap.parse_args()

    api_key = cargar_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    with open(args.red, "rb") as f:
        G = pickle.load(f)

    particion, pagerank, clusters_sig, tamanos = detectar_perspectivas(
        G, min_tamano_cluster=args.min_tamano_cluster
    )
    top_refs = top_referencias_por_cluster(
        particion, pagerank, clusters_sig, top_n=args.top_n
    )

    cache_titulos = {}
    resultados = []
    for cluster in sorted(clusters_sig):
        print(f"Resolviendo títulos del cluster {cluster}...")
        nodos = [nodo for nodo, _ in top_refs[cluster]]
        titulos = [resolver_titulo_openalex(n, cache_titulos) for n in nodos]

        nombre, descripcion = etiquetar_cluster(client, titulos)
        resultados.append({
            "cluster": cluster,
            "tamano": tamanos[cluster],
            "nombre": nombre,
            "descripcion": descripcion,
            "titulos_muestra": titulos,
        })
        print(f"  Perspectiva {cluster} ({tamanos[cluster]} refs): {nombre}")
        print(f"    {descripcion}")

    if args.salida_json:
        os.makedirs(os.path.dirname(args.salida_json) or ".", exist_ok=True)
        with open(args.salida_json, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"Etiquetas guardadas en {args.salida_json}")

    return resultados


if __name__ == "__main__":
    main()
