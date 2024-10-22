from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.schemas.signals_schemas import SignalListing
from app.schemas.utils_schemas import UserInfo, TownList, CategoryList, ArticleStatusList
        
class Article(BaseModel):
    name: str
    town_id: str
    reception_place: str
    category_article_id: str
    article_status_id: str
    description: str = Field(..., max_length=65535)
    end_date: date
    price: float = Field(..., description="Cet attribut supérieur à 0.")
    
    

class ArticleCreate(Article):
   main_image: str
   other_images: Optional[List[str]] = None 
   


class ArticleListing(ArticleCreate):
    id: str
    refnumber: str
    publish: bool = False
    locked: bool = False
    active: bool
    owner_id: str
    updated_by: Optional[constr(max_length=256)] = None
    owner: Optional[UserInfo] = None
    town: Optional[TownList] = None
    article_status: Optional[ArticleStatusList] = None
    category: Optional[CategoryList] = None
    updator: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True 

class ArticleDetail(ArticleListing):
    
    publish: bool
    locked: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    signals: List[SignalListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class ArticleUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    town_id: Optional[constr(max_length=256)] = None
    reception_place: Optional[constr(max_length=256)] = None
    owner_id: Optional[constr(max_length=256)] = None
    category_article_id: Optional[constr(max_length=256)] = None
    article_status_id: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None
    main_image: Optional[constr(max_length=256)] = None
    price: Optional[float] = Field(None, ge=0)
    publish: Optional[bool] = False
    locked: Optional[bool] = False
    # active: bool = True
