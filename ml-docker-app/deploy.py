import boto3

# Define IAM role
role = "arn:aws:iam::072440950856:role/service-role/AmazonSageMaker-ExecutionRole-20240314T135892"

# Define your custom Docker image URI in Amazon ECR
docker_image_uri = "072440950856.dkr.ecr.us-east-1.amazonaws.com/bankchurnprediction:latest4"
model_data_url = "s3://sagemaker-us-east-1-072440950856/sagemaker/model_artifacts.tar.gz"

# Create a SageMaker client
sagemaker_client = boto3.client('sagemaker')

# Define model name and primary container
model_name = "my-randomforest-model4"
primary_container = {
    'Image': docker_image_uri,
    'ModelDataUrl': model_data_url,  # Location of your model artifact in S3
}

# Create the model
sagemaker_client.create_model(
    ModelName=model_name,
    ExecutionRoleArn=role,
    PrimaryContainer=primary_container
)

# Define endpoint configuration name
endpoint_config_name = "my-endpoint-config2"

# Define instance type and count
instance_type = "ml.t2.medium"
instance_count = 1

# Define endpoint name
endpoint_name = "my-endpoint4"

log_group_name = '/aws/sagemaker/random-forest-logs'
log_capture_prefix = 's3://sagemaker-us-east-1-072440950856/sagemaker/outputlogs/'

# Create endpoint configuration
sagemaker_client.create_endpoint_config(
    EndpointConfigName=endpoint_config_name,
    ProductionVariants=[
        {
            "VariantName": "RandomForestVariant1",
            "ModelName": model_name,
            "InitialInstanceCount": instance_count,
            "InstanceType": instance_type,
            "InitialVariantWeight": 1.0
        }
    ]
)


# Create endpoint
sagemaker_client.create_endpoint(
    EndpointName=endpoint_name,
    EndpointConfigName=endpoint_config_name,
)
