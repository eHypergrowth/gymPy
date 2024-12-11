from database.database import conectar  # Actualiza la importación si es necesario
from logger_config import logger  # Importar el logger configurado

def validar_usuario(username, password):
    """Valida las credenciales del usuario y devuelve id_usuario, username y rol si es válido."""
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id_usuario, username, rol
            FROM usuarios
            WHERE LOWER(username) = LOWER(?) AND password = ?
        """, (username, password))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            return resultado  # Devuelve una tupla (id_usuario, username, rol)
        else:
            return None
    except Exception as e:
        logger.error(f"Error al validar usuario: {e}")
        return None
