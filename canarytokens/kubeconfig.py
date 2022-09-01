import base64
import copy
import random
import textwrap
import uuid
from collections import OrderedDict
from typing import Tuple

import yaml
from twisted.logger import Logger

from canarytokens.channel_input_mtls import mTLS
from canarytokens.queries import get_certificate, get_kc_endpoint

UnauthorizedResponseBody = {
    "kind": "Status",
    "apiVersion": "v1",
    "metadata": {},
    "status": "Failure",
    "message": "Unauthorized",
    "reason": "Unauthorized",
    "code": 401,
}
BadRequestResponseBody = {
    "kind": "Status",
    "apiVersion": "v1",
    "metadata": {},
    "status": "Failure",
    "message": "Bad Request",
    "reason": "Bad Request",
    "code": 400,
}
ForbiddenResponseBody = {
    "kind": "Status",
    "apiVersion": "v1",
    "metadata": {},
    "status": "Failure",
    "message": 'forbidden: User "system:anonymous" cannot get path "{}"',
    "reason": "Forbidden",
    "details": {},
    "code": 403,
}

ClientCA = "kubeconfig_client_ca"
ServerCA = "kubeconfig_server"
log = Logger()


class KubeConfig:
    def __init__(self, ca_cert_path, server_endpoint_ip, server_endpoint_port):
        self.ca_cert_path = ca_cert_path
        self.server_endpoint_url = (
            f"https://{server_endpoint_ip}:{server_endpoint_port}"
        )
        self.bodies = {
            "unauthorized": copy.deepcopy(UnauthorizedResponseBody),
            "forbidden": copy.deepcopy(ForbiddenResponseBody),
            "bad": copy.deepcopy(BadRequestResponseBody),
        }

    @staticmethod
    def kc_headers() -> bytes:
        """Generates kubeconfig headers"""
        flow_schema_uid = uuid.uuid4()
        priority_level_uid = uuid.uuid4()
        Headers = (
            textwrap.dedent(
                f"""
                        cache-control: no-cache, private
                        content-type: application/json
                        x-content-type-options: nosniff
                        x-kubernetes-pf-flowschema-uid: {flow_schema_uid}
                        x-kubernetes-pf-prioritylevel-uid: {priority_level_uid}
                        """
            )
            .lstrip()
            .encode()
        )
        return Headers

    def _get_random_username(self):
        k = ["kubernetes", "k8s", "kube", "k", "cluster"]
        t = ["infra", "sre", "devops", "iac", "cloud", "dev", "prod", "cicd"]
        r = ["admin", "user", "superuser", "root"]
        d = ["-", "_", ":"]

        _d = random.choice(d)
        return f"{random.choice(k)}{_d}{random.choice(t)}{_d}{random.choice(r)}"

    def get_kubeconfig(self) -> Tuple[str, str]:
        """Returns the token and associated kubeconfig

        Returns:
            Tuple[str, str]: Returns the token and associated kubeconfig. (token, kubeconfig)
        """
        _ca_data = get_certificate(self.ca_cert_path)

        ca_data = _ca_data.get("c")

        # username can be randomly generated here
        username = self._get_random_username()
        cluster_name = "k8s-prod-cluster"

        client_auth = mTLS.generate_new_certificate(
            ca_cert_path=self.ca_cert_path, username=username
        )

        # Using an OrderedDict here to ensure the output kubeconfig matches the ideal kubeconfig structure
        kc = OrderedDict()

        kc["apiVersion"] = "v1"
        kc["kind"] = "Config"
        kc["clusters"] = [
            {
                "cluster": {
                    "certificate-authority-data": base64.b64encode(ca_data)
                    .decode()
                    .replace("\n", ""),
                    "server": self.server_endpoint_url,
                },
                "name": cluster_name,
            }
        ]
        kc["users"] = [
            {
                "name": username,
                "user": {
                    "client-certificate-data": base64.b64encode(client_auth["c"])
                    .decode()
                    .replace("\n", ""),
                    "client-key-data": base64.b64encode(client_auth["k"])
                    .decode()
                    .replace("\n", ""),
                },
            }
        ]
        kc["contexts"] = [
            {
                "context": {"cluster": cluster_name, "user": username},
                "name": f"{username}-{cluster_name}",
            }
        ]
        kc["current-context"] = f"{username}-{cluster_name}"

        # Custom representer to make OrderDict parseable by pyyaml
        def preserve_order(self, data):
            return self.represent_mapping("tag:yaml.org,2002:map", list(data.items()))

        yaml.add_representer(OrderedDict, preserve_order)
        # 0: Truncated cert fingerprint, 1: b64 encoded kubeconfig
        return (
            client_auth["f"].decode().replace(":", "")[:25].lower(),
            base64.b64encode(
                yaml.dump(kc, None, default_flow_style=False, sort_keys=False).encode()
            ),
        )


def get_kubeconfig():
    server_endpoint_ip, server_endpoint_port = get_kc_endpoint()
    if server_endpoint_ip is None:
        log.error("Kubeconfig endpoint is not set.")
        raise LookupError("Kubeconfig endpoint lookup failed.")
    return KubeConfig(
        ca_cert_path=ClientCA,
        server_endpoint_ip=server_endpoint_ip,
        server_endpoint_port=server_endpoint_port,
    ).get_kubeconfig()
