from dataclasses import dataclass
from datetime import datetime, timezone
import random
import shutil
import string
import secrets
import json
from typing import Union
import boto3
from botocore.exceptions import ClientError
import os

from canarytokens import queries
from canarytokens.canarydrop import Canarydrop
from canarytokens.models import AWSInfraAssetType, AWSInfraOperationType
from canarytokens.settings import FrontendSettings
from canarytokens.tokens import Canarytoken

settings = FrontendSettings()

MANAGEMENT_REQUEST_URL = settings.AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL
INVENTORY_ROLE_NAME = settings.AWS_INFRA_INVENTORY_ROLE
ROLE_SETUP_COMMANDS_TEMPLATE = """aws iam create-role --role-name $role_name --assume-role-policy-document \'{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"AWS": "arn:aws:sts::$aws_account:assumed-role/InventoryManagerRole/$external_id"}, "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"sts:ExternalId": "$external_id"}}}]}\'

aws iam create-policy --policy-name Canarytokens-Inventory-ReadOnly-Policy --policy-document \'{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Action": ["sqs:ListQueues","sqs:GetQueueAttributes"],"Resource": "*"},{"Effect": "Allow","Action": ["s3:ListAllMyBuckets"],"Resource": "*"}]}\'

aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::$customer_aws_account:policy/Canarytokens-Inventory-ReadOnly-Policy"""
ROLE_REMOVAL_COMMANDS_TEMPLATE = """aws iam detach-role-policy --role-name $role_name --policy-arn arn:aws:iam::$customer_aws_account:policy/Canarytokens-Inventory-ReadOnly-Policy

aws iam delete-policy --policy-arn arn:aws:iam::$customer_aws_account:policy/Canarytokens-Inventory-ReadOnly-Policy

aws iam delete-role --role-name  $role_name"""


@dataclass
class Handle:
    response_received: bool
    response: Union[bool, str, dict]


def _get_session():
    os.environ["AWS_CONFIG_FILE"] = "/dev/null"
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/dev/null"
    return boto3.Session()


