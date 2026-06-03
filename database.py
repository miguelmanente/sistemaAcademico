# =====================================================
#            MÓDULO CREACIÓN DE TABLAS DE LA BD
# =====================================================

# ------------------------ LIBRERÍAS  ---------------------------------
import sqlite3
import hashlib
import os, sys
from backup import crear_backup

#--------- función que permite conectarse a la BD profesores -----------------------
def conectar():
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DATABASE = os.path.join(BASE_DIR, "profesores.db")

    print("Base de datos:", DATABASE)

    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
# ----------------------------------------------------------------------------------

# -------------------- Encriptar contraseña de usuarios ----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
#-----------------------------------------------------------------------------------

# ----------- Registrar usuario que luego permite loguearse ------------------------
def registrar_usuario(username, password):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Usuario ya existe
# --------------------------- Fin función Registrar Usuario -------------------------


# ---------------------- Validar login del usuario para loguearse -------------------
def validar_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario
# ---------------------------- Fin función validación---------------------------------------------------


#---------------------  CREAR Y VERIFICAR SI ESTÁN CREADAS LAS TABLAS ----------------
def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS profesores (
        id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
        apenom TEXT,
        telefono TEXT,
        email TEXT,
        sitrev TEXT,
        fechatp TEXT
    );
    
    CREATE TABLE IF NOT EXISTS cargos (
        id_cargo INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_cargo TEXT NOT NULL
    );
                         
    CREATE TABLE IF NOT EXISTS personal_cargos (
        id_personal_cargo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_profesor INTEGER,
        id_cargo INTEGER,
        dia TEXT,
        turno TEXT,
        desde TEXT,
        hasta TEXT,

        FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
        FOREIGN KEY (id_cargo) REFERENCES cargos(id_cargo)
    );

    CREATE TABLE IF NOT EXISTS materias (
        id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS cursos (
        id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        turno TEXT
    );

    CREATE TABLE IF NOT EXISTS horarios (
        id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
        id_curso INTEGER,
        id_materia INTEGER,
        dia TEXT,
        hentrada TEXT,
        hsalida TEXT,
        FOREIGN KEY (id_curso) REFERENCES cursos(id_curso),
        FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
    );

    CREATE TABLE IF NOT EXISTS asignaciones_docentes (
        id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_profesor INTEGER,
        id_horario INTEGER,
        srprofesor TEXT,
        FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
        FOREIGN KEY (id_horario) REFERENCES horarios(id_horario)
    );
                         
    CREATE TABLE IF NOT EXISTS historial_docente (

        id_historial INTEGER PRIMARY KEY AUTOINCREMENT,

        id_profesor INTEGER NOT NULL,
        id_materia INTEGER NOT NULL,
        id_curso INTEGER NOT NULL,

        situacion TEXT NOT NULL,

        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT,

        observaciones TEXT,

        FOREIGN KEY(id_profesor) REFERENCES profesores(id_profesor),
        FOREIGN KEY(id_materia) REFERENCES materias(id_materia),
        FOREIGN KEY(id_curso) REFERENCES cursos(id_curso)
    );
    CREATE TABLE IF NOT EXISTS asistencias_docentes(
        id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_profesor INTEGER NOT NULL,
        fecha_desde TEXT,
        fecha_hasta TEXT,
        estado TEXT,
        observacion TEXT,

        FOREIGN KEY(id_profesor)
            REFERENCES profesores(id_profesor)
    );

    """)

    conn.commit()
    crear_backup()
    conn.close()