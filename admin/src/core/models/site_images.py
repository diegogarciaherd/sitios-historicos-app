from core.database import Base, db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, String, Boolean, DateTime, func
from os import fstat
import uuid
from flask import current_app


class SiteImages(Base):
    """
    Tabla para almacenar las imagenes asociadas a los sitios históricos.
    Cada imagen contiene el ID del sitio, la url de la imagen, un texto alt, una descripcion, un numero de orden, un boolean de si es_portada y su fecha de registro,
    """

    __tablename__ = "site_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id"), index=True, nullable=False
    )
    object_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Almacena el object_name en Minio
    alt_text: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[str] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    def __repr__(self):
        """Representación en cadena del objeto SiteImages."""

        return f"<SiteImages site_id={self.site_id} object_name={self.object_name}>"


def create_site_image(site_id: int, **kwargs) -> SiteImages:
    """Crea una nueva instancia de SiteImages y almacena la imagen en Minio.

    Args:
        site_id (int): ID del sitio histórico asociado.
        **kwargs: Argumentos adicionales para los campos de SiteImages y Metadata de Minio.

    Returns:
        SiteImages: La instancia creada de SiteImages.
    """

    client_storage = current_app.storage
    bucket_name = current_app.config.get("MINIO_BUCKET")

    client_storage.put_object(
        bucket_name=bucket_name,
        object_name=kwargs["object_name"],
        data=kwargs["data"],
        length=kwargs["length"],
        content_type=kwargs["content_type"],
    )

    site_image = SiteImages(
        site_id=site_id,
        object_name=kwargs["object_name"],
        alt_text=kwargs["alt_text"],
        description=kwargs["description"],
        order=kwargs["order"],
        is_cover=kwargs["is_cover"],
    )

    db.session.add(site_image)
    db.session.commit()

    return site_image


def get_images_by_site(site_id: int) -> list[SiteImages]:
    """Obtiene todas las imágenes asociadas a un sitio histórico.

    Args:
        site_id (int): ID del sitio histórico.

    Returns:
        list[SiteImages]: Lista de instancias de SiteImages asociadas al sitio.
    """
    return db.session.query(SiteImages).filter(SiteImages.site_id == site_id).all()


def update_image_data(site_image_id: int, **kwargs):
    """Actualiza los datos de una imagen en la base de datos."""

    image = db.session.query(SiteImages).get(site_image_id)
    if not image:
        raise ValueError(f"Imagen con ID {site_image_id} no encontrada.")

    for key, value in kwargs.items():
        if hasattr(image, key):
            setattr(image, key, value)

    db.session.commit()


def delete_image(image_id: int):
    """Elimina una imagen de la base de datos.

    Args:
        image_id (int): ID de la imagen a eliminar.
    """
    image = db.session.query(SiteImages).get(image_id)
    if image:
        db.session.delete(image)
        db.session.commit()


def get_image_cover_by_site(site_id: int) -> SiteImages | None:
    """Obtiene la imagen de portada asociada a un sitio histórico.

    Args:
        site_id (int): ID del sitio histórico.

    Returns:
        SiteImages | None: Instancia de SiteImages que es la imagen de portada, o None si no existe.
    """
    return (
        db.session.query(SiteImages)
        .filter(SiteImages.site_id == site_id, SiteImages.is_cover == True)
        .first()
    )


def generate_data_for_update(request, site_id) -> list:
    """Genera una lista de diccionarios con los datos actualizados de las imágenes asociadas a un sitio histórico.

    Keyword arguments:
    request -- objeto de la solicitud que contiene los datos del formulario.
    site_id -- ID del sitio histórico.
    Return: lista de diccionarios con los datos actualizados de las imágenes.
    """

    data_for_update = []
    existing_images = get_images_by_site(site_id)

    if len(existing_images) > 0:
        for img in existing_images:
            data_for_update.append(
                {
                    "id": img.id,
                    "alt_text": request.form.get(f"alt-text-{img.object_name}", ""),
                    "description": request.form.get(
                        f"description-{img.object_name}", ""
                    ),
                    "order": request.form.get(f"order-{img.object_name}", 0),
                    "is_cover": (
                        request.form.get(f"is-cover-{img.object_name}", "off") == "on"
                    ),
                }
            )

    return data_for_update


