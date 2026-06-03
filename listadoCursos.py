import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from openpyxl import Workbook
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime


def ventana_listado_curso():

    ventana = tk.Toplevel()
    ventana.title("Listado por Curso")
    ventana.geometry("1000x600")

    ventana.rowconfigure(1, weight=1)
    ventana.columnconfigure(0, weight=1)

    # =========================
    # VARIABLES
    # =========================
    curso_var = tk.StringVar()
    buscar_var = tk.StringVar()

    # =========================
    # FRAME FILTROS
    # =========================
    frame_filtros = ttk.Frame(ventana)
    frame_filtros.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

    ttk.Label(frame_filtros, text="Curso:").grid(row=0, column=0, padx=5)

    combo_curso = ttk.Combobox(
        frame_filtros,
        textvariable=curso_var,
        state="readonly",
        width=30
    )

    combo_curso.grid(row=0, column=1, padx=5)

    ttk.Label(frame_filtros, text="Buscar Profesor:").grid(row=0, column=2, padx=5)

    entry_buscar = ttk.Entry(frame_filtros, textvariable=buscar_var)
    entry_buscar.grid(row=0, column=3, padx=5)

    # =========================
    # TREEVIEW
    # =========================
    columnas = (
        "profesor",
        "materia",
        "dia",
        "situacion"
    )

    tree = ttk.Treeview(
        ventana,
        columns=columnas,
        show="headings"
    )

    tree.grid(row=1, column=0, sticky="nsew", padx=10)

    tree.heading("profesor", text="Profesor")
    tree.heading("materia", text="Materia")
    tree.heading("dia", text="Día")
    tree.heading("situacion", text="Situación")

    tree.column("profesor", width=300)
    tree.column("materia", width=250, anchor="center")
    tree.column("dia", width=150, anchor="center")
    tree.column("situacion", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(
        ventana,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=1, sticky="ns")

    # =========================
    # CARGAR CURSOS
    # =========================
    def cargar_cursos():

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nombre
            FROM cursos
            ORDER BY nombre
        """)

        cursos = [fila[0] for fila in cursor.fetchall()]

        combo_curso["values"] = cursos

        if cursos:
            combo_curso.current(0)

        conn.close()

    # =========================
    # CARGAR TREE
    # =========================
    def cargar():

        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        query = """
            SELECT
                p.apenom,
                m.nombre,
                h.dia,
                a.srprofesor
            FROM asignaciones_docentes a
            JOIN profesores p
                ON a.id_profesor = p.id_profesor
            JOIN horarios h
                ON a.id_horario = h.id_horario
            JOIN materias m
                ON h.id_materia = m.id_materia
            JOIN cursos c
                ON h.id_curso = c.id_curso
            WHERE c.nombre = ?
        """

        parametros = [curso_var.get()]

        # filtro búsqueda
        if buscar_var.get():

            query += " AND p.apenom LIKE ?"

            parametros.append(
                f"%{buscar_var.get()}%"
            )

        query += " ORDER BY p.apenom"

        cursor.execute(query, parametros)

        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

        conn.close()

    # =========================
    # EXPORTAR EXCEL
    # =========================
    def exportar_excel():

        wb = Workbook()
        ws = wb.active

        ws.title = "Listado Curso"

        ws.append([
            "Profesor",
            "Materia",
            "Día",
            "Situación"
        ])

        for item in tree.get_children():
            ws.append(tree.item(item)["values"])
        fecha = datetime.now().strftime("%d-%m-%Y_%H-%M")
        nombre_excel = f"listado_{curso_var.get()}_{fecha}.xlsx"
        ruta_excel = os.path.join(
            "reportes",
            "excel",
            nombre_excel
        )

        wb.save(ruta_excel)
        #wb.save(archivo)

        messagebox.showinfo(
            "Excel",
            f"Exportado a /reportes/excel"
        )

    # =========================
    # EXPORTAR PDF
    # =========================
    def exportar_pdf():
   
        os.makedirs("reportes/pdf", exist_ok=True)

        archivo = f"listado_{curso_var.get()}"
        fecha = datetime.now().strftime("%d-%m-%Y_%H-%M")

        nombre_pdf = f"{archivo}_{fecha}.pdf"

        ruta_pdf = os.path.join(
            "reportes",
            "pdf",
            nombre_pdf
        )

        doc = SimpleDocTemplate(ruta_pdf)

        styles = getSampleStyleSheet()

        titulo = Paragraph(
            f"<b>LISTADO DEL CURSO {curso_var.get()}</b>",
            styles["Title"]
        )

        espacio = Spacer(1, 20)

        data = [[
            "Profesor",
            "Materia",
            "Día",
            "Situación"
        ]]

        for item in tree.get_children():
            data.append(tree.item(item)["values"])

        tabla = Table(data)

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))

        elementos = [
            titulo,
            espacio,
            tabla
        ]

        doc.build(elementos)

        messagebox.showinfo(
            "PDF",
            f"PDF generado:\n{ruta_pdf}"
        )

    # =========================
    # IMPRIMIR
    # =========================
    def imprimir():

        exportar_pdf()

        try:
            os.startfile(
                f"listado_{curso_var.get()}.pdf",
                "print"
            )

        except:
            messagebox.showwarning(
                "Atención",
                "Impresión directa solo en Windows"
            )

    # =========================
    # BOTONES
    # =========================
    frame_botones = ttk.Frame(ventana)
    frame_botones.grid(row=2, column=0, pady=10)

    ttk.Button(
        frame_botones,
        text="🔍 Filtrar",
        command=cargar
    ).grid(row=0, column=0, padx=5)

    ttk.Button(
        frame_botones,
        text="📊 Excel",
        command=exportar_excel
    ).grid(row=0, column=1, padx=5)

    ttk.Button(
        frame_botones,
        text="📄 PDF",
        command=exportar_pdf
    ).grid(row=0, column=2, padx=5)

    ttk.Button(
        frame_botones,
        text="🖨 Imprimir",
        command=imprimir
    ).grid(row=0, column=3, padx=5)

    ttk.Button(
        frame_botones,
        text="❌ Cerrar",
        command=ventana.destroy
    ).grid(row=0, column=4, padx=5)

    cargar_cursos()
    cargar()

    centrar_ventana(ventana)