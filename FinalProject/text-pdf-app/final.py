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

    s3_list = []
    for msg in messages.values():
        msg = re.sub("'", "\"", msg)
        json_obj = json.loads(msg)
        s3_list.append(s3_resource(
            json_obj[0]['s3']['bucket']['name'],
            json_obj[0]['s3']['bucket']['arn'],
            json_obj[0]['s3']['object']['key']))

     
    for res in s3_list:
        text_file = get_file_from_s3(res.object_key, res.bucket_name, res.object_key)
        text_files.append(text_file)
    return text_files

def get_file_from_s3(file_name, bucket_name, object_name):
    my_file = None
    s3_res = boto3.resource('s3')
    try:
        s3_res.Bucket(bucket_name).download_file(Key=object_name, Filename='/tmp/'+file_name)

        my_file = open('local_' + file_name, 'wb+')

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

