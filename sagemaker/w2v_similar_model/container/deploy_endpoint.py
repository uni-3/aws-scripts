# coding: utf-8

import os
import boto3
#import re
import json
#from time import gmtime, strftime
import time

region = boto3.Session().region_name

# model data url
# put your s3 bucket name here, and create s3 bucket
bucket = 'sagemaker-ap-northeast-1-xxxxxxxxx'
prefix = 'sagemaker/similar'
model_file_name = 'similar-model'

key = os.path.join(prefix, 'output', model_file_name, 'output/model.tar.gz')
model_data_url = 'https://s3-{}.amazonaws.com/{}/{}'.format(region, bucket, key)
#print(model_data_url)

bucket_path = 'https://s3-{}.amazonaws.com/{}'.format(region, bucket)

# model config
container_url = 'xxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/sm-w2v-similar:latest'
# copy from notebook instances's arn
sm_role = 'arn:aws:iam::xxxxxxxx:role/service-role/AmazonSageMaker-ExecutionRole'
model_name = 'similar' + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

# endpoint config
endpoint_config_name = 'Similar-EndpointConfig-' + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
instance_type = 'ml.t2.medium' # 'ml.m4.xlarge'

# hosting endpoint config
endpoint_name = 'Similar'


# refer https://docs.aws.amazon.com/sagemaker/latest/dg/ex1-train-model.html#ex1-train-model-create-training-job
def train(sm_client, model_data_url):
    # To be able to pass this role to Amazon SageMaker, the caller of this API must have the iam:PassRole permission.
    role = ""
    training_job_params = {
        "TrainingJobName": "w2v-similar",
        "AlgorithmSpecification": {
            "TrainingImage": container_url,
            "TrainingInputMode": "File"
        },
        "HyperParameters": {
            "size": 200,
        },
        "ResourceConfig": {
            "InstanceCount": 1,   
            "InstanceType": "ml.m4.xlarge",
            "VolumeSizeInGB": 5
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 86400
        },
        "RoleArn": role,
        "OutputDataConfig": {
            "S3OutputPath": bucket + "/"+ prefix + "/output"
        },
        "InputDataConfig": [
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": bucket + "/"+ prefix+ '/train/',
                        "S3DataDistributionType": "FullyReplicated" 
                    }
                },
                "ContentType": "text/csv",
                "CompressionType": "None"
            },
        ]
    }

    sm.create_training_job(**training_job_params)

    # wait for training to complete
    status = sm.describe_training_job(TrainingJobName=training_job_name)['TrainingJobStatus']
    print(status)
    sm.get_waiter('training_job_completed_or_stopped').wait(TrainingJobName=training_job_name)
    status = sm.describe_training_job(TrainingJobName=training_job_name)['TrainingJobStatus']
    print("Training job ended with status: " + status)
    if status == 'Failed':
        message = sm.describe_training_job(TrainingJobName=training_job_name)['FailureReason']
        print('Training failed with the following error: {}'.format(message))
        raise Exception('Training job failed')


def create_model(sm_client, model_data_url):

    primary_container = {
        'Image': container_url,
        'ModelDataUrl': model_data_url,
    }

    create_model_response = sm_client.create_model(
        ModelName=model_name,
        ExecutionRoleArn=sm_role,
        PrimaryContainer=primary_container
    )


def create_endpoint_config(sm_client):
    # model_url
    #sm_client = boto3.client('sagemaker')

    create_endpoint_config_response = sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[{
            'InstanceType': instance_type,
            'InitialInstanceCount': 1,
            'InitialVariantWeight': 1,
            'ModelName': model_name,
            'VariantName': 'AllTraffic'}])

    print("Endpoint Config Arn: " + create_endpoint_config_response['EndpointConfigArn'])


def create_endpoint(sm_client):
    # deploy & hosting

    #endpoint_config_name = 'BlazingText-Similar-EndpointConfig-2019-05-08-09-20-22'
    #sm_client = boto3.client('sagemaker')

    create_endpoint_response = sm_client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name)
    print(create_endpoint_response['EndpointArn'])

    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
    status = resp['EndpointStatus']
    print("Status: " + status)

    # wait for create endpoint
    while status == 'Creating':
        time.sleep(60)
        resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
        status = resp['EndpointStatus']
        print("Status: " + status)

    print("Arn: " + resp['EndpointArn'])
    print("Status: " + status)


def update_endpoint(sm_client, endpoint_name, endpoint_config_name):
    update_response = sm_client.update_endpoint(
        EndpointName=endpoint_name, # 'BlazingText-Similar-2019-05-09-04-12-31',
        EndpointConfigName=endpoint_config_name # 'BlazingText-Similar-EndpointConfig-2019-05-08-09-20-22'
    )

    print(update_response)


def delete_endpoint(sm_client, endpoint_name):
    delete_response = sm_client.delete_endpoint(
        EndpointName=endpoint_name
    )



def main():
    sm_client = boto3.client('sagemaker')

    # create model
    create_model(sm_client, model_data_url)
    create_endpoint_config(sm_client)
    create_endpoint(sm_client)

    # validate model
    endpoint_name = 'Similar'
    runtime_client = boto3.client('runtime.sagemaker')


    filename = './local_test/payload.csv'

    with open(filename, 'r') as f:
        payload = f.read().strip()

    print('payload', payload)
    custom_attributes = {
        "topn": 10
    }

    response = runtime_client.invoke_endpoint(
        EndpointName=endpoint_name,
        CustomAttributes=json.dumps(custom_attributes),
        ContentType='text/csv',
        Accept='application/json',
        Body=payload
    )


    #print(response)
    res_body = response['Body']
    #print(res_body)
    res_json = json.load(res_body)

    for i, rows in enumerate(res_json['results']):
        print(i+1)
        for row in rows:
            print('word:', row['word'])
            print('similarity:', row['similarity'])


if __name__ == '__main__':
    main()
