from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional
from app.schemas.utils_schemas import AnounceList, EntertainmentSiteList, ReelList, StoryList, UserInfo, EventList

class Signal(BaseModel):
    event_id: Optional[constr(max_length=256)] = None
    anounce_id: Optional[constr(max_length=256)] = None
    reel_id: Optional[constr(max_length=256)] = None
    story_id: Optional[constr(max_length=256)] = None
    entertainment_site_id: Optional[constr(max_length=256)] = None
       

class SignalCreate(Signal):
   pass


class SignalListing(Signal):
    id: str
    refnumber: str
    owner_id: str
    created_by: Optional[constr(max_length=256)] = None
    updated_by: Optional[constr(max_length=256)] = None
    creator: Optional[UserInfo] = None
    updator: Optional[UserInfo] = None
    owner: Optional[UserInfo] = None
    event: Optional[EventList] = None
    anounce: Optional[AnounceList] = None
    reel: Optional[ReelList] = None
    story: Optional[StoryList] = None
    entertainment_site: Optional[EntertainmentSiteList] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    active: bool
    
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
    event_id: Optional[constr(max_length=256)] = None
    anounce_id: Optional[constr(max_length=256)] = None
    reel_id: Optional[constr(max_length=256)] = None
    story_id: Optional[constr(max_length=256)] = None
    entertainment_site_id: Optional[constr(max_length=256)] = None
    

