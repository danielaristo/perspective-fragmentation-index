"""Genera copias en inglés de las etiquetas usadas en las figuras del paper
(solo el campo 'nombre', que es lo único que aparece en las figuras)."""
import json

TRADUCCIONES = {
    "etiquetas/rvrp_titulo.json": {
        "VRP clásico con ventanas de tiempo (perecederos)":
            "Classical VRP with time windows (perishables)",
        "Huella de carbono en logística general":
            "General carbon-footprint logistics",
        "VRP verde en cadena de frío (emisiones de carbono)":
            "Green cold-chain VRP (carbon emissions)",
        "Problema de Ruteo de Inventarios (IRP) para perecederos":
            "Inventory Routing Problem (IRP) for perishables",
        "Localización-Inventario-Ruteo integrado (LIRP)":
            "Integrated Location-Inventory-Routing (LIRP)",
        "Contaminación microbiana de productos frescos":
            "Microbial contamination of fresh produce",
    },
    "etiquetas/rvrp_control_topico.json": {
        "Ruteo de vehículos en logística de frío bajo en carbono":
            "Low-carbon cold-chain vehicle routing",
        "Ruteo de vehículos para alimentos perecederos":
            "Vehicle routing for perishable food",
        "Ruteo de vehículos verde y multicompartimento":
            "Green, multi-compartment vehicle routing",
        "Producción-Inventario-Ruteo integrado (PIRP)":
            "Integrated Production-Inventory-Routing (PIRP)",
        "Inventory Routing Problem (IRP) clásico y colaborativo":
            "Classical and collaborative Inventory Routing Problem (IRP)",
        "Metaheurísticas para problemas de ruteo de vehículos":
            "Metaheuristics for vehicle routing problems",
        "Problema integrado de localización-ruteo-inventario":
            "Integrated location-routing-inventory problem",
    },
    "etiquetas/cadena_suministro.json": {
        "Fundamentos teóricos de la resiliencia (2005-2014)":
            "Theoretical foundations of resilience (2005-2014)",
        "Tradición de gestión de riesgos (2004-2015)":
            "Risk management tradition (2004-2015)",
        "Ola cuantitativa: COVID-19 e Industria 4.0 (2018-2020)":
            "Quantitative wave: COVID-19 and Industry 4.0 (2018-2020)",
    },
    "etiquetas/movilidad_urbana.json": {
        "Calidad y accesibilidad del transporte público":
            "Public transport quality and accessibility",
        "Integración de políticas de transporte sostenible":
            "Integration of sustainable transport policies",
        "Diseño y optimización de redes de transporte público":
            "Design and optimization of public transport networks",
        "Transporte público gratuito y políticas tarifarias":
            "Free public transport and fare policies",
        "Planes de movilidad urbana sostenible":
            "Sustainable urban mobility plans",
        "Gobernanza institucional del transporte público":
            "Institutional governance of public transport",
        "Integración tarifaria y uso del transporte público":
            "Fare integration and public transport usage",
        "Análisis de movilidad con datos masivos":
            "Mobility analysis with big data",
        "Justicia social y equidad en el transporte":
            "Social justice and equity in transport",
        "Factores psicológicos en elección de transporte":
            "Psychological factors in transport choice",
        "Análisis envolvente de datos (DEA) aplicado":
            "Applied Data Envelopment Analysis (DEA)",
        "Decisión multicriterio para transporte sostenible":
            "Multi-criteria decision-making for sustainable transport",
    },
}

for ruta, mapa in TRADUCCIONES.items():
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    faltantes = []
    for entrada in datos:
        nombre_es = entrada["nombre"]
        if nombre_es in mapa:
            entrada["nombre"] = mapa[nombre_es]
        else:
            faltantes.append(nombre_es)
    if faltantes:
        print(f"AVISO: sin traducción en {ruta}: {faltantes}")
    ruta_en = ruta.replace(".json", "_en.json")
    with open(ruta_en, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"Guardado: {ruta_en}")
