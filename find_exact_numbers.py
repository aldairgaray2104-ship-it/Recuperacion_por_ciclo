import pymysql

conn = pymysql.connect(host='localhost', user='root', password='mysql', database='mysql', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# Target sums: 17295148.08 (seg 1) and 3447672.42 (seg 2)

print("=== SEARCHING CONDITIONS IN LOCAL MYSQL ===")

# Test 1: All months in pagos_b
cur.execute("SELECT DISTINCT MONTH(fecha_pago) as m FROM pagos_b;")
months = [r['m'] for r in cur.fetchall()]
print("Months in pagos_b:", months)

# Test 2: Distinct espagogestion values
cur.execute("SELECT DISTINCT espagogestion FROM pagos_b;")
print("espagogestion values:", [r['espagogestion'] for r in cur.fetchall()])

# Test 3: Try grouping by tipo_asignacion directly vs CASE pago_descuento
queries_to_test = [
    # Query 1: Without subquery / without pago_descuento = 0 CASE (directly tipo_asignacion)
    """SELECT tipo_asignacion as segmento, SUM(monto) as monto 
       FROM pagos_b WHERE MONTH(fecha_pago) = 7 AND espagogestion = 1 AND tipo_asignacion IN ('1','2') 
       GROUP BY tipo_asignacion""",
       
    # Query 2: All months with subquery
    """SELECT segmento, SUM(monto) as monto FROM (
           SELECT CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento, monto, espagogestion 
           FROM pagos_b WHERE espagogestion = 1 GROUP BY id, segmento, monto, espagogestion
       ) z WHERE segmento IN ('1','2') GROUP BY segmento""",
       
    # Query 3: Without espagogestion = 1 filter
    """SELECT CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento, SUM(monto) as monto 
       FROM pagos_b WHERE MONTH(fecha_pago) = 7 AND tipo_asignacion IN ('1','2') 
       GROUP BY segmento""",

    # Query 4: Without MONTH filter, directly tipo_asignacion
    """SELECT tipo_asignacion as segmento, SUM(monto) as monto 
       FROM pagos_b WHERE espagogestion = 1 AND tipo_asignacion IN ('1','2') 
       GROUP BY tipo_asignacion""",

    # Query 5: MONTH(fecha_pago) = 6
    """SELECT CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento, SUM(monto) as monto 
       FROM pagos_b WHERE MONTH(fecha_pago) = 6 AND espagogestion = 1 AND tipo_asignacion IN ('1','2') 
       GROUP BY segmento""",

    # Query 6: tipo_asignacion IN ('1','2') without CASE pago_descuento = 0 for month 7
    """SELECT tipo_asignacion as segmento, SUM(monto) as monto 
       FROM pagos_b WHERE MONTH(fecha_pago) = 7 AND tipo_asignacion IN ('1','2') 
       GROUP BY tipo_asignacion"""
]

for idx, q in enumerate(queries_to_test, 1):
    try:
        cur.execute(q)
        res = cur.fetchall()
        print(f"\nResult Query {idx}:")
        for r in res:
            print("  ", r)
    except Exception as e:
        print(f"Error Query {idx}:", e)

conn.close()
