import pymysql
import json

db_names = ['mysql', 'telefonia', 'cobranza', 'pagos', 'recuperacion', 'test']
found_db = None

# First find which database contains pagos_b
for db in ['mysql', 'test', 'information_schema']:
    try:
        conn = pymysql.connect(host='localhost', user='root', password='mysql', database=db, charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SHOW DATABASES;")
        all_dbs = [r[0] for r in cur.fetchall()]
        print("Available MySQL DBs:", all_dbs)
        for d in all_dbs:
            try:
                cur.execute(f"USE `{d}`;")
                cur.execute("SHOW TABLES LIKE 'pagos_b';")
                if cur.fetchone():
                    found_db = d
                    print(f"FOUND table 'pagos_b' in database: {found_db}")
                    break
            except Exception as e:
                pass
        conn.close()
        if found_db: break
    except Exception as e:
        print("Connection error:", e)
        break

if found_db:
    conn = pymysql.connect(host='localhost', user='root', password='mysql', database=found_db, charset='utf8mb4')
    cur = conn.cursor(pymysql.cursors.DictCursor)
    
    # Query to fetch all rows for month 07 with espagogestion=1 and TIPO_ASIGNACION in ('1','2')
    sql = """
    SELECT 
        id,
        producto,
        numero_tarjeta,
        numero_cuenta,
        saldo_total,
        pago_descuento,
        monto,
        fecha_pago,
        corte,
        tipo_asignacion,
        despacho,
        espagogestion
    FROM pagos_b
    WHERE MONTH(fecha_pago) = 7
      AND espagogestion = 1
      AND TIPO_ASIGNACION IN ('1', '2')
    """
    cur.execute(sql)
    rows = cur.fetchall()
    print(f"Fetched {len(rows)} rows from database {found_db}.pagos_b")
    
    # Serialize date
    for r in rows:
        r['fecha_pago'] = str(r['fecha_pago'])
        r['monto'] = float(r['monto']) if r['monto'] is not None else 0.0
        r['saldo_total'] = float(r['saldo_total']) if r['saldo_total'] is not None else 0.0
        r['pago_descuento'] = float(r['pago_descuento']) if r['pago_descuento'] is not None else 0.0

    with open('real_payments.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print("Saved real_payments.json successfully!")
    conn.close()
else:
    print("Could not find table 'pagos_b' in MySQL databases.")
