from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from app.database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session

from app.models import models as models
from app.database import SessionLocal, engine, get_db
from app.schemas.users_schemas import Token, TokenData
from app import config_sething

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login', auto_error=False)

from passlib.context import CryptContext

# SECRET_KEY
# Algorithm
# Expriation time

SECRET_KEY = config_sething.secret_key
ALGORITHM = config_sething.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config_sething.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = config_sething.refresh_token_expire_days


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None or token in invalid_tokens:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

invalid_tokens = set()


def verify_access_token_optional(token: str):
    """Vérifie le token JWT sans lever d'exception si le token est invalide ou absent."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            return None  # Si l'ID utilisateur n'est pas trouvé dans le token
        token_data = TokenData(id=user_id)
    except JWTError:
        return None  # Si le token est invalide, retourne None
    return token_data

def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[models.User]:
    """
    Récupère l'utilisateur authentifié si le token est valide, sinon retourne None.
    """
    if not token:
        return None  # Aucun token fourni, utilisateur non authentifié

    token_data = verify_access_token_optional(token)
    if not token_data:
        return None  # Si le token est invalide, retourne None

    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user  # Retourne l'utilisateur authentifié ou None si non trouvé