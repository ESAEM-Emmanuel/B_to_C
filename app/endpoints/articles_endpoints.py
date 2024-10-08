import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import articles_schemas
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

# /articles/

router = APIRouter(prefix = "/article", tags=['Articles Requests'])
 
# create a new article sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=articles_schemas.ArticleListing)
async def create_article(new_article_c: articles_schemas.ArticleCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    # article_query = db.query(models.Article).filter(models.Article.name == new_article_c.name, models.Article.type_article_id == new_article_c.type_article_id).first()
    # if  article_query:
    #     raise HTTPException(status_code=403, detail="This association article, type article also exists !")
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.Article).filter(models.Article.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    owner_id = current_user.id
    
    new_article= models.Article(id = concatenated_uuid, **new_article_c.dict(), refnumber = concatenated_num_ref, owner_id = owner_id)
    
    try:
        db.add(new_article )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_article)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_article)

# Get all articles requests
@router.get("/get_all/", response_model=List[articles_schemas.ArticleListing])
async def read_articles_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    articles_queries = db.query(models.Article).filter(models.Article.active == "True", models.Article.publish == "True", models.Article.locked == "False").order_by(models.Article.name).offset(skip).limit(limit).all()
    print(current_user.is_staff)
    if current_user.is_staff ==True:
        articles_queries = db.query(models.Article).order_by(models.Article.name).offset(skip).limit(limit).all()                   
    return jsonable_encoder(articles_queries)

# Get all articles requests
@router.get("/get_all_actif/", response_model=List[articles_schemas.ArticleListing])
async def read_articles_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    articles_queries = db.query(models.Article).filter(models.Article.active == "True", models.Article.publish == "True", models.Article.locked == "False").order_by(models.Article.name).offset(skip).limit(limit).all()                   
    return jsonable_encoder(articles_queries)



# Get an article
# "/get_article_impersonal/?refnumber=value_refnumber&phone=valeur_phone&email=valeur_email&articlename=valeur_articlename" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_article_by_attribute/", status_code=status.HTTP_200_OK, response_model=List[articles_schemas.ArticleListing])
async def detail_article_by_attribute(refnumber: Optional[str] = None, town_id: Optional[str] = None, category_article_id: Optional[str] = None, article_statu_id: Optional[str] = None, end_date: Optional[str] = None, image_principal: Optional[str] = None, publish: Optional[str] = None, locked: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    article_query = {} # objet vide
    if refnumber is not None :
        article_query = db.query(models.Article).filter(models.Article.refnumber == refnumber, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if name is not None :
        article_query = db.query(models.Article).filter(models.Article.name.contains(name), models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if town_id is not None :
        article_query = db.query(models.Article).filter(models.Article.name.contains(town_id), models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if category_article_id is not None :
        article_query = db.query(models.Article).filter(models.Article.category_article_id == category_article_id, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if article_statu_id is not None :
        article_query = db.query(models.Article).filter(models.Article.article_statu_id == article_statu_id, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if description is not None:
        article_query = db.query(models.Article).filter(models.Article.description.contains(description), models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if end_date is not None :
        article_query = db.query(models.Article).filter(models.Article.end_date == end_date, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if image_principal is not None :
        article_query = db.query(models.Article).filter(models.Article.image_principal == image_principal, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if publish is not None :
        article_query = db.query(models.Article).filter(models.Article.publish == publish, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if locked is not None :
        article_query = db.query(models.Article).filter(models.Article.locked == locked, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    if price is not None :
        article_query = db.query(models.Article).filter(models.Article.price == price, models.Article.active == "True").order_by(models.Article.name).offset(skip).limit(limit).all()
    
    return jsonable_encoder(article_query)

# Get an article
@router.get("/get/{article_id}", status_code=status.HTTP_200_OK, response_model=articles_schemas.ArticleDetail)
async def detail_article(article_id: str, db: Session = Depends(get_db)):
    article_query = db.query(models.Article).filter(models.Article.id == article_id, models.Article.active == "True").first()
    if not article_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
    
    article_query = db.query(models.Article).filter(models.Article.id == article_id).first()
    
    article_multimedias = article_query.article_multimedias
    details = [{ 'id': article_multimedia.id, 'refnumber': article_multimedia.refnumber, 'link_media': article_multimedia.link_media, 'article_id': article_multimedia.article_id, 'active': article_multimedia.active} for article_multimedia in article_multimedias]
    article_multimedias = details
    
    signals = article_query.signals
    details = [{ 'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 'article_id': signal.article_id, 'description': signal.description, 'active': signal.active} for signal in signals]
    signals = details
        
    return jsonable_encoder(article_query)



# update an permission request
@router.put("/update/{article_id}", status_code=status.HTTP_200_OK, response_model = articles_schemas.ArticleDetail)
async def update_article(article_id: str, article_update: articles_schemas.ArticleUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    article_query = db.query(models.Article).filter(models.Article.id == article_id).first()

    if not article_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
    else:
        
        article_query.updated_by =  current_user.id
        
        if article_update.name:
            article_query.name = article_update.name
        if article_update.town_id:
            article_query.town_id = article_update.town_id
        if article_update.reception_place:
            article_query.reception_place = article_update.reception_place
        if article_update.owner_id:
            article_query.owner_id = article_update.owner_id
        if article_update.category_article_id:
            article_query.category_article_id = article_update.category_article_id
        if article_update.article_statu_id:
            article_query.article_statu_id = article_update.article_statu_id
        if article_update.description:
            article_query.description = article_update.description
        if article_update.image_principal:
            article_query.image_principal = article_update.image_principal
        if article_update.price:
            article_query.price = article_update.price
        if article_update.publish:
            article_query.publish = article_update.publish
        if article_update.locked:
            article_query.locked = article_update.locked
            
    
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(article_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    article_query = db.query(models.Article).filter(models.Article.id == article_id).first()
    article_multimedias = article_query.article_multimedias
    details = [{ 'id': article_multimedia.id, 'refnumber': article_multimedia.refnumber, 'link_media': article_multimedia.link_media, 'article_id': article_multimedia.article_id, 'active': article_multimedia.active} for article_multimedia in article_multimedias]
    article_multimedias = details
    
    signals = article_query.signals
    details = [{ 'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 'article_id': signal.article_id, 'description': signal.description, 'active': signal.active} for signal in signals]
    signals = details
        
    return jsonable_encoder(article_query)


# delete article
@router.patch("/delete/{article_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_query = db.query(models.Article).filter(models.Article.id == article_id, models.Article.active == "True").first()
    
    if not article_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
        
    article_query.active = False
    article_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(article_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return {"message": "article deleted!"}


# Get all article inactive requests
@router.get("/get_all_inactive/", response_model=List[articles_schemas.ArticleListing])
async def read_articles_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    articles_queries = db.query(models.Article).filter(models.Article.active == "False", ).order_by(models.Article.name).offset(skip).limit(limit).all()
                       
    return jsonable_encoder(articles_queries)


# Restore permission
@router.patch("/restore/{article_id}", status_code = status.HTTP_200_OK,response_model = articles_schemas.ArticleListing)
async def restore_article(article_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    article_query = db.query(models.Article).filter(models.Article.id == article_id, models.Article.active == "False").first()
    
    if not article_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
        
    article_query.active = True
    article_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(article_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return jsonable_encoder(article_query)
