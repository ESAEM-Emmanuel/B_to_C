# import sys
# import os
from fastapi import Depends, HTTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, PrivilegeUser, UserRole, Role, PrivilegeRole, Privilege, BaseMixin
from datetime import datetime
from typing import Type, List, Optional
from app.schemas.utils_schemas import UserInfo
from app.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# sys.path.append("..")

# Hsher Password
def hash(password: str):
    return pwd_context.hash(password)

# Verify token
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def send_email(to_email: str, subject: str, content: str):
    # Paramètres d'authentification du serveur SMTP
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_username = settings.SMTP_USERNAME
    smtp_password = settings.SMTP_PASSWORD

    # Création de l'objet du message e-mail
    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject

    # Ajout du contenu du message
    msg.attach(MIMEText(content, "plain"))

    # Connexion au serveur SMTP et envoi de l'e-mail
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


def serialize_user(user_id: str, db: Session):
    if not user_id:
        return None
    user_query = db.query(models.User).filter(models.User.id == user_id).first()
    return UserInfo.from_orm(user_query) if user_query else None

   
def generate_unique_num_ref(
    model: Type[BaseMixin], 
    db: Session = None
) -> str:
    """
    Génère un numéro de référence unique pour un modèle donné.
    Le format est : "NUM_REF/codefin", où NUM_REF est incrémenté et codefin est "MM/YYYY".
    
    :param model: Le modèle SQLAlchemy pour lequel générer le numéro de référence.
    :param db: Une session SQLAlchemy pour accéder à la base de données.
    :return: Le numéro de référence unique.
    """
    if not db:
        raise ValueError("La session de base de données (db) est requise.")
    
    # Formatage de la date actuelle (MM/YYYY)
    codefin = datetime.now().strftime("%m/%Y")
    
    # Récupérer le nombre d'enregistrements existants avec un refnumber se terminant par codefin
    existing_records = (
        db.query(model)
        .filter(model.refnumber.like(f"%/{codefin}"))
        .count()
    )
    # Calculer le nouveau NUM_REF
    NUM_REF = 10001 + existing_records
    
    # Concaténer NUM_REF et codefin pour former le nouveau numéro de référence
    concatenated_num_ref = f"{NUM_REF}/{codefin}"
    
    return concatenated_num_ref

def get_privileges(
    user_id: Optional[str],
    db: Session = Depends(get_db),
) -> List[str]:
    """
    Récupère tous les privilèges d'un utilisateur donné.
    Les privilèges peuvent être directement attribués via PrivilegeUser
    ou indirectement via les rôles auxquels l'utilisateur appartient (UserRole).
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="L'ID de l'utilisateur est requis")

    # Initialiser un ensemble pour stocker les privilèges uniques
    privileges = set()

    # 1. Récupérer les privilèges directement attribués à l'utilisateur (via PrivilegeUser)
    privilege_users = (
        db.query(Privilege.name)
        .join(PrivilegeUser, Privilege.id == PrivilegeUser.privilege_id)
        .filter(PrivilegeUser.owner_id == user_id, Privilege.active == True)
        .all()
    )
    privileges.update([privilege[0] for privilege in privilege_users])

    # 2. Récupérer les privilèges via les rôles de l'utilisateur (via UserRole et PrivilegeRole)
    user_roles = (
        db.query(Role.id)
        .join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.owner_id == user_id, Role.active == True)
        .all()
    )
    role_ids = [role[0] for role in user_roles]

    if role_ids:
        role_privileges = (
            db.query(Privilege.name)
            .join(PrivilegeRole, Privilege.id == PrivilegeRole.privilege_id)
            .filter(PrivilegeRole.role_id.in_(role_ids), Privilege.active == True)
            .all()
        )
        privileges.update([privilege[0] for privilege in role_privileges])

    # Retourner la liste des privilèges uniques
    return list(privileges)

def get_user_by_id(db: Session, user_id: str) -> Optional[UserInfo]:
    """
    Récupère un utilisateur par son ID et le sérialise avec UserInfo.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return UserInfo.from_orm(user)
    return None

