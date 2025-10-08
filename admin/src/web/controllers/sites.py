from datetime import datetime
from flask import Blueprint, send_file, jsonify
from flask import render_template, flash, abort, session
from core.models.sites import (
    list_sites,
    list_sites_with_filters,
    create_sites,
    update_site,
    get_site,
    delete_site_by_id,
    get_all_cities,
    get_all_provinces,
    SitioHistorico,
    EstadoConservacion,
    export_to_csv,
)
from core.database import db
from flask import request, redirect, url_for
from .validators.site_validator import validate_site_data
import tempfile

sites_bp = Blueprint(
    "sites", __name__, url_prefix="/sitios", template_folder="../templates/sites"
)  # Define el blueprint para las rutas de sitios


@sites_bp.route("/")
def list_all_sites():
    query_params = request.args.to_dict()

    page = request.args.get("page", 1, type=int)
    per_page = 25
    # sites, total = list_sites(page=page, per_page=per_page)
    sites, total = list_sites_with_filters(query_params, page=page, per_page=per_page)

    # Ordenar los resultaos por fecha de registro, nombre o ciudad (asc/desc).
    # Primero por fecha de registro descendente (los más recientes primero)
    # En caso de empate, por nombre ascendente (A-Z)
    # En caso de nuevo empate, por ciudad ascendente (A-Z)
    sites.sort(
        key=lambda s: (s.fechaRegistro, s.nombre.lower(), s.ciudad.lower()),
        reverse=True,
    )

    # Calcular información de paginación
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_num": prev_num,
        "next_num": next_num,
    }

    cities = [c[0] for c in get_all_cities()]
    provinces = [p[0] for p in get_all_provinces()]

    return render_template(
        "sites.html",
        pagination=pagination,
        sites=sites,
        cities=cities,
        provinces=provinces,
    )


@sites_bp.route("/crear_sitio", methods=["GET", "POST"])
def create_site():
    if request.method == "POST":
        try:
            # Convertir a diccionario normal
            data = request.form.to_dict()

            # Procesar checkbox
            data["visible"] = "visible" in request.form

            # 1. Validar datos primero
            errors = validate_site_data(data)
            if errors:
                for field, error_message in errors.items():
                    flash(f"{field}: {error_message}", "error")
                return render_template("form.html")

            create_sites(**data)
            session["success_message"] = "Sitio histórico creado correctamente"
            return redirect(url_for("sites.list_all_sites"))

        except Exception as e:
            flash(f"Error al crear el sitio: {str(e)}", "error")

    return render_template("form.html")


@sites_bp.route("/editar_sitio/<int:id>", methods=["GET", "POST"])
# Mejorada con validación y manejo de errores
def edit_site(id):
    site = get_site(id)
    if not site:
        abort(404)

    if request.method == "POST":
        try:
            # Validar datos
            data = request.form.to_dict()
            data["visible"] = "visible" in request.form

            errors = validate_site_data(data)
            if errors:
                for field, error_message in errors.items():
                    flash(f"{field}: {error_message}", "error")
                return render_template("form.html", site=site)

            # Actualizar
            update_site(id, **data)
            session["success_message"] = "Sitio histórico actualizado correctamente"
            return redirect(url_for("sites.list_all_sites"))
        except Exception as e:
            flash(f"Error al crear el sitio: {str(e)}", "error")

    return render_template("form.html", site=site)


@sites_bp.route("/eliminar_sitio/<int:id>", methods=["POST"])
def delete_site(id):
    try:
        # Llama a la función existente
        delete_site_by_id(id)
        site = get_site(id)  # Verifica si el sitio aún existe
        if not site:
            flash("Sitio eliminado correctamente", "success")
        else:
            flash("Sitio no encontrado", "error")
    except Exception as e:
        flash(f"Error al eliminar el sitio: {str(e)}", "error")
    return redirect(url_for("sites.list_all_sites"))


@sites_bp.route("/ver_sitio/<int:id>", methods=["GET"])
def view_site(id):
    site = get_site(id)
    return render_template("show_site.html", site=site)


@sites_bp.route("/exportar_csv", methods=["GET"])
def export_csv():
    """Función para exportar los sitios a un archivo CSV."""

    try:
        query_params = request.args.to_dict()

        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".csv"
        ) as temp_csv:
            export_to_csv(temp_csv.name, filters=query_params)
            temp_csv.flush()

        # Nombre del archivo: sitios_<YYYYMMDD_HHMM>.csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        download_name = f"sitios_{timestamp}.csv"

        return send_file(
            temp_csv.name,
            as_attachment=True,
            download_name=download_name,
            mimetype="text/csv",
        )
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al exportar CSV: {str(e)}"}), 500
