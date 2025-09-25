from flask import Blueprint
from flask import render_template
from src.core.models.sites import SitioHistorico, EstadoConservacion
from src.core.models import list_sites, create_sites
from src.core.database import db
from flask import request, redirect, url_for

sites_bp = Blueprint('sites', __name__, url_prefix='/sitios', template_folder='../templates/sites') # Define el blueprint para las rutas de sitios

@sites_bp.route('/')
def list_all_sites():
    sites = list_sites()
    return render_template('sites.html', sites=sites)

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