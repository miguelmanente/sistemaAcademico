# ========================================================================================
#                  MÓDULO PARA BACKUP DE BASE DE DATOS
# ========================================================================================
import os
import shutil

# --------------------------------------- FUNCION DE CREACIÓN ----------------------------
def crear_backup():

    try:

        carpeta = "backups"

        os.makedirs(carpeta, exist_ok=True)

        destino = os.path.join(
            carpeta,
            "profesoresBak.db"
        )

        shutil.copy2(
            "profesores.db",
            destino
        )

        print("Backup actualizado")

    except Exception as e:

        print("Error backup:", e)
# -------------------------------------------------------------------------------------------