
import os
import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, status

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from app import config_sething
load_dotenv('.env')

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import  get_db
from app.models import models as models
from app.database import engine, get_db
from app.models import models
from typing import Optional


from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hsher Password
def hash(password: str):
    return pwd_context.hash(password)

# Verify token
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# send mail
class Envs:
    smtp_host_sys = config_sething.smtp_host
    smtp_port_sys = config_sething.smtp_port
    smtp_username_sys = config_sething.smtp_username
    smtp_password_sys = config_sething.smtp_password

def send_email(to_email: str, subject: str, content: str):
    # Paramètres d'authentification du serveur SMTP
    smtp_host = Envs.smtp_host_sys
    smtp_port = Envs.smtp_port_sys
    smtp_username = Envs.smtp_username_sys
    smtp_password = Envs.smtp_password_sys

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


# def get_privileges(
#     user_id: Optional[str]= None,
#     profil_id: Optional[str]= None,
#     entertainment_site_id: Optional[str]= None,
#     db: Session = Depends(get_db),):
#     if profil_id:
#         profil = db.query(models.Profil).filter(
#             models.Profil.id == profil_id, models.Profil.active == True
#         ).first()
#     else:
#         profil = db.query(models.Profil).filter(
#             models.Profil.owner == user_id,
#             models.Profil.entertainment_site_id == entertainment_site_id,
#             models.Profil.active == True
#         ).first()
    
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

#     return privileges