from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Literal
from app.models.models import GenderType, StatusArticle
from app.schemas.utils_schemas import (
    ArticleSchema,
    SignalSchema,
    FavoriteSchema,
    SubscriptionSchema,
    PrivilegeUserSchema,
    BaseMixinSchema,
    TownSchema,
    CategoryArticleSchema,
    ArticleStateSchema,
    PaymentSchema,
    NotificationSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    PrivilegeSchema,
    RoleSchema,
    UserInfo
    )
import re



class Article(BaseModel):
    name: str = Field(..., description="Le nom de l'article est obligatoire.")
    description: Optional[str] = Field(
        None,
        description="Description facultative de l'article."
    )
    reception_place: str = Field(..., description="Le lieu de réception est obligatoire.")
    phone: str = Field(
        ...,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés)."
    )
    phone_transaction: str = Field(
        ...,
        description="Le numéro de téléphone pour la transaction doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés)."
    )
    price: float = Field(
        ...,
        description="Le prix minimal est obligatoire."
    )
    main_image: str = Field(..., description="L'image principale est obligatoire.")
    other_images: List[str] = Field(
        [],
        description="Liste facultative d'autres images associées à l'article."
    )
    start_date: date = Field(..., description="La date de début est obligatoire.")
    end_date: date = Field(..., description="La date de fin est obligatoire.")
    owner_id: Optional[str] = Field(
        None,
        description="Identifiant facultatif du propriétaire."
    )
    subscription_id: str = Field(
        None,
        description="Identifiant obligatoire de l'abonnement."
    )
    town_id: str = Field(
        ...,
        description="Identifiant obligatoire de la ville."
    )
    category_article_id: str = Field(
        ...,
        description="Identifiant obligatoire de la catégorie de l'article."
    )
    article_state_id: str = Field(
        ...,
        description="Identifiant obligatoire de l'état de l'article."
    )

    @validator("phone", "phone_transaction")
    def validate_phone(cls, value):
        """
        Valide que le numéro de téléphone respecte le format attendu :
        - Entre 9 et 15 chiffres.
        - Autorise les caractères '+' au début et '-' comme séparateur.
        """
        if not re.fullmatch(r"^\+?[0-9]{9,15}(-[0-9]{1,4})?$", value):
            raise ValueError(
                "Le numéro de téléphone doit contenir entre 9 et 15 chiffres avec un format valide (+ ou - autorisé)."
            )
        return value

    @validator("price")
    def validate_price(cls, value):
        """
        Valide que le prix est supérieur ou égal à 1.
        """
        if value < 1:
            raise ValueError("Le prix doit être supérieur ou égal à 1.")
        return value

    @validator("end_date")
    def validate_dates(cls, value, values):
        """
        Valide que la date de début est inférieure d'au moins un jour à la date de fin.
        """
        start_date = values.get("start_date")
        if start_date and value <= start_date + timedelta(days=1):
            raise ValueError("La date de fin doit être supérieure d'au moins un jour à la date de début.")
        return value
    


class ArticleCreate(Article):
   pass


class ArticleUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = Field(
        None, description="Nom facultatif de l'article (max 256 caractères)."
    )
    description: Optional[constr(max_length=65535)] = Field(
        None, description="Description facultative de l'article (max 256 caractères)."
    )
    reception_place: Optional[constr(max_length=256)] = Field(
        None, description="Lieu de réception facultatif (max 256 caractères)."
    )
    phone: Optional[constr(max_length=256)] = Field(
        None,
        description="Numéro de téléphone facultatif (format valide : + ou -, entre 9 et 15 chiffres)."
    )
    phone_transaction: Optional[constr(max_length=256)] = Field(
        None,
        description="Numéro de téléphone pour la transaction facultatif (format valide : + ou -, entre 9 et 15 chiffres)."
    )
    price: Optional[float] = Field(
        None, description="Prix facultatif de l'article."
    )
    main_image: Optional[constr(max_length=256)] = Field(
        None, description="Image principale facultative (max 256 caractères)."
    )
    other_images: Optional[List[constr(max_length=256)]] = Field(
        default_factory=list,
        description="Liste facultative d'autres images associées à l'article."
    )
    start_date: Optional[date] = Field(
        None, description="Date de début facultative (format YYYY-MM-DD)."
    )
    end_date: Optional[date] = Field(
        None, description="Date de fin facultative (format YYYY-MM-DD)."
    )
    nb_visite: Optional[int] = Field(
        None, description="Nombre de visites facultatif."
    )
    status: Optional[StatusArticle] = Field(  # Remplacez `str` par `StatusArticle` si défini
        None, description="Statut facultatif de l'article."
    )
    amount_to_pay: Optional[float] = Field(
        None, description="Taux journalier facultatif."
    )
    owner_id: Optional[constr(max_length=256)] = Field(
        None, description="Identifiant facultatif du propriétaire (max 256 caractères)."
    )
    subscription_id: Optional[constr(max_length=256)] = Field(
        None, description="Identifiant facultatif de l'abonnement (max 256 caractères)."
    )
    town_id: Optional[constr(max_length=256)] = Field(
        None, description="Identifiant facultatif de la ville (max 256 caractères)."
    )
    category_article_id: Optional[constr(max_length=256)] = Field(
        None, description="Identifiant facultatif de la catégorie de l'article (max 256 caractères)."
    )
    article_state_id: Optional[constr(max_length=256)] = Field(
        None, description="Identifiant facultatif de l'état de l'article (max 256 caractères)."
    )

    @validator("phone", "phone_transaction")
    def validate_phone(cls, value):
        """
        Valide que le numéro de téléphone respecte le format attendu :
        - Entre 9 et 15 chiffres.
        - Autorise les caractères '+' au début et '-' comme séparateur.
        """
        if value is not None and not re.fullmatch(r"^\+?[0-9]{9,15}(-[0-9]{1,4})?$", value):
            raise ValueError(
                "Le numéro de téléphone doit contenir entre 9 et 15 chiffres avec un format valide (+ ou - autorisé)."
            )
        return value

    @validator("price")
    def validate_price(cls, value):
        """
        Valide que le prix est supérieur ou égal à 1.
        """
        if value is not None and value < 1:
            raise ValueError("Le prix doit être supérieur ou égal à 1.")
        return value

    @validator("end_date")
    def validate_dates(cls, value, values):
        """
        Valide que la date de début est inférieure d'au moins un jour à la date de fin.
        Cette validation n'est effectuée que si les deux dates sont fournies.
        """
        start_date = values.get("start_date")
        if start_date is not None and value is not None:
            if value <= start_date + timedelta(days=1):
                raise ValueError("La date de fin doit être supérieure d'au moins un jour à la date de début.")
        return value
    


# =============================== USER SCHEMA ===============================
class  ArticleSchema(BaseMixinSchema):
    name: str
    description: Optional[str] = None
    reception_place: Optional[str] = None
    phone: Optional[str] = None
    phone_transaction: Optional[str] = None
    price: Optional[float] = None
    main_image: Optional[str] = None
    other_images: Optional[List[constr(max_length=256)]] = []
    start_date: Optional[date]
    end_date: Optional[date]
    nb_visite: Optional[int] = None
    status: StatusArticle
    amount_to_pay: Optional[float] = None
    owner_id: Optional[str] = None
    owner: Optional[UserInfo] = None
    subscription_id: Optional[str] = None
    subscription: Optional[SubscriptionSchema] = None
    town_id: str
    town: TownSchema = None
    category_article_id: str
    category: CategoryArticleSchema = None
    article_state_id: str
    article_state: ArticleStateSchema = None

    signals: List[SignalSchema] = []  # Liste vide par défaut
    favorites: List[FavoriteSchema] = []  # Liste vide par défaut
    notifications: List[NotificationSchema] = []  # Liste vide par défaut
    payments: List[PaymentSchema] = []  # Liste vide par défaut

