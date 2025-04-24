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



class Payment(BaseModel):
    payment_number: str = Field(
        ...,
        description="Rentrez votre numéro de paiment.",
    )
    article_id: str = Field(
        None,
        description="Séléctionnez un article existant.",
    )
    subscription_id: str = Field(
        None,
        description="Séléctionnez un abonnement existant.",
    )
    @validator("payment_number")
    def validate_phone(cls, value):
        # Vérifier si le numéro respecte le format attendu
        if not re.fullmatch(r"^\+?[0-9]{9,15}(-[0-9]{1,4})?$", value):
            raise ValueError(
                "Le numéro de payment valide)."
            )
        return value


    


class PaymentCreate(Payment):
   pass


class PaymentUpdate(BaseModel):
    payment_number: Optional[constr(max_length=256)] = None
    article_id: Optional[constr(max_length=256)] = None
    subscription_id: Optional[constr(max_length=256)] = None
    is_read: Optional[bool] = False
    @validator("payment_number")
    def validate_phone(cls, value):
        if value and not re.fullmatch(r"^\+?[0-9]{9,15}(-[0-9]{1,4})?$", value):
            raise ValueError(
                "Le numéro de payment doit être valide."
            )
        return value
    


# =============================== USER SCHEMA ===============================
class PaymentSchema(BaseMixinSchema):
    payment_number: Optional[str] = None
    article_id: Optional[str] = None
    subscription_id: Optional[str] = None
    is_read: Optional[bool] = False

    article: Optional[ArticleSchema] = None
    subscription: Optional[SubscriptionSchema] = None

    class Config:
        from_attributes = True


