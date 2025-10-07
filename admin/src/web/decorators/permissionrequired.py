from functools import wraps
from flask import abort, session

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get("user_role")
            if user_role not in roles:
                return abort(401)
            return f(*args, **kwargs)
        return decorated_function 
    return decorator
