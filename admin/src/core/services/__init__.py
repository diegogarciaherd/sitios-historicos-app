# src/core/services/__init__.py
from .auth_roles import (
    load_user,
    inject_template_helpers,
    require_login,
    require_permission,
)