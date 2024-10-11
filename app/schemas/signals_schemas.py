from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional
from app.schemas.utils_schemas import UserInfo
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
    created_by: Optional[constr(max_length=256)] = None
    updated_by: Optional[constr(max_length=256)] = None
    creator: Optional[UserInfo] = None
    updator: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True 

class SignalDetail(SignalListing):
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class SignalUpdate(BaseModel):
    owner_id: Optional[constr(max_length=256)] = None
    article_id: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None


