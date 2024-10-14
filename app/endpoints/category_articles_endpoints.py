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
    # concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.CategoryArticle).filter(models.CategoryArticle.refnumber.endswith(codefin)).all())) + "/" + codefin
    new_category_c.name = new_category_c.name.lower()
    new_category_c.description = new_category_c.description.lower()
    author = current_user.id
    
    new_category_= models.CategoryArticle(id = str(uuid.uuid4()), **new_category_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_category_ )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_category_)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_category_)

# Get all type products requests

@router.get("/")
async def get_all_category_articles(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.CategoryArticle)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.CategoryArticle.active == active)
            
        if limit ==-1:
            query = query.filter(models.CategoryArticle.active == active)
            serialized_category_articles = [category_aticles_schemas.CategoryArticleListing.from_orm(country) for country in category_articles]
            return {
                "category_articles": jsonable_encoder(serialized_category_articles)
            }

        total_category_articles = query.count()  # Nombre total de pays

        # Pagination
        category_articles = query.order_by(models.CategoryArticle.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_category_articles / limit) if limit > 0 else 1

        serialized_category_articles = []
        for category_article in category_articles:
            serialized_category_article = category_aticles_schemas.CategoryArticleListing.from_orm(category_article)
            if category_article.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == category_article.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {category_article.created_by} does not exist")
                creator_serialized = category_aticles_schemas.UserInfo.from_orm(creator_query)
                serialized_category_article.creator = creator_serialized
            if category_article.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == category_article.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {category_article.updated_by} does not exist")
                updator_serialized = category_aticles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_category_article.updator = updator_serialized
            serialized_category_articles.append(serialized_category_article)

        return {
            "category_articles": jsonable_encoder(serialized_category_articles),
            "total_category_articles": total_category_articles,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/search/")
async def search_category_articles(
    name: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(models.CategoryArticle)

        # Filtrer par nom si fourni
        if name:
            query = query.filter(models.CategoryArticle.name.contains(name.lower()))

        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.CategoryArticle.active == active)

        # Pagination
        total_category_articles = query.count()  # Nombre total de pays

        # Pagination
        category_articles = query.order_by(models.CategoryArticle.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_category_articles / limit) if limit > 0 else 1

        serialized_category_articles = []
        for category_article in category_articles:
            serialized_category_article = category_aticles_schemas.CategoryArticleListing.from_orm(category_article)
            if category_article.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == category_article.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {category_article.created_by} does not exist")
                creator_serialized = category_aticles_schemas.UserInfo.from_orm(creator_query)
                serialized_category_article.creator = creator_serialized
            if category_article.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == category_article.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {category_article.updated_by} does not exist")
                updator_serialized = category_aticles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_category_article.updator = updator_serialized
            serialized_category_articles.append(serialized_category_article)

        return {
            "category_articles": jsonable_encoder(serialized_category_articles),
            "total_category_articles": total_category_articles,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get an category
@router.get("/{category_id}", status_code=status.HTTP_200_OK, response_model=category_aticles_schemas.CategoryArticleDetail)
async def detail_category(category_id: str, db: Session = Depends(get_db)):
    query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id, models.CategoryArticle.active == "True").first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"category with id: {category_id} does not exist")
    
    articles = [{ 'id': article.id,
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
                'active': article.active} for article in query.articles]
    serialized_category_article = category_aticles_schemas.CategoryArticleDetail.from_orm(query)
    if serialized_category_article.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = category_aticles_schemas.UserInfo.from_orm(creator_query)
        serialized_category_article.creator = creator_serialized
    if serialized_category_article.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = category_aticles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_category_article.updator = updator_serialized
    
    return jsonable_encoder(serialized_category_article)


# update an type product request
@router.put("/{category_id}", status_code=status.HTTP_200_OK, response_model = category_aticles_schemas.CategoryArticleDetail)
async def update_category(category_id: str, category_update: category_aticles_schemas.CategoryArticleUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id).first()

    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"category with id: {category_id} does not exist")
    else:
        
        query.updated_by =  current_user.id
        
        if category_update.name:
            query.name = category_update.name.lower()
        if category_update.description:
            query.description = category_update.description.lower()
        if category_update.image:
            query.image = category_update.image
        
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id).first()
    articles = [{ 'id': article.id,
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
                'active': article.active} for article in query.articles]
    serialized_category_article = category_aticles_schemas.CategoryArticleDetail.from_orm(query)
    if serialized_category_article.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = category_aticles_schemas.UserInfo.from_orm(creator_query)
        serialized_category_article.creator = creator_serialized
    if serialized_category_article.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = category_aticles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_category_article.updator = updator_serialized
    
    return jsonable_encoder(serialized_category_article)


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


# Restore category
@router.patch("/restore/{category_id}", status_code = status.HTTP_200_OK,response_model = category_aticles_schemas.CategoryArticleDetail)
async def restore_category(category_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id, models.CategoryArticle.active == "False").first()
    
    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"category with id: {category_id} does not exist")
        
    query.active = True
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    query = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == category_id).first()
    articles = [{ 'id': article.id,
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
                'active': article.active} for article in query.articles]
    serialized_category_article = category_aticles_schemas.CategoryArticleDetail.from_orm(query)
    if serialized_category_article.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = category_aticles_schemas.UserInfo.from_orm(creator_query)
        serialized_category_article.creator = creator_serialized
    if serialized_category_article.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = category_aticles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_category_article.updator = updator_serialized
    
    return jsonable_encoder(serialized_category_article)
