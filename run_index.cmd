@echo off
REM Ejecuta index.py desde la carpeta de la aplicación usando el entorno virtual.
cd /d %~dp0
set "TCL_LIBRARY=C:\Users\migue\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
set "TK_LIBRARY=C:\Users\migue\AppData\Local\Programs\Python\Python313\tcl\tk8.6"
"C:\Users\migue\OneDrive\Escritorio\Python\.venv\Scripts\python.exe" index.py
pause
