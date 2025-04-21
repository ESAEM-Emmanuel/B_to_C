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



class Signal(BaseModel):
    # owner_id: str = Field(
    #     ...,
    #     description="Séléctionnez un rôle existant.",
    # )
    article_id: str = Field(
        None,
        description="Séléctionnez un privilege existant.",
    )
    offender_id: str = Field(
        None,
        description="Séléctionnez un privilege existant.",
    )
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    


class SignalCreate(Signal):
   pass


class SignalUpdate(BaseModel):
    owner_id: Optional[constr(max_length=256)] = None
    article_id: Optional[constr(max_length=256)] = None
    offender_id: Optional[constr(max_length=256)] = None
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    


# =============================== USER SCHEMA ===============================
# class  SignalSchema(BaseMixinSchema):
#     owner_id: str
#     article_id: Optional[str] = None
#     offender_id: Optional[str] = None
#     description: Optional[str] = None

#     owner: UserInfo
#     article: ArticleSchema = None
#     offender: UserInfo = None

#     class Config:
#         from_attributes = True
class SignalSchema(BaseMixinSchema):
    owner_id: str
    article_id: Optional[str] = None
    offender_id: Optional[str] = None
    description: Optional[str] = None

    owner: UserInfo
    article: Optional[ArticleSchema] = None
    offender: Optional[UserInfo] = None

    class Config:
        from_attributes = True


