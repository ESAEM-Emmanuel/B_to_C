import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import article_status_schemas
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


# /article_statuss/

router = APIRouter(prefix = "/article_status", tags=['Article status Requests'])
 
# create a new type articles status sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=article_status_schemas.ArticleStatusListing)
async def create_article_status(new_article_status_c: article_status_schemas.ArticleStatusCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.name == new_article_status_c.name).first()
    if  article_status_query:
        raise HTTPException(status_code=403, detail="This type articles status also exists !")
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.ArticleStatus).filter(models.ArticleStatus.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    
    new_article_status= models.ArticleStatus(id = concatenated_uuid, **new_article_status_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_article_status )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_article_status)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_article_status)

# Get all type articles statuss requests
@router.get("/get_all_actif/", response_model=List[article_status_schemas.ArticleStatusListing])
async def read_article_status_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    article_status_queries = db.query(models.ArticleStatus).filter(models.ArticleStatus.active == "True").order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()
    
                        
    return jsonable_encoder(article_status_queries)


# Get an article_status
@router.get("/get/{article_status_id}", status_code=status.HTTP_200_OK, response_model=article_status_schemas.ArticleStatusDetail)
async def detail_article_status(article_status_id: str, db: Session = Depends(get_db)):
    article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id, models.ArticleStatus.active == "True").first()
    if not article_status_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_status with id: {article_status_id} does not exist")
    
    articles = article_status_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
    
    return jsonable_encoder(article_status_query)




# Get an article_status
# "/get_article_status_impersonal/?name=value_name&description=valeur_description" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_article_status_by_attribute/", status_code=status.HTTP_200_OK, response_model=List[article_status_schemas.ArticleStatusListing])
async def detail_article_status_by_attribute(name: Optional[str] = None, description: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    article_status_query = {} # objet vide
    if name is not None :
        article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.name.contains(name), models.ArticleStatus.active == "True").order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()
    if description is not None :
        article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.description.contains(description), models.ArticleStatus.active == "True").order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()
       
    return jsonable_encoder(article_status_query)



# update an type articles status request
@router.put("/update/{article_status_id}", status_code=status.HTTP_200_OK, response_model = article_status_schemas.ArticleStatusDetail)
async def update_article_status(article_status_id: str, article_status_update: article_status_schemas.ArticleStatusUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id).first()

    if not article_status_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_status with id: {article_status_id} does not exist")
    else:
        
        article_status_query.updated_by =  current_user.id
        
        if article_status_update.name:
            article_status_query.name = article_status_update.name
        if article_status_update.description:
            article_status_query.description = article_status_update.description
        
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(article_status_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id).first()
    articles = article_status_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
       
    return jsonable_encoder(article_status_query)


# delete type articles status
@router.patch("/delete/{article_status_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_article_status(article_status_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id, models.ArticleStatus.active == "True").first()
    
    if not article_status_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"family card with id: {article_status_id} does not exist")
        
    article_status_query.active = False
    article_status_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(article_status_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return {"message": "status article deleted!"}


# Get all article_status inactive requests
@router.get("/get_all_inactive/", response_model=List[article_status_schemas.ArticleStatusListing])
async def read_article_statuss_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_status_queries = db.query(models.ArticleStatus).filter(models.ArticleStatus.active == "False", ).order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()
                        
    return jsonable_encoder(article_status_queries)


# Restore article_status
@router.patch("/restore/{article_status_id}", status_code = status.HTTP_200_OK,response_model = article_status_schemas.ArticleStatusListing)
async def restore_article_status(article_status_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_status_query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id, models.ArticleStatus.active == "False").first()
    
    if not article_status_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_status with id: {article_status_id} does not exist")
        
    article_status_query.active = True
    article_status_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(article_status_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return jsonable_encoder(article_status_query)
