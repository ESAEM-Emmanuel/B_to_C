import os
from fastapi import APIRouter, HTTPException, Depends, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas import users_schemas
from utils.users_utils import hash
from typing import Optional
from  utils import oauth2
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.models import models
import uuid
from datetime import datetime, timedelta
from app.database import engine, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from math import ceil

models.Base.metadata.create_all(bind=engine)

# /users/

router = APIRouter(prefix = "/users", tags=['Users Requests'])

@router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=users_schemas.UserListing)
async def create_user(
    new_user_c: users_schemas.UserCreate, 
    db: Session = Depends(get_db), 
    current_user: Optional[models.User] = Depends(oauth2.get_current_user_optional)  # Auth facultative
):
    # Vérifie si l'utilisateur existe déjà
    user_exist = db.query(models.User).filter(
        (models.User.username == new_user_c.username.lower()) |
        (models.User.phone == new_user_c.phone) |
        (models.User.email == new_user_c.email) |
        (models.User.image == new_user_c.image)
    ).first()

    if user_exist:
        raise HTTPException(status_code=400, detail="User already exists with these credentials.")

    # Générer un identifiant unique et un refnumber
    concatenated_uuid = str(uuid.uuid4())
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    concatenated_num_ref = str(
        NUM_REF + len(db.query(models.User).filter(models.User.refnumber.endswith(codefin)).all())
    ) + "/" + codefin

    # Hashage du mot de passe
    hashed_password = hash(new_user_c.password)
    new_user_c.password = hashed_password

    # Si l'utilisateur est authentifié, utiliser son nom, sinon "Anonymous"
    author = current_user.id if current_user else ""

    # Créer un nouvel utilisateur
    new_user = models.User(
        id=concatenated_uuid, 
        **new_user_c.dict(), 
        refnumber=concatenated_num_ref, 
        created_by=author
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=f"An error occurred during the process: {str(e)}")

    return new_user


