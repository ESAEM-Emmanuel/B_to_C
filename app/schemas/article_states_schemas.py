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
    # PrivilegeSchema,
    # SubscriptionTypeSchema,
    # ArticleStateSchema,
    # RoleSchema,
    )
import re



class ArticleState(BaseModel):
    name: str
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    


class ArticleStateCreate(ArticleState):
   pass


class ArticleStateUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None
    


# =============================== USER SCHEMA ===============================
class ArticleStateSchema(BaseMixinSchema):
    name: str
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    
    articles: List[ArticleSchema] = []  # Liste vide par défaut

    class Config:
        from_attributes = True


