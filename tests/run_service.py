"""Launch application services with the local test receiver address allowed."""

import os
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    from canarytokens import advocate
    from tests.webhook_capture import allow_capture_delivery

    service = sys.argv[1]
    receiver = os.getenv("TEST_WEBHOOK_URL", "http://127.0.0.1:8088")
    advocate.post = allow_capture_delivery(advocate.post, receiver)
    os.chdir(ROOT / service)
    sys.path.insert(0, str(ROOT / service))
    if service == "frontend":
        sys.argv = ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8082"]
        runpy.run_module("uvicorn", run_name="__main__")
    elif service == "switchboard":
        from twisted.scripts.twistd import run

        sys.argv = ["twistd", "-noy", "switchboard.tac", "--pidfile=switchboard.pid"]
        run()
    else:
        raise ValueError(f"Unknown service: {service}")
