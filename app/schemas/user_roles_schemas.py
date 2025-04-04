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



class UserRole(BaseModel):
    role_id: str = Field(
        None,
        role_id="Séléctionnez un rôle existant.",
    )
    owner_id: str = Field(
        None,
        owner_id="Séléctionnez un privilege existant.",
    )
    


class UserRoleCreate(UserRole):
   pass


class UserRoleUpdate(BaseModel):
    role_id: Optional[constr(max_length=256)] = None
    owner_id: Optional[constr(max_length=256)] = None
    


# =============================== USER SCHEMA ===============================
class  UserRoleSchema(BaseMixinSchema):
    role_id: str
    owner_id: str

    role: RoleSchema
    owner: UserInfo

    class Config:
        from_attributes = True


