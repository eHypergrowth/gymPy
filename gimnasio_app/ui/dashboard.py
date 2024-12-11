from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QStackedWidget
)
from PyQt5.QtCore import Qt
from logger_config import logger
from ui.gestion_clientes_ui import GestionClientes
from ui.gestion_planes_ui import GestionPlanes
from ui.gestion_pagos_ui import GestionPagos
from ui.gestion_usuarios_ui import GestionUsuarios
from ui.gestion_entradas_salidas_ui import GestionEntradasSalidas
from ui.configuracion_parametros_ui import ConfiguracionParametros
from ui.gestion_contratos_ui import GestionContratos  # Nuevo módulo de contratos


class Dashboard(QMainWindow):
    def __init__(self, id_usuario, username, rol):
        super().__init__()
        self.id_usuario = id_usuario
        self.username = username
        self.rol = rol

        # Configuración de la ventana
        self.setWindowTitle(f"Dashboard - {id_usuario} | {username} | {rol if rol else 'Sistema'}")
        self.setGeometry(100, 100, 1000, 600)
        logger.info(f"Iniciando Dashboard con rol: {rol}")

        # Estilo del sistema
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
                padding: 8px;
            }
        """)

        # Layout principal
        main_layout = QHBoxLayout()
        menu_layout = QVBoxLayout()

        # Botones de menú
        self.btn_clientes = QPushButton("Gestión de Clientes")
        self.btn_planes = QPushButton("Gestión de Planes")
        self.btn_pagos = QPushButton("Gestión de Pagos")
        self.btn_entradas_salidas = QPushButton("Entradas/Salidas")
        self.btn_contratos = QPushButton("Gestión de Contratos")  # Nuevo botón de contratos
        self.btn_config = QPushButton("Config")
        self.btn_usuarios = QPushButton("Gestión de Usuarios")
        self.btn_salir = QPushButton("Salir")
        self.btn_salir.setStyleSheet("background-color: #E74C3C; color: #FFFFFF;")

        # Conectar el botón de salir
        self.btn_salir.clicked.connect(self.salir)

        # Mostrar menús según el rol
        self.mostrar_menus_por_rol(menu_layout)

        # Agregar el botón Salir siempre visible
        menu_layout.addWidget(self.btn_salir)

        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)
        menu_widget.setFixedWidth(200)

        # Contenido principal
        self.content = QStackedWidget()
        self.content.setStyleSheet("background-color: #34495E; border-radius: 10px;")

        # Páginas
        self.inicializar_paginas()

        main_layout.addWidget(menu_widget)
        main_layout.addWidget(self.content)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Mostrar la primera página del rol
        self.mostrar_primera_pagina()

    def inicializar_paginas(self):
        """Inicializa las páginas del Dashboard."""
        try:
            self.pagina_clientes = GestionClientes()
            self.content.addWidget(self.pagina_clientes)
        except Exception as e:
            logger.error(f"Error al cargar Gestión de Clientes: {e}")

        try:
            self.pagina_planes = GestionPlanes()
            self.content.addWidget(self.pagina_planes)
        except Exception as e:
            logger.error(f"Error al cargar Gestión de Planes: {e}")

        try:
            self.pagina_pagos = GestionPagos(usuario_actual=self.username)
            self.content.addWidget(self.pagina_pagos)
        except Exception as e:
            logger.error(f"Error al cargar Gestión de Pagos: {e}")

        try:
            self.pagina_entradas_salidas = GestionEntradasSalidas()
            self.content.addWidget(self.pagina_entradas_salidas)
        except Exception as e:
            logger.error(f"Error al cargar Gestión de Entradas y Salidas: {e}")

        try:
            self.pagina_contratos = GestionContratos()  # Nueva página de contratos
            self.content.addWidget(self.pagina_contratos)
        except Exception as e:
            logger.error(f"Error al cargar Gestión de Contratos: {e}")

        try:
            self.pagina_config = ConfiguracionParametros()
            self.content.addWidget(self.pagina_config)
        except Exception as e:
            logger.error(f"Error al cargar Configuración: {e}")

        try:
            self.pagina_usuarios = GestionUsuarios()
            self.content.addWidget(self.pagina_usuarios)
        except Exception as e:
            logger.error(f"Error al cargar Gestión de Usuarios: {e}")

    def mostrar_menus_por_rol(self, menu_layout):
        """Muestra los menús según el rol del usuario."""
        if self.rol == "SysAdmin":
            self.btn_config.clicked.connect(self.mostrar_configuracion)
            self.btn_config.setStyleSheet("background-color: #E67E22; color: #FFFFFF;")
            menu_layout.addWidget(self.btn_config)

        elif self.rol == "Administrador":
            self.btn_clientes.clicked.connect(self.mostrar_clientes)
            self.btn_planes.clicked.connect(self.mostrar_planes)
            self.btn_pagos.clicked.connect(self.mostrar_pagos)
            self.btn_entradas_salidas.clicked.connect(self.mostrar_entradas_salidas)
            self.btn_contratos.clicked.connect(self.mostrar_gestion_contratos)  # Conectar botón de contratos
            self.btn_usuarios.clicked.connect(self.mostrar_usuarios)

            menu_layout.addWidget(self.btn_clientes)
            menu_layout.addWidget(self.btn_planes)
            menu_layout.addWidget(self.btn_pagos)
            menu_layout.addWidget(self.btn_entradas_salidas)
            menu_layout.addWidget(self.btn_contratos)  # Agregar debajo de Entradas/Salidas
            menu_layout.addWidget(self.btn_usuarios)

        elif self.rol == "Cajero":
            self.btn_clientes.clicked.connect(self.mostrar_clientes)
            self.btn_pagos.clicked.connect(self.mostrar_pagos)
            self.btn_entradas_salidas.clicked.connect(self.mostrar_entradas_salidas)
            menu_layout.addWidget(self.btn_clientes)
            menu_layout.addWidget(self.btn_pagos)
            menu_layout.addWidget(self.btn_entradas_salidas)

        elif self.rol == "Consultor":
            self.btn_planes.clicked.connect(self.mostrar_planes)
            menu_layout.addWidget(self.btn_planes)

    def mostrar_primera_pagina(self):
        """Muestra la primera página correspondiente al rol."""
        if self.rol == "SysAdmin":
            self.mostrar_configuracion()
        elif self.rol == "Administrador":
            self.mostrar_clientes()
        elif self.rol == "Cajero":
            self.mostrar_clientes()
        elif self.rol == "Consultor":
            self.mostrar_planes()

    def mostrar_clientes(self):
        self.content.setCurrentWidget(self.pagina_clientes)

    def mostrar_planes(self):
        self.content.setCurrentWidget(self.pagina_planes)

    def mostrar_pagos(self):
        self.content.setCurrentWidget(self.pagina_pagos)

    def mostrar_entradas_salidas(self):
        self.content.setCurrentWidget(self.pagina_entradas_salidas)

    def mostrar_gestion_contratos(self):
        """Muestra la página de Gestión de Contratos."""
        try:
            self.content.setCurrentWidget(self.pagina_contratos)
            logger.info("Gestión de Contratos mostrada correctamente.")
        except Exception as e:
            logger.error(f"Error al mostrar Gestión de Contratos: {e}")

    def mostrar_configuracion(self):
        self.content.setCurrentWidget(self.pagina_config)

    def mostrar_usuarios(self):
        self.content.setCurrentWidget(self.pagina_usuarios)

    def salir(self):
        """Cierra la sesión actual y regresa al login."""
        from ui.login_ui import Login
        self.close()
        self.login = Login()
        self.login.show()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    rol_prueba = "Administrador"
    window = Dashboard(1, "admin", rol_prueba)  # Prueba con ID, Username y Rol
    window.show()
    sys.exit(app.exec_())
