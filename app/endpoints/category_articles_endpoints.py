import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import category_aticles_schemas
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


# /categorys/

router = APIRouter(prefix = "/category_artile", tags=['Category article Requests'])
 
# create a new type product sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=category_aticles_schemas.CategoryArticleListing)
async def create_category(new_category_c: category_aticles_schemas.CategoryArticleCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.name == new_category_c.name).first()
    if  category_query:
        raise HTTPException(status_code=403, detail="This type product also exists !")
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.CategoryArticle).filter(models.CategoryArticle.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    
    new_category_= models.CategoryArticle(id = concatenated_uuid, **new_category_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_category_ )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_category_)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_category_)

# Get all type products requests
@router.get("/get_all_actif/", response_model=List[category_aticles_schemas.CategoryArticleListing])
async def read_category_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    categorys_queries = db.query(models.CategoryArticle).filter(models.CategoryArticle.active == "True").order_by(models.CategoryArticle.name).offset(skip).limit(limit).all()
    
                        
    return jsonable_encoder(categorys_queries)


# Get an category
@router.get("/get/{category_id}", status_code=status.HTTP_200_OK, response_model=category_aticles_schemas.CategoryArticleDetail)
async def detail_category(category_id: str, db: Session = Depends(get_db)):
    category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id, models.CategoryArticle.active == "True").first()
    if not category_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"category with id: {category_id} does not exist")
    
    articles = category_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
    
    return jsonable_encoder(category_query)




# Get an category
# "/get_category_impersonal/?name=value_name&description=valeur_description" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_category_by_attribute/", status_code=status.HTTP_200_OK, response_model=List[category_aticles_schemas.CategoryArticleListing])
async def detail_category_by_attribute(name: Optional[str] = None, description: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    category_query = {} # objet vide
    if name is not None :
        category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.name.contains(name), models.CategoryArticle.active == "True").order_by(models.CategoryArticle.name).offset(skip).limit(limit).all()
    if description is not None :
        category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.description.contains(description), models.CategoryArticle.active == "True").order_by(models.CategoryArticle.name).offset(skip).limit(limit).all()
       
    return jsonable_encoder(category_query)



# update an type product request
@router.put("/update/{category_id}", status_code=status.HTTP_200_OK, response_model = category_aticles_schemas.CategoryArticleDetail)
async def update_category(category_id: str, category_update: category_aticles_schemas.CategoryArticleUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id).first()

    if not category_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"category with id: {category_id} does not exist")
    else:
        
        category_query.updated_by =  current_user.id
        
        if category_update.name:
            category_query.name = category_update.name
        if category_update.description:
            category_query.description = category_update.description
        if category_update.image:
            category_query.image = category_update.image
        
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(category_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id).first()
    articles = category_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
       
    return jsonable_encoder(category_query)


# delete type product
@router.patch("/delete/{category_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id, models.CategoryArticle.active == "True").first()
    
    if not category_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"family card with id: {category_id} does not exist")
        
    category_query.active = False
    category_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(category_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return {"message": "family card deleted!"}


# Get all category inactive requests
@router.get("/get_all_inactive/", response_model=List[category_aticles_schemas.CategoryArticleListing])
async def read_categorys_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    categorys_queries = db.query(models.CategoryArticle).filter(models.CategoryArticle.active == "False", ).order_by(models.CategoryArticle.name).offset(skip).limit(limit).all()
                      
    return jsonable_encoder(categorys_queries)


# Restore category
@router.patch("/restore/{category_id}", status_code = status.HTTP_200_OK,response_model = category_aticles_schemas.CategoryArticleListing)
async def restore_category(category_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    category_query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id, models.CategoryArticle.active == "False").first()
    
    if not category_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"category with id: {category_id} does not exist")
        
    category_query.active = True
    category_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(category_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return jsonable_encoder(category_query)
