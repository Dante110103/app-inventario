# run.py
from waitress import serve
from app import app  # Importa la variable 'app' desde tu archivo app.py

if __name__ == '__main__':
    # Escucha en la IP 0.0.0.0 para ser accesible desde otros PCs en la red
    # Usa el puerto 5001 que ya conocemos
    print("Iniciando servidor de producción en http://<IP_DE_TU_PC>:5001")
    print("Presiona CTRL+C para detener el servidor.")
    serve(app, host='0.0.0.0', port=5001)