import database.database as database

def listar_clientes():
    """Retorna todos los clientes."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_cliente, nombre, apellido, email, telefono FROM clientes")
    registros = cursor.fetchall()
    conexion.close()
    return registros

def agregar_cliente(nombre, apellido, email, telefono):
    """Agrega un cliente nuevo."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO clientes (nombre, apellido, email, telefono) 
        VALUES (?, ?, ?, ?)
    """, (nombre, apellido, email, telefono))
    conexion.commit()
    conexion.close()

def eliminar_cliente(id_cliente):
    """Elimina un cliente por ID."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
    conexion.commit()
    conexion.close()
