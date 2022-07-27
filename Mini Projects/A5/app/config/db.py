from click import echo
from sqlalchemy import create_engine
from app.config.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)