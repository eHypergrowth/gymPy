from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QDateEdit, QGridLayout, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from logger_config import logger
from database.database import conectar

class GestionContratos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Contratos")
        self.setGeometry(100, 100, 1100, 700)
        logger.info("Inicializando la ventana de Gestión de Contratos")

        # Configurar la interfaz
        self.configurar_interfaz()

        # Conectar botones
        self.btn_agregar.clicked.connect(self.agregar_contrato)
        self.btn_eliminar.clicked.connect(self.eliminar_contrato)

        # Cargar datos iniciales
        self.cargar_clientes_y_planes()
        self.cargar_contratos()

    def configurar_interfaz(self):
        """Configura el diseño y la interfaz gráfica."""
        # Layout principal
        layout_principal = QVBoxLayout()

        # Tabla para mostrar contratos
        self.tabla_contratos = QTableWidget()
        self.tabla_contratos.setColumnCount(6)
        self.tabla_contratos.setHorizontalHeaderLabels(["ID", "Cliente", "Plan", "Fecha Inicio", "Fecha Fin", "Estado"])
        self.tabla_contratos.setAlternatingRowColors(True)
        self.tabla_contratos.setStyleSheet(
            """
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #BDC3C7;
                font-size: 14px;
                color: #2C3E50;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #1ABC9C;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #34495E;
                color: white;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            """
        )
        layout_principal.addWidget(self.tabla_contratos)

        # Contenedor del formulario
        contenedor_formulario = QWidget()
        layout_formulario = QGridLayout()

        self.label_cliente = QLabel("Cliente:")
        self.label_cliente.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_cliente = QComboBox()
        self.input_cliente.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout_formulario.addWidget(self.label_cliente, 0, 0)
        layout_formulario.addWidget(self.input_cliente, 0, 1)

        self.label_plan = QLabel("Plan:")
        self.label_plan.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_plan = QComboBox()
        self.input_plan.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout_formulario.addWidget(self.label_plan, 1, 0)
        layout_formulario.addWidget(self.input_plan, 1, 1)

        self.label_fecha_inicio = QLabel("Fecha de Inicio:")
        self.label_fecha_inicio.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_fecha_inicio = QDateEdit()
        self.input_fecha_inicio.setCalendarPopup(True)
        self.input_fecha_inicio.setDate(QDate.currentDate())
        self.input_fecha_inicio.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF;
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout_formulario.addWidget(self.label_fecha_inicio, 2, 0)
        layout_formulario.addWidget(self.input_fecha_inicio, 2, 1)

        self.label_fecha_fin = QLabel("Fecha de Fin:")
        self.label_fecha_fin.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_fecha_fin = QDateEdit()
        self.input_fecha_fin.setCalendarPopup(True)
        self.input_fecha_fin.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF;
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        layout_formulario.addWidget(self.label_fecha_fin, 3, 0)
        layout_formulario.addWidget(self.input_fecha_fin, 3, 1)

        self.label_estado = QLabel("Estado:")
        self.label_estado.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_estado = QComboBox()
        self.input_estado.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        self.input_estado.addItems(["Activo", "Vencido", "Cancelado"])
        layout_formulario.addWidget(self.label_estado, 4, 0)
        layout_formulario.addWidget(self.input_estado, 4, 1)

        contenedor_formulario.setLayout(layout_formulario)
        layout_principal.addWidget(contenedor_formulario)

        # Botones para agregar y eliminar contratos
        layout_botones = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Contrato")
        self.btn_agregar.setStyleSheet(
            """
            QPushButton {
                background-color: #1ABC9C;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            """
        )
        self.btn_eliminar = QPushButton("Eliminar Contrato")
        self.btn_eliminar.setStyleSheet(
            """
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            """
        )
        layout_botones.addWidget(self.btn_agregar)
        layout_botones.addWidget(self.btn_eliminar)
        layout_principal.addLayout(layout_botones)

        # Establecer el layout principal
        self.setLayout(layout_principal)

    def cargar_clientes_y_planes(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_cliente, nombre || ' ' || apellido FROM clientes")
            clientes = cursor.fetchall()
            self.input_cliente.clear()
            for cliente in clientes:
                self.input_cliente.addItem(cliente[1], cliente[0])

            cursor.execute("SELECT id_plan, nombre_plan FROM planes")
            planes = cursor.fetchall()
            self.input_plan.clear()
            for plan in planes:
                self.input_plan.addItem(plan[1], plan[0])

            conexion.close()
        except Exception as e:
            logger.error(f"Error al cargar clientes y planes: {e}")

    def cargar_contratos(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT c.id_contrato, cl.nombre || ' ' || cl.apellido, p.nombre_plan, 
                       c.fecha_inicio, c.fecha_fin, c.estado
                FROM contratos c
                JOIN clientes cl ON c.id_cliente = cl.id_cliente
                JOIN planes p ON c.id_plan = p.id_plan
                """
            )
            contratos = cursor.fetchall()
            self.tabla_contratos.setRowCount(len(contratos))
            for row, contrato in enumerate(contratos):
                for col, data in enumerate(contrato):
                    self.tabla_contratos.setItem(row, col, QTableWidgetItem(str(data)))
            conexion.close()
        except Exception as e:
            logger.error(f"Error al cargar contratos: {e}")

    def agregar_contrato(self):
        """Agrega un contrato nuevo."""
        try:
            id_cliente = self.input_cliente.currentData()
            id_plan = self.input_plan.currentData()
            fecha_inicio = self.input_fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.input_fecha_fin.date().toString("yyyy-MM-dd")
            estado = self.input_estado.currentText()

            if not id_cliente or not id_plan:
                QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")
                return

            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO contratos (id_cliente, id_plan, fecha_inicio, fecha_fin, monto_total, estado)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (id_cliente, id_plan, fecha_inicio, fecha_fin, estado),
            )
            conexion.commit()
            conexion.close()

            logger.info(f"Contrato agregado: Cliente={id_cliente}, Plan={id_plan}")
            QMessageBox.information(self, "Éxito", "Contrato agregado correctamente.")
            self.cargar_contratos()
        except Exception as e:
            logger.error(f"Error al agregar contrato: {e}")
            QMessageBox.critical(self, "Error", f"Error al agregar contrato: {e}")

    def eliminar_contrato(self):
        """Elimina el contrato seleccionado."""
        fila_seleccionada = self.tabla_contratos.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Advertencia", "Selecciona un contrato para eliminar.")
            return

        id_contrato = self.tabla_contratos.item(fila_seleccionada, 0).text()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM contratos WHERE id_contrato = ?", (id_contrato,))
            conexion.commit()
            conexion.close()

            logger.info(f"Contrato eliminado: ID={id_contrato}")
            QMessageBox.information(self, "Éxito", "Contrato eliminado correctamente.")
            self.cargar_contratos()
        except Exception as e:
            logger.error(f"Error al eliminar contrato ID={id_contrato}: {e}")
            QMessageBox.critical(self, "Error", f"Error al eliminar contrato: {e}")
