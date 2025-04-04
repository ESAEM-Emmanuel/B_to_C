# app/database.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from app.config import settings  # Importez les configurations

# Création du moteur SQLAlchemy
engine = create_engine(settings.DATABASE_URL)

# Création d'une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Déclaration de la classe de base pour les modèles SQLAlchemy
Base = declarative_base()

# Fonction utilitaire pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()