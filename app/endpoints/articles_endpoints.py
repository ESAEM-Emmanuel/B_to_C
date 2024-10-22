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

router = APIRouter(prefix = "/articles", tags=['Articles Requests'])
 
# create a new article sheet
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=articles_schemas.ArticleListing)
async def create_article(new_article_c: articles_schemas.ArticleCreate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.Article).filter(models.Article.name == new_article_c.name,
                                            models.Article.town_id == new_article_c.town_id,
                                            models.Article.reception_place == new_article_c.reception_place.lower(),
                                            models.Article.category_article_id == new_article_c.category_article_id,
                                            models.Article.article_status_id == new_article_c.article_status_id,
                                            models.Article.article_status_id == new_article_c.article_status_id,
                                            models.Article.owner_id == current_user.id,
                                            models.Article.price == new_article_c.price).first()
    if  query:
        query.active = True
        query.publish = False
        query.updated_by =  current_user.id
        
        try:  
            db.commit() # pour faire l'enregistrement
            db.refresh(query)# pour renvoyer le résultat
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=403, detail="An error occurred when reactivating an existing item!")
        return jsonable_encoder(query)
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())#+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.Article).filter(models.Article.refnumber.endswith(codefin)).all())) + "/" + codefin
    
    owner_id = current_user.id
    new_article_c.name = new_article_c.name.lower()
    new_article_c.reception_place = new_article_c.reception_place.lower()
    new_article_c.description = new_article_c.description.lower()
    
    new_article= models.Article(id = concatenated_uuid, **new_article_c.dict(), refnumber = concatenated_num_ref, owner_id = owner_id)
    
    try:
        db.add(new_article )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_article)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_article)

