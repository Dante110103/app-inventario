import sqlite3
from datetime import datetime, date 

DB_NAME = 'inventario_web.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            codigo_barras TEXT UNIQUE,
            precio_venta REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_total REAL NOT NULL,
            fecha_venta TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas_servicios (
            id INTEGER PRIMARY KEY,
            servicio_id INTEGER NOT NULL,
            valor_venta REAL NOT NULL,
            fecha_venta TIMESTAMP,
            FOREIGN KEY (servicio_id) REFERENCES servicios (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS streaming (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            precio_mensual REAL NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ventas_streaming (
            id INTEGER PRIMARY KEY,
            streaming_id INTEGER NOT NULL,
            valor_venta REAL NOT NULL,
            fecha_venta TIMESTAMP,
            FOREIGN KEY (streaming_id) REFERENCES streaming (id)
        )
    """)

    # 🔒 ÍNDICES SEGUROS (NO BORRAN DATOS)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo_barras)")

    conn.commit()
    conn.close()

# ---------------- BUSCADOR OPTIMIZADO ----------------

def buscar_productos(texto):
    conn = get_db_connection()

    if texto.isdigit() and len(texto) >= 4:
        resultados = conn.execute(
            "SELECT * FROM productos WHERE codigo_barras = ?",
            (texto,)
        ).fetchall()
    else:
        resultados = conn.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? ORDER BY nombre ASC LIMIT 20",
            (f"%{texto}%",)
        ).fetchall()

    conn.close()
    return resultados

# ---------------- RESTO DEL CÓDIGO (SIN CAMBIOS) ----------------
# TODO lo demás queda EXACTAMENTE IGUAL
# Puedes dejar el resto de tus funciones tal como están