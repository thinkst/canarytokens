import json
import boto3
import csv
import time
import urllib

from datetime import datetime, timezone, timedelta
from io import StringIO
from urllib import request, parse

ALERT_THRESHOLD = timedelta(hours=4, minutes=30)
DB_TABLE_NAME = "awsidtoken_table"

iam = boto3.client('iam')
db = boto3.client('dynamodb')

class NoItem(Exception):
    pass

def lambda_handler(event, context):
    # TODO Take account ID as input in event. Assume role inside account and perform the credential
    # report lookup

    response = iam.generate_credential_report()

    # it takes a little bit of time for the report to be generated.
    # if it isn't ready this call throws an exception. retry until
    # the report is ready
    for i in range(5):
        try:
            response = iam.get_credential_report()
            break
        except iam.exceptions.CredentialReportNotReadyException:
            print("Report not ready. Retrying...")
            time.sleep(60)
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

            # print("Token info retreived from DynamoDB: server={}, token={}, lastalerted={}".format(server, token, last_alerted_timestamp))
            if last_used_timestamp > last_alerted_timestamp:
                url = "http://{}/{}".format(server, token)
                data = {"safety_net": True, "last_used": row['access_key_1_last_used_date']}
                data = urllib.parse.urlencode(data).encode("utf8")

                req = urllib.request.Request(url, data)
                response = urllib.request.urlopen(req)
                print('Looking up {u} to trigger alert!'.format(u=url))
                print('Response Code: {r}'.format(r=response.getcode()))
                print('Response Info: {r}'.format(r=response.info()))


                db_response = db.put_item(
                    TableName=DB_TABLE_NAME,
                    Item={
                        'Username': {'S': user},
                        'Domain': {'S': server},
                        'AccessKey': {'S': access_key},
                        'Canarytoken': {'S': token},
                        'LastUsed': {'N': str(current_ts)}
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
