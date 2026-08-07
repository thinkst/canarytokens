import json
import subprocess
from pathlib import Path
from typing import Any, Literal, Union

import pycountry_convert
from pydantic import BaseModel
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
from canarytokens.constants import AUTO_ESCAPED_FILE_EXTENSIONS

autoescape_config = select_autoescape(
    enabled_extensions=AUTO_ESCAPED_FILE_EXTENSIONS,
    disabled_extensions=(),
    default_for_string=True,
    default=True
)

def get_autoescaped_env(template_dir: str) -> Environment:
    """ Returns a jinja2.Environment with auto escaping enabled on it.
        This environment uses the provided template_dir as its search path

    Args:
        template_dir (str): Path to use as a search path to the jinja2.Environment.

    Returns:
        Environment: A jinja2.Environment with auto escaping enabled on it.
    """
    return Environment(autoescape=autoescape_config, loader=FileSystemLoader(template_dir))


def get_autoescaped_template(template_source: str, trim_blocks: bool = False) -> Template:
    """ Returns a jinja2.Template with auto escaping enabled on it.
        This template uses the provided template_source as the source of its contents.

    Args:
        template_source (str)   : The contents of the jinja2.Template.
        trim_blocks     (bool)  : If this is set to True the first newline after a Jinja
                                  block is removed (block, not variable tag!)

    Returns:
        Template: A jinja2.Template with auto escaping enabled on it.
    """
    return Template(template_source, trim_blocks=trim_blocks, autoescape=autoescape_config)


def json_safe_dict(m: BaseModel, exclude: tuple = ()) -> dict[str, str]:
    return json.loads(m.json(exclude_none=True, exclude=set(exclude)))


def dict_to_csv(d: dict) -> str:
    """Convert dict to CSV"""
    return ", ".join(f"{k}: {v}" for k, v in d.items())


def prettify_snake_case(s: str):
    """Capitalize first letter and convert underscores to spaces"""
    s = s.replace("_", " ")
    s = s[0].upper() + s[1:]
    return s


def coerce_to_float(value: Any) -> Union[Literal[False], float]:
    """
    Tries to convert `value` to a float and returns
    the float or false.
    Args:
        value (Any): value to try coerce to float
    """
    try:
        return float(value)
    except ValueError:
        return False
    except TypeError:
        return False


def get_deployed_commit_sha(commit_sha_file: Path = Path("/COMMIT_SHA")):
    """"""
    if commit_sha_file.is_file():
        with open(commit_sha_file, mode="r") as fp:
            commit_sha = fp.read().strip()
    else:
        commit_sha = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )
    return commit_sha


def get_src_ip_continent(geo_data: dict) -> str:
    """Helper function that returns the continent of country given it's ISO 3166-2 code.

    Args:
        geo_data (dict): The "country" key contains an ISO 3166-2 code

    Returns:
        str: A two character code representing a continent
    """
    country = geo_data.get("country")
    if country is None:
        return "NO_CONTINENT"
    # AQ is the ISO 3166-2 code for Antarctica, and is returned from IPinfo,
    # but it's not included in pycountry_convert.
    if country == "AQ":
        return "AN"
    try:
        return pycountry_convert.country_alpha2_to_continent_code(country)
    except KeyError:
        return "NO_CONTINENT"


def strtobool(string: str) -> bool:
    """Convert a string to a boolean value.

    Args:
        s (str): The string to convert.

    Returns:
        bool: The boolean value of the string.
    """
    string = string.lower()
    if string in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif string in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"Not convertible to boolean: {string}")
