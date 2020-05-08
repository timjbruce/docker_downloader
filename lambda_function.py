import json
import boto3
import os
import requests
import sys

dynamodb = boto3.client('dynamodb', region_name='us-east-2')
filetable = os.getenv('FileTable', 'CallbackFiles')
s3 = boto3.client('s3', region_name='us-east-2')
def lambda_handler(event, context):

    URI = event['name']

    keyconditionexpression = 'URI = :val1'
    expressionattributevalues = {':val1':{"S":URI}}
    print(expressionattributevalues)
    files = dynamodb.query(TableName=filetable, Limit=100,
        KeyConditionExpression=keyconditionexpression,
        ExpressionAttributeValues=expressionattributevalues)
    print(files)
    for file in files['Items']:
        shortfile = file['FilenameURL']['S'][file['FilenameURL']['S'].rfind('/')+1:]
        fullfile = '/tmp/' + shortfile
        response = requests.get(file['FilenameURL']['S'])
        if response.status_code == 200:
            open(fullfile, 'wb').write(response.content)
            s3.put_object(Body=fullfile, Bucket='awstb-useast2-datacopy', Key=shortfile)
            #could delete file in dynamodb

    return {
        "statusCode": 200,
        "body": ""
    }
    
def container_start():
    #create an event and context that is like that passed in from Step Functions
    print('started container')
    print(sys.argv)
    event = {}
    context = {}
    event['name']=str(sys.argv[1])
    #call lambda_handler
    print(f'calling download function with {event}')
    response = lambda_handler(event, context)
    return response
