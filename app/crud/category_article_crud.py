from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.models import CategoryArticle
from app.schemas.category_articles_schemas import CategoryArticleCreate, CategoryArticleUpdate
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
    return db.query(CategoryArticle).filter(CategoryArticle.id == item_id).first()


def research(
    db: Session,
    name: Optional[str] = None,
    description: Optional[str] = None,
    image: Optional[str] = None,
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

    
    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in CategoryArticle.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")

    # Construction de la requête
    query = db.query(CategoryArticle)

    # Filtres génériques
    if name:
        query = query.filter(CategoryArticle.name.ilike(f"%{name.lower()}%"))
    if description:
        query = query.filter(CategoryArticle.description.ilike(f"%{description.lower()}%"))
    if image:
        query = query.filter(CategoryArticle.image.ilike(f"%{image}%"))
    if refnumber:
        query = query.filter(CategoryArticle.refnumber.ilike(f"%{refnumber}%"))
    if created_by is not None:
        query = query.filter(CategoryArticle.created_by == created_by)
    if updated_by is not None:
        query = query.filter(CategoryArticle.updated_by == updated_by)
    if active is not None:
        query = query.filter(CategoryArticle.active == active)

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
        (CategoryArticle.created_at, created_at, created_at_bis, created_at_operation),
        (CategoryArticle.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(CategoryArticle, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(CategoryArticle.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records


def create(db: Session, data: CategoryArticleCreate, current_user_id: str = None):
    # Normalisation des champs (déplacée dans Pydantic si possible)
    data.name = data.name.strip().lower()
    if data.description is not None:
        data.description = data.description.strip().lower()
    if data.image is not None:
        data.image = data.image.strip()

    # Vérification des doublons
    existing = db.query(CategoryArticle).filter(CategoryArticle.name == data.name).first()
    if existing:
        raise ValueError(f"Un privilège avec le nom '{data.name}' existe déjà.")

    # Création de l'enregistrement
    try:
        concatenated_uuid = str(uuid4())
        unique_ref = generate_unique_num_ref(CategoryArticle, db)

        item = CategoryArticle(
            id=concatenated_uuid,
            refnumber=unique_ref,
            created_by=current_user_id,
            name=data.name,
            description=data.description,
            image=data.image,
        )

        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    except SQLAlchemyError as e:
        db.rollback()
        # Journalisation de l'erreur
        logger.error(f"Erreur lors de la création du privilège : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la création du privilège.")



def update(db: Session, item_id: str, data: CategoryArticleUpdate, current_user_id: str):
    item = db.query(CategoryArticle).filter(CategoryArticle.id == item_id).first()
    if not item:
        raise ValueError("L'utilisateur n'a pas été trouvé.")

    # Détection des conflits
    filters = [
        (CategoryArticle.name == data.name.lower()),
    ]
    existing = db.query(CategoryArticle).filter(or_(*filters)).first()
    if existing and existing.id != item.id:
        conflicts = []
        if existing.name == data.name:
            conflicts.append("nom")
        conflict_message = ", ".join(conflicts)
        raise ValueError(f"Un privilège existe déjà avec les champs suivants : {conflict_message}.")

    # Mise à jour des champs
    if data.name is not None:
        item.name = data.name.lower()
    if data.description is not None:
        item.description = data.description.lower()
    if data.image is not None:
        item.image = data.image

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(CategoryArticle).filter(CategoryArticle.id == item_id, CategoryArticle.active == True).first()
    if not item:
        raise ValueError("CategoryArticle not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(CategoryArticle).filter(CategoryArticle.id == item_id, CategoryArticle.active == False).first()
    if not item:
        raise ValueError("CategoryArticle not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item