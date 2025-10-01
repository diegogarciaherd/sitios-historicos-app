from flask import Blueprint
from flask import render_template
from src.core.models.sites import SitioHistorico, EstadoConservacion
from src.core.models.sites import list_sites, create_sites, update_site, get_site, delete_site
from src.core.database import db
from flask import request, redirect, url_for

sites_bp = Blueprint('sites', __name__, url_prefix='/sitios', template_folder='../templates/sites') # Define el blueprint para las rutas de sitios

@sites_bp.route('/')
def list_all_sites():
    page = request.args.get('page', 1, type=int)
    pagination = list_sites(page=page)
    return render_template('sites.html', pagination=pagination, sites=pagination.items)



@sites_bp.route('/crear_sitio', methods=['GET', 'POST'])
def create_site():
    if request.method == 'POST':
        estado_str = request.form["estado"]
        estado = EstadoConservacion[estado_str]

        data = {
            "nombre": request.form["nombre"],
            "descripcionBreve": request.form["descripcionBreve"],
            "descripcionCompleta": request.form.get("descripcionCompleta") or None,
            "ciudad": request.form["ciudad"],
            "provincia": request.form["provincia"],
            "latitud": float(request.form["latitud"]),
            "longitud": float(request.form["longitud"]),
            "estado": estado,
            "añoInauguracion": int(request.form["añoInauguracion"]) if request.form.get("añoInauguracion") else None,
            "categoria": request.form["categoria_nombre"],  # campo texto en este branch
            "visible": "visible" in request.form,
        }

        create_sites(**data)
        return redirect(url_for('sites.list_all_sites'))

    return render_template('form.html')

@sites_bp.route('/editar_sitio/<int:id>', methods=['GET', 'POST'])
def edit_site(id):
    site = get_site(id)
    if request.method == 'POST':
        update_site(id, request.form)
        return redirect(url_for('sites.list_all_sites'))
    return render_template('form.html', site=site)

@sites_bp.route('/eliminar_sitio/<int:id>', methods=['POST'])
def delete_site(id):
    delete_site(id)
    return redirect(url_for('sites.list_all_sites'))

@sites_bp.route('/ver_sitio/<int:id>', methods=['GET'])
def view_site(id):
    site = get_site(id)
    return render_template('view.html', site=site)


