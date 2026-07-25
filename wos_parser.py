"""Parser mínimo para exportaciones de Web of Science en formato "Plain Text" (savedrecs.txt).

Cada registro empieza en una línea "PT ..." y termina en "ER". Los campos son
tags de 2 letras al inicio de línea; las líneas de continuación (mismo campo,
varias entradas: autores, referencias citadas) empiezan con 3 espacios.
"""
import re


def parse_wos_file(path):
    """Devuelve una lista de dicts, uno por artículo, con los campos crudos."""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    records = []
    current = None
    current_tag = None

    for line in lines:
        if not line.strip():
            continue
        if line.startswith("FN ") or line.startswith("VR "):
            continue
        if line.startswith("ER"):
            if current is not None:
                records.append(current)
            current = None
            current_tag = None
            continue
        if line.startswith("PT "):
            current = {}
            current_tag = None
        if current is None:
            continue
        if line[:2].isupper() and line[:2].isalpha() and (len(line) == 2 or line[2] == " "):
            tag = line[:2]
            value = line[3:].strip()
            current_tag = tag
            current.setdefault(tag, [])
            if value:
                current[tag].append(value)
        elif line.startswith("   ") and current_tag:
            current[current_tag].append(line.strip())

    return records


def cited_references(record):
    """Lista de strings de referencias citadas (campo CR) de un registro."""
    return record.get("CR", [])


def articulo_id(record):
    ut = record.get("UT", [""])[0]
    if ut:
        return ut
    ti = " ".join(record.get("TI", [""]))
    py = " ".join(record.get("PY", [""]))
    return f"{ti}|{py}"


_DOI_RE = re.compile(r"DOI\s+(10\.\S+)", re.IGNORECASE)


def normalizar_referencia(ref_str):
    """Clave de identidad para una referencia citada: DOI si existe, si no
    el string completo en mayúsculas/espacios colapsados (mejor esfuerzo)."""
    m = _DOI_RE.search(ref_str)
    if m:
        return "DOI:" + m.group(1).rstrip(",.").lower()
    norm = re.sub(r"\s+", " ", ref_str).strip().upper()
    return norm


if __name__ == "__main__":
    import sys
    recs = parse_wos_file(sys.argv[1])
    print(f"Artículos parseados: {len(recs)}")
    if recs:
        print("Ejemplo de referencias citadas del primer artículo:")
        for r in cited_references(recs[0])[:5]:
            print(" -", r, "->", normalizar_referencia(r))
