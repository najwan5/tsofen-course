import boto3
from botocore.exceptions import ClientError
import requests
import os

dynamodb = boto3.resource('dynamodb')

def create_table(table_name):
    users = dynamodb.create_table(
        TableName= table_name,
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Wait until the table exists.
    users.wait_until_exists()
    print('table ' + table_name + ' was created')
    return users

def add_item_to_table(item, table):
    #Add item to table
    table.put_item(
    Item= item
    )
    print('items was added')

def get_item_from_table(table, key):
    
    response = table.get_item(
        Key= key
    )
    item = response['Item']
    print('getting item of ' + key[users.key_scema[0]['AttributeName']] + ' key from table ' +table.name +': ' +  str(item))



#########################################
users = create_table('users')

#Get existing table
#users = dynamodb.Table('users')


item ={
            'username': 'janedoe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'age': 25,
            'levels': ['l1', 'l2', 3]
            
        }
add_item_to_table(item, users)
item ={
            'username': 'bobalice',
            'first_name': 'Bob',
            'last_name': 'Aice',
            'age': 35,
            'levels': ['l1', 'l2', 3, 'level4']
            
        }
add_item_to_table(item, users)

key={
        users.key_schema[0]['AttributeName']: 'janedoe'
    }
get_item_from_table(users, key)