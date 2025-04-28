# Étape 1 : Utiliser une image de base Python
FROM python:3.10-slim

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers nécessaires dans le conteneur
COPY ./requirements.txt .
COPY .env .

# Étape 4 : Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier le reste du code source
COPY . .

# Étape 6 : Exposer le port sur lequel FastAPI écoutera
EXPOSE 8000
# etape 7 : effectuer les migration
alembic upgrade head

# Étape 7 : Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]