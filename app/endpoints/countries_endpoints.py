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

        serialized_countries = [countries_schemas.CountryListing.from_orm(country) for country in countries]

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
    query: Optional[str] = None,
    active: Optional[bool] = None,
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        country_query = db.query(models.Country)

        # Filtrer par nom si fourni
        if query:
            country_query = country_query.filter(models.Country.name.contains(query.lower()))

        # Filtrer par statut actif/inactif
        if active is not None:
            country_query = country_query.filter(models.Country.active == active)
            
        towns = country_query.towns
        details = [{ 'id': town.id, 'refnumber': town.refnumber, 'name': town.name, 'country_id': town.country_id, 'active': town.active} for town in towns]
        towns = details

        # Pagination
        total_countries = country_query.count()
        countries = country_query.order_by(models.Country.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_countries / limit) if limit > 0 else 1

        serialized_countries = [countries_schemas.CountryListing.from_orm(country) for country in countries]

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
    country_query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "True").first()
    if not country_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
    
    towns = country_query.towns
    details = [{ 'id': town.id, 'refnumber': town.refnumber, 'name': town.name, 'country_id': town.country_id, 'active': town.active} for town in towns]
    towns = details
    
    return jsonable_encoder(country_query)


# update an country request
@router.put("/{country_id}", status_code=status.HTTP_200_OK, response_model = countries_schemas.CountryDetail)
async def update_country(country_id: str, country_update: countries_schemas.CountryUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    country_query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "True").first()

    if not country_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
    else:
        
        country_query.updated_by =  current_user.id
        
        if country_update.name:
            country_query.name = country_update.name
         
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(country_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    towns = country_query.towns
    details = [{ 'id': town.id, 'refnumber': town.refnumber, 'name': town.name, 'country_id': town.country_id, 'active': town.active} for town in towns]
    towns = details    
    return jsonable_encoder(country_query)


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


# Get all country inactive requests
@router.get("/get_all_inactive/", response_model=List[countries_schemas.CountryListing])
async def read_countrys_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    countries_queries = db.query(models.Country).filter(models.Country.active == "False").order_by(models.Country.name).offset(skip).limit(limit).all()
                     
    return jsonable_encoder(countries_queries)


# Restore permission
@router.patch("/restore/{country_id}", status_code = status.HTTP_200_OK,response_model = countries_schemas.CountryListing)
async def restore_country(country_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    country_query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "False").first()
    
    if not country_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
        
    country_query.active = True
    country_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(country_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(country_query)
