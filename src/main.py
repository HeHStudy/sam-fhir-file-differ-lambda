import sys
import boto3
import json
import os

s3_client  = boto3.client('s3')
BUCKET     = os.environ['BUCKET']
LAMBDA_ARN = os.environ['COPY_FILE_LAMBDA_ARN']

def lambda_handler(event, context):

    print(event)
    print(BUCKET)
    file1         = event['file1']
    file2         = event['file2']
    version       = event['version']
    requestId     = event['requestId']
    json1   = json.loads(s3_read(file1))
    json2   = json.loads(s3_read(file2))

    if json1['entry'] != json2['entry']:
        print("NEW FILE FOUND, COPYING DATA TO LAYER2")
        lambda_client = boto3.client('lambda')
        payload       = {
          's3_key': file1,
          'version': version,
          'requestId': requestId
        }
        #response = lambda_client.invoke(
        #    FunctionName=LAMBDA_ARN,
        #    InvocationType="RequestResponse",
        #    Payload=json.dumps(payload)
        #)
    else:
        print("> Same file")


def s3_read(file):
    fileobj = s3_client.get_object(
        Bucket=BUCKET,
        Key=file
    )
    filedata = fileobj['Body'].read()
    contents = filedata.decode('utf-8')

    return contents

