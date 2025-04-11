from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import Subscription, SubscriptionType, StatusProposition
from app.schemas.subscriptions_schemas import SubscriptionCreate, SubscriptionUpdate
from app.utils.utils import (
    generate_unique_num_ref,
    )
from uuid import uuid4
from typing import Optional, List
from datetime import date, datetime, time, timedelta, timezone
from sqlalchemy import asc, desc
from fastapi import HTTPException
from pydantic import EmailStr
import bcrypt


def get_by_id(db: Session, item_id: str):
    item = db.query(Subscription).filter(Subscription.id == item_id).first()
    if not item:
        raise ValueError("Subscription not found or already deleted.")
    item.is_read = True
    db.commit()
    db.refresh(item)
    return item
    # return db.query(Subscription).filter(Subscription.id == item_id).first()


def research(
    db: Session,
    subscription_type_id: Optional[str] = None,
    owner_id: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[date] = None,
    start_date_bis: Optional[date] = None,
    start_date_operation: Optional[str] = None,
    expiration_date: Optional[date] = None,
    expiration_date_bis: Optional[date] = None,
    expiration_date_operation: Optional[str] = None,
    remaining_advertisements: Optional[int] = None,
    remaining_advertisements_bis: Optional[int] = None,
    remaining_advertisements_operation: Optional[str] = None,
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
    if start_date_operation and start_date_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'start_date_operation' doit être 'inf' ou 'sup'.")
    if expiration_date_operation and expiration_date_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'expiration_date_operation' doit être 'inf' ou 'sup'.")
    if remaining_advertisements_operation and remaining_advertisements_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'remaining_advertisements_operation' doit être 'inf' ou 'sup'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in Subscription.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(Subscription).options(joinedload(Subscription.owner), 
    joinedload(Subscription.subscription_type))

    

    # Filtres génériques
    if subscription_type_id:
        query = query.filter(Subscription.subscription_type_id == subscription_type_id)
    if owner_id:
        query = query.filter(Subscription.owner_id== owner_id)
    if refnumber:
        query = query.filter(Subscription.refnumber.ilike(f"%{refnumber}%"))
    if description:
        query = query.filter(Subscription.description.ilike(f"%{description}%"))
    if is_read is not None:
        query = query.filter(Subscription.is_read == is_read)
    if created_by is not None:
        query = query.filter(Subscription.created_by == created_by)
    if updated_by is not None:
        query = query.filter(Subscription.updated_by == updated_by)
    if active is not None:
        query = query.filter(Subscription.active == active)

    # Filtres sur les dates
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
        (Subscription.start_date, start_date, start_date_bis, start_date_operation),
        (Subscription.expiration_date, expiration_date, expiration_date_bis, expiration_date_operation),
        (Subscription.remaining_advertisements, remaining_advertisements, remaining_advertisements_bis, remaining_advertisements_operation),
        (Subscription.created_at, created_at, created_at_bis, created_at_operation),
        (Subscription.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(Subscription, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(Subscription.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records


def create(
    db: Session,
    data: SubscriptionCreate,
    current_user_id: str = None
):
    # Validation du type d'abonnement
    subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == data.subscription_type_id).first()
    if not subscription_type:
        raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")

    # Gestion du propriétaire (owner_id)
    if data.owner_id is None:
        if current_user_id is None:
            raise HTTPException(status_code=400, detail="Impossible de déterminer le propriétaire de l'abonnement.")
        data.owner_id = current_user_id

    # Calcul de la date d'expiration
    try:
        expiration_date = data.start_date + timedelta(days=subscription_type.duration)
    except TypeError:
        raise HTTPException(status_code=400, detail="La durée du type d'abonnement ou la date de début est invalide.")

    # Génération d'un ID unique et d'une référence unique
    concatenated_uuid = str(uuid4())
    unique_ref = generate_unique_num_ref(Subscription, db)

    # Création de l'objet Subscription
    try:
        item = Subscription(
            id=concatenated_uuid,
            refnumber=unique_ref,
            subscription_type_id=data.subscription_type_id,
            owner_id=data.owner_id,
            description=data.description,
            start_date=data.start_date,
            expiration_date=expiration_date,
            remaining_advertisements=subscription_type.advertisements,
            created_by=current_user_id,
        )

        # Ajout à la base de données
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'abonnement : {str(e)}")


def update(db: Session, item_id: str, data: SubscriptionUpdate, current_user_id: str):
    # Récupération de l'élément à mettre à jour
    item = db.query(Subscription).filter(Subscription.id == item_id).first()
    if not item:
        raise ValueError("L'utilisateur n'a pas été trouvé.")

    # Convertir item.start_date en offset-naive si elle est offset-aware
    if item.start_date and item.start_date.tzinfo is not None:
        item.start_date = item.start_date.replace(tzinfo=None)

    # Vérification que start_date ne peut pas être modifiée après le début de l'événement
    if data.start_date is not None:
        if item.start_date and datetime.now() >= item.start_date:
            raise HTTPException(
                status_code=400,
                detail="La date de début ne peut pas être modifiée après le début de l'événement."
            )
        if data.start_date < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="La nouvelle date de début ne peut pas être dans le Passé."
            )

    # Mise à jour des champs
    if data.start_date is not None and data.subscription_type_id is None:
        print("Ici1")
        item.start_date = data.start_date
        subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == item.subscription_type_id).first()
        if not subscription_type:
            raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")
        expiration_date = data.start_date + timedelta(days=subscription_type.duration)
        item.expiration_date = expiration_date  # Assignation manquante ajoutée ici
        print("expiration_date :", item.expiration_date, " = ", expiration_date)

    elif data.subscription_type_id is not None and data.start_date is None:
        print("Ici2")
        item.subscription_type_id = data.subscription_type_id
        subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == data.subscription_type_id).first()
        if not subscription_type:
            raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")
        item.expiration_date = item.start_date + timedelta(days=subscription_type.duration)
        item.remaining_advertisements = subscription_type.advertisements
        print("expiration_date :", item.expiration_date, " = ", item.expiration_date)

    elif data.subscription_type_id is not None and data.start_date is not None:
        print("Ici3")
        item.subscription_type_id = data.subscription_type_id
        subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == data.subscription_type_id).first()
        if not subscription_type:
            raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")
        item.expiration_date = data.start_date + timedelta(days=subscription_type.duration)
        item.remaining_advertisements = subscription_type.advertisements
        print("expiration_date :", item.expiration_date, " = ", item.expiration_date)

    # Mise à jour des autres champs
    if data.owner_id is not None:
        item.owner_id = data.owner_id

    if data.description is not None:
        item.description = data.description

    if data.is_read is not None:
        item.is_read = data.is_read

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

