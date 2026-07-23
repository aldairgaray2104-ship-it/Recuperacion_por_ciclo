import pymysql
import ssl

import os

AIVEN_DB_HOST = 'mysql-21306377-bdnegociov1.b.aivencloud.com'
AIVEN_DB_PORT = 24225
AIVEN_DB_USER = 'avnadmin'
AIVEN_DB_PASS = os.environ.get('AIVEN_DB_PASS', '')

def get_aiven_connection(db=None):
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    return pymysql.connect(
        host=AIVEN_DB_HOST,
        port=AIVEN_DB_PORT,
        user=AIVEN_DB_USER,
        password=AIVEN_DB_PASS,
        database=db,
        ssl=ssl_ctx,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    conn = get_aiven_connection()
    cur = conn.cursor()
    cur.execute("SHOW DATABASES;")
    dbs = [r['Database'] for r in cur.fetchall()]
    print("Databases in Aiven MySQL:", dbs)

    for db in dbs:
        if db in ['information_schema', 'performance_schema', 'sys', 'mysql']:
            continue
        try:
            cur.execute(f"USE `{db}`;")
            cur.execute("SHOW TABLES LIKE 'pagos_b';")
            tbl = cur.fetchone()
            print(f"Database `{db}` -> pagos_b: {tbl}")
        except Exception as e:
            print(f"Error checking `{db}`:", e)

    conn.close()

except Exception as e:
    print("Error:", e)
