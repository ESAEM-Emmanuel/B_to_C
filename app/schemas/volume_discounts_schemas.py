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



class VolumeDiscounts(BaseModel):
    threshold: int = Field(
        ...,
        threshold="Le prix minimal est obligatoire.",
    )
    reduction: float = Field(
        ...,
        reduction="Le la tarification jour nalière  est obligatoire.",
    )
    

class VolumeDiscountsCreate(VolumeDiscounts):
   pass


class VolumeDiscountsUpdate(BaseModel):
    threshold: Optional[int] = None
    reduction: Optional[float] = None
    


# =============================== SUBSCRITION SCHEMA ===============================

class VolumeDiscountsSchema(BaseMixinSchema):
    threshold: int
    reduction: float

    class Config:
        from_attributes = True