def generate_data_for_create(request, site_id) -> list:
    """Genera una lista de diccionarios con los datos de las nuevas imágenes a crear asociadas a un sitio histórico.

    Keyword arguments:
    request -- objeto de la solicitud que contiene los datos del formulario.
    site_id -- ID del sitio histórico.
    Return: lista de diccionarios con los datos de las nuevas imágenes a crear.
    """

    data_for_create = []

    new_images = request.files.getlist("images")
    if new_images and len(new_images) > 0 and new_images[0].filename != "":
        for img in new_images:
            data_for_create.append(
                {
                    "object_name": f"public/sites/{site_id}/{uuid.uuid4()}{img.filename}",
                    "data": img,
                    "length": fstat(img.fileno()).st_size,
                    "content_type": img.content_type,
                    "alt_text": request.form.get(f"alt-text-{img.filename}", ""),
                    "description": request.form.get(f"description-{img.filename}", ""),
                    "order": request.form.get(f"order-{img.filename}", 0),
                    "is_cover": request.form.get(f"is-cover-{img.filename}", "off")
                    == "on",
                }
            )

    return data_for_create


def validate_site_images_data(request, site_id) -> list:
    """Verifica que los datos de las imagenes a subir cumplan con las restricciones establecidas.

    Args:
        request: Objeto de la solicitud que contiene los datos de las imágenes.
        site_id: ID del sitio histórico, puede ser None si es un nuevo sitio.

    Returns:
        list: Lista de errores encontrados durante la validación.
    """

    errors = []
    model_data_to_validate = []  # Para validar los datos de la tabla
    new_data_to_validate = []  # Para validar los datos de minio

    # Verificamos si el sitio tiene imagenes guardadas
    existing_images = []
    if site_id is not None:
        existing_images = get_images_by_site(site_id)

    # Si el sitio tiene imagenes guardadas, agregamos los inputs de las mismas al model_data_to_validate
    if len(existing_images) > 0:
        for img in existing_images:
            model_data_to_validate.append(
                {
                    "image": img.object_name,
                    "order": request.form.get(f"order-{img.object_name}", 0),
                    "is_cover": (
                        request.form.get(f"is-cover-{img.object_name}", "off") == "on"
                    ),
                    "alt_text": request.form.get(f"alt-text-{img.object_name}", ""),
                }
            )

    # Verificamos si se están subiendo nuevas imágenes
    new_images = request.files.getlist("images")

    # Si hay nuevas imágenes, agregamos sus datos al model_data_to_validate y new_data_to_validate
    if new_images and len(new_images) > 0 and new_images[0].filename != "":
        for img in new_images:
            model_data_to_validate.append(
                {
                    "image": img.filename,
                    "order": request.form.get(f"order-{img.filename}", 0),
                    "is_cover": request.form.get(f"is-cover-{img.filename}", "off")
                    == "on",
                    "alt_text": request.form.get(f"alt-text-{img.filename}", ""),
                }
            )

            new_data_to_validate.append(
                {
                    "image": img.filename,
                    "format": img.content_type,
                    "size": fstat(img.fileno()).st_size,
                }
            )

    # Realizamos las validaciones necesarias en model_data_to_validate y new_data_to_validate

    if len(model_data_to_validate) > 0:
        # Validacion 1: Un sitio histórico puede tener un máximo de 10 imágenes.
        total_images = len(existing_images) + len(new_data_to_validate)
        if total_images > 10:
            errors.append("Se excede el límite máximo de 10 imágenes por sitio.")

        # Validacion 2: El campo 'alt_text' no puede estar vacío.
        for data in model_data_to_validate:
            if not data["alt_text"] or data["alt_text"].strip() == "":
                errors.append(
                    "El campo 'Titulo/Alt' no puede estar vacío en la imagen: "
                    + data["image"]
                )

        # Validacion 3: Un sitio histórico sólo puede tener una imagen de portada.
        covers = sum(1 for data in model_data_to_validate if data["is_cover"])
        if covers > 1:
            errors.append("Un sitio sólo puede tener una imagen de portada.")
        elif covers == 0:
            errors.append("Debe seleccionarse una imagen de portada.")

        # Validacion 4: Los numeros de orden deben ser únicos y consecutivos, sin saltos.
        orders = [int(data["order"]) for data in model_data_to_validate]
        orders.sort()
        for i in range(len(orders)):
            if orders[i] != i + 1:
                errors.append(
                    "Los números de orden deben ser únicos y consecutivos, sin saltos."
                )
                break

        # Validacion 5 y 6: Formatos permitidos: JPG, PNG, WEBP y Tamaño máximo por archivo: 5 MB.
        allowed_formats = ["image/jpg", "image/jpeg", "image/png", "image/webp"]
        maxSize = 5 * 1024 * 1024  # 5 MB
        for data in new_data_to_validate:
            if data["format"].lower() not in allowed_formats:
                errors.append(f"Formato no permitido para la imagen {data['image']}.")
            if data["size"] > maxSize:
                errors.append(f"Tamaño excedido para la imagen {data['image']}.")

    return errors
