import pymysql
import ssl
import json
import os

AIVEN_DB_HOST = 'mysql-21306377-bdnegociov1.b.aivencloud.com'
AIVEN_DB_PORT = 24225
AIVEN_DB_USER = 'avnadmin'
AIVEN_DB_PASS = os.environ.get('AIVEN_DB_PASS', '')
AIVEN_DB_NAME = 'defaultdb'

def get_aiven_connection():
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    return pymysql.connect(
        host=AIVEN_DB_HOST,
        port=AIVEN_DB_PORT,
        user=AIVEN_DB_USER,
        password=AIVEN_DB_PASS,
        database=AIVEN_DB_NAME,
        ssl=ssl_ctx,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    print(f"Connecting to Aiven Cloud MySQL ({AIVEN_DB_HOST}:{AIVEN_DB_PORT}, database: {AIVEN_DB_NAME})...")
    conn = get_aiven_connection()
    print("SUCCESSFULLY CONNECTED TO AIVEN!")
    cur = conn.cursor()
    
    # Check tables in database 'procesos'
    cur.execute("SHOW TABLES LIKE 'pagos_b';")
    tbl = cur.fetchone()
    print("Table check:", tbl)
    
    # Check count of rows for month 6 and 7 in pagos_b
    sql = """
    SELECT 
        MONTH(fecha_pago) as mes,
        COUNT(*) as total_filas,
        SUM(monto) as total_monto
    FROM pagos_b
    WHERE MONTH(fecha_pago) IN (6, 7)
      AND espagogestion = 1
      AND TIPO_ASIGNACION IN ('1', '2')
    GROUP BY MONTH(fecha_pago);
    """
    cur.execute(sql)
    res = cur.fetchall()
    print("Monthly stats in Aiven `procesos.pagos_b`:")
    for r in res:
        print(r)

    # Let's inspect column names of `pagos_b` to see if there are contención columns or fields
    cur.execute("DESCRIBE pagos_b;")
    cols = cur.fetchall()
    print("\nColumns in `pagos_b`:")
    for c in cols:
        print(f"  {c['Field']} ({c['Type']})")

    conn.close()

except Exception as e:
    print("ERROR connecting to Aiven:", e)
