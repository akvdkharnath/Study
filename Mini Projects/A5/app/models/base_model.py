
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from app.config.db import engine

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    """ Create a seeion for it"""
    db = Session()
    try:
        yield db
    finally:
        db.close()
        

class BaseTime(object):
    @classmethod
    def get_time(cls):
        """ returns current Indian datetime """
        utc_dt = datetime.now(timezone.utc) # UTC time
        hours_added = timedelta(hours = 5, minutes= 30)
        return utc_dt + hours_added

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_archive = Column(Integer, default=0)

    @declared_attr
    def created_datetime(self):
        return Column(DateTime, default=BaseTime.get_time)

    @declared_attr
    def updated_datetime(self):
        return Column(DateTime, default=BaseTime.get_time, onupdate=BaseTime.get_time)

    @declared_attr
    def created_by(self):
        return Column(String(255))

    @declared_attr
    def updated_by(self):
        return Column(String(255))

    def __repr__(self):
        name = self.id
        return "{}('{}')".format(self.__class__.__name__, name)