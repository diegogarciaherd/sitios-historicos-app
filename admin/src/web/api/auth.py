from flask import Blueprint, jsonify, request
from core.models.user import read_user_by_email
from core.services.auth_service import authenticate
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_api_bp =  Blueprint("auth_api", __name__, url_prefix="/api/auth")

def validate_user_data(data: dict):
    errors = []
    if not "email" in data or not data["email"].strip():
        errors.append("El campo email esta vacio.")
    if not "password" in data or not data["password"].strip():
        errors.append("El campo contrasena esta vacio.")
    return errors

@auth_api_bp.post("/")
def login():
    data = request.get_json()
    errors = validate_user_data(data)
    if not errors:
        user = read_user_by_email(data["email"])
        if user:
            auth_errors = authenticate(data["email"], data["password"])[1]
            if not auth_errors:
                ttl = timedelta(seconds=99999)
                token = create_access_token(identity=str(user.id), expires_delta=ttl)
                return jsonify({
                    "token": token,
                    "expires_in": 99999
                }), 200
            else:
                return jsonify({
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Credenciales invalidas."
                    }
                }), 401
        else:
            return jsonify({
                "error": {
                    "code": "invalid_credentials",
                    "message": "Credenciales invalidas."
                }
            }), 401
    else:
        return jsonify({
            "error": {
            "code": "Parameter validation failed",
            "message": errors
        }
    }), 400
