# admin/src/web/api/auth.py
"""
Endpoints de autenticación para el portal público.

Acá exponemos un login simple basado en JWT para que el frontend
pueda autenticarse contra la API.

Flujo general:
- El portal hace POST /api/auth/ con { "email", "password" }.
- Validamos que vengan los campos básicos.
- Usamos el servicio `authenticate` para verificar credenciales.
- Si todo está bien, generamos un JWT con `create_access_token`.
- Devolvemos:
    {
        "access_token": "<jwt>",
        "token": "<jwt>",           # alias por compatibilidad
        "expires_in": 7200,
        "user_id": 1,
        "user": {
            "id": 1,
            "name": "...",
            "last_name": "...",
            "email": "..."
        }
    }

Así el hook `useAuth` del portal puede leer `access_token` y opcionalmente `user_id`.
"""

from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from google.oauth2 import id_token
from google.auth.transport import requests

from core.models.user import read_user_by_email, create_user_from_google_auth
from core.services.auth_service import authenticate

# Blueprint con prefijo /api/auth
auth_api_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")


def validate_user_data(data: dict) -> list[str]:
    """
    Valida que el payload de login tenga email y password no vacíos.

    Args:
        data (dict): JSON recibido en el body.

    Returns:
        list[str]: Lista de errores encontrados. Vacía si está todo bien.
    """
    errors: list[str] = []

    # email obligatorio
    if "email" not in data or not str(data["email"]).strip():
        errors.append("El campo email esta vacio.")

    # password obligatoria
    if "password" not in data or not str(data["password"]).strip():
        errors.append("El campo contrasena esta vacio.")

    return errors


@auth_api_bp.post("/")
def login():
    """
    Endpoint de login para el portal público.

    Espera un JSON con:
        {
            "email": "usuario@example.com",
            "password": "secreta"
        }

    Respuestas:
    - 200 OK: credenciales válidas, devuelve JWT y datos básicos del usuario.
    - 401 Unauthorized: credenciales incorrectas o cuenta inactiva/eliminada.
    - 400 Bad Request: faltan parámetros o son inválidos.
    """
    data = request.get_json() or {}

    # Validamos estructura mínima
    errors = validate_user_data(data)
    if errors:
        return (
            jsonify(
                {
                    "error": {
                        "code": "Parameter validation failed",
                        "message": errors,
                    }
                }
            ),
            400,
        )

    email = data["email"].strip()
    password = data["password"].strip()

    # Buscamos al usuario
    user = read_user_by_email(email)
    if not user:
        # No filtramos info: mismo error para usuario inexistente o pass mal
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Credenciales invalidas.",
                    }
                }
            ),
            401,
        )

    # Usamos el servicio existente, que devuelve (user, error_str)
    _, auth_error = authenticate(email, password)
    if auth_error:
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Credenciales invalidas.",
                    }
                }
            ),
            401,
        )

    # Si llegamos acá, las credenciales son válidas.
    # Generamos un JWT que el portal usará en el header Authorization.
    ttl = timedelta(hours=2)
    # IMPORTANTE: identity como string para evitar "Subject must be a string"
    access_token = create_access_token(identity=str(user.id), expires_delta=ttl)

    payload = {
        "access_token": access_token,
        # Alias por compatibilidad (por si alguien usa "token")
        "token": access_token,
        "expires_in": int(ttl.total_seconds()),
        "user_id": user.id,
        "user": {
            "id": user.id,
            "name": getattr(user, "name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": user.email,
        },
    }

    return jsonify(payload), 200


@auth_api_bp.post("/google")
def google_auth():
    """
    Endpoint de login con Google para el portal público.

    Espera un JSON con:
        { "token": "<id_token_de_google>" }

    Verifica el token con Google, crea el usuario si no existe
    y devuelve un JWT con la misma estructura que el login normal.
    """
    data = request.get_json() or {}

    if "token" not in data:
        return (
            jsonify(
                {
                    "error": {
                        "code": "Parameter validation failed",
                        "message": ["El token de Google es obligatorio."],
                    }
                }
            ),
            400,
        )

    # Verificamos el ID token de Google
    idinfo = id_token.verify_oauth2_token(
        data["token"],
        requests.Request(),
    )

    # Buscamos o creamos el usuario
    user = read_user_by_email(idinfo["email"])
    if not user:
        new_user_data = {
            "email": idinfo["email"],
            "name": idinfo.get("name", ""),
        }
        create_user_from_google_auth(new_user_data)
        user = read_user_by_email(idinfo["email"])

    # Generamos el JWT para el portal
    ttl = timedelta(hours=2)
    access_token = create_access_token(
        identity=str(user.id),  # de nuevo, STRING
        expires_delta=ttl,
        additional_claims={
            "email": user.email,
            "name": getattr(user, "name", ""),
            "last_name": getattr(user, "last_name", ""),
        },
    )

    if not access_token:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error ocurred.",
                    }
                }
            ),
            500,
        )

    payload = {
        "access_token": access_token,
        "token": access_token,
        "expires_in": int(ttl.total_seconds()),
        "user_id": user.id,
        "user": {
            "id": user.id,
            "name": getattr(user, "name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": user.email,
        },
    }

    return jsonify(payload), 200
