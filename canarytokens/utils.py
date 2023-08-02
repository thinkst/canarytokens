import subprocess
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Literal, Tuple, Union

from canarytokens.models import TokenTypes


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


def retry_on_returned_error(
    retry_if: Callable,
    retry_intervals: Tuple[float] = (3.0, 3.0, 5.0, 5.0),
) -> Callable:
    """Decorator to add retries to functions that depend on external systems.


    Args:
        retry_if (Callable):
        retry_intervals (Tuple[int]): Tuple of seconds to wait before retrying. Defaults (3.0, 3.0, 5.0, 5.0)
    Returns:
        Callable: Returns the wrapped function.
    """

    def inner(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):  # type: ignore
            for interval in retry_intervals:
                res = f(*args, **kwargs)
                if retry_if(*res):
                    # Blocking sleep!
                    time.sleep(interval)
                    continue
                else:
                    return res
            return res

        return wrapper

    return inner


def token_type_as_readable(token_type: TokenTypes) -> tuple[str, str]:
    return {
        TokenTypes.WEB: ("A", "web bug"),
        TokenTypes.DNS: ("A", "DNS"),
        TokenTypes.WEB_IMAGE: ("A", "custom image"),
        TokenTypes.MS_WORD: ("An", "MS Word"),
        TokenTypes.MS_EXCEL: ("An", "MS Excel"),
        TokenTypes.ADOBE_PDF: ("An", "Adobe PDF"),
        TokenTypes.WIREGUARD: ("A", "WireGuard"),
        TokenTypes.WINDOWS_DIR: ("A", "Windows folder"),
        TokenTypes.CLONEDSITE: ("A", "cloned website"),
        TokenTypes.QR_CODE: ("A", "QR code"),
        TokenTypes.SVN: ("An", "SVN"),
        TokenTypes.SMTP: ("A", "email address"),
        TokenTypes.SQL_SERVER: ("An", "MS SQL Server"),
        TokenTypes.MY_SQL: ("A", "MySQL"),
        TokenTypes.AWS_KEYS: ("An", "AWS key"),
        TokenTypes.AZURE_ID: ("An", "Azure key"),
        TokenTypes.SIGNED_EXE: ("A", "custom exe/binary"),
        TokenTypes.FAST_REDIRECT: ("A", "fast redirect"),
        TokenTypes.SLOW_REDIRECT: ("A", "slow redirect"),
        TokenTypes.KUBECONFIG: ("A", "Kubeconfig"),
        TokenTypes.LOG4SHELL: ("A", "Log4Shell"),
        TokenTypes.CMD: ("A", "sensitive command"),
        TokenTypes.CC: ("A", "credit card"),
        TokenTypes.SLACK_API: ("A", "Slack API"),
    }[token_type]
