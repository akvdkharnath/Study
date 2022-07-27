
from app.models.base_model import Session
from .base_service import BaseService

import uuid
import json
import math
from sqlalchemy import desc, asc
from typing import List

from app.models.user import User as UserModel
from app.schema.profile import ProfileCreate
from .auth import AuthOperations

class Profile(BaseService):

    def __init__(self):
        pass

    def create_profile(self, db: Session, data: ProfileCreate):
        password, salt = AuthOperations.password_hasing(data["password"])
        data["password"] = password
        data["salt"] = salt
        data["account_id"] = str(uuid.uuid4()) 
        insert = self.insert_data_to_table(db, UserModel, data)
        print(f"Profile for user {insert.name} created")
        return insert
        
ProfileOperations = Profile()
