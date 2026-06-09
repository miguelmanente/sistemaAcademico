# =====================================================
#            MÓDULO HISTORIAL DOCENTE
# =====================================================

# ------------------   LIBRERÍAS ----------------------
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from datetime import datetime
import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from estilos import configurar_estilos

def ventana_historial():

    ventana = tk.Toplevel()
    from estilos import configurar_estilos
    ventana.title("Historial Docente")
    ventana.geometry("1200x700")

    ventana.rowconfigure(1, weight=1)
    ventana.columnconfigure(0, weight=1)

    # =====================================================
    #                   VARIABLES
    # =====================================================

    profesor_var = tk.StringVar()
    materia_var = tk.StringVar()
    curso_var = tk.StringVar()
    situacion_var = tk.StringVar()
    inicio_var = tk.StringVar()
    fin_var = tk.StringVar()
    antiguedad_var =tk.StringVar()
    observacion_var = tk.StringVar()

    profesores_dict = {}
    materias_dict = {}
    cursos_dict = {}

    id_seleccionado = None
    buscar_var = tk.StringVar()
    filtro_situacion = tk.StringVar()

    # =====================================================
    #                 FRAME SUPERIOR
    # =====================================================
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12)) 

    frame = ttk.LabelFrame(ventana, text="Datos Historial")
    frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

    # PROFESOR
    ttk.Label(frame, text="Profesor", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=10)

    combo_profesor = ttk.Combobox(frame, textvariable=profesor_var, width=40, state="readonly")
    combo_profesor.grid(row=0, column=1, padx=5, pady=10)

    # MATERIA
    ttk.Label(frame, text="Materia", font=("Arial", 12)).grid(row=0, column=2, pady=10)

    combo_materia = ttk.Combobox(frame, textvariable=materia_var, width=30, state="readonly")
    combo_materia.grid(row=0, column=3, padx=10)

    # CURSO
    ttk.Label(frame, text="Curso", font=("Arial", 12)).grid(row=1, column=0, pady=10)

    combo_curso = ttk.Combobox(frame, textvariable=curso_var, width=30, state="readonly")
    combo_curso.grid(row=1, column=1, padx=10)

    # SITUACION
    ttk.Label(frame, text="Situación", font=("Arial", 12)).grid(row=1, column=2, pady=10)

    combo_situacion = ttk.Combobox(
        frame,
        textvariable=situacion_var,
        values=["Titular", "Provisorio", "Suplente"],
        state="readonly",
        font=("Arial", 12)
    )

    combo_situacion.grid(row=1, column=3)

    # FECHA INICIO
    ttk.Label(frame, text="Fecha Inicio", font=("Arial", 12)).grid(row=2, column=0, pady=10)
    ttk.Entry(frame, textvariable=inicio_var, font=("Arial", 12)).grid(row=2, column=1, pady=10)

    # FECHA FIN
    ttk.Label(frame, text="Fecha Fin", font=("Arial", 12)).grid(row=2, column=2, pady=10)
    ttk.Entry(frame, textvariable=fin_var, font=("Arial", 12)).grid(row=2, column=3, pady=10)

    # OBSERVACIONES
    ttk.Label(frame, text="Observaciones", font=("Arial", 12)).grid(row=3, column=0, pady=10)
    ttk.Entry(frame, textvariable=observacion_var, width=80, font=("Arial", 12)).grid(
        row=3,
        column=1,
        columnspan=3,
        padx=5,
        pady=5
    )

    # =====================================================
    # ANTIGÜEDAD TOTAL
    # =====================================================

    lbl_total = ttk.Label(
        ventana,
        text="Antigüedad Total: 0 años",
        font=("Arial", 11, "bold"),
        foreground="blue"
    )

    lbl_total.grid(
        row=4,
        column=0,
        sticky="w",
        padx=10,
        pady=2
    )

    # =====================================================
    #      FILTROS PARA SELECCIÓN DE DATOS
    # =====================================================

    frame_filtro = ttk.LabelFrame(ventana, text="Búsqueda")
    frame_filtro.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    ttk.Label(frame_filtro, text="Profesor").grid(row=0, column=0)

    entry_buscar = ttk.Entry(frame_filtro, textvariable=buscar_var)
    entry_buscar.grid(row=0, column=1, padx=5)

    ttk.Label(frame_filtro, text="Situación").grid(row=0, column=2)

    combo_filtro = ttk.Combobox(frame_filtro, textvariable=filtro_situacion, values=["Todos", "Titular", "Provisorio", "Suplente"], state="readonly")

    combo_filtro.grid(row=0, column=3, padx=5)
    combo_filtro.current(0)

    ttk.Button(frame_filtro, text="Buscar", command=lambda: cargar_tree()).grid(row=0, column=4, padx=5)

    # =====================================================
   
    # ====================================================================
    # =====================================================
    #                  DISEÑO DEL TREEVIEW
    # =====================================================
    # El frame se ubica en la fila 2 de la ventana principal
    frame_tabla = ttk.Frame(ventana)
    frame_tabla.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    # Configuramos el peso para que la fila 0 (el Treeview) se estire
    frame_tabla.rowconfigure(0, weight=1)
    frame_tabla.columnconfigure(0, weight=1)
    
    columnas = ("id_historial", "id_profesor", "profesor", "materia", "curso", "situacion", "inicio", "fin", "antiguedad", "observaciones")

    # El padre es frame_tabla
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

    # CORRECCIÓN: Se ubica en la row=0 (la que tiene el weight) y quitamos padx/pady internos
    tree.grid(row=0, column=0, sticky="nsew")

    for col in columnas:
        tree.heading(col, text=col.capitalize())

    # Ocultar IDs
    tree.column("id_historial", width=0, stretch=False)
    tree.column("id_profesor", width=0, stretch=False)

    # Tamaños y alineaciones
    tree.column("profesor", width=220, anchor="w")
    tree.column("materia", width=180, anchor="w")
    tree.column("curso", width=60, anchor="center")
    tree.column("situacion", width=100, anchor="center")
    tree.column("inicio", width=80, anchor="center")
    tree.column("fin", width=80, anchor="center")
    tree.column("antiguedad", width=80, anchor="center")
    tree.column("observaciones", width=150, anchor="w")

    # ============================= SCROLLBARS ============================
    # El padre de los scrollbars también es 'frame_tabla'
    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
    
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # Ubicación perfecta de los componentes DENTRO de frame_tabla
    scrollbar_y.grid(row=0, column=1, sticky="ns")  # Al lado del Treeview
    scrollbar_x.grid(row=1, column=0, sticky="ew")  # Debajo del Treeview
    # =====================================================
    #     CARGAR COMBOS CON PROFESORES, MATERIAS Y CURSOS
    # =====================================================

    def cargar_combos():

        conn = conectar()
        cursor = conn.cursor()

        # PROFESORES
        cursor.execute("""
            SELECT id_profesor, apenom
            FROM profesores
        """)

        for id_, nombre in cursor.fetchall():

            texto = f"{id_} - {nombre}"

            profesores_dict[texto] = id_

        combo_profesor["values"] = list(
            profesores_dict.keys()
        )

        # MATERIAS
        cursor.execute("""
            SELECT id_materia, nombre
            FROM materias
        """)

        for id_, nombre in cursor.fetchall():

            texto = f"{id_} - {nombre}"

            materias_dict[texto] = id_

        combo_materia["values"] = list(
            materias_dict.keys()
        )

        # CURSOS
        cursor.execute("""
            SELECT id_curso, nombre
            FROM cursos
        """)

        for id_, nombre in cursor.fetchall():

            texto = f"{id_} - {nombre}"

            cursos_dict[texto] = id_

        combo_curso["values"] = list(
            cursos_dict.keys()
        )

        conn.close()

    # =====================================================
    #            ANTIGUEDAD INDIVIDUAL
    # =====================================================

    def calcular_antiguedad(inicio, fin):

        try:

            fecha_inicio = datetime.strptime(
                inicio,
                "%d/%m/%Y"
            )

            if fin:
                fecha_fin = datetime.strptime(
                    fin,
                    "%d/%m/%Y"
                )
            else:
                fecha_fin = datetime.now()

            dias = (fecha_fin - fecha_inicio).days

            anios = round(dias / 365, 1)

            return f"{anios} años"

        except:
            return ""

    # =====================================================
    #             CARGAR TREEVIEW
    # =====================================================

    def cargar_tree():

        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        query = """
            SELECT
                h.id_historial,
                h.id_profesor,
                p.apenom,
                m.nombre,
                c.nombre,
                h.situacion,
                h.fecha_inicio,
                h.fecha_fin,
                h.observaciones
                

            FROM historial_docente h

            JOIN profesores p
                ON h.id_profesor = p.id_profesor

            JOIN materias m
                ON h.id_materia = m.id_materia

            JOIN cursos c
                ON h.id_curso = c.id_curso

            WHERE 1=1
        """

        parametros = []

        # filtro profesor
        if buscar_var.get():

            query += " AND p.apenom LIKE ?"

            parametros.append(
                f"%{buscar_var.get()}%"
            )

        # filtro situación
        if filtro_situacion.get() != "Todos":

            query += " AND h.situacion=?"

            parametros.append(
                filtro_situacion.get()
            )

        query += " ORDER BY p.apenom"

        cursor.execute(query, parametros)

        registros = cursor.fetchall()

        for fila in registros:

            antiguedad = calcular_antiguedad(
                fila[6],
                fila[7]
            )

            nueva = list(fila)

            tree.insert(
                "",
                "end",
                values=(
                    fila[0],  # id_historial
                    fila[1],  # id_profesor
                    fila[2],  # profesor
                    fila[3],  # materia
                    fila[4],  # curso
                    fila[5],  # situacion
                    fila[6],  # inicio
                    fila[7],  # fin
                    antiguedad,
                    fila[8]   # observaciones
                )
            )

        conn.close()

    # =====================================================
    #             ANTIGÜEDAD TOTAL DEL DOCENTE
    # =====================================================

    def antiguedad_total(id_profesor):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fecha_inicio, fecha_fin
            FROM historial_docente
            WHERE id_profesor=?
            ORDER BY fecha_inicio
        """, (id_profesor,))

        registros = cursor.fetchall()

        conn.close()

        periodos = []

        # ==========================================
        # CONVERTIR FECHAS
        # ==========================================

        for inicio, fin in registros:

            try:

                fecha_inicio = datetime.strptime(
                    inicio,
                    "%d/%m/%Y"
                )

                if fin == "" or fin is None:

                    fecha_fin = datetime.today()

                else:

                    fecha_fin = datetime.strptime(
                        fin,
                        "%d/%m/%Y"
                    )

                periodos.append(
                    (fecha_inicio, fecha_fin)
                )

            except Exception as e:
                print(e)

        # ==========================================
        # NO HAY DATOS
        # ==========================================

        if not periodos:
            return "0 años"

        # ==========================================
        # ORDENAR PERIODOS
        # ==========================================

        periodos.sort(key=lambda x: x[0])

        # ==========================================
        # UNIR PERIODOS SUPERPUESTOS
        # ==========================================

        unidos = []

        actual_inicio, actual_fin = periodos[0]

        for inicio, fin in periodos[1:]:

            # si se superponen
            if inicio <= actual_fin:

                if fin > actual_fin:
                    actual_fin = fin

            else:

                unidos.append(
                    (actual_inicio, actual_fin)
                )

                actual_inicio = inicio
                actual_fin = fin

        unidos.append(
            (actual_inicio, actual_fin)
        )

        # ==========================================
        # SUMAR DÍAS REALES
        # ==========================================

        total_dias = 0

        for inicio, fin in unidos:

            total_dias += (
                fin - inicio
            ).days

        anios = total_dias // 365

        meses = (
            (total_dias % 365) // 30
        )

        return f"{anios} años - {meses} meses"


    # =====================================================
    #          GUARDAR HISTORIAL DOCENTE
    # =====================================================

    def guardar():

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO historial_docente (
                id_profesor,
                id_materia,
                id_curso,
                situacion,
                fecha_inicio,
                fecha_fin,
                observaciones
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (

            profesores_dict[
                profesor_var.get()
            ],

            materias_dict[
                materia_var.get()
            ],

            cursos_dict[
                curso_var.get()
            ],

            situacion_var.get(),

            inicio_var.get(),

            fin_var.get(),

            observacion_var.get()
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "OK",
            "Historial guardado",
            parent=ventana
        )

        cargar_tree()
        limpiar()

    # =====================================================
    #          SELECCIONAR REGISTRO
    # =====================================================

    def seleccionar(event):

        nonlocal id_seleccionado

        item = tree.selection()

        if not item:
            return

        valores = tree.item(
            item[0],
            "values"
        )

        id_seleccionado = valores[0]

        id_profesor = valores[1]

        # ==================================
        # ANTIGÜEDAD TOTAL
        # ==================================

        total = antiguedad_total(
            id_profesor
        )

        lbl_total.config(
            text=f"Antigüedad Total: {total}"
        )

        # ==================================
        # CARGAR COMBOS
        # ==================================

        for texto in profesores_dict:

            if valores[2] in texto:

                profesor_var.set(texto)

        for texto in materias_dict:

            if valores[3] in texto:

                materia_var.set(texto)

        for texto in cursos_dict:

            if valores[4] in texto:

                curso_var.set(texto)

        situacion_var.set(valores[5])

        inicio_var.set(valores[6])

        fin_var.set(valores[7])

        observacion_var.set(valores[9])

    tree.bind("<<TreeviewSelect>>", seleccionar)

    # =====================================================
    #            MODIFICAR HISTORIAL
    # =====================================================

    def modificar():

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro", parent= ventana
            )

            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE historial_docente
            SET
                id_profesor=?,
                id_materia=?,
                id_curso=?,
                situacion=?,
                fecha_inicio=?,
                fecha_fin=?,
                observaciones=?

            WHERE id_historial=?
        """, (

            profesores_dict[
                profesor_var.get()
            ],

            materias_dict[
                materia_var.get()
            ],

            cursos_dict[
                curso_var.get()
            ],

            situacion_var.get(),

            inicio_var.get(),

            fin_var.get(),

            observacion_var.get(),

            id_seleccionado
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "OK",
            "Registro modificado", parent=ventana
        )

        cargar_tree()
        limpiar()

    # =====================================================
    #               ELIMINAR HISTORIAL
    # =====================================================

    def eliminar():

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro", parent=ventana
            )

            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar historial?", parent=ventana
        ):
            return

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM historial_docente
                WHERE id_historial=?
            """, (id_seleccionado,))
        except Exception as e:
          print(e)
          messagebox.showerror("ERROR", f"NO se pudo eliminar el registro.\nEstá vinculado con otros datos", parent=ventana)
        
        conn.commit()
        conn.close()

        messagebox.showinfo(
            "OK",
            "Registro eliminado", parent=ventana
        )

        cargar_tree()
        limpiar()

    # =====================================================
    #             GENERAR LEGAJO PDF
    # =====================================================

    def generar_legajo_pdf():

        item = tree.selection()

        if not item:

            messagebox.showwarning(
                "Atención",
                "Seleccione un docente", parent=ventana
            )

            return

        valores = tree.item(
            item[0],
            "values"
        )

        id_profesor = valores[1]
        nombre_profesor = valores[2]


        nombre_pdf = f"Legajo_{nombre_profesor}.pdf"

        ruta_pdf = os.path.join(
            "reportes",
            "pdf",
            nombre_pdf
        )

        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4
        )

        elementos = []

        styles = getSampleStyleSheet()

        # ==========================================
        # LOGO
        # ==========================================

        try:

            logo = Image(
                "logos.png",
                width=120,
                height=120
            )

            elementos.append(logo)

        except:
            pass

        # ==========================================
        # TITULO
        # ==========================================

        titulo = Paragraph(
            "<b>LEGAJO DOCENTE</b>",
            styles["Title"]
        )

        elementos.append(titulo)

        elementos.append(
            Spacer(1, 20)
        )

        # ==========================================
        # DATOS DOCENTE
        # ==========================================

        datos = Paragraph(
            f"""
            <b>Profesor:</b> {nombre_profesor}<br/>
            <b>Antigüedad Total:</b>
            {antiguedad_total(id_profesor)}
            """,
            styles["BodyText"]
        )

        elementos.append(datos)

        elementos.append(
            Spacer(1, 20)
        )

        # ==========================================
        # OBTENER HISTORIAL
        # ==========================================

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                m.nombre,
                c.nombre,
                h.situacion,
                h.fecha_inicio,
                h.fecha_fin,
                h.observaciones

            FROM historial_docente h

            JOIN materias m
                ON h.id_materia = m.id_materia

            JOIN cursos c
                ON h.id_curso = c.id_curso

            WHERE h.id_profesor=?
        """, (id_profesor,))

        registros = cursor.fetchall()

        conn.close()

        # ==========================================
        # TABLA
        # ==========================================

        data = [[
            "Materia",
            "Curso",
            "Situación",
            "Inicio",
            "Fin",
            "Observaciones"
        ]]

        for fila in registros:

            data.append(list(fila))

        tabla = Table(data)

        tabla.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (-1,0),
                colors.darkblue),

            ('TEXTCOLOR', (0,0), (-1,0),
                colors.white),

            ('FONTNAME', (0,0), (-1,0),
                'Helvetica-Bold'),

            ('GRID', (0,0), (-1,-1),
                1, colors.black),

            ('BACKGROUND', (0,1), (-1,-1),
                colors.beige),

            ('FONTSIZE', (0,0), (-1,-1),
                9)

        ]))

        elementos.append(tabla)

        elementos.append(
            Spacer(1, 40)
        )

        # ==========================================
        # FIRMA
        # ==========================================

        firma = Paragraph(
            """
            <br/><br/><br/>
            ___________________________<br/>
            Firma Dirección
            """,
            styles["BodyText"]
        )

        elementos.append(firma)

        # ==========================================
        # CREAR PDF
        # ==========================================

        doc.build(elementos)

        messagebox.showinfo(
            "PDF",
            "Legajo generado correctamente", parent=ventana
        )
    # =========================================================================


    # =====================================================
    #         CERTIFICACIÓN DE SERVICIOS
    # =====================================================
    def certificacion_servicios():

        item = tree.selection()

        if not item:

            messagebox.showwarning(
                "Atención",
                "Seleccione un docente", parent=ventana
            )

            return

        valores = tree.item(
            item[0],
            "values"
        )

        id_profesor = int(valores[0])
        nombre_profesor = valores[2]

     
        # ==========================================
        # BUSCAR ID DEL PROFESOR
        # ==========================================

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_profesor
            FROM profesores
            WHERE apenom=?
        """, (nombre_profesor,))

        resultado = cursor.fetchone()

        if not resultado:

            messagebox.showerror(
                "Error",
                "No se encontró el profesor", parent=ventana
            )

            conn.close()
            return

        id_profesor = resultado[0]

        # ==========================================
        # CREAR CARPETA PDF
        # ==========================================

        os.makedirs(
            "reportes/pdf",
            exist_ok=True
        )

        archivo = os.path.join(
            "reportes",
            "pdf",
            f"Certificacion_{nombre_profesor}.pdf"
        )

        doc = SimpleDocTemplate(
            archivo,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        elementos = []

        # ==========================================
        # LOGO
        # ==========================================

        try:

            logo = Image(
                "logos.png",
                width=80,
                height=80
            )

            elementos.append(logo)

        except Exception as e:
            print(e)

        # ==========================================
        # TITULO
        # ==========================================

        titulo = Paragraph(
            "<b>CERTIFICACIÓN DE SERVICIOS</b>",
            styles["Title"]
        )

        elementos.append(titulo)

        elementos.append(
            Spacer(1, 20)
        )

        # ==========================================
        # TEXTO CERTIFICACIÓN
        # ==========================================

        texto = Paragraph(
            f"""
            Se certifica que el/la docente
            <b>{nombre_profesor}</b>
            presta y/o prestó servicios
            en esta institución educativa.
            <br/><br/>

            Antigüedad Total:
            <b>{antiguedad_total(id_profesor)}</b>
            """,
            styles["BodyText"]
        )

        elementos.append(texto)

        elementos.append(
            Spacer(1, 20)
        )

        # ==========================================
        # OBTENER HISTORIAL
        # ==========================================

        cursor.execute("""
            SELECT
                m.nombre,
                c.nombre,
                h.situacion,
                h.fecha_inicio,
                h.fecha_fin

            FROM historial_docente h

            JOIN materias m
                ON h.id_materia = m.id_materia

            JOIN cursos c
                ON h.id_curso = c.id_curso

            WHERE h.id_profesor=?
        """, (id_profesor,))

        registros = cursor.fetchall()

        conn.close()

        # ==========================================
        # TABLA
        # ==========================================

        data = [[
            "Materia",
            "Curso",
            "Situación",
            "Inicio",
            "Fin"
        ]]

        for fila in registros:

            data.append(list(fila))

        tabla = Table(data)

        tabla.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (-1,0),
                colors.darkblue),

            ('TEXTCOLOR', (0,0), (-1,0),
                colors.white),

            ('GRID', (0,0), (-1,-1),
                1, colors.black),

            ('FONTNAME', (0,0), (-1,0),
                'Helvetica-Bold')

        ]))

        elementos.append(tabla)

        elementos.append(
            Spacer(1, 50)
        )

        # ==========================================
        # FIRMA
        # ==========================================

        firma = Paragraph(
            """
            ___________________________<br/>
            Firma Dirección
            """,
            styles["BodyText"]
        )

        elementos.append(firma)

        # ==========================================
        # CREAR PDF
        # ==========================================

        doc.build(elementos)

        messagebox.showinfo(
            "PDF",
            f"Certificación generada:\n{archivo}", parent=ventana
        )
    #========================================================



    # =====================================================
    #                 LIMPIAR CAMPOS
    # =====================================================

    def limpiar():

        nonlocal id_seleccionado

        id_seleccionado = None

        profesor_var.set("")
        materia_var.set("")
        curso_var.set("")
        situacion_var.set("")
        inicio_var.set("")
        fin_var.set("")
        observacion_var.set("")

        lbl_total.config(
            text="Antigüedad Total: 0 años"
        )

    # =====================================================
    # BOTONES
    # =====================================================

    frame_btn = ttk.Frame(ventana)
    frame_btn.grid(row=3, column=0, pady=10)

    ttk.Button(
        frame_btn,
        text="💾 Guardar", 
        command=guardar
    ).grid(row=0, column=1, padx=5)

    ttk.Button(
        frame_btn,
        text="✏ Modificar",
        command=modificar
    ).grid(row=0, column=2, padx=5)

    ttk.Button(
        frame_btn,
        text="🗑 Eliminar",
        command=eliminar
    ).grid(row=0, column=3, padx=5)

    ttk.Button(
        frame_btn,
        text="🧹 Limpiar",
        command=limpiar
    ).grid(row=0, column=4, padx=5)

    ttk.Button(
        frame_btn,
        text="📄 Legajo PDF",
        command=generar_legajo_pdf
    ).grid(row=0, column=5, padx=5)

    ttk.Button(
        frame_btn,
        text="📑 Certificación",
        command=certificacion_servicios
    ).grid(row=0, column=6, padx=5)

    ttk.Button(
        frame_btn,
        text="❌ Cerrar",
        command=ventana.destroy
    ).grid(row=0, column=7, padx=5)
    # =====================================================

    # =====================================================
    #           LLAMADOS A MÓDULOS A EJECUTAR
    # =====================================================
    cargar_combos()
    cargar_tree()
    centrar_ventana(ventana)