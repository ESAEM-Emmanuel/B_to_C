from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import TaxInterval, TaxInterval, StatusProposition
from app.schemas.tax_intervals_schemas import TaxIntervalCreate, TaxIntervalUpdate
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
    return db.query(TaxInterval).filter(TaxInterval.id == item_id).first()


def research(
    db: Session,
    min_price: Optional[float] = None,
    min_price_bis: Optional[float] = None,
    min_price_operation: Optional[str] = None,
    max_price: Optional[float] = None,
    max_price_bis: Optional[float] = None,
    max_price_operation: Optional[str] = None,
    daily_rate: Optional[float] = None,
    daily_rate_bis: Optional[float] = None,
    daily_rate_operation: Optional[str] = None,
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
    sort_by: str = "daily_rate",
    skip: int = 0,
    limit: int = 100,
):
    # Validation des paramètres
    if order not in ["asc", "desc"]:
        raise ValueError("Le paramètre 'order' doit être 'asc' ou 'desc'.")
    if min_price_operation and min_price_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'min_price_operation' doit être 'inf' ou 'sup'.")
    if max_price_operation and max_price_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'max_price_operation' doit être 'inf' ou 'sup'.")
    if daily_rate_operation and daily_rate_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'daily_rate_operation' doit être 'inf' ou 'sup'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in TaxInterval.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(TaxInterval)

    # Filtres génériques

    if refnumber:
        query = query.filter(TaxInterval.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(TaxInterval.created_by == created_by)
    if updated_by is not None:
        query = query.filter(TaxInterval.updated_by == updated_by)
    if active is not None:
        query = query.filter(TaxInterval.active == active)

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
        (TaxInterval.min_price, min_price, min_price_bis, min_price_operation),
        (TaxInterval.max_price, max_price, max_price_bis, max_price_operation),
        (TaxInterval.daily_rate, daily_rate, daily_rate_bis, daily_rate_operation),
        (TaxInterval.created_at, created_at, created_at_bis, created_at_operation),
        (TaxInterval.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(TaxInterval, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(TaxInterval.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records


def create(
    db: Session,
    data: TaxIntervalCreate,
    current_user_id: str = None
):
    
    # Vérification des doublons
    existing = db.query(TaxInterval).filter(
        and_(
            TaxInterval.min_price == data.min_price,
            TaxInterval.max_price == data.max_price,
            TaxInterval.daily_rate == data.daily_rate
        )
    ).first()

    if existing:
        raise ValueError(f"L'intervalle de taxe avec les données : '{data.min_price}', '{data.max_price}' et '{data.daily_rate}' existe déjà.")

    # Génération d'un ID unique et d'une référence unique
    concatenated_uuid = str(uuid4())
    unique_ref = generate_unique_num_ref(TaxInterval, db)
    print('existing : ', existing, " concatenated_uuid : ", concatenated_uuid, " unique_ref : ", unique_ref)

    # Création de l'objet TaxInterval
    try:
        item = TaxInterval(
            id=concatenated_uuid,
            refnumber=unique_ref,
            min_price=data.min_price,
            max_price=data.max_price,
            daily_rate=data.daily_rate,
            created_by=current_user_id,
        )

        # Ajout à la base de données
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'interval : {str(e)}")


def update(db: Session, item_id: str, data: TaxIntervalUpdate, current_user_id: str):
    # Récupération de l'élément à mettre à jour
    item = db.query(TaxInterval).filter(TaxInterval.id == item_id).first()
    if not item:
        raise ValueError("l'intervalle n'a pas été trouvé.")



    # Mise à jour des champs
    if data.min_price is not None and data.max_price is None:
        if data.min_price > item.max_price:
            raise ValueError(f"Le prix min : '{data.min_price}', doit être inférieux au prix max '{item.max_price}' de cet interval.")
        item.min_price = data.min_price  # Assignation manquante ajoutée ici

    elif data.max_price is not None and data.min_price is None:
        if data.max_price < item.min_price:
            raise ValueError(f"Le prix max : '{data.max_price}', doit être supérieur au prix min '{item.min_price}' de cet interval.")  
        item.max_price = data.max_price

    elif data.min_price is not None and data.max_price is not None:
        if data.max_price < data.min_price:
            raise ValueError(f"Le prix max : '{data.max_price}', doit être supérieur au prix min '{data.min_price}' de cet interval.") 
        item.max_price = data.max_price
        item.min_price = data.min_price

    # Mise à jour des autres champs
    if data.daily_rate is not None:
        item.daily_rate = data.daily_rate

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(TaxInterval).filter(TaxInterval.id == item_id, TaxInterval.active == True).first()
    if not item:
        raise ValueError("TaxInterval not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(TaxInterval).filter(TaxInterval.id == item_id, TaxInterval.active == False).first()
    if not item:
        raise ValueError("TaxInterval not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item