"""
site_history.py
----------------
Servicio auxiliar para registrar el historial de modificaciones realizadas sobre
los sitios históricos. Permite generar trazabilidad de acciones como creación,
edición, eliminación y cambios de tags o coordenadas.

Incluye dos funciones principales:
- log_site_change(): persiste los cambios detectados en la tabla `sites_history`.
- diff_site(): compara dos estados de un sitio y devuelve las diferencias.

Notas de implementación:
- `diff_site` acepta tanto instancias de SQLAlchemy como snapshots en forma de
  diccionarios (por ejemplo, cuando tomás el "antes" como dict para evitar que
  quede enlazado a la sesión y pierdas el valor anterior).
- Las coordenadas (lat/lng) se registran como un único campo lógico
  `coordenadas`, con valores "lat, lng".
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from core.database import db
from core.models.site_history import SiteChange


def log_site_change(
    site_id: int,
    user_id: int | None,
    action: str,
    changes: dict[str, tuple[object, object]] | None = None,
) -> None:
    """
    Registra un evento en el historial de cambios (tabla `sites_history`).

    Args:
        site_id (int): ID del sitio afectado.
        user_id (int | None): ID del usuario que realizó la acción, si está disponible.
        action (str): Tipo de acción realizada. Valores posibles: 'create', 'update', 'delete'.
        changes (dict[str, tuple[object, object]] | None):
            Diccionario con los campos modificados y sus valores anteriores/nuevos.
            Ejemplo: {'nombre': ('Viejo', 'Nuevo'), 'estado': ('Bueno', 'Regular')}

    Comportamiento:
        - Si la acción es 'create' o 'delete', se registra una sola entrada sin campos.
        - Si es 'update', se registra una fila por cada campo modificado.
        - No realiza commit; este se delega al flujo del controlador.
    """
    if action in ("create", "delete") or not changes:
        db.session.add(
            SiteChange(
                site_id=site_id,
                user_id=user_id,
                action=action,
                field=None,
                old_value=None,
                new_value=None,
            )
        )
        return

    for field, (old, new) in changes.items():
        # Evitar filas inútiles cuando no hay cambio real
        if str(old) == str(new):
            continue
        db.session.add(
            SiteChange(
                site_id=site_id,
                user_id=user_id,
                action=action,
                field=field,
                old_value=str(old) if old is not None else None,
                new_value=str(new) if new is not None else None,
            )
        )


def _to_list_names(maybe_tags) -> list[str]:
    """
    Convierte una lista de objetos Tag en una lista ordenada de nombres.

    Args:
        maybe_tags (list | None): Lista de objetos Tag o None.

    Returns:
        list[str]: Nombres de los tags ordenados alfabéticamente.
    """
    try:
        return sorted([t.name for t in (maybe_tags or [])])
    except Exception:
        return []


def _get(source: Any, key: str) -> Any:
    """
    Obtiene un valor desde un snapshot que puede ser dict o instancia.

    Args:
        source: Diccionario o instancia de modelo.
        key (str): Nombre del atributo / clave.

    Returns:
        Any: Valor encontrado o None.
    """
    if isinstance(source, dict):
        return source.get(key, None)

    return getattr(source, key, None)


def diff_site(before: Any, after: Any) -> dict[str, tuple[object, object]]:
    """
    Compara dos estados de un sitio (antes y después) y detecta qué campos cambiaron.

    Acepta:
        - Instancias de `SitioHistorico` (objetos SQLAlchemy), o
        - Snapshots en forma de `dict` (útil para tomar el "antes" sin que se
          actualice por la sesión).

    Args:
        before: Estado del sitio antes de los cambios (objeto o dict).
        after:  Estado del sitio después de los cambios (objeto o dict).

    Returns:
        dict[str, tuple[object, object]]:
            Diccionario con las diferencias detectadas, donde cada clave es el nombre
            del campo y el valor es una tupla (valor_anterior, valor_nuevo).

    Campos rastreados:
        - nombre
        - descripcionBreve
        - estado
        - ciudad
        - provincia
        - visible
        - categoria
        - coordenadas (lat/lng agrupadas en un único campo lógico)
    """
    tracked_scalars = [
        "nombre",
        "descripcionBreve",
        "estado",
        "ciudad",
        "provincia",
        "visible",
        "categoria",
    ]
    out: Dict[str, Tuple[object, object]] = {}

    # Cambios simples (no coordenadas)
    for f in tracked_scalars:
        old = _get(before, f)
        new = _get(after, f)
        if str(old) != str(new):
            out[f] = (old, new)

    # Coordenadas agrupadas (si existen)
    old_lat, old_lng = _get(before, "lat"), _get(before, "lng")
    new_lat, new_lng = _get(after, "lat"), _get(after, "lng")
    if str(old_lat) != str(new_lat) or str(old_lng) != str(new_lng):

        def _pair(lat, lng):
            # Si falta alguno, devolvemos None para evitar "None, None" confuso
            if lat is None or lng is None:
                return None
            return f"{lat}, {lng}"

        out["coordenadas"] = (_pair(old_lat, old_lng), _pair(new_lat, new_lng))

    return out


def diff_tags(before: Any, after: Any) -> dict[str, tuple[object, object]]:
    """
    Devuelve {'tags': ('tag1, tag2', 'tag1, tag3')} si cambió el set de tags.
    No hace nada si son iguales.

    Acepta objetos SQLAlchemy con relación .tags ya cargada. Si no hay relación
    o no está cargada, devolverá {}.
    """

    def _names(sitio) -> list[str]:
        try:
            return [t["name"] for t in sitio["tags"]]
        except Exception:
            return []

    old_names = _names(before)
    new_names = _names(after)

    if old_names != new_names:
        return {
            "tags": (
                ", ".join(old_names) or None,
                ", ".join(new_names) or None,
            )
        }
    return {}
