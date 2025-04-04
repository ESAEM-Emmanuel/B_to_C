from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, Generic, List, TypeVar
from app.models.models import GenderType
from pydantic import BaseModel

# Définir un type générique pour les schémas
T = TypeVar("T")

# =============================== Pagination Metadata Schema ===============================
class PaginationMetadata(BaseModel):
    total_records: int
    total_pages: int
    current_page: int

# =============================== Paginated Response Schema ===============================
class PaginatedResponse(BaseModel, Generic[T]):
    records: List[T]  # Les enregistrements peuvent être de n'importe quel type T
    metadata: PaginationMetadata


class UserInfo(BaseModel):
    id: str
    refnumber: str
    phone: str
    username: Optional[str] = None
    email: EmailStr
    birthday: Optional[date] = None
    gender: Optional[GenderType] = None
    image: Optional[constr(max_length=256)] = None
    active: bool
    class Config:
        from_attributes = True  #
        
# =============================== BASE MIXIN SCHEMA ===============================
class BaseMixinSchema(BaseModel):
    id: str
    refnumber: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    creator: Optional[UserInfo] = None
    updated_by: Optional[str] = None
    updator: Optional[UserInfo] = None
    active: bool = True  # Valeur par défaut

    class Config:
        from_attributes = True

# =============================== TOWN SCHEMA ===============================
class CountrySchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class TownSchema(BaseModel):
    id: str
    name: str
    country_id: str
    country: CountrySchema

    class Config:
        from_attributes = True

# =============================== ARTICLE SCHEMA ===============================
class CategoryArticleSchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class ArticleStateSchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class ArticleSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    reception_place: str
    phone: Optional[str] = None
    price: Optional[float] = None
    main_image: str
    other_images: Optional[List[str]] = []
    end_date: Optional[datetime] = None
    nb_visite: int
    status: Optional[str] = None
    daily_rate: Optional[float] = None
    town_id: str
    town: TownSchema
    category_article_id: str
    category: CategoryArticleSchema
    article_state_id: str
    article_state: ArticleStateSchema

    class Config:
        from_attributes = True

# =============================== SIGNAL SCHEMA ===============================
class SignalSchema(BaseModel):
    id: str
    description: str
    owner_id: str
    offender_id: str
    article_id: str
    owner: Optional[UserInfo] = None
    offender: Optional[UserInfo] = None
    article: ArticleSchema

    class Config:
        from_attributes = True

# =============================== FAVORITE SCHEMA ===============================
class FavoriteSchema(BaseModel):
    id: str
    owner_id: str
    article_id: str
    owner: Optional[UserInfo] = None
    article: ArticleSchema

    class Config:
        from_attributes = True

# =============================== SUBSCRIPTION SCHEMA ===============================
class SubscriptionTypeSchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class SubscriptionSchema(BaseModel):
    id: str
    subscription_type_id: str
    subscription_type: SubscriptionTypeSchema
    owner_id: str
    description: Optional[str] = None
    start_date: datetime
    expiration_date: datetime
    remaining_advertisements: int
    is_read: bool
    status: str
    owner: Optional[UserInfo] = None

    class Config:
        from_attributes = True

# =============================== PRIVILEGE USER SCHEMA ===============================
class PrivilegeSchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class PrivilegeUserSchema(BaseModel):
    id: str
    owner_id: str
    privilege_id: str
    owner: Optional[UserInfo] = None
    privilege: Optional[PrivilegeSchema] = None

    class Config:
        from_attributes = True


# =============================== USER ROLE SCHEMA ===============================
class RoleSchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class UserRoleSchema(BaseModel):
    id: str
    owner_id: str
    role_id: str
    owner: Optional[UserInfo] = None
    role: Optional[RoleSchema] = None

    class Config:
        from_attributes = True

# =============================== PRIVILEGE ROLE SCHEMA ===============================
class PrivilegeRoleSchema(BaseModel):
    id: str
    role_id: str
    privilege_id: str
    privilege: Optional[PrivilegeSchema] = None
    # privilege: PrivilegeSchema
    role: Optional[RoleSchema] = None
    # role: RoleSchema

    class Config:
        from_attributes = True