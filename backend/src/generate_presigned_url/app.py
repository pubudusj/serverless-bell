import json
import boto3
from uuid import uuid4
import os
from botocore.exceptions import ClientError
from botocore.client import Config

s3 = boto3.client('s3', config=Config(
    signature_version='s3v4',
    s3={'addressing_style': 'virtual'}
    ))


def index(event, context):
    body = json.loads(event['body'])

    if 'username' not in body:
        return {
            "statusCode": 500,
            "body": {
                'message': 'Username not found.'
            }
        }
    extension = body['name'].split('.')[-1]
    key = str(uuid4()) + '.' + extension
    bucket = os.getenv('S3BUCKET')

    try:
        url = s3.generate_presigned_url('put_object',
                                        Params={'Bucket': bucket, 'Key': 'uploads/' + key, 'ContentType': 'multipart/form-data', 'Metadata': {'user': body['username']}},
                                        ExpiresIn=os.getenv('EXPIRY_TIME'),
                                        HttpMethod='PUT',
                                        )

        response = {
            "statusCode": 200,
            "body": json.dumps({'url': url, 'key': key}),
            "headers": {
                'Content-Type': 'application/json', 
                'Access-Control-Allow-Origin': '*'
            }
        }
    except ClientError as e:
        print(e)
        response = {
            "statusCode": 500,
            "body": {
                'message': 'Error generating the url'
            }
        }

    return response
