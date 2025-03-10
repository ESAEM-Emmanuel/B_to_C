from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional
from app.schemas.utils_schemas import UserInfo, ArticleList
class Signal(BaseModel):
    
    article_id: str
    description: str = Field(..., max_length=65535)
    
    

class SignalCreate(Signal):
   pass


class SignalListing(Signal):
    id: str
    refnumber: str
    owner_id: str
    active: bool
    updated_by: Optional[constr(max_length=256)] = None
    owner: Optional[UserInfo] = None
    article: Optional[ArticleList] = None
    updator: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True 

class SignalDetail(SignalListing):
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class SignalUpdate(BaseModel):
    owner_id: Optional[constr(max_length=256)] = None
    article_id: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None


