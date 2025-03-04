from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()
from app import config_sething
import logging
from fastapi.staticfiles import StaticFiles

# DATABASE_URL = os.getenv("DATABASE_URL")
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import models
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from app.endpoints.auths_endpoints import router as auths_endpoints_routers
from app.endpoints.users_endpoints import router as users_routers
from app.endpoints.medias_endpoints import router as medias_routers

from app.endpoints.countries_endpoints import router as countries_routers
from app.endpoints.towns_endpoints import router as towns_routers
from app.endpoints.category_articles_endpoints import router as category_articles_routers
from app.endpoints.article_status_endpoints import router as article_status_endpoints_routers
from app.endpoints.articles_endpoints import router as articles_routers
from app.endpoints.signals_endpoints import router as signals_routers

logging.basicConfig(level=logging.INFO)  # Niveau de journalisation souhaité, par exemple INFO

# FastAPI config_sethinguration

if config_sething.debug == "True":
    app = FastAPI(title=config_sething.project_name,version=config_sething.project_version)
else:
    app = FastAPI(title=config_sething.project_name,version=config_sething.project_version, docs_url = None)
       
#     return {"message": "Thank you for visiting our b_to_b API!"}
@app.get("/")
def welcome(db: Session = Depends(get_db)):
    # Fonction pour initialiser le pays et la ville
    def initialize_country_and_town():
        country_init = "cameroun"
        town_init = "douala"
        formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        country_uuid = str(uuid.uuid4())  # UUID pour le pays
        town_uuid = str(uuid.uuid4())     # UUID pour la ville
        NUM_REF = 10001
        codefin = datetime.now().strftime("%m/%Y")
        concatenated_num_ref = str(NUM_REF + len(db.query(models.Town).filter(models.Town.refnumber.endswith(codefin)).all())) + "/" + codefin
        author = "initial migration"
        return country_uuid, town_uuid, country_init, town_init, formated_date, concatenated_num_ref, author

    country_query = db.query(models.Country).first()
    print("country_query: ", country_query)

    if not country_query:
        # Appeler la fonction pour obtenir les valeurs
        concatenated_uuid, town_uuid, country_init, town_init, formated_date, concatenated_num_ref, author = initialize_country_and_town()
        print("data: ", concatenated_uuid, country_init, town_init, formated_date, concatenated_num_ref, author)

        # Ajouter le nouveau pays
        new_country = models.Country(id=concatenated_uuid, name=country_init, refnumber=concatenated_num_ref)
        
        try:
            # Ajouter le nouveau pays à la base de données
            db.add(new_country)
            print("new_country",new_country.__dict__)

            # Ajouter la nouvelle ville
            new_town = models.Town(id=town_uuid, name=town_init, country_id=concatenated_uuid, refnumber=concatenated_num_ref)
            db.add(new_town)
            print("new_town",new_town.__dict__)

            # Commit une seule fois
            db.commit()
            
            # Actualiser les objets ajoutés
            db.refresh(new_country)
            db.refresh(new_town)

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=403, detail="Something went wrong in the process, please try again later!")
        
    return {"message": "Thank you for visiting our b_to_b API!"}

# Routes for multiple applications should be added to the main file.

# Ajout du chemin pour les fichiers médias statiques
app.mount("/static", StaticFiles(directory="medias"), name="static")

app.include_router(auths_endpoints_routers)
app.include_router(medias_routers)

app.include_router(countries_routers)
app.include_router(towns_routers)
app.include_router(users_routers)
app.include_router(category_articles_routers)
app.include_router(article_status_endpoints_routers)
app.include_router(articles_routers)
app.include_router(signals_routers)


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=config_sething.allow_methods,
    allow_headers=config_sething.allow_headers,
)
logging.info("Message de journalisation")

# Exécutez l'application avec uvicorn
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="172.19.120.188", port=8000)
    uvicorn.run("main:app", host=config_sething.server_host, port=config_sething.server_port, reload=True)
    # uvicorn.run("main:app", host="172.19.120.188", port=8000, reload=True)
    # la commande de lancement est : python main.py