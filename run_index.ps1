# Ejecuta index.py desde la carpeta de la aplicación usando el entorno virtual
# Con esto se fijan las rutas de Tcl/Tk necesarias para tkinter.

Set-Location $PSScriptRoot
$env:TCL_LIBRARY = 'C:\Users\migue\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
$env:TK_LIBRARY = 'C:\Users\migue\AppData\Local\Programs\Python\Python313\tcl\tk8.6'
& "C:\Users\migue\OneDrive\Escritorio\Python\.venv\Scripts\python.exe" .\index.py
