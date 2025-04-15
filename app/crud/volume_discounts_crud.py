from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import VolumeDiscounts
from app.schemas.volume_discounts_schemas import VolumeDiscountsCreate,VolumeDiscountsUpdate
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
    return db.query(VolumeDiscounts).filter(VolumeDiscounts.id == item_id).first()


def research(
    db: Session,
    threshold: Optional[int] = None,
    threshold_bis: Optional[int] = None,
    threshold_operation: Optional[str] = None,
    reduction: Optional[float] = None,
    reduction_bis: Optional[float] = None,
    reduction_operation: Optional[str] = None,
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
    sort_by: str = "reduction",
    skip: int = 0,
    limit: int = 100,
):
    # Validation des paramètres
    if order not in ["asc", "desc"]:
        raise ValueError("Le paramètre 'order' doit être 'asc' ou 'desc'.")
    if threshold_operation and threshold_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'threshold_operation' doit être 'inf' ou 'sup'.")
    if reduction_operation and reduction_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'reduction_operation' doit être 'inf' ou 'sup'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in VolumeDiscounts.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(VolumeDiscounts)

    # Filtres génériques

    if refnumber:
        query = query.filter(VolumeDiscounts.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(VolumeDiscounts.created_by == created_by)
    if updated_by is not None:
        query = query.filter(VolumeDiscounts.updated_by == updated_by)
    if active is not None:
        query = query.filter(VolumeDiscounts.active == active)

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
        (VolumeDiscounts.threshold, threshold, threshold_bis, threshold_operation),
        (VolumeDiscounts.reduction, reduction, reduction_bis, reduction_operation),
        (VolumeDiscounts.created_at, created_at, created_at_bis, created_at_operation),
        (VolumeDiscounts.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(VolumeDiscounts, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(VolumeDiscounts.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records


from sqlalchemy import and_

def create(
    db: Session,
    data: VolumeDiscountsCreate,
    current_user_id: str = None
):
    
    # Vérification des doublons
    existing = db.query(VolumeDiscounts).filter(
        and_(
            VolumeDiscounts.threshold == data.threshold,
            VolumeDiscounts.reduction == data.reduction
        )
    ).first()

    if existing:
        raise ValueError(f"la reduction de taxe avec les données : '{data.threshold}' et '{data.reduction}' existe déjà.")

    # Génération d'un ID unique et d'une référence unique
    concatenated_uuid = str(uuid4())
    unique_ref = generate_unique_num_ref(VolumeDiscounts, db)

    # Création de l'objet VolumeDiscounts
    try:
        item = VolumeDiscounts(
            id=concatenated_uuid,
            refnumber=unique_ref,
            threshold=data.threshold,
            reduction=data.reduction,
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


def update(db: Session, item_id: str, data: VolumeDiscountsUpdate, current_user_id: str):
    # Récupération de l'élément à mettre à jour
    item = db.query(VolumeDiscounts).filter(VolumeDiscounts.id == item_id).first()
    if not item:
        raise ValueError("la reduction n'a pas été trouvé.")
    # Vérification des doublons
    existing = db.query(VolumeDiscounts).filter(
        and_(
            VolumeDiscounts.threshold == data.threshold,
            VolumeDiscounts.reduction == data.reduction
        )
    ).first()

    if existing and existing.id != item_id:
        raise ValueError(f"la reduction de taxe avec les données : '{data.threshold}' et '{data.reduction}' existe déjà.")


    # Mise à jour des autres champs
    if data.threshold is not None:
        item.threshold = data.threshold
    if data.reduction is not None:
        item.reduction = data.reduction

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(VolumeDiscounts).filter(VolumeDiscounts.id == item_id, VolumeDiscounts.active == True).first()
    if not item:
        raise ValueError("VolumeDiscounts not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(VolumeDiscounts).filter(VolumeDiscounts.id == item_id, VolumeDiscounts.active == False).first()
    if not item:
        raise ValueError("VolumeDiscounts not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item