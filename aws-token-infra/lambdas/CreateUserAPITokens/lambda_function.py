from __future__ import print_function

import boto3
import json, urllib.request, urllib.parse
import random, string
import datetime
import os


iam = boto3.client('iam')
db = boto3.client('dynamodb')

DB_TABLE_NAME = "awsidtoken_table"
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def send_slack(resp=None):
    if not resp:
        print('No resp found for slack alert')
    print(resp)
    if 'error' in resp:
        data = {"text": resp['error']}
    else:
        data = {"text": "Newly Created AWS ID Token. Details are:\n"+
                      "Username: {u}, \nAccessKeyId: {aid}"
                      .format(u=resp['data'],aid=resp['access_key_id'][:8])}
    data = json.dumps(data)
    bindata = data if type(data) == bytes else data.encode('utf-8')
    headers = {'Content-Type':'application/json', "Accept": "text/plain"}
    req = urllib.request.Request(SLACK_WEBHOOK_URL, bindata, headers)
    resp = urllib.request.urlopen(req)
    return resp


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.'''
    aws_account_id = context.invoked_function_arn.split(":")[4]
    print('.....starting function....')
    if 'queryStringParameters' in event and event['queryStringParameters']:
        if 'data' in event['queryStringParameters']:
            print(event['queryStringParameters']['data'])
            if len(event['queryStringParameters']['data'])==0:
                print('Data parameter given was empty in query string')
                return respond(ValueError('Data parameter given was empty in query string'))
            final_resp = {}
            data = event['queryStringParameters']['data']
            print('.... Received Encoded Data: {t}'.format(t=data))
            final_resp['data'] = data
            user_resp = iam.create_user(UserName=data)
            key_resp = iam.create_access_key(UserName=data)
            print(user_resp)
            print('...........................................')
            print(key_resp)
            if 'AccessKey' in key_resp and 'SecretAccessKey' in key_resp['AccessKey'] and \
                'AccessKeyId' in key_resp['AccessKey']:
                final_resp['secret_access_key'] = key_resp['AccessKey']['SecretAccessKey']
                final_resp['access_key_id'] = key_resp['AccessKey']['AccessKeyId']
                final_resp['aws_account_id'] = aws_account_id
                db_response = db.put_item(
                    TableName=DB_TABLE_NAME,
                    Item={
                            'Username': {'S': data},
                            'Domain': {'S': data.split('@@')[0]},
                            'AccessKey': {'S': final_resp['access_key_id']},
                            'Canarytoken': {'S': data.split('@@')[1]},
                            'LastUsed': {'N': str(datetime.datetime.utcnow().strftime("%s"))},
                            'AwsAccountId': {'S': str(aws_account_id)}
                    }
                )
                print('DynamoDB response: {r}'.format(r=db_response))
            else:
                final_resp['error'] = 'There was an issue creating an AWS ID Token. Please contact an admin.'
            send_slack(final_resp)
            return respond(None, final_resp)
        else:
            print('No data parameter was given in query string')
            return respond(ValueError('No data parameter was given in query string'))
    else:
        print('No query string found. Please use ?data=<encoded_data>.')
        return respond(ValueError('No query string found. Please use ?data=<encoded_data>.'))