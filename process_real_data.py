import json

with open('real_payments.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

# Corte Assignment Days Mapping (Image 1)
CORTES_ASIG = {
    3: 4,
    5: 6,
    8: 9,
    10: 11,
    11: 12,
    15: 16,
    19: 20,
    20: 21,
    23: 24,
    25: 26,
    28: 29
}

# Aggregate metrics
segment_totals = {}
corte_totals = {}
payments_clean = []

for r in rows:
    pago_desc = r['pago_descuento']
    tipo_asig = str(r['tipo_asignacion']).strip()
    
    # Segment logic from user's SQL query:
    # case when pago_descuento = 0 then 'PREV' else tipo_asignacion end
    # filtered by WHERE segmento IN ('1', '2')
    if pago_desc == 0:
        continue # PREV filtered out
    if tipo_asig not in ['1', '2']:
        continue

    segmento = f"{tipo_asig} PV"
    corte = int(r['corte'])
    monto = float(r['monto'])
    fecha_str = str(r['fecha_pago']) # 'YYYY-MM-DD'
    day_of_month = int(fecha_str.split('-')[2])
    
    asig_dia = CORTES_ASIG.get(corte, 1)
    is_c1 = (day_of_month >= asig_dia)
    ciclo = 'Ciclo 1' if is_c1 else 'Ciclo 2'

    # Track Segment Stats
    if segmento not in segment_totals:
        segment_totals[segmento] = {'total': 0.0, 'c1': 0.0, 'c2': 0.0, 'count_c1': 0, 'count_c2': 0}
    segment_totals[segmento]['total'] += monto
    if is_c1:
        segment_totals[segmento]['c1'] += monto
        segment_totals[segmento]['count_c1'] += 1
    else:
        segment_totals[segmento]['c2'] += monto
        segment_totals[segmento]['count_c2'] += 1

    # Track Corte Stats
    if corte not in corte_totals:
        corte_totals[corte] = {'corte': corte, 'asig_dia': asig_dia, 'total': 0.0, 'c1': 0.0, 'c2': 0.0, 'count': 0}
    corte_totals[corte]['total'] += monto
    corte_totals[corte]['count'] += 1
    if is_c1:
        corte_totals[corte]['c1'] += monto
    else:
        corte_totals[corte]['c2'] += monto

    payments_clean.append({
        'corte': corte,
        'segmento': segmento,
        'monto': round(monto, 2),
        'fecha_pago': fecha_str,
        'day': day_of_month,
        'isCiclo1': is_c1
    })

print("=== REAL SEGMENT METRICS ===")
for seg, s in segment_totals.items():
    print(f"Segment {seg}: Total=${s['total']:,.2f} | C1=${s['c1']:,.2f} | C2=${s['c2']:,.2f}")

print("\n=== REAL CORTE METRICS ===")
for corte in sorted(corte_totals.keys()):
    c = corte_totals[corte]
    print(f"Corte {corte:2d} (Asig {c['asig_dia']:2d}): Total=${c['total']:12,.2f} | C1=${c['c1']:12,.2f} | C2=${c['c2']:12,.2f} | Count={c['count']}")

# Save summary json
summary_data = {
    'segment_totals': segment_totals,
    'corte_totals': corte_totals,
    'total_rows': len(payments_clean)
}

with open('real_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary_data, f, indent=2)

print("\nSaved real_summary.json!")
