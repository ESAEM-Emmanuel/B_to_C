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
    PrivilegeRoleSchema,
    # CountrySchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    PrivilegeSchema,
    RoleSchema,
    UserInfo
    )
import re



class Notification(BaseModel):
    article_id: str = Field(
        None,
        description="Séléctionnez un privilege existant.",
    )
    subscription_id: str = Field(
        None,
        description="Séléctionnez un privilege existant.",
    )

    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    


class NotificationCreate(Notification):
   pass


class NotificationUpdate(BaseModel):
    article_id: Optional[constr(max_length=256)] = None
    subscription_id: Optional[constr(max_length=256)] = None
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    is_read: Optional[bool] = False
    


# =============================== USER SCHEMA ===============================
class NotificationSchema(BaseMixinSchema):
    article_id: Optional[str] = None
    subscription_id: Optional[str] = None
    description: Optional[str] = None
    is_read: Optional[bool] = False

    article: Optional[ArticleSchema] = None
    article: Optional[ArticleSchema] = None

    class Config:
        from_attributes = True


