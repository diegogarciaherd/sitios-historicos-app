# admin/src/web/api/auth.py
"""
Endpoints de autenticación para el portal público.

Acá expongo un login simple basado en JWT para que el frontend
pueda autenticarse contra la API.

Flujo:
- El portal hace POST /api/auth/ con { "email", "password" }.
- Valido que vengan esos campos.
- Llamo a `authenticate(email, password)` que devuelve (user, error).
- Si hay error → devuelvo 400/401 con mensaje legible.
- Si todo ok → genero un JWT y respondo con:
    {
        "access_token": "<jwt>",
        "user_id": ...,
        "user": { ... }
    }

El hook `useAuth` del portal espera exactamente:
- response.data.access_token
- response.data.user_id
"""

from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from core.services.auth_service import authenticate

# Blueprint con prefijo /api/auth
auth_api_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")


def validate_user_data(data: dict) -> list[str]:
    """
    Valida que el payload de login tenga email y password no vacíos.
    """
    errors: list[str] = []

    if "email" not in data or not str(data["email"]).strip():
        errors.append("El campo email esta vacio.")

    if "password" not in data or not str(data["password"]).strip():
        errors.append("El campo contrasena esta vacio.")

    return errors


@auth_api_bp.post("/")
def login_api():
    """
    Endpoint de login para el portal público.

    Espera:
        {
            "email": "usuario@example.com",
            "password": "secreta"
        }

    Respuestas:
    - 200 OK: credenciales válidas → devuelve token y datos del usuario.
    - 400 Bad Request: faltan parámetros.
    - 401 Unauthorized: credenciales inválidas o cuenta bloqueada.
    """
    data = request.get_json() or {}

    # Validación básica de payload
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

    # authenticate devuelve (user, error)
    user, auth_error = authenticate(email, password)

    if auth_error or not user:
        # Mantengo un solo código genérico para el portal
        return (
            jsonify(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": auth_error or "Credenciales invalidas.",
                    }
                }
            ),
            401,
        )

    # Si llegamos hasta acá, las credenciales son válidas.
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(hours=2),
        additional_claims={
            "email": user.email,
            "name": getattr(user, "name", ""),
            "last_name": getattr(user, "last_name", ""),
        },
    )

    # Payload alineado con useAuth del portal
    return (
        jsonify(
            {
                "access_token": access_token,
                "user_id": user.id,
                "user": {
                    "id": user.id,
                    "name": getattr(user, "name", ""),
                    "last_name": getattr(user, "last_name", ""),
                    "email": user.email,
                },
            }
        ),
        200,
    )
