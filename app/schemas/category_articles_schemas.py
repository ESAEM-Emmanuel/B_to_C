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
    # PrivilegeSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    # CategoryArticleSchema,
    # RoleSchema,
    )
import re



class CategoryArticle(BaseModel):
    name: str
    description: Optional[str] = Field(
        None,
        description="Faite une description au besoinn .",
    )
    image: Optional[str] = Field(
        None,
        description="Chargez une image au besoinn.",
    )
    


class CategoryArticleCreate(CategoryArticle):
   pass


class CategoryArticleUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None
    image: Optional[constr(max_length=256)] = None
    

# =============================== USER SCHEMA ===============================
class CategoryArticleSchema(BaseMixinSchema):
    name: str
    description: Optional[str] = Field(
        None,
        description="Description.",
    )
    image: Optional[constr(max_length=256)] = None
    
    articles: List[ArticleSchema] = []  # Liste vide par défaut

    class Config:
        from_attributes = True


