# =====================================================
#            MÓDULO REGISTRACIÓN DE USUARIOS
# =====================================================
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import registrar_usuario
from centraVent import cventana


#--------------------- Registros en la tabla ususarios la loguearse ----------------
def ventana_registro():
    registro = tk.Toplevel(bg="#ecf0f1", pady=30)
    registro.title("REGISTRO DE USUARIO")
    registro.geometry("400x300")
    registro.grab_set()

    tk.Label(registro, text="Usuario", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=15)
    entry_usuario = tk.Entry(registro, font=("Arial", 12))
    entry_usuario.pack()

    tk.Label(registro, text="Contraseña", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=15)
    entry_password = tk.Entry(registro, show="*", font=("Arial", 12))
    entry_password.pack()

    def registrar():
        usuario = entry_usuario.get()
        password = entry_password.get()

        if not usuario or not password:
            messagebox.showwarning("Advertencia", "Complete todos los campos", parent=registro)
            return

        if registrar_usuario(usuario, password):
            messagebox.showinfo("Éxito", "Usuario registrado correctamente", parent=registro)
            registro.destroy()
        else:
            messagebox.showerror("Error", "El usuario ya existe", parent=registro)

    
    #-------------------------------  Salir de la aplicación -------------------------------------
    def salir():
        if messagebox.askyesno("Salir", "¿Desea salir de registración?", parent=registro):
            registro.destroy()
    #----------------------------------------------------------------------------------------------
    
    #botenes de la vnetana de logueo
    tk.Button(registro, text="Registrarse", bg="#3498db",fg="white", font=("Arial", 12, "bold"), command=registrar).pack(pady=15)
    tk.Button(registro, text="Salir", bg="#3498db",fg="white", font=("Arial", 12, "bold"), command=salir).pack(pady=15)
#-----------------------------------------------------------------------------------


    #Llama a la función que está en el módulo centraVent
    cventana(registro)