def _get_sqs_client():

    if settings.DOMAINS[0] == "127.0.0.1":
        return _get_session().client(
            "sqs",
            region_name="eu-west-1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )
    return _get_session().client(
        "sqs",
        region_name="eu-west-1",
    )


def _get_s3_client():
    if settings.DOMAINS[0] == "127.0.0.1":
        return _get_session().resource(
            "s3",
            region_name="eu-west-1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )
    return _get_session().resource(
        "s3",
        region_name="eu-west-1",
    )


def get_shared_secret():

    # secret_name = "com.thinkst.awsic.canarytokensorg_auth"
    region_name = "eu-west-1"

    if settings.DOMAINS[0] == "127.0.0.1":
        client = _get_session().client(
            "secretsmanager",
            region_name="eu-west-1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )
    else:
        client = _get_session().client(
            service_name="secretsmanager", region_name=region_name
        )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId="arn:aws:secretsmanager:eu-west-1:194722410205:secret:com.thinkst.awsic.canarytokensorg_auth"
        )
    except ClientError as e:
        raise e

    shared_secret = get_secret_value_response["SecretString"]

    return json.loads(shared_secret).get("auth_key")


def generate_external_id():
    return "".join(
        [secrets.choice(string.ascii_letters + string.digits) for _ in range(21)]
    )


def _generate_handle_id():
    return secrets.token_hex(20)


def get_current_ingestion_bus():
    ssm = _get_session().client("ssm", regio_name="eu-west-1")
    bus_arn = settings.AWS_INFRA_INGESTION_BUS
    try:
        bus_name = ssm.get_parameter(Name=bus_arn).get("Parameter", {}).get("Value")
        if bus_name is None:
            raise RuntimeError(
                f"Could not get the current ingestion bus name stored in: {bus_arn}"
            )
        return bus_name
    except ClientError as e:
        raise e


def get_role_commands(canarydrop: Canarydrop):
    """
    Return the aws-cli commands needed to setup the inventory role in the customer's account
    """
    return {
        "role_name": settings.AWS_INFRA_INVENTORY_ROLE,
        "aws_account": settings.AWS_INFRA_AWS_ACCOUNT,
        "external_id": canarydrop.aws_customer_iam_access_external_id,
        "customer_aws_account": canarydrop.aws_account_id,
    }


def get_role_cleanup_commands(canarydrop: Canarydrop):
    """
    Return the aws-cli commands needed to detach and delete the inventory policy and role in the customer's account
    """
    return {
        "role_name": settings.AWS_INFRA_INVENTORY_ROLE,
        "customer_aws_account": canarydrop.aws_account_id,
    }


def create_handle(operation: AWSInfraOperationType, canarydrop: Canarydrop):
    "Create a new handle entry in the redis DB and trigger the specified operation"
    handle_id = _generate_handle_id()
    queries.add_aws_management_lambda_handle(
        handle_id, canarydrop.canarytoken.value(), operation
    )
    trigger_operation(operation, handle_id, canarydrop)
    return handle_id


def trigger_operation(operation: AWSInfraOperationType, handle, canarydrop: Canarydrop):
    payload = {
        "handle": handle,
        "operation": operation.value,
    }

    if operation == AWSInfraOperationType.CHECK_ROLE:
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": INVENTORY_ROLE_NAME,
        }
    elif operation == AWSInfraOperationType.INVENTORY:
        payload["params"] = {
            "aws_account": canarydrop.aws_account_id,
            "customer_iam_access_external_id": canarydrop.aws_customer_iam_access_external_id,
            "role_name": INVENTORY_ROLE_NAME,
            "region": canarydrop.aws_region,
            "assets_types": [asset_type.value for asset_type in AWSInfraAssetType],
        }

    elif operation == AWSInfraOperationType.SETUP_INGESTION:
        payload["params"] = {
            "canarytoken_id": canarydrop.canarytoken.value(),
            "bus_name": canarydrop.aws_infra_ingestion_bus_name,
            "region": canarydrop.aws_region,
            "aws_account": canarydrop.aws_account_id,
            "callback_domain": settings.DOMAINS[0],
        }

    elif operation == AWSInfraOperationType.TEARDOWN:
        payload["params"] = {
            "canarytoken_id": canarydrop.canarytoken.value(),
            "bus_name": canarydrop.aws_infra_ingestion_bus_name,
            "region": canarydrop.aws_region,
            "aws_account": canarydrop.aws_account_id,
        }
    _get_sqs_client().send_message(
        QueueUrl=MANAGEMENT_REQUEST_URL, MessageBody=json.dumps(payload)
    )


# TODO: add handle exist for token validation
def get_handle_response(handle_id):
    """
    Check if a response has been added to the specified handle in the redis DB and return it.
    """
    handle = queries.get_aws_management_lambda_handle(handle_id)
    if not handle:
        raise Exception("Handle does not exist")
    if handle.get("response_received") == "True":
        response = json.loads(handle.get("response_content"))
        return Handle(response_received=True, response=response)
    requested_time = datetime.strptime(
        handle.get("requested_timestamp"), "%Y-%m-%d %H:%M:%S"
    ).timestamp()
    current_time = datetime.now(timezone.utc).timestamp()
    if requested_time - current_time > 300:
        return Handle(response_received=True, response="")
    return Handle(response_received=False, response="")


def get_handle_operation(handle_id):
    """
    Return the operation type associated with a specific handle
    """
    handle = queries.get_aws_management_lambda_handle(handle_id)
    if handle is None:
        return None
    return handle.get("operation")


def add_handle_response(handle_id, response):
    """
    Update the specified handle with a response in the redis DB.
    """
    queries.update_aws_management_lambda_handle(handle_id, json.dumps(response))


def save_plan(canarydrop: Canarydrop, plan: str):
    """
    Save an AWS Infra plan and upload it to the tf modules S3 bucket.
    """
    # TODO: validate plan
    canarydrop.aws_saved_plan = json.dumps(plan)
    # TODO: add other asset types
    canarydrop.aws_deployed_assets = json.dumps(
        {
            AWSInfraAssetType.S3_BUCKET.value: [
                bucket["bucket_name"]
                for bucket in plan["assets"][AWSInfraAssetType.S3_BUCKET.value]
            ]
        }
    )
    queries.save_canarydrop(canarydrop)
    variables = generate_tf_variables(canarydrop, plan)
    _upload_zip(
        canarydrop.canarytoken.value(), canarydrop.aws_tf_module_prefix, variables
    )


def generate_tf_variables(canarydrop: Canarydrop, plan):
    """
    Generate variables to be used in the terraform template.
    """
    tf_variables = {
        "s3_bucket_names": [],
        "s3_objects": [],
        "canarytoken_id": canarydrop.canarytoken.value(),
        "cloudtrail_bus_name": canarydrop.aws_infra_ingestion_bus_name,
        # "cloudtrail_destination_bucket": settings.AWS_INFRA_CLOUDTRAIL_BUCKET,
    }
    for bucket in plan["assets"]["S3Bucket"]:
        tf_variables["s3_bucket_names"].append(bucket["bucket_name"])
        for s3_object in bucket["objects"]:
            tf_variables["s3_objects"].append(
                {
                    "bucket": bucket["bucket_name"],
                    "key": s3_object["object_path"],
                    "content": "".join(
                        [
                            random.choice(string.ascii_letters + string.digits)
                            for _ in range(random.randint(5, 1000))
                        ]
                    ),
                }
            )
    return tf_variables


def _upload_zip(canarytoken_id, prefix, variables):
    """
    Upload a new terraform module to the terraform module bucket.
    """
    print("*****")
    print(variables)
    new_dir = shutil.copytree(
        "../aws_infra_token_tf",
        f"/tmp/canarytoken_infra{canarytoken_id}",
        dirs_exist_ok=True,
    )
    with open(f"{new_dir}/decoy_vars.json", "w") as f:
        f.write(json.dumps(variables))

    archive = f"{new_dir}/module_tf_{canarytoken_id}.zip"
    if os.path.exists(archive):
        os.remove(archive)
    archive = shutil.make_archive(f"module_tf_{canarytoken_id}", "zip", new_dir)
    s3 = _get_s3_client()
    s3.Bucket(settings.AWS_INFRA_TF_MODULE_BUCKET).upload_file(
        archive, f"{prefix}/{canarytoken_id}/tf.zip"
    )
    shutil.rmtree(new_dir)
    os.remove(archive)


NAME_ENVS = ["prod", "staging", "dev", "testing"]
NAME_TARGETS = ["customer", "user", "admin", "audit"]
MAX_S3_OBJECTS = 100
MAX_S3_BUCKETS = 10


def generate_s3_bucket():
    """
    Return a name for a S3 bucket.
    """
    # TODO: make it smarter
    separator = random.choice(["", "-"])
    suffix = "".join(
        [random.choice(string.ascii_lowercase + string.digits) for _ in range(10)]
    )
    return f"{separator.join([random.choice(s) for s in [NAME_ENVS, NAME_TARGETS]])}{separator}bucket{separator}{suffix}"


def generate_s3_object():
    """
    Return a path for a S3 object.
    """
    # TODO: make it smarter
    objects = ["object", "data", "text", "passwords"]
    directory = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
    )
    return f"{random.randint(2000, 2025)}/{directory}/{random.choice(objects)}"


