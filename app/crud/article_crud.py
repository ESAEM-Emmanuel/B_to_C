from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.models.models import Article, StatusArticle, Subscription, TaxInterval, SlidingScaleTariffs, VolumeDiscounts, User
from app.schemas.articles_schemas import ArticleCreate, ArticleUpdate
from app.utils.utils import (
    hash,
    generate_unique_num_ref,
    verify,get_user_by_id
    )
from uuid import uuid4
from typing import Optional, List
from datetime import date, datetime, time
from sqlalchemy import asc, desc, func
from fastapi import HTTPException
from pydantic import EmailStr
import bcrypt
from app.crud.notification_crud import create as create_notification
from app.schemas.notifications_schemas import NotificationCreate
from app.crud.payment_crud import create as create_payment
from app.schemas.payments_schemas import PaymentCreate

def count_articles_published_by_owner(db, owner_id):
    # Étape 1 : Récupérer les IDs des souscriptions de l'article
    subscription_ids = (
        db.query(Subscription.id)
        .filter(Subscription.owner_id == owner_id)
        .all()
    )
    subscription_ids = [sub.id for sub in subscription_ids]  # Convertir en liste

    # Étape 2 : Filtrer les articles et compter
    nb_articles_published = (
        db.query(Article)
        .filter(
            or_(
                Article.owner_id == owner_id,
                Article.subscription_id.in_(subscription_ids)
            )
        )
        .count()
    )

    return nb_articles_published

def get_daily_rate_for_price(db, price):
    """
    Récupère le amount_to_pay correspondant à un prix donné dans la table TaxInterval.
    
    :param db: Session SQLAlchemy
    :param price: Prix pour lequel on cherche le amount_to_pay
    :return: amount_to_pay (float) ou None si aucun intervalle ne correspond
    """
    # Requête pour trouver l'intervalle correspondant
    tax_interval = (
        db.query(TaxInterval)
        .filter(TaxInterval.min_price <= price, TaxInterval.max_price >= price)
        .order_by(TaxInterval.id.desc())  # Trier par ID décroissant pour récupérer le dernier
        .first()  # Récupérer le premier résultat
    )
    
    # Retourner le amount_to_pay ou None si aucun résultat
    if tax_interval:
        return tax_interval.daily_rate
    else:
        raise ValueError("l'interval de taxation n'existe pas.")

def calculate_discount_for_volume(db, volume):
    """
    Calcule la réduction correspondant à un volume donné dans la table VolumeDiscounts.
    
    :param db: Session SQLAlchemy
    :param volume: Volume pour lequel on cherche la réduction
    :return: reduction (float) ou 0 si aucun seuil ne correspond
    """
    # Requête pour trouver le seuil correspondant
    volume_discount = (
        db.query(VolumeDiscounts)
        .filter(VolumeDiscounts.threshold <= volume)
        .order_by(VolumeDiscounts.threshold.desc())  # Trier par threshold décroissant
        .first()  # Récupérer le premier résultat
    )
    
    # Retourner la réduction ou 0 si aucun résultat
    if volume_discount:
        return volume_discount.reduction
    else:
        return None

def get_rate_for_duration(db, duration):
    """
    Récupère le rate correspondant à une durée donnée dans la table SlidingScaleTariffs.
    
    :param db: Session SQLAlchemy
    :param duration: Durée en jours pour laquelle on cherche le rate
    :return: rate (float) ou None si aucun intervalle ne correspond
    """
    # Requête pour trouver l'intervalle correspondant
    sliding_scale_tariff = (
        db.query(SlidingScaleTariffs)
        .filter(
            SlidingScaleTariffs.days_min <= duration,
            SlidingScaleTariffs.max_days >= duration
        )
        .order_by(SlidingScaleTariffs.id.desc())  # Trier par ID décroissant pour récupérer le dernier
        .first()  # Récupérer le premier résultat
    )
    
    # Retourner le rate ou None si aucun résultat
    if sliding_scale_tariff:
        return sliding_scale_tariff.rate
    else:
        return None

