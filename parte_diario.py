# ========================================================================================
#                  MÓDULO LISTADOS DE PARTE DIARIOS
# ========================================================================================

# ----------------------------------- LIBRERÍAS ------------------------------------------
from tkinter import ttk, Frame, Label, messagebox
from datetime import datetime
import tkinter as tk
from datetime import datetime
from openpyxl import Workbook
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from database import conectar
from centraVent import centrar_ventana
# -----------------------------------------------------------------------------------------

# =================  Función Encabezado de pantalla =============================
def encabezado(fecha="", dia=""):       
        texto = f"""
    ========================================
            ESCUELA SECUNDARIA
    ========================================
        Parte diario de personal Docente
    Fecha: {fecha}
    Día: {dia}
    ========================================
    """
        return texto
#    -----------------------------------------------------------------------------

# ======================= FUNCIÓN PRINCIPAL DEL LISTADO DIARIO ==================
def abrir_parte_diario():

    conn = conectar()

    ventana = tk.Toplevel()
    ventana.title("PARTE DIARIO")
    ventana.geometry("1100x700")

    # =========================
    # VARIABLES
    # =========================
    turno_var = tk.StringVar()
    fecha_var = tk.StringVar()
    dia_var = tk.StringVar()
   
    # =========================
    # SELECTORES
    # =========================

    tk.Label(ventana, text="Turno", font=("Arial", 12)).pack()
    tk.Entry(ventana, textvariable=turno_var, font=("Arial", 12)).pack()
    tk.Label(ventana, text="Fecha", font=("Arial", 12)).pack()
    tk.Entry(ventana, textvariable=fecha_var, font=("Arial", 12)).pack()
    tk.Label(ventana, text="Día", font=("Arial", 12)).pack()
    tk.Entry(ventana, textvariable=dia_var, font=("Arial", 12)).pack()
    lbl_encabezado = tk.Label(ventana, text=encabezado(), justify="left", font=("Arial", 12))
    lbl_encabezado.pack()

    # =================  ACTUALIZAR LO QUE ESCRIBO EN LOS ENTRYS ==============
    def actualizar_encabezado(*args):
        lbl_encabezado.config(
            text=encabezado(
                fecha_var.get(),
                dia_var.get()
            )
        )

    fecha_var.trace_add("write", actualizar_encabezado)
    dia_var.trace_add("write", actualizar_encabezado)
    # --------------------------------------------------------------------------
   
    # ==========================================================================
    #                       TREEVIEW
    # ==========================================================================
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12)) 
    
    tree = ttk.Treeview(ventana, columns=("nombre", "detalle", "entrada", "salida", "firma"), show="headings")

    tree.heading("nombre", text="Nombre")
    tree.heading("detalle", text="Cargo/Materia")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")
    tree.heading("firma", text="Firma")

    tree.pack(fill="both", expand=True)

    tree.column("nombre", width=200)
    tree.column("detalle", width=200)
    tree.column("entrada", width=100)
    tree.column("salida", width=100)
    tree.column("firma", width=150)

    
    # -------------------------------------------------------------------------

    # ====================  CARGA LOS TURNOS Y DOCENTES Y DIAS  ===============
    def cargar_parte_diario(tree, turno_var, dia_var, conn):

        cursor = conn.cursor()

        for item in tree.get_children():
            tree.delete(item)

        # CARGOS
        cursor.execute("""
        SELECT
            p.apenom,
            c.nombre_cargo,
            pc.hentrada,
            pc.hsalida
        FROM personal_cargos pc
        JOIN profesores p ON pc.id_profesor = p.id_profesor
        JOIN cargos c ON pc.id_cargo = c.id_cargo
        WHERE pc.turno = ?
        ORDER BY
            CASE c.nombre_cargo
                WHEN 'Director' THEN 1
                WHEN 'Vice Director' THEN 2
                WHEN 'Secretario' THEN 3
                WHEN 'Prosecretario' THEN 4
                WHEN 'Encargado de Laboratorio' THEN 5
                ELSE 99
            END,
            c.nombre_cargo;
        """, (turno_var.get(),))

        for fila in cursor.fetchall():
            tree.insert("", "end", values=fila)

        cursor.execute("""
                SELECT
                    p.apenom,
                    m.nombre,
                    h.hentrada,
                    h.hsalida
                FROM asignaciones_docentes ad
                JOIN profesores p ON ad.id_profesor = p.id_profesor
                JOIN horarios h ON ad.id_horario = h.id_horario
                JOIN materias m ON h.id_materia = m.id_materia
                WHERE h.dia = ?
            """, (dia_var.get(),))

        # for fila in cursor.fetchall():
        #     tree.insert("", "end", values=fila)
        docentes = cursor.fetchall()

        for fila in docentes:

            hora = fila[2]  # hentrada

            turno_docente = ""

            if hora < "12:00":
                turno_docente = "Mañana"
            elif hora < "18:00":
                turno_docente = "Tarde"
            else:
                turno_docente = "Noche"

            if turno_docente == turno_var.get():

                tree.insert(
                    "",
                    "end",
                    values=(
                        fila[0],
                        fila[1],
                        fila[2],
                        fila[3],
                        ""
                    )
                )
    # ---------------------------------------------------------------------------

    # ====================== EXPORTA PLANILLA A REPORTES/EXCEL  ===================
    def exportar_excel(tree):

        carpeta = "reportes/excel"
        os.makedirs(carpeta, exist_ok=True)

        wb = Workbook()
        ws = wb.active
        ws.title = "Parte Diario"

        # ENCABEZADOS
        ws.append(["Nombre", "Cargo/Materia", "Entrada", "Salida", "Firma"])

        # DATOS DEL TREEVIEW
        for item in tree.get_children():
            ws.append(tree.item(item)["values"])

        nombre_archivo = f"parte_diario_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        ruta = os.path.join(carpeta, nombre_archivo)

        wb.save(ruta)

        messagebox.showinfo( "EXCEL",f"Exportado a Reportes/excel", parent=ventana)
    # -----------------------------------------------------------------------------------

    # ====================== EXPORTA PLANILLA A REPORTES/PDF  ===================
    def exportar_pdf_pro(tree, encabezado_texto):

        carpeta = "reportes/pdf"
        os.makedirs(carpeta, exist_ok=True)

        nombre = f"parte_diario_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        ruta = os.path.join(carpeta, nombre)

        doc = SimpleDocTemplate(ruta)

        elementos = []
        styles = getSampleStyleSheet()

        # ======================
        # ENCABEZADO
        # ======================
        elementos.append(Paragraph(encabezado_texto.replace("\n", "<br/>"), styles["Title"]))
        elementos.append(Spacer(1, 12))

        # ======================
        # DATOS TABLA
        # ======================
        data = [["Nombre", "Cargo/Materia", "Entrada", "Salida", "Firma"]]

        for item in tree.get_children():
            data.append(list(tree.item(item)["values"]))

        table = Table(data, colWidths=[120, 150, 50, 50, 180])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ]))

        elementos.append(table)

        doc.build(elementos)
        messagebox.showinfo( "PDF",f"Exportado a Reportes/pdf", parent=ventana)
    # =========================================================================
    #                       BOTÓN CARGAR
    # =========================================================================
   
   # tk.Button(ventana, text="Cargar", command=lambda: cargar_parte_diario(tree, turno_var, dia_var, conn)).pack()
    #tk.Button(ventana, text="Exportar Excel", command=lambda: exportar_excel(tree)).pack()
    #tk.Button(ventana, text="Exportar PDF", command=lambda: exportar_pdf_pro(tree, encabezado(fecha_var.get(),dia_var.get()))).pack()

    # Frame para los botones
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    tk.Button(frame_botones, text="💾 Cargar", font=("Arial", 12),
        command=lambda: cargar_parte_diario(tree, turno_var, dia_var, conn)).pack(side="left", padx=5)

    tk.Button(frame_botones, text=" 📊 Exportar Excel", font=("Arial", 12), command=lambda: exportar_excel(tree)
    ).pack(side="left", padx=5)

    tk.Button(frame_botones, text=" 📄Exportar PDF", font=("Arial", 12),
        command=lambda: exportar_pdf_pro(tree, encabezado(fecha_var.get(), dia_var.get())        )
    ).pack(side="left", padx=5)

    tk.Button(frame_botones, text="❌ Cerrar", font=("Arial", 12),
        command=ventana.destroy).pack(side="left", padx=5)

    # =================================== INICIO ===========================================
    centrar_ventana(ventana)