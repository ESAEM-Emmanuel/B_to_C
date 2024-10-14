from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.schemas.users_schemas import UserListing
from app.schemas.articles_schemas import ArticleListing
from app.schemas.utils_schemas import UserInfo, CountryList


class Town(BaseModel):
    name: str
    country_id: str
    
    
    

class TownCreate(Town):
   pass


class TownListing(Town):
    id: str
    refnumber: str
    active: bool
    country: CountryList
    created_by: Optional[constr(max_length=256)] = None
    updated_by: Optional[constr(max_length=256)] = None
    creator: Optional[UserInfo] = None
    updator: Optional[UserInfo] = None
    
    
    class Config:
        from_attributes = True 

class TownDetail(TownListing):
    created_at: datetime
    updated_at: Optional[datetime] = None
    country: CountryList
    owners : List[UserListing]
    articles : List[ArticleListing]
    
    class Config:
        from_attributes = True
        

class TownUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    country_id: Optional[constr(max_length=256)] = None
    
    # active: bool = True
