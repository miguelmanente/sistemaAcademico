# ========================================================================================
#                  MÓDULO PARA CARGAR DATOS PERSONALES DE LOS DOCENTES
# ========================================================================================

# ---------------------  Área de declaración de librerías --------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import re
from tkinter import font
from database import conectar
from centraVent import centrar_ventana
from estilos import configurar_estilos
from backup import crear_backup

# ----------- Función que maneja toda la ventana datos personales del profesor ------------
def info_profesor():

    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Datos personales del profesor")
    ventana.geometry("900x500")

    # Configuración del grid de la ventana principal
    ventana.rowconfigure(0, weight=1)  # Parte superior
    ventana.rowconfigure(1, weight=2)  # Parte inferior
    ventana.columnconfigure(0, weight=1)

    # =========================
    # FRAME SUPERIOR (ENTRYS)
    # =========================
    frame_superior = ttk.LabelFrame(ventana, text="Datos del Profesor", padding=10)
    frame_superior.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Configurar columnas del frame superior
    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # Variables
    apellido_nombre = tk.StringVar()
    dni = tk.StringVar()
    cuil = tk.StringVar()
    telefono = tk.StringVar()
    email = tk.StringVar()
    situacion_revista = tk.StringVar()
    fecha_toma = tk.StringVar()
    

    # -------------- Labels y Entrys distribuidos en dos columnas ------------------------------------------
    ttk.Label(frame_superior, text="Apellido y Nombres:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=apellido_nombre, font=("Arial", 12)).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
 
    style = ttk.Style()

    style.configure("Valido.TEntry", foreground="black")
    style.configure("Error.TEntry", foreground="black")
    style.map("Error.TEntry",
            fieldbackground=[("!disabled", "#ffcccc")])  # rojo claro
    
    #Verificación e ingreso de número en DNI
    ttk.Label(frame_superior, text="DNI:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
   
    # --------------------------  VERIFICA DATOS INGRESO EN DNI --------------------------------------------
    def solo_numeros(P):
        return P.isdigit() or P == ""

    vcmd = (ventana.register(solo_numeros), '%P')
    # --------------------------------------------------------------------------------------------------------------

    entry_dni = ttk.Entry(frame_superior, textvariable=dni, validate="key", validatecommand=vcmd, style="Valido.TEntry", font=("Arial", 12))
    entry_dni.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="CUIL:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=cuil, font=("Arial", 12)).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Teléfono:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=telefono, font=("Arial", 12)).grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    #ttk.Entry(frame_superior, textvariable=email).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
    entry_email = ttk.Entry(frame_superior, textvariable=email, style="Valido.TEntry", font=("Arial", 12))
    entry_email.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Situación de Revista:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=situacion_revista,  font=("Arial", 12)).grid(row=2, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Fecha Toma de Posesión:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    #ttk.Entry(frame_superior, textvariable=fecha_toma).grid(row=2, column=3, sticky="ew", padx=5, pady=5)

    entry_fecha = ttk.Entry(frame_superior, textvariable=fecha_toma, font=("Arial", 12))
    entry_fecha.grid(row=3, column=1, sticky="ew", padx=5, pady=5)


    

    # =========================
    # BOTONES
    # =========================
    frame_botones = ttk.Frame(frame_superior)
    frame_botones.grid(row=4, column=0, columnspan=4, pady=10)

    # =========================
    # FRAME INFERIOR (TREEVIEW)
    # =========================
    frame_inferior = ttk.LabelFrame(ventana, text="Listado de Profesores", padding=10)
    frame_inferior.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Configuración del grid del frame inferior
    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    #Columnas del Treeview
    columnas = ("id_profesor","apenom", "dni", "cuil", "telefono", "email", "sitrev", "fechatp")

    tree = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    # Encabezados
    tree.heading("id_profesor", text="ID")
    tree.heading("apenom", text="Apellido y Nombres")
    tree.heading("dni", text="DNI")
    tree.heading("cuil", text="CUIL")
    tree.heading("telefono", text="Teléfono")
    tree.heading("email", text="Email")
    tree.heading("sitrev", text="Situación de Revista")
    tree.heading("fechatp", text="Fecha Toma de Posesión")
    
    
    tree.column("id_profesor", width=0, stretch=False)
    tree.column("apenom", width=150, anchor="w")
    tree.column("dni", width=70, anchor="center")
    tree.column("cuil", width=70, anchor="center")
    tree.column("telefono", width=70, anchor="center")
    tree.column("email", width=120, anchor="w")
    tree.column("sitrev", width=70, anchor="center")
    tree.column("fechatp", width=70, anchor="center")
    

    # Scrollbars
    scrollbar_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(frame_inferior, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Ubicación en el grid
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    
    # ================================================================================
    #    FUNCIONES Agregar, modificar, eliminar. limpiar campos y salir de la ventana 
    # ================================================================================
  
    #----------------------  Funciones que chequean DNI y Email ----------------------
    def marcar_error(entry):
        entry.config(style="Error.TEntry")

    def marcar_valido(entry):
        entry.config(style="Valido.TEntry")
    # --------------------------------------------------------------------------------
    
    #--------------- Validación de dni ---------------------------------------------
    def validar_dni(dni):
         return dni.isdigit() and len(dni) in (7, 8)
   
    # Coloca en rojo la caja hasta que haya error en la escriyura del dni
    def validar_dni_evento(event):
        valor = dni.get()
        if valor.isdigit() and len(valor) in (7, 8):
            marcar_valido(entry_dni)
        else:
            marcar_error(entry_dni)

    entry_dni.bind("<KeyRelease>", validar_dni_evento)
    #-------------------------------------------------------------------------------
    
    # ----------------------- Validación de correo electrónico ------------------------
    def validar_email(valor):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, valor) is not None
    
    # Coloca en rojo la caja hasta que haya error en la escritura del correo
    def validar_email_evento(event):
        valor = email.get()
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if re.match(patron, valor) or valor == "":
            marcar_valido(entry_email)
        else:
            marcar_error(entry_email)

    entry_email.bind("<KeyRelease>", validar_email_evento)

    # --------------------------------------------------------------------------------
   
    # ---  Función que permite selecccionar un registro en el treview ------------------
    id_seleccionado = None

    def seleccionar_registro(event):
        nonlocal id_seleccionado

        item = tree.selection()
        if not item:
            return

        valores = tree.item(item[0], "values")

        id_seleccionado = valores[0]  # 👈 ESTE ES EL CLAVE

        apellido_nombre.set(valores[1])
        dni.set(valores[2])
        cuil.set(valores[3])
        telefono.set(valores[4])
        email.set(valores[5])
        situacion_revista.set(valores[6])
        fecha_toma.set(valores[7])

    tree.bind("<<TreeviewSelect>>", seleccionar_registro) 
    # ---------------------------------------------------------------------------------

    # ----------------- Carga y muestra los registros carado en la BD -----------------
    def cargar_datos_treeview():
        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_profesor, apenom, dni, cuil, telefono, email, sitrev, fechatp
            FROM profesores
            ORDER BY apenom
        """)

        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

        conn.close()
    # ----------------------------------------------------------------------------------

    # ------------------------ Añade registros nuevos a la BD profesores ---------------
    def agregar_datos():
        if not apellido_nombre.get() or not dni.get():
            messagebox.showwarning(
                "Campos obligatorios",
                "Apellido y Nombres y DNI son obligatorios.", parent=ventana)
            return

        # ✅ VALIDAR DNI
        if not validar_dni(dni.get()):
            messagebox.showerror("Error", "DNI inválido (solo números, 7 u 8 dígitos)", parent=ventana)
            return

        # ✅ VALIDAR EMAIL (solo si hay algo cargado)
        if email.get() and not validar_email(email.get()):
            messagebox.showerror("Error", "Email inválido", parent=ventana)
            return
        
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO profesores (apenom, dni, cuil, telefono, email, sitrev, fechatp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                apellido_nombre.get(),
                dni.get(),
                cuil.get(),
                telefono.get(),
                email.get(),
                situacion_revista.get(),
                fecha_toma.get()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Datos guardados correctamente.", parent=ventana)

            cargar_datos_treeview()
           

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos:\n{e}", parent=ventana)
    # ----------------------------------------------------------------------------------
      
    # ----------------  Modifica registro de profesores --------------------------------
    def modificar_registro():
        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro", parent=ventana)
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE profesores
            SET apenom = ?, dni = ?, cuil = ?, telefono = ?, email = ?, sitrev = ?, fechatp = ?
            WHERE id_profesor = ?
        """, (
            apellido_nombre.get(),
            dni.get(),
            cuil.get(),
            telefono.get(),
            email.get(),
            situacion_revista.get(),
            fecha_toma.get(),
            id_seleccionado
        ))

        conn.commit()
        conn.close()

        cargar_datos_treeview()
        limpiar_campos()
        messagebox.showinfo("Éxito", "Registro actualizado", parent=ventana)
    # -------------------------------------------------------------------------------------

    # ----------------  Elimina registros de profesores ----------------------------------
    def eliminar_registro():
        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro", parent=ventana)
            return

        confirmar = messagebox.askyesno("Confirmar", "¿Eliminar registro?", parent=ventana)
        if not confirmar:
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM profesores WHERE id_profesor = ?", (id_seleccionado,))

        conn.commit()
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

    # -------------- Limpia los Entrys de datos ingresados y/o seleccionados ----------------
    def limpiar_campos():
        nonlocal id_seleccionado
        apellido_nombre.set("")
        dni.set("")
        cuil.set("")
        telefono.set("")
        email.set("")
        situacion_revista.set("")
        fecha_toma.set("")
    #------------------------------------------------------------------------------------------
    crear_backup()
    centrar_ventana(ventana)
    cargar_datos_treeview()
    # --------------------------- Botones que permiten agregar, modificar etc. ---------------------------
    ttk.Button(frame_botones, text="Agregar", command=agregar_datos).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="Modificar", command=modificar_registro).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="Eliminar", command=eliminar_registro).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="Limpiar", command=limpiar_campos).grid(row=0, column=3, padx=5)
    ttk.Button(frame_botones, text="Cerrar", command=ventana.destroy).grid(row=0, column=4, padx=5)
    # ----------------------------------------------------------------------------------------------------
  