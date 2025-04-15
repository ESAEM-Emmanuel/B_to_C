from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import SlidingScaleTariffs
from app.schemas.sliding_scale_tariffs_schemas import SlidingScaleTariffsCreate,SlidingScaleTariffsUpdate
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
    return db.query(SlidingScaleTariffs).filter(SlidingScaleTariffs.id == item_id).first()


def research(
    db: Session,
    days_min: Optional[int] = None,
    days_min_bis: Optional[int] = None,
    days_min_operation: Optional[str] = None,
    max_days: Optional[int] = None,
    max_days_bis: Optional[int] = None,
    max_days_operation: Optional[str] = None,
    rate: Optional[float] = None,
    rate_bis: Optional[float] = None,
    rate_operation: Optional[str] = None,
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
    sort_by: str = "rate",
    skip: int = 0,
    limit: int = 100,
):
    # Validation des paramètres
    if order not in ["asc", "desc"]:
        raise ValueError("Le paramètre 'order' doit être 'asc' ou 'desc'.")
    if days_min_operation and days_min_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'days_min_operation' doit être 'inf' ou 'sup'.")
    if max_days_operation and max_days_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'max_days_operation' doit être 'inf' ou 'sup'.")
    if rate_operation and rate_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'rate_operation' doit être 'inf' ou 'sup'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in SlidingScaleTariffs.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(SlidingScaleTariffs)

    # Filtres génériques

    if refnumber:
        query = query.filter(SlidingScaleTariffs.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(SlidingScaleTariffs.created_by == created_by)
    if updated_by is not None:
        query = query.filter(SlidingScaleTariffs.updated_by == updated_by)
    if active is not None:
        query = query.filter(SlidingScaleTariffs.active == active)

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
        (SlidingScaleTariffs.days_min, days_min, days_min_bis, days_min_operation),
        (SlidingScaleTariffs.max_days, max_days, max_days_bis, max_days_operation),
        (SlidingScaleTariffs.rate, rate, rate_bis, rate_operation),
        (SlidingScaleTariffs.created_at, created_at, created_at_bis, created_at_operation),
        (SlidingScaleTariffs.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(SlidingScaleTariffs, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(SlidingScaleTariffs.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records


from sqlalchemy import and_

def create(
    db: Session,
    data: SlidingScaleTariffsCreate,
    current_user_id: str = None
):
    
    # Vérification des doublons
    existing = db.query(SlidingScaleTariffs).filter(
        and_(
            SlidingScaleTariffs.days_min == data.days_min,
            SlidingScaleTariffs.max_days == data.max_days,
            SlidingScaleTariffs.rate == data.rate
        )
    ).first()

    if existing:
        raise ValueError(f"L'intervalle de taxe avec les données : '{data.days_min}', '{data.max_days}' et '{data.rate}' existe déjà.")

    # Génération d'un ID unique et d'une référence unique
    concatenated_uuid = str(uuid4())
    unique_ref = generate_unique_num_ref(SlidingScaleTariffs, db)

    # Création de l'objet SlidingScaleTariffs
    try:
        item = SlidingScaleTariffs(
            id=concatenated_uuid,
            refnumber=unique_ref,
            days_min=data.days_min,
            max_days=data.max_days,
            rate=data.rate,
            created_by=current_user_id,
        )

        # Ajout à la base de données
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'interval : {str(e)}")


def update(db: Session, item_id: str, data: SlidingScaleTariffsUpdate, current_user_id: str):
    # Récupération de l'élément à mettre à jour
    item = db.query(SlidingScaleTariffs).filter(SlidingScaleTariffs.id == item_id).first()
    if not item:
        raise ValueError("l'intervalle n'a pas été trouvé.")



    # Mise à jour des champs
    if data.days_min is not None and data.max_days is None:
        if data.days_min > item.max_days:
            raise ValueError(f"Le nb min de jour : '{data.days_min}', doit être inférieux au nb max de jour '{item.max_days}' de cet interval.")
        item.days_min = data.days_min  # Assignation manquante ajoutée ici

    elif data.max_days is not None and data.days_min is None:
        if data.max_days < item.days_min:
            raise ValueError(f"Le nb max de jour : '{data.max_days}', doit être supérieur au nb min de jour '{item.days_min}' de cet interval.")  
        item.max_days = data.max_days

    elif data.days_min is not None and data.max_days is not None:
        if data.max_days < data.days_min:
            raise ValueError(f"Le nb max de jour : '{data.max_days}', doit être supérieur au nb min de jour '{data.days_min}' de cet interval.") 
        item.max_days = data.max_days
        item.days_min = data.days_min

    # Mise à jour des autres champs
    if data.rate is not None:
        item.rate = data.rate

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(SlidingScaleTariffs).filter(SlidingScaleTariffs.id == item_id, SlidingScaleTariffs.active == True).first()
    if not item:
        raise ValueError("SlidingScaleTariffs not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(SlidingScaleTariffs).filter(SlidingScaleTariffs.id == item_id, SlidingScaleTariffs.active == False).first()
    if not item:
        raise ValueError("SlidingScaleTariffs not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item