# from datetime import datetime, timedelta
# from jose import jwt, JWTError
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# from app.models.models import User, RevokedToken, PrivilegeUser, UserRole, Role, PrivilegeRole, Privilege,BaseMixin 
# from app.schemas.users_schemas import UserSchema
# from app.config import settings
# from app.database import get_db
# from jose.exceptions import ExpiredSignatureError
# from fastapi import Depends, HTTPException, status
# import enum
# from fastapi.security import OAuth2PasswordBearer
# from typing import List, Optional

# # Configuration pour le hachage des mots de passe
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Configuration pour les tokens JWT
# SECRET_KEY = settings.SECRET_KEY
# ALGORITHM = settings.ALGORITHM
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
# REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


# def verify_password(plain_password, hashed_password):
#     """
#     Vérifie si le mot de passe en clair correspond au mot de passe haché.
#     """
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     """
#     Hache un mot de passe en clair.
#     """
#     return pwd_context.hash(password)


# def authenticate_user(db: Session, username: str, password: str):
#     try:
#         user = db.query(User).filter(User.username == username).first()
#         if not user or not verify_password(password, user.password):
#             return None
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur lors de l'authentification : {str(e)}")
        

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     """
#     Crée un token d'accès JWT.
#     """
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def create_refresh_token(data: dict, expires_delta: timedelta = None):
#     """
#     Crée un token de rafraîchissement JWT.
#     """
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode.update({"exp": expire, "type": "refresh"})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# # Fonction pour vérifier si un token est révoqué
# def is_token_revoked(token: str, db: Session) -> bool:
#     revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
#     return revoked_token is not None

# def revoke_token(token: str, db: Session):
#     revoked_token = RevokedToken(id=str(uuid.uuid4()), token=token)
#     db.add(revoked_token)
#     db.commit()
#     db.refresh(revoked_token)


# def extract_user_from_token(token: str, db: Session, is_refresh: bool = False):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("sub")
#         token_type = payload.get("type")

#         if is_token_revoked(token, db):
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token révoqué")

#         if user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
#         if is_refresh and token_type != "refresh":
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de rafraîchissement requis")
#         return {"user_id": user_id, "token": token}
#     except ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expiré")
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Erreur de décodage du token")


# def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     return extract_user_from_token(token, db)

# def get_user_from_token_optional(
#     token: Optional[str] = Depends(oauth2_scheme),
#     db: Session = Depends(get_db)
# ) -> Optional[User]:
#     """
#     Récupère l'utilisateur à partir du token s'il est valide et non révoqué.
#     Si le token est absent ou invalide, retourne None sans lever d'exception.
#     """
#     if not token:
#         return None  # Aucun token fourni, utilisateur non authentifié

#     try:
#         # Utiliser extract_user_from_token pour valider le token
#         user_data = extract_user_from_token(token, db)
#         user_id = user_data.get("user_id")

#         # Rechercher l'utilisateur dans la base de données
#         user = db.query(User).filter(User.id == user_id).first()
#         return user
#     except Exception:
#         # En cas d'erreur (token invalide, expiré, etc.), retourner None
#         return None

# def get_privileges(
#     user_id: Optional[str],
#     db: Session = Depends(get_db),
# ) -> List[str]:
#     """
#     Récupère tous les privilèges d'un utilisateur donné.
#     Les privilèges peuvent être directement attribués via PrivilegeUser
#     ou indirectement via les rôles auxquels l'utilisateur appartient (UserRole).
#     """
#     if not user_id:
#         raise HTTPException(status_code=400, detail="L'ID de l'utilisateur est requis")

#     # Initialiser un ensemble pour stocker les privilèges uniques
#     privileges = set()

#     # 1. Récupérer les privilèges directement attribués à l'utilisateur (via PrivilegeUser)
#     privilege_users = (
#         db.query(Privilege.name)
#         .join(PrivilegeUser, Privilege.id == PrivilegeUser.privilege_id)
#         .filter(PrivilegeUser.owner_id == user_id, Privilege.active == True)
#         .all()
#     )
#     privileges.update([privilege[0] for privilege in privilege_users])

#     # 2. Récupérer les privilèges via les rôles de l'utilisateur (via UserRole et PrivilegeRole)
#     user_roles = (
#         db.query(Role.id)
#         .join(UserRole, Role.id == UserRole.role_id)
#         .filter(UserRole.owner_id == user_id, Role.active == True)
#         .all()
#     )
#     role_ids = [role[0] for role in user_roles]

#     if role_ids:
#         role_privileges = (
#             db.query(Privilege.name)
#             .join(PrivilegeRole, Privilege.id == PrivilegeRole.privilege_id)
#             .filter(PrivilegeRole.role_id.in_(role_ids), Privilege.active == True)
#             .all()
#         )
#         privileges.update([privilege[0] for privilege in role_privileges])

#     # Retourner la liste des privilèges uniques
#     return list(privileges)

