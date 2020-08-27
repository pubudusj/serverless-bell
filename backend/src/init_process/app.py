import os
import boto3
import json


stepfunctions = boto3.client('stepfunctions')
state_machine_arn = os.getenv('STATE_MACHINE_ARN')

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    response = stepfunctions.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({
            'bucket': bucket,
            'key': key
        })
    )