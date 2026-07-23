import pymysql
import ssl
import json

import os

AIVEN_DB_HOST = 'mysql-21306377-bdnegociov1.b.aivencloud.com'
AIVEN_DB_PORT = 24225
AIVEN_DB_USER = 'avnadmin'
AIVEN_DB_PASS = os.environ.get('AIVEN_DB_PASS', '')
AIVEN_DB_NAME = 'procesos'

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

conn = pymysql.connect(
    host=AIVEN_DB_HOST,
    port=AIVEN_DB_PORT,
    user=AIVEN_DB_USER,
    password=AIVEN_DB_PASS,
    database=AIVEN_DB_NAME,
    ssl=ssl_ctx,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

sql = """
SELECT 
    z.segmento,
    CASE 
        WHEN DAY(z.fecha_pago) >= c.asig_dia THEN 'Ciclo 1'
        ELSE 'Ciclo 2'
    END AS ciclo,
    SUM(z.monto) AS monto_recuperado,
    COUNT(*) AS total_pagos
FROM (
    SELECT 
        CASE 
            WHEN pago_descuento = 0 THEN 'PREV'
            ELSE tipo_asignacion 
        END AS segmento,
        monto,
        fecha_pago,
        corte,
        espagogestion
    FROM pagos_b 
    WHERE MONTH(fecha_pago) IN (6, 7)
      AND espagogestion = 1
) z
INNER JOIN (
    SELECT 3 AS corte, 4 AS asig_dia UNION ALL
    SELECT 5, 6 UNION ALL
    SELECT 8, 9 UNION ALL
    SELECT 10, 11 UNION ALL
    SELECT 11, 12 UNION ALL
    SELECT 15, 16 UNION ALL
    SELECT 19, 20 UNION ALL
    SELECT 20, 21 UNION ALL
    SELECT 23, 24 UNION ALL
    SELECT 25, 26 UNION ALL
    SELECT 28, 29
) c ON z.corte = c.corte
WHERE z.segmento IN ('1', '2')
GROUP BY z.segmento, CASE WHEN DAY(z.fecha_pago) >= c.asig_dia THEN 'Ciclo 1' ELSE 'Ciclo 2' END
ORDER BY z.segmento, ciclo;
"""

cur.execute(sql)
res = cur.fetchall()
print("QUERY RESULTS ON AIVEN `procesos.pagos_b`:")
for r in res:
    print(r)

# Detailed Corte Breakdown from Aiven
sql_corte = """
SELECT 
    c.corte,
    c.asig_dia,
    SUM(CASE WHEN DAY(z.fecha_pago) >= c.asig_dia THEN z.monto ELSE 0 END) AS c1,
    SUM(CASE WHEN DAY(z.fecha_pago) < c.asig_dia THEN z.monto ELSE 0 END) AS c2,
    SUM(z.monto) AS total
FROM (
    SELECT 
        CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento,
        monto, fecha_pago, corte
    FROM pagos_b 
    WHERE MONTH(fecha_pago) IN (6, 7) AND espagogestion = 1
) z
INNER JOIN (
    SELECT 3 AS corte, 4 AS asig_dia UNION ALL
    SELECT 5, 6 UNION ALL SELECT 8, 9 UNION ALL SELECT 10, 11 UNION ALL
    SELECT 11, 12 UNION ALL SELECT 15, 16 UNION ALL SELECT 19, 20 UNION ALL
    SELECT 20, 21 UNION ALL SELECT 23, 24 UNION ALL SELECT 25, 26 UNION ALL SELECT 28, 29
) c ON z.corte = c.corte
WHERE z.segmento IN ('1', '2')
GROUP BY c.corte, c.asig_dia
ORDER BY c.corte;
"""
cur.execute(sql_corte)
res_corte = cur.fetchall()
print("\nCORTE BREAKDOWN FROM AIVEN `procesos.pagos_b`:")
for r in res_corte:
    print(f"Corte {r['corte']:2d} (Asig {r['asig_dia']:2d}): Total=${r['total']:12,.2f} | C1=${r['c1']:12,.2f} | C2=${r['c2']:12,.2f}")

conn.close()
