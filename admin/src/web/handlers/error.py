from dataclasses import dataclass
from flask import render_template

@dataclass
class HTTPError:
    '''Representa un error HTTP con código, mensaje y descripción'''
    code: int
    message: str
    description: str

def not_found(e):
    '''Maneja el error 404 - Página no encontrada'''
    error = HTTPError(
            code = 404,
            message = "Página no encontrada",
            description = "La página deseada no existe"
    )
    return render_template('error.html', error=error), 404

def unauthorized(e):
    '''Maneja el error 401 - No autorizado'''
    error = HTTPError(
            code = 401,
            message = "Acceso no autorizado",
            description = "No tiene autorización para ver el contenido"
    )
    return render_template('error.html', error=error), 401

def server_error(e):
    '''Maneja el error 500 - Error interno de servidor'''
    error = HTTPError(
            code = 500,
            message = "Error interno de servidor",
            description = "Ha ocurrido un error inesperado"
    )
    return render_template('error.html', error=error), 500
