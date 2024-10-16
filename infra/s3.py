import boto3
from botocore.config import Config
from dotenv import load_dotenv
import csv
import io
import os

load_dotenv()

aws_access_key_id = os.getenv('S3_ACCESS_KEY')
aws_secret_access_key = os.getenv('S3_SECRET_KEY')
aws_region = os.getenv('AWS_REGION')

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
    config=Config(signature_version='s3v4')
)

def get_csv_from_s3(bucket_name, folder_name, file_name):
    try:
        key = f"{folder_name}/{file_name}"  
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        
        csv_data = obj['Body'].read().decode('utf-8')
        
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        rows = [row for row in csv_reader]
        return rows
    except Exception as e:
        print(f"Error: {e}")
        return None