def generate_proposed_plan(canarydrop: Canarydrop):
    """
    Return a proposed plan for decoy assets containing new and current assets.
    """

    aws_deployed_assets = json.loads(canarydrop.aws_deployed_assets or "{}")
    aws_saved_plan = json.loads(canarydrop.aws_saved_plan or "{}")
    plan = {
        "assets": {
            AWSInfraAssetType.S3_BUCKET.value: []
            # TODO: add other asset types
        }
    }

    # generate new assets
    for i in range(
        random.randint(
            1,
            MAX_S3_BUCKETS
            - len(aws_deployed_assets.get(AWSInfraAssetType.S3_BUCKET.value, [])),
        )
    ):
        plan["assets"][AWSInfraAssetType.S3_BUCKET.value].append(
            {"bucket_name": generate_s3_bucket(), "objects": [], "off_inventory": False}
        )
        for _ in range(random.randint(1, MAX_S3_OBJECTS)):
            plan["assets"][AWSInfraAssetType.S3_BUCKET.value][i]["objects"].append(
                {"object_path": generate_s3_object()}
            )

    # add current assets
    for bucket_name in aws_deployed_assets.get(AWSInfraAssetType.S3_BUCKET.value, []):
        objects = list(
            filter(
                lambda bucket: bucket["bucket_name"] == bucket_name,
                aws_saved_plan.get("assets", {}).get(
                    AWSInfraAssetType.S3_BUCKET.value, []
                ),
            )
        )[0].get("objects", [])
        plan["assets"][AWSInfraAssetType.S3_BUCKET.value].append(
            {"bucket_name": bucket_name, "objects": objects, "off_inventory": False}
        )

    return plan


def save_current_assets(canarydrop: Canarydrop, assets: dict):
    canarydrop.aws_current_assets = json.dumps(assets)
    queries.save_canarydrop(canarydrop)


def get_canarydrop_from_handle(handle_id: str):
    return queries.get_canarydrop(
        Canarytoken(
            value=queries.get_aws_management_lambda_handle(handle_id).get("canarytoken")
        )
    )


def get_module_snippet(canarydrop: Canarydrop):
    """
    Return the snippet that can be pasted in the customer's terraform.
    """

    return f' module "canarytoken_infra" {{ source = "https://{settings.AWS_INFRA_TF_MODULE_BUCKET}.s3.eu-west-1.amazonaws.com/{canarydrop.aws_tf_module_prefix}/{canarydrop.canarytoken.value()}/tf.zip" }}'
