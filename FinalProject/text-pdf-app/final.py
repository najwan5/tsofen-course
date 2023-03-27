import json
import boto3
import re
from botocore.exceptions import ClientError
from fpdf import FPDF
import textwrap
import os
import time


def download_files_from_s3(messages):
    text_files = []
    #messages = {
	#'AQEB9/7y+SEaOBK5TIH2fqo+qzGRo33wWCjq/jRWVpdWO4yHQOUxREzpvB5MIMDO9gCKo5hpklUg/yjNeLkldtlyjyQjvH4KwryyEdqz6IMt/ghxhFgjUOgk/cG1QO0D1fxIEuczCCVZG/ddcX7YyMalItQFKy6rQv7FZcWKSfqJ4+ZMrFwsV7DpsO7n0irXA/OqkkIwy163qvulUg+xKGmtuk1e5CH8ZI9zARxa/3tANb6KsEFRrYgfva5N8DCmtaNg9KiOG3u8K+YgX6resI3S0EUcAraxA4t74plucjnE9YdHzq4tR2rPNq43B0XLpe2uVgCPfG9vA7ynhLQ/GYBNm/D6QGH0GEDtppAGYXOfG5C0nxYP+Dp72awjttmNQqgcoc7tHw1MNEg5KOltY5xkUg==': "[{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2023-03-17T11:17:18.120Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDARVRJFUTV7DNOZFKJD'}, 'requestParameters': {'sourceIPAddress': '141.226.10.162'}, 'responseElements': {'x-amz-request-id': 'R3YHQ1ZNP289KZJ2', 'x-amz-id-2': 'Uf9XQGdpk7uLZs3pLMXeInmrQh+PhF1Mlf9OhoQ6bYONYw7S1guBfJCfJApkcnA53Sr11hiPYuWWrop2FsqklP/vG/8yOoUg'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '4a7f8b9b-393e-43ef-acf3-783240fbce8c', 'bucket': {'name': 'tsofen-final-bucket', 'ownerIdentity': {'principalId': 'AXYSL54NJPX5F'}, 'arn': 'arn:aws:s3:::tsofen-final-bucket'}, 'object': {'key': 'sample2.txt', 'size': 1148, 'eTag': '435600e90e91ddf773a541df7c4b04ac', 'sequencer': '0064144C3E08806DF2'}}}]",
	#'AQEBmhR0FUVN9UmR8g5p/3+W3PaQaQz5LuQfEQURLBkI1roeBDk8d1gR67nLz2UeFIfw8qa9XLmJZPt1eOi6fXMcrWFSJJYGM68pPyG04sq+VbdpiM092doPXv/bPYqpxOveoDBsK4a+m+rHJAlEarZO3bVXbx0ZpcmRdX5kRHnVLX1zwxdWHC0cmjbAHwQu+fQ0cjqTZsT4PqR7ocri+f3dD+WPhLa+PWoJdxOL5JQAJaDPKiXfPlDSgDBT+R88X+OaZbmWMKQHoAkpK12KAyylkyWkVgD2lLzcHUhYkUqCtePOhc9kSKpy8UcTFIiGzQr3uu/oygXaO3Yyiw4sVwsMYmfFIluLCqVyAKiVmarnSC6+3cktApLKYD8Nh6CworK0y5Mtu224UZqzIdumOSRX9Q==': "[{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2023-03-17T11:17:17.338Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDARVRJFUTV7DNOZFKJD'}, 'requestParameters': {'sourceIPAddress': '141.226.10.162'}, 'responseElements': {'x-amz-request-id': 'STKS1BXPB63ZYNCE', 'x-amz-id-2': 'CaCl069I4rm8tEC3o+1um2rmuNDxgBCHCFY10ngQylSyVH4RXuJhKZ2NAs9ap13tz9g5OgogCbEi5mNxGDFFTBfp0ov2Roq/'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '4a7f8b9b-393e-43ef-acf3-783240fbce8c', 'bucket': {'name': 'tsofen-final-bucket', 'ownerIdentity': {'principalId': 'AXYSL54NJPX5F'}, 'arn': 'arn:aws:s3:::tsofen-final-bucket'}, 'object': {'key': 'sample1.txt', 'size': 505, 'eTag': '3d843e5ca6a27489c6f2b719783f6bfa', 'sequencer': '0064144C3D4F27A6A3'}}}]",
	#'AQEBHOChqAzZSyJATPNbCJ0RHEC4lV6pqj90CtIc14+maJqxeHPjXArhnKSb4RSUknjxd3r8Nwj4uIqgLy5VNtTZfGato2M4cssVyUMnAxyiOZr2Bwe9i8JMxu/W4+Av+exN/De/+D9WvxAGjy2I/VCgjMNFyaVI5pIymvaVMJ3a9QQNpwuiMI9SnlKd6uxEw6fyQ49+olRzjhtXYVI5zJhTwmu/VV+X3dT7BmxGE6rmyTw7SjtBGgXPo3x4kHeQBs+DWxKOdZO/nJI9ocSP87sotNJWk96y6BU4dnrVNabEgqFLLrN4BOvNOfHvEumArWFcDyFAUYYjpvfjobqFxvoPyvpcpbefKF+RU7Ko1qIeIT6PcWlTm9RejakUyi2VGRaSFesgdaVs1Zx3P0NwX22RAg==': "[{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1', 'eventTime': '2023-03-17T11:17:16.538Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDARVRJFUTV7DNOZFKJD'}, 'requestParameters': {'sourceIPAddress': '141.226.10.162'}, 'responseElements': {'x-amz-request-id': '36KWKKGCSZEHT821', 'x-amz-id-2': '1uanK0PEc7dAqNtIGrxNSky9xU8y1ob8EzjaGc3yiCYarIhS4+JfK9qzGCVh0dCrFVr8r+moosGazR9rV6EkQU34MZ3kcpnn'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '4a7f8b9b-393e-43ef-acf3-783240fbce8c', 'bucket': {'name': 'tsofen-final-bucket', 'ownerIdentity': {'principalId': 'AXYSL54NJPX5F'}, 'arn': 'arn:aws:s3:::tsofen-final-bucket'}, 'object': {'key': 'sample3.txt', 'size': 1377, 'eTag': 'ceb84ded1280d2aef28b632bab2c618d', 'sequencer': '0064144C3C74A40502'}}}]"
    #}
    s3_list = []
    for msg in messages.values():
        msg = re.sub("'", "\"", msg)
        json_obj = json.loads(msg)
        s3_list.append(s3_resource(
            json_obj[0]['s3']['bucket']['name'],
            json_obj[0]['s3']['bucket']['arn'],
            json_obj[0]['s3']['object']['key']))

     
    for res in s3_list:
        #print(res.bucket_name)
        #print(res.bucket_arn)
        #print(res.object_key)
        text_file = get_file_from_s3(res.object_key, res.bucket_name, res.object_key)
        text_files.append(text_file)
    return text_files

