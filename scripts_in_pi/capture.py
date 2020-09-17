#!/usr/bin/python3

import time
from gpiozero import Button
from picamera import PiCamera
import datetime
import os
from signal import pause
import boto3

camera = PiCamera()
camera.resolution = (800, 600)
bucket = 'bucket-name'
client = boto3.resource('s3')


def capture():
    try:
        timestamp = str(int(time.time()))
        fileName = timestamp + '.jpg'
        camera.capture('./' + fileName)
        client.meta.client.upload_file('./' + fileName, bucket, fileName)
        print('uploaded - ' + fileName)
        os.remove('./' + fileName)
    except:
        print("Oops! an error occured.")


button = Button(2)
button.when_pressed = capture

pause()
