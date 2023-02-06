import boto3
from botocore.exceptions import ClientError
import requests
import os

def get_file_to_Upload(path_to_file):
    my_file = open(path_to_file,'r')
    print(my_file.read())
    return my_file

def upload_to_s3(file_to_s3, bucket_name, object_name):

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_to_s3.name, bucket_name, object_name)
    except ClientError as e:
        return False
    return True

def get_file_from_S3(file_name, bucket_name, object_name):
    my_file = None
    s3_res = boto3.resource('s3')
    try:
        s3_res.Bucket(bucket_name).download_file(Key=object_name, Filename='/tmp/'+file_name)

        my_file = open('local_file.txt', 'wb+')
        s3_res.Bucket(bucket_name).download_fileobj(object_name, my_file)
        my_file.close()
        my_file = open('local_file.txt', 'r')
        return my_file
        

    except ClientError as e:
        print(e.MSG_TEMPLATE)
        return None

###########################################################################################
file_path = '/home/najwan/Documents/Class/AWS/sample.txt'
bucket_name = 'test27012021-2'


#file_to_upload = get_file_to_Upload(file_path)
#object_name = os.path.basename(file_to_upload.name)
#is_uploaded = upload_to_s3(file_to_upload, bucket_name, object_name)
#print("is_uploaded" + str(is_uploaded))

file_name = 'sample.txt'
object_name = file_name
s3_file = get_file_from_S3(file_name, bucket_name, object_name)
if s3_file is not None:
    print('Reading from downloaded file:\n' + s3_file.read())
