import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import towns_schemas
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.models import models
import uuid
from datetime import datetime, timedelta
from app.database import engine, get_db
from typing import Optional
from  utils import oauth2
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from math import ceil

models.Base.metadata.create_all(bind=engine)

# /towns/

router = APIRouter(prefix = "/town", tags=['Towns Requests'])
 
# create a new town sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=towns_schemas.TownListing)
async def create_town(new_town_c: towns_schemas.TownCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    town_query = db.query(models.Town).filter(models.Town.name == new_town_c.name, models.Town.country_id == new_town_c.country_id).first()
    if  town_query:
        raise HTTPException(status_code=403, detail="This Town also existe!")
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.Town).filter(models.Town.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    
    new_town= models.Town(id = concatenated_uuid, **new_town_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_town )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_town)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_town)


@router.get("/")
async def get_all_town(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Town)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.Town.active == active)

        total_towns = query.count()  # Nombre total de villes

        if limit > 0:
            towns = query.order_by(models.Town.name).offset(skip).limit(limit).all()
        else:
            towns = query.order_by(models.Town.name).all()

        total_pages = ceil(total_towns / limit) if limit > 0 else 1

        # Récupérer les informations sur le pays via une jointure
        serialized_towns = []
        for town in towns:
            # Utiliser la jointure pour éviter plusieurs requêtes
            country = db.query(models.Country).filter(models.Country.id == town.country_id).first()

            if country:
                country_serialized = towns_schemas.CountryList.from_orm(country)
                town_serialized = towns_schemas.TownListing.from_orm(town)
                town_serialized.country = country_serialized
                serialized_towns.append(town_serialized)

        return {
            "towns": jsonable_encoder(serialized_towns),
            "total_towns": total_towns,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.get("/search/")
async def search_towns(
    name: Optional[str] = None,
    country_id: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        # Construction de la requête
        query = db.query(models.Town)

        # Filtrer par nom si fourni
        if name:
            query = query.filter(models.Town.name.ilike(f"%{name.lower()}%"))

        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.Town.active == active)

        # Filtrer par pays si fourni
        if country_id is not None:
            query = query.filter(models.Town.country_id == country_id)

        # Pagination
        total_towns = query.count()

        if limit > 0:
            towns = query.order_by(models.Town.name).offset(skip).limit(limit).all()
        else:
            towns = query.order_by(models.Town.name).all()

        total_pages = ceil(total_towns / limit) if limit > 0 else 1

        # Récupérer les informations sur le pays via une jointure
        serialized_towns = []
        for town in towns:
            # Utiliser la jointure pour éviter plusieurs requêtes
            country = db.query(models.Country).filter(models.Country.id == town.country_id).first()

            if country:
                country_serialized = towns_schemas.CountryList.from_orm(country)
                town_serialized = towns_schemas.TownListing.from_orm(town)
                town_serialized.country = country_serialized
                serialized_towns.append(town_serialized)

        return {
            "towns": jsonable_encoder(serialized_towns),
            "total_towns": total_towns,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get a town with country details
@router.get("/{town_id}", status_code=status.HTTP_200_OK, response_model=towns_schemas.TownDetail)
async def detail_town(town_id: str, db: Session = Depends(get_db)):
    town_query = db.query(models.Town).filter(models.Town.id == town_id).first()
    if not town_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {town_id} does not exist")

    # Récupération des informations des propriétaires
    owners_details = [{ 
        'id': owner.id, 
        'refnumber': owner.refnumber, 
        'phone': owner.phone, 
        'town_id': owner.town_id, 
        'username': owner.username, 
        'email': owner.email, 
        'birthday': owner.birthday, 
        'gender': owner.gender, 
        'active': owner.active 
    } for owner in town_query.owners]

    # Récupération des informations des articles
    articles_details = [{ 
        'id': article.id, 
        'refnumber': article.refnumber, 
        'name': article.name, 
        'reception_place': article.reception_place,  
        'category_article_id': article.category_article_id, 
        'article_statu_id': article.article_statu_id, 
        'description': article.description, 
        'end_date': article.end_date, 
        'price': article.price, 
        'image_principal': article.image_principal, 
        'owner_id': article.owner_id, 
        'publish': article.publish, 
        'locked': article.locked, 
        'active': article.active 
    } for article in town_query.articles]

    # Récupération des détails du pays
    country_query = db.query(models.Country).filter(models.Country.id == town_query.country_id).first()
    if not country_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {town_query.country_id} does not exist")

    # Sérialisation du pays
    country = towns_schemas.CountryList.from_orm(country_query)

    # Construction de la réponse
    serialized_town = towns_schemas.TownDetail.from_orm(town_query)
    serialized_town.country = country
    return jsonable_encoder(serialized_town)


# update an town request
@router.put("/{town_id}", status_code=status.HTTP_200_OK, response_model = towns_schemas.TownDetail)
async def update_town(town_id: str, town_update: towns_schemas.TownUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    town_query = db.query(models.Town).filter(models.Town.id == town_id).first()

    if not town_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {town_id} does not exist")
    else:
        
        town_query.updated_by =  current_user.id
        
        if town_update.name:
            town_query.name = town_update.name
        if town_update.country_id:
            town_query.country_id = town_update.country_id
    
    
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(town_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    town_query = db.query(models.Town).filter(models.Town.id == town_id).first()    
    # Récupération des informations des propriétaires
    owners_details = [{ 
        'id': owner.id, 
        'refnumber': owner.refnumber, 
        'phone': owner.phone, 
        'town_id': owner.town_id, 
        'username': owner.username, 
        'email': owner.email, 
        'birthday': owner.birthday, 
        'gender': owner.gender, 
        'active': owner.active 
    } for owner in town_query.owners]

    # Récupération des informations des articles
    articles_details = [{ 
        'id': article.id, 
        'refnumber': article.refnumber, 
        'name': article.name, 
        'reception_place': article.reception_place,  
        'category_article_id': article.category_article_id, 
        'article_statu_id': article.article_statu_id, 
        'description': article.description, 
        'end_date': article.end_date, 
        'price': article.price, 
        'image_principal': article.image_principal, 
        'owner_id': article.owner_id, 
        'publish': article.publish, 
        'locked': article.locked, 
        'active': article.active 
    } for article in town_query.articles]

    # Récupération des détails du pays
    country_query = db.query(models.Country).filter(models.Country.id == town_query.country_id).first()
    if not country_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {town_query.country_id} does not exist")

    print("country_query :", country_query.__dict__)
    
    # Sérialisation du pays
    country = towns_schemas.CountryList.from_orm(country_query)
    # Construction de la réponse
    serialized_town = towns_schemas.TownDetail.from_orm(town_query)
    serialized_town.country = country
    return jsonable_encoder(serialized_town)


# delete permission
@router.patch("/delete/{town_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_town(town_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    town_query = db.query(models.Town).filter(models.Town.id == town_id, models.Town.active == "True").first()
    
    if not town_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {town_id} does not exist")
        
    town_query.active = False
    town_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(town_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return {"message": "town deleted!"}

# Restore town
@router.patch("/restore/{town_id}", status_code = status.HTTP_200_OK,response_model = towns_schemas.TownDetail)
async def restore_town(town_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    town_query = db.query(models.Town).filter(models.Town.id == town_id, models.Town.active == "False").first()
    
    if not town_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {town_id} does not exist")
        
    town_query.active = True
    town_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(town_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    town_query = db.query(models.Town).filter(models.Town.id == town_id).first()    
    # Récupération des informations des propriétaires
    owners_details = [{ 
        'id': owner.id, 
        'refnumber': owner.refnumber, 
        'phone': owner.phone, 
        'town_id': owner.town_id, 
        'username': owner.username, 
        'email': owner.email, 
        'birthday': owner.birthday, 
        'gender': owner.gender, 
        'active': owner.active 
    } for owner in town_query.owners]

    # Récupération des informations des articles
    articles_details = [{ 
        'id': article.id, 
        'refnumber': article.refnumber, 
        'name': article.name, 
        'reception_place': article.reception_place,  
        'category_article_id': article.category_article_id, 
        'article_statu_id': article.article_statu_id, 
        'description': article.description, 
        'end_date': article.end_date, 
        'price': article.price, 
        'image_principal': article.image_principal, 
        'owner_id': article.owner_id, 
        'publish': article.publish, 
        'locked': article.locked, 
        'active': article.active 
    } for article in town_query.articles]

    # Récupération des détails du pays
    country_query = db.query(models.Country).filter(models.Country.id == town_query.country_id).first()
    if not country_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {town_query.country_id} does not exist")

    print("country_query :", country_query.__dict__)
    
    # Sérialisation du pays
    country = towns_schemas.CountryList.from_orm(country_query)

    # Construction de la réponse
    serialized_town = towns_schemas.TownDetail.from_orm(town_query)
    serialized_town.country = country
    return jsonable_encoder(serialized_town)
