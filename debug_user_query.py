import pymysql
import ssl

import os

AIVEN_DB_HOST = 'mysql-21306377-bdnegociov1.b.aivencloud.com'
AIVEN_DB_PORT = 24225
AIVEN_DB_USER = 'avnadmin'
AIVEN_DB_PASS = os.environ.get('AIVEN_DB_PASS', '')
AIVEN_DB_NAME = 'procesos'

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Test local MySQL
try:
    conn_loc = pymysql.connect(host='localhost', user='root', password='mysql', database='mysql', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur_loc = conn_loc.cursor()
    print("=== TESTING LOCAL MYSQL `pagos_b` ===")
    
    # Base query 1: MONTH(fecha_pago) = 7
    cur_loc.execute("""
        SELECT 
            CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento,
            SUM(monto) AS monto
        FROM pagos_b 
        WHERE MONTH(fecha_pago) = 7 AND espagogestion = 1 AND TIPO_ASIGNACION IN ('1','2')
        GROUP BY segmento;
    """)
    for r in cur_loc.fetchall():
        print("  Month 7:", r)

    # Base query 2: MONTH(fecha_pago) IN (6, 7)
    cur_loc.execute("""
        SELECT 
            CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento,
            SUM(monto) AS monto
        FROM pagos_b 
        WHERE MONTH(fecha_pago) IN (6, 7) AND espagogestion = 1 AND TIPO_ASIGNACION IN ('1','2')
        GROUP BY segmento;
    """)
    for r in cur_loc.fetchall():
        print("  Month 6 & 7:", r)

    conn_loc.close()
except Exception as e:
    print("Local DB error:", e)

# Test Aiven MySQL
try:
    conn_aiven = pymysql.connect(host=AIVEN_DB_HOST, port=AIVEN_DB_PORT, user=AIVEN_DB_USER, password=AIVEN_DB_PASS, database=AIVEN_DB_NAME, ssl=ssl_ctx, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur_aiven = conn_aiven.cursor()
    print("\n=== TESTING AIVEN MYSQL `procesos.pagos_b` ===")
    
    # Try different queries on Aiven
    queries = {
        "Month 7": "WHERE MONTH(fecha_pago) = 7 AND espagogestion = 1 AND TIPO_ASIGNACION IN ('1','2')",
        "Month 6 & 7": "WHERE MONTH(fecha_pago) IN (6, 7) AND espagogestion = 1 AND TIPO_ASIGNACION IN ('1','2')",
        "No month filter": "WHERE espagogestion = 1 AND TIPO_ASIGNACION IN ('1','2')",
        "pago_descuento!=0": "WHERE espagogestion = 1 AND pago_descuento != 0 AND TIPO_ASIGNACION IN ('1','2')",
    }
    
    for name, q in queries.items():
        sql = f"""
            SELECT 
                CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento,
                SUM(monto) AS monto
            FROM pagos_b 
            {q}
            GROUP BY segmento;
        """
        cur_aiven.execute(sql)
        res = cur_aiven.fetchall()
        print(f"\nQuery ({name}):")
        for r in res:
            print("  ", r)

    conn_aiven.close()
except Exception as e:
    print("Aiven DB error:", e)
