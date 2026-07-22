import json

with open('real_payments.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

CORTES_ASIG = {
    3: 4, 5: 6, 8: 9, 10: 11, 11: 12, 15: 16, 19: 20, 20: 21, 23: 24, 25: 26, 28: 29
}

# Detailed breakdown: (corte, segmento, is_c1) -> sum_monto
matrix = {}
segment_breakdown = {
    '1 PV': {'total': 0.0, 'c1': 0.0, 'c2': 0.0},
    '2 PV': {'total': 0.0, 'c1': 0.0, 'c2': 0.0}
}
corte_breakdown = {c: {'c1': 0.0, 'c2': 0.0, 'total': 0.0} for c in CORTES_ASIG.keys()}

for r in rows:
    pago_desc = r['pago_descuento']
    tipo_asig = str(r['tipo_asignacion']).strip()
    if pago_desc == 0 or tipo_asig not in ['1', '2']:
        continue

    seg = f"{tipo_asig} PV"
    corte = int(r['corte'])
    monto = float(r['monto'])
    fecha_str = str(r['fecha_pago'])
    day = int(fecha_str.split('-')[2])
    asig_dia = CORTES_ASIG.get(corte, 1)
    is_c1 = (day >= asig_dia)

    segment_breakdown[seg]['total'] += monto
    if is_c1:
        segment_breakdown[seg]['c1'] += monto
        corte_breakdown[corte]['c1'] += monto
    else:
        segment_breakdown[seg]['c2'] += monto
        corte_breakdown[corte]['c2'] += monto
    corte_breakdown[corte]['total'] += monto

    key = (corte, seg, is_c1)
    matrix[key] = matrix.get(key, 0.0) + monto

print("Detailed Segment Breakdown:")
print(json.dumps(segment_breakdown, indent=2))

print("\nDetailed Corte Breakdown:")
print(json.dumps(corte_breakdown, indent=2))

# Save full metrics JS file
js_content = f"""// Real Database Pre-calculated Metrics (From MySQL `pagos_b` - 45,007 rows)
const REAL_DB_SEGMENT_STATS = {json.dumps(segment_breakdown, indent=4)};
const REAL_DB_CORTE_STATS = {json.dumps(corte_breakdown, indent=4)};
"""

with open('real_db_metrics.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("\nSaved real_db_metrics.js successfully!")
