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
    )
import re



class PrivilegeRole(BaseModel):
    role_id: str = Field(
        None,
        role_id="Séléctionnez un rôle existant.",
    )
    privilege_id: str = Field(
        None,
        privilege_id="Séléctionnez un privilege existant.",
    )
    


class PrivilegeRoleCreate(PrivilegeRole):
   pass


class PrivilegeRoleUpdate(BaseModel):
    role_id: Optional[constr(max_length=256)] = None
    privilege_id: Optional[constr(max_length=256)] = None
    


# =============================== USER SCHEMA ===============================
class PrivilegeRoleSchema(BaseMixinSchema):
    role_id: str
    privilege_id: str

    role: RoleSchema
    privilege: PrivilegeSchema

    class Config:
        from_attributes = True


