#!/usr/bin/env python
# --coding:utf-8 --
'''
@File    :   asn_line_item.py
@Time    :   2021/11/11 16:29:45
@Author  :   Eunimart 
@Version :   1.0
@Contact :   contact@eunimart.com
@License :   © Copyright 2021 Eunimart. All rights reserved
@Desc    :   Views/Routes related to asn line item
'''

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
import json

from app.models.base_model import get_db

asn_line_item_router = APIRouter(
    prefix = '/api/v1/eunimart_asn_management/asn_line_items',
    tags = ["ASN LINE ITEMS"]
    )

