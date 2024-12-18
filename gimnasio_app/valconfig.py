import jwt
import datetime

# Clave secreta para verificar el token
SECRET_KEY = "mi_clave_secreta"

def verificar_licencia(token):
    """Verifica la validez del token JWT."""
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Verificar fechas
        ahora = datetime.datetime.utcnow()
        fecha_activacion = datetime.datetime.fromisoformat(payload["activacion"])
        fecha_expiracion = datetime.datetime.fromisoformat(payload["expiracion"])
        
        if ahora < fecha_activacion:
            raise Exception("La licencia aún no está activa.")
        if ahora > fecha_expiracion:
            raise Exception("La licencia ha expirado.")
        
        return True  # Licencia válida
    except jwt.ExpiredSignatureError:
        raise Exception("El token ha expirado.")
    except jwt.InvalidTokenError:
        raise Exception("El token es inválido.")
