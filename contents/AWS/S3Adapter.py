'''
    Custom adapter class for AWS S3 Service.
'''
import boto3
from botocore.exceptions import ClientError

class S3_Store():
    
    connected = False
    bucket_name = ''
    region = ''
    s3 = None


    def __init__(self):
        self.s3 = boto3.client('s3')

    def set_bucket_name(self, _name):
        self.bucket_name = _name
    
    def set_region(self, _region):
        self.region = _region

    def list_buckets(self):
        
        try:
            buckets = self.s3.list_buckets()
            print('buckets')
            for bucket in buckets['Buckets']:
                print(f'{bucket["Name"]}')
        except ClientError as e:
            print(f'Error: {e}')

    # lists all the objects in a bucket
    def list_all_objects_in_bucket(self, bucket_name):

        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                for obj in response['Contents']:
                    print(obj['Key'])
            else:
                print(f'{bucket_name} is empty')
                      
        except Exception as e:
            print(f'Error: {e}')
    
    # puts a local file into an s3 bucket
    def put_file_in_bucket(self, local_file_path, s3_filename) -> bool:

        if self.bucket_name != '' or self.bucket_name is not None:
            try:
                self.s3.upload_file(local_file_path, self.bucket_name, s3_filename)
                return True
            except Exception as e:
                print(f'Error uploading file: {e}')
                return False
        
        return False
    
    # download a file from bucket
    def get_file_from_bucket(self, s3_filename, download_path) -> bool:
        if self.bucket_name != '' or self.bucket_name is not None:
            try:
                self.s3.download_file(self.bucket_name, s3_filename, download_path)
                return True
            except Exception as e:
                print(f'Error downloading file: {e}')
                return False

        return False
    
    # delete a file from a bucket
    def remove_file_from_bucket(self, s3_filename) -> bool:

        if self.bucket_name != '' or self.bucket_name is not None:
            try:
                self.s3.delete_object(self.bucket_name, s3_filename)
                return True
            except Exception as e:
                print(f'Error deleting from s3 bucket: {e}')
