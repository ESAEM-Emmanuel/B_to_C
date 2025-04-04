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



class PrivilegeUser(BaseModel):
    owner_id: str = Field(
        None,
        owner_id="Séléctionnez un rôle existant.",
    )
    privilege_id: str = Field(
        None,
        privilege_id="Séléctionnez un privilege existant.",
    )
    


class PrivilegeUserCreate(PrivilegeUser):
   pass


class PrivilegeUserUpdate(BaseModel):
    owner_id: Optional[constr(max_length=256)] = None
    privilege_id: Optional[constr(max_length=256)] = None
    


# =============================== USER SCHEMA ===============================
class  PrivilegeUserSchema(BaseMixinSchema):
    owner_id: str
    privilege_id: str


    privilege: PrivilegeSchema
    owner: UserInfo

    class Config:
        from_attributes = True


