from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import Notification
from app.schemas.notifications_schemas import NotificationCreate, NotificationUpdate
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
    item = db.query(Notification).filter(Notification.id == item_id).first()
    if not item:
        raise ValueError("Notification not found or already deleted.")
    item.is_read = True
    db.commit()
    db.refresh(item)
    return item
    # return db.query(Notification).filter(Notification.id == item_id).first()


def research(
    db: Session,
    owner_id: Optional[str] = None,
    article_id: Optional[str] = None,
    offender_id: Optional[str] = None,
    description: Optional[str] = None,
    is_read: Optional[bool] = None,
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
    valid_sort_columns = [column.key for column in Notification.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(Notification)

    # Filtres génériques
    if article_id:
        query = query.filter(Notification.article_id == article_id)
    if description:
        query = query.filter(Notification.description == description)
    if refnumber:
        query = query.filter(Notification.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(Notification.created_by == created_by)
    if updated_by is not None:
        query = query.filter(Notification.updated_by == updated_by)
    if active is not None:
        query = query.filter(Notification.active == active)
    if active is not None:
        query = query.filter(Notification.active == active)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

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
        (Notification.created_at, created_at, created_at_bis, created_at_operation),
        (Notification.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(Notification, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(Notification.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all() 
    # print("items : ", items.format_map()    ) 
    return items, total_records


def create(
    db: Session, 
    data: NotificationCreate, 
    current_user_id: Optional[str] = None
) -> Notification:
    """
    Crée une nouvelle association Notification après vérification des doublons.
    
    Args:
        db (Session): La session de base de données.
        data (NotificationCreate): Les données à insérer.
        current_user_id (Optional[str]): L'ID de La notification actuel (facultatif).
    
    Returns:
        Notification: L'objet Notification créé.
    
    Raises:
        ValueError: Si une association identique existe déjà.
        HTTPException: En cas d'erreur lors de la création ou mise à jour.
    """
        # Si aucun doublon n'existe, on crée un nouveau Notification
    try:
        # Génération de l'UUID et du numéro de référence unique
        concatenated_uuid = str(uuid4())
        unique_ref = generate_unique_num_ref(Notification, db)

        # Création de l'objet Notification
        item = Notification(
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
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du Notification : {str(e)}")

def update(db: Session, item_id: str, data: NotificationUpdate, current_user_id: str):
    item = db.query(Notification).filter(Notification.id == item_id).first()
    if not item:
        raise ValueError("La notification n'a pas été trouvé.")

    # Mise à jour des champs
    if data.article_id is not None:
        item.article_id = data.article_id
    if data.description is not None:
        item.description = data.description.lower()
    if data.is_read is not None:
        item.is_read = data.is_read

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(Notification).filter(Notification.id == item_id, Notification.active == True).first()
    if not item:
        raise ValueError("Notification not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(Notification).filter(Notification.id == item_id, Notification.active == False).first()
    if not item:
        raise ValueError("Notification not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item