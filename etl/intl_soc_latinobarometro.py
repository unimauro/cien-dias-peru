# Calcula % ponderados (wt) para Perú (idenpa=604) desde microdatos Stata de Latinobarómetro 2005-2024.
# Uso: ~/.venvs/cien-dias/bin/python etl/intl_soc_latinobarometro.py <carpeta_con_subcarpetas_por_año> [show]
# Columnas RESULT: año, n, apoyo_democracia(cod 1), satisfaccion(1+2), confianza_gobierno(1+2)
import sys,glob,re,pyreadstat
base=sys.argv[1]
M={2005:('p16st','p18st','p45stc'),2006:('p17st','p21st','p32st_a'),2007:('p9st','p12st','p24st_a'),
2008:('p13st','p22st_a','p31s_ta'),2009:('p10st','p12st_a','p24st_a'),2010:('P10ST','P11ST_A','P18ST_A'),
2011:('P13ST','P14ST_A','P20ST_A'),2013:('P12STGBS','P13TGB_A','P26TGB_B'),2015:('P11STGBS','P12TG_A','P16ST_G'),
2016:('P8STGBS','P9STGBSA','P13STE'),2017:('P8STGBS','P9STGBSC_A','P14ST_E'),2018:('P12STGBS','P13STGBS.A','P15STGBSC.E'),
2020:('p10stgbs','P11STGBS_A','p13st_e'),2023:('P10STGBS','P11STGBS_A','P13ST_E'),2024:('P11STGBS','P12STGBS.A','P14ST.E')}
show=len(sys.argv)>2
for y,(ap,sa,co) in M.items():
    f=[x for x in glob.glob(f"{base}/{y}/*.dta") if re.search(r'esp|Esp|2013\.dta',x)][0]
    try: df,m=pyreadstat.read_dta(f,usecols=None)
    except Exception: df,m=pyreadstat.read_dta(f,encoding='latin1')
    cols={c.lower():c for c in df.columns}
    pc=cols['idenpa']; wc=cols['wt']
    d=df[df[pc]==604]
    out=[y,len(d)]
    for v in (ap,sa,co):
        s=d[v]; w=d[wc]; tot=w.sum()
        dist=w.groupby(s).sum()/tot*100
        if show:
            vl=m.variable_value_labels.get(v,{})
            print(y,v,{k:(vl.get(k,'?')[:25],round(p,1)) for k,p in dist.items()})
        if v==ap: val=dist.get(1,0)
        else: val=dist.get(1,0)+dist.get(2,0)
        out.append(round(val,1))
    print('RESULT',*out)
