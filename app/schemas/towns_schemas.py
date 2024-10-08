from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.schemas.users_schemas import UserListing
from app.schemas.articles_schemas import ArticleListing


class CountryList(BaseModel):
    id: str
    name: str
    refnumber: str
    active: bool
    class Config:
        from_attributes = True  #
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
    
    
    class Config:
        from_attributes = True 

class TownDetail(TownListing):
    created_at: datetime
    created_by: Optional[str] = None  # Optionnel si nécessaire
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    country: CountryList
    owners : List[UserListing]
    articles : List[ArticleListing]
    
    class Config:
        from_attributes = True
        

class TownUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    country_id: Optional[constr(max_length=256)] = None
    
    # active: bool = True
