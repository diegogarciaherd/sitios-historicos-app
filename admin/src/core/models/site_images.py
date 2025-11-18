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

    # Validaciones:
    # 1. Que el sitio exista
    # 2. Que no exista otra imagen con el mismo order para el mismo site_id
    # 3. Que el order sea un numero positivo
    # 4. Que alt_text, description y object_name no sean vacios
    # 5. Que el sitio tenga menos de 10 imagenes

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
