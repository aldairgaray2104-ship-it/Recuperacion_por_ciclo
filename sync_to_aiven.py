import pymysql
import ssl
import time

# Local MySQL
local_conn = pymysql.connect(
    host='localhost', user='root', password='mysql', database='mysql', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

import os

# Aiven Cloud MySQL
AIVEN_DB_HOST = 'mysql-21306377-bdnegociov1.b.aivencloud.com'
AIVEN_DB_PORT = 24225
AIVEN_DB_USER = 'avnadmin'
AIVEN_DB_PASS = os.environ.get('AIVEN_DB_PASS', '')
AIVEN_DB_NAME = 'procesos'

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

aiven_conn = pymysql.connect(
    host=AIVEN_DB_HOST,
    port=AIVEN_DB_PORT,
    user=AIVEN_DB_USER,
    password=AIVEN_DB_PASS,
    database=AIVEN_DB_NAME,
    ssl=ssl_ctx,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

local_cur = local_conn.cursor()
aiven_cur = aiven_conn.cursor()

# 1. Get CREATE TABLE statement from local MySQL
local_cur.execute("SHOW CREATE TABLE `pagos_b`;")
create_sql = local_cur.fetchone()['Create Table']
print("Local CREATE TABLE SQL retrieved.")

# 2. Create table in Aiven
aiven_cur.execute("DROP TABLE IF EXISTS `pagos_b`;")
aiven_cur.execute(create_sql)
aiven_conn.commit()
print("Table `pagos_b` created in Aiven `procesos` database.")

# 3. Read rows from local MySQL for Month 6 and Month 7 (or all rows if fast)
local_cur.execute("SELECT * FROM `pagos_b` WHERE MONTH(fecha_pago) IN (6, 7);")
rows = local_cur.fetchall()
total_rows = len(rows)
print(f"Migrating {total_rows} rows from local MySQL to Aiven Cloud MySQL (`procesos.pagos_b`)...")

if total_rows > 0:
    cols = list(rows[0].keys())
    col_names = ", ".join([f"`{c}`" for c in cols])
    placeholders = ", ".join(["%s"] * len(cols))
    insert_sql = f"INSERT INTO `pagos_b` ({col_names}) VALUES ({placeholders})"

    batch_size = 2000
    start_time = time.time()
    
    for i in range(0, total_rows, batch_size):
        batch = rows[i:i+batch_size]
        batch_values = [tuple(r[c] for c in cols) for r in batch]
        aiven_cur.executemany(insert_sql, batch_values)
        aiven_conn.commit()
        print(f"  Inserted {min(i+batch_size, total_rows)} / {total_rows} rows...")

    elapsed = time.time() - start_time
    print(f"MIGRATION COMPLETE IN {elapsed:.2f} seconds!")

# 4. Verify count in Aiven
aiven_cur.execute("SELECT COUNT(*) as count FROM `pagos_b`;")
cnt = aiven_cur.fetchone()['count']
print(f"VERIFIED: Aiven `procesos.pagos_b` has {cnt} rows!")

local_conn.close()
aiven_conn.close()
