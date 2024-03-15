from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional

class ArticleMultimedia(BaseModel):
    link_media: str
    article_id: str
    
    

class ArticleMultimediaCreate(ArticleMultimedia):
   pass


class ArticleMultimediaListing(ArticleMultimedia):
    id: str
    refnumber: str
    active: bool
    
    class Config:
        from_attributes = True 

class ArticleMultimediaDetail(ArticleMultimediaListing):
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class ArticleMultimediaUpdate(BaseModel):
    link_media: Optional[constr(max_length=256)] = None
    article_id: Optional[constr(max_length=256)] = None
    # active: bool = True
