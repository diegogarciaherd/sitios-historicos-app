from src.core.models.sitios import SitioHistorico, EstadoConservacion
# Script para crear todas las tablas de los modelos
from src.core.database import db
from src.core.models.sitios import SitioHistorico

def list_sites():
	return db.session.query(SitioHistorico).all()

def create_sites(**kwargs):
	site = SitioHistorico(**kwargs)
	db.session.add(site)
	db.session.commit()
	return site

