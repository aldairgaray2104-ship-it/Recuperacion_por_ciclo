import pymysql

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='mysql', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# Search across date ranges in July or June-July
print("=== SEARCHING DATE RANGES AND COMBINATIONS ===")

# Test combinations of MONTH(fecha_pago)
for m in [7, (6,7), (5,6,7)]:
    month_clause = f"MONTH(fecha_pago) = {m}" if isinstance(m, int) else f"MONTH(fecha_pago) IN {m}"
    
    # 1. Standard user query
    sql1 = f"""
    SELECT segmento, SUM(monto) as monto FROM (
        SELECT CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento, monto, espagogestion 
        FROM pagos_b WHERE {month_clause} AND espagogestion = 1
    ) z WHERE segmento IN ('1','2') GROUP BY segmento
    """
    cur.execute(sql1)
    res1 = {r['segmento']: float(r['monto']) for r in cur.fetchall()}
    print(f"Month filter {m} (espagogestion=1):", res1)

    # 2. espagogestion in ('1', 1) or all espagogestion
    sql2 = f"""
    SELECT segmento, SUM(monto) as monto FROM (
        SELECT CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento, monto 
        FROM pagos_b WHERE {month_clause}
    ) z WHERE segmento IN ('1','2') GROUP BY segmento
    """
    cur.execute(sql2)
    res2 = {r['segmento']: float(r['monto']) for r in cur.fetchall()}
    print(f"Month filter {m} (all espagogestion):", res2)

# Check if there are specific date filters (e.g. up to 2026-07-22 or specific cut-off date)
sql_days = """
SELECT 
    DAY(fecha_pago) as d,
    SUM(CASE WHEN tipo_asignacion='1' AND pago_descuento!=0 THEN monto ELSE 0 END) as seg1,
    SUM(CASE WHEN tipo_asignacion='2' AND pago_descuento!=0 THEN monto ELSE 0 END) as seg2
FROM pagos_b
WHERE MONTH(fecha_pago) = 7 AND espagogestion = 1
GROUP BY DAY(fecha_pago)
ORDER BY d;
"""
cur.execute(sql_days)
days_data = cur.fetchall()
print("\nJuly Cumulative Sums by Day (espagogestion=1):")
cum1 = 0
cum2 = 0
for r in days_data:
    cum1 += float(r['seg1'])
    cum2 += float(r['seg2'])
    print(f"  Up to July {r['d']:02d}: Seg 1 = ${cum1:,.2f} | Seg 2 = ${cum2:,.2f}")

conn.close()
