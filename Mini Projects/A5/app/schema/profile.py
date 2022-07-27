from pydantic import BaseModel, validator
from enum import Enum
from typing import List, Optional
from datetime import datetime

class ProfileBase(BaseModel):
    name: str
    email: str

class ProfileCreate(ProfileBase):
    password: str
    class Config:
        schema_extra = {
            "example": {
                "name": "harnath",
                "email": "harnath@gmail.com",
                "password": "123456"
            }
        }
    pass



class Profile(ProfileBase):
    id: int
    account_id: str

    class Config:
        orm_mode = True
