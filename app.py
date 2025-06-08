# app.py (Versión Final, Completa y Definitiva)
from flask import Flask, render_template, request, redirect, url_for, flash, session
import database
import os

app = Flask(__name__)
app.secret_key = 'clave_final_12345_super_segura_y_aleatoria'

# --- RUTAS PRINCIPALES DE NAVEGACIÓN ---
@app.route('/')
def pagina_principal():
    return render_template('index.html', 
                           productos=database.ver_inventario(), 
                           servicios=database.ver_servicios(),
                           streaming=database.ver_streaming(),
                           carrito=session.get('carrito', []),
                           total_carrito=sum(item['subtotal'] for item in session.get('carrito', [])))

@app.route('/productos')
def pagina_gestion_productos():
    return render_template('productos.html', productos=database.ver_inventario())

@app.route('/servicios')
def pagina_gestion_servicios():
    return render_template('servicios.html', servicios=database.ver_servicios())

@app.route('/streaming')
def pagina_gestion_streaming():
    return render_template('streaming.html', cuentas=database.ver_streaming())

@app.route('/nuevo_pedido')
def pagina_nuevo_pedido():
    """Muestra la página con productos con bajo stock."""
    productos_para_pedir = database.obtener_productos_para_pedido()
    return render_template('nuevo_pedido.html', productos_a_pedir=productos_para_pedir)

@app.route('/reportes')
def pagina_reportes():
    ventas_productos_hoy = database.ver_ventas_hoy(tipo_venta='producto')
    ventas_servicios_hoy = database.ver_ventas_hoy(tipo_venta='servicio')
    ventas_streaming_hoy = database.ver_ventas_hoy(tipo_venta='streaming')
    total_productos_hoy = sum(fila['precio_total'] for fila in ventas_productos_hoy)
    total_servicios_hoy = sum(fila['valor_venta'] for fila in ventas_servicios_hoy)
    total_streaming_hoy = sum(fila['valor_venta'] for fila in ventas_streaming_hoy)
    total_general_hoy = total_productos_hoy + total_servicios_hoy + total_streaming_hoy
    historial = database.obtener_historial_ventas()
    return render_template('reportes.html', 
                           ventas_productos_hoy=ventas_productos_hoy, total_productos_hoy=total_productos_hoy,
                           ventas_servicios_hoy=ventas_servicios_hoy, total_servicios_hoy=total_servicios_hoy,
                           ventas_streaming_hoy=ventas_streaming_hoy, total_streaming_hoy=total_streaming_hoy,
                           total_general_hoy=total_general_hoy, historial=historial)

@app.route('/producto/editar/<int:id>')
def pagina_editar_producto(id):
    producto = database.obtener_producto_por_id(id)
    return render_template('editar_producto.html', producto=producto) if producto else redirect(url_for('pagina_gestion_productos'))

@app.route('/servicio/editar/<int:id>')
def pagina_editar_servicio(id):
    servicio = database.obtener_servicio_por_id(id)
    return render_template('editar_servicio.html', servicio=servicio) if servicio else redirect(url_for('pagina_gestion_servicios'))

@app.route('/streaming/editar/<int:id>')
def pagina_editar_streaming(id):
    cuenta = database.obtener_streaming_por_id(id)
    return render_template('editar_streaming.html', cuenta=cuenta) if cuenta else redirect(url_for('pagina_gestion_streaming'))

# --- RUTAS DE PROCESAMIENTO (ACCIONES) ---
@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    if 'carrito' not in session: session['carrito'] = []
    tipo = request.form.get('tipo')
    try:
        if tipo == 'producto':
            id_item, cantidad = int(request.form['id_producto']), int(request.form['cantidad'])
            item_db = database.obtener_producto_por_id(id_item)
            if item_db and cantidad > 0:
                item_existente = next((item for item in session['carrito'] if item.get('id') == id_item and item.get('tipo') == 'producto'), None)
                if item_existente:
                    item_existente['cantidad'] += cantidad
                    item_existente['subtotal'] = item_existente['cantidad'] * item_existente['precio_unitario']
                    flash(f"Se sumó más cantidad de '{item_db['nombre']}'.")
                else:
                    item = {"id": id_item, "nombre": item_db['nombre'], "cantidad": cantidad, "precio_unitario": item_db['precio_venta'], "subtotal": cantidad * item_db['precio_venta'], "tipo": "producto"}
                    session['carrito'].append(item)
                    flash(f"'{item_db['nombre']}' añadido al ticket.")
        elif tipo == 'servicio':
            id_item, valor = int(request.form['id_servicio']), float(request.form['valor'])
            item_db = database.obtener_servicio_por_id(id_item)
            if item_db and valor > 0:
                item = {"id": id_item, "nombre": item_db['nombre'], "cantidad": 1, "precio_unitario": valor, "subtotal": valor, "tipo": "servicio"}
                session['carrito'].append(item)
                flash(f"Servicio '{item_db['nombre']}' añadido.")
        elif tipo == 'streaming':
            id_item = int(request.form['id_streaming'])
            item_db = database.obtener_streaming_por_id(id_item)
            if item_db:
                item = {"id": id_item, "nombre": item_db['nombre'], "cantidad": 1, "precio_unitario": item_db['precio_mensual'], "subtotal": item_db['precio_mensual'], "tipo": "streaming"}
                session['carrito'].append(item)
                flash(f"Cuenta '{item_db['nombre']}' añadida.")
        session.modified = True
    except Exception as e:
        flash(f"Error al añadir al carrito: {e}")
    return redirect(url_for('pagina_principal'))