@router.get("/")
async def get_all_user(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Article)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.Article.active == active)

        total_articles = query.count()  # Nombre total de villes

        if limit > 0:
            articles = query.order_by(models.Article.name).offset(skip).limit(limit).all()
        else:
            articles = query.order_by(models.Article.name).all()

        total_pages = ceil(total_articles / limit) if limit > 0 else 1
        # Récupérer les informations sur le pays via une jointure
        articles_serialized = []
        for article in articles:
            # Utiliser la jointure pour éviter plusieurs requêtes
            article_serialized = articles_schemas.ArticleListing.from_orm(article)
            if article.owner_id:
                owner = db.query(models.User).filter(models.User.id == article.owner_id).first()
                if not owner:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {article.owner_id} does not exist")
                article_serialized.owner = articles_schemas.UserInfo.from_orm(owner)
                
            if article.town_id:
                town = db.query(models.Town).filter(models.Town.id == article.town_id).first()
                if not town:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {article.town_id} does not exist")
                article_serialized.town = articles_schemas.TownList.from_orm(town)
                
            if article.article_status_id:
                article_status = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article.article_status_id).first()
                if not article_status:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id: {article.article_status_id} does not exist")
                article_serialized.article_status = articles_schemas.ArticleStatusList.from_orm(article_status)
                
            if article.category_article_id:
                category = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == article.category_article_id).first()
                if not category:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {article.category_article_id} does not exist")
                article_serialized.category = articles_schemas.CategoryList.from_orm(category)
                
            if article.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == article.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {article.updated_by} does not exist")
                updator_serialized = articles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                article_serialized.updator = updator_serialized
            articles_serialized.append(article_serialized)  # Ajouter l'utilisateur complet dans la liste

        return {
            "articles": jsonable_encoder(articles_serialized),
            "total_articles": total_articles,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.get("/search/")
async def search_users(
    name: Optional[str] = None,
    category_article_id: Optional[str] = None,
    refnumber: Optional[str] = None,
    town_id: Optional[str] = None,
    article_status_id: Optional[str] = None,
    uper_date: Optional[str] = None, 
    lower_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    publish: Optional[bool] = None,
    locked: Optional[bool] = None,
    active: Optional[bool] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    lower_price: Optional[float] = None,
    uper_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        # Construction de la requête
        query = db.query(models.Article)

        # Filtrer par nom d'article si fourni
        if name is not None:
            query = query.filter(models.Article.name.ilike(f"%{name.lower()}%"))
        
        # Filtrer par catégorie
        if category_article_id is not None:
            query = query.filter(models.Article.category_article_id == category_article_id)
            
        # Filtrer par ville
        if town_id is not None:
            query = query.filter(models.Article.town_id == town_id)
        
        # Filtrer par statut de l'article
        if article_status_id is not None:
            query = query.filter(models.Article.article_status_id == article_status_id)
        
        # Filtrer par date supérieure (date limite supérieure)
        if uper_date is not None:
            try:
                uper_date_parsed = datetime.strptime(uper_date, "%Y-%m-%d")
                query = query.filter(models.Article.end_date <= uper_date_parsed)
            except ValueError:
                raise ValueError("Format de la date invalide pour 'uper_date', veuillez utiliser 'YYYY-MM-DD'.")
        
        # Filtrer par date inférieure (date limite inférieure)
        if lower_date is not None:
            try:
                lower_date_parsed = datetime.strptime(lower_date, "%Y-%m-%d")
                query = query.filter(models.Article.end_date >= lower_date_parsed)
            except ValueError:
                raise ValueError("Format de la date invalide pour 'lower_date', veuillez utiliser 'YYYY-MM-DD'.")
        
        # Filtrer par date exacte
        if end_date is not None:
            try:
                end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(models.Article.end_date == end_date_parsed)
            except ValueError:
                raise ValueError("Format de la date invalide pour 'end_date', veuillez utiliser 'YYYY-MM-DD'.")
        
        # Filtrer par prix inférieur ou égal
        if uper_price is not None:
            query = query.filter(models.Article.price <= uper_price)
        
        # Filtrer par prix supérieur ou égal
        if lower_price is not None:
            query = query.filter(models.Article.price >= lower_price)
        
        # Filtrer par prix exact
        if price is not None:
            query = query.filter(models.Article.price == price)
        
        # Filtrer par numéro de référence
        if refnumber is not None:
            query = query.filter(models.Article.refnumber.ilike(f"%{refnumber}%"))
        
        # Filtrer par description
        if description is not None:
            query = query.filter(models.Article.description.ilike(f"%{description}%"))
        
        # Filtrer par statut de publication
        if publish is not None:
            query = query.filter(models.Article.publish == publish)

        # Filtrer par statut verrouillé
        if locked is not None:
            query = query.filter(models.Article.locked == locked)
        
        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.Article.active == active)
        
        articles = query
        total_articles = query.count()

        # Pagination
        total_pages = ceil(total_articles / limit) if limit > 0 else 1

        # Récupérer les informations sur le pays via une jointure
        articles_serialized = []
        for article in articles:
            # Utiliser la jointure pour éviter plusieurs requêtes
            article_serialized = articles_schemas.ArticleListing.from_orm(article)
            if article.owner_id:
                owner = db.query(models.User).filter(models.User.id == article.owner_id).first()
                if not owner:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {article.owner_id} does not exist")
                article_serialized.owner = articles_schemas.UserInfo.from_orm(owner)
                
            if article.town_id:
                town = db.query(models.Town).filter(models.Town.id == article.town_id).first()
                if not town:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {article.town_id} does not exist")
                article_serialized.town = articles_schemas.TownList.from_orm(town)
                
            if article.article_status_id:
                article_status = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == article.article_status_id).first()
                if not article_status:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id: {article.article_status_id} does not exist")
                article_serialized.article_status = articles_schemas.ArticleStatusList.from_orm(article_status)
                
            if article.category_article_id:
                category = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == article.category_article_id).first()
                if not category:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {article.category_article_id} does not exist")
                article_serialized.category = articles_schemas.CategoryList.from_orm(category)
                
            if article.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == article.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {article.updated_by} does not exist")
                updator_serialized = articles_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                article_serialized.updator = updator_serialized
            articles_serialized.append(article_serialized)  # Ajouter l'utilisateur complet dans la liste

        return {
            "articles": jsonable_encoder(articles_serialized),
            "total_articles": total_articles,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get an article
@router.get("/{article_id}", status_code=status.HTTP_200_OK, response_model=articles_schemas.ArticleDetail)
async def detail_article(article_id: str, db: Session = Depends(get_db)):
    query = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Article with id: {article_id} does not exist")
    
    # Traiter les signaux associés à l'article
    signals = query.signals
    details = [
        {
            'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 
            'article_id': signal.article_id, 'description': signal.description, 'active': signal.active
        } 
        for signal in signals
    ]
    signals = details

    # Sérialiser l'article
    article_serialized = articles_schemas.ArticleDetail.from_orm(query)
    
    # Traiter le propriétaire (owner)
    if query.owner_id:
        owner = db.query(models.User).filter(models.User.id == query.owner_id).first()
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.owner_id} does not exist")
        article_serialized.owner = articles_schemas.UserInfo.from_orm(owner)
    
    # Traiter la ville (town)
    if query.town_id:
        town = db.query(models.Town).filter(models.Town.id == query.town_id).first()
        if not town:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Town with id: {query.town_id} does not exist")
        article_serialized.town = articles_schemas.TownList.from_orm(town)
    
    # Traiter le statut de l'article
    if query.article_status_id:
        article_status = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == query.article_status_id).first()
        if not article_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id: {query.article_status_id} does not exist")
        article_serialized.article_status = articles_schemas.ArticleStatusList.from_orm(article_status)
    
    # Traiter la catégorie de l'article
    if query.category_article_id:
        category = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == query.category_article_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {query.category_article_id} does not exist")
        article_serialized.category = articles_schemas.CategoryList.from_orm(category)
    
    # Traiter l'utilisateur qui a mis à jour (updator)
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = articles_schemas.UserInfo.from_orm(updator_query)
        article_serialized.updator = updator_serialized
    
    # Retourner l'article sérialisé avec encodage JSON
    return jsonable_encoder(article_serialized)



