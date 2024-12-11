from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QLineEdit, QComboBox, QMessageBox, QHeaderView, QInputDialog
)
from PyQt5.QtCore import Qt
from database.database import conectar
from logger_config import logger

class GestionUsuarios(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios")
        self.setGeometry(100, 100, 800, 600)

        # Estilo moderno con colores claros
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                font-size: 14px;
                color: #2C3E50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #4CAF50;
                padding: 8px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4CAF50;
            }
        """)

        layout = QVBoxLayout()

        # Tabla para mostrar usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Usuario", "Rol", "Acciones"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # No permitir editar directamente
        layout.addWidget(self.table)

        # Ajustar automáticamente el tamaño de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Ajustar "ID" al contenido
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Ajustar "Usuario" proporcionalmente
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Ajustar "Rol" al contenido
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Ajustar "Acciones" al contenido

        logger.info("Mostrando Tabla de Usuarios")

        # Formulario para agregar o actualizar usuarios
        form_layout = QHBoxLayout()
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Nombre de Usuario")
        form_layout.addWidget(self.input_username)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.input_password)

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["SysAdmin", "Administrador", "Cajero", "Consultor"])
        form_layout.addWidget(self.combo_rol)

        btn_agregar = QPushButton("Agregar Usuario")
        btn_agregar.clicked.connect(self.agregar_usuario)
        form_layout.addWidget(btn_agregar)

        layout.addLayout(form_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Carga todos los usuarios en la tabla."""
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_usuario, username, rol FROM usuarios")
        registros = cursor.fetchall()
        conexion.close()

        self.table.setRowCount(0)
        for row, registro in enumerate(registros):
            self.table.insertRow(row)
            for col, data in enumerate(registro):
                item = QTableWidgetItem(str(data))
                if col == 0:  # Hacer que la columna ID no sea editable
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

            # Crear un widget para contener los botones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(5)  # Espaciado entre los botones
            actions_layout.setContentsMargins(0, 0, 0, 0)  # Quitar márgenes

            # Botón Editar
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; border-radius: 5px;")
            btn_editar.clicked.connect(lambda _, r=registro: self.editar_usuario(r))
            actions_layout.addWidget(btn_editar)

            # Botón Eliminar
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("background-color: #E74C3C; color: white; padding: 5px; border-radius: 5px;")
            btn_eliminar.clicked.connect(lambda _, id=registro[0]: self.eliminar_usuario(id))
            actions_layout.addWidget(btn_eliminar)

            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 3, actions_widget)

    def agregar_usuario(self):
        """Agrega un nuevo usuario al sistema."""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        rol = self.combo_rol.currentText()

        if not username or not password:
            QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
            return

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (username, password, rol)
                VALUES (?, ?, ?)
            """, (username, password, rol))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Usuario agregado correctamente.")
            self.input_username.clear()
            self.input_password.clear()
            self.combo_rol.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar usuario: {e}")
            logger.error(f"Error al agregar usuario: {e}")
        finally:
            conexion.close()
            self.cargar_usuarios()


    def editar_usuario(self, registro):
        """
        Editar un usuario existente.
        :param registro: Registro completo del usuario (id_usuario, username, rol)
        """
        id_usuario, username, rol = registro

        # Solicitar nuevo nombre de usuario
        nuevo_username, ok = QInputDialog.getText(self, "Editar Usuario", 
                                                "Nuevo Nombre de Usuario:", 
                                                text=username)
        if not ok or not nuevo_username.strip():
            QMessageBox.warning(self, "Edición Cancelada", "No se realizaron cambios.")
            return

        # Solicitar nuevo rol
        nuevo_rol, ok = QInputDialog.getItem(self, "Editar Rol", 
                                            "Nuevo Rol:", 
                                            ["SysAdmin", "Administrador", "Cajero", "Consultor"], 
                                            editable=False)
        if not ok:
            QMessageBox.warning(self, "Edición Cancelada", "No se realizaron cambios.")
            return

        # Actualizar en la base de datos
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET username = ?, rol = ?
                WHERE id_usuario = ?
            """, (nuevo_username.strip(), nuevo_rol, id_usuario))
            conexion.commit()
            conexion.close()

            # Recargar la tabla de usuarios
            self.cargar_usuarios()
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar el usuario: {e}")


    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario del sistema."""
        confirmacion = QMessageBox.question(self, "Eliminar Usuario", "¿Está seguro de eliminar este usuario?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.No:
            return

        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar usuario: {e}")
            logger.error(f"Error al eliminar usuario: {e}")
        finally:
            conexion.close()
            self.cargar_usuarios()
