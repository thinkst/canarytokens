import os
import random
import json

from datetime import datetime
from math import floor
from io import StringIO
from csv import DictWriter

from canarytokens.models import Hostname

MODULE_PATH = os.path.dirname(__file__)

TOKEN_TEMPLATE = f"{MODULE_PATH}/token_template"
TOKEN_DEPLOY_TEMPLATE = f"{TOKEN_TEMPLATE}/Deployment.ps1"
TOKEN_SCHEDULED_TASK_TEMPLATE = f"{TOKEN_TEMPLATE}/ScheduledTask.ps1"
TOKEN_SCHEDULED_TASK_XML_TEMPLATE = f"{TOKEN_TEMPLATE}/ScheduledTask.xml"
TOKEN_PROVIDER = f"{TOKEN_TEMPLATE}/WindowsFakeFS.cs"

FOLDER_STRUCTURES = f"{MODULE_PATH}/folder_structures"
FOLDER_MAP = {
    "personal_finances": f"{FOLDER_STRUCTURES}/personal_finances.json",
    "home_network": f"{FOLDER_STRUCTURES}/home_network.json",
    "personal_correspondence": f"{FOLDER_STRUCTURES}/personal_correspondence.json",
    "photo_archive": f"{FOLDER_STRUCTURES}/photo_archive.json",
    "defense": f"{FOLDER_STRUCTURES}/defense.json",
    "med_tech": f"{FOLDER_STRUCTURES}/med_tech.json",
    "network_admin": f"{FOLDER_STRUCTURES}/network_admin.json",
    "security_admin": f"{FOLDER_STRUCTURES}/security_admin.json",
    "testing": f"{FOLDER_STRUCTURES}/defense.json",
}


def _gen_ts() -> str:
    """
    Generates a random timestamp in the near past
    """
    now = floor(datetime.now().timestamp())
    random_hours = random.randint(1, 10000)
    return str(now - (random_hours * 60 * 60))


def _new_item(path: str, is_folder: bool, size: int = 0) -> dict:
    isdir = "true" if is_folder else "false"
    return {"path": path, "isdir": isdir, "size": size, "timestamp": _gen_ts()}


def _process_item(item: dict, path: str) -> str:
    out = []
    if item["type"] == "folder":
        out.append(_new_item(path=f"{path}\\{item['name']}", is_folder=True))
        for c in item["children"]:
            out.extend(_process_item(c, f"{path}\\{item['name']}"))
    else:
        out.append(
            _new_item(
                path=f"{path}\\{item['name']}",
                is_folder=False,
                size=random.randint(1024, 51200),
            )
        )
    return out


def _json_to_csv(fake_file_structure: list[dict]) -> str:
    """
    Converts a JSON-based dict of a file system structure to the CSV format used by the ProjFS provider
    """

    fieldnames = ["path", "isdir", "size", "timestamp"]
    out = []
    for item in fake_file_structure:
        out.extend(_process_item(item, ""))

    out_csv = StringIO()
    writer = DictWriter(out_csv, fieldnames=fieldnames)
    writer.writerows(out)
    return out_csv.getvalue().strip()


def _read_file(file_path: str) -> str:
    """Read file and return contents"""
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()
        return data


def make_windows_fake_fs(
    token_hostname: Hostname, root_dir: str, fake_file_structure: str
) -> str:
    """Returns a Powershell script file which has the steps to deploy a
    Windows Folder Token embedded in it.
    The token is in a 'hostname' eg: {some}.{thing}.CMD.{token}.{canarytoken_hostname}

    Args:
        token_hostname (Hostname): {token}.{canarytoken_server_hostname} eg: 1234dsaa.canarytokens.com
        root_dir (str): Path (e.g., 'C:\\Secrets') where the folder should be created.
        fake_file_structure str: Name of the file structure to use.

    Returns:
        str: A valid powershell file that is to be loaded on a windows machine.
    """
    # import pdb; pdb.set_trace()
    folder_structure_json = json.loads(_read_file(FOLDER_MAP.get(fake_file_structure)))
    folder_structure_csv = _json_to_csv(folder_structure_json)

    deployment = _read_file(TOKEN_DEPLOY_TEMPLATE)
    scheduled_task = _read_file(TOKEN_SCHEDULED_TASK_TEMPLATE)
    scheduled_task_xml = _read_file(TOKEN_SCHEDULED_TASK_XML_TEMPLATE)
    token_provider = _read_file(TOKEN_PROVIDER)

    scheduled_task = scheduled_task.replace("REPLACE_TOKEN_DOMAIN", token_hostname)
    scheduled_task = scheduled_task.replace(
        "REPLACE_CSHARP_PROVIDER_CODE", token_provider
    )
    scheduled_task = scheduled_task.replace(
        "REPLACE_CSV_DIR_STRUCTURE", folder_structure_csv
    )

    # .format does not work because of certain characters in the template
    # that cause and escape issue so we use replace
    deployment = deployment.replace("REPLACE_ROOT_DIR", root_dir)
    deployment = deployment.replace("REPLACE_SCHEDULED_TASK_XML", scheduled_task_xml)
    deployment = deployment.replace("REPLACE_SCHEDULED_TASK", scheduled_task)

    return deployment
