
import os
from fastapi import APIRouter, HTTPException, Depends, Response, status,File, UploadFile, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, get_db
from app.schemas import users_schemas
from app.models import models as models
from  utils import oauth2
from utils.users_utils import hash
import uuid
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.database import engine, get_db
from app.models import models
from typing import List

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=users_schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.username == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not oauth2.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


# create a new anounce sheet
@router.get("/get_user_by_token/", status_code = status.HTTP_200_OK, response_model=users_schemas.UserDetail)
async def get_user_by_token( db: Session = Depends(get_db), current_user : str = Depends(oauth2.get_current_user)):
    
    user_id = current_user.id
    
    user_query = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {user_id} does not exist")
    
    articles = user_query.articles
    details = [{ 'id': article.id, 'refnumber': article.refnumber, 'name': article.name, 'reception_place': article.reception_place,  'category_article_id': article.category_article_id, 'article_statu_id': article.article_statu_id, 'description': article.description, 'end_date': article.end_date, 'price': article.price, 'image_principal': article.image_principal, 'owner_id': article.owner_id, 'publish': article.publish, 'locked': article.locked, 'active': article.active} for article in articles]
    articles = details
    
    signals = user_query.signals
    details = [{ 'id': signal.id, 'refnumber': signal.refnumber, 'owner_id': signal.owner_id, 'article_id': signal.article_id, 'description': signal.description, 'active': signal.active} for signal in signals]
    signals = details
    
    return jsonable_encoder(current_user)


# @router.get("/user/{profil_id}/privileges", response_model=List[dict])
# @router.get("/user_privileges/{profil_id}")
# def get_privileges_for_user_profil(
#     profil_id: str,
#     db: Session = Depends(get_db),
#     # current_user: str Depends(oauth2.get_current_user)
#     current_user: models.User = Depends(oauth2.get_current_user),  # Utilisation du modèle User
# ):
#     # Utilisation de .first() au lieu de .all() pour obtenir un seul résultat
#     profil = db.query(models.Profil).filter(
#         models.Profil.id == profil_id, models.Profil.active == True
#     ).first()
    
#     if not profil:
#         raise HTTPException(status_code=404, detail="Profil non trouvé")

#     # Obtenez les privilèges directement liés au profil
#     profile_privileges = [p.privilege.name for p in profil.profil_privileges]

#     # Obtenez les privilèges liés aux rôles du profil
#     for profil_role in profil.profil_roles:
#         role_privileges = [rp.privilege.name for rp in profil_role.role.privilege_roles]
#         profile_privileges.extend(role_privileges)

#     # Supprimer les doublons
#     privileges = list(set(profile_privileges))
    
    

#     return {"profil_id": profil_id, "privileges": privileges}
    
    
# Endpoint de déconnexion
# @router.post("/logout")
# async def logout(request: Request, current_user : str = Depends(oauth2.get_current_user)):
    
#     headers = dict(request.headers)  # Convertir les headers en dict pour pouvoir les modifier
#     print(headers)
    
#     if "Authorization" in headers:
#         del headers["Authorization"]  # Supprimer la clé "Authorization" du dict des headers
        
#     token = request.headers.get("Authorization")  # Vérifier que le token a été supprimé
#     print(token)
    
#     if token is not None:
#         return {"error": "Invalid token"}
    

#     return {"message": "User successfully logged out"}

# Endpoint de déconnexion
# @router.post("/logout")
# async def logout( token : str = Depends(oauth2.get_current_user)):
#     oauth2.invalid_tokens.add(token)
#     return {"message": "Logout successful"}

