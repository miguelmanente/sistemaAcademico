# =========================================================================================
#                       MÓDULO LISTADO DOCENTES - LISTADOS.PY
# =========================================================================================

# -------------------  LIBRERÍAS -----------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from estilos import configurar_estilos



def ventana_listado(tipo):

    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title(f"Listado {tipo}")
    ventana.geometry("1000x600")

    ventana.rowconfigure(1, weight=1)
    ventana.columnconfigure(0, weight=1)

    # =========================
    # VARIABLES
    # =========================
    buscar_var = tk.StringVar()
    curso_var = tk.StringVar()

    # =========================
    # FILTROS
    # =========================
    frame_filtros = ttk.Frame(ventana)
    frame_filtros.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

    ttk.Label(frame_filtros, text="Buscar Profesor:", font=("Arial", 12)).grid(row=0, column=0)
    entry_buscar = ttk.Entry(frame_filtros, textvariable=buscar_var)
    entry_buscar.grid(row=0, column=1, padx=5)

    ttk.Label(frame_filtros, text="Curso:", font=("Arial", 12)).grid(row=0, column=2)
    combo_curso = ttk.Combobox(frame_filtros, textvariable=curso_var, state="readonly", font=("Arial", 12))
    combo_curso.grid(row=0, column=3, padx=5)

    ttk.Button(frame_filtros, text="Filtrar", command=lambda: cargar()).grid(row=0, column=4, padx=5)

    # =========================
    # FRAME TREEVIEW
    # =========================

    frame_tree = ttk.Frame(ventana)
    frame_tree.grid(row=1, column=0, sticky="nsew")

    ventana.rowconfigure(1, weight=1)
    ventana.columnconfigure(0, weight=1)

    frame_tree.rowconfigure(0, weight=1)
    frame_tree.columnconfigure(0, weight=1)

    # =========================
    # TREEVIEW
    # =========================
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))

    columnas = ("profesor", "curso", "materia", "dia", "entrada", "salida" )
    tree = ttk.Treeview(frame_tree, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")
    

    tree.heading("profesor", text="Profesor")
    tree.heading("curso", text="Curso")
    tree.heading("materia", text="Materia")
    tree.heading("dia", text="Día")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")
  
    tree.column("profesor", width=230)
    tree.column("curso", width=50)
    tree.column("materia", width=230)
    tree.column("dia", width=50)
    tree.column("entrada", width=50)
    tree.column("salida", width=50)


    # =========================
    # SCROLL VERTICAL
    # =========================

    scroll_y = ttk.Scrollbar(
        frame_tree,
        orient="vertical",
        command=tree.yview
    )

    scroll_y.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    # =========================
    # SCROLL HORIZONTAL
    # =========================

    scroll_x = ttk.Scrollbar(
        frame_tree,
        orient="horizontal",
        command=tree.xview
    )

    scroll_x.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    # =========================
    # CONFIGURAR TREEVIEW
    # =========================

    tree.configure(

        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set

    )    

    # =========================
    # CARGAR CURSOS
    # =========================
    def cargar_cursos():
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT nombre FROM cursos")
        cursos = ["Todos"] + [c[0] for c in cursor.fetchall()]

        combo_curso["values"] = cursos
        combo_curso.current(0)

        conn.close()

    # =========================
    # CARGAR DATOS
    # =========================
    def cargar():
        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        query = """
            SELECT p.apenom, c.nombre, m.nombre,
                   h.dia, h.hentrada, h.hsalida
            FROM asignaciones_docentes a
            JOIN profesores p ON a.id_profesor = p.id_profesor
            JOIN horarios h ON a.id_horario = h.id_horario
            JOIN cursos c ON h.id_curso = c.id_curso
            JOIN materias m ON h.id_materia = m.id_materia
            WHERE a.srprofesor = ?
        """

        params = [tipo]

        # filtro por búsqueda
        if buscar_var.get():
            query += " AND p.apenom LIKE ?"
            params.append(f"%{buscar_var.get()}%")

        # filtro por curso
        if curso_var.get() and curso_var.get() != "Todos":
            query += " AND c.nombre = ?"
            params.append(curso_var.get())

        query += " ORDER BY p.apenom"

        cursor.execute(query, params)

        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

        conn.close()

    # =========================
    # EXPORTAR EXCEL
    # =========================
    def exportar_excel():
        wb = Workbook()
        ws = wb.active

        ws.append(["Profesor", "Curso", "Materia", "Día", "Entrada", "Salida"])

        for item in tree.get_children():
            ws.append(tree.item(item)["values"])

        fecha = datetime.now().strftime("%d-%m-%Y_%H-%M")
        #wb.save("listado.xlsx")
        nombre_excel = f"listado_{fecha}.xlsx"
        ruta_excel = os.path.join(
            "reportes",
            "excel",
            nombre_excel)

        wb.save(ruta_excel)
        messagebox.showinfo("OK", "Exportado a listado.xlsx", parent=ventana)

    # =========================
    # EXPORTAR PDF
    # =========================
  
    def exportar_pdf(tipo):
        
        fecha = datetime.now().strftime("%d-%m-%Y_%H-%M")
        nombre_pdf = f"listado_{fecha}.pdf"
        ruta_pdf = os.path.join(
            "reportes",
            "pdf",
            nombre_pdf
        )
      
        doc = SimpleDocTemplate(ruta_pdf)

        styles = getSampleStyleSheet()

        titulo = Paragraph(f"<b>Listado de Profesores {tipo}</b>", styles["Title"])

        # Espacio
        espacio = Spacer(1, 20)

        data = [["Profesor", "Curso", "Materia", "Día", "Entrada", "Salida"]]

        for item in tree.get_children():
             data.append(tree.item(item)["values"])

        # Tabla
        tabla = Table(data)

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))

        elementos = []
        elementos.append(titulo)
        elementos.append(espacio)
        elementos.append(tabla)

        doc.build(elementos)
        

    # =========================
    # IMPRIMIR DIRECTO
    # =========================
    def imprimir():
        exportar_pdf(tipo)
        try:
            os.startfile("listado_{fecha}.pdf", "print")
        except:
            messagebox.showwarning("Atención", "Impresión directa solo funciona en Windows", parent=ventana)

    # =========================
    # BOTONES
    # =========================
    frame_botones = ttk.Frame(ventana)
    frame_botones.grid(row=2, column=0, pady=10)

    ttk.Button(frame_botones, text="🖨 Imprimir", command=imprimir).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="📊 Excel", command=exportar_excel).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="📄 PDF", command=lambda: exportar_pdf(tipo)).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="❌ Cerrar", command=ventana.destroy).grid(row=0, column=3, padx=5)

    cargar_cursos()
    cargar()
    centrar_ventana(ventana)