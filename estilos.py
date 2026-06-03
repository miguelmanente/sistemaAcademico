#=======================================================================
#                      ESTILOS DE PANTALLAS
#=======================================================================

from tkinter import ttk

def configurar_estilos():

    style = ttk.Style()

    # Tema
    style.theme_use("clam")

    # Labels
    style.configure(
        "TLabel",
        background="#ecf0f1",
        foreground="#2c3e50",
        font=("Arial", 11)
    )

    # Botones normales
    style.configure(
        "TButton",
        font=("Arial", 12, "bold"),
        padding=6
    )

    # Entry
    style.configure(
        "TEntry",
        padding=5
    )

    # Combobox
    style.configure(
        "TCombobox",
        padding=5
    )

    # Treeview
    style.configure(
        "Treeview",
        font=("Arial", 12),
        rowheight=25
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 12, "bold")
    )

    # Botón azul personalizado
    style.configure(
        "Azul.TButton",
        background="#3498db",
        foreground="white",
        font=("Arial", 12, "bold")
    )

    return style