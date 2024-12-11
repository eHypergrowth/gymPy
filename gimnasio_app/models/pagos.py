import database

def listar_pagos():
    """Retorna todos los pagos."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_pago, id_cliente, monto, fecha_pago FROM pagos")
    registros = cursor.fetchall()
    conexion.close()
    return registros

def registrar_pago(id_cliente, monto, fecha_pago):
    """Registra un nuevo pago."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO pagos (id_cliente, monto, fecha_pago) 
        VALUES (?, ?, ?)
    """, (id_cliente, monto, fecha_pago))
    conexion.commit()
    conexion.close()
