import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import article_miltimedias_schemas
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

# /article_multimedias/

router = APIRouter(prefix = "/article_multimedia", tags=['Articles multimedias Requests'])
 
# create a new article_multimedia sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=article_miltimedias_schemas.ArticleMultimediaListing)
async def create_article_multimedia(new_article_multimedia_c: article_miltimedias_schemas.ArticleMultimediaCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.article_id == new_article_multimedia_c.article_id, models.ArticleMultimedia.link_media == new_article_multimedia_c.link_media).first()
    if  article_multimedia_query:
        raise HTTPException(status_code=403, detail="This article also the same image !")
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    
    new_article_multimedia= models.ArticleMultimedia(id = concatenated_uuid, **new_article_multimedia_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_article_multimedia )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_article_multimedia)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_article_multimedia)

# Get all article_multimedias requests
@router.get("/get_all_actif/", response_model=List[article_miltimedias_schemas.ArticleMultimediaListing])
async def read_article_multimedias_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    article_multimedias_queries = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.active == "True").order_by(models.ArticleMultimedia.created_at).offset(skip).limit(limit).all()
                        
    return jsonable_encoder(article_multimedias_queries)

# Get an article_multimedia
@router.get("/get/{article_multimedia_id}", status_code=status.HTTP_200_OK, response_model=article_miltimedias_schemas.ArticleMultimediaDetail)
async def detail_article_multimedia(article_multimedia_id: str, db: Session = Depends(get_db)):
    article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.id == article_multimedia_id).first()
    if not article_multimedia_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_multimedia with id: {article_multimedia_id} does not exist")
    return jsonable_encoder(article_multimedia_query)

# Get an article_multimedia
# "/get_article_multimedia_impersonal/?refnumber=value_refnumber&phone=valeur_phone&email=valeur_email&article_multimedianame=valeur_article_multimedianame" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_article_multimedia_by_attribute/", status_code=status.HTTP_200_OK, response_model=List[article_miltimedias_schemas.ArticleMultimediaListing])
async def detail_article_multimedia_by_attribute(refnumber: Optional[str] = None, link_media: Optional[str] = None, article_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    article_multimedia_query = {} # objet vide
    if refnumber is not None :
        article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.refnumber == refnumber, models.ArticleMultimedia.active == "True").order_by(models.ArticleMultimedia.created_at).offset(skip).limit(limit).all()
    if link_media is not None :
        article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.link_media.contains(link_media), models.ArticleMultimedia.active == "True").order_by(models.ArticleMultimedia.created_at).offset(skip).limit(limit).all()
    if article_id is not None :
        article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.article_id == article_id, models.ArticleMultimedia.active == "True").order_by(models.ArticleMultimedia.created_at).offset(skip).limit(limit).all()
    
    return jsonable_encoder(article_multimedia_query)



# update an article_multimedia request
@router.put("/update/{article_multimedia_id}", status_code=status.HTTP_200_OK, response_model = article_miltimedias_schemas.ArticleMultimediaDetail)
async def update_article_multimedia(article_multimedia_id: str, article_multimedia_update: article_miltimedias_schemas.ArticleMultimediaUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.id == article_multimedia_id, models.ArticleMultimedia.active == "True").first()

    if not article_multimedia_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_multimedia with id: {article_multimedia_id} does not exist")
    else:
        
        article_multimedia_query.updated_by =  current_user.id
        
        if article_multimedia_update.link_media:
            article_multimedia_query.link_media = article_multimedia_update.link_media
        if article_multimedia_update.article_id:
            article_multimedia_query.article_id = article_multimedia_update.article_id
        
    
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(article_multimedia_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
        
    return jsonable_encoder(article_multimedia_query)


# delete article_multimedia
@router.patch("/delete/{article_multimedia_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_article_multimedia(article_multimedia_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.id == article_multimedia_id, models.ArticleMultimedia.active == "True").first()
    
    if not article_multimedia_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_multimedia with id: {article_multimedia_id} does not exist")
        
    article_multimedia_query.active = False
    article_multimedia_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(article_multimedia_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return {"message": "article_multimedia deleted!"}


# Get all article_multimedia inactive requests
@router.get("/get_all_inactive/", response_model=List[article_miltimedias_schemas.ArticleMultimediaListing])
async def read_article_multimedias_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_multimedias_queries = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.active == "False", ).offset(skip).limit(limit).all()
                       
    return jsonable_encoder(article_multimedias_queries)


# Restore article_multimedia
@router.patch("/restore/{article_multimedia_id}", status_code = status.HTTP_200_OK,response_model = article_miltimedias_schemas.ArticleMultimediaListing)
async def restore_article_multimedia(article_multimedia_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_multimedia_query = db.query(models.ArticleMultimedia).filter(models.ArticleMultimedia.id == article_multimedia_id, models.ArticleMultimedia.active == "False").first()
    
    if not article_multimedia_query:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_multimedia with id: {article_multimedia_id} does not exist")
        
    article_multimedia_query.active = True
    article_multimedia_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(article_multimedia_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return jsonable_encoder(article_multimedia_query)
