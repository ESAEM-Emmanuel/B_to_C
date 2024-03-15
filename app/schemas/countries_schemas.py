from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from app.schemas.towns_schemas import TownListing
from typing import Optional, List


class Country(BaseModel):
    name: str
    
     

class CountryCreate(Country):
   pass


class CountryListing(Country):
    id: str
    refnumber: str
    active: bool
    
    class Config:
        from_attributes = True 

class CountryDetail(CountryListing):
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    towns : List[TownListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class CountryUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    # active: bool = True
