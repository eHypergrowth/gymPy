import sqlite3
import os

# Ruta del directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gimnasio.db")  # Ruta completa para la base de datos
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")  # Ruta completa para el esquema

def inicializar_db(force=False):
    """
    Crea la base de datos y las tablas usando schema.sql.
    Si force=True, elimina y recrea la base de datos.
    """
    try:
        if force and os.path.exists(DB_PATH):
            os.remove(DB_PATH)  # Eliminar base de datos existente si force=True
            print("Base de datos eliminada y será recreada.")
        
        if not os.path.exists(DB_PATH) or force:
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
            with open(SCHEMA_PATH, "r") as archivo:
                cursor.executescript(archivo.read())  # Ejecuta el script del esquema
            conexion.commit()
            conexion.close()
            print("Base de datos inicializada/creada correctamente.")
        else:
            print("La base de datos ya existe y no se modificará.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

def conectar():
    """Establece la conexión a la base de datos."""
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def obtener_configuracion(clave):
    """Obtiene el valor de una configuración específica."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT valor FROM configuraciones WHERE clave = ?", (clave,))
        resultado = cursor.fetchone()
        conexion.close()
        if resultado:
            return resultado[0]
        return None  # Si no se encuentra la clave
    except Exception as e:
        print(f"Error al obtener configuración: {e}")
        return None


# Ejecutar la inicialización si se ejecuta directamente
if __name__ == "__main__":
    inicializar_db()
