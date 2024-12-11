import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.database import conectar

def enviar_email(destinatario, asunto, mensaje_html):
    """Envía un correo electrónico utilizando la configuración de la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()

    # Obtener configuración SMTP desde la base de datos
    cursor.execute("""
        SELECT clave, valor 
        FROM configuraciones 
        WHERE clave LIKE 'smtp_%' OR clave = 'nombre_sistema'
    """)
    configuraciones = {fila[0]: fila[1] for fila in cursor.fetchall()}
    conexion.close()

    smtp_server = configuraciones.get("smtp_server")
    smtp_port = int(configuraciones.get("smtp_port"))
    smtp_email = configuraciones.get("smtp_email")
    smtp_password = configuraciones.get("smtp_password")
    smtp_use_tls = configuraciones.get("smtp_use_tls") == "1"
    smtp_use_ssl = configuraciones.get("smtp_use_ssl") == "1"

    # Personalizar el "From" con un nombre amigable
    nombre_sistema = configuraciones.get("nombre_sistema", "Sistema")
    from_email = f"{nombre_sistema} <{smtp_email}>"

    # Configurar el correo
    mensaje = MIMEMultipart()
    mensaje["From"] = from_email  # Campo personalizado
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto

    mensaje.attach(MIMEText(mensaje_html, "html"))

    # Conectar al servidor SMTP
    try:
        if smtp_use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)

        if smtp_use_tls:
            server.starttls()

        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, destinatario, mensaje.as_string())
        server.quit()
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
