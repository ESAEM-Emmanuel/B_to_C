from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from app.schemas.users_schemas import UserListing
from app.schemas.articles_schemas import ArticleListing

class Town(BaseModel):
    name: str
    country_id: str
    
    
    

class TownCreate(Town):
   pass


class TownListing(Town):
    id: str
    refnumber: str
    active: bool
    
    
    class Config:
        from_attributes = True 

class TownDetail(TownListing):
    
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[constr(max_length=256)] = None
    owners : List[UserListing]
    articles : List[ArticleListing]
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class TownUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    country_id: Optional[constr(max_length=256)] = None
    
    # active: bool = True
