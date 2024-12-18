from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QDateEdit, QGridLayout, QMessageBox, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen
from logger_config import logger
from database.database import conectar
import os
import webbrowser
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class GestionContratos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Contratos")
        self.setGeometry(100, 100, 1100, 700)
        logger.info("Inicializando la ventana de Gestión de Contratos")

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

        # Configurar la interfaz
        self.configurar_interfaz()

        # Conectar botones
        self.btn_agregar.clicked.connect(self.abrir_captura_firma)
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
        layout_principal.addWidget(self.tabla_contratos)

        # Contenedor del formulario
        contenedor_formulario = QWidget()
        layout_formulario = QGridLayout()

        self.label_cliente = QLabel("Cliente:")
        self.input_cliente = QComboBox()
        layout_formulario.addWidget(self.label_cliente, 0, 0)
        layout_formulario.addWidget(self.input_cliente, 0, 1)

        self.label_plan = QLabel("Plan:")
        self.input_plan = QComboBox()
        layout_formulario.addWidget(self.label_plan, 1, 0)
        layout_formulario.addWidget(self.input_plan, 1, 1)

        self.label_fecha_inicio = QLabel("Fecha de Inicio:")
        self.input_fecha_inicio = QDateEdit()
        self.input_fecha_inicio.setCalendarPopup(True)
        self.input_fecha_inicio.setDate(QDate.currentDate())
        layout_formulario.addWidget(self.label_fecha_inicio, 2, 0)
        layout_formulario.addWidget(self.input_fecha_inicio, 2, 1)

        self.label_fecha_fin = QLabel("Fecha de Fin:")
        self.input_fecha_fin = QDateEdit()
        self.input_fecha_fin.setCalendarPopup(True)
        layout_formulario.addWidget(self.label_fecha_fin, 3, 0)
        layout_formulario.addWidget(self.input_fecha_fin, 3, 1)

        contenedor_formulario.setLayout(layout_formulario)
        layout_principal.addWidget(contenedor_formulario)

        # Botones para agregar y eliminar contratos
        layout_botones = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Contrato")
        self.btn_eliminar = QPushButton("Eliminar Contrato")
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

    def abrir_captura_firma(self):
        """Abre la ventana para capturar la firma digital."""
        try:
            ventana_firma = VentanaFirma(self)
            if ventana_firma.exec_() == QDialog.Accepted:
                ruta_firma = ventana_firma.ruta_firma
                self.generar_contrato(ruta_firma)
        except Exception as e:
            logger.error(f"Error al abrir la ventana de captura de firma: {e}")

    def generar_contrato(self, ruta_firma):
        """Genera un contrato en PDF con la firma digital."""
        try:
            id_cliente = self.input_cliente.currentData()
            id_plan = self.input_plan.currentData()
            fecha_inicio = self.input_fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.input_fecha_fin.date().toString("yyyy-MM-dd")

            if not id_cliente or not id_plan:
                QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")
                return

            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre || ' ' || apellido FROM clientes WHERE id_cliente = ?", (id_cliente,))
            cliente = cursor.fetchone()[0]

            cursor.execute("SELECT nombre_plan FROM planes WHERE id_plan = ?", (id_plan,))
            plan = cursor.fetchone()[0]
            conexion.close()

            nombre_archivo = f"generated_pdfs/contrato_{cliente.replace(' ', '_')}.pdf"
            c = canvas.Canvas(nombre_archivo, pagesize=letter)
            c.drawString(100, 750, f"Contrato de Servicios")
            c.drawString(100, 730, f"Cliente: {cliente}")
            c.drawString(100, 710, f"Plan: {plan}")
            c.drawString(100, 690, f"Fecha de Inicio: {fecha_inicio}")
            c.drawString(100, 670, f"Fecha de Fin: {fecha_fin}")

            if os.path.exists(ruta_firma):
                c.drawImage(ruta_firma, 100, 600, width=200, height=100)

            c.save()
            webbrowser.open(nombre_archivo)
            QMessageBox.information(self, "Contrato Generado", "El contrato se ha generado y abierto en el navegador.")
        except Exception as e:
            logger.error(f"Error al generar contrato: {e}")
            QMessageBox.critical(self, "Error", f"Error al generar contrato: {e}")

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

class VentanaFirma(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Captura de Firma")
        self.setGeometry(100, 100, 500, 400)
        self.ruta_firma = None
        self.dibujo = QPixmap(400, 200)
        self.dibujo.fill(Qt.white)

        # Configurar la interfaz
        self.configurar_interfaz()

    def configurar_interfaz(self):
        """Configura la interfaz gráfica de la ventana de captura de firma."""
        layout_principal = QVBoxLayout()

        self.area_dibujo = QWidget(self)
        self.area_dibujo.setFixedSize(400, 200)
        layout_principal.addWidget(self.area_dibujo, alignment=Qt.AlignCenter)

        layout_botones = QHBoxLayout()
        btn_guardar = QPushButton("Guardar Firma")
        btn_cancelar = QPushButton("Cancelar")
        layout_botones.addWidget(btn_guardar)
        layout_botones.addWidget(btn_cancelar)

        layout_principal.addLayout(layout_botones)
        btn_guardar.clicked.connect(self.guardar_firma)
        btn_cancelar.clicked.connect(self.reject)

        self.setLayout(layout_principal)

    def guardar_firma(self):
        """Guarda la firma como una imagen PNG."""
        ruta_imagen = "generated_pdfs/firma.png"
        self.dibujo.save(ruta_imagen)
        self.ruta_firma = ruta_imagen
        self.accept()
