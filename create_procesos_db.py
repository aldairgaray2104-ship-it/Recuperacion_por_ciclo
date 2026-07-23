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
    cur.execute("CREATE DATABASE IF NOT EXISTS `procesos`;")
    print("CREATE DATABASE `procesos` executed successfully!")
    cur.execute("USE `procesos`;")
    print("Switched to database `procesos`!")
    conn.close()
except Exception as e:
    print("Error creating database procesos:", e)
