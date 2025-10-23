from flask import Blueprint
from flask import render_template, flash, abort
from msgspec import ValidationError
from core.models.feature_flags import list_feature_flags, update_feature_flag, get_feature_flag
from flask import request, redirect, url_for
from core.services.auth_roles import require_permission

feature_flags_bp = Blueprint('feature_flags', __name__, url_prefix='/feature_flags', template_folder='../templates/feature_flags') # Define el blueprint para las rutas de sitios

@feature_flags_bp.route('/')
@require_permission('feature_flags.manage')
def list_all_feature_flags():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    feature_flags, total = list_feature_flags(page=page, per_page=per_page)

    # Calcular información de paginación
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_num': prev_num,
        'next_num': next_num
    }
    return render_template('feature_flags.html', pagination=pagination, feature_flags=feature_flags)

@feature_flags_bp.route('/editar_flag/<int:id>', methods=['GET', 'POST'])
@require_permission('feature_flags.manage')
# Mejorada con validación y manejo de errores
def edit_feature_flag(id):
    feature_flag = get_feature_flag(id)
    if not feature_flag:
        abort(404)
    
    if request.method == 'POST':
        try:
            # Validar datos
            data = request.form.to_dict()
            # Actualizar
            updated_feature_flag = update_feature_flag(id, **data)
            flash('Flag de funcionalidad actualizado correctamente', 'success')
            return redirect(url_for('feature_flags.list_all_feature_flags'))
        except ValidationError as e:
            flash(str(e), 'error')

    return render_template('form.html', feature_flag=feature_flag)

@feature_flags_bp.route('/toggle_feature_flag/<int:id>', methods=['GET'])
@require_permission('feature_flags.manage')
def toggle_feature_flag(id):
    feature_flag = get_feature_flag(id)
    if not feature_flag:
        abort(404)

    # Alternar el estado del flag
    new_state = not feature_flag.activated
    update_feature_flag(id, activated=new_state)
    return '', 204