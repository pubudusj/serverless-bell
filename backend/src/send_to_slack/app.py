import requests
import json
import boto3
import os

region = os.getenv('REGION')
slack_url = os.getenv('SLACK_URL')

def arrange_url(bucket, key):
    return "https://%s.s3.%s.amazonaws.com/%s" % (bucket, region, key)

def arrange_message(data):
    message = ''
    total_faces = data['total_faces_detected']
    if total_faces > 0 :
        message += 'I can see ' + str(total_faces)
        message += ' people. ' if total_faces > 1 else ' person. '
        if len(data['matched_faces']) > 0:
            message += 'And I can recognize ' + ', '.join(data['matched_faces']) + '.'
    else:
        message = 'Sorry I cannot see any people.'
        
    return message


def handler(event, context):
    bucket = event[1]['image']['bucket']
    key = event[1]['image']['key']

    url = arrange_url(bucket, key)
    message = arrange_message(event[0])

    output = {
        "attachments": [
            {
                "color": "#f00",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                                    "text": "There's someone at the door! :bell::bell:"
                        }
                    },
                    {
                        "type": "image",
                        "image_url": url,
                        "alt_text": "Serverless Bell"
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "*" + message + "*"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    requests.post(
        url = slack_url,
        data = json.dumps(output),
        headers = {'Content-type': 'application/json'}
    )
