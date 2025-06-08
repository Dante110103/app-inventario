@echo off
ECHO ==========================================================
ECHO  INICIANDO SERVIDOR DE LA APLICACION DE INVENTARIO...
ECHO ==========================================================
ECHO.
ECHO Este es el servidor. No cierres esta ventana.
ECHO Abre tu navegador y ve a: http://localhost:5001
ECHO.

REM Activa el entorno virtual de Python
call venv\Scripts\activate

REM Inicia la aplicacion
python app.py

REM Mantiene la ventana abierta si hay un error
pause