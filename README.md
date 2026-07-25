# The Index of Perspective Fragmentation (IFP)

An automated, comparative co-citation analysis pipeline that measures how fragmented a research field's intellectual structure is — from a Web of Science search query to a named set of "perspectives" and a single comparable fragmentation score.

This repository accompanies the manuscript *"The Index of Perspective Fragmentation: An Automated, Comparative Co-Citation Analysis Across Twenty Research Fields"* (submitted to *Quantitative Science Studies*), which validates the pipeline against a manually constructed co-citation map of the Refrigerated Vehicle Routing Problem (RVRP) literature (Aristizábal Torres et al., 2026, *Frontiers in Research Metrics and Analytics*) and applies it comparatively to 20 research fields.

## Pipeline

1. **Search** — Web of Science, Title (TI) field, exported as Plain Text.
2. **Co-citation network** (`construir_red.py`) — parses cited references, builds a weighted co-citation network, and prunes it toward a fixed target size (~2,500 nodes) so that networks from corpora of very different raw sizes remain comparable.
3. **Community detection** (`clustering.py`) — Louvain modularity optimization + PageRank centrality; computes the Index of Perspective Fragmentation (IFP).
4. **Automated labeling** (`etiquetado_llm.py`) — resolves top-PageRank references to titles via the OpenAlex API and prompts an LLM (Claude) for a short name and description per cluster.
5. **Visualization** (`visualizar.py`, `figura_metodologia.py`, `figura_robustez.py`) — community-aware network layouts and comparative figures.

## Repository structure

```
construir_red.py         Co-citation network construction + size-standardization pruning
clustering.py             Louvain community detection, PageRank, IFP computation
etiquetado_llm.py         LLM-based automated cluster labeling (OpenAlex + Claude)
wos_parser.py              Web of Science plain-text export parser
visualizar.py               Network and comparative-bar-chart figures
figura_metodologia.py    Methodology pipeline diagram
figura_robustez.py         IFP-vs-corpus-size robustness check
exportar_redes_csv.py     Exports pruned networks as portable edge-list CSVs

resultados_ifp.csv          Full results table, all 20 fields (Spanish field names)
resultados_ifp_en.csv     Same, with English field names (used for figures/paper)
etiquetas/                  LLM-generated cluster labels per field (JSON)
redes_csv/                  Pruned co-citation networks as edge lists (source,target,weight)
figuras/                    All figures (network maps, comparative chart, robustness check)
manuscrito/                 Manuscript source (Markdown) and compiled PDF
```

## Data availability

Raw Web of Science exports are **not** redistributed here due to licensing restrictions. The derived co-citation networks (`redes_csv/`, one edge-list CSV per field) are provided so the clustering and indexing steps can be independently replicated from that point onward. Node identifiers are DOIs where available, or normalized reference strings otherwise (see `wos_parser.py`).

## Reproducing a field from scratch

```bash
# 1. Export a Web of Science Title-field search as Plain Text into campos/<field>.txt
# 2. Build and prune the co-citation network
python3 construir_red.py campos/<field>.txt --salida redes/<field>.gpickle --nodos-objetivo 2500

# 3. Run clustering + compute IFP
python3 clustering.py redes/<field>.gpickle --min-tamano-cluster 0.03

# 4. Auto-label clusters (requires an Anthropic API key, see below)
python3 etiquetado_llm.py redes/<field>.gpickle --min-tamano-cluster 0.03 \
    --salida-json etiquetas/<field>.json

# 5. Generate the network figure
python3 visualizar.py red redes/<field>.gpickle figuras/red_<field>.png \
    --etiquetas-json etiquetas/<field>.json
```

The labeling step (`etiquetado_llm.py`) requires an Anthropic API key, either as the `ANTHROPIC_API_KEY` environment variable or in a local `.llm_key` file (never committed — see `.gitignore`).

## Citation

If you use this pipeline, please cite both the present manuscript and the anchor validation study:

> [Manuscript citation — to be completed once published]

> Aristizábal Torres, D., Peñuela Meneses, C. A., Santa Chávez, J. J., & Escobar Falcón, L. M. (2026). Mapping the intellectual structure of the refrigerated vehicle routing problem: Research perspectives and structural knowledge gaps. *Frontiers in Research Metrics and Analytics*, 11, 1817900. https://doi.org/10.3389/frma.2026.1817900

## License

Code: MIT. See individual figures/data for reuse terms.
