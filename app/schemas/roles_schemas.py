# from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
# from datetime import datetime, date
# from enum import Enum
# from typing import Optional, List
# from app.schemas.profil_roles_schemas import ProfilRoleListing
# from app.schemas.privilege_roles_schemas import PrivilegeRoleListing
# from app.schemas.utils_schemas import UserInfo, TownList
# import re

# class Role(BaseModel):
#     name: str
#     description: Optional[str] = Field(
#         None,
#         description="La description du rôle est util pour définir comprendre la fonctionnalité.",
#     )
    
    

# class RoleCreate(Role):
#    pass


# class RoleListing(Role):
#     id: str
#     refnumber: str
#     created_by: Optional[constr(max_length=256)] = None
#     updated_by: Optional[constr(max_length=256)] = None
#     creator: Optional[UserInfo] = None
#     updator: Optional[UserInfo] = None
#     active: bool
    
#     class Config:
#         from_attributes = True 

# class RoleDetail(RoleListing):
    
#     created_at: datetime
#     created_by: str
#     privilege_roles: List[PrivilegeRoleListing]
#     profil_roles: List[ProfilRoleListing]
    
#     class Config:
#         from_attributes = True 
#         # orm_mode = True 
        

# class RoleUpdate(BaseModel):
#     name: Optional[constr(max_length=256)] = None
#     description: Optional[constr(max_length=65535)] = None
    
from pydantic import BaseModel, EmailStr, PositiveInt, validator, root_validator, constr,Field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Literal
from app.models.models import GenderType
from app.schemas.utils_schemas import (
    ArticleSchema,
    SignalSchema,
    FavoriteSchema,
    SubscriptionSchema,
    PrivilegeUserSchema,
    UserRoleSchema,
    BaseMixinSchema,
    TownSchema,
    PrivilegeRoleSchema,
    # CountrySchema,
    # CategoryArticleSchema,
    # ArticleStateSchema,
    # SubscriptionTypeSchema,
    # PrivilegeSchema,
    # RoleSchema,
    )
import re



class Role(BaseModel):
    name: str
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )
    


class RoleCreate(Role):
   pass


class RoleUpdate(BaseModel):
    name: Optional[constr(max_length=256)] = None
    description: Optional[constr(max_length=65535)] = None
    


# =============================== USER SCHEMA ===============================
class RoleSchema(BaseMixinSchema):
    name: str
    description: Optional[str] = Field(
        None,
        description="Le numéro de téléphone doit contenir entre 9 et 15 chiffres, avec un format valide (+, - autorisés).",
    )

    
    user_roles: List[UserRoleSchema] = []  # Liste vide par défaut
    privilege_roles: List[PrivilegeRoleSchema] = []  # Liste vide par défaut

    class Config:
        from_attributes = True


