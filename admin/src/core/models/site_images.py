from core.database import Base, db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, String, Boolean, DateTime, func


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


def create_site_image(
    site_id: int,
    object_name: str,
    alt_text: str,
    description: str,
    order: int,
    is_cover: bool = False,
) -> SiteImages:
    """Crea una nueva instancia de SiteImages y la guarda en la base de datos.

    Args:
        site_id (int): ID del sitio histórico asociado.
        object_name (str): Nombre del objeto en Minio.
        alt_text (str): Texto alternativo para la imagen.
        description (str): Descripción de la imagen.
        order (int): Orden de la imagen.
        is_cover (bool, optional): Indica si es la imagen de portada. Por defecto es False.
    """

    site_image = SiteImages(
        site_id=site_id,
        object_name=object_name,
        alt_text=alt_text,
        description=description,
        order=order,
        is_cover=is_cover,
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


def validate_site_images(site_id: int, images: list) -> bool:
    """Verifica si se pueden subir una cantidad determinada de imágenes a un sitio histórico, considerando las restricciones establecidas:
    1. Formatos permitidos: JPG, PNG, WEBP.
    2. Tamaño máximo por archivo: 5 MB.
    3. Sólo una imagen puede ser marcada como portada.
    4. Los numeros de orden deben ser únicos y consecutivos, sin saltos.
    5. Límite máximo de 10 imágenes por sitio.


    Args:
        site_id (int): ID del sitio histórico.
        images: Lista de imágenes que se desean subir.

    Returns:
        bool: True si se pueden subir las imágenes, False en caso contrario.
    """
    flag = True
    existing_images = get_images_by_site(site_id)

    # Validar límite máximo de 10 imágenes
    total_images = len(existing_images) + len(images)
    if total_images > 10:
        flag = False
        raise ValueError("Error: Se excede el límite máximo de 10 imágenes por sitio.")

    # Validar numeros de orden únicos y consecutivos
    existing_orders = [img.order for img in existing_images]
    new_orders = [img["order"] for img in images]
    all_orders = existing_orders + new_orders
    for i in range(0, len(all_orders)):
        if int(all_orders[i]) != i + 1:
            flag = False
            raise ValueError(
                "Error: Los números de orden deben ser únicos y consecutivos, sin saltos."
            )

    # Validamos que sólo haya una imagen de portada
    existing_cover = any(img.is_cover for img in existing_images)
    new_covers = sum(1 for img in images if img.get("is_cover", False))
    if existing_cover and new_covers > 0:
        flag = False
        raise ValueError(
            "Error: Ya existe una imagen de portada para este sitio histórico."
        )
    if new_covers > 1:
        flag = False
        raise ValueError("Error: Sólo se permite una imagen de portada por sitio.")

    # Validar formatos y tamaños
    allowed_formats = ["image/jpg", "image/jpeg", "image/png", "image/webp"]
    maxSize = 5 * 1024 * 1024  # 5 MB
    for img in images:
        if img["format"].lower() not in allowed_formats:
            flag = False
            raise ValueError(
                f"Error: Formato no permitido para la imagen {img.get('filename', '')}. "
                f"Formatos permitidos: JPG, PNG, WEBP."
            )
        if img["size"] > maxSize:
            flag = False
            raise ValueError(
                f"Error: Tamaño excedido para la imagen {img.get('filename', '')}. "
                f"Tamaño máximo permitido: 5 MB."
            )

    return flag
