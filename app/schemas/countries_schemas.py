from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from app.schemas.towns_schemas import TownListing
from typing import Optional, List
from app.schemas.utils_schemas import UserInfo
        
class Country(BaseModel):
    name: str
        

class CountryCreate(Country):
   pass


class CountryListing(Country):
    id: str
    refnumber: str
    active: bool
    created_by: Optional[constr(max_length=256)] = None
    updated_by: Optional[constr(max_length=256)] = None
    creator: Optional[UserInfo] = None
    updator: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True 

class CountryDetail(CountryListing):
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    towns : List[TownListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class CountryUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    # active: bool = True
