from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Literal
from app.schemas.utils_schemas import (
    ArticleSchema,
    SignalSchema,
    FavoriteSchema,
    SubscriptionSchema,
    PrivilegeUserSchema,
    SubscriptionSchema,
    BaseMixinSchema,
    TownSchema,
    PrivilegeRoleSchema,
    # CountrySchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    PrivilegeSchema,
    SubscriptionTypeSchema,
    PaymentSchema,
    UserInfo
    )
import re



class Subscription(BaseModel):
    subscription_type_id: str = Field(
        None,
        subscription_type_id="Séléctionnez un type de souscription existant.",
    )
    owner_id: Optional[str] = Field(
        None,
        owner_id="Séléctionnez un jtilisateur existant.",
    )
    description: Optional[str] = Field(
        None,
        description="Faites en une description.",
    )
    start_date : date
    # expiration_date : date
    
    


class SubscriptionCreate(Subscription):
   pass


class SubscriptionUpdate(BaseModel):
    subscription_type_id: Optional[constr(max_length=256)] = None
    owner_id: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = Field(
        None,
        description="Faite une description au besoinn .",
    )
    start_date: Optional[date] = None
    is_read: Optional[bool] = None
    


# =============================== USER SCHEMA ===============================
# class  SubscriptionSchema(BaseMixinSchema):
#     subscription_type_id: str
#     owner_id: str
#     description: str
#     start_date: date
#     expiration_date: date
#     remaining_advertisements: int
#     is_read: bool

#     subscription_type: SubscriptionTypeSchema
#     owner: UserInfo
#     articles: List[ArticleSchema] = []  # Liste vide par défaut
#     payments: List[PaymentSchema] = [] 

#     class Config:
#         from_attributes = True

class SubscriptionSchema(BaseMixinSchema):
    subscription_type_id: str
    owner_id: str
    description: Optional[str] = Field(None, description="Description de l'abonnement.")
    start_date: date
    expiration_date: Optional[date] = Field(None, description="Date d'expiration de l'abonnement.")
    remaining_advertisements: Optional[int] = Field(None, description="Nombre d'annonces restantes.")
    is_read: Optional[bool] = Field(None, description="Indique si l'abonnement a été lu.")

    subscription_type: SubscriptionTypeSchema
    owner: UserInfo
    articles: List[ArticleSchema] = []  # Liste vide par défaut
    payments: List[PaymentSchema] = []

    class Config:
        from_attributes = True


