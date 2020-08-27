import boto3
import os
from uuid import uuid4
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from datetime import datetime

s3 = boto3.client('s3')


def add_watermark(bucket, key):
    image_byte_string = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
    image = Image.open(BytesIO(image_byte_string)).convert("RGBA")

    txt = Image.new('RGBA', image.size, (255,255,255,0))
    font = ImageFont.truetype('resources/arial.ttf', 12)
    d = ImageDraw.Draw(txt)
    d.text(xy=(image.size[0]-350, image.size[1]-20), text="Produced by Serverless Bell @ " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S") + ' UTC', font=font, fill=(255, 255, 0, 255))
    image = Image.alpha_composite(image, txt)

    logo = Image.open('resources/logo.png').convert("RGBA")
    image.paste(logo, (10, 10), mask=logo)

    byte_array = BytesIO()
    image.save(byte_array, format='PNG')

    # Save to bucket/location
    print(str(uuid4()))
    new_path = 'preview/' + str(uuid4()) + '.png'
    s3.put_object(Bucket=bucket, Key=new_path, Body=byte_array.getvalue(), ACL='public-read')

    return new_path;

def handler(event, context):
    bucket = event['bucket']
    key = event['key']

    new_path = add_watermark(bucket, key)

    return {
        'image': {
            'bucket': bucket,
            'key': new_path
        }
    }
