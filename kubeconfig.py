from channel_input_mtls import mTLS
from queries import get_kc_endpoint
from collections import OrderedDict
from twisted.logger import Logger

import copy
import yaml
import random
import base64

UnauthorizedResponseBody = {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"Unauthorized","reason":"Unauthorized","code":401}
BadRequestResponseBody = {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"Bad Request","reason":"Bad Request","code":400}
ForbiddenResponseBody = {"kind": "Status","apiVersion": "v1","metadata":{},"status": "Failure","message":"forbidden: User \"system:anonymous\" cannot get path \"{}\"","reason": "Forbidden","details": {},"code": 403}

ClientCA = "kubeconfig_client_ca"

log = Logger()

class KubeConfig():
    bodies = {}

    def __init__(self, ca_cert_path, server_endpoint):
        self.ca_cert_path = ca_cert_path
        self.server_endpoint = server_endpoint
        self.bodies = {'unauthorized': copy.deepcopy(UnauthorizedResponseBody), 'forbidden': copy.deepcopy(ForbiddenResponseBody), 'bad': copy.deepcopy(BadRequestResponseBody)}

    def kc_headers(self):
        import uuid
        Headers = "cache-control: no-cache, private\r\ncontent-type: application/json\r\nx-content-type-options: nosniff\r\nx-kubernetes-pf-flowschema-uid: %s\r\nx-kubernetes-pf-prioritylevel-uid: %s\r\n"
        flow_schema_uid = str(uuid.uuid4())
        priority_level_uid = str(uuid.uuid4())
        return Headers % (flow_schema_uid, priority_level_uid)

    def _get_random_username(self):
        k = ["kubernetes", "k8s", "kube", "k", "cluster"]
        t = ["infra", "sre", "devops", "iac", "cloud", "dev", "prod", "cicd"]
        r = ["admin", "user", "superuser", "root"]
        d = ["-", "_", ":"]

        _d = d[random.randint(0,len(d)-1)]
        return "%s%s%s%s%s" % (k[random.randint(0,len(k)-1)], _d, t[random.randint(0,len(t))-1], _d, r[random.randint(0,len(r)-1)])

    def get_kubeconfig(self):
        try:
            # Using an OrderedDict here to ensure the output kubeconfig matches the ideal kubeconfig structure
            kc = OrderedDict()

            kc['apiVersion'] = 'v1'
            kc['kind'] = 'Config'
            kc['clusters'] = [{'cluster': {'insecure-skip-tls-verify': True, 'server': None}, 'name': None}]
            kc['users'] = [{'name': None, 'user': {'client-certificate-data': None, 'client-key-data': None}}]
            kc['contexts'] = [{'context': {'cluster': None, 'user': None}, 'name': None}]
            kc['current-context'] = None

            # username can be randomly generated here
            username = self._get_random_username()
            cluster_name = "k8s-prod-cluster"

            client_auth = mTLS.generate_new_certificate(ca_cert_path=self.ca_cert_path, username=username)

            cluster_endpoint = "https://%s" % self.server_endpoint

            kc['clusters'][0]['cluster']['server'] = cluster_endpoint
            kc['clusters'][0]['name'] = cluster_name

            kc['users'][0]['name'] = username
            kc['users'][0]['user']['client-certificate-data'] = client_auth['c'].encode('utf-8')
            kc['users'][0]['user']['client-key-data'] = client_auth['k'].encode('utf-8')

            kc['contexts'][0]['context']['cluster'] = cluster_name
            kc['contexts'][0]['context']['user'] = username
            kc['contexts'][0]['name'] = "%s-%s" % (username, cluster_name)

            kc['current-context'] = "%s-%s" % (username, cluster_name)

            # Custom representer to make OrderDict parseable by pyyaml
            preserve_order = lambda self, data:  self.represent_mapping('tag:yaml.org,2002:map', data.items())
            yaml.add_representer(OrderedDict, preserve_order)
            # 0: Truncated cert fingerprint, 1: b64 encoded kubeconfig
            return (client_auth["f"].replace(":","")[:25].lower(), base64.b64encode(yaml.dump(kc, None, default_flow_style=False, sort_keys=False)))
        except Exception as e:
            log.error(u"%s" % e)
            return None

def get_kubeconfig():
    return KubeConfig(ca_cert_path=ClientCA, server_endpoint=get_kc_endpoint()).get_kubeconfig()
