from datetime import datetime
import random
from math import floor
from io import StringIO
from csv import DictWriter

from canarytokens.models import Hostname
from canarytokens.windows_fake_fs_templates.powershell_template import (
    POWERSHELL_TEMPLATE,
)
from canarytokens.windows_fake_fs_templates.folder_personal_finances import (
    PERSONAL_FINANCES_STRUCTURE,
)
from canarytokens.windows_fake_fs_templates.folder_home_network import (
    HOME_NETWORK_STRUCTURE,
)
from canarytokens.windows_fake_fs_templates.folder_personal_correspondence import (
    PERSONAL_CORRESPONDENCE_STRUCTURE,
)
from canarytokens.windows_fake_fs_templates.folder_photo_archive import (
    PHOTO_ARCHIVE_STRUCTURE,
)
from canarytokens.windows_fake_fs_templates.folder_defense import (
    DEFENSE_STRUCTURE,
)
from canarytokens.windows_fake_fs_templates.folder_med_tech import MED_TECH_STRUCTURE
from canarytokens.windows_fake_fs_templates.folder_network_admin import (
    NETWORK_ADMIN_STRUCTURE,
)
from canarytokens.windows_fake_fs_templates.folder_security_admin import (
    SECURITY_ADMIN_STRUCTURE,
)


FOLDER_MAP = {
    "personal_finances": PERSONAL_FINANCES_STRUCTURE,
    "home_network": HOME_NETWORK_STRUCTURE,
    "personal_correspondence": PERSONAL_CORRESPONDENCE_STRUCTURE,
    "photo_archive": PHOTO_ARCHIVE_STRUCTURE,
    "defense": DEFENSE_STRUCTURE,
    "med_tech": MED_TECH_STRUCTURE,
    "network_admin": NETWORK_ADMIN_STRUCTURE,
    "security_admin": SECURITY_ADMIN_STRUCTURE,
}


def _gen_ts() -> str:
    """
    Generates a random timestamp in the near past
    """
    now = floor(datetime.now().timestamp())
    random_hours = random.randint(1, 10000)
    return str(now - (random_hours * 60 * 60))


def _new_item(path: str, is_folder: bool, size: int = 0) -> dict:
    isdir = "false"
    if is_folder:
        isdir = "true"
    return {"path": path, "isdir": isdir, "size": size, "timestamp": _gen_ts()}


def _process_item(item: dict, path: str) -> str:
    out = []
    if item["type"] == "folder":
        out.append(_new_item(path=path + "\\" + item["name"], is_folder=True))
        for c in item["children"]:
            out += _process_item(c, path + "\\" + item["name"])
    else:
        out.append(
            _new_item(
                path=path + "\\" + item["name"],
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
        out += _process_item(item, "")

    out_csv = StringIO()
    writer = DictWriter(out_csv, fieldnames=fieldnames)
    writer.writerows(out)
    return out_csv.getvalue().strip()


def make_windows_fake_fs(
    token_hostname: Hostname, root_dir: str, fake_file_structure: list[dict]
) -> str:
    """Returns a Powershell script file which has the steps to deploy a
    Windows Folder Token embedded in it.
    The token is in a 'hostname' eg: {some}.{thing}.CMD.{token}.{canarytoken_hostname}

    Args:
        token_hostname (Hostname): {token}.{canarytoken_server_hostname} eg: 1234dsaa.canarytokens.com
        root_dir (str): Path (e.g., 'C:\\vfs') where the folder should be created.
        fake_file_structure list[dict]: The fake file structure to use when the token is deployed.

    Returns:
        str: A valid powershell file that is to be loaded on a windows machine.
    """
    fs_csv = _json_to_csv(fake_file_structure)

    # .format does not work because of certain characters in the template
    # that cause and escape issue so we use replace
    return (
        POWERSHELL_TEMPLATE.replace("{CSV_DATA}", fs_csv)
        .replace("{TOKEN_DOMAIN}", token_hostname)
        .replace("{ROOT_DIR}", root_dir)
    )
