import random
import hashlib
import os
import base64
from typing import List


from app.models.base_model import Session
from app.config.config import Config

from .base_service import BaseService



class Auth(BaseService):

    def __init__(self):
        pass

    def password_hasing(self, raw_password: str) -> List:
        algo = Config.HASHING_ALGORITHM
        salt = os.urandom(32)       
        key = hashlib.pbkdf2_hmac(algo, raw_password.encode('utf-8'), salt, 100000, dklen=128)
        # key = key.decode('utf-8')
        # salt = salt.decode('utf-8')
        
        key = base64.b64encode(key).decode('utf-8')
        salt = base64.b64encode(salt).decode('utf-8')
        return [salt, key]

    def password_verification(self, password: str, salt: str, key: str) -> bool:
        algo = Config.HASHING_ALGORITHM
        key = base64.b64decode(key)
        new_key = hashlib.pbkdf2_hmac(algo,password.encode('utf-8'),salt, 100000)
        return new_key == key 


AuthOperations = Auth()

