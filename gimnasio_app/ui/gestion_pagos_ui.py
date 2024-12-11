import os
import webbrowser  # Para abrir el PDF en el navegador
from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QMessageBox, QCompleter, QComboBox, QDateEdit, QHeaderView
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QStringListModel, QDate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from reportlab.lib.pagesizes import mm  # Usar milímetros para definir el tamaño del ticket
from reportlab.pdfgen import canvas
from database.database import conectar  # Importar desde la ruta correcta
from logger_config import logger  # Importar el logger configurado
import logging
from reportlab.lib.utils import ImageReader
import qrcode
from textwrap import wrap

from utils.text_utils import TextUtils

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

# Configurar el directorio de PDFs
PDF_DIR = "generated_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)  # Crear el directorio si no existe

class GestionPagos(QMainWindow):
    def __init__(self, usuario_actual=None):
        super().__init__()
        self.usuario_actual = usuario_actual  # Guarda el usuario actual para usarlo después
        logger.info("Usuario actual registrado en la sesión: %s", self.usuario_actual)

        self.setWindowTitle("Gestión de Pagos")
        self.setGeometry(100, 100, 1000, 600)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QTableWidget {
                background-color: #ECF0F1;
                border: none;
                font-size: 12px;
                color: #2C3E50;
            }
            QPushButton {
                background-color: #1ABC9C;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
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
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QDateEdit, QComboBox {
                border: 2px solid #34495E;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                background-color: #ECF0F1;
                color: #2C3E50;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 2px solid #1ABC9C;
            }
        """)

        layout = QVBoxLayout()

        # Formulario para el corte de caja
        corte_layout = QHBoxLayout()
        self.input_fecha_inicio = QDateEdit()
        self.input_fecha_inicio.setCalendarPopup(True)
        self.input_fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_inicio.setDate(QDate.currentDate())
        corte_layout.addWidget(self.input_fecha_inicio)

        self.input_fecha_fin = QDateEdit()
        self.input_fecha_fin.setCalendarPopup(True)
        self.input_fecha_fin.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha_fin.setDate(QDate.currentDate())
        corte_layout.addWidget(self.input_fecha_fin)

        btn_generar_corte = QPushButton("Generar Corte de Caja")
        btn_generar_corte.clicked.connect(self.generar_corte_caja)
        corte_layout.addWidget(btn_generar_corte)
        layout.addLayout(corte_layout)

        # Tabla para mostrar pagos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID-Pago", "Cliente", "Monto", "Fecha-Pago", "Fecha Fin", "Descargar Ticket"])
        layout.addWidget(self.table)
        # Ajustar automáticamente el tamaño de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        logger.info("Mostrando Tabla de pagos")

        # Campo con autocompletado para seleccionar cliente
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Buscar cliente por nombre o apellido")
        TextUtils.forzar_mayusculas(self.input_cliente)  # Aplicar utilidad
        layout.addWidget(self.input_cliente)
        logger.info("Búsqueda Cliente: %s", self.input_cliente.text())

        # Configurar autocompletado
        self.completer = QCompleter()
        self.input_cliente.setCompleter(self.completer)
        self.configurar_autocompletado()

        # ComboBox para seleccionar planes
        self.combo_planes = QComboBox()
        self.combo_planes.addItems(self.obtener_planes())
        self.combo_planes.currentIndexChanged.connect(self.actualizar_monto)
        layout.addWidget(self.combo_planes)

        # Campo para mostrar el monto seleccionado
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("Monto")
        self.input_monto.setReadOnly(True)
        layout.addWidget(self.input_monto)

        # Campo de fecha con calendario gráfico
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")
        self.input_fecha.setDate(QDate.currentDate())
        layout.addWidget(self.input_fecha)

        btn_agregar = QPushButton("Registrar Pago")
        btn_agregar.clicked.connect(self.agregar_pago)
        layout.addWidget(btn_agregar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.cargar_pagos()

    #cargar_pagos
    def cargar_pagos(self):
        """Carga todos los pagos en la tabla."""
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT 
                    pagos.id_pago AS id_pago,
                    clientes.nombre || ' ' || clientes.apellido AS nombre_cliente,
                    pagos.monto AS monto,
                    pagos.fecha_pago AS fecha_pago,
                    planes.duracion_meses AS duracion_meses
                FROM pagos
                INNER JOIN clientes ON pagos.id_cliente = clientes.id_cliente
                INNER JOIN planes ON pagos.id_plan = planes.id_plan
            """)
            registros = cursor.fetchall()
            logger.info("Pagos cargados: %s", registros)  # Log para ver los datos cargados
            conexion.close()

            self.table.setRowCount(0)

            for row, registro in enumerate(registros):
                id_pago, nombre_cliente, monto, fecha_pago, duracion_meses = registro

                fecha_pago_dt = datetime.strptime(fecha_pago, "%Y-%m-%d")
                fecha_fin_dt = fecha_pago_dt + relativedelta(months=duracion_meses)

                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(id_pago)))
                self.table.setItem(row, 1, QTableWidgetItem(nombre_cliente))
                self.table.setItem(row, 2, QTableWidgetItem(str(monto)))
                self.table.setItem(row, 3, QTableWidgetItem(fecha_pago))
                self.table.setItem(row, 4, QTableWidgetItem(fecha_fin_dt.strftime("%Y-%m-%d")))

                btn_descargar = QPushButton("Imprimir Ticket")
                btn_descargar.setStyleSheet("""
                    QPushButton {
                        background-color: #1ABC9C;
                        color: white;
                        border: 1px solid #16A085;
                        border-radius: 10px;
                        padding: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #16A085;
                    }
                    QPushButton:pressed {
                        background-color: #1ABC9C;
                        padding: 4px;
                    }
                """)
                btn_descargar.clicked.connect(lambda _, p=id_pago, c=nombre_cliente, m=monto, f=fecha_pago: self.abrir_ticket(p, c, m, f))
                self.table.setCellWidget(row, 5, btn_descargar)
        except Exception as e:
            logger.error(f"Error al cargar pagos: {e}")


    #abrir_ticket
    def abrir_ticket(self, id_pago, cliente, monto, fecha_pago):
        """Genera un ticket en PDF con información adicional del gimnasio."""
        try:
            # Tamaño estándar para ticket: 80 mm x altura dinámica
            ticket_width = 80 * mm
            ticket_height = 220 * mm

            nombre_archivo = os.path.join(PDF_DIR, f"ticket_pago_{id_pago}.pdf")

            # Consultar información del gimnasio desde la base de datos
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT clave, valor FROM configuraciones WHERE clave IN ('nombre_sistema', 'logo_sistema', 'ubicacion_gym', 'web_gym', 'whatsapp_gym')")
            configuraciones = {row[0]: row[1] for row in cursor.fetchall()}

            # Obtener el usuario que procesó el pago
            cursor.execute("""
                SELECT usuarios.username
                FROM pagos
                INNER JOIN usuarios ON pagos.id_usuario = usuarios.id_usuario
                WHERE pagos.id_pago = ?
            """, (id_pago,))
            usuario = cursor.fetchone()[0]  # Obtener el nombre de usuario

            cursor.close()
            conexion.close()

            # Generar QR
            qr_data = f"https://wa.me/{configuraciones['whatsapp_gym']}?text=Hola,%20soy%20{cliente}%20y%20generé%20un%20pago%20el%20{fecha_pago}%20con%20el%20monto%20de%20${monto}.%20Solicito%20una%20factura."
            qr = qrcode.make(qr_data)
            qr_path = os.path.join(PDF_DIR, f"qr_ticket_{id_pago}.png")
            qr.save(qr_path)

            # Crear el PDF
            c = canvas.Canvas(nombre_archivo, pagesize=(ticket_width, ticket_height))
            margen_lateral = 8 * mm  # Ajustar margen lateral
            y = ticket_height - 10 * mm  # Espacio inicial desde arriba
            line_height = 8 * mm

            # Agregar logo
            logo_path = configuraciones["logo_sistema"]
            if os.path.exists(logo_path):
                logo = ImageReader(logo_path)
                c.drawImage(logo, margen_lateral, y - 15 * mm, width=20 * mm, height=20 * mm, preserveAspectRatio=True, mask='auto')
            y -= 25 * mm

            # Agregar información del gimnasio
            c.setFont("Helvetica-Bold", 10)
            c.drawString(ticket_width / 2 - (len(configuraciones["nombre_sistema"]) * 2), y, configuraciones["nombre_sistema"])
            y -= line_height
            c.setFont("Helvetica", 8)

            # Manejar texto largo con salto de línea
            ubicacion_wrapped = wrap(configuraciones["ubicacion_gym"], width=40)  # 40 caracteres por línea
            for line in ubicacion_wrapped:
                c.drawString(margen_lateral, y, line)
                y -= line_height
            y -= line_height  # Espaciado adicional después de la ubicación

            # Información del ticket
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margen_lateral, y, "Ticket de Pago")
            y -= line_height
            c.setFont("Helvetica", 8)
            c.drawString(margen_lateral, y, f"ID-Pago: {id_pago}")
            y -= line_height
            c.drawString(margen_lateral, y, f"Cliente: {cliente}")
            y -= line_height
            c.drawString(margen_lateral, y, f"Monto: ${monto:.2f}")
            y -= line_height
            c.drawString(margen_lateral, y, f"Fecha de Pago: {fecha_pago}")
            y -= 2 * line_height
            c.drawString(margen_lateral, y, f"Procesado por: {usuario}")  # Agregar el usuario
            y -= line_height


            # Mensaje de agradecimiento
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(margen_lateral, y, "¡Gracias por su pago!")
            y -= 3 * line_height

            # Pie de página
            c.setFont("Helvetica", 8)
            direccion_wrapped = wrap(configuraciones["ubicacion_gym"], width=40)
            for line in direccion_wrapped:
                c.drawString(margen_lateral, y, f"Dirección: {line}")
                y -= line_height
            c.drawString(margen_lateral, y, f"Web: {configuraciones['web_gym']}")
            y -= line_height

            # Agregar QR
            c.drawImage(qr_path, ticket_width / 2 - 15 * mm, y - 25 * mm, width=30 * mm, height=30 * mm, preserveAspectRatio=True, mask='auto')
            c.save()

            # Abrir el archivo PDF
            webbrowser.open(nombre_archivo)
            QMessageBox.information(self, "Ticket Generado", f"El ticket se ha abierto en el navegador.")
            logger.info("Ticket generado para el pago: %s", id_pago)
        except Exception as e:
            logger.error(f"Error al generar ticket: {e}")
            QMessageBox.critical(self, "Error", "No se pudo generar el ticket.")


    #generar_corte_cja
    def generar_corte_caja(self):
        """Genera un corte de caja en PDF considerando pagos, entradas y salidas."""
        try:
            fecha_inicio = self.input_fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.input_fecha_fin.date().toString("yyyy-MM-dd")
            usuario_actual = "Admin"  # Cambia esto según el sistema de autenticación

            conexion = conectar()
            cursor = conexion.cursor()

            # Consultar pagos
            cursor.execute("""
                SELECT pagos.id_pago, clientes.nombre || ' ' || clientes.apellido, pagos.monto, pagos.fecha_pago
                FROM pagos
                INNER JOIN clientes ON pagos.id_cliente = clientes.id_cliente
                WHERE pagos.fecha_pago BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            registros_pagos = cursor.fetchall()
            logger.info(f"Pagos obtenidos: {registros_pagos}")

            # Consultar entradas y salidas
            # Consulta corregida para movimientos
            cursor.execute("""
                SELECT tipo_movimiento, monto, descripcion, fecha_movimiento
                FROM entradas_salidas
                WHERE date(fecha_movimiento) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            registros_movimientos = cursor.fetchall()
            logger.info(f"Movimientos obtenidos: {registros_movimientos}")

            cursor.execute("SELECT clave, valor FROM configuraciones WHERE clave IN ('nombre_sistema', 'logo_sistema', 'ubicacion_gym', 'web_gym', 'whatsapp_gym')")
            configuraciones = {row[0]: row[1] for row in cursor.fetchall()}
            conexion.close()

            if not registros_pagos and not registros_movimientos:
                logger.warning("No se encontraron registros en el rango de fechas especificado.")
                QMessageBox.warning(self, "Sin datos", "No se encontraron registros en el rango de fechas especificado.")
                return

            # Generar QR para el corte
            qr_data = f"Corte de caja generado por {usuario_actual} del {fecha_inicio} al {fecha_fin}."
            qr = qrcode.make(qr_data)
            qr_path = os.path.join(PDF_DIR, f"qr_corte_{fecha_inicio}_a_{fecha_fin}.png")
            qr.save(qr_path)

            # Crear el PDF
            ticket_width = 80 * mm
            ticket_height = 200 * mm + (len(registros_pagos) + len(registros_movimientos)) * 10 * mm  # Ajustar altura dinámica
            nombre_archivo = os.path.join(PDF_DIR, f"corte_caja_{fecha_inicio}_a_{fecha_fin}.pdf")
            c = canvas.Canvas(nombre_archivo, pagesize=(ticket_width, ticket_height))

            margen_lateral = 8 * mm
            y = ticket_height - 10 * mm
            line_height = 8 * mm

            # Cabecera
            logo_path = configuraciones["logo_sistema"]
            if os.path.exists(logo_path):
                logo = ImageReader(logo_path)
                c.drawImage(logo, margen_lateral, y - 15 * mm, width=20 * mm, height=20 * mm, preserveAspectRatio=True, mask='auto')
            y -= 25 * mm

            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(ticket_width / 2, y, configuraciones["nombre_sistema"])
            y -= line_height

            c.setFont("Helvetica", 8)
            ubicacion_wrapped = wrap(configuraciones["ubicacion_gym"], width=40)
            for line in ubicacion_wrapped:
                c.drawCentredString(ticket_width / 2, y, line)
                y -= line_height
            y -= line_height  # Espaciado adicional después de la ubicación

            # Detalles de pagos
            c.setFont("Helvetica-Bold", 8)
            c.drawString(margen_lateral, y, "Pagos:")
            y -= line_height

            total_pagos = 0
            for id_pago, cliente, monto, fecha_pago in registros_pagos:
                c.drawString(margen_lateral, y, f"ID: {id_pago} Cliente: {cliente}")
                y -= line_height
                c.drawString(margen_lateral, y, f"Fecha: {fecha_pago} Monto: ${monto:.2f}")
                y -= 2 * line_height
                total_pagos += monto

            c.setFont("Helvetica-Bold", 8)
            c.drawString(margen_lateral, y, f"Total Pagos: ${total_pagos:.2f}")
            y -= 2 * line_height

            # Detalles de movimientos
            c.setFont("Helvetica-Bold", 8)
            c.drawString(margen_lateral, y, "Movimientos:")
            y -= line_height

            total_entradas = 0
            total_salidas = 0 
            
            for tipo, monto, descripcion, fecha in registros_movimientos:
                c.drawString(margen_lateral, y, f"{tipo}: ${monto:.2f} ({descripcion})")
                y -= line_height
                if tipo == "ENTRADA":
                    total_entradas += monto
                elif tipo == "SALIDA":
                    total_salidas += monto

            c.drawString(margen_lateral, y, f"Total Entradas: ${total_entradas:.2f}")
            y -= line_height
            c.drawString(margen_lateral, y, f"Total Salidas: ${total_salidas:.2f}")
            y -= 2 * line_height

            # Total general del corte
            total_general = total_pagos + total_entradas - total_salidas
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margen_lateral, y, f"Total General del Corte: ${total_general:.2f}")
            y -= 2 * line_height

            # Pie de página
            c.setFont("Helvetica", 8)
            direccion_wrapped = wrap(configuraciones["ubicacion_gym"], width=40)
            for line in direccion_wrapped:
                c.drawString(margen_lateral, y, f"Dirección: {line}")
                y -= line_height
            c.drawString(margen_lateral, y, f"Web: {configuraciones['web_gym']}")
            y -= line_height

            # Agregar QR
            c.drawImage(qr_path, ticket_width / 2 - 15 * mm, y - 25 * mm, width=30 * mm, height=30 * mm, preserveAspectRatio=True, mask='auto')
            c.save()

            c.drawString(margen_lateral, y, f"Web: {configuraciones['web_gym']}")
            y -= line_height

            webbrowser.open(nombre_archivo)
            QMessageBox.information(self, "Corte de Caja", "El corte de caja se ha generado correctamente.")
            logger.info("Corte de caja generado por %s: Desde %s Hasta %s", usuario_actual, fecha_inicio, fecha_fin)
        except Exception as e:
            logger.error(f"Error al generar el corte de caja: {e}")
            QMessageBox.critical(self, "Error", "No se pudo generar el corte de caja.")








    #agregar_pagos
    def agregar_pago(self):
        logger.info("Usuario actual registrado en la sesión: %s", self.usuario_actual)
        """Registra un nuevo pago."""
        cliente_nombre = self.input_cliente.text()
        monto = self.input_monto.text()
        fecha = self.input_fecha.date().toString("yyyy-MM-dd")
        plan_seleccionado = self.combo_planes.currentText().split(" - $")[0]

        if not cliente_nombre or not monto or not plan_seleccionado:
            QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
            return

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # Obtener ID del cliente
            cursor.execute("""
                SELECT id_cliente 
                FROM clientes 
                WHERE LOWER(nombre || ' ' || apellido) = LOWER(?)
            """, (cliente_nombre,))
            cliente_id = cursor.fetchone()
            if not cliente_id:
                QMessageBox.critical(self, "Error", "Cliente no encontrado.")
                conexion.close()
                return

            # Obtener ID del plan
            cursor.execute("SELECT id_plan FROM planes WHERE nombre_plan = ?", (plan_seleccionado,))
            plan_id = cursor.fetchone()
            if not plan_id:
                QMessageBox.critical(self, "Error", "Plan no encontrado.")
                conexion.close()
                return

            # Obtener ID del usuario autenticado
            cursor.execute("SELECT id_usuario FROM usuarios WHERE LOWER(TRIM(username)) = LOWER(TRIM(?))", (self.usuario_actual,))
            usuario_id = cursor.fetchone()
            if not usuario_id:
                QMessageBox.critical(self, "Error", "Usuario no encontrado.")
                conexion.close()
                return

            # Insertar pago
            cursor.execute("""
                INSERT INTO pagos (id_cliente, monto, fecha_pago, id_plan, id_usuario)
                VALUES (?, ?, ?, ?, ?)
            """, (cliente_id[0], monto, fecha, plan_id[0], usuario_id[0]))
            conexion.commit()
            logger.info("Pago registrado: Cliente %s, Plan %s, Monto %s, Usuario %s",
                        cliente_nombre, plan_seleccionado, monto, self.usuario_actual)
            conexion.close()

            self.cargar_pagos()
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente.")
        except Exception as e:
            logger.error(f"Error al registrar pago: {e}")
            QMessageBox.critical(self, "Error", "No se pudo registrar el pago.")



    def configurar_autocompletado(self):
        self.input_cliente.textChanged.connect(self.actualizar_autocompletado)

    def actualizar_autocompletado(self):
        texto_busqueda = self.input_cliente.text()
        nombres = self.obtener_nombres_clientes(texto_busqueda)
        model = QStringListModel()
        model.setStringList(nombres)
        self.completer.setModel(model)

    #obtener_planes
    def obtener_planes(self):
        """Obtiene todos los planes disponibles como lista de cadenas."""
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre_plan || ' - $' || printf('%.2f', costo) FROM planes")
            planes = [row[0] for row in cursor.fetchall()]
            logger.info("Planes obtenidos: %s", planes)
            conexion.close()
            # Agregar el placeholder "Selecciona el plan" al inicio
            return ["Selecciona el plan"] + planes if planes else ["Selecciona el plan"]
        except Exception as e:
            logger.error(f"Error al obtener planes: {e}")
            return ["Selecciona el plan"]  # Retorna una lista con el placeholder en caso de error



    

    def obtener_nombres_clientes(self, texto_busqueda=""):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT nombre || ' ' || apellido AS nombre_completo 
                FROM clientes
                WHERE LOWER(nombre) LIKE LOWER(?) OR LOWER(apellido) LIKE LOWER(?)
            """, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))
            nombres = [row[0] for row in cursor.fetchall()]
            conexion.close()
            return nombres
        except Exception as e:
            logging.error(f"Error al obtener nombres de clientes: {e}")
            return []

    def actualizar_monto(self):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            # Obtener el nombre del plan seleccionado (sin el costo)
            plan_seleccionado = self.combo_planes.currentText().split(" - $")[0]
            cursor.execute("SELECT costo FROM planes WHERE nombre_plan = ?", (plan_seleccionado,))
            resultado = cursor.fetchone()
            conexion.close()
            # Actualizar el campo de monto si se encontró el plan
            if resultado:
                self.input_monto.setText(f"{resultado[0]:.2f}")
            else:
                self.input_monto.clear()
        except Exception as e:
            logging.error(f"Error al actualizar el monto: {e}")
            self.input_monto.clear()
