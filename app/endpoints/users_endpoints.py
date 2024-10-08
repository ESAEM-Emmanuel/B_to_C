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

router = APIRouter(prefix = "/user", tags=['Users Requests'])

# create a new user
@router.post("/create/", status_code = status.HTTP_201_CREATED, response_model=users_schemas.UserListing)
# async def create_user(new_user_c: users_schemas.UserCreate, file: UploadFile = File(...), db: Session = Depends(get_db)):
async def create_user(new_user_c: users_schemas.UserCreate, db: Session = Depends(get_db)):
    # Vérifiez si l'utilisateur existe déjà dans la base de données
    if new_user_c.username:
        if db.query(models.User).filter(models.User.username == new_user_c.username.lower()).first():
            raise HTTPException(status_code=400, detail='Registered user with this username')
    if new_user_c.phone:
        if db.query(models.User).filter(models.User.phone == new_user_c.phone).first():
            raise HTTPException(status_code=400, detail='Registered user with this phone number')
    if new_user_c.email:
        if db.query(models.User).filter(models.User.email == new_user_c.email).first():
            raise HTTPException(status_code=400, detail='Registered user with this email')
    if new_user_c.image:
        if db.query(models.User).filter(models.User.image == new_user_c.image).first():
            raise HTTPException(status_code=400, detail='Registered user with this image')
    
    formated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# Formatage de la date au format souhaité (par exemple, YYYY-MM-DD HH:MM:SS)
    concatenated_uuid = str(uuid.uuid4())#+ ":" + formated_date
    NUM_REF = 10001
    codefin = datetime.now().strftime("%m/%Y")
    new_user_c.username = new_user_c.username.lower()
       
    concatenated_num_ref = str(
            NUM_REF + len(db.query(models.User).filter(models.User.refnumber.endswith(codefin)).all())) + "/" + codefin
    hashed_password = hash(new_user_c.password)
    new_user_c.password = hashed_password
    
    author = "current_user"
    
    new_user= models.User(id = concatenated_uuid, **new_user_c.dict(), refnumber = concatenated_num_ref, created_by = author)
    
    try:
        db.add(new_user )# pour ajouter une tuple
        db.commit() # pour faire l'enregistrement
        db.refresh(new_user)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return jsonable_encoder(new_user)

