from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QWidget, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from database.database import conectar
from logger_config import logger


class ConfiguracionParametros(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración de Parámetros")
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
        """)

        # Layout principal
        layout = QVBoxLayout()

        # Tabla para mostrar configuraciones
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Clave", "Valor", "Descripción"])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)  # Habilitar edición con doble clic
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Ajustar columnas automáticamente
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Clave
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Descripción
        layout.addWidget(self.table)

        # Botón para guardar cambios
        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.clicked.connect(self.guardar_cambios)
        layout.addWidget(btn_guardar)

        # Configurar el contenedor principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Cargar configuraciones al iniciar
        self.cargar_configuraciones()

    def cargar_configuraciones(self):
        """Carga los parámetros desde la base de datos en la tabla."""
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT clave, valor, descripcion FROM configuraciones")
        configuraciones = cursor.fetchall()
        conexion.close()

        self.table.setRowCount(0)
        for row, config in enumerate(configuraciones):
            self.table.insertRow(row)
            for col, data in enumerate(config):
                item = QTableWidgetItem(str(data))
                if col == 0:  # La clave no debe ser editable
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

    def guardar_cambios(self):
        """Guarda los cambios realizados en los valores de configuración."""
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            for row in range(self.table.rowCount()):
                clave = self.table.item(row, 0).text()
                valor = self.table.item(row, 1).text()
                cursor.execute("UPDATE configuraciones SET valor = ? WHERE clave = ?", (valor, clave))
            conexion.commit()
            conexion.close()
            QMessageBox.information(self, "Éxito", "Los parámetros se han actualizado correctamente.")
            logger.info("Parámetros actualizados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron actualizar los parámetros: {e}")
            logger.error(f"Error al actualizar parámetros: {e}")
