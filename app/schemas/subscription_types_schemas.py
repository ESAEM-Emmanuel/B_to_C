from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Literal
from app.models.models import StatusProposition
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
    # SubscriptionTypeSchema,
    # RoleSchema,
    )
import re



class SubscriptionType(BaseModel):
    name: str
    advertisements: int = Field(..., description="Cet attribut doit être supérieur à 0.") 
    duration: int = Field(..., description="Cet attribut doit être supérieur à 0.") 
    # description: Optional[constr(max_length=65535)] = Field(
    #     None,
    #     description="Faite une description au besoinn .",
    # )
    price: float = Field(..., description="Cet attribut doit être supérieur à 0.") 
    price_max_article: float = Field(..., description="Cet attribut doit être supérieur à 0.") 
    status: StatusProposition = Field("actif", description="Cet attribut prend les valeur actif et inactif.") 
    
    


class SubscriptionTypeCreate(SubscriptionType):
   pass


class SubscriptionTypeUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    advertisements: Optional[int] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    duration: Optional[int] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    # description: Optional[constr(max_length=65535)] = Field(
    #     None,
    #     description="Faite une description au besoinn .",
    # )
    price: Optional[float] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    price_max_article: Optional[float] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    status: Optional[StatusProposition] = Field("actif", description="Cet attribut doit être supérieur à 0.") 
    

# =============================== USER SCHEMA ===============================
class SubscriptionTypeSchema(BaseMixinSchema):
    name: str
    advertisements: Optional[int] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    duration: Optional[int] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    description: Optional[constr(max_length=65535)] = Field(
        None,
        description="Faite une description au besoinn .",
    )
    price: Optional[float] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    price_max_article: Optional[float] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    status: Optional[StatusProposition] = Field(None, description="Cet attribut doit être supérieur à 0.") 
    
    subscriptions: List[StatusProposition] = []  # Liste vide par défaut

    class Config:
        from_attributes = True


