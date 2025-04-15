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



class TaxInterval(BaseModel):
    min_price: float = Field(
        ...,
        min_price="Le prix minimal est obligatoire.",
    )
    max_price: float = Field(
        ...,
        max_price="Le prix max est obligatoire.",
    )
    daily_rate: float = Field(
        ...,
        daily_rate="Le la tarification jour nalière  est obligatoire.",
    )
    

class TaxIntervalCreate(TaxInterval):
   pass


class TaxIntervalUpdate(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    daily_rate: Optional[float] = None
    


# =============================== SUBSCRITION SCHEMA ===============================

class TaxIntervalSchema(BaseMixinSchema):
    min_price: float
    max_price: float
    daily_rate: float

    class Config:
        from_attributes = True


