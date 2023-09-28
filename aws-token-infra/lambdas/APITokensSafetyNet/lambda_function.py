import json
import boto3
import csv
import os
import time
import urllib
import urllib.error

from datetime import datetime, timezone, timedelta
from io import StringIO
from urllib import request, parse

DB_TABLE_NAME = "awsidtoken_table"
TICKET_URL = os.environ.get('TICKET_URL')
TICKET_TEAM = os.environ.get('TICKET_TEAM')

iam = boto3.client('iam')
db = boto3.client('dynamodb')

class NoItem(Exception):
    pass

def file_ticket(subject=None, team=TICKET_TEAM, priority=3, text=None):
    data = {}
    data['subject'] = subject
    data['team'] = team
    data['priority'] = str(priority)
    data['text'] = text
    data['dedupe_key'] = f"key_credsreportchecker_canarytokensorg_{aws_account_id}"
    req =  request.Request(TICKET_URL, data=json.dumps(data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    resp = request.urlopen(req)

def ticket_exception(exception):
    file_ticket(subject="AWSIDCredentialReportChecker Exception", text=f"An exception occurred whilst running the AWSIDCredentialReportChecker lambda function. The affected aws subaccount was {aws_account_id}. The exception was {repr(exception)}")

aws_account_id = None
def lambda_handler(event, context):
    global aws_account_id
    aws_account_id = context.invoked_function_arn.split(":")[4]
    try:
        try:
            check_credential_report()
        except ReportNotGeneratedInTime as e:
            ticket_exception(e)
    except Exception as e:
        ticket_exception(e)

def check_credential_report():
    response = iam.generate_credential_report()

    # it takes a little bit of time for the report to be generated.
    # if it isn't ready this call throws an exception. retry until
    # the report is ready
    for i in range(29):
        try:
            response = iam.get_credential_report()
            break
        except iam.exceptions.CredentialReportNotReadyException:
            print("Report not ready. Retrying...")
            time.sleep(30)
    else:
        raise ReportNotGeneratedInTime("Could not generate credentials report")

    f = StringIO(response['Content'].decode("utf-8"))
    reader = csv.DictReader(f, delimiter=',')
    current_ts = datetime.utcnow().strftime("%s")
    for row in reader:
        try:
            user = row['user']
            last_used_timestamp = iso8601_to_datetime(row['access_key_1_last_used_date'])
            # print('csvrow={}'.format(row))

            try:
                server, access_key, token, last_alerted_timestamp = get_token_info(user)
            except NoItem:
                # No record of this key. Every key must have an entry created in the DynamoDB when the key is generated
                print('No record for key')
                continue

            if last_used_timestamp > last_alerted_timestamp:
                print('Safety net triggered for {}'.format(token))
                try:
                    url = "http://{}/{}".format(server, token)
                    data = {
                        "safety_net": True,
                        "last_used": row['access_key_1_last_used_date'],
                        "last_used_service": row['access_key_1_last_used_service']
                    }
                    data = urllib.parse.urlencode(data).encode("utf8")
                    print('Looking up {u} to trigger alert!'.format(u=url))
                    req = urllib.request.Request(url, data)
                    response = urllib.request.urlopen(req)
                    msg = f"The token is {token}. Please investigate what API was called that it was only detected by the safety net."
                    file_ticket(subject="Canarytokens.org AWS Safety Net Caught Something", text=msg)
                except urllib.error.URLError as e:
                    print('Failed to trigger token: {e}'.format(e=e))
                    ticket_exception(e)

                db_response = db.put_item(
                    TableName=DB_TABLE_NAME,
                    Item={
                        'Username': {'S': user},
                        'Domain': {'S': server},
                        'AccessKey': {'S': access_key},
                        'Canarytoken': {'S': token},
                        'LastUsed': {'N': current_ts}
                    }
                )
                # print('DynamoDB response: {r}'.format(r=db_response))
        except ValueError as e:
            print('ValueError: {}'.format(e))
            continue

    return {
        'statusCode': 200,
        'body': json.dumps('Done')
    }


def iso8601_to_datetime(date):
    if date == "N/A":
        date = "1970-01-01T00:00:00+00:00"
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)


def get_token_info(user):
    # print(user)
    row = db.get_item(TableName=DB_TABLE_NAME, Key={'Username':{'S': user}})
    if 'Item' not in row:
        raise NoItem

    # print('row={}'.format(row))
    db_item = row['Item']
    # print('item={}'.format(db_item))
    return db_item['Domain']['S'], db_item['AccessKey']['S'], db_item['Canarytoken']['S'], datetime.utcfromtimestamp(int(db_item['LastUsed']['N']))

class ReportNotGeneratedInTime(Exception):
    pass
