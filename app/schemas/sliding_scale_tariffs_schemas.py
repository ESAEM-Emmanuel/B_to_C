from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Literal
from app.schemas.utils_schemas import (
    ArticleSchema,
    SignalSchema,
    FavoriteSchema,
    PrivilegeUserSchema,
    BaseMixinSchema,
    TownSchema,
    PrivilegeRoleSchema,
    # CountrySchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    PrivilegeSchema,
    PaymentSchema,
    UserInfo
    )
import re



class SlidingScaleTariffs(BaseModel):
    days_min: int = Field(
        ...,
        days_min="Le prix minimal est obligatoire.",
    )
    max_days: int = Field(
        ...,
        max_days="Le prix max est obligatoire.",
    )
    rate: float = Field(
        ...,
        rate="Le la tarification jour nalière  est obligatoire.",
    )
    

class SlidingScaleTariffsCreate(SlidingScaleTariffs):
   pass


class SlidingScaleTariffsUpdate(BaseModel):
    days_min: Optional[int] = None
    max_days: Optional[int] = None
    rate: Optional[float] = None
    


# =============================== SUBSCRITION SCHEMA ===============================

class SlidingScaleTariffsSchema(BaseMixinSchema):
    days_min: int
    max_days: int
    rate: float

    class Config:
        from_attributes = True


