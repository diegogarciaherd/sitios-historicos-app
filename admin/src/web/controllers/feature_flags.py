from flask import Blueprint
from flask import render_template, flash, abort
from src.core.models.feature_flags import FeatureFlag
from src.core.models.feature_flags import list_feature_flags, create_feature_flag, update_feature_flag, get_feature_flag, delete_feature_flag
from src.core.database import db
from flask import request, redirect, url_for

feature_flags_bp = Blueprint('feature_flags', __name__, url_prefix='/feature_flags', template_folder='../templates/feature_flags') # Define el blueprint para las rutas de sitios

def validate_feature_flag_data(form_data, is_update=False):
    errors = []
    data = {}
    
    # Validar campos obligatorios
    required_fields = ['name', 'activated']
    for field in required_fields:
        if not form_data.get(field):
            errors.append(f"El campo {field} es obligatorio")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    # Validar y convertir datos
    try:
        data['name'] = form_data['name'].strip()
        data['activated'] = form_data['activated'] == 'true'
    except (ValueError, KeyError) as e:
        raise ValueError(f"Error en el formato de los datos: {str(e)}")
    
    return data

@feature_flags_bp.route('/')
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

@feature_flags_bp.route('/crear_flag', methods=['GET', 'POST'])
def create_feature_flag():
    if request.method == 'POST':
        try:
            data = validate_feature_flag_data(request.form)
            create_feature_flag(**data)
            flash('Flag de funcionalidad creado correctamente', 'success')
            return redirect(url_for('feature_flags.list_all_feature_flags'))
        except ValueError as e:
            flash(f'Error de validación: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error al crear el flag de funcionalidad: {str(e)}', 'error')

    return render_template('form.html')

@feature_flags_bp.route('/editar_flag/<int:id>', methods=['GET', 'POST'])
# Mejorada con validación y manejo de errores
def edit_feature_flag(id):
    feature_flag = get_feature_flag(id)
    if not feature_flag:
        abort(404)
    
    if request.method == 'POST':
        try:
            # Validar datos
            data = validate_feature_flag_data(request.form)
            # Actualizar
            updated_feature_flag = update_feature_flag(id, **data)
            flash('Flag de funcionalidad actualizado correctamente', 'success')
            return redirect(url_for('feature_flags.list_all_feature_flags'))
        except ValidationError as e:
            flash(str(e), 'error')

    return render_template('form.html', feature_flag=feature_flag)

@feature_flags_bp.route('/eliminar_flag/<int:id>', methods=['POST'])
def delete_feature_flag(id):
    delete_feature_flag(id)
    return redirect(url_for('feature_flags.list_all_feature_flags'))

@feature_flags_bp.route('/ver_flag/<int:id>', methods=['GET'])
def view_feature_flag(id):
    feature_flag = get_feature_flag(id)
    return render_template('view.html', feature_flag=feature_flag)