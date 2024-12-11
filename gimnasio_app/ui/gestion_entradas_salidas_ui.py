from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
    QMessageBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from database.database import conectar

class GestionEntradasSalidas(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Entradas y Salidas")
        self.setFixedSize(800, 600)

        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #2C3E50;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #ECF0F1;
                border: 1px solid #34495E;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                color: #2C3E50;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #1ABC9C;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
                padding: 6px;
            }
            QTableWidget {
                background-color: #ECF0F1;
                border: none;
                font-size: 12px;
                color: #2C3E50;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout()

        # Formulario
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Tipo de Movimiento:"))
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["ENTRADA", "SALIDA"])
        form_layout.addWidget(self.tipo_combo)

        form_layout.addWidget(QLabel("Monto:"))
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("Monto")
        form_layout.addWidget(self.input_monto)

        form_layout.addWidget(QLabel("Descripción:"))
        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Descripción")
        form_layout.addWidget(self.input_descripcion)

        # Botones
        botones_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.registrar_movimiento)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.close)
        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_cancelar)
        form_layout.addLayout(botones_layout)

        main_layout.addLayout(form_layout)

        # Tabla para mostrar movimientos
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Tipo", "Monto", "Descripción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Cargar movimientos existentes
        self.cargar_movimientos()

    def registrar_movimiento(self):
        """Registra un nuevo movimiento en la base de datos."""
        tipo = self.tipo_combo.currentText()
        monto = self.input_monto.text()
        descripcion = self.input_descripcion.text()

        if not monto or not descripcion:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        try:
            monto = float(monto)
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO entradas_salidas (tipo_movimiento, monto, descripcion)
                VALUES (?, ?, ?)
            """, (tipo, monto, descripcion))
            conexion.commit()
            conexion.close()

            QMessageBox.information(self, "Éxito", f"Movimiento {tipo} registrado correctamente.")
            self.limpiar_formulario()
            self.cargar_movimientos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el movimiento: {e}")

    def cargar_movimientos(self):
        """Carga los movimientos registrados en la tabla."""
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT tipo_movimiento, monto, descripcion
                FROM entradas_salidas
                ORDER BY id_movimiento DESC
            """)
            movimientos = cursor.fetchall()
            conexion.close()

            self.table.setRowCount(0)  # Limpiar la tabla
            for row, movimiento in enumerate(movimientos):
                self.table.insertRow(row)
                for col, data in enumerate(movimiento):
                    self.table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los movimientos: {e}")

    def limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.input_monto.clear()
        self.input_descripcion.clear()
        self.tipo_combo.setCurrentIndex(0)
