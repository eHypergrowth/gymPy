import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt
from models.login import validar_usuario  # Función para validar usuario
from ui.dashboard import Dashboard  # Dashboard al que redirige después del login
from database.database import obtener_configuracion  # Para obtener configuraciones de la base de datos


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Sistema de Gestión")
        self.setGeometry(100, 100, 400, 400)

        # Estilo moderno
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                border: 2px solid #34495E;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #ECF0F1;
                color: #2C3E50;
            }
            QLineEdit:focus {
                border: 2px solid #1ABC9C;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout()

        # Título
        title_label = QLabel("Bienvenido al Sistema")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ECF0F1; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Logotipo dinámico
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        ruta_logo = obtener_configuracion("logo_sistema")  # Obtener ruta del logo desde la base de datos
        if ruta_logo:
            pixmap = QPixmap(ruta_logo)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                logo_label.setText("Logo no encontrado")
        else:
            logo_label.setText("Logo no configurado")
        layout.addWidget(logo_label)

        # Campo de Usuario
        self.user_label = QLabel("Usuario:")
        layout.addWidget(self.user_label)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su usuario")
        layout.addWidget(self.user_input)

        # Campo de Contraseña
        self.password_label = QLabel("Contraseña:")
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.iniciar_sesion)  # Procesar al presionar Enter
        layout.addWidget(self.password_input)

        # Botón de inicio de sesión
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.clicked.connect(self.iniciar_sesion)
        layout.addWidget(self.login_button)

        # Contenedor principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def iniciar_sesion(self):
        """Valida las credenciales y redirige al dashboard si son correctas."""
        username = self.user_input.text().strip()  # Eliminar espacios adicionales
        password = self.password_input.text().strip()

        # Llamar a la función de validación de usuario
        resultado = validar_usuario(username, password)  # Devuelve id_usuario, username, rol
        if resultado:
            id_usuario, username, rol = resultado
            # Configurar colores visibles para el QMessageBox
            self.reset_messagebox_styles()
            QMessageBox.information(self, "Éxito", f"Bienvenido, {username}")
            self.ir_dashboard(id_usuario, username, rol)  # Redirigir al dashboard
        else:
            self.reset_messagebox_styles()
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    def reset_messagebox_styles(self):
        """Restablece los estilos del QMessageBox para evitar problemas de visibilidad."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#2C3E50"))
        palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Text, QColor("#2abada"))
        QApplication.setPalette(palette)

    def ir_dashboard(self, id_usuario, username, rol):
        """Redirige al dashboard principal según el rol del usuario."""
        self.dashboard = Dashboard(id_usuario, username, rol)
        self.dashboard.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec_())
