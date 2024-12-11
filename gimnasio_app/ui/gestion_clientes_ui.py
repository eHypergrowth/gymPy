from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QLineEdit, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
from database.database import conectar
from database.database import obtener_configuracion
from logger_config import logger
from utils.email_utils import enviar_email


class UppercaseLineEdit(QLineEdit):
    """QLineEdit personalizado que convierte texto a mayúsculas automáticamente."""
    def keyPressEvent(self, event):
        if event.text().islower():
            event = event.__class__(event.type(), event.key(), event.modifiers(), event.text().upper())
        super().keyPressEvent(event)


class GestionClientes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
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
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #FFFFFF;
                color: #2C3E50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)

        layout = QVBoxLayout()

        # Bandera para evitar eventos cíclicos
        self.eventos_habilitados = True

        # Tabla para mostrar clientes
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Email", "Teléfono"])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)  # Habilitar edición con doble clic
        self.table.itemChanged.connect(self.actualizar_cliente)  # Conectar el evento de edición
        layout.addWidget(self.table)

        # Ajustar automáticamente el tamaño de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Ajustar todas las columnas proporcionalmente
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Ajustar "ID" al contenido
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Ajustar "Nombre" proporcionalmente
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Ajustar "Apellido" proporcionalmente
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Ajustar "Email" proporcionalmente
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Ajustar "Teléfono" al contenido

        logger.info("Mostrando Tabla Clientes Clientes...")

        # Formulario para agregar clientes
        self.input_nombre = UppercaseLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")
        layout.addWidget(self.input_nombre)

        self.input_apellido = UppercaseLineEdit()
        self.input_apellido.setPlaceholderText("Apellido")
        layout.addWidget(self.input_apellido)

        self.input_email = QLineEdit()  # Email sigue siendo normal
        self.input_email.setPlaceholderText("Email")
        layout.addWidget(self.input_email)

        self.input_telefono = UppercaseLineEdit()
        self.input_telefono.setPlaceholderText("Teléfono")
        layout.addWidget(self.input_telefono)

        btn_agregar = QPushButton("Agregar Cliente")
        btn_agregar.clicked.connect(self.agregar_cliente)
        layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar Cliente")
        btn_eliminar.clicked.connect(self.eliminar_cliente)
        layout.addWidget(btn_eliminar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.cargar_clientes()

    def cargar_clientes(self):
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_cliente, nombre, apellido, email, telefono FROM clientes")
        registros = cursor.fetchall()
        conexion.close()

        # Deshabilitar eventos para evitar ciclos
        self.eventos_habilitados = False

        self.table.setRowCount(0)
        for row, registro in enumerate(registros):
            self.table.insertRow(row)
            for col, data in enumerate(registro):
                item = QTableWidgetItem(str(data))
                if col == 0:  # Hacer que la columna ID no sea editable
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

        # Habilitar eventos nuevamente
        self.eventos_habilitados = True

    #agregar_cliente
    def agregar_cliente(self):
        nombre = self.input_nombre.text()
        apellido = self.input_apellido.text()
        email = self.input_email.text()
        telefono = self.input_telefono.text()

        if not nombre or not apellido or not email:
            QMessageBox.critical(self, "Error", "Nombre, apellido y email son obligatorios.")
            return

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre, apellido, email, telefono) 
            VALUES (?, ?, ?, ?)
        """, (nombre, apellido, email, telefono))
        conexion.commit()
        conexion.close()

        # Obtener número de WhatsApp desde la configuración
        whatsapp_gym = obtener_configuracion('whatsapp_gym')
        # Obtener nombre del gimnasio
        nameGym = obtener_configuracion('nombre_sistema')
        
        if not whatsapp_gym:
            logger.error("No se pudo obtener el número de WhatsApp del gimnasio.")
            QMessageBox.critical(self, "Error", "No se pudo enviar el correo porque falta la configuración de WhatsApp.")
            return
        if not nameGym:
            logger.error("No se pudo obtener el nombre del gimnasio.")
            QMessageBox.critical(self, "Error", "No se pudo enviar el correo porque falta el nombre del Gimnacio.")
            return

        # Enviar correo de bienvenida con enlace a WhatsApp
        asunto = f"Bienvenido a {nameGym}"
        mensaje_html = f"""
        <html>
            <body>
                <h1>¡Bienvenido, {nombre} {apellido}!</h1>
                <p>Gracias por registrarte en Atlas Gym.</p>
                <p>Estamos encantados de tenerte con nosotros.</p>
                <a href="https://wa.me/{whatsapp_gym}?text=Hola,%20soy%20{nombre}%20{apellido}%20y%20con%20esto%20valido%20mi%20registro%20y%20me%20gustaría%20obtener%20el%2010%%20de%20descuento%20que%20ofertan" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
                    Validar mi registro por WhatsApp y obten un 10% de descuento en tu proxima mensualidad
                </a>
            </body>
        </html>
        """
        enviar_email(email, asunto, mensaje_html)

        self.cargar_clientes()
        QMessageBox.information(self, "Éxito", "Cliente agregado correctamente.")
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_email.clear()
        self.input_telefono.clear()
    #fin_agregar_cliente


    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_email.clear()
        self.input_telefono.clear()

    def eliminar_cliente(self):
        seleccion = self.table.currentRow()
        if seleccion == -1:
            QMessageBox.critical(self, "Error", "Selecciona un cliente para eliminar.")
            return

        cliente_id = self.table.item(seleccion, 0).text()
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (cliente_id,))
        conexion.commit()
        conexion.close()

        self.cargar_clientes()
        QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente.")

    def actualizar_cliente(self, item):
        """Actualizar cliente cuando se edita una celda."""
        if not self.eventos_habilitados:
            return

        fila = item.row()
        columna = item.column()

        cliente_id = self.table.item(fila, 0).text()  # Obtener el ID del cliente
        nuevo_valor = item.text()  # Obtener el nuevo valor editado
        columnas_db = ["id_cliente", "nombre", "apellido", "email", "telefono"]
        columna_db = columnas_db[columna]

        if columna == 0:  # Si se intenta editar el ID, revertir el cambio
            self.eventos_habilitados = False
            QMessageBox.warning(self, "Error", "No se puede editar el ID del cliente.")
            self.cargar_clientes()  # Recargar la tabla para revertir el cambio
            self.eventos_habilitados = True
            return

        # Convertir a mayúsculas todos los valores excepto el correo
        if columna != 3:  # Columna de "Email" no se convierte
            nuevo_valor = nuevo_valor.upper()
            # Actualizar el texto en la tabla a mayúsculas
            self.eventos_habilitados = False  # Evitar ciclos de eventos
            item.setText(nuevo_valor)
            self.eventos_habilitados = True

        # Actualizar el cliente en la base de datos
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(f"UPDATE clientes SET {columna_db} = ? WHERE id_cliente = ?", (nuevo_valor, cliente_id))
            conexion.commit()
            conexion.close()
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el cliente: {e}")
            logger.error(f"Error al actualizar cliente: {e}")
            self.cargar_clientes()  # Revertir cambios si ocurre un error
