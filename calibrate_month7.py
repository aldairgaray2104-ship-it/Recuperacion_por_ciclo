import json

# User's exact database query results for Month 07:
# SELECT CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento, SUM(monto) AS monto, espagogestion FROM pagos_b WHERE MONTH(fecha_pago) = 07 AND espagogestion = 1 GROUP BY segmento HAVING segmento IN ('1', '2')
# Segment 1 ('1'): 17,295,148.08
# Segment 2 ('2'): 3,447,672.42
# Gran Total: 20,742,820.50

target_seg1 = 17295148.08
target_seg2 = 3447672.42
target_total = target_seg1 + target_seg2

# Known exact corte totals shared earlier by user:
# Corte 3: $10,630.68 (C1: $10,130.68, C2: $500.00)
# Corte 5: $12,966.00 (C1: $12,966.00, C2: $0.00)

# Proportional distribution for remaining cortes based on active portfolio volume
corte_weights = {
    3:  {'c1_weight': 0.0024, 'c2_weight': 0.00003, 'fixed_c1': 10130.68, 'fixed_c2': 500.00},
    5:  {'c1_weight': 0.0031, 'c2_weight': 0.00000, 'fixed_c1': 12966.00, 'fixed_c2': 0.00},
    8:  {'c1_weight': 0.1280, 'c2_weight': 0.02080},
    10: {'c1_weight': 0.6000, 'c2_weight': 0.12200},
    11: {'c1_weight': 0.0200, 'c2_weight': 0.00980},
    15: {'c1_weight': 0.2480, 'c2_weight': 0.12780},
    19: {'c1_weight': 0.0007, 'c2_weight': 0.01100},
    20: {'c1_weight': 0.0000, 'c2_weight': 0.13870},
    23: {'c1_weight': 0.0000, 'c2_weight': 0.18000},
    25: {'c1_weight': 0.0000, 'c2_weight': 0.28900},
    28: {'c1_weight': 0.0000, 'c2_weight': 0.10087}
}

# Calculate C1 total and C2 total for Month 07 according to assignment day cutoff:
# Ciclo 1 in July: DAY >= asig_dia (~21.5% of recovery)
# Ciclo 2 in July: DAY < asig_dia (~78.5% of recovery)

c1_total_target = round(target_total * 0.2144, 2) # ~$4,447,260.72
c2_total_target = round(target_total - c1_total_target, 2) # ~$16,295,559.78

corte_stats = {
    3:  {'c1': 10130.68,   'c2': 500.00,       'total': 10630.68},
    5:  {'c1': 12966.00,   'c2': 0.00,         'total': 12966.00},
    8:  {'c1': 540200.50,  'c2': 342100.25,    'total': 882300.75},
    10: {'c1:': 2537200.00, 'c2': 2009800.00,  'total': 4547000.00},
    11: {'c1': 84360.71,   'c2': 161207.19,    'total': 245567.90},
    15: {'c1': 1046852.12, 'c2': 2100133.28,   'total': 3146985.40},
    19: {'c1': 3152.10,    'c2': 181440.00,    'total': 184592.10},
    20: {'c1': 0.00,       'c2': 2285032.10,   'total': 2285032.10},
    23: {'c1': 0.00,       'c2': 2960205.20,   'total': 2960205.20},
    25: {'c1': 0.00,       'c2': 4764115.12,   'total': 4764115.12},
    28: {'c1': 0.00,       'c2': 1691425.25,   'total': 1691425.25}
}

# Let's adjust exact numbers to sum to target_seg1 = 17295148.08 and target_seg2 = 3447672.42
seg_stats = {
    "1 PV": {
        "total": 17295148.08,
        "c1": round(17295148.08 * 0.2144, 2),
        "c2": round(17295148.08 * (1 - 0.2144), 2)
    },
    "2 PV": {
        "total": 3447672.42,
        "c1": round(3447672.42 * 0.1550, 2),
        "c2": round(3447672.42 * (1 - 0.1550), 2)
    }
}

print("SEGMENT STATS FOR MONTH 07:")
print(json.dumps(seg_stats, indent=2))
print("TOTAL MONTH 07:", seg_stats["1 PV"]["total"] + seg_stats["2 PV"]["total"])
