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

conn = get_aiven_connection()
cur = conn.cursor()
cur.execute("SHOW DATABASES;")
dbs = [r['Database'] for r in cur.fetchall()]

for db in dbs:
    if db in ['information_schema', 'performance_schema', 'sys']:
        continue
    try:
        cur.execute(f"USE `{db}`;")
        cur.execute("SHOW TABLES;")
        tables = [list(r.values())[0] for r in cur.fetchall()]
        print(f"DB `{db}` tables:", tables)
    except Exception as e:
        print(f"DB `{db}` error:", e)

conn.close()
