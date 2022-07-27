import email
from .base_model import BaseModel, BaseTime
from sqlalchemy import Column, String, Integer, Float, DateTime , Date, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

class User(BaseModel):
    """ master table for User management service"""
    __tablename__ = 'user'
    account_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
 
    