# from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
# from datetime import datetime, date
# from enum import Enum
# from typing import Optional, List
# from app.schemas.quarters_schemas import QuarterListing
# from app.schemas.utils_schemas import UserInfo

# class Town(BaseModel):
#     name: str
#     Town_id: str
    
    
    

# class TownCreate(Town):
#    pass


# class TownListing(Town):
#     id: str
#     refnumber: str
#     created_by: Optional[constr(max_length=256)] = None
#     updated_by: Optional[constr(max_length=256)] = None
#     creator: Optional[UserInfo] = None
#     updator: Optional[UserInfo] = None
#     active: bool
    
    
#     class Config:
#         from_attributes = True 

# class TownDetail(TownListing):
    
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#     quaters : List[QuarterListing]
    
#     class Config:
#         from_attributes = True 
#         # orm_mode = True 
        

# class TownUpdate(BaseModel):
#     name: Optional[constr(max_length=256)] = None
#     Town_id: Optional[constr(max_length=256)] = None


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
    UserInfo,
    # PrivilegeSchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    CountrySchema,
    # RoleSchema,
    )
import re



class Town(BaseModel):
    name: str
    country_id: str

    


class TownCreate(Town):
   pass


class TownUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    country_id: Optional[constr(max_length=256)] = None
    


# =============================== USER SCHEMA ===============================
class TownSchema(BaseMixinSchema):
    name: str
    country_id: str
    country: CountrySchema = None
    owners: List[UserInfo] = []  # Liste vide par défaut
    articles: List[ArticleSchema] = []  # Liste vide par défaut

    class Config:
        from_attributes = True