def get_file_from_s3(file_name, bucket_name, object_name):
    my_file = None
    s3_res = boto3.resource('s3')
    try:
        # sample1.txt will be downloaded to /tmp
        s3_res.Bucket(bucket_name).download_file(Key=object_name, Filename='/tmp/'+file_name)

        my_file = open('local_' + file_name, 'wb+')
        #local_sample1.txt will be downloded to /home/najwan/Documents/Class/Python/testEnv
        s3_res.Bucket(bucket_name).download_fileobj(object_name, my_file)
        my_file.close()
        my_file = open('local_' + file_name, 'r')
        return my_file
        
    except ClientError as e:
        print(e.MSG_TEMPLATE)
        return None
    
def convert_text_to_pdf(text_files):
    
    for txt in text_files:
        input_filename = txt.name.split(".")[0]
        output_filename = input_filename + '.pdf'
        file = open(input_filename + '.txt')
        text = file.read()
        file.close()
        text_to_pdf(text, output_filename)
        
    path = os.path.abspath(os.getcwd())
    return path


def text_to_pdf(text, filename):
    a4_width_mm = 160
    pt_to_mm = 0.35
    fontsize_pt = 14
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')

def upload_pdf_to_s3(pdf_files_path):
    #'/home/najwan/Documents/Class/Python/testEnv'
    s3_client = boto3.client('s3')
    files_list = os.listdir(pdf_files_path)
    pdfs = get_pdfs(files_list)

    if(len(pdfs) > 0):
        for pdf in pdfs:
            try:
                response = s3_client.upload_file(pdf, s3_bucket_name, pdf)
            except ClientError as e:
                return False
        return True
    else:
        return False

def get_pdfs(files):
    pdfs = []
    for file in files:
        if file.endswith('.pdf'):
            pdfs.append(file)
    return pdfs


def handle_messages(messages):
    text_files = download_files_from_s3(messages)
    pdf_files_path = convert_text_to_pdf(text_files)
    #pdf_files_path = '/home/najwan/Documents/Class/Python/testEnv'
    is_uploaded = upload_pdf_to_s3(pdf_files_path)
    if is_uploaded:
        print('PDFs uploaded successfully to S3')
    else:
        print('Failed to upload PDFs to S3')

#####################################

s3_bucket_name = 'tsofen-final-bucket'
client = boto3.client('sqs')
queues = client.list_queues()
queue_url = queues['QueueUrls'][0]
class s3_resource:
    def __init__(self, bucket_name, bucket_arn, object_key):
        self.bucket_name = bucket_name
        self.bucket_arn = bucket_arn
        self.object_key = object_key
messages =	{}
while True:
    receive_response = client.receive_message(
        QueueUrl = queue_url,
        AttributeNames = ['All'],
        VisibilityTimeout = 60
    )
    
    if 'Messages' in receive_response:
        msg_body = receive_response['Messages'][0]['Body']
        msg_body = re.sub("'", "\"", msg_body)
        json_obj = json.loads(msg_body)
        key = json_obj[0]['s3']['object']['key']
        receipt_handle = receive_response['Messages'][0]['ReceiptHandle']

        if key.endswith('.txt'):         
            messages[receipt_handle] = receive_response['Messages'][0]['Body']
            print('received message:')
            print(key) 

        deleted = client.delete_message(
            QueueUrl = queue_url,
            ReceiptHandle = receipt_handle
        )
        #print('receive_response:')
        #print(receive_response)       
    else:
        if len(messages) > 0:
            handle_messages(messages)
        print('Queue is empty. Waiting for new messages.')
        time.sleep(5)

