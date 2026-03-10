import os
import gzip
import json
import re
import time
import urllib.request, urllib.error, urllib.parse
import base64
import random
import datetime
from io import BytesIO

import boto3

DB_TABLE_NAME = "awsidtoken_table"

db = boto3.client("dynamodb")


def lambda_handler(event, context):
    """Process AWS Api key token use logs,
    coming from CLOUDWATCH LOGS
    """
    print("Starting the Process of AWSTokens Logs...")
    # event is a dict containing a base64 string gzipped
    print(event)
    event = json.loads(
        gzip.GzipFile(
            fileobj=BytesIO(base64.b64decode(event["awslogs"]["data"]))
        ).read()
    )
    log_events = event["logEvents"]

    current_ts = datetime.datetime.utcnow().strftime("%s")
    for log_event in log_events:
        print(log_event)
        if "userIdentity" in log_event["message"]:
            msg = json.loads(log_event["message"])
            id_record = msg["userIdentity"]
            agent = ""
            if "userAgent" in msg:
                agent = msg["userAgent"]

            ip = msg["sourceIPAddress"]

            encoded_info = id_record["userName"].split("@@")
            accessKeyId = id_record["accessKeyId"]
            server = encoded_info[0]
            token = encoded_info[1]

            url = "http://{}/{}".format(server, token)
            data = {"ip": ip, "user_agent": agent}
            if "eventName" in msg:
                data["eventName"] = msg["eventName"]

            data = urllib.parse.urlencode(data).encode("utf8")

            req = urllib.request.Request(url, data)
            response = urllib.request.urlopen(req)
            print("AWS Access-key was used from IP {p}".format(p=ip))
            print("Looking up {u} to trigger alert!".format(u=url))
            print("Response Code: {r}".format(r=response.getcode()))
            print("Response Info: {r}".format(r=response.info()))

            db_response = db.put_item(
                TableName=DB_TABLE_NAME,
                Item={
                    "Username": {"S": id_record["userName"]},
                    "Domain": {"S": server},
                    "AccessKey": {"S": accessKeyId},
                    "Canarytoken": {"S": token},
                    "LastUsed": {"N": str(current_ts)},
                },
            )
            print("DynamoDB response: {r}".format(r=db_response))
    return {"status": "ok"}


MAX_LENGTH = 253
