from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional

from app.schemas.utils_schemas import EntertainmentSiteList, UserInfo

class Favorite(BaseModel):
    entertainment_site_id: str
    
    

class FavoriteCreate(Favorite):
   pass


class FavoriteListing(Favorite):
    id: str
    refnumber: str
    owner_id: str
    created_by: Optional[constr(max_length=256)] = None
    updated_by: Optional[constr(max_length=256)] = None
    creator: Optional[UserInfo] = None
    updator: Optional[UserInfo] = None
    owner: Optional[UserInfo] = None
    entertainment_site: Optional[EntertainmentSiteList] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    active: bool
    
    class Config:
        from_attributes = True 

class FavoriteDetail(FavoriteListing):
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 
        # orm_mode = True 
        

class FavoriteUpdate(BaseModel):
    entertainment_site_id: Optional[constr(max_length=256)] = None
    

