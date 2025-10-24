from functools import wraps
from flask import session
from flask import redirect, url_for

def login_required(f):
    '''Decorator que verifica si un usuario está autenticado'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login.login"))
        return f(*args, **kwargs)
    return decorated_function
