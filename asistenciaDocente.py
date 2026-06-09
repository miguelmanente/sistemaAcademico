#===========================================================
#             MÓDULO DE ASISTENCIA DOCENTE
#===========================================================

# ======================   LIBRERÍAS =======================
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from datetime import datetime, timedelta
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os
from backup import crear_backup
from estilos import configurar_estilos

# ================== VENTANA DE INASISTENCIA ==========================
def ventana_asistencias():
    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Control de Inasistencias")
    ventana.geometry("1200x700")
    ventana.rowconfigure(1, weight=1)
    ventana.columnconfigure(0, weight=1)

    # =============== VARIABLES ====================================
    profesor_var = tk.StringVar()
    desde_var = tk.StringVar()
    hasta_var = tk.StringVar()
    estado_var = tk.StringVar()
    observacion_var = tk.StringVar()
    profesores_dict = {}
    id_seleccionado = None

    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12)) 

    # ============ FRAME SUPERIOR =================================
    frame = ttk.LabelFrame(ventana, text="Inasistencia Docente")
    frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

    # ================ COMBO PROFESORES ============================
    ttk.Label(frame, text="Profesor", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
    combo_profesor = ttk.Combobox(frame, textvariable=profesor_var, width=40, state="readonly")
    combo_profesor.grid(row=0, column=1, padx=5, pady=5)

    # ====================  INGRESOS DE FECHAS ========================
    ttk.Label(
        frame,
        text="Desde", font=("Arial", 12)
    ).grid(row=1, column=0)

    ttk.Entry(
        frame,
        textvariable=desde_var, font=("Arial", 12)
    ).grid(row=1, column=1)


    ttk.Label(
        frame,
        text="Hasta", font=("Arial", 12)
    ).grid(row=1, column=2)

    ttk.Entry(
        frame,
        textvariable=hasta_var, font=("Arial", 12)
    ).grid(row=1, column=3)

    # ========================== ESTADO =============================
    ttk.Label(
        frame,
        text="Estado", font=("Arial", 12)
    ).grid(row=2, column=0)

    combo_estado = ttk.Combobox(

        frame,

        textvariable=estado_var,

        values=[
            "",
            "Presente",
            "Ausente",
            "Licencia Médica",
            "ART",
            "Particular",
            "Maternidad",
            "Estudio"

        ],

        state="readonly",

        width=30
    )

    combo_estado.grid(
        row=2,
        column=1,
        padx=5,
        pady=5
    )

    # =========================== OBSERVACIONES ==========================
    ttk.Label(
        frame,
        text="Observación", font=("Arial", 12)
    ).grid(row=3, column=0)

    ttk.Entry(
        frame,
        textvariable=observacion_var, font=("Arial", 12),
        width=80
    ).grid(
        row=3,
        column=1,
        columnspan=3,
        padx=5,
        pady=5
    )
    # =================================================================
    # CONTENEDOR PARA EL TREEVIEW Y SCROLLBARS (Fila 1 de la ventana)
    # =================================================================
    frame_tabla = ttk.Frame(ventana)
    frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # Configuramos el peso dentro del nuevo frame para que el treeview se estire
    frame_tabla.rowconfigure(0, weight=1)
    frame_tabla.columnconfigure(0, weight=1)

    # ============================= TREEVIEW ============================
    columnas = ("id", "profesor", "desde", "hasta", "dias", "estado", "observacion")
    
    # IMPORTANTE: Ahora el padre de tree es 'frame_tabla'
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    # Encabezados
    tree.heading("id", text="ID")
    tree.heading("profesor", text="Profesor")
    tree.heading("desde", text="Desde el Día")
    tree.heading("hasta", text="Hasta el Día")
    tree.heading("dias", text="Cant.de Dias")
    tree.heading("estado", text="Estado")
    tree.heading("observacion", text="Observación")
   
    # Configuración de columnas
    tree.column("id", width=0, stretch=False)
    tree.column("profesor", width=150, anchor="center")
    tree.column("desde", width=100, anchor="center")
    tree.column("hasta", width=100, anchor="center")
    tree.column("dias", width=50, anchor="center")
    tree.column("estado", width=100, anchor="center")
    tree.column("observacion", width=200, anchor="w")

    # ============================= SCROLLBARS ============================
    # IMPORTANTE: El padre de los scrollbars también es 'frame_tabla'
    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
    
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Ubicación de los componentes DENTRO del frame_tabla
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    # ==========================================================
    # ==========  RESUMEN DE INASISTENCIAS POR PROFESOR ========================
    lbl_resumen = ttk.Label(ventana, text="Resumen de inasistencias: ", font=("Arial", 11, "bold"), foreground="blue")
    lbl_resumen.grid(row=3, column=0, sticky="w", padx=10, pady=5)

    # =========== MENSAJES DE ALERTAS CUANDO SE SUPERAN LÍMITES ================
    lbl_alerta = ttk.Label(ventana, text="", font=("Arial", 11, "bold"), foreground="red")
    lbl_alerta.grid(row=4, column=0, sticky="w", padx=10, pady=5)

    # ============== Cantidad de días trabajados ===============================
    lbl_trabajados = ttk.Label(ventana, text="Días trabajados: 0", font=("Arial", 11, "bold"), foreground="green")
    lbl_trabajados.grid(row=5, column=0, sticky="w", padx=10, pady=5)

    # =========================  CARGA DE PROFESORES ============================
    def cargar_profesores():

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id_profesor,
                apenom
            FROM profesores
            ORDER BY apenom
        """)

        resultados = cursor.fetchall()

        profesores_dict.clear()

        lista = [""]

        for id_profesor, nombre in resultados:

            profesores_dict[nombre] = id_profesor
            lista.append(nombre)

        combo_profesor["values"] = lista

        conn.close()

    # -----------------------------------------------------------

    # ======================= CALCULA LOS DÍAS DE INASISTENCIAS =====================
    def calcular_dias(id_profesor, desde, hasta):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""

            SELECT DISTINCT h.dia

            FROM asignaciones_docentes a

            JOIN horarios h
            ON a.id_horario = h.id_horario

            WHERE a.id_profesor = ?

        """, (id_profesor,))

        resultados = cursor.fetchall()

        conn.close()

        dias_trabajo = [fila[0] for fila in resultados]

        mapa = {
            "Lunes": 0,
            "Martes": 1,
            "Miércoles": 2,
            "Jueves": 3,
            "Viernes": 4
        }

        dias_validos = []

        for dia in dias_trabajo:

            if dia in mapa:
                dias_validos.append(mapa[dia])

        fecha_actual = datetime.strptime(
            desde,
            "%d/%m/%Y"
        )

        fecha_hasta = datetime.strptime(
            hasta,
            "%d/%m/%Y"
        )

        total = 0

        while fecha_actual <= fecha_hasta:

            if fecha_actual.weekday() in dias_validos:
                total += 1

            fecha_actual += timedelta(days=1)

        return total
        
   # ================= CONTAR DÍAS LABORALES ============================
    def contar_dias_laborales(id_profesor):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""

            SELECT DISTINCT h.dia

            FROM asignaciones_docentes a

            JOIN horarios h
            ON a.id_horario = h.id_horario

            WHERE a.id_profesor = ?

        """, (id_profesor,))

        resultados = cursor.fetchall()

        conn.close()

        dias_trabajo = [fila[0] for fila in resultados]

        dias_map = {
            "Lunes": 0,
            "Martes": 1,
            "Miércoles": 2,
            "Jueves": 3,
            "Viernes": 4
        }

        fecha_inicio = datetime.strptime(
            "01/03/2026",
            "%d/%m/%Y"
        )

        fecha_fin = datetime.today()

        total = 0

        while fecha_inicio <= fecha_fin:

            dias_validos = []

            for dia in dias_trabajo:

                if dia == "Lunes a Viernes":

                    dias_validos.extend([0, 1, 2, 3, 4])

                elif dia in dias_map:

                    dias_validos.append(dias_map[dia])

            if fecha_inicio.weekday() in dias_validos:

                total += 1

            fecha_inicio += timedelta(days=1)

        return total
    # -----------------------------------------------------------------------
    
    # ================== GUARDAR DATOS =====================================
    def guardar():

        conn = conectar()
        cursor = conn.cursor()

        id_profesor = profesores_dict[
            profesor_var.get()
        ]

        cursor.execute("""

            INSERT INTO asistencias_docentes(

                id_profesor,
                fecha_desde,
                fecha_hasta,
                estado,
                observacion

            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            id_profesor,
            desde_var.get(),
            hasta_var.get(),
            estado_var.get(),
            observacion_var.get()

        ))

        conn.commit()
        conn.close()

        dias = calcular_dias(
            id_profesor,
            desde_var.get(),
            hasta_var.get()
        )

        if dias >= 5:

            messagebox.showwarning(

                "ALERTA SUPLENTE",

                "El docente supera 5 días de inasistencia",
                parent=ventana

            )

        messagebox.showinfo(
            "OK",
            "Registro guardado",
            parent=ventana
        )

        cargar_tree()
        actualizar_pantalla()
        limpiar()

    # ------------------------------------------------------------

    # ============== MODIFICAR REGISTRO ASISTENCIA ===============
    def modificar():

        nonlocal id_seleccionado

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro",
                parent=ventana
            )

            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""

            UPDATE asistencias_docentes
            SET

                id_profesor=?,
                fecha_desde=?,
                fecha_hasta=?,
                estado=?,
                observacion=?

            WHERE id_asistencia=?

        """, (

            profesores_dict[profesor_var.get()],
            desde_var.get(),
            hasta_var.get(),
            estado_var.get(),
            observacion_var.get(),
            id_seleccionado

        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "OK",
            "Registro modificado",
            parent=ventana
        )

        cargar_tree()
        actualizar_pantalla()
        limpiar()

    # ------------------------------------------------------------

    # ===================== ELIMINAR =====================
    def eliminar():

        nonlocal id_seleccionado

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro", parent=ventana
            )

            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Eliminar registro?", parent=ventana
        )

        if not confirmar:
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""

            DELETE FROM asistencias_docentes
            WHERE id_asistencia=?

        """, (id_seleccionado,))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "OK",
            "Registro eliminado", parent=ventana
        )

        cargar_tree()
        actualizar_pantalla()
        limpiar()
    # ------------------------------------------------------------
    
    # ===================== CARGAR TREEVIEW =====================
    def cargar_tree(id_profesor=None):

        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        query = """

            SELECT

                a.id_asistencia,
                a.id_profesor,
                p.apenom,
                a.fecha_desde,
                a.fecha_hasta,
                a.estado,
                a.observacion

            FROM asistencias_docentes a

            JOIN profesores p
            ON a.id_profesor = p.id_profesor

        """

        parametros = []

        if id_profesor:

            query += " WHERE a.id_profesor = ?"

            parametros.append(id_profesor)

        query += " ORDER BY a.fecha_desde DESC"

        cursor.execute(query, parametros)

        registros = cursor.fetchall()

        for fila in registros:

            dias = calcular_dias(

                fila[1],  # id_profesor
                fila[3],  # fecha_desde
                fila[4]   # fecha_hasta

            )

            nueva = [

                fila[0],   # id_asistencia
                fila[2],   # nombre profesor
                fila[3],   # desde
                fila[4],   # hasta
                dias,
                fila[5],   # estado
                fila[6]    # observacion

            ]

            tree.insert(
                "",
                "end",
                values=nueva
            )

        conn.close()

    # ------------------------------------------------------------------

    # ============ SELECCIONAR REGISTROS DEL TREEVIEW ==============
    def seleccionar(event):

        nonlocal id_seleccionado

        item = tree.selection()

        if not item:
            return

        valores = tree.item(item[0], "values")

        id_seleccionado = valores[0]

        profesor_var.set(valores[1])

        desde_var.set(valores[2])
        hasta_var.set(valores[3])
        estado_var.set(valores[5])
        observacion_var.set(valores[6])

    tree.bind("<<TreeviewSelect>>", seleccionar)
    # --------------------------------------------------------------

    #  ================  RESUMEN DE INASISTENCIAS ==================
    def resumen_inasistencias(id_profesor):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                estado,
                fecha_desde,
                fecha_hasta
            FROM asistencias_docentes
            WHERE id_profesor = ?
        """, (id_profesor,))

        registros = cursor.fetchall()

        conn.close()

        resumen = {}
        total_general = 0

        for estado, desde, hasta in registros:

            dias = calcular_dias(
                id_profesor,
                desde,
                hasta
            )

            if estado not in resumen:
                resumen[estado] = 0

            resumen[estado] += dias
            total_general += dias

        texto = ""

        for estado, dias in resumen.items():

            texto += f"{estado}: {dias} días\n"

        texto += f"\nTOTAL GENERAL: {total_general} días"

        lbl_resumen.config(text=texto)

    # ------------------------------------------------------------------------------

    # ================= TOTAL INASISTENCIAS =================
    def total_inasistencias(id_profesor):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                fecha_desde,
                fecha_hasta
            FROM asistencias_docentes
            WHERE id_profesor = ?
        """, (id_profesor,))

        registros = cursor.fetchall()

        conn.close()

        total = 0

        for desde, hasta in registros:

            total += calcular_dias(
                id_profesor,
                desde,
                hasta
            )

        return total
    # ------------------------------------------------------------

    # ==================== BUSCA DOCENTES ===================
    def buscar_docente():

        if profesor_var.get() == "":

            messagebox.showwarning(
                "Atención",
                "Seleccione un profesor",
                parent=ventana
            )

            return

        id_profesor = profesores_dict[
            profesor_var.get()
        ]

        cargar_tree(id_profesor)

        resumen_inasistencias(id_profesor)

        verificar_alertas(id_profesor)

        # =====================================
        # CALCULAR DÍAS TRABAJADOS
        # =====================================

        laborales = contar_dias_laborales(
            id_profesor
        )

        faltas = total_inasistencias(
            id_profesor
        )

        trabajados = laborales - faltas

        porcentaje = round(
            (trabajados / laborales) * 100,
            2
        )

        lbl_trabajados.config(

            text=(
                f"Días laborales: {laborales} | "
                f"Trabajados: {trabajados} | "
                f"Presentismo: {porcentaje}%"
            )

        )

    # --------------------------------------------------------------

    # ==================  FUNCIÓN DE ALERTAS =======================
    def verificar_alertas(id_profesor):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                estado,
                fecha_desde,
                fecha_hasta
            FROM asistencias_docentes
            WHERE id_profesor = ?
        """, (id_profesor,))

        registros = cursor.fetchall()

        conn.close()

        licencia_medica = 0
        particular = 0

        dias_totales = set()

        for estado, desde, hasta in registros:

            dias = calcular_dias(
                id_profesor,
                desde,
                hasta
            )

            if estado == "Licencia Médica":
                licencia_medica += dias

            if estado == "Particular":
                particular += dias

            fecha_actual = datetime.strptime(
                desde,
                "%d/%m/%Y"
            )

            fecha_hasta = datetime.strptime(
                hasta,
                "%d/%m/%Y"
            )

            while fecha_actual <= fecha_hasta:

                dias_totales.add(
                    fecha_actual.strftime("%d/%m/%Y")
                )

                fecha_actual += timedelta(days=1)

        alertas = ""

        if licencia_medica >= 20:

            alertas += (
                f"⚠ Supera 20 días de Licencia Médica "
                f"({licencia_medica} días)\n"
            )

        if particular >= 5:

            alertas += (
                f"⚠ Supera 5 faltas particulares "
                f"({particular} días)\n"
            )

        if len(dias_totales) > 5:

            alertas += (
                f"⚠ Necesita suplente ({len(dias_totales)} días)\n"
            )

        if alertas == "":
            alertas = "Sin alertas"

        lbl_alerta.config(text=alertas)

    # -----------------------------------------------------------------

    # ====================== ACTUALIZA PANTALLA ========================
    def actualizar_pantalla():

        if profesor_var.get() == "":
            return

        id_profesor = profesores_dict[
            profesor_var.get()
        ]

        cargar_tree(id_profesor)

        resumen_inasistencias(id_profesor)

        verificar_alertas(id_profesor)

        laborales = contar_dias_laborales(
            id_profesor
        )

        faltas = total_inasistencias(
            id_profesor
        )

        trabajados = laborales - faltas

        porcentaje = round(
            (trabajados / laborales) * 100,
            2
        ) if laborales > 0 else 0

        lbl_trabajados.config(
            text=(
                f"Días laborales: {laborales} | "
                f"Trabajados: {trabajados} | "
                f"Presentismo: {porcentaje}%"
            )
        )
    # ------------------------------------------------------------------


    # ================  GENERAR PDFS DE INASISTENCIAS MENSUALES ========
    def pdf_mensual():

        profesor = profesor_var.get()

        if profesor == "":

            messagebox.showwarning(
                "Atención",
                "Seleccione un profesor", parent = ventana
            )

            return

        id_profesor = profesores_dict[profesor]

        mes_actual = datetime.now().month
        anio_actual = datetime.now().year

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                p.apenom,
                a.fecha_desde,
                a.fecha_hasta,
                a.estado

            FROM asistencias_docentes a

            JOIN profesores p
            ON a.id_profesor = p.id_profesor

            WHERE a.id_profesor = ?

        """, (id_profesor,))

        registros = cursor.fetchall()

        if not registros:

            messagebox.showwarning("Atención", "El docente no posee inasistencias registradas", parent=ventana)
            return
        
        conn.close()

        nombre_pdf = (
            f"Inasist_Mens_{profesor}.pdf"
        )

        ruta_pdf = os.path.join(
            "reportes",
            "pdf",
            nombre_pdf
        )

        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4
        )

        styles = getSampleStyleSheet()

        elementos = []

        titulo = Paragraph(

            f"<b>INFORME MENSUAL DE ASISTENCIAS</b>",

            styles["Title"]

        )

        elementos.append(titulo)

        elementos.append(Spacer(1, 20))

        nombre_docente = registros[0][0]

        subtitulo = Paragraph(

            f"""
            <b>Docente:</b> {nombre_docente}<br/>
            <b>Mes:</b> {mes_actual}/{anio_actual}
            """,

            styles["BodyText"]

        )

        elementos.append(subtitulo)

        elementos.append(Spacer(1, 20))

        data = [[

            "Desde",
            "Hasta",
            "Días",
            "Estado"

        ]]

        total = 0

        for fila in registros:

          dias = calcular_dias(
            id_profesor,
            fila[1],
            fila[2]
        )

        total += dias

        data.append([

            fila[1],   # desde
            fila[2],   # hasta
            str(dias),
            fila[3]    # estado
        ])

        tabla = Table(data)

        tabla.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),

            ('TEXTCOLOR', (0,0), (-1,0), colors.white),

            ('GRID', (0,0), (-1,-1), 1, colors.black),

            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')

        ]))

        elementos.append(tabla)

        elementos.append(Spacer(1, 20))

        total_parrafo = Paragraph(

            f"<b>TOTAL DE INASISTENCIAS:</b> {total} días",

            styles["Heading2"]

        )

        elementos.append(total_parrafo)

        doc.build(elementos)

        messagebox.showinfo(

            "PDF",

            f"Reporte generado:\n{ruta_pdf}", parent=ventana

        )
    # ----------------------------------------------------------------
    
    #=====================  PDF ANUAL ASISTENCIA DOCENTE =============
    def pdf_anual():
        profesor = profesor_var.get()
        if profesor == "":
            messagebox.showwarning(
                "Atención",
                "Seleccione un profesor"
            )
            return

        id_profesor = profesores_dict[profesor]
        anio_actual = datetime.now().year
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""

            SELECT

                p.apenom,
                a.fecha_desde,
                a.fecha_hasta,
                a.estado

            FROM asistencias_docentes a

            JOIN profesores p
            ON a.id_profesor = p.id_profesor

            WHERE a.id_profesor = ?

            ORDER BY a.fecha_desde

        """, (id_profesor,))

        registros = cursor.fetchall()
        conn.close()

        if not registros:
            messagebox.showwarning(
                "Atención",
                "No hay registros"
            )
            return
        nombre_docente = registros[0][0]
        nombre_pdf = (
            f"RepAnu_{nombre_docente}.pdf"
        )
        ruta_pdf = os.path.join(
            "reportes",
            "pdf",
            nombre_pdf
        )

        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4
        )

        styles = getSampleStyleSheet()
        elementos = []

        # ======================================
        # TITULO
        # ======================================
        titulo = Paragraph(
            f"<b>INFORME ANUAL DE ASISTENCIAS</b>",
            styles["Title"]
        )

        elementos.append(titulo)
        elementos.append(Spacer(1, 20))
        subtitulo = Paragraph(
            f"""
            <b>Docente:</b> {nombre_docente}<br/>
            <b>Año:</b> {anio_actual}
            """,
            styles["BodyText"]
        )

        elementos.append(subtitulo)
        elementos.append(Spacer(1, 20))

        # ======================================
        # TABLA
        # ======================================

        data = [[
            "Mes",
            "Desde",
            "Hasta",
            "Días",
            "Estado"
        ]]

        total = 0
        resumen_estados = {}

        for fila in registros:
            fecha = datetime.strptime(
                fila[1],
                "%d/%m/%Y"
            )   
            
            mes = fecha.strftime("%B")

            dias = calcular_dias(
                id_profesor,
                fila[1],
                fila[2]
            )

            total += dias

            estado = fila[3]

            if estado not in resumen_estados:

                resumen_estados[estado] = 0

            resumen_estados[estado] += dias
        
        data.append([
            mes,
            fila[1],
            fila[2],
            str(dias),
            estado
        ])

        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 20))

        # ======================================
        # RESUMEN
        # ======================================

        resumen = "<b>RESUMEN ANUAL</b><br/><br/>"
        for estado, dias in resumen_estados.items():
            resumen += f"{estado}: {dias} días<br/>"
        resumen += f"<br/><b>TOTAL ANUAL:</b> {total} días"
        resumen_parrafo = Paragraph(
            resumen,
            styles["BodyText"]
        )

        elementos.append(resumen_parrafo)
        doc.build(elementos)
        messagebox.showinfo(
            "PDF",
            f"PDF anual generado:\n{ruta_pdf}", parent=ventana

        )
    # --------------------------------------------------------------

    # =====================  LIMPIAR ENTRYS ========================
    def limpiar():

        nonlocal id_seleccionado

        id_seleccionado = None

        profesor_var.set("")
        desde_var.set("")
        hasta_var.set("")
        estado_var.set("")
        observacion_var.set("")
    
    # ======================  BOTONES =============================
    frame_btn = ttk.Frame(ventana)
    frame_btn.grid(row=2, column=0, pady=10)

    # Botón agregar
    ttk.Button(frame_btn, text="💾 Guardar", command=guardar).grid(row=0, column=0, padx=5)
    # Botón Modificar
    ttk.Button(frame_btn, text="✏ Modificar", command=modificar).grid(row=0, column=1, padx=5)
    # Botón Eliminar
    ttk.Button(frame_btn, text="🗑 Eliminar", command=eliminar).grid(row=0, column=2, padx=5)
    # Botón Limpiar entrys
    ttk.Button(frame_btn, text="🧹 Limpiar", command=limpiar).grid(row=0, column=3, padx=5)
    # Botón Buscar Docente
    ttk.Button(frame_btn, text="🔍 Buscar Docente", command=buscar_docente).grid(row=0, column=4, padx=5)
    # Botón PDF mensual
    ttk.Button(frame_btn, text="📄 PDF Mensual", command=pdf_mensual).grid(row=0, column=5, padx=5)
    # Botón PDF anual
    ttk.Button(frame_btn, text="📘 PDF Anual", command=pdf_anual).grid(row=0, column=6, padx=5)
    # Botón Cerrar
    ttk.Button(frame_btn, text="❌ Cerrar", command=ventana.destroy).grid(row=0, column=7, padx=5)

    cargar_profesores()

    cargar_tree()

    centrar_ventana(ventana)
    crear_backup()