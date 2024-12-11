# Proyecto de Gestión de Gimnasio

Este proyecto es una aplicación de escritorio desarrollada en Python y PyQt5 para gestionar un gimnasio. Incluye funcionalidades como gestión de clientes, planes, pagos, contratos y más.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes requisitos en tu sistema:

1. **Python 3.8+**: Descárgalo desde [Python.org](https://www.python.org/).
2. **Git**: Para clonar el repositorio.

## Instalación

Para instalar y configurar el proyecto, simplemente ejecuta el script `installDevelop`, el cual automatiza todo el proceso:

### 1. Clonar el repositorio

Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/eHypergrowth/gymPy.git
cd gymPy/gimnasio_app
```

### 2. Ejecutar el script de instalación

El proyecto incluye un script llamado `installDevelop` que realiza la instalación completa. Solo necesitas ejecutarlo:
```bash
chmod +x installDevelop
./installDevelop
```

Este script:
- Verifica si `python3-venv` está instalado e intenta instalarlo si falta.
- Crea un entorno virtual llamado `env`.
- Instala las dependencias desde el archivo `requirements.txt`.
- Ejecuta automáticamente la aplicación.

### 3. Iniciar manualmente la aplicación (opcional)

Si prefieres iniciar manualmente la aplicación después de configurar el entorno:
```bash
source env/bin/activate  # Activa el entorno virtual
python main.py           # Ejecuta la aplicación
```

## Estructura del Proyecto

```
📂 gimnasio_app
├── assets
│   ├── icons
│   │   └── login_icon.jpg
│   └── styles
├── database
│   ├── database.py          # Configuración y manejo de la base de datos
│   ├── gimnasio.db          # Base de datos SQLite
│   ├── __init__.py
│   └── schema.sql           # Esquema de la base de datos
├── docs                     # Documentación
├── generated_pdfs           # PDFs generados
├── installDevelop           # Script de instalación para desarrollo
├── logger_config.py         # Configuración del sistema de logs
├── logs
│   └── app.log              # Logs de la aplicación
├── main.py                  # Punto de entrada de la aplicación
├── models
│   ├── clientes.py          # Modelo para clientes
│   ├── contratos.py         # Modelo para contratos
│   ├── login.py             # Modelo para login
│   ├── pagos.py             # Modelo para pagos
│   └── planes.py            # Modelo para planes
├── requirements.txt         # Dependencias del proyecto
├── resetDb                  # Script para resetear la base de datos
├── run                      # Script para ejecutar la aplicación
├── sqlite3console           # Consola SQLite3
├── structure                # Script para mostrar la estructura del proyecto
├── testingSqLite.py         # Pruebas con SQLite
├── ui
│   ├── configuracion_parametros_ui.py # Gestión de configuración
│   ├── dashboard.py         # Ventana principal del sistema
│   ├── gestion_clientes_ui.py  # Gestión de clientes
│   ├── gestion_contratos_ui.py # Gestión de contratos
│   ├── gestion_entradas_salidas_ui.py # Gestión de entradas y salidas
│   ├── gestion_pagos_ui.py    # Gestión de pagos
│   ├── gestion_planes_ui.py   # Gestión de planes
│   ├── gestion_usuarios_ui.py # Gestión de usuarios
│   └── login_ui.py            # Pantalla de inicio de sesión
└── utils
    ├── email_utils.py        # Utilidades para correos
    └── text_utils.py         # Utilidades para manejo de texto
```

## Funcionalidades Principales

- **Gestión de Clientes**: Crear, leer, actualizar y eliminar clientes.
- **Gestión de Planes**: Configurar diferentes tipos de planes.
- **Gestión de Pagos**: Registrar pagos realizados por los clientes.
- **Gestión de Contratos**: Administrar los contratos de los clientes.

## Problemas Comunes

### Error: "`sqlite3.OperationalError: no such table`"
Esto ocurre si la base de datos no está inicializada correctamente. Asegúrate de ejecutar:
```bash
python database/database.py
```

### Problemas con dependencias
Si encuentras problemas con dependencias, intenta reinstalarlas:
```bash
pip install -r requirements.txt --force-reinstall
```

## Contribuir

1. Haz un fork del proyecto.
2. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Haz tus cambios y realiza un commit:
   ```bash
   git commit -m "Agrega nueva funcionalidad"
   ```
4. Haz push a tu rama y abre un Pull Request:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
