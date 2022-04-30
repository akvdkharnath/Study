#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   asn.py
@Time    :   2021/11/10 14:18:39
@Author  :   Eunimart 
@Version :   1.0
@Contact :   contact@eunimart.com
@License :   © Copyright 2021 Eunimart. All rights reserved
@Desc    :   Business rules related to ASN header and ASN line item
'''

from email import message
from .base_service import BaseService, calculator_dic, logistics_dic
import uuid
import json
import math
from sqlalchemy import desc, asc
from typing import List
class Asn(BaseService):

    def __init__(self):
        pass
       
AsnOperations = Asn()
