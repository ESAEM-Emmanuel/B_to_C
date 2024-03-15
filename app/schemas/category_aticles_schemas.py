from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.schemas.articles_schemas import ArticleListing

class CategoryArticle(BaseModel):
    name: str
    description: str = Field(..., max_length=65535)
    
    

class CategoryArticleCreate(CategoryArticle):
   image: str


class CategoryArticleListing(CategoryArticleCreate):
    id: str
    refnumber: str
    active: bool
    
    class Config:
        from_attributes = True 

class CategoryArticleDetail(CategoryArticleListing):
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    articles: List[ArticleListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class CategoryArticleUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None
    image: Optional[constr(max_length=256)] = None
    

