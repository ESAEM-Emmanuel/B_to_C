from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.models.models import GenderType

class UserInfo(BaseModel):
    id: str
    refnumber: str
    phone: str
    town_id: str
    username: Optional[str] = None
    email: EmailStr
    birthday: Optional[date] = None
    gender: Optional[GenderType] = None
    image: Optional[constr(max_length=256)] = None
    active: bool
    class Config:
        from_attributes = True  #
        

class CountryList(BaseModel):
    id: str
    name: str
    refnumber: str
    active: bool
    class Config:
        from_attributes = True  #
        
class TownList(BaseModel):
    id: str
    name: str
    country_id: str
    refnumber: str
    active: bool
    class Config:
        from_attributes = True  #