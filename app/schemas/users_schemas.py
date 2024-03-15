from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from app.schemas.articles_schemas import ArticleListing
from app.schemas.signals_schemas import SignalListing

from app.models.models import GenderType

class User(BaseModel):
    phone: str
    town_id: str
    username: Optional[str] = None
    email: EmailStr
    birthday: Optional[date] = None
    gender: Optional[GenderType] = None
    image: Optional[constr(max_length=256)] = None
    

class UserCreate(User):
   password: str
   is_staff: bool = False
   


class UserListing(User):
    id: str
    refnumber: str
    active: bool
   
    class Config:
        from_attributes = True 

class UserDetail(UserListing):
    
    image: str
    is_staff: bool
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    articles: List[ArticleListing]
    signals: List[SignalListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class UserUpdate(BaseModel):
    username: Optional[constr(max_length=256)] = None
    town_id: Optional[constr(max_length=256)] = None
    phone: Optional[constr(max_length=256)] = None
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    gender: Optional[GenderType] = None
    image: Optional[constr(max_length=256)] = None
    password: Optional[constr(max_length=256)] = None
    is_staff: Optional[bool] = False
    # active: bool = True


class UserLogin(BaseModel):
#    email: EmailStr
   username: str
   password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
