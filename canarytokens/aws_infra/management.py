import json
import os
import shutil
import boto3
from botocore.exceptions import ClientError

from canarytokens.settings import FrontendSettings

AWS_INFRA_REGION = "eu-west-1"
AWS_INFRA_SHARED_SECRET = None
settings = FrontendSettings()


def _get_session():
    os.environ["AWS_CONFIG_FILE"] = "/dev/null"
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "/dev/null"
    return boto3.Session()


def _get_client(service: str, region_name: str = AWS_INFRA_REGION):
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


def _get_resource(service: str, region_name: str = AWS_INFRA_REGION):
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


S3_RESOURCE = _get_resource("s3")
SQS_CLIENT = _get_client("sqs")
SSM_CLIENT = _get_client("ssm")


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
    try:
        bus_name = (
            SSM_CLIENT.get_parameter(Name=bus_ssm_parameter)
            .get("Parameter", {})
            .get("Value")
        )
        if bus_name is None:
            raise RuntimeError(
                f"Could not get the current ingestion bus name stored in: {bus_ssm_parameter}"
            )
        return bus_name
    except ClientError as e:
        raise e


def upload_tf_module(canarytoken_id, prefix, variables):
    """
    Upload a new terraform module to the terraform module bucket.
    """
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

    S3_RESOURCE.Bucket(settings.AWS_INFRA_TF_MODULE_BUCKET).upload_file(
        archive, f"{prefix}/{canarytoken_id}/tf.zip"
    )
    shutil.rmtree(new_dir)
    os.remove(archive)
