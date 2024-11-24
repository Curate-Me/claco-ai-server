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
    
def upload_csv_to_s3(bucket_name, folder_name, file_name, csv_data):
    try:
        key = f"{folder_name}/{file_name}"  

        csv_bytes = csv_data.encode('utf-8')

        s3_client.put_object(Bucket=bucket_name, Key=key, Body=csv_bytes)

        print(f"File {file_name} successfully uploaded to {bucket_name}/{folder_name}")
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False

def upload_poster_to_s3(bucket_name, folder_name, file_name):
    try:
        key = f"{folder_name}/{file_name}"  # S3 키 생성

        # 파일 열기
        with open(file_name, 'rb') as file_data:
            s3_client.upload_fileobj(file_data, bucket_name, key)

        # S3 URL 반환
        s3_url = f"https://{bucket_name}.s3.{s3_client.meta.region_name}.amazonaws.com/{key}"
        return s3_url  # 문자열로 반환

    except Exception as e:
            print(f"Error uploading file to S3: {e}")
            return False

