from os import getenv, path
from os import getenv, path
from dotenv import load_dotenv
load_dotenv()

class Config(object):

    DEPLOY_ENV = getenv('RUN_ENV','test')
    
    SERVER_PORT = getenv('SERVER_PORT','9000')
    
    SERVER_URL = getenv('SERVER_URL','127.0.0.1')

    POSTGRES_USER = getenv('POSTGRES_USER')

    POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD')

    POSTGRES_HOST = getenv('POSTGRES_HOST')

    POSTGRES_PORT = getenv('POSTGRES_PORT')

    POSTGRES_DATABASE = getenv('POSTGRES_DATABASE')

    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')

    JWT_ALGORITHM = getenv('JWT_ALGORITHM')

    HASHING_ALGORITHM = getenv('HASHING_ALGORITHM')

    ACCESS_TOKEN_EXPIRE_MINUTES = getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


    # SQLALCHEMY_DATABASE_URL = "postgresql://{}:{}@{}:{}/{}".format(POSTGRES_USER,POSTGRES_PASSWORD,POSTGRES_HOST,POSTGRES_PORT,POSTGRES_DATABASE)
    SQLALCHEMY_DATABASE_URL = "postgresql://llnimppazukiib:08ebcf22ee533f69f4e391815de654d4e92005376ae87dac05e51ad9a19c3bb8@ec2-44-195-169-163.compute-1.amazonaws.com:5432/df2cgd61ece65k"