# update an permission request
@router.put("/update/{article_id}", status_code=status.HTTP_200_OK, response_model = articles_schemas.ArticleDetail)
async def update_article(article_id: str, article_update: articles_schemas.ArticleUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    query = db.query(models.Article).filter(models.Article.id == article_id).first()

    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
    else:
        
        query.updated_by =  current_user.id
        
        if article_update.name:
            query.name = article_update.name
        if article_update.town_id:
            query.town_id = article_update.town_id
        if article_update.reception_place:
            query.reception_place = article_update.reception_place
        if article_update.owner_id:
            query.owner_id = article_update.owner_id
        if article_update.category_article_id:
            query.category_article_id = article_update.category_article_id
        if article_update.article_status_id:
            query.article_status_id = article_update.article_status_id
        if article_update.description:
            query.description = article_update.description
        if article_update.main_image:
            query.main_image = article_update.main_image
        if article_update.price:
            query.price = article_update.price
        if article_update.publish:
            query.publish = article_update.publish
        if article_update.locked:
            query.locked = article_update.locked
            
    
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    # Traiter les signaux associés à l'article
    signals = query.signals
    details = [
        {
            'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 
            'article_id': signal.article_id, 'description': signal.description, 'active': signal.active
        } 
        for signal in signals
    ]
    signals = details

    # Sérialiser l'article
    article_serialized = articles_schemas.ArticleDetail.from_orm(query)
    
    # Traiter le propriétaire (owner)
    if query.owner_id:
        owner = db.query(models.User).filter(models.User.id == query.owner_id).first()
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.owner_id} does not exist")
        article_serialized.owner = articles_schemas.UserInfo.from_orm(owner)
    
    # Traiter la ville (town)
    if query.town_id:
        town = db.query(models.Town).filter(models.Town.id == query.town_id).first()
        if not town:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Town with id: {query.town_id} does not exist")
        article_serialized.town = articles_schemas.TownList.from_orm(town)
    
    # Traiter le statut de l'article
    if query.article_status_id:
        article_status = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == query.article_status_id).first()
        if not article_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id: {query.article_status_id} does not exist")
        article_serialized.article_status = articles_schemas.ArticleStatusList.from_orm(article_status)
    
    # Traiter la catégorie de l'article
    if query.category_article_id:
        category = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == query.category_article_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {query.category_article_id} does not exist")
        article_serialized.category = articles_schemas.CategoryList.from_orm(category)
    
    # Traiter l'utilisateur qui a mis à jour (updator)
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = articles_schemas.UserInfo.from_orm(updator_query)
        article_serialized.updator = updator_serialized
    
    # Retourner l'article sérialisé avec encodage JSON
    return jsonable_encoder(article_serialized)


# delete article
@router.patch("/delete/{article_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.Article).filter(models.Article.id == article_id, models.Article.active == "True").first()
    
    if not query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
        
    query.active = False
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return {"message": "article deleted!"}

# Restore permission
@router.patch("/restore/{article_id}", status_code = status.HTTP_200_OK,response_model = articles_schemas.ArticleDetail)
async def restore_article(article_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.Article).filter(models.Article.id == article_id, models.Article.active == "False").first()
    
    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"article with id: {article_id} does not exist")
        
    query.active = True
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    # Traiter les signaux associés à l'article
    signals = query.signals
    details = [
        {
            'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 
            'article_id': signal.article_id, 'description': signal.description, 'active': signal.active
        } 
        for signal in signals
    ]
    signals = details

    # Sérialiser l'article
    article_serialized = articles_schemas.ArticleDetail.from_orm(query)
    
    # Traiter le propriétaire (owner)
    if query.owner_id:
        owner = db.query(models.User).filter(models.User.id == query.owner_id).first()
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.owner_id} does not exist")
        article_serialized.owner = articles_schemas.UserInfo.from_orm(owner)
    
    # Traiter la ville (town)
    if query.town_id:
        town = db.query(models.Town).filter(models.Town.id == query.town_id).first()
        if not town:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Town with id: {query.town_id} does not exist")
        article_serialized.town = articles_schemas.TownList.from_orm(town)
    
    # Traiter le statut de l'article
    if query.article_status_id:
        article_status = db.query(models.ArticleStatus).filter(models.ArticleStatus.id == query.article_status_id).first()
        if not article_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id: {query.article_status_id} does not exist")
        article_serialized.article_status = articles_schemas.ArticleStatusList.from_orm(article_status)
    
    # Traiter la catégorie de l'article
    if query.category_article_id:
        category = db.query(models.CategoryArticle).filter(models.CategoryArticle.id == query.category_article_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {query.category_article_id} does not exist")
        article_serialized.category = articles_schemas.CategoryList.from_orm(category)
    
    # Traiter l'utilisateur qui a mis à jour (updator)
    if query.updated_by:
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {query.updated_by} does not exist")
        updator_serialized = articles_schemas.UserInfo.from_orm(updator_query)
        article_serialized.updator = updator_serialized
    
    # Retourner l'article sérialisé avec encodage JSON
    return jsonable_encoder(article_serialized)
