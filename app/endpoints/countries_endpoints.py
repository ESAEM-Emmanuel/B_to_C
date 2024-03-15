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

models.Base.metadata.create_all(bind=engine)

# /countrys/

router = APIRouter(prefix = "/country", tags=['Countrys Requests'])
 
# create a new country sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=countries_schemas.CountryListing)
async def create_country(new_country_c: countries_schemas.CountryCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    country_query = db.query(models.Country).filter(models.Country.name == new_country_c.name).first()
    if  country_query:
        raise HTTPException(status_code=403, detail="This country also existe!")
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.Country).filter(models.Country.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    
    new_country= models.Country(id = concatenated_uuid, **new_country_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_country )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_country)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_country)

# Get all countrys requests
@router.get("/get_all_actif/", response_model=List[countries_schemas.CountryListing])
async def read_countrys_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    countries_queries = db.query(models.Country).filter(models.Country.active == "True").order_by(models.Country.name).offset(skip).limit(limit).all()
                        
    return jsonable_encoder(countries_queries)



# Get an country
# "/get_country_impersonal/?refnumber=value_refnumber&phone=valeur_phone&email=valeur_email&countryname=valeur_countryname" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_country_by_attribute/", status_code=status.HTTP_200_OK, response_model=List[countries_schemas.CountryListing])
async def detail_country_by_attribute(refnumber: Optional[str] = None, name: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    country_query = {} # objet vide
    if refnumber is not None :
        country_query = db.query(models.Country).filter(models.Country.refnumber == refnumber, models.Country.active == "True").order_by(models.Country.name).offset(skip).limit(limit).all()
    if name is not None :
        country_query = db.query(models.Country).filter(models.Country.name.contains(name), models.Country.active == "True" ).order_by(models.Country.name).offset(skip).limit(limit).all()
    
    
    return jsonable_encoder(country_query)

# Get an country
@router.get("/get/{country_id}", status_code=status.HTTP_200_OK, response_model=countries_schemas.CountryDetail)
async def detail_country(country_id: str, db: Session = Depends(get_db)):
    country_query = db.query(models.Country).filter(models.Country.id == country_id, models.Country.active == "True").first()
    if not country_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"country with id: {country_id} does not exist")
    
    towns = country_query.towns
    details = [{ 'id': town.id, 'refnumber': town.refnumber, 'name': town.name, 'country_id': town.country_id, 'active': town.active} for town in towns]
    towns = details
    
    return jsonable_encoder(country_query)


# update an country request
@router.put("/update/{country_id}", status_code=status.HTTP_200_OK, response_model = countries_schemas.CountryDetail)
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
