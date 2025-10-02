import json
import logging
import os
import shutil
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

from canarytokens.aws_infra.terraform_generation import generate_tf_variables
from canarytokens.aws_infra.utils import AWS_INFRA_ENABLED
from canarytokens.canarydrop import Canarydrop
from canarytokens.settings import FrontendSettings

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
AWS_INFRA_SHARED_SECRET = None
settings = FrontendSettings()
MANAGEMENT_REQUEST_URL = settings.AWS_INFRA_MANAGEMENT_REQUEST_SQS_URL
log = logging.getLogger()


def _get_session():
    os.environ["AWS_CONFIG_FILE"] = "/dev/null"
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/dev/null"
    return boto3.Session()


def _get_client(service: str, region_name: str = settings.AWS_INFRA_AWS_REGION):
    if settings.DOMAINS[0] == "127.0.0.1":
        return _get_session().client(
            service,
            region_name=region_name,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    return _get_session().client(
        service,
        region_name=region_name,
    )


def _get_resource(service: str, region_name: str = settings.AWS_INFRA_AWS_REGION):
    if settings.DOMAINS[0] == "127.0.0.1":
        return _get_session().resource(
            service,
            region_name=region_name,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    return _get_session().resource(
        service,
        region_name=region_name,
    )


if AWS_INFRA_ENABLED:
    S3_RESOURCE = _get_resource("s3")
    SQS_CLIENT = _get_client("sqs")
    SSM_CLIENT = _get_client("ssm")


def queue_management_request(payload: dict):
    """
    Send a message to the management request queue.
    """
    response = SQS_CLIENT.send_message(
        QueueUrl=MANAGEMENT_REQUEST_URL, MessageBody=json.dumps(payload)
    )
    return response


def get_shared_secret():
    global AWS_INFRA_SHARED_SECRET
    if AWS_INFRA_SHARED_SECRET is not None:
        return AWS_INFRA_SHARED_SECRET

    client = _get_client("secretsmanager")
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=settings.AWS_INFRA_SHARED_SECRET
        )
    except ClientError as e:
        raise e

    shared_secret = get_secret_value_response["SecretString"]
    AWS_INFRA_SHARED_SECRET = json.loads(shared_secret).get("auth_key")
    if AWS_INFRA_SHARED_SECRET is None:
        raise RuntimeError(
            "Shared secret is not setup correctly, expected key was not found."
        )

    return AWS_INFRA_SHARED_SECRET


def get_current_ingestion_bus():
    bus_ssm_parameter = settings.AWS_INFRA_INGESTION_BUS
    if bus_ssm_parameter is None:
        error_message = "AWS_INFRA_INGESTION_BUS is not set!"
        logging.error(error_message)
        raise RuntimeError(error_message)
    try:
        bus_name = (
            SSM_CLIENT.get_parameter(Name=bus_ssm_parameter)
            .get("Parameter", {})
            .get("Value")
        )
        if bus_name is None:
            error_message = f"Could not get the current ingestion bus name stored in: {bus_ssm_parameter}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        return bus_name
    except ClientError as e:
        logging.error(
            " ".join(e.args)
            if len(e.args) > 0
            else e.response["Error"]["Message"]
            or "ClientError occurred when fetching SSM parameter"
        )
        raise e


def upload_tf_module(canarydrop: Canarydrop, plan: dict):
    """
    Upload a new terraform module to the terraform module bucket.
    """
    variables = generate_tf_variables(canarydrop, plan)
    canarytoken_id = canarydrop.canarytoken.value()
    tf_template_dir = PROJECT_ROOT / "aws_infra_token_tf"
    new_dir = shutil.copytree(
        str(tf_template_dir),
        f"/tmp/canarytoken_infra{canarytoken_id}",
        dirs_exist_ok=True,
    )
    with open(f"{new_dir}/decoy_vars.json", "w") as f:
        f.write(json.dumps(variables))

    archive = f"{new_dir}/module_tf_{canarytoken_id}.zip"
    if os.path.exists(archive):
        os.remove(archive)
    archive = shutil.make_archive(f"module_tf_{canarytoken_id}", "zip", new_dir)

    S3_RESOURCE.Bucket(settings.AWS_INFRA_TF_MODULE_BUCKET).upload_file(
        archive, f"{canarydrop.aws_tf_module_prefix}/{canarytoken_id}/tf.zip"
    )
    shutil.rmtree(new_dir)
    os.remove(archive)
