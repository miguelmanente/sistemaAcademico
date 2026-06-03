# =====================================================
#        MÓDULO LOGIN DE USUARIO Y REGISTRACIÓN
# =====================================================

# -----------------------------------------  LIBRERÍAS ---------------------------------------------------
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from centraVent import centrar_ventana, cventana
from database import validar_usuario
from app import pPrincipal
from registrar import ventana_registro
import sesion  # muestra la variable del usuario conectado al sistema
from backup import crear_backup
from estilos import configurar_estilos


# ------------------------------------------------ VARIABLE GLOBAL ----------------------------------------
usuario_logueado = None
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------------- LOGIN -----------------------------------------------------
def ventana_login(root, barramenu, lbl_usuario):
    global usuario_logueado

    login = tk.Toplevel(root, bg="#ecf0f1", pady=30)
    configurar_estilos()
    login.title("LOGIN DE USUARIOS")
    login.geometry("500x400")
    #login.grab_set()  # 🔥 bloquea la ventana principal

    tk.Label(login, text="Usuario", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=15)
    entry_usuario = tk.Entry(login, font=("Arial", 12))
    entry_usuario.pack()

    tk.Label(login, text="Contraseña", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=15)
    entry_password = tk.Entry(login, show="*", font=("Arial", 12))
    entry_password.pack()

    def iniciar_sesion():
        global usuario_logueado

        usuario = entry_usuario.get()
        password = entry_password.get()

        if validar_usuario(usuario, password):
            usuario_logueado = usuario
            sesion.usuario_actual = usuario
            lbl_usuario.config(text=f"Usuario: {usuario}")

            # habilitar menú
            for i in range(barramenu.index("end") + 1):
                barramenu.entryconfig(i, state="normal")

            messagebox.showinfo("Bienvenido", f"Bienvenido, {usuario} ha ingresado Sistema de Gestión Educativa")

            login.destroy()
            root.deiconify()  # 🔥 mostrar sistema

        else:
            messagebox.showerror("Error!!!", "Usuario o contraseña incorrectos o no está registrado", parent=login)

            if not(validar_usuario(usuario, password)):
                respuesta = messagebox.askyesno("Registrar Usuarios", "Desea Registrarse (Si/No)?")
                if respuesta:
                    ventana_registro()
                else:
                    ventana_login(root, barramenu, lbl_usuario)
    # ----------------------------------------------------------------------------------------------------------------

    # ------------------------------------------- SALIR DE LA APLICACIÓN ---------------------------------------------
    def salir():
        root.destroy()
    # ----------------------------------------------------------------------------------------------------------------

    # ------------------------------------- BOTONES PARA INICIAR Y SALIR DEL LOGIN -----------------------------------
    tk.Button(login, text="Ingresar", bg="#3498db", fg="white", font=("Arial", 12, "bold"), command=iniciar_sesion).pack(pady=15)
    tk.Button(login, text="Salir", bg="#3498db", fg="white", font=("Arial", 12, "bold"), command=salir).pack(pady=15)
    # ----------------------------------------------------------------------------------------------------------------
    cventana(login)


# ------------------------------------------- VENTANA PRINCIPAL -----------------------------------------------------
root = tk.Tk()
root.title("SISTEMA ACADÉMICO")
root.geometry("1100x700")

# 🔥 OCULTAR HASTA LOGIN
root.withdraw()
# -------------------------------------------------------------------------------------------------------------------

# ---------------- BARRA INDICADORA DE USUARIO LOGUEADO  ------------------------------------------------------------
frame_top = tk.Frame(root, bg="#2c3e50", height=30)
frame_top.pack(fill="x")

lbl_usuario = tk.Label(
    frame_top,
    text="Usuario: ---",
    bg="#2c3e50",
    fg="white",
    font=("Arial", 10, "bold")
)
lbl_usuario.pack(side="right", padx=10)
# --------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------ BARRA DE MENÚES ---------------------------------------------
barramenu = tk.Menu(root)
root.config(menu=barramenu)

mArchivo = tk.Menu(barramenu, tearoff=0)
barramenu.add_cascade(label="Archivo", menu=mArchivo)
mArchivo.add_command(label="Abrir Sistema", command=pPrincipal)
mArchivo.add_separator()
mArchivo.add_command(label="Salir", command=root.destroy)

# 🔒 DESHABILITAR MENÚ
for i in range(barramenu.index("end") + 1):
    barramenu.entryconfig(i, state="disabled")
# --------------------------------------------------------------------------------------------------------------------

 # ---------------------------------- LOGO PRINCIPAL -----------------------------------------------------------------
logoP = tk.Frame(root)
logoP.pack(expand=True)  # Centra el contenido en la ventana

# Cargar el logo
try:
    logo = Image.open("logo.png")  # Asegúrate de que el archivo esté en la misma carpeta
    logo = logo.resize((500, 400))
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
#----------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------  FOOTER  -----------------------------------------------------------
img = Image.open("logo2.png")
img = img.resize((120, 80))  # tamaño exacto que quieras
logo = ImageTk.PhotoImage(img)
# logo = tk.PhotoImage(file="logotipo.png")
# logo = logo.subsample(10, 10)

# Frame footer (usar PACK porque la ventana usa pack)
frame_footer = tk.Frame(root)
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
#----------------------------------------------------------------------------------------------------------------------

# ---------------- INICIAR LOGIN AUTOMÁTICO ---------------------------------------------------------------------------
ventana_login(root, barramenu, lbl_usuario)
crear_backup()
centrar_ventana(root)
# ---------------------------------------------------------------------------------------------------------------------

root.mainloop()



