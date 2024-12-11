import sqlite3

# Conectar a la base de datos
conexion = sqlite3.connect("database/gimnasio.db")

# Crear un cursor para ejecutar comandos SQL
cursor = conexion.cursor()

# Listar las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

# Mostrar las tablas
print("Tablas en la base de datos:")
for tabla in tablas:
    print(tabla[0])

# Cerrar la conexión
conexion.close()
