from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.models import User
from app.schemas.users_schemas import UserCreate, UserUpdate
from app.utils.utils import (
    hash,
    generate_unique_num_ref,
    verify,get_user_by_id
    )
from uuid import uuid4
from typing import Optional, List
from datetime import date, datetime, time
from sqlalchemy import asc, desc
from fastapi import HTTPException
from pydantic import EmailStr
import bcrypt


def get_by_id(db: Session, item_id: str):
    return db.query(User).filter(User.id == item_id).first()


def research(
    db: Session,
    username: Optional[str] = None,
    refnumber: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    birthday: Optional[date] = None,
    birthday_bis: Optional[date] = None,
    operation_birthday: Optional[str] = None,
    gender: Optional[str] = None,
    town_id: Optional[str] = None,
    is_staff: Optional[bool] = None,
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
    sort_by: str = "username",
    skip: int = 0,
    limit: int = 100,
):
    # Validation des paramètres
    if order not in ["asc", "desc"]:
        raise ValueError("Le paramètre 'order' doit être 'asc' ou 'desc'.")
    if operation_birthday and operation_birthday not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'operation_birthday' doit être 'inf' ou 'sup'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in User.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")


    # Construction de la requête
    query = db.query(User)

    # Filtres génériques
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if refnumber:
        query = query.filter(User.refnumber.ilike(f"%{refnumber}%"))
    if phone:
        query = query.filter(User.phone.ilike(f"%{phone}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if gender:
        query = query.filter(User.gender == gender)
    if town_id:
        query = query.filter(User.town_id == town_id)
    if is_staff is not None:
        query = query.filter(User.is_staff == is_staff)
    if created_by is not None:
        query = query.filter(User.created_by == created_by)
    if updated_by is not None:
        query = query.filter(User.updated_by == updated_by)
    if active is not None:
        query = query.filter(User.active == active)

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
        (User.birthday, birthday, birthday_bis, operation_birthday),
        (User.created_at, created_at, created_at_bis, created_at_operation),
        (User.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(User, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(User.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records




def create(db: Session, data: UserCreate, current_user_id: str = None):
    # Vérification des doublons
    filters = [
        (User.username == data.username),
        (User.phone == data.phone),
        (User.email == data.email)
    ]
    if data.image:
        filters.append(User.image == data.image)

    existing = db.query(User).filter(or_(*filters)).first()
    if existing:
        conflicts = []
        if existing.username == data.username:
            conflicts.append("username")
        if existing.phone == data.phone:
            conflicts.append("phone")
        if data.image and existing.image == data.image:
            conflicts.append("image")
        if existing.email == data.email:
            conflicts.append("email")
        conflict_message = ", ".join(conflicts)
        raise ValueError(f"Un utilisateur existe déjà avec les champs suivants : {conflict_message}.")

    # Création de l'utilisateur
    try:
        concatenated_uuid = str(uuid4())
        hashed_password = hash(data.password)  # Utilisation de bcrypt
        unique_ref = generate_unique_num_ref(User, db)

        if current_user_id is None:
            current_user_id = concatenated_uuid

        if hasattr(data, "dict"):
            data_dict = data.dict(exclude={"password", "confirm_password"})
        else:
            data_dict = {key: value for key, value in data.items() if key not in {"password", "confirm_password"}}

        item = User(
            id=concatenated_uuid,
            refnumber=unique_ref,
            created_by=current_user_id,
            **data_dict,
            password=hashed_password
        )

        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'utilisateur : {str(e)}")



def update(db: Session, item_id: str, data: UserUpdate, current_user_id: str):
    item = db.query(User).filter(User.id == item_id).first()
    if not item:
        raise ValueError("L'utilisateur n'a pas été trouvé.")

    # Détection des conflits
    filters = [
        (User.username == data.username),
        (User.phone == data.phone),
        (User.email == data.email)
    ]
    if data.image:
        filters.append(User.image == data.image)

    existing = db.query(User).filter(or_(*filters)).first()
    if existing and existing.id != item.id:
        conflicts = []
        if existing.username == data.username:
            conflicts.append("nom d'utilisateur")
        if existing.phone == data.phone:
            conflicts.append("numéro de téléphone")
        if data.image and existing.image == data.image:
            conflicts.append("image")
        if existing.email == data.email:
            conflicts.append("email")
        conflict_message = ", ".join(conflicts)
        raise ValueError(f"Un utilisateur existe déjà avec les champs suivants : {conflict_message}.")

    # Mise à jour des champs
    if data.username is not None:
        item.username = data.username
    if data.email is not None:
        item.email = data.email
    if data.phone is not None:
        item.phone = data.phone
    if data.town_id is not None:
        item.town_id = data.town_id
    if data.birthday is not None:
        item.birthday = data.birthday
    if data.gender is not None:
        item.gender = data.gender
    if data.image is not None:
        item.image = data.image
    if data.is_staff is not None:
        item.is_staff = data.is_staff

    # Mise à jour du mot de passe
    if data.new_password is not None:
        if len(data.new_password) < 8:
            raise ValueError("Le nouveau mot de passe doit contenir au moins 8 caractères.")
        if data.new_password == data.password:
            raise ValueError("Le nouveau mot de passe doit être différent de l'ancien.")
        if not verify(data.password, item.password):
            raise ValueError("Le mot de passe actuel est incorrect.")
        item.password = hash(data.new_password)

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(User).filter(User.id == item_id, User.active == True).first()
    if not item:
        raise ValueError("User not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(User).filter(User.id == item_id, User.active == False).first()
    if not item:
        raise ValueError("User not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item