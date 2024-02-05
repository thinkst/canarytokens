import subprocess
from pathlib import Path
from typing import Any, Literal, Union


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


# def retry_on_returned_error(
#     retry_if: Callable,
#     retry_intervals: Tuple[float] = (3.0, 3.0, 5.0, 5.0),
# ) -> Callable:
#     """Decorator to add retries to functions that depend on external systems.


#     Args:
#         retry_if (Callable):
#         retry_intervals (Tuple[int]): Tuple of seconds to wait before retrying. Defaults (3.0, 3.0, 5.0, 5.0)
#     Returns:
#         Callable: Returns the wrapped function.
#     """

#     def inner(f: Callable) -> Callable:
#         @wraps(f)
#         def wrapper(*args, **kwargs):  # type: ignore
#             for interval in retry_intervals:
#                 res = f(*args, **kwargs)
#                 if retry_if(*res):
#                     # Blocking sleep!
#                     time.sleep(interval)
#                     continue
#                 else:
#                     return res
#             return res

#         return wrapper

#     return inner
