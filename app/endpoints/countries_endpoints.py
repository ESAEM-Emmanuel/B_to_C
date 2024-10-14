import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import countries_schemas
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

# /countrys/

router = APIRouter(prefix = "/countries", tags=['Countrys Requests'])
 
# create a new country sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=countries_schemas.CountryListing)
async def create_country(new_country_c: countries_schemas.CountryCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    country_query = db.query(models.Country).filter(models.Country.name == new_country_c.name).first()
    if  country_query:
        raise HTTPException(status_code=403, detail="This country also existe!")
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    # concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.Country).filter(models.Country.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    # Convertir le nom en minuscules
    new_country_c.name = new_country_c.name.lower()
    
    new_country= models.Country(id = str(uuid.uuid4()), **new_country_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_country )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_country)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_country)


@router.get("/")
async def get_all_countries(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Country)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.Country.active == active)
            
        if limit ==-1:
            query = query.filter(models.Country.active == active)
            serialized_countries = [countries_schemas.CountryListing.from_orm(country) for country in countries]
            return {
                "countries": jsonable_encoder(serialized_countries)
            }

        total_countries = query.count()  # Nombre total de pays

        # Pagination
        countries = query.order_by(models.Country.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_countries / limit) if limit > 0 else 1
        
        serialized_countries = []
        for country in countries:
            # serialized_countrie = [countries_schemas.CountryListing.from_orm(country) for country in countries]
            serialized_country = countries_schemas.CountryListing.from_orm(country)
            if country.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == country.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {country.created_by} does not exist")
                creator_serialized = countries_schemas.UserInfo.from_orm(creator_query)
                serialized_country.creator = creator_serialized
            if country.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == country.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {country.updated_by} does not exist")
                updator_serialized = countries_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_country.updator = updator_serialized
            serialized_countries.append(serialized_country)

        return {
            "countries": jsonable_encoder(serialized_countries),
            "total_countries": total_countries,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/search/")
async def search_countries(
    name: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    # query: Optional[str] = None,
):
    try:
        query = db.query(models.Country)

        # Filtrer par nom si fourni
        if name:
            query = query.filter(models.Country.name.contains(name.lower()))

        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.Country.active == active)
        
        # Pagination
        total_countries = query.count()
        countries = query.order_by(models.Country.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_countries / limit) if limit > 0 else 1

        serialized_countries = []
        for country in countries:
            # serialized_countrie = [countries_schemas.CountryListing.from_orm(country) for country in countries]
            serialized_country = countries_schemas.CountryListing.from_orm(country)
            if country.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == country.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {country.created_by} does not exist")
                creator_serialized = countries_schemas.UserInfo.from_orm(creator_query)
                serialized_country.creator = creator_serialized
            if country.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == country.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {country.updated_by} does not exist")
                updator_serialized = countries_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_country.updator = updator_serialized
            serialized_countries.append(serialized_country)

        return {
            "countries": jsonable_encoder(serialized_countries),
            "total_countries": total_countries,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get an country
@router.get("/{country_id}", status_code=status.HTTP_200_OK, response_model=countries_schemas.CountryDetail)
async def detail_country(country_id: str, db: Session = Depends(get_db)):
    query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "True").first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {country_id} does not exist")
    
    towns = [{ 'id': town.id,
              'refnumber': town.refnumber,
              'name': town.name,
              'country_id': town.country_id,
              'active': town.active} for town in query.towns]
    serialized_country = countries_schemas.CountryDetail.from_orm(query)
    
    if query.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = countries_schemas.UserInfo.from_orm(creator_query)
        serialized_country.creator = creator_serialized
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = countries_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_country.updator = updator_serialized
    
    return jsonable_encoder(serialized_country)


# update an country request
@router.put("/{country_id}", status_code=status.HTTP_200_OK, response_model = countries_schemas.CountryDetail)
async def update_country(country_id: str, country_update: countries_schemas.CountryUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "True").first()

    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
    else:
        
        query.updated_by =  current_user.id
        
        if country_update.name:
            query.name = country_update.name
         
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    towns = [{ 'id': town.id,
              'refnumber': town.refnumber,
              'name': town.name,
              'country_id': town.country_id,
              'active': town.active} for town in query.towns]
    serialized_country = countries_schemas.CountryDetail.from_orm(query)
    
    if query.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = countries_schemas.UserInfo.from_orm(creator_query)
        serialized_country.creator = creator_serialized
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = countries_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_country.updator = updator_serialized
    
    return jsonable_encoder(serialized_country)


# delete country
@router.patch("/delete/{country_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_country(country_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    country_query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "True").first()
    
    if not country_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
        
    country_query.active = False
    country_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(country_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return {"message": "country deleted!"}

# Restore permission
@router.patch("/restore/{country_id}", status_code = status.HTTP_200_OK,response_model = countries_schemas.CountryDetail)
async def restore_country(country_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "False").first()
    
    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
        
    query.active = True
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    towns = [{ 'id': town.id,
              'refnumber': town.refnumber,
              'name': town.name,
              'country_id': town.country_id,
              'active': town.active} for town in query.towns]
    serialized_country = countries_schemas.CountryDetail.from_orm(query)
    
    if query.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = countries_schemas.UserInfo.from_orm(creator_query)
        serialized_country.creator = creator_serialized
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = countries_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_country.updator = updator_serialized
    
    return jsonable_encoder(serialized_country)
