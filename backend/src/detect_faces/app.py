import os
import boto3
import json
import io
from PIL import Image
from io import BytesIO


s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
index_collection_id = os.getenv('REKOGNITION_COLLECTION')


def detect_faces(bucket, key):
    detect_faces = rekognition.detect_faces(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
    )

    matched_faces = []
    if detect_faces['FaceDetails']:
        image = read_image_from_s3(bucket, key)

        # Crop each face from image
        for face in detect_faces['FaceDetails']:
            cropped_image = crop_face_from_image(face['BoundingBox'], image)

            # Search cropped images in Recognition collection
            response = rekognition.search_faces_by_image(
                CollectionId=index_collection_id,
                Image={'Bytes': cropped_image}
            )

            for face in response['FaceMatches']:
                matched_faces.append(face['Face']['ExternalImageId'].replace('_', ' '))

            return {
                'matched_faces': list(set(matched_faces)),
                'total_faces_detected': len(detect_faces['FaceDetails'])
            }
    else:
        return {
            'matched_faces': [],
            'total_faces_detected': 0
        }

def crop_face_from_image(box, image):
    image_width = image.size[0]
    image_height = image.size[1]

    x1 = int(box['Left'] * image_width) * 0.9
    y1 = int(box['Top'] * image_height) * 0.9
    x2 = int(box['Left'] * image_width + box['Width'] * image_width) * 1.10
    y2 = int(box['Top'] * image_height + box['Height'] * image_height) * 1.10
    image_crop = image.crop((x1, y1, x2, y2))

    stream = io.BytesIO()
    image_crop.save(stream, format="JPEG")

    return stream.getvalue()


def read_image_from_s3(bucket, key):
    image_byte_string = s3.get_object(Bucket=bucket, Key=key)['Body'].read()

    return Image.open(BytesIO(image_byte_string))


def handler(event, context):
    bucket = event['bucket']
    image = event['key']

    return detect_faces(bucket, image)