# Get all users requests
@router.get("/get_all_actif/", response_model=List[users_schemas.UserListing])
async def read_users_actif(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users_queries = db.query(models.User).filter(models.User.active == "True").order_by(models.User.username).offset(skip).limit(limit).all()                  
    
    return jsonable_encoder(users_queries)

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
        print(users)

        # Récupérer les informations sur le pays via une jointure
        serialized_users = []
        for user in users:
            # Utiliser la jointure pour éviter plusieurs requêtes
            town = db.query(models.Town).filter(models.Town.id == user.town_id).first()

            if town:
                town_serialized = users_schemas.TownList.from_orm(town)
                user_serialized = users_schemas.UserListing.from_orm(user)
                user_serialized.town = town_serialized  # Assigner la ville sérialisée à l'utilisateur
                serialized_users.append(user_serialized)  # Ajouter l'utilisateur complet dans la liste

        return {
            "towns": jsonable_encoder(serialized_users),
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

        # Pagination
        total_users = query.count()  # Nombre total de villes

        if limit > 0:
            users = query.order_by(models.User.name).offset(skip).limit(limit).all()
        else:
            users = query.order_by(models.User.name).all()

        total_pages = ceil(total_users / limit) if limit > 0 else 1

        # Récupérer les informations sur le pays via une jointure
        serialized_users = []
        for user in users:
            # Utiliser la jointure pour éviter plusieurs requêtes
            town = db.query(models.Town).filter(models.Town.id == user.town_id).first()

            if town:
                town_serialized = users_schemas.TownList.from_orm(town)
                user_serialized = users_schemas.UserListing.from_orm(user)
                user_serialized.town = town_serialized
                serialized_users.append(town_serialized)

        return {
            "towns": jsonable_encoder(serialized_users),
            "total_users": total_users,
            "total_pages": total_pages,
            "current_page": (skip // limit) + 1 if limit > 0 else 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Get an user
# "/get_user_impersonal/?refnumber=value_refnumber&phone=valeur_phone&email=valeur_email&username=valeur_username" : Retourne `{"param1": "value1", "param2": 42, "param3": null}`.
@router.get("/get_user_by_attribut/", status_code=status.HTTP_200_OK, response_model=List[users_schemas.UserListing])
async def detail_user_by_attribut(refnumber: Optional[str] = None, phone: Optional[str] = None, username: Optional[str] = None, email: Optional[str] = None, is_staff: Optional[bool] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_query = {} # objet vide
    if refnumber is not None :
        user_query = db.query(models.User).filter(models.User.refnumber == refnumber, models.User.active == "True").order_by(models.User.username).offset(skip).limit(limit).all()
    if phone is not None :
        user_query = db.query(models.User).filter(models.User.phone.contains(phone), models.User.active == "True").order_by(models.User.username).offset(skip).limit(limit).all()
    if email is not None:
        user_query = db.query(models.User).filter(models.User.email.contains(email), models.User.active == "True").order_by(models.User.username).offset(skip).limit(limit).all()
    if username is not None :
        user_query = db.query(models.User).filter(models.User.username.contains(username), models.User.active == "True").order_by(models.User.username).offset(skip).limit(limit).all()
    if is_staff is not None :
        user_query = db.query(models.User).filter(models.User.is_staff == is_staff, models.User.active == "True").order_by(models.User.username).offset(skip).limit(limit).all()
    
    return jsonable_encoder(user_query)

# Get an user
@router.get("/get/{user_id}", status_code=status.HTTP_200_OK, response_model=users_schemas.UserDetail)
async def detail_user(user_id: str, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
    
    
    articles = user_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
    
    signals = user_query.signals
    details = [{ 'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 'article_id': signal.article_id, 'description': signal.description, 'active': signal.active} for signal in signals]
    signals = details
    
    return jsonable_encoder(user_query)


# update an user request
@router.put("/update/{user_id}", status_code=status.HTTP_200_OK, response_model = users_schemas.UserDetail)
async def update_user(user_id: str, user_update: users_schemas.UserUpdate, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
        
    user_query = db.query(models.User).filter(models.User.id == user_id).first()

    if not user_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
    else:
        
        user_query.updated_by =  current_user.id
        
        if user_update.username:
            user_query.username = user_update.username
        if user_update.town_id:
            user_query.town_id = user_update.town_id
        if user_update.phone:
            user_query.phone = user_update.phone
        if user_update.birthday:
            user_query.birthday = user_update.birthday
        if user_update.gender:
            user_query.gender = user_update.gender
        if user_update.email:
            user_query.email = user_update.email
        if user_update.image:
            user_query.image = user_update.image
        if user_update.password:
            hashed_password = hash(user_update.password)
            user_update.password = hashed_password
            user_query.password = user_update.password
        if user_update.is_staff:
            user_query.is_staff = user_update.is_staff
    
    try:
        db.commit() # pour faire l'enregistrement
        db.refresh(user_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process , pleace try later sorry!")
    
    user_query = db.query(models.User).filter(models.User.id == user_id).first()
    articles = user_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
    
    signals = user_query.signals
    details = [{ 'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 'article_id': signal.article_id, 'description': signal.description, 'active': signal.active} for signal in signals]
    signals = details    
    return jsonable_encoder(user_query)


# delete permission
@router.patch("/delete/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str,  db: Session = Depends(get_db),current_user : str = Depends(oauth2.get_current_user)):
    
    user_query = db.query(models.User).filter(models.User.id == user_id, models.User.active == "True").first()
    
    if not user_query:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
        
    user_query.active = False
    user_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(user_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    return {"message": "User deleted!"}


# Get all user inactive requests
@router.get("/get_all_inactive/", response_model=List[users_schemas.UserListing])
async def read_users_inactive(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    users_queries = db.query(models.User).filter(models.User.active == "False").order_by(models.User.name).offset(skip).limit(limit).all()
                      
    return jsonable_encoder(users_queries)


# Restore user
@router.patch("/restore/{user_id}", status_code = status.HTTP_200_OK,response_model = users_schemas.UserListing)
async def restore_user(user_id: str,  db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    user_query = db.query(models.User).filter(models.User.id == user_id, models.User.active == "False").first()
    
    if not user_query:
            
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
        
    user_query.active = True
    user_query.updated_by =  current_user.id
    
    try:  
        db.commit() # pour faire l'enregistrement
        db.refresh(user_query)# pour renvoyer le résultat
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Somthing is wrong in the process, pleace try later sorry!")
    
    
    return jsonable_encoder(user_query)
