from os import getenv, path
from os import getenv, path
from dotenv import load_dotenv


FILE_PATH = path.dirname(__file__)
APP_ROOT = '/'.join(FILE_PATH.split('/')[:-2])
DOT_ENV_PATH = APP_ROOT + '/.env' 

load_dotenv(DOT_ENV_PATH)

class Config(object):

    DEPLOY_ENV = getenv('RUN_ENV','test')
    
    SERVER_PORT = getenv('SERVER_PORT','9000')
    
    SERVER_URL = getenv('SERVER_URL','127.0.0.1')

    POSTGRES_USER = getenv('POSTGRES_USER')

    POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD')

    POSTGRES_HOST = getenv('POSTGRES_HOST')

    POSTGRES_PORT = getenv('POSTGRES_PORT')

    POSTGRES_DATABASE = getenv('POSTGRES_DATABASE')
    
    # postgres://rwmlzpnxtekxbt:a3244d8047c8fd0a22844a69be002dc39a3bbab5e3dac8b84cf5f46ac73af1b6@ec2-52-5-110-35.compute-1.amazonaws.com:5432/dfn446ohg0bbis
    
    # SQLALCHEMY_DATABASE_URL = "postgres://{}:{}@{}:{}/{}".format(POSTGRES_USER,POSTGRES_PASSWORD,POSTGRES_HOST,POSTGRES_PORT,POSTGRES_DATABASE)
    SQLALCHEMY_DATABASE_URL = "postgresql://rwmlzpnxtekxbt:a3244d8047c8fd0a22844a69be002dc39a3bbab5e3dac8b84cf5f46ac73af1b6@ec2-52-5-110-35.compute-1.amazonaws.com:5432/dfn446ohg0bbis"