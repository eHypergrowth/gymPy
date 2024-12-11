import database

def listar_planes():
    """Retorna todos los planes."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_plan, nombre_plan, costo FROM planes")
    registros = cursor.fetchall()
    conexion.close()
    return registros

def agregar_plan(nombre_plan, costo):
    """Agrega un nuevo plan."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO planes (nombre_plan, costo) 
        VALUES (?, ?)
    """, (nombre_plan, costo))
    conexion.commit()
    conexion.close()

def eliminar_plan(id_plan):
    """Elimina un plan por ID."""
    conexion = database.conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM planes WHERE id_plan = ?", (id_plan,))
    conexion.commit()
    conexion.close()
