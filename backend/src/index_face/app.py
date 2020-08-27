import os, boto3, json

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
index_collection_id = os.getenv('REKOGNITION_COLLECTION')

def index_faces(bucket, image, username):
    index_faces = rekognition.index_faces(
        CollectionId=index_collection_id,
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': image
            }
        },
        ExternalImageId=username,
        MaxFaces=1
    )

def fetch_user_name(bucket, key):
    try:
        image_data = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        return image_data['Metadata']['user'].replace(' ', '_')

    except:
        return None;

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    image = event['Records'][0]['s3']['object']['key']

    username = fetch_user_name(bucket, image)

    if username is not None:
        index_faces(bucket, image, username)
    else:
        print('username is not available')
    
