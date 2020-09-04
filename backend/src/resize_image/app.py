import boto3
import os
from PIL import Image
from io import BytesIO

s3 = boto3.client('s3')
max_width = int(os.getenv('RESIZE_MAX_WIDTH'))

def resize_image(bucket, key, max_width):
    # Get image
    image_byte_string = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    image = Image.open(BytesIO(image_byte_string))

    image_width = image.size[0]
    image_height = image.size[1]

    file_path, file_name = os.path.split(key)
    new_path = 'resized/' + file_name

    if image_width <= max_width:
        # No resize required, just copy
        s3.copy_object(
            Bucket=bucket,
            CopySource='/' + bucket + '/' + key,
            Key=new_path,
        )
    else:
        # Caclculate resize height
        new_size = max_width, int(image_height*(max_width/image_width))

        # Resize
        image.thumbnail(new_size, Image.ANTIALIAS)
        byte_array = BytesIO()
        image.save(byte_array, format='JPEG')

        # Save to bucket/location
        s3.put_object(Bucket=bucket, Key=new_path, Body=byte_array.getvalue())

    return new_path


def handler(event, context):
    bucket = event['bucket']
    key = event['key']

    new_path = resize_image(bucket, key, max_width)

    return {
        'bucket': bucket,
        'key': new_path
    }