@router.get("/")
async def get_all_user(skip: int = 0, limit: int = 100, active: Optional[bool] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(models.User)

        # Filtrer par actif/inactif si fourni
        if active is not None:
            query = query.filter(models.User.active == active)

        total_users = query.count()  # Nombre total de villes

        if limit > 0:
            users = query.order_by(models.User.username).offset(skip).limit(limit).all()
        else:
            users = query.order_by(models.User.username).all()

        total_pages = ceil(total_users / limit) if limit > 0 else 1

        # Récupérer les informations sur le pays via une jointure
        serialized_users = []
        for user in users:
            # Utiliser la jointure pour éviter plusieurs requêtes

            user_serialized = users_schemas.UserListing.from_orm(user)
            if user.town_id:
                town = db.query(models.Town).filter(models.Town.id == user.town_id).first()
                town_serialized = users_schemas.TownList.from_orm(town)
                user_serialized.town = town_serialized  # Assigner la ville sérialisée à l'utilisateur
            if user.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == user.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {user.created_by} does not exist")
                creator_serialized = users_schemas.UserInfo.from_orm(creator_query)
                user_serialized.creator = creator_serialized
            if user.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == user.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {user.updated_by} does not exist")
                updator_serialized = users_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                user_serialized.updator = updator_serialized
            serialized_users.append(user_serialized)  # Ajouter l'utilisateur complet dans la liste

        return {
            "users": jsonable_encoder(serialized_users),
            "total_users": total_users,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.get("/search/")
async def search_users(
    username: Optional[str] = None,
    refnumber: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    is_staff: Optional[bool] = None,
    town_id: Optional[str] = None,
    active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        # Construction de la requête
        query = db.query(models.User)

        # Filtrer par nom utilisateur si fourni
        if username is not None:
            query = query.filter(models.User.username.ilike(f"%{username.lower()}%"))
        # Filtrer par nom utilisateur si fourni
        if refnumber is not None:
            query = query.filter(models.User.refnumber.ilike(f"%{refnumber}%"))
        # Filtrer par numéro de téléphone fourni
        if phone is not None:
            query = query.filter(models.User.phone.ilike(f"%{phone}%"))
        # Filtrer par l'email fourni
        if email is not None:
            query = query.filter(models.User.email.ilike(f"%{email}%"))

        # Filtrer par statut actif/inactif
        if active is not None:
            query = query.filter(models.User.active == active)
        # Filtrer par statut actif/inactif
        if is_staff is not None:
            query = query.filter(models.User.is_staff == active)

        # Filtrer par pays si fourni
        if town_id is not None:
            query = query.filter(models.User.town_id == town_id)
        
        users = query

        # Pagination
        total_users = query.count()  # Nombre total de villes

        total_pages = ceil(total_users / limit) if limit > 0 else 1

        # Récupérer les informations sur le pays via une jointure
        serialized_users = []
        for user in users:
            # Utiliser la jointure pour éviter plusieurs requêtes
            user_serialized = users_schemas.UserListing.from_orm(user)
            if user.town_id:
                town = db.query(models.Town).filter(models.Town.id == user.town_id).first()
                town_serialized = users_schemas.TownList.from_orm(town)
                user_serialized.town = town_serialized  # Assigner la ville sérialisée à l'utilisateur
            if user.created_by :
                # Récupération des détails du pays
                creator_query = db.query(models.User).filter(models.User.id == user.created_by).first()
                if not creator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {user.created_by} does not exist")
                creator_serialized = users_schemas.UserInfo.from_orm(creator_query)
                user_serialized.creator = creator_serialized
            if user.updated_by:
                updator_query = db.query(models.User).filter(models.User.id == user.updated_by).first()
                if not updator_query:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {user.updated_by} does not exist")
                updator_serialized = users_schemas.UserInfo.from_orm(updator_query)  # Use updator_query here
                user_serialized.updator = updator_serialized
            serialized_users.append(user_serialized)  # Ajouter l'utilisateur complet dans la liste

        return {
            "users": jsonable_encoder(serialized_users),
            "total_users": total_users,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get an user
@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=users_schemas.UserDetail)
async def detail_user(user_id: str, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(models.User.id == user_id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
    
    details = [{ 
                'id': article.id,
                'refnumber': article.refnumber,
                'name': article.name,
                'reception_place': article.reception_place, 
                'category_article_id': article.category_article_id,
                'article_status_id': article.article_status_id,
                'description': article.description,
                'end_date': article.end_date,
                'price': article.price,
                'main_image': article.main_image,
                'owner_id': article.owner_id,
                'publish': article.publish,
                'locked': article.locked,
                'active': article.active
                } for article in query.articles]
    articles = details
    
    details = [{ 'id': signal.id,
                'refnumber': signal.refnumber,
                'owner_id': signal.owner_id,
                'article_id': signal.article_id,
                'description': signal.description,
                'active': signal.active
                } for signal in query.signals]
    signals = details

    # Construction de la réponse
    serialized_user = users_schemas.UserDetail.from_orm(query)
    
    if query.town_id:
        # Récupération des détails du pays
        town_query = db.query(models.Town).filter(models.Town.id == query.town_id).first()
        if not town_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {query.town_id} does not exist")
        # Sérialisation de la ville
        town_serialized = users_schemas.TownList.from_orm(town_query)
        serialized_user.town = town_serialized
        
    if query.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {query.created_by} does not exist")
        creator_serialized = users_schemas.UserInfo.from_orm(creator_query)
        serialized_user.creator = creator_serialized
    if query.updated_by :
        # Récupération des détails du pays
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {query.updated_by} does not exist")
        updator_serialized = users_schemas.UserInfo.from_orm(updator_query)
        serialized_user.updator = updator_serialized
    
    return jsonable_encoder(serialized_user)


# update an user request
@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model = users_schemas.UserDetail)
async def update_user(user_id: str, user_update: users_schemas.UserUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    print(user_id)  
    query = db.query(models.User).filter(models.User.id == user_id).first()

    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
    else:
        
        query.updated_by =  current_user.id
        
        if user_update.username:
            query.username = user_update.username
        if user_update.town_id:
            query.town_id = user_update.town_id
        if user_update.phone:
            query.phone = user_update.phone
        if user_update.birthday:
            query.birthday = user_update.birthday
        if user_update.gender:
            query.gender = user_update.gender
        if user_update.email:
            query.email = user_update.email
        if user_update.image:
            query.image = user_update.image
        if user_update.password:
            hashed_password = hash(user_update.password)
            user_update.password = hashed_password
            query.password = user_update.password
        if user_update.is_staff:
            query.is_staff = user_update.is_staff
    
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    query = db.query(models.User).filter(models.User.id == user_id).first()
    
    details = [{ 
                'id': article.id,
                'refnumber': article.refnumber,
                'name': article.name,
                'reception_place': article.reception_place, 
                'category_article_id': article.category_article_id,
                'article_status_id': article.article_status_id,
                'description': article.description,
                'end_date': article.end_date,
                'price': article.price,
                'main_image': article.main_image,
                'owner_id': article.owner_id,
                'publish': article.publish,
                'locked': article.locked,
                'active': article.active
                } for article in query.articles]
    articles = details
    
    details = [{ 'id': signal.id,
                'refnumber': signal.refnumber,
                'owner_id': signal.owner_id,
                'article_id': signal.article_id,
                'description': signal.description,
                'active': signal.active
                } for signal in query.signals]
    signals = details

    # Construction de la réponse
    serialized_user = users_schemas.UserDetail.from_orm(query)
    
    # Récupération des détails du pays
    town_query = db.query(models.Town).filter(models.Town.id == query.town_id).first()
    if not town_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {query.town_id} does not exist")
    # Sérialisation de la ville
    town_serialized = users_schemas.TownList.from_orm(town_query)
    serialized_user.town = town_serialized
    
    if query.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {query.created_by} does not exist")
        creator_serialized = users_schemas.UserInfo.from_orm(creator_query)
        serialized_user.creator = creator_serialized
    if query.updated_by :
        # Récupération des détails du pays
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {query.updated_by} does not exist")
        updator_serialized = users_schemas.UserInfo.from_orm(creator_query)
        serialized_user.updator = updator_serialized
    
    return jsonable_encoder(serialized_user)


# delete permission
@router.patch("/delete/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str,  db: Session = Depends(get_db),current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.User).filter(models.User.id == user_id, models.User.active == "True").first()
    
    if not query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
        
    query.active = False
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return {"message": "User deleted!"}

# Restore user
@router.patch("/restore/{user_id}", status_code = status.HTTP_200_OK, response_model=users_schemas.UserDetail)
async def restore_user(user_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    query = db.query(models.User).filter(models.User.id == user_id, models.User.active == "False").first()
    
    if not query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
        
    query.active = True
    query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    query = db.query(models.User).filter(models.User.id == user_id).first()
    
    details = [{ 
                'id': article.id,
                'refnumber': article.refnumber,
                'name': article.name,
                'reception_place': article.reception_place, 
                'category_article_id': article.category_article_id,
                'article_status_id': article.article_status_id,
                'description': article.description,
                'end_date': article.end_date,
                'price': article.price,
                'main_image': article.main_image,
                'owner_id': article.owner_id,
                'publish': article.publish,
                'locked': article.locked,
                'active': article.active
                } for article in query.articles]
    articles = details
    
    details = [{ 'id': signal.id,
                'refnumber': signal.refnumber,
                'owner_id': signal.owner_id,
                'article_id': signal.article_id,
                'description': signal.description,
                'active': signal.active
                } for signal in query.signals]
    signals = details

    # Construction de la réponse
    serialized_user = users_schemas.UserDetail.from_orm(query)
    
    if query.town_id:
        # Récupération des détails du pays
        town_query = db.query(models.Town).filter(models.Town.id == query.town_id).first()
        if not town_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"town with id: {query.town_id} does not exist")
        # Sérialisation de la ville
        town_serialized = users_schemas.TownList.from_orm(town_query)
        serialized_user.town = town_serialized
        
    if query.created_by :
        # Récupération des détails du pays
        creator_query = db.query(models.User).filter(models.User.id == query.created_by).first()
        if not creator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {query.created_by} does not exist")
        creator_serialized = users_schemas.UserInfo.from_orm(creator_query)
        serialized_user.creator = creator_serialized
    if query.updated_by :
        # Récupération des détails du pays
        updator_query = db.query(models.User).filter(models.User.id == query.updated_by).first()
        if not updator_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {query.updated_by} does not exist")
        updator_serialized = users_schemas.UserInfo.from_orm(updator_query)
        serialized_user.updator = updator_serialized
    
    return jsonable_encoder(serialized_user)
