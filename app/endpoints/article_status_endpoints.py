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
from math import ceil

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
    # concatenated_uuid = str(uuid.uuid4())+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.ArticleStatus).filter(models.ArticleStatus.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    author = current_user.id
    new_article_status_c.name = new_article_status_c.name.lower()
    new_article_status_c.description = new_article_status_c.description.lower()
    
    new_article_status= models.ArticleStatus(id = str(uuid.uuid4()), **new_article_status_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_article_status )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_article_status)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_article_status)

# Get all type articles statuss requests
@router.get("/")
async def get_all_article_status(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    
    # article_status_queries = db.query(models.ArticleStatus).filter(models.ArticleStatus.active == "True").order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()
    try:
        query = db.query(models.ArticleStatus)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.ArticleStatus.active == active)
            
        if limit ==-1:
            articles_status = query.filter(models.ArticleStatus.active == active)
            serialized_articles_status = [article_status_schemas.ArticleStatusListing.from_orm(article_status) for article_status in articles_status]
            return {
                "articles_status": jsonable_encoder(serialized_articles_status)
            }

        total_articles_status = query.count()  # Nombre total de pays

        # Pagination
        articles_status = query.order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_articles_status / limit) if limit > 0 else 1
        
        serialized_articles_status = []
        for article_status in articles_status:
            # serialized_countrie = [countries_schemas.CountryListing.from_orm(country) for country in countries]
            serialized_article_status = article_status_schemas.ArticleStatusListing.from_orm(article_status)
            if serialized_article_status.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == article_status.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {article_status.created_by} does not exist")
                creator_serialized = article_status_schemas.UserInfo.from_orm(creator_query)
                serialized_article_status.creator = creator_serialized
            if serialized_article_status.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == article_status.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {article_status.updated_by} does not exist")
                updator_serialized = article_status_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_article_status.updator = updator_serialized
            serialized_articles_status.append(serialized_article_status)

        return {
            "articles_status": jsonable_encoder(serialized_articles_status),
            "total_articles_status": total_articles_status,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.get("/search/")
async def search_articles_status(
    name: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    # query: Optional[str] = None,
):
    try:
        query = db.query(models.ArticleStatus)

        # Filtrer par nom si fourni
        if name:
            query = query.filter(models.ArticleStatus.name.contains(name.lower()))

        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.ArticleStatus.active == active)
        
        # Pagination
        total_articles_status = query.count()  # Nombre total de pays

        # Pagination
        articles_status = query.order_by(models.ArticleStatus.name).offset(skip).limit(limit).all()

        total_pages = ceil(total_articles_status / limit) if limit > 0 else 1
        
        serialized_articles_status = []
        for article_status in articles_status:
            # serialized_countrie = [countries_schemas.CountryListing.from_orm(country) for country in countries]
            serialized_article_status = article_status_schemas.ArticleStatusListing.from_orm(article_status)
            if serialized_article_status.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == article_status.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {article_status.created_by} does not exist")
                creator_serialized = article_status_schemas.UserInfo.from_orm(creator_query)
                serialized_article_status.creator = creator_serialized
            if serialized_article_status.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == article_status.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {article_status.updated_by} does not exist")
                updator_serialized = article_status_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                serialized_article_status.updator = updator_serialized
            serialized_articles_status.append(serialized_article_status)

        return {
            "articles_status": jsonable_encoder(serialized_articles_status),
            "total_articles_status": total_articles_status,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Get an article_status
@router.get("/{article_status_id}", status_code=status.HTTP_200_OK, response_model=article_status_schemas.ArticleStatusDetail)
async def detail_article_status(article_status_id: str, db: Session = Depends(get_db)):
    query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id, models.ArticleStatus.active == "True").first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_status with id: {article_status_id} does not exist")
    
    articles = [{ 'id': article.id,
                 'refnumber': article.refnumber,
                 'name': article.name,
                 'reception_place': article.reception_place,
                 'category_article_id': article.category_article_id,
                 'article_status_id': article.article_status_id,
                 'description': article.description,
                 'end_date': article.end_date,
                 'price': article.price,
                 'image_principal': article.image_principal,
                 'owner_id': article.owner_id,
                 'publish': article.publish,
                 'locked': article.locked,
                 'active': article.active} for article in query.articles]
    
    serialized_article_status = article_status_schemas.ArticleStatusDetail.from_orm(query)
    if serialized_article_status.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = article_status_schemas.UserInfo.from_orm(creator_query)
        serialized_article_status.creator = creator_serialized
    if serialized_article_status.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {query.updated_by} does not exist")
        updator_serialized = article_status_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_article_status.updator = updator_serialized
    
    return jsonable_encoder(serialized_article_status)


# update an type articles status request
@router.put("/{article_status_id}", status_code=status.HTTP_200_OK, response_model = article_status_schemas.ArticleStatusDetail)
async def update_article_status(article_status_id: str, article_status_update: article_status_schemas.ArticleStatusUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id).first()
    print("query :", query)

    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_status with id: {article_status_id} does not exist")
    else:
        
        query.updated_by =  current_user.id
        
        if article_status_update.name:
            query.name = article_status_update.name
        if article_status_update.description:
            query.description = article_status_update.description
        
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    articles = [{ 'id': article.id,
                 'refnumber': article.refnumber,
                 'name': article.name,
                 'reception_place': article.reception_place,
                 'category_article_id': article.category_article_id,
                 'article_status_id': article.article_status_id,
                 'description': article.description,
                 'end_date': article.end_date,
                 'price': article.price,
                 'image_principal': article.image_principal,
                 'owner_id': article.owner_id,
                 'publish': article.publish,
                 'locked': article.locked,
                 'active': article.active} for article in query.articles]
    
    serialized_article_status = article_status_schemas.ArticleStatusDetail.from_orm(query)
    if serialized_article_status.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = article_status_schemas.UserInfo.from_orm(creator_query)
        serialized_article_status.creator = creator_serialized
    if serialized_article_status.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {query.updated_by} does not exist")
        updator_serialized = article_status_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_article_status.updator = updator_serialized
    
    return jsonable_encoder(serialized_article_status)


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


# Restore article_status
@router.patch("/restore/{article_status_id}", status_code = status.HTTP_200_OK,response_model = article_status_schemas.ArticleStatusListing)
async def restore_article_status(article_status_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article_status_id, models.ArticleStatus.active == "False").first()
    
    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article_status with id: {article_status_id} does not exist")
        
    query.active = True
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    articles = [{ 'id': article.id,
                 'refnumber': article.refnumber,
                 'name': article.name,
                 'reception_place': article.reception_place,
                 'category_article_id': article.category_article_id,
                 'article_status_id': article.article_status_id,
                 'description': article.description,
                 'end_date': article.end_date,
                 'price': article.price,
                 'image_principal': article.image_principal,
                 'owner_id': article.owner_id,
                 'publish': article.publish,
                 'locked': article.locked,
                 'active': article.active} for article in query.articles]
    
    serialized_article_status = article_status_schemas.ArticleStatusDetail.from_orm(query)
    if serialized_article_status.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.created_by} does not exist")
        creator_serialized = article_status_schemas.UserInfo.from_orm(creator_query)
        serialized_article_status.creator = creator_serialized
    if serialized_article_status.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Country with id: {query.updated_by} does not exist")
        updator_serialized = article_status_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
        serialized_article_status.updator = updator_serialized
    
    return jsonable_encoder(serialized_article_status)
