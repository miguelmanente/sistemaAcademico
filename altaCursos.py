# ========================================================================================
#                  MÓDULO PARA CARGAR DATOS LOS CURSOS 
# ========================================================================================

# ---------------------  Área de declaración de librerías --------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from backup import crear_backup
from dbm import sqlite3
from estilos import configurar_estilos

def info_cursos():

    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Información de los Cursos")
    ventana.geometry("1100x700")

    # Configuración del grid de la ventana principal
    ventana.rowconfigure(0, weight=1)  # Parte superior
    ventana.rowconfigure(1, weight=2)  # Parte inferior
    ventana.columnconfigure(0, weight=1)


    # =========================
    # FRAME SUPERIOR (ENTRYS)
    # =========================
    frame_superior = ttk.LabelFrame(ventana, text="Ingreso de Cursos Secundaria y Polimodal", padding=10)
    frame_superior.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

    # Configurar columnas del frame superior
    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # -------------------------- Variables ----------------------------------------------------------------------------
    nombre = tk.StringVar()
    turno = tk.StringVar()
 

    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------  Labels y Entrys distribuidos en dos columnas  ------------------------------------
    # Labels y entry que permite ingregar elnombre de la materia
    ttk.Label(frame_superior, text="Nbre del Curso :", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=nombre, font=("Arial", 12)).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

      # Labels y entry para ingresar el turno del curso 
    ttk.Label(frame_superior, text="Turno del Curso:", font=("Arial", 12)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=turno, font=("Arial", 12)).grid(row=0, column=3, sticky="ew", padx=5, pady=5)

 
    # =========================
    # BOTONES
    # =========================
    frame_botones = ttk.Frame(frame_superior)
    frame_botones.grid(row=3, column=0, columnspan=4, pady=10)

    # =========================
    # FRAME INFERIOR (TREEVIEW)
    # =========================
    frame_inferior = ttk.LabelFrame(ventana, text="Listado de Cursos", padding=10)
    frame_inferior.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Configuración del grid del frame inferior
    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    #Columnas del Treeview
    columnas = ("id_curso","nombre","turno")

    tree = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    # Encabezados
    tree.heading("id_curso", text="ID")
    tree.heading("nombre", text="Nbre del Curso")
    tree.heading("turno", text="Turno del Curso")
   
    
    tree.column("id_curso", width=0, stretch=False)
    tree.column("nombre", width=200, anchor="center")
    tree.column("turno", width=100, anchor="center")
  

    # Scrollbars
    scrollbar_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(frame_inferior, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Ubicación en el grid
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    #========================================================================================
    #                                  MÉTODOS O FUNCIONES
    #========================================================================================
    
    # Variable global ha usar en las distintas funciones 
    id_seleccionado = None

      # ----------------- Carga y muestra los registros cargados en la BD Materias -------------
    def cargar_datos_treeview():
        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_curso, nombre, turno
            FROM cursos
            ORDER BY nombre
        """)

        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

        conn.close()
    # ---------------------------------------------------------------------------------------

    # ------------------------ Añade registros nuevos a la BD materias ----------------------
    def agregar_cursos():
        if not nombre.get() or not nombre.get() or not turno.get():
            messagebox.showwarning(
                "Campos obligatorios",
                "Nombres del curso, y turno son obligatorios.", parent=ventana
            )
            return
        
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO cursos (nombre, turno)
                VALUES (?, ?)
            """, (
                nombre.get(),
                turno.get(),
   
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Curso guardado correctamente.", parent=ventana)

            cargar_datos_treeview()
           

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los Cursos:\n{e}", parent=ventana)
    # ----------------------------------------------------------------------------------

    # ---  Función que permite selecccionar un registro en el treview ------------------
    def seleccionar_registro(event):
        nonlocal id_seleccionado

        item = tree.selection()
        if not item:
            return

        valores = tree.item(item[0], "values")

        id_seleccionado = valores[0]  # 👈 ESTE ES EL CLAVE

        nombre.set(valores[1])
        turno.set(valores[2])
    

    tree.bind("<<TreeviewSelect>>", seleccionar_registro) 
    # ---------------------------------------------------------------------------------


    # ----------------  Modifica registro de profesores --------------------------------
    
    def modificar_curso():
        nonlocal id_seleccionado
        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro", parent=ventana)
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE cursos
            SET nombre = ?, turno = ?
            WHERE id_curso = ?
        """, (
            nombre.get(),
            turno.get(),
            id_seleccionado
        ))

        conn.commit()
        conn.close()

        cargar_datos_treeview()
        limpiar_campos()
        messagebox.showinfo("Éxito", "Curso actualizado", parent=ventana)
    # -------------------------------------------------------------------------------------

    # ----------------  Elimina registros de profesores ----------------------------------
    def eliminar_curso():
        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro", parent=ventana)
            return

        confirmar = messagebox.askyesno("Confirmar", "¿Eliminar registro?", parent=ventana)
        if not confirmar:
            return

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cursos WHERE id_curso = ?", (id_seleccionado,))
            conn.commit()
        except Exception as e:
          print(e)
          messagebox.showerror("ERROR", f"NO se pudo eliminar el registro.\nEstá vinculado con otros datos", parent=ventana)
          conn.close()

        cargar_datos_treeview()
        limpiar_campos()
    #---------------------------------------------------------------------------------------


    # -------------------- BÚSQUEDA POR LETRA INICIAL EN LA TABLA  -------------------------
    texto_busqueda = ""

    texto_busqueda = ""
    ultimo_tiempo = 0

    def buscar_treeview(event):
        nonlocal texto_busqueda, ultimo_tiempo

        import time
        ahora = time.time()

        # Si pasa más de 1 segundo → reinicia búsqueda
        if ahora - ultimo_tiempo > 1:
            texto_busqueda = ""

        ultimo_tiempo = ahora

        if not event.char.isalpha():
            return

        texto_busqueda += event.char.lower()

        items = tree.get_children()

        # desde dónde empezar (posición actual)
        seleccion = tree.selection()
        start_index = 0

        if seleccion:
            start_index = items.index(seleccion[0]) + 1

        # recorrer desde la posición actual hacia abajo
        for i in range(len(items)):
            idx = (start_index + i) % len(items)  # 🔥 ciclo

            item = items[idx]
            valores = tree.item(item, "values")
            apellido = valores[1].lower()

            if apellido.startswith(texto_busqueda):
                tree.selection_set(item)
                tree.focus(item)
                tree.see(item)
                break
    tree.bind("<Key>", buscar_treeview)
    # ---------------------------------------------------------------------------------------



     # -------------- Limpia los Entrys de datos ingresados y/o seleccionados ------------------------------
    def limpiar_campos():
        nonlocal id_seleccionado
        nombre.set("")
        turno.set("")
      
    #-----------------------------------------------------------------------------------------------------


    # --------------------------- Botones que permiten agregar, modificar etc. ---------------------------
    ttk.Button(frame_botones, text="Agregar", command=agregar_cursos).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="Modificar", command=modificar_curso).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="Eliminar", command=eliminar_curso).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="Limpiar", command=limpiar_campos).grid(row=0, column=3, padx=5)
    ttk.Button(frame_botones, text="Cerrar", command=ventana.destroy).grid(row=0, column=4, padx=5)
    # ----------------------------------------------------------------------------------------------------

    centrar_ventana(ventana)  #centra pantalla Cursos
    cargar_datos_treeview()
    crear_backup()