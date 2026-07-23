const dns = require('dns');
try {
  dns.setDefaultResultOrder('ipv4first');
} catch (e) {
  // Ignore if unsupported in older environments
}

const mysql = require('mysql2/promise');

const AIVEN_CONFIG = {
  host: process.env.AIVEN_DB_HOST || 'mysql-21306377-bdnegociov1.b.aivencloud.com',
  port: parseInt(process.env.AIVEN_DB_PORT || '24225', 10),
  user: process.env.AIVEN_DB_USER || 'avnadmin',
  password: process.env.AIVEN_DB_PASS || '',
  database: process.env.AIVEN_DB_NAME || 'procesos',
  ssl: { rejectUnauthorized: false },
  connectTimeout: 10000
};

const CORTES_ASIG = [
  { corte: 3,  asig_dia: 4 },
  { corte: 5,  asig_dia: 6 },
  { corte: 8,  asig_dia: 9 },
  { corte: 10, asig_dia: 11 },
  { corte: 11, asig_dia: 12 },
  { corte: 15, asig_dia: 16 },
  { corte: 19, asig_dia: 20 },
  { corte: 20, asig_dia: 21 },
  { corte: 23, asig_dia: 24 },
  { corte: 25, asig_dia: 26 },
  { corte: 28, asig_dia: 29 }
];

module.exports = async (req, res) => {
  // CORS & Cache control
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  let connection;
  try {
    connection = await mysql.createConnection(AIVEN_CONFIG);

    const sql = `
      SELECT 
        c.corte,
        c.asig_dia,
        SUM(CASE WHEN z.segmento = '1' AND DAY(z.fecha_pago) >= c.asig_dia THEN z.monto ELSE 0 END) AS seg1_c1,
        SUM(CASE WHEN z.segmento = '1' AND DAY(z.fecha_pago) < c.asig_dia THEN z.monto ELSE 0 END) AS seg1_c2,
        SUM(CASE WHEN z.segmento = '2' AND DAY(z.fecha_pago) >= c.asig_dia THEN z.monto ELSE 0 END) AS seg2_c1,
        SUM(CASE WHEN z.segmento = '2' AND DAY(z.fecha_pago) < c.asig_dia THEN z.monto ELSE 0 END) AS seg2_c2,
        SUM(CASE WHEN DAY(z.fecha_pago) >= c.asig_dia THEN z.monto ELSE 0 END) AS total_c1,
        SUM(CASE WHEN DAY(z.fecha_pago) < c.asig_dia THEN z.monto ELSE 0 END) AS total_c2,
        SUM(z.monto) AS total_corte
      FROM (
        SELECT 
          CASE WHEN pago_descuento = 0 THEN 'PREV' ELSE tipo_asignacion END AS segmento,
          monto,
          fecha_pago,
          corte
        FROM pagos_b 
        WHERE MONTH(fecha_pago) = 7
          AND espagogestion = 1
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
    `;

    const [rows] = await connection.query(sql);
    await connection.end();

    const segmentStats = {
      "1 PV": { total: 0, c1: 0, c2: 0 },
      "2 PV": { total: 0, c1: 0, c2: 0 }
    };

    const corteStats = {};
    CORTES_ASIG.forEach(c => {
      corteStats[c.corte] = { c1: 0, c2: 0, total: 0 };
    });

    for (const r of rows) {
      const corte = r.corte;
      const seg1_c1 = parseFloat(r.seg1_c1 || 0);
      const seg1_c2 = parseFloat(r.seg1_c2 || 0);
      const seg2_c1 = parseFloat(r.seg2_c1 || 0);
      const seg2_c2 = parseFloat(r.seg2_c2 || 0);
      const total_c1 = parseFloat(r.total_c1 || 0);
      const total_c2 = parseFloat(r.total_c2 || 0);
      const total_corte = parseFloat(r.total_corte || 0);

      segmentStats["1 PV"].c1 += seg1_c1;
      segmentStats["1 PV"].c2 += seg1_c2;
      segmentStats["1 PV"].total += (seg1_c1 + seg1_c2);

      segmentStats["2 PV"].c1 += seg2_c1;
      segmentStats["2 PV"].c2 += seg2_c2;
      segmentStats["2 PV"].total += (seg2_c1 + seg2_c2);

      corteStats[corte] = {
        c1: total_c1,
        c2: total_c2,
        total: total_corte
      };
    }

    return res.status(200).json({
      status: "success",
      source: "aiven_cloud_mysql",
      timestamp: new Date().toISOString(),
      segmentStats,
      corteStats
    });

  } catch (error) {
    if (connection) {
      try { await connection.end(); } catch (e) {}
    }
    console.error('Aiven DB Error:', error);
    return res.status(500).json({
      status: "error",
      message: error.message || "Failed to query Aiven DB"
    });
  }
};
