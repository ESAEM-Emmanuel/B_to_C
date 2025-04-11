from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Literal
from app.models.models import GenderType
from app.schemas.utils_schemas import (
    ArticleSchema,
    SignalSchema,
    FavoriteSchema,
    SubscriptionSchema,
    PrivilegeUserSchema,
    UserRoleSchema,
    BaseMixinSchema,
    TownSchema,
    # CountrySchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    # PrivilegeSchema,
    # RoleSchema,
    )
import re


class UserLogin(BaseModel):
   username: str
   password: str
   
class UserOutSchema(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str 


class TokenData(BaseModel):
    id: Optional[str] = None

class User(BaseModel):
    username: str = Field(..., description="Le nom d'utilisateur est obligatoire.")
    phone: str = Field(
        ...,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    email: EmailStr = Field(..., description="L'adresse e-mail est obligatoire.")
    birthday: Optional[date] = None
    gender: Optional[GenderType] = None
    image: Optional[str] = None

    @validator("phone")
    def validate_phone(cls, value):
        # Vérifier si le numéro respecte le format attendu
        if not re.fullmatch(r"^\+?[0-9]{9,15}(-[0-9]{1,4})?$", value):
            raise ValueError(
                "Le numéro de téléphone doit contenir entre 9 et 15 chiffres avec un format valide (+ ou - autorisé)."
            )
        return value


class UserCreate(User):
    town_id: str
    is_staff: bool = False  
    password: str
    confirm_password: str

    @validator("password")
    def validate_password(cls, value):
        # Vérifier si le mot de passe contient au moins 4 caractères et ne contient pas de points, espaces, ou points-virgules
        if not re.fullmatch(r"^(?!.*[.;\s])[A-Za-z0-9!@#$%^&*()_+={}\[\]:;'\"<>,.?/-]{4,}$", value):
            raise ValueError(
                "Le mot de passe doit contenir au moins 4 caractères, incluant des chiffres, des lettres ou des caractères spéciaux, mais sans espaces, points ou points-virgules."
            )
        return value

    @validator("confirm_password")
    def passwords_match(cls, value, values):
        # Vérifier que `confirm_password` est égal à `password`
        if "password" in values and value != values["password"]:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return value

PASSWORD_REGEX = r"^(?!.*[.;\s])[A-Za-z0-9!@#$%^&*()_+={}\[\]:;'\"<>,.?/-]{4,}$"

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="Le nom d'utilisateur.")
    email: Optional[str] = Field(None, description="Email de l'utilisateur.")
    phone: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    town_id: Optional[str] = Field(None, description="L'ID de la ville associée à l'utilisateur.")
    birthday: Optional[date] = Field(None, description="La date de naissance de l'utilisateur.")
    gender: Optional[GenderType] = Field(None, description="Le genre de l'utilisateur (par exemple, 'M', 'F').")
    image: Optional[str] = Field(None, description="L'URL de l'image de profil de l'utilisateur.")
    password: Optional[str] = Field(None, description="Le mot de passe actuel de l'utilisateur.")
    new_password: Optional[str] = Field(None, description="Le nouveau mot de passe proposé.")
    confirm_new_password: Optional[str] = Field(None, description="Confirmation du nouveau mot de passe.")
    is_staff: Optional[bool] = Field(False, description="Indique si l'utilisateur est un membre du personnel.")

    @validator("phone")
    def validate_phone(cls, value):
        if value and not re.fullmatch(r"^\+?[0-9]{9,15}(-[0-9]{1,4})?$", value):
            raise ValueError(
                "Le numéro de téléphone doit contenir entre 9 et 15 chiffres avec un format valide (+ ou - autorisé)."
            )
        return value

    @root_validator(pre=True)
    def validate_passwords(cls, values):
        password = values.get("password")
        new_password = values.get("new_password")
        confirm_new_password = values.get("confirm_new_password")

        if new_password:
            if not password:
                raise ValueError("Le mot de passe actuel est requis pour définir un nouveau mot de passe.")
            if not re.fullmatch(PASSWORD_REGEX, new_password):
                raise ValueError(
                    "Le mot de passe doit contenir au moins 4 caractères, incluant des chiffres, des lettres ou des caractères spéciaux, mais sans espaces, points ou points-virgules."
                )
            if confirm_new_password != new_password:
                raise ValueError("Le nouveau mot de passe et sa confirmation doivent être identiques.")

        return values


# =============================== USER SCHEMA ===============================
class UserSchema(BaseMixinSchema):
    username: str
    phone: Optional[str] = None
    email: EmailStr
    birthday: Optional[date] = None
    gender: Optional[GenderType] = None
    image: Optional[str] = None
    is_staff: bool = False  # Valeur par défaut
    town_id: str
    town: TownSchema = None
    owned_articles: List[ArticleSchema] = []  # Liste vide par défaut
    reported_signals: List[SignalSchema] = []  # Liste vide par défaut
    offender_signals: List[SignalSchema] = []  # Liste vide par défaut
    favorites: List[FavoriteSchema] = []  # Liste vide par défaut
    subscriptions: List[SubscriptionSchema] = []  # Liste vide par défaut
    privilege_users: List[PrivilegeUserSchema] = []  # Liste vide par défaut
    user_roles: List[UserRoleSchema] = []  # Liste vide par défaut

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserSchema  # Assurez-vous que UserSchema est déjà défini
    privileges: List[str] 
