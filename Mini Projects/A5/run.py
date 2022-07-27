#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   run.py
@Time    :   2021/11/11 16:29:45
@Author  :   Harnath 
@Version :   1.0
@Contact :   akvdkharnath@gmail.com.com
@License :   © Copyright 2021 Harnath. All rights reserved
@Desc    :   Main file
'''

import uvicorn
import time
import string
import random
from sqlalchemy.orm import Session
# from app.config.db import database

from fastapi import FastAPI, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware

from app.models.base_model import Base
from app.config.config import Config
from app.config.db import engine
from app.core.exception_handler import application_exception_handler

from app.routers.v1.profile import profile_router

from app.core.exception_handler import *

BIND_URL = Config.SERVER_URL
BIND_PORT = int(Config.SERVER_PORT)

description = """
"""

async def log_json(request: Request):
    if request.method in ["POST","PATCH"]:
        print("Request Body:")
        print(await request.json())


def build_router(app):
    """ Mapping all API's from router to application """ 
    app.include_router(profile_router, dependencies=[Depends(log_json)])

def create_tables():
    """ creating tables in database """
    Base.metadata.create_all(bind=engine)
    print("tables creation completed")


def create_static_data():
    """ inserting basic data required for static tables in database """
    # from app.models.base_data import base_data
    # base_data()
    # print("base data creation completed")
    pass


def start_application():
    app = FastAPI(
        title="PROJECT A5",
        description=description,
        version="2.0",
        license_info={
            "name": "© Copyright 2021 Harnath. All rights reserved",
        },
    )

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # exception handler for whole project
    app.add_exception_handler(Exception, handler= application_exception_handler)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """ will log request details and call function and log response details
        """
        if request.method == "OPTIONS": 
            return Response("", status_code=200, headers={
            'Access-Control-Max-Age': "10",
            'Content-Type': 'application/json',
            'Access-Control-Allow-Methods' : "GET, POST, PUT, OPTIONS, DELETE, PATCH",
            'Access-Control-Allow-Headers' : '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Origin': '*'
            } )

        idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        print("--------------------------Start-------------------------------------------")
        print(f"Request: {idem} started")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        print(f"Request: {idem} Completed")
        print(f"Process Time: {formatted_process_time} ms")
        print(f'Response Status code: {response.status_code}')
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        print("Response Body:")
        body = body.decode('utf8').replace("'", '"')
        print(body)
        print("--------------------------End---------------------------------------------")
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

    build_router(app)
    create_tables() 
    create_static_data()  
    # from app.config.schedule import auto_schedule
    return app 


if __name__ == "__main__":
    app = start_application()
    from app.models.base_model import get_db

    @app.get("/health-check")
    @app.get("/")
    async def root(db: Session = Depends(get_db)):
        return {"message": "Hello World server is working fine"}
    
    uvicorn.run(app, host=BIND_URL, port=BIND_PORT)