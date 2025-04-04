from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import UserRole
from app.schemas.user_roles_schemas import UserRoleCreate, UserRoleUpdate
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
    return db.query(UserRole).filter(UserRole.id == item_id).first()


def research(
    db: Session,
    role_id: Optional[str] = None,
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
    valid_sort_columns = [column.key for column in UserRole.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    # query = db.query(UserRole)
    query = db.query(UserRole).options(joinedload(UserRole.owner), 
    joinedload(UserRole.role))

    # Filtres génériques
    if role_id:
        query = query.filter(UserRole.role_id == role_id)
    if owner_id:
        query = query.filter(UserRole.owner_id== owner_id)
    if refnumber:
        query = query.filter(UserRole.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(UserRole.created_by == created_by)
    if updated_by is not None:
        query = query.filter(UserRole.updated_by == updated_by)
    if active is not None:
        query = query.filter(UserRole.active == active)

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
        (UserRole.created_at, created_at, created_at_bis, created_at_operation),
        (UserRole.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(UserRole, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(UserRole.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records




def create(
    db: Session,
    data: UserRoleCreate,
    current_user_id: str = None
):
    # Vérification des doublons
    filters = [
        UserRole.role_id == data.role_id,
        UserRole.owner_id == data.owner_id
    ]

    existing = db.query(UserRole).filter(and_(*filters)).first()
    if existing:
        raise ValueError(
            "L'association existe déjà avec les champs suivants : privilege_id et owner_id."
        )

    # Création de l'utilisateur
    try:
        concatenated_uuid = str(uuid4())
        unique_ref = generate_unique_num_ref(UserRole, db)

        item = UserRole(
            id=concatenated_uuid,
            refnumber=unique_ref,
            created_by=current_user_id,
            **data.dict(),  # Conversion en dictionnaire
            # **data,
        )

        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du privilège : {str(e)}")



def update(db: Session, item_id: str, data: UserRoleUpdate, current_user_id: str):
    item = db.query(UserRole).filter(UserRole.id == item_id).first()
    if not item:
        raise ValueError("L'utilisateur n'a pas été trouvé.")

    # Détection des conflits
    filters = [
        UserRole.role_id == data.role_id,
        UserRole.owner_id == data.owner_id
    ]
    existing = db.query(UserRole).filter(and_(*filters)).first()
    print("ici!")
    if existing and existing.id != item.id:
        print("et là!")
        raise ValueError(
            f"L'association existe déjà avec les champs suivants : owner_id={data.owner_id}, role_id={data.role_id}."
        )

    # Mise à jour des champs
    if data.owner_id is not None:
        item.owner_id = data.owner_id
    if data.role_id is not None:
        item.role_id = data.role_id

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(UserRole).filter(UserRole.id == item_id, UserRole.active == True).first()
    if not item:
        raise ValueError("UserRole not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(UserRole).filter(UserRole.id == item_id, UserRole.active == False).first()
    if not item:
        raise ValueError("UserRole not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item