def get_by_id(db: Session, item_id: str):
    item = db.query(Article).filter(Article.id == item_id).first()
    if not item:
        raise ValueError("Article not found or already deleted.")
    item.nb_visite = item.nb_visite+1
    db.commit()
    db.refresh(item)
    return item
    # return db.query(Article).filter(Article.id == item_id).first()


def research(
    db: Session,
    name: Optional[str] = None,
    description: Optional[str] = None,
    reception_place: Optional[str] = None,
    phone: Optional[str] = None,
    phone_transaction: Optional[str] = None,
    price: Optional[float] = None,
    price_bis: Optional[float] = None,
    price_operation: Optional[str] = None,
    start_date: Optional[date] = None,
    start_date_bis: Optional[date] = None,
    start_date_operation: Optional[str] = None,
    end_date: Optional[float] = None,
    end_date_bis: Optional[float] = None,
    end_date_operation: Optional[str] = None,
    nb_visite: Optional[float] = None,
    nb_visite_bis: Optional[float] = None,
    nb_visite_operation: Optional[str] = None,
    amount_to_pay: Optional[float] = None,
    amount_to_pay_bis: Optional[float] = None,
    amount_to_pay_operation: Optional[str] = None,
    status: Optional[StatusArticle] = None,
    owner_id: Optional[str] = None,
    subscription_id: Optional[str] = None,
    town_id: Optional[str] = None,
    category_article_id: Optional[str] = None,
    article_state_id: Optional[str] = None,
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
    if price_operation and price_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'price_operation' doit être 'inf' ou 'sup'.")
    if start_date_operation and start_date_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'start_date_operation' doit être 'inf' ou 'sup'.")
    if end_date_operation and end_date_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'end_date_operation' doit être 'inf' ou 'sup'.")
    if nb_visite_operation and nb_visite_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'nb_visite_operation' doit être 'inf' ou 'sup'.")
    if amount_to_pay_operation and amount_to_pay_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'amount_to_pay_operation' doit être 'inf' ou 'sup'.")
    if created_at_operation and created_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'created_at_operation' doit être 'inf' ou 'sup'.")
    if updated_at_operation and updated_at_operation not in ["inf", "sup"]:
        raise ValueError("Le paramètre 'updated_at_operation' doit être 'inf' ou 'sup'.")

    # Liste des colonnes valides pour le tri
    valid_sort_columns = [column.key for column in Article.__table__.columns]
    if sort_by not in valid_sort_columns:
        raise ValueError(f"Invalid sort_by value: {sort_by}. Valid options are: {valid_sort_columns}")


    # Construction de la requête
    query = db.query(Article)
    # Construction de la requête avec chargement des relations
    # query = db.query(Article).options(
    #     # joinedload(Article.owner),  # Charger la relation `owner`
    #     # joinedload(Article.subscription),  # Charger la relation `subscription`
    #     # joinedload(Article.town),  # Charger la relation `town`
    #     joinedload(Article.category),  # Charger la relation `category`
    #     joinedload(Article.article_state),  # Charger la relation `article_state`
    #     joinedload(Article.signals),  # Charger la relation `signals`
    #     joinedload(Article.favorites),  # Charger la relation `favorites`
    #     joinedload(Article.notifications),  # Charger la relation `notifications`
    #     joinedload(Article.payments),  # Charger la relation `payments`
    # )

    # Filtres génériques
    if name:
        query = query.filter(Article.name.ilike(f"%{name}%"))
    if refnumber:
        query = query.filter(Article.refnumber.ilike(f"%{refnumber}%"))
    if description:
        query = query.filter(Article.description.ilike(f"%{description}%"))
    if reception_place:
        query = query.filter(Article.reception_place.ilike(f"%{reception_place}%"))
    if phone:
        query = query.filter(Article.phone.ilike(f"%{phone}%"))
    if phone_transaction:
        query = query.filter(Article.phone_transaction.ilike(f"%{phone_transaction}%"))
    if town_id:
        query = query.filter(Article.town_id == town_id)
    if owner_id is not None:
        query = query.filter(Article.owner_id == owner_id)
    if subscription_id is not None:
        query = query.filter(Article.subscription_id == subscription_id)
    if category_article_id is not None:
        query = query.filter(Article.category_article_id == category_article_id)
    if article_state_id is not None:
        query = query.filter(Article.article_state_id == article_state_id)
    if created_by is not None:
        query = query.filter(Article.created_by == created_by)
    if updated_by is not None:
        query = query.filter(Article.updated_by == updated_by)
    if active is not None:
        query = query.filter(Article.active == active)

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
        (Article.price, price, price_bis, price_operation),
        (Article.nb_visite, nb_visite, nb_visite_bis, nb_visite_operation),
        (Article.amount_to_pay, amount_to_pay, amount_to_pay_bis, amount_to_pay_operation),
        (Article.start_date, start_date, start_date_bis, start_date_operation),
        (Article.end_date, end_date, end_date_bis, end_date_operation),
        (Article.created_at, created_at, created_at_bis, created_at_operation),
        (Article.updated_at, updated_at, updated_at_bis, updated_at_operation),
    ]:
        filter_condition = apply_date_filter(field, value, bis_value, operation)
        if filter_condition is not None:
            filters.append(filter_condition)

    if filters:
        query = query.filter(*filters)

    # Tri
    order_func = asc if order == "asc" else desc
    query = query.order_by(order_func(getattr(Article, sort_by)))

    # Pagination
    total_records = query.count()

    if limit == -1:
        # Si limit = -1, on filtre uniquement les utilisateurs actifs
        items = query.filter(Article.active == True).all()
        total_records = len(items)  # Recalcul du nombre total d'enregistrements
    else:
        items = query.offset(skip).limit(limit).all() if limit > 0 else query.all()  
    return items, total_records


