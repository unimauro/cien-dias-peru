"""Dosis COVID-19 aplicadas (MINSA, vía espejo OWID que cita datosabiertos.gob.pe/dataset/vacunacion).
Uso: python3 -I resultados_vacunas.py <out.json>   (solo stdlib)"""
import csv, io, json, sys, urllib.request
from datetime import date, timedelta
URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/Peru.csv"
rows = {r["date"]: r for r in csv.DictReader(io.StringIO(urllib.request.urlopen(URL, timeout=120).read().decode()))}
def tot(d, k="total_vaccinations"):
    return int(float(rows[str(d)][k]))
ini, fin = date(2021, 7, 28), date(2021, 11, 5)
pre_ini = ini - timedelta(days=100)
out = {
 "fuente": URL,
 "dosis_100_dias_previos": tot(ini - timedelta(days=1)) - tot(pre_ini - timedelta(days=1)),
 "dosis_100_dias_gobierno": tot(fin) - tot(ini - timedelta(days=1)),
 "completos_27jul": tot(ini - timedelta(days=1), "people_fully_vaccinated"),
 "completos_5nov": tot(fin, "people_fully_vaccinated"),
 "acumulado_27jul": tot(ini - timedelta(days=1)), "acumulado_5nov": tot(fin),
 "serie_mensual_acumulado": [[m, tot(max(d for d in rows if d.startswith(m)))] for m in
     ["2021-04","2021-05","2021-06","2021-07","2021-08","2021-09","2021-10","2021-11"]],
}
json.dump(out, open(sys.argv[1], "w"), indent=1); print(out)
