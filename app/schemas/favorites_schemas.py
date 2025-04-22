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


class Favorite(BaseModel):
    article_id: str = Field(
        None,
        description="Séléctionnez un privilege existant.",
    )
  


class FavoriteCreate(Favorite):
   pass


class FavoriteUpdate(BaseModel):
    owner_id: Optional[constr(max_length=256)] = None
    article_id: Optional[constr(max_length=256)] = None


# =============================== USER SCHEMA ===============================
class FavoriteSchema(BaseMixinSchema):
    owner_id: str
    article_id: Optional[str] = None

    owner: UserInfo
    article: Optional[ArticleSchema] = None

    class Config:
        from_attributes = True


