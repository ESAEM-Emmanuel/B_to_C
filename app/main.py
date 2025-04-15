from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime
from app.config import settings
from app.database import engine, get_db
from app.models.models import Base, Country, Town
from fastapi.openapi.utils import get_openapi

# Initialisation de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=None if not settings.DEBUG else "/docs",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="medias"), name="static")

# Journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Personnalisation de la documentation OpenAPI
def custom_openapi():
    # Vérifie si le schéma OpenAPI a déjà été généré
    if app.openapi_schema:
        return app.openapi_schema

    # Génère le schéma OpenAPI avec les paramètres personnalisés
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Documentation de l'API",
        routes=app.routes,
    )

    # Ajoute un schéma de sécurité OAuth2 avec un flux de mot de passe
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/login",  # Endpoint utilisé pour l'authentification
                    "scopes": {},          # Aucun scope défini ici
                }
            },
            "auto_error": False,  # Empêche l'erreur automatique si le token n'est pas fourni
        }
    }

    # Enregistre le schéma personnalisé dans l'application
    app.openapi_schema = openapi_schema

    # Retourne le schéma final
    return app.openapi_schema


app.openapi = custom_openapi


# Inclure les routes API
from app.api.auth_routes import router as auth_routes
from app.api.media_routes import router as media_routes
from app.api.user_routes import router as user_routes
from app.api.privilege_routes import router as privilege_routes
from app.api.role_routes import router as role_routes
from app.api.role_routes import router as role_routes
from app.api.privilege_role_routes import router as privilege_role_routes
from app.api.privilege_user_routes import router as privilege_user_routes
from app.api.user_role_routes import router as user_role_routes
from app.api.country_routes import router as country_routes
from app.api.town_routes import router as town_routes
from app.api.category_article_routes import router as category_article_routes
from app.api.article_state_routes import router as article_state_routes
from app.api.subscription_type_routes import router as subscription_type_routes
from app.api.subscription_routes import router as subscription_routes
from app.api.tax_interval_routes import router as tax_interval_routes
from app.api.sliding_scale_tariffs_routes import router as sliding_scale_tariffs_routes
from app.api.volume_discounts_routes import router as volume_discounts_routes

app.include_router(auth_routes)
app.include_router(media_routes)
app.include_router(user_routes)
app.include_router(privilege_routes)
app.include_router(role_routes)
app.include_router(privilege_role_routes)
app.include_router(privilege_user_routes)
app.include_router(user_role_routes)
app.include_router(country_routes)
app.include_router(town_routes)
app.include_router(category_article_routes)
app.include_router(article_state_routes)
app.include_router(subscription_type_routes)
app.include_router(subscription_routes)
app.include_router(tax_interval_routes)
app.include_router(sliding_scale_tariffs_routes)
app.include_router(volume_discounts_routes)



# Endpoint racine
@app.get("/")
def welcome(db: Session = Depends(get_db)):
    """
    Endpoint racine pour initialiser les données de base (pays et ville).
    """
    def initialize_country_and_town():
        country_init = "cameroun"
        town_init = "douala"
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        country_uuid = str(uuid.uuid4())
        town_uuid = str(uuid.uuid4())
        NUM_REF = 10001
        codefin = datetime.now().strftime("%m/%Y")
        concatenated_num_ref = f"{NUM_REF + len(db.query(Town).filter(Town.refnumber.endswith(codefin)).all())}/{codefin}"
        author = "Initial Migration"
        return country_uuid, town_uuid, country_init, town_init, formatted_date, concatenated_num_ref, author

    country_query = db.query(Country).first()
    if not country_query:
        (
            country_uuid,
            town_uuid,
            country_init,
            town_init,
            formatted_date,
            concatenated_num_ref,
            author,
        ) = initialize_country_and_town()

        new_country = Country(
            id=country_uuid,
            name=country_init,
            refnumber=concatenated_num_ref,
            created_at=formatted_date,
            updated_at=formatted_date,
            created_by=author,
        )

        new_town = Town(
            id=town_uuid,
            name=town_init,
            country_id=country_uuid,
            refnumber=concatenated_num_ref,
            created_at=formatted_date,
            updated_at=formatted_date,
            created_by=author,
        )

        try:
            db.add(new_country)
            db.add(new_town)
            db.commit()
            db.refresh(new_country)
            db.refresh(new_town)
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de l'initialisation des données : {e}")
            raise HTTPException(status_code=500, detail="Une erreur est survenue lors de l'initialisation des données.")

    return {"message": "Bienvenue sur notre API b_to_b!"}

# Exécution de l'application avec Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )