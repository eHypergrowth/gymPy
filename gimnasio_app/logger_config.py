import logging
import os
from logging.handlers import RotatingFileHandler

# Crear el directorio "logs" si no existe
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configurar el archivo de logs
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configurar rotación de logs
rotating_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5
)

# Configuración del logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        rotating_handler,          # Rotación de logs
        logging.StreamHandler()    # Mostrar logs en consola
    ]
)

logger = logging.getLogger("GimnasioApp")
