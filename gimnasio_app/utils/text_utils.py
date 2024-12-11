# utils/text_utils.py

from PyQt5.QtWidgets import QLineEdit

class TextUtils:
    @staticmethod
    def forzar_mayusculas(input_field: QLineEdit):
        """
        Convierte automáticamente el texto ingresado en un QLineEdit a mayúsculas.
        
        Args:
            input_field (QLineEdit): Campo de texto a modificar.
        """
        input_field.textChanged.connect(lambda texto: TextUtils._convertir_a_mayusculas(input_field, texto))
    
    @staticmethod
    def _convertir_a_mayusculas(input_field: QLineEdit, texto: str):
        """
        Función interna para actualizar el texto del QLineEdit a mayúsculas.
        
        Args:
            input_field (QLineEdit): Campo de texto a modificar.
            texto (str): Texto ingresado.
        """
        input_field.blockSignals(True)  # Evitar bucles infinitos
        input_field.setText(texto.upper())
        input_field.blockSignals(False)  # Restaurar señales