from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.models import User, RevokedToken, PrivilegeUser, UserRole, Role, PrivilegeRole, Privilege,BaseMixin 
from app.schemas.users_schemas import UserSchema
from app.config import settings
from app.database import get_db
from jose.exceptions import ExpiredSignatureError
from fastapi import Depends, HTTPException, status
import enum
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy import select
import uuid


# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration pour les tokens JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def verify_password(plain_password, hashed_password):
    """
    Vérifie si le mot de passe en clair correspond au mot de passe haché.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hache un mot de passe en clair.
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password):
            return None
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur lors de l'authentification : {str(e)}")
        

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Crée un token d'accès JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """
    Crée un token de rafraîchissement JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Fonction pour vérifier si un token est révoqué
def is_token_revoked(token: str, db: Session) -> bool:
    revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    return revoked_token is not None

def revoke_token(token: str, db: Session):
    revoked_token = RevokedToken(id=str(uuid.uuid4()), token=token)
    db.add(revoked_token)
    db.commit()
    db.refresh(revoked_token)


def extract_user_from_token(token: str, db: Session, is_refresh: bool = False):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if is_token_revoked(token, db):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token révoqué")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
        if is_refresh and token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de rafraîchissement requis")
        return {"user_id": user_id, "token": token}
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expiré")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Erreur de décodage du token")


# def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     return extract_user_from_token(token, db)
def get_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Décoder le token pour obtenir l'ID de l'utilisateur
    user_data = extract_user_from_token(token, db)
    user_id = user_data.get("user_id")

    # Charger l'utilisateur complet depuis la base de données
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    return user

def get_user_from_token_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Récupère l'utilisateur à partir du token s'il est valide et non révoqué.
    Si le token est absent ou invalide, retourne None sans lever d'exception.
    """
    if not token:
        return None  # Aucun token fourni, utilisateur non authentifié

    try:
        # Utiliser extract_user_from_token pour valider le token
        user_data = extract_user_from_token(token, db)
        user_id = user_data.get("user_id")

        # Rechercher l'utilisateur dans la base de données
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception:
        # En cas d'erreur (token invalide, expiré, etc.), retourner None
        return None

# def get_user_from_token_optional(
#     token: Optional[str] = Depends(oauth2_scheme),
#     db: Session = Depends(get_db)
# ) -> Optional[User]:
#     """
#     Récupère l'utilisateur à partir du token s'il est valide et non révoqué.
#     Si le token est absent ou invalide, retourne None sans lever d'exception.
#     """
#     if not token:
#         return None  # Aucun token fourni, utilisateur non authentifié

#     try:
#         # Utiliser extract_user_from_token pour valider le token
#         user_data = extract_user_from_token(token, db)
#         user_id = user_data.get("user_id")

#         # Rechercher l'utilisateur dans la base de données
#         user = db.query(User).filter(User.id == user_id).first()
#         return user
#     except Exception:
#         # En cas d'erreur (token invalide, expiré, etc.), retourner None
#         return None


def get_privileges(
    user_id: Optional[str],
    db: Session = Depends(get_db),
) -> List[str]:
    """
    Récupère tous les privilèges d'un utilisateur donné.
    
    Les privilèges peuvent être directement attribués via PrivilegeUser
    ou indirectement via les rôles auxquels l'utilisateur appartient (UserRole).
    
    Args:
        user_id (Optional[str]): L'ID de l'utilisateur. Doit être fourni.
        db (Session): Session SQLAlchemy pour interagir avec la base de données.
    
    Returns:
        List[str]: Liste des noms de privilèges uniques.
    
    Raises:
        HTTPException: Si `user_id` est None ou si une erreur survient lors de l'accès à la base de données.
    """
    # Validation précoce de l'ID utilisateur
    if not user_id:
        raise HTTPException(status_code=400, detail="L'ID de l'utilisateur est requis")

    try:
        # Initialiser un ensemble pour stocker les privilèges uniques
        privileges: Set[str] = set()

        # 1. Récupérer les privilèges directement attribués à l'utilisateur (via PrivilegeUser)
        privilege_users_query = (
            select(Privilege.name)
            .join(PrivilegeUser, Privilege.id == PrivilegeUser.privilege_id)
            .where(PrivilegeUser.owner_id == user_id, Privilege.active == True)
        )
        privilege_users = db.execute(privilege_users_query).scalars().all()
        privileges.update(privilege_users)

        # 2. Récupérer les privilèges via les rôles de l'utilisateur (via UserRole et PrivilegeRole)
        user_roles_query = (
            select(Role.id)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.owner_id == user_id, Role.active == True)
        )
        role_ids = db.execute(user_roles_query).scalars().all()

        if role_ids:
            role_privileges_query = (
                select(Privilege.name)
                .join(PrivilegeRole, Privilege.id == PrivilegeRole.privilege_id)
                .where(PrivilegeRole.role_id.in_(role_ids), Privilege.active == True)
            )
            role_privileges = db.execute(role_privileges_query).scalars().all()
            privileges.update(role_privileges)

        # Retourner la liste des privilèges uniques
        return list(privileges)

    except Exception as e:
        # Gestion des erreurs potentielles lors de l'accès à la base de données
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des privilèges : {str(e)}")
