# ================================================
#             RANKING DE AUSENTISMOS             
#=================================================

#=============== LIBRERÍAS =======================
import tkinter as tk
from tkinter import ttk
from database import conectar
from centraVent import centrar_ventana
from datetime import datetime, timedelta

# ============== VENTANA PRINCIPAL ===============
def ventana_ranking():

    ventana = tk.Toplevel()
    ventana.title("Ranking de Ausentismo")
    ventana.geometry("700x500")
    ventana.rowconfigure(0, weight=1)
    ventana.columnconfigure(0, weight=1)

    columnas = ("puesto", "docente", "dias")

    tree = ttk.Treeview(ventana, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    tree.heading("puesto", text="Puesto")
    tree.heading("docente", text="Docente")
    tree.heading("dias", text="Días")

    tree.column("puesto", width=80, anchor="center")
    tree.column("docente", width=400)
    tree.column("dias", width=120, anchor="center")

    lbl = ttk.Label(ventana, text="Ranking institucional de ausentismo docente", font=("Arial", 12, "bold"))
    lbl.grid(row=1, column=0, pady=5)

    def calcular_dias(desde, hasta):

        fecha_desde = datetime.strptime(
            desde,
            "%d/%m/%Y"
        )

        fecha_hasta = datetime.strptime(
            hasta,
            "%d/%m/%Y"
        )

        return (
            fecha_hasta - fecha_desde
        ).days + 1
    
    def cargar_ranking():

        for item in tree.get_children():

            tree.delete(item)

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                p.apenom,
                a.fecha_desde,
                a.fecha_hasta

            FROM asistencias_docentes a

            JOIN profesores p
            ON a.id_profesor = p.id_profesor

        """)

        registros = cursor.fetchall()

        conn.close()

        # ranking = {}

        # for docente, desde, hasta in registros:

        #     dias = calcular_dias(
        #         desde,
        #         hasta
        #     )

        #     if docente not in ranking:

        #         ranking[docente] = 0

        #     ranking[docente] += dias
        ranking_fechas = {}

        for docente, desde, hasta in registros:

            if docente not in ranking_fechas:

                ranking_fechas[docente] = set()

            fecha_actual = datetime.strptime(
                desde,
                "%d/%m/%Y"
            )

            fecha_hasta = datetime.strptime(
                hasta,
                "%d/%m/%Y"
            )

            while fecha_actual <= fecha_hasta:

                ranking_fechas[docente].add(
                    fecha_actual.strftime("%d/%m/%Y")
                )

                fecha_actual += timedelta(days=1)

        ranking = {}

        for docente, fechas in ranking_fechas.items():

            ranking[docente] = len(fechas)

        ordenado = sorted(

            ranking.items(),

            key=lambda x: x[1],

            reverse=True
        )

        puesto = 1

        for docente, dias in ordenado:

            tree.insert(

                "",

                "end",

                values=(
                    puesto,
                    docente,
                    dias
                )
            )

            puesto += 1
    
    ttk.Button(ventana, text="❌ Cerrar", command=ventana.destroy).grid(row=2, column=0, pady=10)

    cargar_ranking()

    centrar_ventana(ventana)