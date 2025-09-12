from dataclasses import dataclass
from flask import render_template

@dataclass
class HTTPError:
    code: int
    message: str
    description: str

def not_found(e):
    error = HTTPError(
            code = 404,
            message = "Página no encontrada",
            description = "La página deseada no existe"
    )
    return render_template('error.html', error=error), 404

def unauthorized(e):
    error = HTTPError(
            code = 401,
            message = "Acceso no autorizado",
            description = "No tiene autorización para ver el contenido"
    )
    return render_template('error.html', error=error), 401

def server_error(e):
    error = HTTPError(
            code = 500,
            message = "Error interno de servidor",
            description = "Ha ocurrido un error inesperado"
    )
    return render_template('error.html', error=error), 500
