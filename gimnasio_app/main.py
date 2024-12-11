import sys
from PyQt5.QtWidgets import QApplication
from ui.login_ui import Login
from logger_config import logger  # Importar el logger configurado
from database.database import inicializar_db  # Importar la función para inicializar la base de datos

def main():
    """Función principal que inicializa la aplicación."""
    logger.info("Iniciando la APP")

    # Inicializar la base de datos
    try:
        inicializar_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)  # Salir si hay un error crítico al inicializar la base de datos

    # Iniciar la aplicación
    app = QApplication(sys.argv)
    ventana = Login()  # Carga la interfaz de login
    ventana.show()
    exit_code = app.exec_()
    logger.info("Saliendo del Sistema")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
