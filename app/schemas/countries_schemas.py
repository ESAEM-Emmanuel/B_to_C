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
    # PrivilegeSchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    CountrySchema,
    # RoleSchema,
    )
import re



class Country(BaseModel):
    name: str

    


class CountryCreate(Country):
   pass


class CountryUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    


# =============================== USER SCHEMA ===============================
class CountrySchema(BaseMixinSchema):
    name: str

    towns: List[TownSchema] = []  # Liste vide par défaut

    class Config:
        from_attributes = True