# def update(db: Session, item_id: str, data: SubscriptionUpdate, current_user_id: str):
#     item = db.query(Subscription).filter(Subscription.id == item_id).first()
#     if not item:
#         raise ValueError("L'utilisateur n'a pas été trouvé.")

#     # Mise à jour des champs
#     if data.start_date is not None and data.subscription_type_id is None:
#         print("Ici1")
#         if data.start_date > date.now(tz=None):
#             raise HTTPException(status_code=404, detail="La date de début ne peux être remplacer après le début.")
#         item.start_date = data.start_date
#         subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == item.subscription_type_id).first()
#         if not subscription_type:
#             raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")
#         expiration_date = data.start_date + timedelta(days=subscription_type.duration)
#         item.expiration_date = expiration_date  # Assignation manquante ajoutée ici
#         print("expiration_date :", item.expiration_date, " = ", expiration_date)
#     elif data.subscription_type_id is not None and data.start_date is None:
#         print("Ici2")
#         item.subscription_type_id = data.subscription_type_id
#         subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == data.subscription_type_id).first()
#         if not subscription_type:
#             raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")
#         item.expiration_date = item.start_date + timedelta(days=subscription_type.duration)
#         item.remaining_advertisements = subscription_type.advertisements
#         print("expiration_date :", item.expiration_date, " = ", item.expiration_date)
#     elif data.subscription_type_id is not None and data.start_date is not None:
#         print("Ici3")
#         if data.start_date > date.now(tz=None):
#             raise HTTPException(status_code=404, detail="La date de début ne peux être remplacer après le début.")
#         item.subscription_type_id = data.subscription_type_id
#         subscription_type = db.query(SubscriptionType).filter(SubscriptionType.id == data.subscription_type_id).first()
#         if not subscription_type:
#             raise HTTPException(status_code=404, detail="Le type d'abonnement spécifié n'existe pas.")
#         item.expiration_date = data.start_date + timedelta(days=subscription_type.duration)
#         item.remaining_advertisements = subscription_type.advertisements
#         print("expiration_date :", item.expiration_date, " = ", item.expiration_date)

#     if data.owner_id is not None:
#         item.owner_id = data.owner_id

#     if data.description is not None:
#         item.description = data.description

#     if data.is_read is not None:
#         item.is_read = data.is_read

#     item.updated_by = current_user_id
#     db.commit()
#     db.refresh(item)
#     return item

    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(Subscription).filter(Subscription.id == item_id, Subscription.active == True).first()
    if not item:
        raise ValueError("Subscription not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(Subscription).filter(Subscription.id == item_id, Subscription.active == False).first()
    if not item:
        raise ValueError("Subscription not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item