def create(db: Session, data: ArticleCreate, current_user_id: str = None):
    try:
        if data.owner_id is None and data.subscription_id is None:
            data.owner_id = current_user_id
        item = db.query(User).filter(User.id == data.owner_id).first()
        if not item:
            raise ValueError("l'Utilisateur n'a pas été trouvé.")
            
        nb_article_owner = count_articles_published_by_owner(db, data.owner_id)
        duration = (data.end_date - data.start_date).days
        daily_rate = get_daily_rate_for_price(db, data.price)
        duration_rate_reduction = get_rate_for_duration(db, duration)
        volume_reduction = calculate_discount_for_volume(db, nb_article_owner)
        amount_to_pay = duration*daily_rate
        if duration_rate_reduction is not None and volume_reduction is None:
            amount_to_pay = amount_to_pay * (1-duration_rate_reduction)
        elif volume_reduction is not None and duration_rate_reduction is None:
            amount_to_pay = amount_to_pay * (1-volume_reduction)
        elif volume_reduction is not None and duration_rate_reduction is not None:
            amount_to_pay = amount_to_pay * (1-volume_reduction-duration_rate_reduction)
        data.name = data.name.lower()
        data.reception_place = data.reception_place.lower()
        if data.description is not None:
            data.description = data.description.lower()
        concatenated_uuid = str(uuid4())
        unique_ref = generate_unique_num_ref(Article, db)

        item = Article(
            id=concatenated_uuid,
            refnumber=unique_ref,
            name=data.name,
            description=data.description,
            reception_place=data.reception_place,
            phone=data.phone,
            phone_transaction=data.phone_transaction,
            price=data.price,
            main_image=data.main_image,
            other_images=data.other_images,
            start_date=data.start_date,
            end_date=data.end_date,
            # status=StatusArticle.PENDING.value,
            owner_id=data.owner_id,
            subscription_id=data.subscription_id,
            town_id=data.town_id,
            category_article_id=data.category_article_id,
            article_state_id=data.article_state_id,
            amount_to_pay=amount_to_pay,
            created_by=current_user_id
        )
        # Ajout de l'article à la session
        db.add(item)

        # Préparation des données pour la notification
        
        data_notification = NotificationCreate(
            article_id=item.id,
            description="création"
        )

        # Création de la notification
        notification = create_notification(db, data_notification, current_user_id)

        # Validation de la transaction
        db.commit()

        # Rafraîchissement des objets pour récupérer les données finales
        db.refresh(item)
        return item
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'article : {str(e)}")


