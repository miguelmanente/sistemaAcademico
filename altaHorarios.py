# ========================================================================================
#                  MÓDULO PARA CARGAR LOS HORARIOS
# ========================================================================================

# ------------------------------- LIBRERÍAS  --------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from backup import crear_backup
from estilos import configurar_estilos
# ---------------------------------------------------------------------------------------

# ------------------------  FUNCIÓN PRINCIPAL PARA AÑADIR HORARIOS -----------------------
def info_horarios():

    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Información de los Horarios")
    ventana.geometry("1100x700")

    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=2)
    ventana.columnconfigure(0, weight=1)

    # =========================
    # FRAME SUPERIOR
    # =========================
    frame_superior = ttk.LabelFrame(ventana, text="Carga de Horarios", padding=20)
    frame_superior.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # Variables
    curso_var = tk.StringVar()
    materia_var = tk.StringVar()
    dia_var = tk.StringVar()
    entrada_var = tk.StringVar()
    salida_var = tk.StringVar()

    cursos_dict = {}
    materias_dict = {}

    # =========================
    # CAMPOS
    # =========================
    ttk.Label(frame_superior, text="Curso:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    combo_curso = ttk.Combobox(frame_superior, textvariable=curso_var, state="readonly")
    combo_curso.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Materia:", font=("Arial", 12)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
    combo_materia = ttk.Combobox(frame_superior, textvariable=materia_var, state="readonly", font=("Arial", 12))
    combo_materia.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Día:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    combo_dia = ttk.Combobox(frame_superior, textvariable=dia_var,
                             values=["","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Lunes a Viernes"],
                             state="readonly", font=("Arial", 12))
    combo_dia.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame_superior, text="Entrada:", font=("Arial", 12)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=entrada_var, font=("Arial", 12)).grid(row=1, column=3, padx=5, pady=5)

    ttk.Label(frame_superior, text="Salida:", font=("Arial", 12)).grid(row=2, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=salida_var, font=("Arial", 12)).grid(row=2, column=3, padx=5, pady=5)

    # =========================
    # TREEVIEW
    # =========================
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))
    frame_inferior = ttk.LabelFrame(ventana, text="Listado Horarios", padding=10)
    frame_inferior.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    columnas = ("id", "curso", "materia", "dia", "entrada", "salida")

    tree = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    tree.heading("id", text="ID")
    tree.heading("curso", text="Curso")
    tree.heading("materia", text="Materia")
    tree.heading("dia", text="Día")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")

    tree.column("id", width=0, stretch=False)
    tree.column("curso", anchor="center")
    tree.column("materia", anchor="center")
    tree.column("dia", anchor="center")
    tree.column("entrada", anchor="center")
    tree.column("salida", anchor="center")

    scrollbar_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    # ---------------------------------------------------------------------------------------

    # =======================================================================================
    #                            FUNCIONES
    # ========================================================================================

    # ------------------------  LLENA LOS COMBOBOX CON INFORMACION DE LAS TABLAS -------------
    def cargar_combos():
        conn = conectar()
        cursor = conn.cursor()

        cursos_dict.clear()
        materias_dict.clear()
        cursos_dict[""] = None
        materias_dict[""] = None

        cursor.execute("SELECT id_curso, nombre FROM cursos")
        for id_, nombre in cursor.fetchall():
            texto = f"{id_} - {nombre}"
            cursos_dict[texto] = id_

        combo_curso["values"] = list(cursos_dict.keys())

        cursor.execute("SELECT id_materia, nombre FROM materias")
        for id_, nombre in cursor.fetchall():
            texto = f"{id_} - {nombre}"
            materias_dict[texto] = id_

        combo_materia["values"] = list(materias_dict.keys())

        conn.close()
    # ---------------------------------------------------------------------------------

    # -------------------- FUNCIÓN CONTROLA EL FORMATO DE FECHA -----------------------
    def validar_hora(hora):
        try:
            h, m = hora.split(":")
            return 0 <= int(h) <= 23 and 0 <= int(m) <= 59
        except:
            return False
    # ---------------------------------------------------------------------------------

    # -------------------------- LLENA EL TREEVIEW -------------------------------------
    def cargar_tree():
        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT h.id_horario, c.nombre, m.nombre, h.dia, h.hentrada, h.hsalida
            FROM horarios h
            JOIN cursos c ON h.id_curso = c.id_curso
            JOIN materias m ON h.id_materia = m.id_materia
        """)

        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

        conn.close()

    id_seleccionado = None
    # ----------------------------------------------------------------------------------

    # ---------------- FUNCIÓN PARA SELLECIONAR REGISTRO EN EL TREEVIEW ----------------
    def seleccionar(event):
        nonlocal id_seleccionado

        item = tree.selection()
        if not item:
            return

        valores = tree.item(item[0], "values")
        id_seleccionado = valores[0]

        # reconstruir combo correctamente
        for texto in cursos_dict:
            if valores[1] in texto:
                curso_var.set(texto)

        for texto in materias_dict:
            if valores[2] in texto:
                materia_var.set(texto)

        dia_var.set(valores[3])
        entrada_var.set(valores[4])
        salida_var.set(valores[5])

    tree.bind("<<TreeviewSelect>>", seleccionar)
    #------------------------------------------------------------------------------------------

    # ----------------------   GUARDA LOS NUEVOS HORARIOS ---------------------------------------
    def guardar():
        if not curso_var.get() or not materia_var.get() or not dia_var.get():
            messagebox.showwarning("Atención", "Complete todos los campos")
            return

        if not validar_hora(entrada_var.get()) or not validar_hora(salida_var.get()):
            messagebox.showerror("Error", "Hora inválida")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO horarios (id_curso, id_materia, dia, hentrada, hsalida)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cursos_dict[curso_var.get()],
                materias_dict[materia_var.get()],
                dia_var.get(),
                entrada_var.get(),
                salida_var.get()
            ))

            conn.commit()
            crear_backup()
            conn.close()

            messagebox.showinfo("OK", "Horario guardado")
            cargar_tree()
            limpiar()

        except Exception as e:
            messagebox.showerror("Error", str(e))
    # -----------------------------------------------------------------------------------------

    # --------------------- MODIFICAR REGISTRO DE LA TABALA ------------------------------------
    def modificar():
        nonlocal id_seleccionado
        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro")
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE horarios
            SET id_curso=?, id_materia=?, dia=?, hentrada=?, hsalida=?
            WHERE id_horario=?
        """, (
            cursos_dict[curso_var.get()],
            materias_dict[materia_var.get()],
            dia_var.get(),
            entrada_var.get(),
            salida_var.get(),
            id_seleccionado
        ))

        conn.commit()
        crear_backup()
        conn.close()

        cargar_tree()
        limpiar()
    # -----------------------------------------------------------------------------------------

    # ------------------------  ELIMINA REGISTRO DE LA TABLA ----------------------------------
    def eliminar():
        nonlocal id_seleccionado

        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar horario?"):
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM horarios WHERE id_horario=?", (id_seleccionado,))
        conn.commit()
        crear_backup()
        conn.close()

        cargar_tree()
        limpiar()
    # -----------------------------------------------------------------------------------------

    # ------------------------------------  LIMPIAR ENTRYS CON INFORMACIÓN --------------------
    def limpiar():
        nonlocal id_seleccionado
        id_seleccionado = None

        curso_var.set("")
        materia_var.set("")
        dia_var.set("")
        entrada_var.set("")
        salida_var.set("")
    # -----------------------------------------------------------------------------------------

    # =========================
    # BOTONES
    # =========================
    frame_botones = ttk.Frame(frame_superior)
    frame_botones.grid(row=3, column=0, columnspan=4, pady=15)

    ttk.Button(frame_botones, text="💾 Guardar", command=guardar).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="Modificar", command=modificar).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="Eliminar", command=eliminar).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="Limpiar", command=limpiar).grid(row=0, column=3, padx=5)
    ttk.Button(frame_botones, text="Salir", command=ventana.destroy).grid(row=0, column=4, padx=5)

    # =========================
    # INICIO
    # =========================
    cargar_combos()
    cargar_tree()
    centrar_ventana(ventana)
    crear_backup()