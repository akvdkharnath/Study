#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   db.py
@Time    :   2021/11/10 14:19:32
@Author  :   Eunimart 
@Version :   1.0
@Contact :   contact@eunimart.com
@License :   © Copyright 2021 Eunimart. All rights reserved
@Desc    :   Used to maintain and establish the database connection.
'''

from click import echo
from sqlalchemy import create_engine
from app.config.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)