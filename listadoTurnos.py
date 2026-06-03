#========================================================================================
#                  MÓDULO LISTAR TURNOS DOCENTES 
# ========================================================================================

# ----------------------------------- LIBRERÍAS ------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from estilos import configurar_estilos
# ----------------------------------------------------------------------------------------

# ==========================================================
#              VENTANA GESTIÓN DE CARGOS
# ==========================================================

def listado_personal_turnos():

    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Listados del Personal por Turnos")
    ventana.geometry("900x600")

    # ======================================================
    # VARIABLES
    # ======================================================
    turno_var = tk.StringVar()
    dia_var = tk.StringVar()

    # ======================================================
    # FRAME
    # ======================================================

    frame = ttk.LabelFrame(ventana, text="")
    frame.pack(fill="x", padx=10, pady=10)

    # ======================================================
    # COMBO TURNOS
    # ======================================================
       
    ttk.Label(frame, text="Turno:").grid(row=0, column=0, padx=5, pady=5)
    combo_turno = ttk.Combobox(frame, textvariable=turno_var, values=["Mañana", "Tarde", "Noche"], state="readonly", width=20)
    combo_turno.grid(row=0, column=1,  padx=5, pady=5)

    ttk.Label(frame, text="Día").grid(row=0, column=2, padx=5, pady=5)
    combo_dia = ttk.Combobox(frame, textvariable=dia_var, values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"], state="readonly", width=15)
    combo_dia.grid(row=0, column=3, padx=5, pady=5)

    # ======================================================
    # TREEVIEW
    # ======================================================

    columnas = ("nombre","cargo","entrada","salida", "firma")

    tree = ttk.Treeview(ventana, columns=columnas, show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    tree.heading("nombre", text="Personal")
    tree.heading("cargo", text="Cargo")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")
    tree.heading("firma", text="Firma")

    tree.column("nombre", width=250)
    tree.column("cargo", width=200)
    tree.column("entrada", width=100)
    tree.column("salida", width=100)
    tree.column("firma", width=200)


    # ===========================  Mostrar datos en el treeview ===================
    def cargar_tree():

        for item in tree.get_children():
            tree.delete(item)

        if turno_var.get() == "":
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.apenom,
                c.nombre_cargo,
                pc.hentrada,
                pc.hsalida

            FROM personal_cargos pc

            JOIN profesores p
                ON pc.id_profesor = p.id_profesor

            JOIN cargos c
                ON pc.id_cargo = c.id_cargo

            WHERE pc.turno = ?
            AND pc.dia = ?

            ORDER BY c.orden, p.apenom

        """, (turno_var.get(),
            dia_var.get()))

      
        registros = cursor.fetchall()
   
        conn.close()

        print("Turno seleccionado:", repr(turno_var.get()))
        for fila in registros:

            tree.insert(
                "",
                "end",
                values=fila
            )
        
    # -------------------------------------------------------------------------------

    # ============================== BOTÓN ============================================
    ttk.Button(frame, text="Buscar", command=cargar_tree).grid(row=0, column=2,padx=10)
    # ---------------------------------------------------------------------------------

    # =========================  INICIO ============================================
    centrar_ventana(ventana)