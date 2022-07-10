import boto3
from typing import List

class DynamoDB(object):

    def __init__(self):
        # self.dynamo_client = boto3.client('dynamodb')
        self.dynamodb = boto3.resource('dynamodb')

    def create_table(self, table_name:str, key_schema: List, attributes: List, provision: dict):
        table = self.dynamodb.create_table(
            TableName = table_name,
            KeySchema = key_schema,
            AttributeDefinitions = attributes,
            ProvisionedThroughput = provision
        )
        print(table)
        

    def insert_into_table(self, table_name:str, data:dict):
        table  = self.dynamodb.Table(table_name)        
        table.put_item(Item = data, TableName = table_name)
        
    def get_from_table(self, table_name:str, data:dict):
        table  = self.dynamodb.Table(table_name)
        data = table.get_item(Key = data, TableName = table_name)
        print(data)
        data = data["Item"]
        print(data)

DynamoDBOperations = DynamoDB()


# creating a table 

KEY_SCHEMA = [
    {
    "AttributeName": 'key',
    'KeyType': 'HASH'
    },
    {
    "AttributeName": 'name',
    'KeyType': 'RANGE'
    },
]    

ATTRIBUTE_DEFINITIONS = [
    {
    "AttributeName": "key",
    "AttributeType": "S"
    },
    {
    "AttributeName": "name",
    "AttributeType": "S"
    },
]

PROVISIONED_THROUGHPUT = {
    "ReadCapacityUnits": 5,
    "WriteCapacityUnits": 5
}

table_name = "dynamoH1"

# DynamoDBOperations.create_table(table_name, KEY_SCHEMA, ATTRIBUTE_DEFINITIONS, PROVISIONED_THROUGHPUT)


# Adding data to a table 

data  = {
    "key": "key3",
    "name": "harnath",
    "age": "24",
    "sex": "M",
    "amount": 2000
}

# DynamoDBOperations.insert_into_table(table_name, data)


# getting data from table 
data  = {
    "key": "key3",
    "name": "harnath",
}

DynamoDBOperations.get_from_table(table_name, data)
