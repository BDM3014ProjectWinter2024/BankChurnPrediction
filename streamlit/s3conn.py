import json
import boto3
import botocore
import pandas as pd

class S3Utils:
    def __init__(self, secret_name_or_arn, file_path=None):
        self.secret_name_or_arn = secret_name_or_arn
        self.file_path = file_path
        if file_path:
            self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name = self.get_aws_credentials_from_file()
        else:
            self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name = self.get_aws_credentials_from_secrets_manager()
        self.s3_client = self.create_s3_client()

    def get_aws_credentials_from_secrets_manager(self):
        client = boto3.client(service_name='secretsmanager')
        get_secret_value_response = client.get_secret_value(SecretId=self.secret_name_or_arn)
        secret_dict = json.loads(get_secret_value_response['SecretString'])
        return secret_dict['aws_access_key_id'], secret_dict['aws_secret_access_key'], secret_dict['bucket_name']

    def get_aws_credentials_from_file(self):
        credentials_df = pd.read_csv(self.file_path)
        return credentials_df['aws_access_key_id'].iloc[0], credentials_df['aws_secret_access_key'].iloc[0], credentials_df['bucket_name'].iloc[0]

    def create_s3_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def check_and_transfer_file(self, source_key, destination_key):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=destination_key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                self.s3_client.copy_object(
                    Bucket=self.bucket_name,
                    CopySource=f"{self.bucket_name}/{source_key}",
                    Key=destination_key
                )
            else:
                raise e

    def check_file_exists(self, file_key):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise e

    def read_csv_from_s3(self, file_key):
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
        return pd.read_csv(obj['Body'])

    def write_csv_to_s3(self, file_key, df):
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=file_key,
            Body=csv_buffer.getvalue()
        )
    
    def upload_file(self, file_key, file_path):
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, file_key)
            print(f"The file '{file_key}' has been successfully uploaded to the S3 bucket '{self.bucket_name}'.")
        except botocore.exceptions.ClientError as e:
            printhist(f"Failed to upload file '{file_key}' to S3 bucket '{self.bucket_name}'. Error: {e}")
        
    def get_s3_object(self, file_key):
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return obj['Body']
        except botocore.exceptions.ClientError as e:
            print(f"Failed to get file '{file_key}' from S3 bucket '{self.bucket_name}'. Error: {e}")
            return None
class ConnectToS3:
    def __init__(self):
        self.env = "dev"  # dev, test, staging, prod
        # output file keys for various stages of the pipeline
        self.output_file_key_data_feature_engineering = f'{self.env}/final/bank_data_feature_eng.csv'
        self.output_file_key_data_random_forest_pkl = f'{self.env}/final/model_one/model.pkl'
        self.output_file_key_data_xg_boost_pkl = f'{self.env}/final/model_two/model.pkl'
        self.output_file_key_data_svm_model_pkl = f'{self.env}/final/model_three/model.pkl'
        self.output_file_key_data_clustering_model_pkl = f'{self.env}/final/model_clustering/model.pkl'
        self.output_file_key_data_svm_model_tar = f'{self.env}/final/model_three/model.tar.gz'
        # Initialize S3Utils using credentials from Secrets Manager
        self.s3_utils = S3Utils(secret_name_or_arn="arn:aws:secretsmanager:us-east-2:767397996410:secret:dev/s3/bucket_token-6t6xMP")
 