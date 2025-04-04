from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import PrivilegeUser
from app.schemas.privilege_users_schemas import PrivilegeUserCreate, PrivilegeUserUpdate
from app.utils.utils import (
    generate_unique_num_ref,
    )
from uuid import uuid4
from typing import Optional, List
from datetime import date, datetime, time
from sqlalchemy import asc, desc
from fastapi import HTTPException
from pydantic import EmailStr
import bcrypt


def get_by_id(db: Session, item_id: str):
    return db.query(PrivilegeUser).filter(PrivilegeUser.id == item_id).first()


def research(
    db: Session,
    privilege_id: Optional[str] = None,
    owner_id: Optional[str] = None,
    refnumber: Optional[str] = None,
    created_by: Optional[str] = None,
    created_at: Optional[date] = None,
    created_at_bis: Optional[date] = None,
    created_at_operation: Optional[str] = None,
    updated_by: Optional[str] = None,
    updated_at: Optional[date] = None,
    updated_at_bis: Optional[date] = None,
    updated_at_operation: Optional[str] = None,
    active: Optional[bool] = None,
    order: str = "asc",
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 100,
):
    # Validation des paramètres
    if order not in ["asc", "desc"]:
        raise ValueError("Le paramètre 'order' doit être 'asc' ou 'desc'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in PrivilegeUser.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")


    # Construction de la requête
    # query = db.query(PrivilegeUser)
    query = db.query(PrivilegeUser).options(joinedload(PrivilegeUser.owner), 
    joinedload(PrivilegeUser.privilege))

    # Filtres génériques
    if privilege_id:
        query = query.filter(PrivilegeUser.privilege_id == privilege_id)
    if owner_id:
        query = query.filter(PrivilegeUser.owner_id== owner_id)
    if refnumber:
        query = query.filter(PrivilegeUser.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(PrivilegeUser.created_by == created_by)
    if updated_by is not None:
        query = query.filter(PrivilegeUser.updated_by == updated_by)
    if active is not None:
        query = query.filter(PrivilegeUser.active == active)

    # Filtres sur les dates
    def apply_date_filter(field, value, bis_value, operation):
        if value and bis_value:
            start = datetime.combine(value, time(0, 0, 0))
            end = datetime.combine(bis_value, time(23, 59, 59))
            return field.between(start, end)
        elif value and operation == "inf":
            return field <= datetime.combine(value, time(23, 59, 59))
        elif value and operation == "sup":
            return field >= datetime.combine(value, time(0, 0, 0))
        elif value:
            return field == datetime.combine(value, time(0, 0, 0))
        return None

    filters = []
    for field, value, bis_value, operation in [
        (PrivilegeUser.created_at, created_at, created_at_bis, created_at_operation),
        (PrivilegeUser.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(PrivilegeUser, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(PrivilegeUser.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records




def create(
    db: Session, 
    data: PrivilegeUserCreate, 
    current_user_id: Optional[str] = None
):
    """
    Crée une nouvelle association PrivilegeUser après vérification des doublons.
    
    Args:
        db (Session): La session de base de données.
        data (PrivilegeUserCreate): Les données à insérer.
        current_user_id (Optional[str]): L'ID de l'utilisateur actuel (facultatif).
    
    Returns:
        PrivilegeUser: L'objet PrivilegeUser créé.
    
    Raises:
        ValueError: Si une association identique existe déjà.
        Exception: En cas d'erreur lors de la création.
    """
    # Vérification des doublons
    filters = [
        PrivilegeUser.privilege_id == data.privilege_id,
        PrivilegeUser.owner_id == data.owner_id
    ]
    
    existing = db.query(PrivilegeUser).filter(and_(*filters)).first()
    if existing:
        raise ValueError(
            "L'association existe déjà avec les champs suivants : privilege_id et owner_id."
        )
    
    try:
        # Génération de l'UUID et du numéro de référence unique
        concatenated_uuid = str(uuid4())
        unique_ref = generate_unique_num_ref(PrivilegeUser, db)

        # Création de l'objet PrivilegeUser
        item = PrivilegeUser(
            id=concatenated_uuid,
            refnumber=unique_ref,
            created_by=current_user_id,
            **data.dict()  # Conversion en dictionnaire
        )

        # Ajout et validation dans la base de données
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        # Rollback en cas d'erreur
        db.rollback()
        raise Exception(f"Erreur lors de la création du privilège : {str(e)}")



def update(db: Session, item_id: str, data: PrivilegeUserUpdate, current_user_id: str):
    item = db.query(PrivilegeUser).filter(PrivilegeUser.id == item_id).first()
    if not item:
        raise ValueError("L'utilisateur n'a pas été trouvé.")

    # Détection des conflits
    filters = [
        PrivilegeUser.privilege_id == data.privilege_id,
        PrivilegeUser.owner_id == data.owner_id
    ]
    
    existing = db.query(PrivilegeUser).filter(and_(*filters)).first()
    if existing and existing.id != item.id:
        raise ValueError(
            f"L'association existe déjà avec les champs suivants : owner_id={data.owner_id}, privilege_id={data.privilege_id}."
        )
    # Mise à jour des champs
    if data.owner_id is not None:
        item.owner_id = data.owner_id
    if data.privilege_id is not None:
        item.privilege_id = data.privilege_id

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(PrivilegeUser).filter(PrivilegeUser.id == item_id, PrivilegeUser.active == True).first()
    if not item:
        raise ValueError("PrivilegeUser not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(PrivilegeUser).filter(PrivilegeUser.id == item_id, PrivilegeUser.active == False).first()
    if not item:
        raise ValueError("PrivilegeUser not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item