import pymysql
import json

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='mysql', charset='utf8mb4')
cur = conn.cursor(pymysql.cursors.DictCursor)

# Query payments for both month 6 (June) and month 7 (July)
sql = """
SELECT 
    id,
    pago_descuento,
    monto,
    fecha_pago,
    corte,
    tipo_asignacion,
    espagogestion
FROM pagos_b
WHERE MONTH(fecha_pago) IN (6, 7)
  AND espagogestion = 1
  AND TIPO_ASIGNACION IN ('1', '2')
"""

cur.execute(sql)
rows = cur.fetchall()
print(f"Total rows fetched for Month 6 and Month 7: {len(rows)}")

# Corte definitions from the image
# DIAS C1, DIAS C2, CICLO 1 (DESDE, HASTA), CICLO 2 (DESDE, HASTA)
# For July assignment (Mes 07):
# CICLO 1: desde asig_dia/07/2026 hasta 31/07/2026
# CICLO 2: desde 01/08/2026 hasta (retiro_dia)/08/2026
# For June assignment (Mes 06):
# CICLO 1: desde asig_dia/06/2026 hasta 30/06/2026
# CICLO 2: desde 01/07/2026 hasta (asig_dia - 1)/07/2026  (or retiro_dia in July)

CORTES_CONFIG = {
    3:  {'asig_dia': 4,  'dias_c1': 27, 'dias_c2': 3},
    5:  {'asig_dia': 6,  'dias_c1': 25, 'dias_c2': 5},
    8:  {'asig_dia': 9,  'dias_c1': 22, 'dias_c2': 8},
    10: {'asig_dia': 11, 'dias_c1': 20, 'dias_c2': 10},
    11: {'asig_dia': 12, 'dias_c1': 19, 'dias_c2': 11},
    15: {'asig_dia': 16, 'dias_c1': 15, 'dias_c2': 15},
    19: {'asig_dia': 20, 'dias_c1': 11, 'dias_c2': 19},
    20: {'asig_dia': 21, 'dias_c1': 10, 'dias_c2': 20},
    23: {'asig_dia': 24, 'dias_c1': 7,  'dias_c2': 23},
    25: {'asig_dia': 26, 'dias_c1': 5,  'dias_c2': 25},
    28: {'asig_dia': 29, 'dias_c1': 2,  'dias_c2': 28}
}

# Let's aggregate payments for the July Evaluation Cycle (which includes Ciclo 1 in July AND Ciclo 2 of June in July)
# OR let's evaluate:
# - Payments in July with DAY >= asig_dia => CICLO 1 of July assignment
# - Payments in July with DAY < asig_dia => CICLO 2 of June assignment!
# AND payments in June with DAY >= asig_dia => CICLO 1 of June assignment!

stats_july_eval = {c: {'c1': 0.0, 'c2': 0.0, 'total': 0.0} for c in CORTES_CONFIG.keys()}
stats_by_month = {
    6: {c: {'c1': 0.0, 'c2': 0.0, 'total': 0.0} for c in CORTES_CONFIG.keys()},
    7: {c: {'c1': 0.0, 'c2': 0.0, 'total': 0.0} for c in CORTES_CONFIG.keys()}
}

segment_stats_july_eval = {
    '1 PV': {'c1': 0.0, 'c2': 0.0, 'total': 0.0},
    '2 PV': {'c1': 0.0, 'c2': 0.0, 'total': 0.0}
}

for r in rows:
    pago_desc = float(r['pago_descuento']) if r['pago_descuento'] is not None else 0
    if pago_desc == 0:
        continue # PREV
    
    tipo_asig = str(r['tipo_asignacion']).strip()
    if tipo_asig not in ['1', '2']:
        continue

    seg = f"{tipo_asig} PV"
    corte = int(r['corte'])
    monto = float(r['monto']) if r['monto'] is not None else 0.0
    fecha = str(r['fecha_pago']) # 'YYYY-MM-DD'
    parts = fecha.split('-')
    month = int(parts[1])
    day = int(parts[2])

    cfg = CORTES_CONFIG.get(corte, {'asig_dia': 1})
    asig_dia = cfg['asig_dia']

    if month == 7:
        if day >= asig_dia:
            # Payment in July after assignment => CICLO 1 of July assignment
            stats_july_eval[corte]['c1'] += monto
            segment_stats_july_eval[seg]['c1'] += monto
        else:
            # Payment in July before assignment => CICLO 2 of June assignment!
            stats_july_eval[corte]['c2'] += monto
            segment_stats_july_eval[seg]['c2'] += monto
        stats_july_eval[corte]['total'] += monto
        segment_stats_july_eval[seg]['total'] += monto

    # Also track per month
    is_c1 = (day >= asig_dia)
    if is_c1:
        stats_by_month[month][corte]['c1'] += monto
    else:
        stats_by_month[month][corte]['c2'] += monto
    stats_by_month[month][corte]['total'] += monto

print("\n================ JULIO EVALUATION (JULY C1 + JUNE C2 in July) ================")
print(f"{'Corte':<8} | {'Asig Dia':<8} | {'Ciclo 1 ($)':<15} | {'Ciclo 2 ($)':<15} | {'Total ($)':<15} | {'% C1':<8} | {'% C2':<8}")
print("-" * 85)
for corte in sorted(stats_july_eval.keys()):
    s = stats_july_eval[corte]
    asig = CORTES_CONFIG[corte]['asig_dia']
    tot = s['total']
    pct_c1 = (s['c1'] / tot * 100) if tot > 0 else 0
    pct_c2 = (s['c2'] / tot * 100) if tot > 0 else 0
    print(f"Corte {corte:<2} | Dia {asig:<2}   | ${s['c1']:>13,.2f} | ${s['c2']:>13,.2f} | ${tot:>13,.2f} | {pct_c1:>6.2f}% | {pct_c2:>6.2f}%")

print("\n================ SEGMENT TOTALS (JULY C1 + JUNE C2) ================")
for seg, s in segment_stats_july_eval.items():
    print(f"{seg}: Total=${s['total']:,.2f} | C1=${s['c1']:,.2f} | C2=${s['c2']:,.2f}")

conn.close()