def update(db: Session, item_id: str, data: ArticleUpdate, current_user_id: str):
    item = db.query(Article).filter(Article.id == item_id).first()
    if not item:
        raise ValueError("L'articlen'a pas été trouvé.")

    # Mise à jour des champs
    if data.name is not None:
        item.name = data.name.lower()
    if data.description is not None:
        item.description = data.description.lower()
    if data.reception_place is not None:
        item.reception_place = data.reception_place.lower()
    if data.phone is not None:
        item.phone = data.phone
    if data.phone_transaction is not None:
        item.phone_transaction = data.phone_transaction
    if data.main_image is not None:
        item.main_image = data.main_image
    if data.other_images is not None:
        item.other_images = data.other_images
    if data.nb_visite is not None:
        item.nb_visite = data.nb_visite
    if data.status is not None:
        item.status = data.status
        # if item.status == StatusArticle.PENDING.value and data.status == StatusArticle.PUBLISHED.value:
        #     # Préparation des données pour le payment
        #     data_notification = PaymentCreate(
        #         article_id=item.id,
        #         payment_number=item.phone_transaction
        #     )

        #     # Création de la notification
        #     payment = create_payment(db, data_notification, current_user_id)
        #     item.status = data.status
        # else:
        #     item.status = data.status
    if data.owner_id is not None:
        item.owner_id = data.owner_id
    if data.town_id is not None:
        item.town_id = data.town_id
    if data.category_article_id is not None:
        item.category_article_id = data.category_article_id
    if data.article_state_id is not None:
        item.article_state_id = data.article_state_id

    if data.subscription_id is not None:
        item.subscription_id = data.subscription_id
    if data.amount_to_pay is not None:
        item.amount_to_pay = data.amount_to_pay
    if data.price is not None:
        item.price = data.price
    if data.start_date is not None:
        item.start_date = data.start_date
    if data.end_date is not None:
        item.end_date = data.end_date

    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item
    

def delete(db: Session, item_id: str, current_user_id: str):
    item = db.query(Article).filter(Article.id == item_id, Article.active == True).first()
    if not item:
        raise ValueError("Article not found or already deleted.")
    item.active = False
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def restore(db: Session, item_id: str, current_user_id: str):
    item = db.query(Article).filter(Article.id == item_id, Article.active == False).first()
    if not item:
        raise ValueError("Article not found or already active.")
    item.active = True
    item.updated_by = current_user_id
    db.commit()
    db.refresh(item)
    return item

def random(db: Session, limit: int = 10, skip: int = 0, active: Optional[bool] = True):
    try:
        # Construction de la requête
        query = db.query(Article)

        # Filtre optionnel pour les articles actifs
        if active is not None:
            query = query.filter(Article.active == active)

        # Tri aléatoire
        query = query.order_by(func.random())  # Pour PostgreSQL/SQLite
        # query = query.order_by(func.rand())  # Pour MySQL
        total_records = query.count()

        if limit == -1:
            # Si limit = -1, on filtre uniquement les utilisateurs actifs
            items = query.all()
            total_records = len(items)  # Recalcul du nombre total d'enregistrements
        else:
            items = query.offset(skip).limit(limit).all() 
            
        return items, total_records

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des articles aléatoires : {str(e)}")
