from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout,
    QWidget, QLineEdit, QLabel, QMessageBox, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt
from database.database import conectar
from logger_config import logger  # Importar el logger configurado
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GestionPlanes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Planes")
        self.setGeometry(100, 100, 800, 600)

        # Estilo moderno
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QTableWidget {
                background-color: #ECF0F1;
                color: #2C3E50;
                border: 1px solid #34495E;
                border-radius: 5px;
                gridline-color: #BDC3C7;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #1ABC9C;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
                padding: 8px;
            }
            QLineEdit {
                border: 2px solid #1ABC9C;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                background-color: #ECF0F1;
                color: #2C3E50;
                margin: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
                margin: 5px 0;
            }
        """)

        layout = QVBoxLayout()

        # Bandera para evitar eventos cíclicos
        self.eventos_habilitados = True

        # Tabla para mostrar planes
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Ahora incluye 'Duración'
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Duración (meses)", "Costo"])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)  # Habilitar edición con doble clic
        self.table.itemChanged.connect(self.actualizar_plan)  # Conectar el evento de edición
        layout.addWidget(self.table)
        
        # Ajustar automáticamente el tamaño de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Ajustar "ID" al contenido
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Ajustar "Nombre" proporcionalmente
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Ajustar "Duración (meses)" al contenido
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Ajustar "Costo" al contenido

        logger.info("Mostrando Tabla de planes")

        # Formulario para agregar planes
        form_layout = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del Plan")
        form_layout.addWidget(self.input_nombre)

        self.input_duracion = QLineEdit()
        self.input_duracion.setPlaceholderText("Duración (en meses)")
        form_layout.addWidget(self.input_duracion)

        self.input_costo = QLineEdit()
        self.input_costo.setPlaceholderText("Costo")
        form_layout.addWidget(self.input_costo)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar Plan")
        btn_agregar.clicked.connect(self.agregar_plan)
        button_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar Plan")
        btn_eliminar.clicked.connect(self.eliminar_plan)
        button_layout.addWidget(btn_eliminar)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.cargar_planes()

    def cargar_planes(self):
        """Carga todos los planes desde la base de datos en la tabla."""
        try:
            self.eventos_habilitados = False  # Deshabilitar eventos para evitar ciclos
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_plan, nombre_plan, duracion_meses, costo FROM planes")
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
            self.eventos_habilitados = True  # Habilitar eventos nuevamente
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar planes: {str(e)}")

    def agregar_plan(self):
        """Agrega un nuevo plan a la base de datos."""
        nombre = self.input_nombre.text()
        duracion = self.input_duracion.text()
        costo = self.input_costo.text()

        if not nombre or not duracion or not costo:
            QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
            return

        try:
            duracion = int(duracion)
            costo = float(costo)
        except ValueError:
            QMessageBox.critical(self, "Error", "Duración debe ser un número entero y Costo debe ser un número.")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO planes (nombre_plan, duracion_meses, costo) 
                VALUES (?, ?, ?)
            """, (nombre, duracion, costo))
            conexion.commit()
            conexion.close()

            self.cargar_planes()
            QMessageBox.information(self, "Éxito", "Plan agregado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar plan: {str(e)}")

    def eliminar_plan(self):
        """Elimina un plan seleccionado de la tabla."""
        seleccion = self.table.currentRow()
        if seleccion == -1:
            QMessageBox.critical(self, "Error", "Selecciona un plan para eliminar.")
            return

        plan_id = self.table.item(seleccion, 0).text()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM planes WHERE id_plan = ?", (plan_id,))
            conexion.commit()
            conexion.close()

            self.cargar_planes()
            QMessageBox.information(self, "Éxito", "Plan eliminado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar plan: {str(e)}")

    def actualizar_plan(self, item):
        """Actualizar plan cuando se edita una celda."""
        if not self.eventos_habilitados:
            return

        fila = item.row()
        columna = item.column()

        plan_id = self.table.item(fila, 0).text()  # Obtener el ID del plan
        nuevo_valor = item.text()  # Obtener el nuevo valor editado
        columnas_db = ["id_plan", "nombre_plan", "duracion_meses", "costo"]
        columna_db = columnas_db[columna]

        if columna == 0:  # Si se intenta editar el ID, revertir el cambio
            QMessageBox.warning(self, "Error", "No se puede editar el ID del plan.")
            self.cargar_planes()  # Revertir cambios
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(f"UPDATE planes SET {columna_db} = ? WHERE id_plan = ?", (nuevo_valor, plan_id))
            conexion.commit()
            conexion.close()
            QMessageBox.information(self, "Éxito", "Plan actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el plan: {str(e)}")
            self.cargar_planes()  # Revertir cambios si ocurre un error
