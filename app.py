# =====================================================
#            MÓDULO SISTEMA EDUCATIVO - APP
# =====================================================

# ----------------------------- LIBRERÍAS -------------------------------
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk  # Necesitas instalar Pillow para el logo pag ppal
import os
from database import crear_tablas
from centraVent import centrar_ventana
from datos_personales import info_profesor
from altasCargos import ventana_cargos
from altaMaterias import info_materias
from altaCursos import info_cursos
from altaHorarios import info_horarios
from altaAsignaciones import info_asignaciones
from listados import ventana_listado
import sesion
from estilos import configurar_estilos
from listadoCursos import ventana_listado_curso
from listadoTurnos import listado_personal_turnos
from historialDocente import ventana_historial
from asistenciaDocente import ventana_asistencias
from rankingAusentismo import ventana_ranking
from estadisticasDocentes import ventana_estadisticas
from parte_diario import abrir_parte_diario


#Código - Zona de funciones
#Crea la tablas de la BD si no están creadas

# ----------------------  CREACIÓN DE VENTANA ABRIR SISTEMA --------------------------------------
def pPrincipal():
    crear_tablas()

    # ------------------------------- Pantalla Acerca de la App ----------------------------------
    def acerca_de():

        win = tk.Toplevel(ventana)
        win.title("Acerca de")
        win.geometry("400x250")
        win.resizable(False, False)

        imagen = Image.open("logotipo.png")
        imagen = imagen.resize((120, 120))
        logo = ImageTk.PhotoImage(imagen)
        lbl_logo = ttk.Label(win, image=logo)
        lbl_logo.image = logo
        lbl_logo.pack(pady=10)

        ttk.Label(win, text="Sistema de Gestión Académica", font=("Arial", 16, "bold")).pack(pady=15)
        ttk.Label(win, text="Versión 1.9", font=("Arial", 11)).pack()
        ttk.Label(win, text="Desarrollado por:\nMiguel Ángel Manente", font=("Arial", 11)).pack(pady=15)
        ttk.Label(win, text="© 2026", font=("Arial", 10)).pack()
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=20)
        centrar_ventana(win)
    # -----------------------------------------------------------------------------------------------

    #-------------------------------  Salir de la aplicación -------------------------------------  
    def salir():
        if messagebox.askyesno("Salir", "¿Desea cerrar Sistema de Gestión Educativo?", parent=ventana):
            ventana.destroy()
    #----------------------------------------------------------------------------------------------


    #------ TKINTER -------------------------------------------------------------------------------
    #-------------------------------------- VENTANA PRINCIPAL -------------------------------------
    #Ventana principal 
    ventana = tk.Toplevel()
    ventana.tk.call('tk', 'scaling', 1.0)  # (opcional)
    ventana.title("SISTEMA ACADÉMICO")
    ventana.geometry("1100x700")
    
    #ventana.protocol("WM_DELETE_WINDOW", lambda: None)  anula de la barra superior LA X para cerrar ventana
    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=0)
    ventana.columnconfigure(0, weight=1)

        # ---------------- TOP BAR ----------------
    frame_top = tk.Frame(ventana, bg="#2c3e50", height=30)
    frame_top.pack(fill="x")

    lbl_usuario = tk.Label(
        frame_top,
        text=f"Usuario: {sesion.usuario_actual}",
        bg="#2c3e50",
        fg="white",
        font=("Arial", 10, "bold")
    )
    lbl_usuario.pack(side="right", padx=10)
    

    #-------------------------------------- BARRA DE NENÚ -----------------------------------------

    #Barra de menúes
    barramenu = tk.Menu(ventana)
    ventana.config(menu=barramenu)

    #Menú Archivo
    mArchivo = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Archivo", menu=mArchivo)
    mArchivo.add_command(label="Salir", command=salir)

    #Menú Profesor
    mProfesor =tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Profesor", menu=mProfesor)
    mProfesor.add_command(label="Datos Personales", command=info_profesor)
    mProfesor.add_command(label="Personal con cargos", command=ventana_cargos)

    #Menú Materias
    mMaterias = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Materias", menu=mMaterias)
    mMaterias.add_command(label="Agregar Materias", command=info_materias)

    #Menú Cursos
    mCursos = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Cursos", menu=mCursos)
    mCursos.add_command(label="Agregar Cursos", command=info_cursos)

    #Menú Horarios
    mHorarios = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Horarios", menu=mHorarios)
    mHorarios.add_command(label="Creación de Horarios", command=info_horarios)

    #Menú Asignacopnes de Profesores
    mAsignaciones = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Asignaciones", menu=mAsignaciones)
    mAsignaciones.add_command(label="Asignaciones Profesores", command=info_asignaciones)

    #Menú Listados de profesores
    mListados = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Listados", menu=mListados)
    mListados.add_command(label="Profesores Titulares", command=lambda: ventana_listado("Titular"))
    mListados.add_command(label="Profesores Provisorio", command=lambda: ventana_listado("Provisorio"))
    mListados.add_command(label="Profesores Suplentes",command=lambda: ventana_listado("Suplente"))
    mListados.add_separator()
    mListados.add_command(label="Listado por Curso", command=ventana_listado_curso)
    mListados.add_command(label="Listados por Turnos", command=abrir_parte_diario)

    #Menú Historial Docente
    mHistorial = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Historial", menu=mHistorial)
    mHistorial.add_command(label="Historial Docente", command=ventana_historial)

    # Menú Asistencias Docentes
    mAsistencias = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Asistencias", menu=mAsistencias)
    mAsistencias.add_command(label="Control Docente", command=ventana_asistencias)
    mAsistencias.add_command(label="Ranking Inasistencias", command=ventana_ranking)
    mAsistencias.add_command(label="Estadisticas Docentes", command=ventana_estadisticas)

    #Menú Acerca
    mAcerca = tk.Menu(barramenu, tearoff=0)
    barramenu.add_cascade(label="Ayuda", menu=mAcerca)
    mAcerca.add_command(label="Acerca de la App", command=acerca_de)
    
  # ---------------------------------- LOGO PRINCIPAL -------------------------------------
   
    
    logoP = tk.Frame(ventana)
    logoP.pack(expand=True)  # Centra el contenido en la ventana

    # Cargar el logo
    try:
        logo = Image.open("logos.png")  # Asegúrate de que el archivo esté en la misma carpeta
        logo = logo.resize((600, 400))
        logo_tk = ImageTk.PhotoImage(logo)

        # Mostrar el logo
        label_logo = tk.Label(logoP, image=logo_tk)
        label_logo.image = logo_tk  # Mantener referencia para evitar que se elimine
        label_logo.pack(pady=(10,5))

    except Exception as e:
        print(f"No se pudo cargar el logo: {e}")
        label_logo = tk.Label(logoP, text="[Logo no disponible]")
        label_logo.pack(pady=(10,5))

    # Texto debajo del logo
    label_text = tk.Label(
        logoP,
        text="Sistema Educativo - Gestión Escolar",
        font=("Arial", 20, "bold")
    )
    label_text.pack(pady=(0,10))
    # ---------------------------------------------------------------------------------------

    # ---------------------------------- FOOTER -------------------------------------

    img = Image.open("logo2.png")
    img = img.resize((120, 80))  # tamaño exacto que quieras
    logo = ImageTk.PhotoImage(img)
    # logo = tk.PhotoImage(file="logotipo.png")
    # logo = logo.subsample(10, 10)

    # Frame footer (usar PACK porque la ventana usa pack)
    frame_footer = tk.Frame(ventana)
    frame_footer.pack(side="bottom", anchor="w", padx=10, pady=5)

    lbl_logo = tk.Label(frame_footer, image=logo)
    lbl_logo.pack(anchor="w")

    lbl_texto = tk.Label(
        frame_footer,
        text="© 2026 Programas MAM",
        font=("Arial", 12),
        fg="gray"
    )
    lbl_texto.pack(anchor="w")

    lbl_logo.image = logo
    #-------------------------------------------------------------------------------------------

    configurar_estilos()
    centrar_ventana(ventana)



