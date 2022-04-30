#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   base_service.py
@Time    :   2021/11/10 14:18:42
@Author  :   Eunimart 
@Version :   1.0
@Contact :   contact@eunimart.com
@License :   © Copyright 2021 Eunimart. All rights reserved
@Desc    :   Base configuration for services
'''

import math
import json
from typing import Dict, Optional, List, Any, Union
from urllib import response
import requests
from app.core.helpers import Helpers
from sqlalchemy.orm import load_only
from sqlalchemy import desc, asc


from app.models.base_data import get_base_data

calculator_dic,package_dic,logistics_dic = get_base_data()
# calculator_dic,package_dic,logistics_dic = ({},{},{})


class BaseService(object):
    def __init__(self):
        pass
    
    def make_request(self, method: str, url: str, token: str, data: Optional[Union[dict, List]] = None, params: Optional[dict] = None, api_name: Optional[str] = "Data not provided"):
        """ makes request as per the method given 

        Args:
            method (str): method of request POST, GET or DELETE
            token (str): having barer token
            url (str): url
            data (Optional[Union[dict, List]], optional): request payload (body of the request). Defaults to None.
            params (Optional[dict]): query params. Defaults to {}.
            api_name (Optional[str]): name of API to which we are making request
        Returns:
            response from url requested
        """
        if params is None:
            params = {}
        header = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        print("Request:")
        print(f"Making an API call to {api_name}")
        print("URL: ", url)
        print("Method: ", method)
        print("Params: ", params)
        print("Body: ", data)

        if data  != None:
            response = requests.request(method,headers=header,url=url,data=json.dumps(data, indent=4),params=params)
        else:
            response = requests.request(method,headers=header,url=url,params=params)

        print("Response:")
        print("status:", response.status_code)
        if response.status_code != 200:
            print(response.text)
            print(f"unable to recive data from {api_name}")
            return {}
        print(response.json())
        return response.json()

    def currency_format(self,n: Any) -> str:
        """ Converts number as comma supperated value
        
        ex:

        100 --> 100

        1001 --> 1,001
        
        201020.10 --> 2,01,020.10
        """
        s, *d = str(n).partition(".")
        r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        return "".join([r] + d)
    
    def json_serializable_converter(self, data):
        data.pop("_sa_instance_state",None)
        if "created_datetime" in data:
            data["created_datetime"] = str(data["created_datetime"])
        if "created_date" in data:
            data["created_date"] = str(data["created_date"])
        if "updated_datetime" in data:
            data["updated_datetime"] = str(data["updated_datetime"])
        if "status_timestamp" in data:
            data["status_timestamp"] = str(data["status_timestamp"])
        if "expected_date" in data:
            data["expected_date"] = str(data["expected_date"])
        if "pickup_date" in data:
            data["pickup_date"] = str(data["pickup_date"])
        if "time_stamp" in data:
            data["time_stamp"] = str(data["time_stamp"])
        if "expected_date" in data:
            if data["expected_date"] == "None":
                data["expected_date"] = None
        if "pickup_date" in data:
            if data["pickup_date"] == "None":
                data["pickup_date"] = None       
        if "history" in data:
            if type(data["history"]) != type({}):
                data["history"] = json.loads(data["history"])
        return data

        
    def object_converter(self, results):
        """ convert DB responce to List of dict """
        if not isinstance(results, list):
            return self.json_serializable_converter(results._asdict())
        response_dic = []
        for row in results:
            try:
                response_dic.append(self.json_serializable_converter(row._asdict()))
            except Exception:
                response_dic.append(self.json_serializable_converter(row.__dict__))
        return response_dic

    def get_data_from_table(self, db: object, model):
        """ Get data from table

        Args:
            db (obj): database object
            model (SQLAlchemy class): table class

        Returns:
            [obj]: retrived row
        """
        # table_name = model.__class__.__name__
        query = db.query(model)
        results = query.all()
        return self.object_converter(results)
        
    def filter_data_from_table(self, db: object, model, filters: dict, columns: list = [], start_date: str = None, end_date: str = None, sort_column: str = None, sort_order: int = None) -> List:
        """ develops a filter query and return results

        Args:
            db (object): database pointer
            model (class): table name 
            filters (dict): filters to be applied
            columns (list, optional): list of columns to be selected from table. Defaults to [].
            start_date (str, optional): if given records with grater than or equal created date. Defaults to None.
            end_date (str, optional): if given records with less than or equal created date. Defaults to None.
            sort_column (str, optional): column name on which sort to apply. Defaults to None.
            sort_order (int, optional): -1 for sort selected column in asc else it desc. Defaults to None.

        Returns:
            [list]: list of record 
        """
        if columns:
            query = db.query(model).options(load_only(*columns))
        else:
            query = db.query(model)
        for attr,value in filters.items():
            # query = query.filter(getattr(model,attr) == value)
            if attr == "warehouse_id":
                query = query.filter(getattr(model,attr) == value)
            if type(value) == type([]):
                query = query.filter(getattr(model,attr).in_(value))
            else:
                query = query.filter(getattr(model,attr).like(f'%{value}%'))
        if start_date is not None and end_date is not None:
            query = query.filter(getattr(model,"created_datetime").between(start_date, end_date))
        if sort_column is not None:
            if sort_order == -1:
                results = query.order_by(asc(getattr(model,sort_column))).all()
            else:
                results = query.order_by(desc(getattr(model,sort_column))).all()
        else:
            results = query.order_by(desc(getattr(model,"created_datetime"))).all()

        return self.object_converter(results)
    
    def insert_data_to_table(self,db,model,data):
        """ Insert data into table

        Args:
            db (obj): database object
            model (SQLAlchemy class): table class
            data (dic): key(column) values values to be inserted

        Returns:
            [obj]: inserted row
        """
        insert = model(**data)
        db.add(insert)
        db.commit()
        return insert

    def update_data_to_table(self, db, model, id, data):
        """ Update data for an existing row

        Args:
            db (obj): database object
            model (SQLAlchemy class): table class
            data (dic): key(column) values values to be inserted
            id (int): id(PK)
            
        Returns:
            [obj]: Updated row
        """
        
        row_data = db.query(model).filter_by(id = id).first()
        for k,v in data.items():
            setattr(row_data, k, v)
        db.commit()
        return row_data
    
    def get_next_page(self,page_number, total_pages):
        return 0 if total_pages == 0 or page_number == total_pages else page_number + 1
    
    def get_previous_page(self, page_number):
        return 0 if (page_number == 1) else page_number - 1
    
    def get_paginated(self, results_object, per_page: int, page_number: int) -> dict:
        """ will add pagination  

        Args:
            data (List[dict]): list of dict, where dict represents a record
            per_page (int): number of records per page
            page_number (int): page number to which data requested

        Returns:
            [dict]: paginated data
        """
        
        records = results_object.limit(per_page).offset((page_number-1) * per_page)
        count = results_object.count()
        total_pages = math.ceil(count/per_page)
        
        if records in [None, []] or (page_number > total_pages):
            return {
                "status" : True,
                "data" : [],
                "pagination" : {
                    "per_page" : per_page,
                    "current_page" : page_number,
                    "next_page" : self.get_next_page(page_number, total_pages),
                    "previous_page" : self.get_previous_page(page_number),
                    "total_pages" :total_pages,
                    "total_rows" : count
                }
            }
        
        response_data = self.object_converter(records.all())
        return {
                "status" : True,
                "data" : response_data,
                "pagination" : {
                    "per_page" : per_page,
                    "current_page" : page_number,
                    "next_page" : self.get_next_page(page_number,total_pages),
                    "previous_page" : self.get_previous_page(page_number),
                    "total_pages" :total_pages ,
                    "total_rows" : count
                }
            }
    
    def delete_one_from_table(self, db, model,id):
        data = db.query(model).filter_by(id = id).first()
        db.delete(data)
        db.commit()
        return True

    def delete_all_from_table(self, db, model):
        data = db.query(model).all()
        for i in data:
            db.delete(i)
        db.commit()
        return True


BaseServiceOperations = BaseService()