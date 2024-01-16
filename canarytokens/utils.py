import subprocess
from pathlib import Path
from typing import Any, Literal, Union
from twisted.web.http import Request


def check_and_add_cors_headers(request: Request):
    """
    According to https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request, we
    should check for `Access-Control-Request-Method` and `Origin` and optionally,
    `Access-Control-Request-Headers` headers in an OPTIONS request to determine its a preflight request; and
    respond with `Access-Control-Allow-Origin` and `Access-Control-Allow-Methods`. Else, we
    will add `Access-Control-Allow-Origin: *` to the GET request.
    """
    if request.method.upper() == b"GET":
        request.setHeader("Access-Control-Allow-Origin", "*")
    elif request.method.upper() == b"OPTIONS":
        if (
            request.getHeader("Access-Control-Request-Method") is None
            or request.getHeader("Origin") is None
        ):
            return

        acr_headers = request.getHeader("Access-Control-Request-Headers")
        if acr_headers is not None:
            request.setHeader("Access-Control-Allow-Headers", acr_headers)

        request.setHeader("Access-Control-Allow-Origin", request.getHeader("Origin"))
        request.setHeader("Access-Control-Allow-Methods", "OPTIONS, GET, POST")


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
