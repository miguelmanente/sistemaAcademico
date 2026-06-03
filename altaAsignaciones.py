# ================================================================================
#                       MÓDULO ASIGNACIONES DOCENTES
#=================================================================================

# =============================  LIBRERÍAS =======================================
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from backup import crear_backup
from estilos import configurar_estilos
# --------------------------------------------------------------------------------

# ====================== PANTALLA PRINCIPAL DE ASIGNACIONES ======================
def info_asignaciones():
    # -----------------  DEFINICIÓN DE LA VENTANA PRINCIPAL ----------------------
    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Asignaciones Docentes")
    ventana.geometry("1100x700")

    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=2)
    ventana.columnconfigure(0, weight=1)

    # =========================
    # FRAME SUPERIOR
    # =========================
    frame_superior = ttk.LabelFrame(ventana, text="Asignar Profesor", padding=20)
    frame_superior.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # Variables
    profesor_var = tk.StringVar()
    horario_var = tk.StringVar()
    situacion_var = tk.StringVar()

    profesores_dict = {}
    horarios_dict = {}

    # =========================
    # CAMPOS
    # =========================
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))

    ttk.Label(frame_superior, text="Profesor:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    combo_profesor = ttk.Combobox(frame_superior, textvariable=profesor_var, state="readonly", font=("Arial", 12))
    combo_profesor.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Horario:", font=("Arial", 12)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
    combo_horario = ttk.Combobox(frame_superior, textvariable=horario_var, state="readonly", font=("Arial", 12))
    combo_horario.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Situación:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    combo_situacion = ttk.Combobox(
        frame_superior,
        textvariable=situacion_var,
        values=["","Titular", "Provisorio", "Suplente"],
        state="readonly",
        font=("Arial", 12)
    )
    combo_situacion.grid(row=1, column=1, padx=5, pady=5)

    # =========================
    # TREEVIEW
    # =========================
    frame_inferior = ttk.LabelFrame(ventana, text="Listado Asignaciones", padding=10)
    frame_inferior.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    columnas = ("id", "profesor", "curso", "materia", "dia", "entrada", "salida", "situacion")

    tree = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")
    tree.heading("id", text="ID")
    tree.heading("profesor", text="Profesor")
    tree.heading("curso", text="Curso")
    tree.heading("materia", text="Materia")
    tree.heading("dia", text="Día")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")
    tree.heading("situacion", text="Situación")

    #tree.column("id", width=50, stretch=False)
    tree.column("id", width=0, minwidth=0, stretch=False)
    tree.column("profesor", width=230)
    tree.column("curso", width=50)
    tree.column("materia", width=230)
    tree.column("dia", width=50)
    tree.column("entrada", width=50)
    tree.column("salida", width=50)
    tree.column("situacion", width=70)
    #for col in columnas:
    #    tree.heading(col, text=col.capitalize())

   # tree.column("id", width=0, stretch=False)

    scrollbar_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    # -----------------------------------------------------------------------------------------


    # ==========================================================================================
    #                               FUNCIONES O MÓDULOS 
    # ==========================================================================================
    
    # ====================================  LLENA LOS DATOS DE LOS COMBOS ======================
    def cargar_combos():
        conn = conectar()
        cursor = conn.cursor()

        profesores_dict.clear()
        horarios_dict.clear()
        profesores_dict[""] = None
        horarios_dict[""] = None

        # Profesores
        cursor.execute("SELECT id_profesor, apenom FROM profesores")
        for id_, nombre in cursor.fetchall():
            texto = f"{id_} - {nombre}"
            profesores_dict[texto] = id_

        combo_profesor["values"] = list(profesores_dict.keys())

        # Horarios
        cursor.execute("""
            SELECT h.id_horario, c.nombre, m.nombre, h.dia, h.hentrada, h.hsalida
            FROM horarios h
            JOIN cursos c ON h.id_curso = c.id_curso
            JOIN materias m ON h.id_materia = m.id_materia
        """)

        for fila in cursor.fetchall():
            texto = f"{fila[0]} - {fila[1]} | {fila[2]} | {fila[3]} {fila[4]}-{fila[5]}"
            horarios_dict[texto] = fila[0]

        combo_horario["values"] = list(horarios_dict.keys())

        conn.close()
    # --------------------------------------------------------------------------------------

    # =========================== MUESTRA DATOS EN EL TREEVIEW  ============================
    id_seleccionado = None

    def cargar_tree():

        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                a.id_asignacion,
                a.id_profesor,
                a.id_horario,

                p.apenom,
                c.nombre,
                m.nombre,
                h.dia,
                h.hentrada,
                h.hsalida,

                a.srprofesor

            FROM asignaciones_docentes a

            LEFT JOIN profesores p
            ON a.id_profesor = p.id_profesor

            LEFT JOIN horarios h
            ON a.id_horario = h.id_horario

            LEFT JOIN cursos c
            ON h.id_curso = c.id_curso

            LEFT JOIN materias m
            ON h.id_materia = m.id_materia

        """)

        for fila in cursor.fetchall():

            tree.insert("", "end", values=(

                fila[0],  # id asignacion
                fila[3],  # profesor
                fila[4],  # curso
                fila[5],  # materia
                fila[6],  # dia
                fila[7],  # entrada
                fila[8],  # salida
                fila[9]   # situacion

            ))

        conn.close()
    # -------------------------------------------------------------------------------------

    # ============================ SELECCIONAR REGISTRO EN EL TREEVIEW ====================

    def seleccionar(event):

        nonlocal id_seleccionado

        item = tree.selection()

        if not item:
            return

        valores = tree.item(item[0], "values")

        id_seleccionado = valores[0]

        nombre_profesor = valores[1]

        # =========================================
        # BUSCAR PROFESOR EN EL COMBO
        # =========================================

        for texto in profesores_dict:

            if nombre_profesor in texto:

                profesor_var.set(texto)
                break

        # =========================================
        # BUSCAR HORARIO EN EL COMBO
        # =========================================

        curso = valores[2]
        materia = valores[3]
        dia = valores[4]

        for texto in horarios_dict:

            if curso in texto and materia in texto and dia in texto:

                horario_var.set(texto)
                break

        situacion_var.set(valores[7])

    tree.bind("<<TreeviewSelect>>", seleccionar)
    # -------------------------------------------------------------------------------------

    # =============================  GUARDA aSIGNACIONES EN LA TABLA  ======================
    def guardar():
        if not profesor_var.get() or not horario_var.get() or not situacion_var.get():
            messagebox.showwarning("Atención", "Complete todos los campos", parent=ventana)
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO asignaciones_docentes (id_profesor, id_horario, srprofesor)
                VALUES (?, ?, ?)
            """, (
                profesores_dict[profesor_var.get()],
                horarios_dict[horario_var.get()],
                situacion_var.get()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("OK", "Asignación guardada", parent=ventana)
            cargar_tree()
            limpiar()

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=ventana)
    # -------------------------------------------------------------------------------------

    # =============================  Modifica registro de Asignación ========================
    def modificar():

        nonlocal id_seleccionado

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro", parent=ventana
            )

            return

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute("""

            UPDATE asignaciones_docentes

            SET

                id_profesor=?,
                id_horario=?,
                srprofesor=?

            WHERE id_asignacion=?

        """, (

            profesores_dict[profesor_var.get()],
            horarios_dict[horario_var.get()],
            situacion_var.get(),
            id_seleccionado

        ))

        conn.commit()

        conn.close()

        messagebox.showinfo(
            "OK",
            "Asignación modificada", parent=ventana
        )

        cargar_tree()

        limpiar()
    # -------------------------------------------------------------------------------------


    # ================================= ELIMINA ASIGNACIONES ==============================
    def eliminar():
        nonlocal id_seleccionado

        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro", parent=ventana)
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar asignación?", parent=ventana):
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM asignaciones_docentes WHERE id_asignacion=?", (id_seleccionado,))
        conn.commit()
        conn.close()

        cargar_tree()
        limpiar()
    # ------------------------------------------------------------------------------------------

    # =============== LIMPIA INFORMACIÓN CONTENIDA EN COMBOS Y ENTRYS ==========================
    def limpiar():
        nonlocal id_seleccionado
        id_seleccionado = None

        profesor_var.set("")
        horario_var.set("")
        situacion_var.set("")
    # -----------------------------------------------------------------------------------------

    # ==============================================================================================
    #                                       BOTONES
    # ===============================================================================================
    frame_botones = ttk.Frame(frame_superior)
    frame_botones.grid(row=2, column=0, columnspan=4, pady=15)

    ttk.Button(frame_botones, text="💾 Guardar", command=guardar).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="✏ Modificar", command=modificar).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="🗑 Eliminar", command=eliminar).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="🧹 Limpiar", command=limpiar).grid(row=0, column=3, padx=5)
    ttk.Button(frame_botones, text="❌ Cerrar", command=ventana.destroy).grid(row=0, column=4, padx=5)

    # =========================
    # INICIO
    # =========================
    cargar_combos()
    cargar_tree()
    centrar_ventana(ventana)
    crear_backup()