@app.route('/finalizar_venta', methods=['POST'])
def finalizar_venta():
    for item in session.get('carrito', []):
        if item['tipo'] == 'producto': database.registrar_venta(item['id'], item['cantidad'])
        elif item['tipo'] == 'servicio': database.registrar_venta_servicio(item['id'], item['precio_unitario'])
        elif item['tipo'] == 'streaming': database.registrar_venta_streaming(item['id'], item['precio_unitario'])
    session.pop('carrito', None)
    flash("¡Venta finalizada con éxito!")
    return redirect(url_for('pagina_principal'))

@app.route('/limpiar_carrito')
def limpiar_carrito():
    session.pop('carrito', None)
    flash("Ticket limpiado.")
    return redirect(url_for('pagina_principal'))

@app.route('/quitar_del_carrito/<int:item_index>')
def quitar_del_carrito(item_index):
    # Verificamos que el carrito exista en la sesión
    if 'carrito' in session and session['carrito']:
        try:
            # .pop() elimina el ítem de la lista en la posición (índice) especificada
            item_eliminado = session['carrito'].pop(item_index)
            session.modified = True # Importante para que Flask guarde el cambio en la sesión
            flash(f"Se ha quitado '{item_eliminado['nombre']}' del ticket.")
        except IndexError:
            # Esto pasaría si el índice está fuera de rango, aunque es poco probable con nuestro método
            flash("Error: No se pudo quitar el ítem.")
            
    return redirect(url_for('pagina_principal'))

@app.route('/agregar_producto', methods=['POST'])
def procesar_agregado_producto():
    try:
        exito, mensaje = database.agregar_producto(request.form['nombre'], request.form.get('codigo_barras', ''), float(request.form['precio_venta']), int(request.form['stock']))
        flash(mensaje)
    except Exception as e:
        flash(f"Error al agregar producto: {e}")
    return redirect(url_for('pagina_gestion_productos'))

@app.route('/producto/actualizar', methods=['POST'])
def procesar_actualizacion_producto():
    try:
        exito, mensaje = database.actualizar_producto(request.form['id'], request.form['nombre'], request.form.get('codigo_barras', ''), float(request.form['precio_venta']), int(request.form['stock']))
        flash(mensaje)
    except Exception as e:
        flash(f"Error al actualizar: {e}")
    return redirect(url_for('pagina_gestion_productos'))

@app.route('/eliminar_producto', methods=['POST'])
def procesar_eliminado_producto():
    try:
        database.eliminar_producto(request.form['id_producto'])
        flash(f"Producto ID {request.form['id_producto']} eliminado.")
    except Exception as e:
        flash(f"Error al eliminar: {e}")
    return redirect(url_for('pagina_gestion_productos'))

@app.route('/agregar_servicio', methods=['POST'])
def procesar_agregado_servicio():
    try:
        exito, mensaje = database.agregar_servicio(request.form['nombre_servicio'])
        flash(mensaje)
    except Exception as e:
        flash(f"Error al agregar servicio: {e}")
    return redirect(url_for('pagina_gestion_servicios'))

@app.route('/servicio/actualizar', methods=['POST'])
def procesar_actualizacion_servicio():
    try:
        exito, mensaje = database.actualizar_servicio(request.form['id'], request.form['nombre'])
        flash(mensaje)
    except Exception as e:
        flash(f"Error al actualizar servicio: {e}")
    return redirect(url_for('pagina_gestion_servicios'))

@app.route('/eliminar_servicio', methods=['POST'])
def procesar_eliminado_servicio():
    try:
        database.eliminar_servicio(request.form['id_servicio'])
        flash(f"Servicio ID {request.form['id_servicio']} eliminado.")
    except Exception as e:
        flash(f"Error al eliminar servicio: {e}")
    return redirect(url_for('pagina_gestion_servicios'))

@app.route('/agregar_streaming', methods=['POST'])
def procesar_agregado_streaming():
    try:
        exito, mensaje = database.agregar_streaming(request.form['nombre_streaming'], float(request.form['precio_mensual']))
        flash(mensaje)
    except Exception as e:
        flash(f"Error al agregar cuenta: {e}")
    return redirect(url_for('pagina_gestion_streaming'))

@app.route('/streaming/actualizar', methods=['POST'])
def procesar_actualizacion_streaming():
    try:
        exito, mensaje = database.actualizar_streaming(request.form['id'], request.form['nombre'], float(request.form['precio_mensual']))
        flash(mensaje)
    except Exception as e:
        flash(f"Error al actualizar cuenta: {e}")
    return redirect(url_for('pagina_gestion_streaming'))

@app.route('/eliminar_streaming', methods=['POST'])
def procesar_eliminado_streaming():
    try:
        database.eliminar_streaming(request.form['id_streaming'])
        flash(f"Cuenta ID {request.form['id_streaming']} eliminada.")
    except Exception as e:
        flash(f"Error al eliminar cuenta: {e}")
    return redirect(url_for('pagina_gestion_streaming'))

# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    db_file = 'inventario_web.db'
    # Si la base de datos no existe, la crea vacía
    if not os.path.exists(db_file):
        print("Base de datos no encontrada. Creando una nueva base de datos vacía...")
        database.inicializar_bd()
        print("Base de datos 'inventario_web.db' creada exitosamente.")
    
    # Inicia el servidor de producción con Waitress
    from waitress import serve
    print("Iniciando servidor en http://localhost:5001")
    print("La aplicación está lista para usarse en el navegador.")
    print("Para detener el servidor, cierra esta ventana.")
    serve(app, host='0.0.0.0', port=5001)