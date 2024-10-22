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
        
class CategoryList(BaseModel):
    id: str
    name: str
    refnumber: str
    description: str = Field(..., max_length=65535)
    active: bool
    class Config:
        from_attributes = True  #
        
class ArticleStatusList(BaseModel):
    id: str
    name: str
    refnumber: str
    description: str = Field(..., max_length=65535)
    active: bool
    class Config:
        from_attributes = True  #
        
class ArticleList(BaseModel):
    id: str
    refnumber: str
    name: str
    town_id: str
    reception_place: str
    category_article_id: str
    article_status_id: str
    description: str = Field(..., max_length=65535)
    end_date: date
    price: float = Field(..., description="Cet attribut supérieur à 0.")
    main_image: str
    other_images: Optional[List[str]] = None
    publish: bool = False
    locked: bool = False
    owner_id: str
    updated_by: Optional[constr(max_length=256)] = None
    owner: Optional[UserInfo] = None
    town: Optional[TownList] = None
    article_status: Optional[ArticleStatusList] = None
    category: Optional[CategoryList] = None
    updator: Optional[UserInfo] = None 
    active: bool
    class Config:
        from_attributes = True  #