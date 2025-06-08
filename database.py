import sqlite3
from datetime import datetime, date 

def get_db_connection():
    """Crea una conexión a la BD que devuelve filas que se pueden acceder por nombre de columna."""
    conexion = sqlite3.connect('inventario_web.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_bd():
    """Crea todas las tablas necesarias en la base de datos si no existen."""
    conn = get_db_connection()
    # (Las definiciones de las 6 tablas se quedan igual)
    conn.execute('CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE, codigo_barras TEXT UNIQUE, precio_venta REAL NOT NULL, stock INTEGER NOT NULL DEFAULT 0)')
    conn.execute('CREATE TABLE IF NOT EXISTS ventas (id INTEGER PRIMARY KEY, producto_id INTEGER NOT NULL, cantidad INTEGER NOT NULL, precio_total REAL NOT NULL, fecha_venta TIMESTAMP, FOREIGN KEY (producto_id) REFERENCES productos (id))')
    conn.execute('CREATE TABLE IF NOT EXISTS servicios (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE)')
    conn.execute('CREATE TABLE IF NOT EXISTS ventas_servicios (id INTEGER PRIMARY KEY, servicio_id INTEGER NOT NULL, valor_venta REAL NOT NULL, fecha_venta TIMESTAMP, FOREIGN KEY (servicio_id) REFERENCES servicios (id))')
    conn.execute('CREATE TABLE IF NOT EXISTS streaming (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE, precio_mensual REAL NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS ventas_streaming (id INTEGER PRIMARY KEY, streaming_id INTEGER NOT NULL, valor_venta REAL NOT NULL, fecha_venta TIMESTAMP, FOREIGN KEY (streaming_id) REFERENCES streaming (id))')
    conn.commit()
    conn.close()

# --- FUNCIONES DE PRODUCTOS ---
def ver_inventario():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM productos ORDER BY nombre ASC").fetchall()
    conn.close()
    return items

def obtener_producto_por_id(id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()
    conn.close()
    return item

def agregar_producto(nombre, codigo, precio, stock):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO productos (nombre, codigo_barras, precio_venta, stock) VALUES (?, ?, ?, ?)", (nombre, codigo, precio, stock))
        conn.commit()
        return True, "Producto agregado."
    except sqlite3.IntegrityError:
        return False, "Error: Ya existe un producto con ese nombre o código."
    finally:
        conn.close()

def actualizar_producto(id, nombre, codigo, precio, stock):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE productos SET nombre = ?, codigo_barras = ?, precio_venta = ?, stock = ? WHERE id = ?", (nombre, codigo, precio, stock, id))
        conn.commit()
        return True, "Producto actualizado."
    except sqlite3.IntegrityError:
        return False, "Error: Otro producto ya tiene ese nombre o código."
    finally:
        conn.close()

def eliminar_producto(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM productos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def registrar_venta(id_producto, cantidad):
    conn = get_db_connection()
    try:
        producto = conn.execute("SELECT * FROM productos WHERE id = ?", (id_producto,)).fetchone()
        if not producto: return False, f"Error: Producto con ID {id_producto} no existe."
        if producto['stock'] < cantidad: return False, f"Stock insuficiente. Quedan {producto['stock']}."
        nuevo_stock = producto['stock'] - cantidad
        precio_total = cantidad * producto['precio_venta']
        conn.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, id_producto))
        conn.execute("INSERT INTO ventas (producto_id, cantidad, precio_total, fecha_venta) VALUES (?, ?, ?, ?)", (id_producto, cantidad, precio_total, datetime.now()))
        conn.commit()
        return True, "Venta de producto registrada."
    finally:
        conn.close()

def obtener_productos_para_pedido(umbral=5):
    """Obtiene productos cuyo stock es igual o menor al umbral."""
    conn = get_db_connection()
    productos = conn.execute("SELECT * FROM productos WHERE stock <= ? ORDER BY stock ASC", (umbral,)).fetchall()
    conn.close()
    return productos

# --- FUNCIONES DE SERVICIOS ---
def ver_servicios():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM servicios ORDER BY nombre ASC").fetchall()
    conn.close()
    return items

def obtener_servicio_por_id(id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM servicios WHERE id = ?", (id,)).fetchone()
    conn.close()
    return item

def agregar_servicio(nombre):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO servicios (nombre) VALUES (?)", (nombre,))
        conn.commit()
        return True, "Servicio agregado."
    except sqlite3.IntegrityError:
        return False, "Error: Ese servicio ya existe."
    finally:
        conn.close()

def actualizar_servicio(id, nombre):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE servicios SET nombre = ? WHERE id = ?", (nombre, id))
        conn.commit()
        return True, "Servicio actualizado."
    except sqlite3.IntegrityError:
        return False, "Error: Ya existe otro servicio con ese nombre."
    finally:
        conn.close()

def eliminar_servicio(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM servicios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def registrar_venta_servicio(id, valor):
    conn = get_db_connection()
    try:
        item = conn.execute("SELECT id FROM servicios WHERE id = ?", (id,)).fetchone()
        if not item: return False, f"Error: Servicio con ID {id} no existe."
        conn.execute("INSERT INTO ventas_servicios (servicio_id, valor_venta, fecha_venta) VALUES (?, ?, ?)", (id, valor, datetime.now()))
        conn.commit()
        return True, "Venta de servicio registrada."
    finally:
        conn.close()

# --- FUNCIONES DE STREAMING ---
def ver_streaming():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM streaming ORDER BY nombre ASC").fetchall()
    conn.close()
    return items

def obtener_streaming_por_id(id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM streaming WHERE id = ?", (id,)).fetchone()
    conn.close()
    return item

def agregar_streaming(nombre, precio):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO streaming (nombre, precio_mensual) VALUES (?, ?)", (nombre, precio))
        conn.commit()
        return True, "Cuenta de streaming agregada."
    except sqlite3.IntegrityError:
        return False, "Error: Esa cuenta ya existe."
    finally:
        conn.close()

def actualizar_streaming(id, nombre, precio):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE streaming SET nombre = ?, precio_mensual = ? WHERE id = ?", (nombre, precio, id))
        conn.commit()
        return True, "Cuenta de streaming actualizada."
    except sqlite3.IntegrityError:
        return False, "Error: Otra cuenta ya tiene ese nombre."
    finally:
        conn.close()

def eliminar_streaming(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM streaming WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def registrar_venta_streaming(id, valor):
    conn = get_db_connection()
    try:
        item = conn.execute("SELECT id FROM streaming WHERE id = ?", (id,)).fetchone()
        if not item: return False, f"Error: Cuenta ID {id} no existe."
        conn.execute("INSERT INTO ventas_streaming (streaming_id, valor_venta, fecha_venta) VALUES (?, ?, ?)", (id, valor, datetime.now()))
        conn.commit()
        return True, "Venta de streaming registrada."
    finally:
        conn.close()

# --- FUNCIONES DE REPORTES ---
def ver_ventas_hoy(tipo_venta):
    """Obtiene las ventas detalladas (productos, servicios o streaming) solo del día actual."""
    conn = get_db_connection()
    
    # Obtenemos la fecha de hoy desde Python de forma explícita
    fecha_de_hoy = date.today().isoformat() # Formato 'YYYY-MM-DD'
    
    query = ""
    if tipo_venta == 'producto':
        query = "SELECT p.nombre, v.cantidad, v.precio_total, v.fecha_venta FROM ventas v JOIN productos p ON v.producto_id = p.id WHERE DATE(v.fecha_venta) = ? ORDER BY v.fecha_venta DESC"
    elif tipo_venta == 'servicio':
        query = "SELECT s.nombre, vs.valor_venta, vs.fecha_venta FROM ventas_servicios vs JOIN servicios s ON vs.servicio_id = s.id WHERE DATE(vs.fecha_venta) = ? ORDER BY vs.fecha_venta DESC"
    elif tipo_venta == 'streaming':
        query = "SELECT str.nombre, v_str.valor_venta, v_str.fecha_venta FROM ventas_streaming v_str JOIN streaming str ON v_str.streaming_id = str.id WHERE DATE(v_str.fecha_venta) = ? ORDER BY v_str.fecha_venta DESC"
    
    reporte = conn.execute(query, (fecha_de_hoy,)).fetchall()
    conn.close()
    return reporte

def obtener_historial_ventas():
    """Obtiene un resumen de los totales vendidos por día, excluyendo el día de hoy."""
    conn = get_db_connection()
    
    # Obtenemos la fecha de hoy desde Python para la exclusión
    fecha_de_hoy = date.today().isoformat() # Formato 'YYYY-MM-DD'

    query = """
        SELECT DATE(fecha_venta) as dia, SUM(total) as total_dia FROM (
            SELECT fecha_venta, precio_total as total FROM ventas
            UNION ALL
            SELECT fecha_venta, valor_venta as total FROM ventas_servicios
            UNION ALL
            SELECT fecha_venta, valor_venta as total FROM ventas_streaming
        )
        WHERE DATE(fecha_venta) < ?
        GROUP BY dia ORDER BY dia DESC
    """
    historial = conn.execute(query, (fecha_de_hoy,)).fetchall()
    conn.close()
    return historial