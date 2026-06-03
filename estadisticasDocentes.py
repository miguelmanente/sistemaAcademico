# =========================================================================
#                    MÓDULO ESTADÍSTICAS DOCENTES
# =========================================================================

# ======================== LIBRERÍAS =====================================
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from database import conectar
from centraVent import centrar_ventana
from datetime import datetime, timedelta
from datetime import datetime
from estilos import configurar_estilos


# ==========================  VENTANA  ====================================
def ventana_estadisticas():

    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Estadísticas Docentes")

    ventana.geometry("700x600")

    # ==========================================================
    # FUNCIÓN CALCULAR DÍAS
    # ==========================================================
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

    # ==========================================================
    # VARIABLES
    # ==========================================================
    total_inasistencias = 0

    docentes = {}

    estados = {}

    # ==========================================================
    # CONSULTA GENERAL
    # ==========================================================
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

    """)

    registros = cursor.fetchall()

    conn.close()

    # ==========================================================
    # PROCESAR DATOS SIN DUPLICAR DÍAS
    # ==========================================================

    docentes_fechas = {}
    estados_fechas = {}

    for docente, desde, hasta, estado in registros:

            if docente not in docentes_fechas:
                docentes_fechas[docente] = set()

            if estado not in estados_fechas:
                estados_fechas[estado] = set()

            fecha_actual = datetime.strptime(
                desde,
                "%d/%m/%Y"
            )

            fecha_hasta = datetime.strptime(
                hasta,
                "%d/%m/%Y"
            )

            while fecha_actual <= fecha_hasta:

                fecha_txt = fecha_actual.strftime(
                    "%d/%m/%Y"
                )

                docentes_fechas[docente].add(
                    fecha_txt
                )

                estados_fechas[estado].add(
                    fecha_txt
                )

                fecha_actual += timedelta(days=1)

        # convertir sets en cantidades

    docentes = {}

    for docente, fechas in docentes_fechas.items():

            docentes[docente] = len(fechas)

    estados = {}

    for estado, fechas in estados_fechas.items():

            estados[estado] = len(fechas)

    total_inasistencias = sum(docentes.values())

    # ==========================================================
    # PROMEDIO
    # ==========================================================
    cantidad_docentes = len(docentes)

    if cantidad_docentes > 0:

        promedio = round(
            total_inasistencias / cantidad_docentes,
            2
        )

        mayor = max(
            docentes,
            key=docentes.get
        )

        menor = min(
            docentes,
            key=docentes.get
        )

    else:

        promedio = 0

        mayor = "Sin datos"

        menor = "Sin datos"
    
    # ==========================================================
    # GRÁFICO DE AUSENTISMO
    # ==========================================================
    def grafico_barras():

        nombres = list(docentes.keys())

        valores = list(docentes.values())

        plt.figure(figsize=(10, 6))

        plt.bar(
            nombres,
            valores
        )

        plt.title(
            "Ausentismo Docente"
        )

        plt.xlabel(
            "Docentes"
        )

        plt.ylabel(
            "Días de Inasistencia"
        )

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.show()

    # ==========================================================
    # GRÁFICO TORTA
    # ==========================================================
    def grafico_torta():

        etiquetas = list(estados.keys())

        valores = list(estados.values())

        plt.figure(figsize=(8, 8))

        plt.pie(

            valores,

            labels=etiquetas,

            autopct='%1.1f%%'

        )

        plt.title(
            "Tipos de Inasistencias"
        )

        plt.show()


    # ==========================================================
    # FRAME PRINCIPAL
    # ==========================================================
    frame = ttk.LabelFrame(

        ventana,

        text="Estadísticas Institucionales"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    # ==========================================================
    # LABELS
    # ==========================================================
    ttk.Label(

        frame,

        text=f"Total Institucional: {total_inasistencias} días",

        font=("Arial", 11, "bold")

    ).pack(anchor="w", pady=5)

    ttk.Label(

        frame,

        text=f"Cantidad de Docentes: {cantidad_docentes}",

        font=("Arial", 11)

    ).pack(anchor="w", pady=5)

    ttk.Label(

        frame,

        text=f"Promedio Institucional: {promedio} días",

        font=("Arial", 11)

    ).pack(anchor="w", pady=5)

    ttk.Label(

        frame,

        text=f"Más Ausencias: {mayor} ({docentes.get(mayor,0)} días)",

        font=("Arial", 11),

        foreground="red"

    ).pack(anchor="w", pady=5)

    ttk.Label(

        frame,

        text=f"Menos Ausencias: {menor} ({docentes.get(menor,0)} días)",

        font=("Arial", 11),

        foreground="green"

    ).pack(anchor="w", pady=5)

    # ==========================================================
    # SEPARADOR
    # ==========================================================
    ttk.Separator(
        frame,
        orient="horizontal"
    ).pack(fill="x", pady=10)

    ttk.Label(

        frame,

        text="Resumen por Tipo",

        font=("Arial", 11, "bold")

    ).pack(anchor="w")

    # ==========================================================
    # ESTADOS
    # ==========================================================
    for estado, dias in estados.items():

        ttk.Label(

            frame,

            text=f"{estado}: {dias} días"

        ).pack(anchor="w")

    # ==========================================================
    #                   BOTONES
    # ==========================================================
    
    # ---------------------- BOTÓN CERRAR -------------------------------------
    ttk.Button(ventana, text="❌ Cerrar", command=ventana.destroy).pack(pady=10)
    
    # ---------------------- BOTÓN GRÁFICO DE BARRAS --------------------------
    ttk.Button(ventana, text="📊 Gráfico Barras", command=grafico_barras).pack(pady=5)
    
    # ---------------------- BOTÓN GRÁFICO TORTA --------------------------
    ttk.Button(ventana, text="🥧 Gráfico Torta", command=grafico_torta).pack(pady=5)

    centrar_ventana(ventana)