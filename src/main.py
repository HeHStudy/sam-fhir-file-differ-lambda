import sys
import boto3
import json
import os
from deepdiff import DeepDiff

s3_client  = boto3.client('s3')
BUCKET     = os.environ['BUCKET']
LAMBDA_ARN = os.environ['COPY_FILE_LAMBDA_ARN']

def lambda_handler(event, context):

    #print(event)
    file1         = event['file1']
    file2         = event['file2']
    version       = event['version']
    requestId     = event['requestId']
    json1   = json.loads(s3_read(file1))
    json2   = json.loads(s3_read(file2))
    entry1  = json1.get('entry', [])
    entry2  = json2.get('entry', [])

    #print(f'initial file1 entries size: {len(entry1)}')
    #print(f'initial file2 entries size: {len(entry2)}')

    # First we check the obvious difference and then use deepdiff
    if len(entry1) != len(entry2) or diffyng(entry1, entry2):
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

# This can exclude elements from the path
# see: https://zepworks.com/deepdiff/current/ignore_types_or_values.html#exclude-obj-callback
def exclude_fullUrl(obj, path):
    return True if "fullUrl" in path else False

def exclude_operation_outcomes_from_entry(entries):
    for entry in entries:
        if entry['resource']['resourceType'] == 'OperationOutcome':
            entries.remove(entry)
    return entries

def diffyng(entry1, entry2):
    n_entry1 = exclude_operation_outcomes_from_entry(entry1)
    n_entry2 = exclude_operation_outcomes_from_entry(entry2)
    #print(f'relevant file1 entries size: {len(entry1)}')
    #print(f'relevant file2 entries size: {len(entry2)}')

    print('Diffyng...')
    d = DeepDiff(n_entry1, n_entry2, ignore_order=True)
    print(d)
    return d

def s3_read(file):
    fileobj = s3_client.get_object(
        Bucket=BUCKET,
        Key=file
    )
    filedata = fileobj['Body'].read()
    contents = filedata.decode('utf-8')

    return contents

