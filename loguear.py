import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import validar_usuario
from centraVent import cventana

#----------------------------- Ventana para que el usuario se loguee ----------------------
usuario_logueado = None  # Variable global


def ventana_login(root):

    global usuario_logueado

    login = tk.Toplevel(root)
    login.title("Iniciar Sesión")
    login.geometry("400x300")
    login.grab_set()

    tk.Label(login, text="Usuario").pack(pady=5)
    entry_usuario = tk.Entry(login)
    entry_usuario.pack()

    tk.Label(login, text="Contraseña").pack(pady=5)
    entry_password = tk.Entry(login, show="*")
    entry_password.pack()

    def iniciar_sesion():
        global usuario_logueado

        usuario = entry_usuario.get()
        password = entry_password.get()

        resultado = validar_usuario(usuario, password)

        if resultado:
            usuario_logueado = usuario
            messagebox.showinfo("Bienvenido", f"Se ha logueado al sistema {usuario}")
            login.destroy()
            root.deiconify()  # 🔥 MOSTRAR APP
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def salir():
        root.destroy()  # 🔥 cerrar toda la app

    tk.Button(login, text="Ingresar", command=iniciar_sesion).pack(pady=10)
    tk.Button(login, text="Salir", command=salir).pack(pady=10)

    # 🔥 si cierra la X → también cerrar todo
    login.protocol("WM_DELETE_WINDOW", salir)
#--------------------------------------------------------------------------------------------

    cventana(login)

