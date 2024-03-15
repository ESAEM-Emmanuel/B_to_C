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

# Get all towns requests
@router.get("/get_all_actif/", response_model=List[towns_schemas.TownListing])
async def read_towns_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    # towns_queries = db.query(models.Town).filter(models.Town.active == "True" ).order_by(models.Town.name).offset(skip).limit(limit).all()
    # Récupérez les villes du pays
    towns_queries = db.query(models.Town).filter(models.Town.active == "True").order_by(models.Town.name).join(models.Country).filter(models.Country.id == models.Town.country_id).group_by(models.Town.id).limit(limit).offset(skip).all()
    
    # pas de town
    # if not towns_queries:
    #     raise HTTPException(status_code=404, detail="town not found")
                        
    return jsonable_encoder(towns_queries)



# Get an town
# "/get_town_impersonal/?refnumber=value_refnumber&phone=valeur_phone&email=valeur_email&townname=valeur_townname" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_town_by_attribute/", status_code=status.HTTP_200_OK, response_model=List[towns_schemas.TownListing])
async def detail_town_by_attribute(refnumber: Optional[str] = None, country_id: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    town_query = {} # objet vide
    if refnumber is not None :
        town_query = db.query(models.Town).filter(models.Town.refnumber == refnumber, models.Town.active == "True").order_by(models.Town.name).offset(skip).limit(limit).all()
    if name is not None :
        town_query = db.query(models.Town).filter(models.Town.name.contains(name), models.Town.active == "True").order_by(models.Town.name).offset(skip).limit(limit).all()
    if country_id is not None :
        town_query = db.query(models.Town).filter(models.Town.country_id == country_id, models.Town.active == "True").order_by(models.Town.name).offset(skip).limit(limit).all()
    
    
    if not town_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town does not exist")
    return jsonable_encoder(town_query)

# Get an town
@router.get("/get/{town_id}", status_code=status.HTTP_200_OK, response_model=towns_schemas.TownDetail)
async def detail_town(town_id: str, db: Session = Depends(get_db)):
    town_query = db.query(models.Town).filter(models.Town.id == town_id).first()
    if not town_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {town_id} does not exist")
    
    owners = town_query.owners
    details = [{ 'id': owner.id, 'refnumber': owner.refnumber, 'phone': owner.phone, 'town_id': owner.town_id, 'username': owner.username, 'email': owner.email, 'birthday': owner.birthday, 'gender': owner.gender, 'active': owner.active} for owner in owners]
    owners = details
    
    return jsonable_encoder(town_query)





# update an town request
@router.put("/update/{town_id}", status_code=status.HTTP_200_OK, response_model = towns_schemas.TownDetail)
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
    owners = town_query.owners
    details = [{ 'id': owner.id, 'refnumber': owner.refnumber, 'phone': owner.phone, 'town_id': owner.town_id, 'username': owner.username, 'email': owner.email, 'birthday': owner.birthday, 'gender': owner.gender, 'active': owner.active} for owner in owners]
    owners = details
        
    return jsonable_encoder(town_query)


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


# Get all town inactive requests
@router.get("/get_all_inactive/", response_model=List[towns_schemas.TownListing])
async def read_towns_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    towns_queries = db.query(models.Town).filter(models.Town.active == "False").order_by(models.Town.name).offset(skip).limit(limit).all()
                      
    return jsonable_encoder(towns_queries)


# Restore town
@router.patch("/restore/{town_id}", status_code = status.HTTP_200_OK,response_model = towns_schemas.TownListing)
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
    
    return jsonable_encoder(town_query)
