-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('SysAdmin','Administrador', 'Cajero', 'Consultor'))
);

-- Insertar un usuario por defecto
INSERT OR IGNORE INTO usuarios (username, password, rol) 
VALUES ('admin', 'admin123', 'Administrador');
INSERT OR IGNORE INTO usuarios (username, password, rol) 
VALUES ('sysadmin', 'sysadmin', 'SysAdmin');
INSERT OR IGNORE INTO usuarios (username, password, rol) 
VALUES ('cajero', 'cajero2370', 'Cajero');
INSERT OR IGNORE INTO usuarios (username, password, rol) 
VALUES ('entrenador', 'entre2370', 'Consultor');

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    fecha_nacimiento TEXT
);

-- Inserción inicial para un cliente demo en la tabla de Clientes
INSERT OR IGNORE INTO clientes (nombre, apellido, email, telefono, fecha_nacimiento)
VALUES 
('DEMO', 'CLIENTE', 'demo@cliente.com', '1234567890', '2000-01-01');


-- Tabla de Planes
CREATE TABLE IF NOT EXISTS planes (
    id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_plan TEXT NOT NULL,
    duracion_meses INTEGER NOT NULL,
    costo REAL NOT NULL
);

-- Inserciones iniciales para la tabla de Planes
INSERT OR IGNORE INTO planes (nombre_plan, duracion_meses, costo)
VALUES 
('MENSUAL', 1, 500);


-- Tabla de Pagos
CREATE TABLE IF NOT EXISTS pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_plan INTEGER NOT NULL,
    monto REAL NOT NULL,
    fecha_pago TEXT NOT NULL,
    id_usuario INTEGER NOT NULL, -- Relación con la tabla usuarios
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_plan) REFERENCES planes(id_plan)
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla de Rutinas
CREATE TABLE IF NOT EXISTS rutinas (
    id_rutina INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_plan INTEGER NOT NULL,
    series INTEGER NOT NULL,
    repeticiones INTEGER NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_plan) REFERENCES planes(id_plan)
);

-- Tabla de Categorías de Ejercicio
CREATE TABLE IF NOT EXISTS categorias_de_ejercicio (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_categoria TEXT NOT NULL
);

-- Tabla de Ejercicios
CREATE TABLE IF NOT EXISTS ejercicios (
    id_ejercicio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_ejercicio TEXT NOT NULL,
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categorias_de_ejercicio(id_categoria)
);

CREATE TABLE IF NOT EXISTS contratos (
    id_contrato INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_plan INTEGER NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    monto_total REAL NOT NULL,
    estado TEXT CHECK(estado IN ('Activo', 'Vencido', 'Cancelado')) DEFAULT 'Activo',
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_plan) REFERENCES planes(id_plan)
);


-- Tabla de Evaluaciones Físicas
CREATE TABLE IF NOT EXISTS evaluaciones_fisicas (
    id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    fecha_evaluacion TEXT NOT NULL,
    peso REAL NOT NULL,
    grasa_corporal REAL NOT NULL,
    masa_muscular REAL NOT NULL,
    notas TEXT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- Tabla de Horarios
CREATE TABLE IF NOT EXISTS horarios (
    id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    dia_semana TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- ConfigSystem
CREATE TABLE IF NOT EXISTS configuraciones (
    id_config INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT
);

-- Valores iniciales para ConfigSystem
INSERT OR IGNORE INTO configuraciones (clave, valor, descripcion) VALUES
('nombre_sistema', 'Atlas Gym', 'El nombre del sistema mostrado en la interfaz.'),
('logo_sistema','assets/icons/login_icon.jpg','Logo del Gimnasio'),
('web_gym','https://atlasgym.com','Web del Gimnasio'),
('ubicacion_gym','Av. Demo Direccion Hidalgo del Parral Chihuahua','Direccion del Gimnasio'),
('whatsapp_gym', '+526271131171', 'Número de WhatsApp del Gym para CTA en correos'),
('rfc_gym', 'RFCATLASGYM', 'Clave de Registro Federal de Contribuyentes'),
('moneda', 'MXN', 'Moneda predeterminada para operaciones.'),
('formato_fecha', 'YYYY-MM-DD', 'Formato de fecha usado en el sistema.'),
('smtp_server', 'smtp.gmail.com', 'Servidor SMTP para envío de correos'),
('smtp_port', '587', 'Puerto del servidor SMTP (TLS)'),
('smtp_email', 'altasgym2024@gmail.com', 'Correo utilizado para envío de correos'),
('smtp_password', 'lpfr udjk uulc cjha', 'Contraseña generada para la cuenta SMTP'),
('smtp_use_tls', '1', 'Usar TLS en la conexión (1=Sí, 0=No)'),
('smtp_use_ssl', '0', 'Usar SSL en la conexión (1=Sí, 0=No)');

CREATE TABLE IF NOT EXISTS entradas_salidas (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('ENTRADA', 'SALIDA')) NOT NULL,
    monto REAL NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_movimiento TEXT DEFAULT (datetime('now', 'localtime'))
);


