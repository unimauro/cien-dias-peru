#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma research/performance.json a partir de:
 - etl/cache/mef_sector_<año>_<ap>.json (performance_mef_sectores.py, Consulta Amigable MEF)
 - etl/cache/performance_web.json (datos verificados a mano/por búsqueda web con URL: obras
   paralizadas, conflictos, rotación, otros, caveats extra)
"""
import json, os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "research", "performance.json")
CA_URL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx"
GOB = {2006: "Alan García (2do)", 2011: "Ollanta Humala", 2016: "Pedro Pablo Kuczynski",
       2021: "Pedro Castillo", 2026: "Keiko Fujimori"}


def sector_rows(d):
    out = []
    for lab, v in d["sectores"].items():
        if v["pim"] <= 0:
            continue
        nmes = len(v.get("dev_mes", {}))
        out.append({
            "sector": lab.split(":", 1)[1].strip() if ":" in lab else lab,
            "codigo": lab.split(":", 1)[0].strip(),
            "pim": round(v["pim"], 0),
            "devengado": round(v["dev_ene_oct"], 0),
            "pct": round(100 * v["dev_ene_oct"] / v["pim"], 1),
            "devengado_ago_oct": round(v["dev_ago_oct"], 0),
            "pct_ago_oct": round(100 * v["dev_ago_oct"] / v["pim"], 1),
            "devengado_anual": round(v["devengado_total"], 0),
            "meses_con_dato": nmes,
            "fuente_url": CA_URL,
            "confianza": "alta" if nmes else "media",
        })
    return sorted(out, key=lambda r: -r["pct"])


def main():
    res = {"meta": {"descripcion": "Desempeño estatal en los primeros 100 días (28-jul a 5-nov). "
                    "Ejecución = devengado acumulado ene-oct / PIM, Gobierno Nacional, por sector.",
                    "gobiernos": GOB, "generado": __import__("datetime").date.today().isoformat()},
           "ejecucion_sectorial": {}, "ejecucion_sectorial_proyectos": {}, "ranking": {},
           "totales_gobierno_nacional": {}}
    for f in sorted(glob.glob(os.path.join(CACHE, "mef_sector_*.json"))):
        d = json.load(open(f))
        y, ap = str(d["anio"]), d["ap"]
        if not d.get("sectores"):
            continue
        rows = sector_rows(d)
        key = "ejecucion_sectorial" if ap == "ActProy" else "ejecucion_sectorial_proyectos"
        res[key][y] = rows
        pim = sum(r["pim"] for r in rows); dev = sum(r["devengado"] for r in rows)
        res["totales_gobierno_nacional"].setdefault(y, {})[ap] = {
            "pim": pim, "devengado_ene_oct": dev, "pct": round(100 * dev / pim, 1) if pim else None,
            "n_sectores": len(rows), "consultado": d.get("consultado"),
            "fuente_url": CA_URL, "confianza": "alta"}
        # ranking solo con sectores de PIM >= S/ 50 M (evita ruido de pliegos minúsculos)
        big = [r for r in rows if r["pim"] >= 50e6]
        res["ranking"].setdefault(y, {})[ap] = {
            "mejores_5": [{"sector": r["sector"], "pct": r["pct"]} for r in big[:5]],
            "peores_5": [{"sector": r["sector"], "pct": r["pct"]} for r in big[-5:][::-1]],
            "criterio": "sectores con PIM >= S/ 50 millones"}
    web = os.path.join(CACHE, "performance_web.json")
    w = json.load(open(web)) if os.path.exists(web) else {}
    for k in ("obras_paralizadas", "conflictos", "rotacion", "otros"):
        res[k] = w.get(k, [])
    res["caveats"] = [
        "Fuente de ejecución: Consulta Amigable del MEF (drill-down Año > Nivel de Gobierno E > Sector > Mes). "
        "La API CKAN datastore_search_sql de api.datosabiertos.mef.gob.pe devolvía 404 'Recurso no encontrado' el 7-nov-2026, por eso no se usó.",
        "PIM: la Consulta Amigable no publica el PIM por mes. Para años cerrados (2006/2011/2016/2021) el denominador es el PIM FINAL al 31-dic; "
        "para 2026 es el PIM vigente a la fecha de consulta (~6-7 nov-2026). El PIM final suele ser algo mayor que el PIM a octubre, "
        "por lo que el % de años cerrados tiende a estar levemente subestimado frente a 2026.",
        "Devengado ene-oct = suma de los devengados mensuales de enero a octubre según la fecha de registro en el SIAF; 2026 puede tener ajustes posteriores.",
        "'ejecucion_sectorial' = toda la ejecución (actividades + proyectos); 'ejecucion_sectorial_proyectos' = solo proyectos de inversión (filtro 'Proyecto' de la consulta).",
        "Solo Gobierno Nacional: los gobiernos regionales y locales no se desagregan por sector aquí. Los nombres y códigos de sector cambian entre años (p. ej. ministerios creados después de 2006).",
        "El presupuesto de enero-julio corresponde al gobierno saliente; la columna devengado_ago_oct aproxima lo ejecutado en la ventana de 100 días.",
        "La inversión pública total (genérica 2.6) se calcula en otro archivo del proyecto; aquí solo el desglose sectorial.",
    ] + w.get("caveats", [])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("escrito", OUT, {k: list(v) for k, v in res["ejecucion_sectorial"].items()} if False else "")


if __name__ == "__main__":
    main()
