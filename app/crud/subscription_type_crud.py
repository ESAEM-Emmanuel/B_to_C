from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.models import SubscriptionType
from app.schemas.subscription_types_schemas import SubscriptionTypeCreate, SubscriptionTypeUpdate
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
from app.models.models import StatusProposition
from enum import Enum


def get_by_id(db: Session, item_id: str):
    return db.query(SubscriptionType).filter(SubscriptionType.id == item_id).first()


def research(
    db: Session,
    name: Optional[str] = None,
    advertisements: Optional[int] = None,
    advertisements_bis: Optional[int] = None,
    advertisements_operation: Optional[str] = None,
    price: Optional[float] = None,
    price_bis: Optional[float] = None,
    price_operation: Optional[str] = None,
    price_max_article: Optional[float] = None,
    price_max_article_bis: Optional[float] = None,
    price_max_article_operation: Optional[str] = None,
    duration: Optional[float] = None,
    duration_bis: Optional[float] = None,
    duration_operation: Optional[str] = None,
    status: Optional[StatusProposition] = None,  # Utiliser directement StatusProposition
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
    sort_by: str = "name",
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
    if advertisements_operation and advertisements_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'advertisements_operation' doit être 'inf' ou 'sup'.")
    if price_operation and price_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'price_operation' doit être 'inf' ou 'sup'.")
    if price_max_article_operation and price_max_article_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'price_max_article_operation' doit être 'inf' ou 'sup'.")
    if duration_operation and duration_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'duration_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in SubscriptionType.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(SubscriptionType)

    # Filtres génériques
    if name:
        query = query.filter(SubscriptionType.name.ilike(f"%{name.lower()}%"))
    if status:
        query = query.filter(SubscriptionType.status == status)  # Correction : utiliser directement status
    if refnumber:
        query = query.filter(SubscriptionType.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(SubscriptionType.created_by == created_by)
    if updated_by is not None:
        query = query.filter(SubscriptionType.updated_by == updated_by)
    if active is not None:
        query = query.filter(SubscriptionType.active == active)

    # Filtres sur les dates
    # def apply_date_filter(field, value, bis_value, operation):
    #     if value and bis_value:
    #         start = datetime.combine(value, time(0, 0, 0))
    #         end = datetime.combine(bis_value, time(23, 59, 59))
    #         return field.between(start, end)
    #     elif value and operation == "inf":
    #         return field <= datetime.combine(value, time(23, 59, 59))
    #     elif value and operation == "sup":
    #         return field >= datetime.combine(value, time(0, 0, 0))
    #     elif value:
    #         return field == datetime.combine(value, time(0, 0, 0))
    #     return None
    def apply_date_filter(field, value, bis_value, operation):
    # Vérifier si le champ est une date
        if isinstance(value, (date, datetime)):
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
        
        # Gérer les champs numériques
        elif isinstance(value, (int, float)):
            if value and bis_value:
                return field.between(value, bis_value)
            elif value and operation == "inf":
                return field <= value
            elif value and operation == "sup":
                return field >= value
            elif value:
                return field == value

    filters = []
    for field, value, bis_value, operation in [
        (SubscriptionType.advertisements, advertisements, advertisements_bis, advertisements_operation),
        (SubscriptionType.price, price, price_bis, price_operation),
        (SubscriptionType.price_max_article, price_max_article, price_max_article_bis, price_max_article_operation),
        (SubscriptionType.duration, duration, duration_bis, duration_operation),
        (SubscriptionType.created_at, created_at, created_at_bis, created_at_operation),
        (SubscriptionType.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(SubscriptionType, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(SubscriptionType.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()

    return items, total_records


def create(db: Session, data: SubscriptionTypeCreate, current_user_id: str = None):
    # Normalisation des champs texte
    data.name = data.name.strip().lower()

    # Vérification des doublons
    existing = db.query(SubscriptionType).filter(SubscriptionType.name == data.name).first()
    if existing:
        raise ValueError(f"Un privilège avec le nom '{data.name}' existe déjà.")

    # Création de l'enregistrement
    try:
        concatenated_uuid = str(uuid4())
        unique_ref = generate_unique_num_ref(SubscriptionType, db)

        item = SubscriptionType(
            id=concatenated_uuid,
            refnumber=unique_ref,
            created_by=current_user_id,
            name=data.name,
            advertisements=data.advertisements,
            price=data.price,
            price_max_article=data.price_max_article, 
            duration=data.duration,
            status=data.status,
        )

        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du type d'abonnement : {str(e)}")

def update(db: Session, item_id: str, data: SubscriptionTypeUpdate, current_user_id: str):
    item = db.query(SubscriptionType).filter(SubscriptionType.id == item_id).first()
    if not item:
        raise ValueError("L'utilisateur n'a pas été trouvé.")

    # Détection des conflits
    filters = [
        (SubscriptionType.name == data.name.lower()),
    ]
    existing = db.query(SubscriptionType).filter(or_(*filters)).first()
    if existing and existing.id != item.id:
        conflicts = []
        if existing.name == data.name:
            conflicts.append("nom")
        conflict_message = ", ".join(conflicts)
        raise ValueError(f"Un privilège existe déjà avec les champs suivants : {conflict_message}.")

    # Mise à jour des champs
    if data.name is not None:
        item.name = data.name.lower()
    if data.advertisements is not None:
        item.advertisements = data.advertisements
    if data.price is not None:
        item.price = data.price
    if data.price_max_article is not None:
        item.price_max_article = data.price_max_article
    if data.duration is not None:
        item.duration = data.duration
    if data.status is not None:
        item.status = data.status

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(SubscriptionType).filter(SubscriptionType.id == item_id, SubscriptionType.active == True).first()
    if not item:
        raise ValueError("SubscriptionType not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(SubscriptionType).filter(SubscriptionType.id == item_id, SubscriptionType.active == False).first()
    if not item:
        raise ValueError("SubscriptionType not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item