from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.schemas.signals_schemas import SignalListing
from app.schemas.article_miltimedias_schemas import ArticleMultimediaListing

class Article(BaseModel):
    name: str
    reception_place: str
    category_article_id: str
    article_statu_id: str
    description: str = Field(..., max_length=65535)
    end_date: datetime
    price: float = Field(..., description="Cet attribut supérieur à 0.")
    
    

class ArticleCreate(Article):
   image_principal: str
   


class ArticleListing(ArticleCreate):
    id: str
    refnumber: str
    owner_id: str
    publish: bool = False
    locked: bool = False
    active: bool
    
    class Config:
        from_attributes = True 

class ArticleDetail(ArticleListing):
    
    publish: bool
    locked: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    article_multimedias: List[ArticleMultimediaListing]
    signals: List[SignalListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class ArticleUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    reception_place: Optional[constr(max_length=256)] = None
    owner_id: Optional[constr(max_length=256)] = None
    category_article_id: Optional[constr(max_length=256)] = None
    article_statu_id: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None
    image_principal: Optional[constr(max_length=256)] = None
    price: Optional[float] = Field(None, ge=0)
    publish: Optional[bool] = False
    locked: Optional[bool] = False
    # active: bool = True
