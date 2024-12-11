from database.database import conectar

def obtener_contratos():
    """Obtiene todos los contratos desde la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT contratos.id_contrato, clientes.nombre || ' ' || clientes.apellido AS cliente, 
               planes.nombre_plan, contratos.fecha_inicio, contratos.fecha_fin, contratos.monto_total, contratos.estado
        FROM contratos
        INNER JOIN clientes ON contratos.id_cliente = clientes.id_cliente
        INNER JOIN planes ON contratos.id_plan = planes.id_plan
    """)
    contratos = cursor.fetchall()
    conexion.close()
    return contratos

def registrar_contrato(id_cliente, id_plan, fecha_inicio, fecha_fin, monto_total):
    """Registra un nuevo contrato en la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO contratos (id_cliente, id_plan, fecha_inicio, fecha_fin, monto_total, estado)
        VALUES (?, ?, ?, ?, ?, 'Activo')
    """, (id_cliente, id_plan, fecha_inicio, fecha_fin, monto_total))
    conexion.commit()
    conexion.close()

def actualizar_estado_contrato(id_contrato, nuevo_estado):
    """Actualiza el estado de un contrato."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE contratos
        SET estado = ?
        WHERE id_contrato = ?
    """, (nuevo_estado, id_contrato))
    conexion.commit()
    conexion.close()
