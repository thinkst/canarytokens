from typing import TYPE_CHECKING
import boto3
from botocore.config import Config
from exposed_key_checker import support_ticketer

if TYPE_CHECKING:
    from exposed_keys import ExposedKeyData

DB_TABLE_NAME = "ExposedKeyCheckerProcessed"
BOTO_CONFIG = Config(region_name="us-east-2")


class Database:
    def __init__(self):
        self._db = boto3.client("dynamodb", config=BOTO_CONFIG)

    def mark_key_as_processed(self, key_data: "ExposedKeyData"):
        try:
            self._db.put_item(TableName=DB_TABLE_NAME, Item=key_data.to_db_item())
        except Exception as e:
            text = f"The key checker could not save the following item as processed in DynamoDB: {key_data}. The exception was {e}."
            support_ticketer.create_ticket(
                "Exposed AWS Key Checker could not save processed state",
                text,
                "exposed-aws-key-checker-save-error",
            )

    def has_key_been_processed(self, key_data: "ExposedKeyData") -> bool:
        res = self._db.query(
            TableName=DB_TABLE_NAME,
            Select="COUNT",
            ExpressionAttributeValues={
                ":v1": {
                    "S": key_data.iam_user,
                },
            },
            KeyConditionExpression="IamUser = :v1",
        )
        return res.get("Count", 0) > 0
